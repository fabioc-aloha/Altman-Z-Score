"""
Consensus Data Fetcher - Analyst Consensus Estimates

Fetches analyst consensus estimates for key financial metrics used in Z-Score calculations.
Integrates with FMP's analyst estimates API for forward-looking data.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ..data_fetch.fmp_fetcher import FMPDataFetcher

logger = get_logger(__name__)


@dataclass
class ConsensusEstimate:
    """Single consensus estimate for a specific metric and period."""
    ticker: str
    metric: str
    fiscal_year: int
    fiscal_quarter: Optional[int]  # None for annual estimates
    estimate_mean: float
    estimate_high: float
    estimate_low: float
    number_of_analysts: int
    last_updated: datetime
    confidence_score: float  # 0.0 to 1.0 based on analyst agreement


@dataclass
class ConsensusData:
    """Complete consensus data for a ticker."""
    ticker: str
    company_name: str
    estimates: List[ConsensusEstimate]
    coverage_quality: float  # 0.0 to 1.0 based on analyst coverage
    data_vintage: datetime
    

class ConsensusFetcher:
    """Fetches analyst consensus estimates for forecasting."""
    
    def __init__(self):
        """Initialize consensus fetcher."""
        self.logger = get_logger(self.__class__.__name__)
        self.fmp_fetcher = FMPDataFetcher()
        
        # Key metrics needed for Z-Score forecasting
        self.required_metrics = {
            'revenue': 'Revenue',
            'ebitda': 'EBITDA', 
            'net_income': 'Net Income',
            'total_assets': 'Total Assets',
            'total_debt': 'Total Debt',
            'total_equity': 'Total Equity',
            'working_capital': 'Working Capital',
            'retained_earnings': 'Retained Earnings'
        }
    
    async def fetch_consensus_estimates(
        self, 
        ticker: str, 
        forecast_years: int = 2
    ) -> Optional[ConsensusData]:
        """
        Fetch analyst consensus estimates for Z-Score forecasting.
        
        Args:
            ticker: Stock ticker symbol
            forecast_years: Number of years to forecast (1-3)
            
        Returns:
            ConsensusData: Consensus estimates or None if unavailable
        """
        try:
            self.logger.info(f"Fetching consensus estimates for {ticker} ({forecast_years} years)")
            
            # Fetch analyst estimates from FMP
            estimates_data = await self._fetch_analyst_estimates(ticker, forecast_years)
            
            if not estimates_data:
                self.logger.warning(f"No analyst consensus data available for {ticker}")
                return None
            
            # Process and validate estimates
            consensus_estimates = self._process_estimates(ticker, estimates_data)
            
            if not consensus_estimates:
                self.logger.warning(f"Unable to process consensus estimates for {ticker}")
                return None
            
            # Calculate coverage quality
            coverage_quality = self._calculate_coverage_quality(consensus_estimates)
            
            # Get company name
            company_name = await self._get_company_name(ticker)
            
            consensus_data = ConsensusData(
                ticker=ticker,
                company_name=company_name,
                estimates=consensus_estimates,
                coverage_quality=coverage_quality,
                data_vintage=datetime.now()
            )
            
            self.logger.info(f"Successfully fetched consensus data for {ticker}: "
                           f"{len(consensus_estimates)} estimates, "
                           f"coverage quality: {coverage_quality:.2f}")
            
            return consensus_data
            
        except Exception as e:
            self.logger.error(f"Error fetching consensus estimates for {ticker}: {str(e)}")
            return None
    
    async def _fetch_analyst_estimates(
        self, 
        ticker: str, 
        forecast_years: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch raw analyst estimates from FMP API."""
        try:
            # FMP analyst estimates endpoints
            estimates_data = []
            
            # Annual estimates
            annual_estimates = self.fmp_fetcher.get_analyst_estimates_annual(ticker)
            if annual_estimates:
                estimates_data.extend(annual_estimates)
            
            # Quarterly estimates (for more granular forecasting)
            quarterly_estimates = self.fmp_fetcher.get_analyst_estimates_quarterly(ticker)
            if quarterly_estimates:
                estimates_data.extend(quarterly_estimates)
            
            # Earnings estimates (key for EBIT calculation)
            earnings_estimates = self.fmp_fetcher.get_earnings_surprises(ticker)
            if earnings_estimates:
                estimates_data.extend(earnings_estimates)
            
            return estimates_data if estimates_data else None
            
        except Exception as e:
            self.logger.error(f"Error fetching raw analyst estimates: {str(e)}")
            return None
    
    def _process_estimates(
        self, 
        ticker: str, 
        raw_estimates: List[Dict[str, Any]]
    ) -> List[ConsensusEstimate]:
        """Process raw estimates into structured consensus data."""
        consensus_estimates = []
        
        try:
            for estimate_data in raw_estimates:
                # Extract key fields with error handling
                metric = self._map_estimate_metric(estimate_data)
                if not metric:
                    continue
                
                fiscal_year = self._extract_fiscal_year(estimate_data)
                fiscal_quarter = self._extract_fiscal_quarter(estimate_data)
                
                # Calculate consensus statistics
                estimates = self._extract_estimate_values(estimate_data)
                if not estimates:
                    continue
                
                estimate_mean = estimates.get('mean', 0.0)
                estimate_high = estimates.get('high', estimate_mean * 1.1)
                estimate_low = estimates.get('low', estimate_mean * 0.9)
                number_of_analysts = estimates.get('analyst_count', 1)
                
                # Calculate confidence score based on analyst agreement
                confidence_score = self._calculate_confidence_score(estimates)
                
                consensus_estimate = ConsensusEstimate(
                    ticker=ticker,
                    metric=metric,
                    fiscal_year=fiscal_year,
                    fiscal_quarter=fiscal_quarter,
                    estimate_mean=estimate_mean,
                    estimate_high=estimate_high,
                    estimate_low=estimate_low,
                    number_of_analysts=number_of_analysts,
                    last_updated=datetime.now(),
                    confidence_score=confidence_score
                )
                
                consensus_estimates.append(consensus_estimate)
        
        except Exception as e:
            self.logger.error(f"Error processing estimates: {str(e)}")
        
        return consensus_estimates
    
    def _map_estimate_metric(self, estimate_data: Dict[str, Any]) -> Optional[str]:
        """Map FMP estimate fields to Z-Score metrics."""
        # FMP field mapping to Z-Score components
        field_mapping = {
            'estimatedRevenueAvg': 'revenue',
            'estimatedRevenueLow': 'revenue',
            'estimatedRevenueHigh': 'revenue',
            'estimatedEbitdaAvg': 'ebitda',
            'estimatedEbitdaLow': 'ebitda', 
            'estimatedEbitdaHigh': 'ebitda',
            'estimatedNetIncomeAvg': 'net_income',
            'estimatedNetIncomeLow': 'net_income',
            'estimatedNetIncomeHigh': 'net_income',
            'estimatedEpsAvg': 'eps',  # For earnings-based calculations
            'estimatedEpsLow': 'eps',
            'estimatedEpsHigh': 'eps'
        }
        
        # Check for known fields
        for field, metric in field_mapping.items():
            if field in estimate_data and estimate_data[field] is not None:
                return metric
        
        return None
    
    def _extract_fiscal_year(self, estimate_data: Dict[str, Any]) -> int:
        """Extract fiscal year from estimate data."""
        try:
            # Try different date fields
            date_fields = ['date', 'fiscalYear', 'year', 'period']
            
            for field in date_fields:
                if field in estimate_data:
                    date_value = estimate_data[field]
                    if isinstance(date_value, str):
                        # Parse date string
                        date_obj = pd.to_datetime(date_value)
                        return date_obj.year
                    elif isinstance(date_value, int):
                        return date_value
            
            # Default to current year + 1 if no date found
            return datetime.now().year + 1
            
        except Exception:
            return datetime.now().year + 1
    
    def _extract_fiscal_quarter(self, estimate_data: Dict[str, Any]) -> Optional[int]:
        """Extract fiscal quarter if available."""
        try:
            quarter_fields = ['quarter', 'fiscalQuarter', 'q']
            
            for field in quarter_fields:
                if field in estimate_data:
                    quarter = estimate_data[field]
                    if isinstance(quarter, int) and 1 <= quarter <= 4:
                        return quarter
            
            return None  # Annual estimate
            
        except Exception:
            return None
    
    def _extract_estimate_values(self, estimate_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract estimate values (mean, high, low, count)."""
        estimates = {}
        
        try:
            # Look for estimate fields
            avg_fields = ['estimatedRevenueAvg', 'estimatedEbitdaAvg', 'estimatedNetIncomeAvg', 'estimatedEpsAvg']
            high_fields = ['estimatedRevenueHigh', 'estimatedEbitdaHigh', 'estimatedNetIncomeHigh', 'estimatedEpsHigh']
            low_fields = ['estimatedRevenueLow', 'estimatedEbitdaLow', 'estimatedNetIncomeLow', 'estimatedEpsLow']
            
            # Extract mean estimate
            for field in avg_fields:
                if field in estimate_data and estimate_data[field] is not None:
                    estimates['mean'] = float(estimate_data[field])
                    break
            
            # Extract high estimate
            for field in high_fields:
                if field in estimate_data and estimate_data[field] is not None:
                    estimates['high'] = float(estimate_data[field])
                    break
            
            # Extract low estimate
            for field in low_fields:
                if field in estimate_data and estimate_data[field] is not None:
                    estimates['low'] = float(estimate_data[field])
                    break
            
            # Extract analyst count
            count_fields = ['numberAnalystEstimatedRevenue', 'numberAnalystEstimatedEps', 'analystCount']
            for field in count_fields:
                if field in estimate_data and estimate_data[field] is not None:
                    estimates['analyst_count'] = int(estimate_data[field])
                    break
            
            return estimates
            
        except Exception as e:
            self.logger.warning(f"Error extracting estimate values: {str(e)}")
            return {}
    
    def _calculate_confidence_score(self, estimates: Dict[str, float]) -> float:
        """Calculate confidence score based on analyst agreement."""
        try:
            mean = estimates.get('mean', 0)
            high = estimates.get('high', mean)
            low = estimates.get('low', mean)
            analyst_count = estimates.get('analyst_count', 1)
            
            if mean == 0:
                return 0.0
            
            # Calculate range as percentage of mean
            range_pct = abs(high - low) / abs(mean) if mean != 0 else 1.0
            
            # Lower range = higher confidence
            range_confidence = max(0.0, 1.0 - min(range_pct, 1.0))
            
            # More analysts = higher confidence
            analyst_confidence = min(1.0, analyst_count / 10.0)
            
            # Combined confidence score
            confidence = (range_confidence * 0.7) + (analyst_confidence * 0.3)
            
            return round(confidence, 3)
            
        except Exception:
            return 0.5  # Default moderate confidence
    
    def _calculate_coverage_quality(self, estimates: List[ConsensusEstimate]) -> float:
        """Calculate overall coverage quality for the ticker."""
        if not estimates:
            return 0.0
        
        try:
            # Factors: number of metrics covered, analyst count, confidence scores
            metrics_covered = len(set(est.metric for est in estimates))
            total_analysts = sum(est.number_of_analysts for est in estimates)
            avg_confidence = sum(est.confidence_score for est in estimates) / len(estimates)
            
            # Normalize metrics coverage (max 8 key metrics)
            metrics_score = min(1.0, metrics_covered / 8.0)
            
            # Normalize analyst count (good coverage = 5+ analysts)
            analyst_score = min(1.0, total_analysts / (len(estimates) * 5.0))
            
            # Combined quality score
            quality = (metrics_score * 0.4) + (analyst_score * 0.3) + (avg_confidence * 0.3)
            
            return round(quality, 3)
            
        except Exception:
            return 0.5
    
    async def _get_company_name(self, ticker: str) -> str:
        """Get company name for the ticker."""
        try:
            profile = self.fmp_fetcher.get_company_profile(ticker)
            if profile and isinstance(profile, list) and len(profile) > 0:
                return profile[0].get('companyName', ticker)
            return ticker
        except Exception:
            return ticker
