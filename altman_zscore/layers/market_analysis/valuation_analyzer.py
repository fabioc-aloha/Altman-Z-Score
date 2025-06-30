"""
Valuation Analyzer - P/E, P/B, PEG, dividend analysis and relative valuation

Provides comprehensive valuation analysis including:
- Core valuation ratios (P/E, P/B, P/S, PEG)
- Dividend analysis (yield, payout, growth)
- Market cap and enterprise value metrics
- Sector comparative analysis
- Analyst price targets and estimates
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ...common.api_rate_limiter import rate_limiter
from ...models.market_models import ValuationMetrics, AnalysisParameters
from ..data_fetch.yahoo_fetcher import YahooDataFetcher

logger = get_logger(__name__)


class ValuationAnalyzer:
    """Valuation analysis for stock fundamental metrics."""
    
    def __init__(self, parameters: Optional[AnalysisParameters] = None):
        """
        Initialize valuation analyzer.
        
        Args:
            parameters: Analysis parameters, uses defaults if None
        """
        self.params = parameters or AnalysisParameters()
        self.yahoo_fetcher = YahooDataFetcher()
    
    @rate_limiter.rate_limited("valuation_analysis")
    def analyze_ticker(self, ticker: str) -> ValuationMetrics:
        """
        Perform comprehensive valuation analysis for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            ValuationMetrics with complete valuation analysis
        """
        try:
            logger.info(f"Starting valuation analysis for {ticker}")
            
            # Get comprehensive Yahoo Finance info data
            info = self.yahoo_fetcher._YahooDataFetcher__direct_yahoo_call_get_ticker_info(ticker)
            
            # Calculate core valuation ratios
            core_ratios = self._calculate_core_ratios(info)
            
            # Calculate dividend metrics
            dividend_metrics = self._calculate_dividend_metrics(info, ticker)
            
            # Calculate market metrics
            market_metrics = self._calculate_market_metrics(info)
            
            # Get sector comparison data
            sector_comparison = self._get_sector_comparison(info)
            
            # Get analyst estimates
            analyst_data = self._get_analyst_estimates(info)
            
            return ValuationMetrics(
                ticker=ticker,
                analysis_date=datetime.now(),
                **core_ratios,
                **dividend_metrics,
                **market_metrics,
                **sector_comparison,
                **analyst_data
            )
            
        except Exception as e:
            logger.error(f"Valuation analysis failed for {ticker}: {e}")
            raise DataFetchError(f"Valuation analysis failed for {ticker}: {str(e)}")
    
    def _calculate_core_ratios(self, info: Dict) -> Dict[str, Optional[float]]:
        """Calculate core valuation ratios."""
        ratios = {}
        
        # P/E Ratio
        pe_ratio = info.get('trailingPE') or info.get('forwardPE')
        ratios['pe_ratio'] = float(pe_ratio) if pe_ratio and pe_ratio > 0 else None
        
        # P/B Ratio
        pb_ratio = info.get('priceToBook')
        ratios['pb_ratio'] = float(pb_ratio) if pb_ratio and pb_ratio > 0 else None
        
        # P/S Ratio
        ps_ratio = info.get('priceToSalesTrailing12Months')
        ratios['ps_ratio'] = float(ps_ratio) if ps_ratio and ps_ratio > 0 else None
        
        # PEG Ratio
        peg_ratio = info.get('pegRatio')
        ratios['peg_ratio'] = float(peg_ratio) if peg_ratio and peg_ratio > 0 else None
        
        # If PEG not available, calculate it
        if not ratios['peg_ratio'] and ratios['pe_ratio']:
            earnings_growth = info.get('earningsQuarterlyGrowth') or info.get('earningsGrowth')
            if earnings_growth and earnings_growth > 0:
                ratios['peg_ratio'] = ratios['pe_ratio'] / (earnings_growth * 100)
        
        return ratios
    
    def _calculate_dividend_metrics(self, info: Dict, ticker: str) -> Dict[str, Optional[float]]:
        """Calculate dividend-related metrics."""
        metrics = {}
        
        # Dividend yield
        dividend_yield = info.get('dividendYield')
        metrics['dividend_yield'] = float(dividend_yield) if dividend_yield else None
        
        # Dividend payout ratio
        payout_ratio = info.get('payoutRatio')
        metrics['dividend_payout_ratio'] = float(payout_ratio) if payout_ratio else None
        
        # Dividend growth rate calculation - simplified for cached data
        # Note: Historical dividend data would require additional API calls
        # For now, we'll skip this calculation to avoid cache issues
        metrics['dividend_growth_rate'] = None
        
        return metrics
    
    def _calculate_market_metrics(self, info: Dict) -> Dict[str, Optional[float]]:
        """Calculate market-based valuation metrics."""
        metrics = {}
        
        # Market cap
        market_cap = info.get('marketCap')
        metrics['market_cap'] = float(market_cap) if market_cap else None
        
        # Enterprise value
        enterprise_value = info.get('enterpriseValue')
        metrics['enterprise_value'] = float(enterprise_value) if enterprise_value else None
        
        # EV/EBITDA
        ev_ebitda = info.get('enterpriseToEbitda')
        metrics['ev_ebitda'] = float(ev_ebitda) if ev_ebitda and ev_ebitda > 0 else None
        
        return metrics
    
    def _get_sector_comparison(self, info: Dict) -> Dict[str, Optional[Any]]:
        """Get sector-relative valuation metrics."""
        comparison = {}
        
        # Get sector information
        sector = info.get('sector')
        industry = info.get('industry')
        
        # Sector median P/E (approximate values by sector)
        sector_pe_medians = {
            'Technology': 25.0,
            'Healthcare': 20.0,
            'Financials': 12.0,
            'Consumer Discretionary': 18.0,
            'Communication Services': 22.0,
            'Industrials': 16.0,
            'Consumer Staples': 19.0,
            'Energy': 15.0,
            'Utilities': 17.0,
            'Real Estate': 20.0,
            'Materials': 14.0
        }
        
        # Sector median P/B (approximate values by sector)
        sector_pb_medians = {
            'Technology': 4.5,
            'Healthcare': 3.2,
            'Financials': 1.1,
            'Consumer Discretionary': 2.8,
            'Communication Services': 2.5,
            'Industrials': 2.2,
            'Consumer Staples': 3.0,
            'Energy': 1.5,
            'Utilities': 1.8,
            'Real Estate': 1.6,
            'Materials': 1.8
        }
        
        comparison['sector_pe_median'] = sector_pe_medians.get(sector)
        comparison['sector_pb_median'] = sector_pb_medians.get(sector)
        
        # Relative valuation assessment
        current_pe = info.get('trailingPE')
        current_pb = info.get('priceToBook')
        
        relative_signals = []
        
        if current_pe and comparison['sector_pe_median']:
            pe_ratio = current_pe / comparison['sector_pe_median']
            if pe_ratio < 0.8:
                relative_signals.append('undervalued_pe')
            elif pe_ratio > 1.2:
                relative_signals.append('overvalued_pe')
        
        if current_pb and comparison['sector_pb_median']:
            pb_ratio = current_pb / comparison['sector_pb_median']
            if pb_ratio < 0.8:
                relative_signals.append('undervalued_pb')
            elif pb_ratio > 1.2:
                relative_signals.append('overvalued_pb')
        
        # Overall relative valuation
        undervalued_signals = len([s for s in relative_signals if 'undervalued' in s])
        overvalued_signals = len([s for s in relative_signals if 'overvalued' in s])
        
        if undervalued_signals > overvalued_signals:
            comparison['relative_valuation'] = 'undervalued'
        elif overvalued_signals > undervalued_signals:
            comparison['relative_valuation'] = 'overvalued'
        else:
            comparison['relative_valuation'] = 'fairly_valued'
        
        return comparison
    
    def _get_analyst_estimates(self, info: Dict) -> Dict[str, Optional[float]]:
        """Get analyst price targets and estimates."""
        estimates = {}
        
        # Target price from analyst recommendations
        target_price = info.get('targetMeanPrice')
        estimates['analyst_price_target'] = float(target_price) if target_price else None
        
        # Calculate upside potential
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if estimates['analyst_price_target'] and current_price:
            upside = (estimates['analyst_price_target'] - current_price) / current_price
            estimates['upside_potential'] = float(upside)
        else:
            estimates['upside_potential'] = None
        
        return estimates
    
    def get_valuation_summary(self, valuation_metrics: ValuationMetrics) -> Dict[str, Any]:
        """
        Generate a summary of valuation analysis.
        
        Args:
            valuation_metrics: Completed valuation analysis
            
        Returns:
            Dictionary with valuation summary and key insights
        """
        summary = {
            'ticker': valuation_metrics.ticker,
            'analysis_date': valuation_metrics.analysis_date,
            'key_metrics': {},
            'valuation_signals': [],
            'investment_attractiveness': 'neutral'
        }
        
        # Key metrics
        if valuation_metrics.pe_ratio:
            summary['key_metrics']['P/E Ratio'] = valuation_metrics.pe_ratio
        if valuation_metrics.pb_ratio:
            summary['key_metrics']['P/B Ratio'] = valuation_metrics.pb_ratio
        if valuation_metrics.dividend_yield:
            summary['key_metrics']['Dividend Yield'] = f"{valuation_metrics.dividend_yield:.2%}"
        if valuation_metrics.peg_ratio:
            summary['key_metrics']['PEG Ratio'] = valuation_metrics.peg_ratio
        
        # Valuation signals
        signals = []
        
        # P/E analysis
        if valuation_metrics.pe_ratio:
            if valuation_metrics.pe_ratio < 15:
                signals.append("Low P/E - Potentially undervalued")
            elif valuation_metrics.pe_ratio > 30:
                signals.append("High P/E - Potentially overvalued")
        
        # PEG analysis
        if valuation_metrics.peg_ratio:
            if valuation_metrics.peg_ratio < 1.0:
                signals.append("PEG < 1.0 - Growth at reasonable price")
            elif valuation_metrics.peg_ratio > 2.0:
                signals.append("PEG > 2.0 - Expensive relative to growth")
        
        # Dividend analysis
        if valuation_metrics.dividend_yield:
            if valuation_metrics.dividend_yield > 0.04:  # 4%
                signals.append("Attractive dividend yield")
        
        # Sector relative valuation
        if valuation_metrics.relative_valuation:
            if valuation_metrics.relative_valuation == 'undervalued':
                signals.append("Undervalued relative to sector")
            elif valuation_metrics.relative_valuation == 'overvalued':
                signals.append("Overvalued relative to sector")
        
        # Analyst upside
        if valuation_metrics.upside_potential:
            if valuation_metrics.upside_potential > 0.15:  # 15%
                signals.append("Significant analyst upside potential")
            elif valuation_metrics.upside_potential < -0.10:  # -10%
                signals.append("Limited upside per analyst targets")
        
        summary['valuation_signals'] = signals
        
        # Overall investment attractiveness
        positive_signals = len([s for s in signals if any(word in s.lower() 
                                                       for word in ['undervalued', 'attractive', 'reasonable', 'upside'])])
        negative_signals = len([s for s in signals if any(word in s.lower() 
                                                       for word in ['overvalued', 'expensive', 'limited'])])
        
        if positive_signals > negative_signals + 1:
            summary['investment_attractiveness'] = 'attractive'
        elif negative_signals > positive_signals + 1:
            summary['investment_attractiveness'] = 'unattractive'
        else:
            summary['investment_attractiveness'] = 'neutral'
        
        return summary
