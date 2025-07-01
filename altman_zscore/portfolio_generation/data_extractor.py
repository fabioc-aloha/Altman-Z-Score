"""
Data Extractor for Portfolio Generation

Extracts and parses company data from analysis reports and summaries.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import CompanyData
from ..common.logging_config import get_logger

logger = get_logger(__name__)


class CompanyDataExtractor:
    """
    Extracts company data from analysis output files.
    
    Parses summary files and comprehensive reports to extract:
    - Basic company information
    - Z-Score and risk metrics
    - Investment ratings by profile
    - Key financial metrics
    - AI insights and market analysis
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize data extractor.
        
        Args:
            output_dir: Directory containing company analysis outputs
        """
        self.output_dir = Path(output_dir)
        self.logger = get_logger(self.__class__.__name__)
    
    def extract_all_companies(self) -> List[CompanyData]:
        """
        Extract data for all companies in the output directory.
        
        Returns:
            List of CompanyData objects
        """
        companies = []
        
        if not self.output_dir.exists():
            self.logger.warning(f"Output directory {self.output_dir} does not exist")
            return companies
        
        # Get all company directories
        company_dirs = [
            d for d in self.output_dir.iterdir() 
            if d.is_dir() and len(d.name) >= 1  # Any directory with at least 1 character
        ]
        
        self.logger.info(f"Found {len(company_dirs)} company directories to process")
        
        for ticker_dir in company_dirs:
            try:
                company_data = self.extract_company_data(ticker_dir.name)
                if company_data:
                    companies.append(company_data)
            except Exception as e:
                self.logger.warning(f"Failed to extract data for {ticker_dir.name}: {str(e)}")
        
        self.logger.info(f"Successfully extracted data for {len(companies)} companies")
        return companies
    
    def extract_company_data(self, ticker: str) -> Optional[CompanyData]:
        """
        Extract data for a specific company.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            CompanyData object or None if extraction fails
        """
        ticker_dir = self.output_dir / ticker
        summary_path = ticker_dir / f"{ticker}_summary.txt"
        report_path = ticker_dir / f"{ticker}_comprehensive_report.html"
        
        if not summary_path.exists():
            self.logger.warning(f"No summary file found for {ticker}")
            return None
        
        try:
            # Read summary content
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary_content = f.read()
            
            # Extract basic information
            company_name = self._extract_company_name(summary_content, ticker)
            z_score = self._extract_z_score(summary_content)
            risk_category = self._extract_risk_category(summary_content)
            
            # Extract investment ratings
            investment_ratings = self._extract_investment_ratings(summary_content)
            
            # Extract key metrics
            key_metrics = self._extract_key_metrics(summary_content)
            
            # Extract AI insights
            ai_insights = self._extract_ai_insights(summary_content)
            
            # Extract market analysis
            market_analysis = self._extract_market_analysis(summary_content)
            
            return CompanyData(
                ticker=ticker,
                company_name=company_name,
                z_score=z_score,
                risk_category=risk_category,
                investment_ratings=investment_ratings,
                key_metrics=key_metrics,
                ai_insights=ai_insights,
                market_analysis=market_analysis,
                summary_content=summary_content,
                report_path=str(report_path) if report_path.exists() else None
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting data for {ticker}: {str(e)}")
            return None
    
    def _extract_company_name(self, content: str, ticker: str) -> str:
        """Extract company name from summary content."""
        # Look for patterns like "Company: Apple Inc." or "AAPL - Apple Inc."
        patterns = [
            r"Company:\s*(.+?)(?:\n|$)",
            rf"{ticker}\s*-\s*(.+?)(?:\n|$)",
            r"Company Name:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return ticker  # Fallback to ticker
    
    def _extract_z_score(self, content: str) -> float:
        """Extract Z-Score value from summary content."""
        # Look for patterns like "Z-Score: 2.34", "Z-SCORE: 2.34", or "Altman Z-Score: 1.23"
        patterns = [
            r"Z-SCORE:\s*([\d.-]+)",  # Legacy format (uppercase)
            r"Z-Score:\s*([\d.-]+)",
            r"Altman Z-Score:\s*([\d.-]+)",
            r"Current Z-Score:\s*([\d.-]+)",
            r"Z Score:\s*([\d.-]+)"  # Handle spaces
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0  # Default if not found
    
    def _extract_risk_category(self, content: str) -> str:
        """Extract risk category from summary content."""
        # Look for risk categories
        patterns = [
            r"Risk Category:\s*(.+?)(?:\n|$)",
            r"Zone:\s*(Safe|Grey|Gray|Distress)",
            r"Risk Level:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                category = match.group(1).strip()
                # Normalize risk categories
                if any(word in category.lower() for word in ['safe', 'low']):
                    return "Safe"
                elif any(word in category.lower() for word in ['grey', 'gray', 'medium', 'moderate']):
                    return "Gray Zone"
                elif any(word in category.lower() for word in ['distress', 'high', 'danger']):
                    return "Distress"
                return category
        
        return "Unknown"
    
    def _extract_investment_ratings(self, content: str) -> Dict[str, str]:
        """Extract investment ratings by investor profile."""
        ratings = {}
        
        # First, look for the legacy "Action:" format
        action_match = re.search(r"Action:\s*(.*?)(?:\n|$)", content, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip().upper().replace(' ', '_')
            ratings['overall_investment_rating'] = action
        
        # Look for different investor profiles and their ratings
        profiles = [
            "Conservative Investor", "Growth Investor", "Value Investor", 
            "Dividend Investor", "Aggressive Investor", "Income Investor",
            "Overall Investment Rating", "Investment Recommendation"
        ]
        
        for profile in profiles:
            pattern = rf"{profile}.*?(?:Rating|Recommendation):\s*(STRONG\s+BUY|BUY|HOLD|SELL|STRONG\s+SELL)"
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                rating = match.group(1).upper().replace(' ', '_')
                ratings[profile.lower().replace(' ', '_')] = rating
        
        return ratings
    
    def _extract_key_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key financial metrics from summary content."""
        metrics = {}
        
        # Common financial metrics to extract
        metric_patterns = {
            'market_cap': r"Market Cap[:\s]*\$?([\d.,]+[BMK]?)",
            'pe_ratio': r"P/E Ratio[:\s]*([\d.-]+)",
            'pb_ratio': r"P/B Ratio[:\s]*([\d.-]+)",
            'debt_to_equity': r"Debt[/\s]to[/\s]Equity[:\s]*([\d.-]+)",
            'current_ratio': r"Current Ratio[:\s]*([\d.-]+)",
            'roa': r"ROA[:\s]*([\d.-]+)%?",
            'roe': r"ROE[:\s]*([\d.-]+)%?",
            'revenue_growth': r"Revenue Growth[:\s]*([\d.-]+)%?",
            'profit_margin': r"Profit Margin[:\s]*([\d.-]+)%?"
        }
        
        for metric, pattern in metric_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                try:
                    # Handle special cases
                    if 'B' in value_str:
                        metrics[metric] = float(value_str.replace('B', '').replace(',', '')) * 1e9
                    elif 'M' in value_str:
                        metrics[metric] = float(value_str.replace('M', '').replace(',', '')) * 1e6
                    elif 'K' in value_str:
                        metrics[metric] = float(value_str.replace('K', '').replace(',', '')) * 1e3
                    else:
                        metrics[metric] = float(value_str.replace(',', ''))
                except ValueError:
                    metrics[metric] = value_str
        
        return metrics
    
    def _extract_ai_insights(self, content: str) -> Dict[str, Any]:
        """Extract AI insights from summary content."""
        insights = {}
        
        # Look for AI analysis sections
        ai_patterns = {
            'sentiment_score': r"Sentiment Score[:\s]*([\d.-]+)",
            'confidence_level': r"AI Confidence[:\s]*([\d.-]+)%?",
            'risk_assessment': r"AI Risk Assessment[:\s]*(.+?)(?:\n|$)",
            'key_insights': r"Key AI Insights[:\s]*(.+?)(?:\n\n|$)"
        }
        
        for key, pattern in ai_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if key in ['sentiment_score', 'confidence_level']:
                    try:
                        insights[key] = float(value.replace('%', ''))
                    except ValueError:
                        insights[key] = value
                else:
                    insights[key] = value
        
        return insights
    
    def _extract_market_analysis(self, content: str) -> Dict[str, Any]:
        """Extract market analysis data from summary content."""
        analysis = {}
        
        # Look for market analysis metrics
        market_patterns = {
            'rsi': r"RSI[:\s]*([\d.-]+)",
            'volatility': r"Volatility[:\s]*([\d.-]+)%?",
            'beta': r"Beta[:\s]*([\d.-]+)",
            'price_trend': r"Price Trend[:\s]*(.+?)(?:\n|$)",
            'volume_trend': r"Volume Trend[:\s]*(.+?)(?:\n|$)"
        }
        
        for key, pattern in market_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if key in ['rsi', 'volatility', 'beta']:
                    try:
                        analysis[key] = float(value.replace('%', ''))
                    except ValueError:
                        analysis[key] = value
                else:
                    analysis[key] = value
        
        return analysis
