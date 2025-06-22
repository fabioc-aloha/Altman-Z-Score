"""
Data Merger - Combine FMP financial data with Yahoo market data

This module implements the strategic FMP-first approach by merging:
1. FMP pre-calculated financial ratios (eliminates field mapping complexity)
2. Yahoo Finance market data (prices, market cap, shares outstanding)

Key Strategic Advantages:
- Uses FMP pre-calculated Z-Score ratios directly
- No complex field mapping or transformation required
- Maintains 48-hour caching performance
- Focuses on integration and quality rather than data transformation
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError, ValidationError
from ...common.api_rate_limiter import rate_limiter
from ...models.data_models import MergedFinancialData, DataQualityReport
from .fmp_fetcher import FMPDataFetcher
from .yahoo_fetcher import YahooDataFetcher

logger = get_logger(__name__)


@dataclass
class FMPRatiosData:
    """FMP financial ratios data structure."""
    working_capital_ratio: Optional[float] = None
    retained_earnings_ratio: Optional[float] = None
    ebit_ratio: Optional[float] = None
    asset_turnover: Optional[float] = None
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    raw_ratios: Dict[str, Any] = None


@dataclass
class YahooMarketData:
    """Yahoo market data structure."""
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None
    volume: Optional[int] = None
    raw_data: Dict[str, Any] = None


class DataMerger:
    """
    Merge FMP financial ratios with Yahoo market data.
    
    Strategic Focus: Integration of pre-calculated ratios rather than
    complex field mapping and transformation.
    """
    
    def __init__(self):
        self.fmp_fetcher = FMPDataFetcher()
        self.yahoo_fetcher = YahooDataFetcher()
        
    @rate_limiter.rate_limited("data_merger")
    async def merge_financial_data(self, ticker: str) -> MergedFinancialData:
        """
        Merge FMP and Yahoo data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            MergedFinancialData with integrated ratios and market data
        """
        logger.info(f"Starting data merger for {ticker}")
        
        try:
            # Fetch FMP financial ratios (pre-calculated, no field mapping needed)
            fmp_data = await self._fetch_fmp_ratios(ticker)
            
            # Fetch Yahoo market data
            yahoo_data = await self._fetch_yahoo_market_data(ticker)
            
            # Merge the data sources
            merged_data = self._integrate_data_sources(ticker, fmp_data, yahoo_data)
              logger.info(f"Successfully merged data for {ticker}")
            return merged_data
            
        except Exception as e:
            logger.error(f"Failed to merge data for {ticker}: {e}")
            raise DataFetchError(f"Data merger failed for {ticker}: {str(e)}")
    
    async def _fetch_fmp_ratios(self, ticker: str) -> FMPRatiosData:
        """Fetch financial data from FMP API and calculate Z-Score ratios."""
        try:
            # Get financial statements and ratios
            ratios = self.fmp_fetcher.get_financial_ratios(ticker, period="annual", limit=1)
            income_stmt = self.fmp_fetcher.get_income_statement(ticker, period="annual", limit=1)
            balance_sheet = self.fmp_fetcher.get_balance_sheet(ticker, period="annual", limit=1)
            
            if not ratios or not income_stmt or not balance_sheet:
                raise DataFetchError(f"Incomplete FMP data for {ticker}")
            
            latest_ratios = ratios[0]
            latest_income = income_stmt[0]
            latest_balance = balance_sheet[0]
            
            # Calculate Z-Score ratios from raw financial data
            total_assets = latest_balance.get('totalAssets', 0)
            current_assets = latest_balance.get('totalCurrentAssets', 0)
            current_liabilities = latest_balance.get('totalCurrentLiabilities', 0)
            retained_earnings = latest_balance.get('retainedEarnings', 0)
            ebit = latest_income.get('operatingIncome', 0)  # EBIT approximation
            revenue = latest_income.get('revenue', 0)
            
            # Calculate working capital ratio (X1)
            working_capital = current_assets - current_liabilities
            working_capital_ratio = working_capital / total_assets if total_assets > 0 else None
            
            # Calculate retained earnings ratio (X2)
            retained_earnings_ratio = retained_earnings / total_assets if total_assets > 0 else None
            
            # Calculate EBIT ratio (X3)
            ebit_ratio = ebit / total_assets if total_assets > 0 else None
            
            # Get asset turnover (X4) from ratios API
            asset_turnover = self._safe_get_ratio(latest_ratios, 'assetTurnover')
            
            # Alternative calculation if not available
            if asset_turnover is None:
                asset_turnover = revenue / total_assets if total_assets > 0 else None
            
            return FMPRatiosData(
                working_capital_ratio=working_capital_ratio,
                retained_earnings_ratio=retained_earnings_ratio,
                ebit_ratio=ebit_ratio,
                asset_turnover=asset_turnover,
                current_ratio=self._safe_get_ratio(latest_ratios, 'currentRatio'),
                debt_to_equity=self._safe_get_ratio(latest_ratios, 'debtEquityRatio'),
                raw_ratios={
                    'ratios': latest_ratios,
                    'income_statement': latest_income,
                    'balance_sheet': latest_balance
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch and calculate FMP ratios for {ticker}: {e}")
            raise DataFetchError(f"FMP ratios calculation failed: {str(e)}")
    
    async def _fetch_yahoo_market_data(self, ticker: str) -> YahooMarketData:
        """Fetch market data from Yahoo Finance."""
        try:
            # Get market data from Yahoo
            market_data = self.yahoo_fetcher.get_market_data_summary(ticker)
            
            if not market_data:
                raise DataFetchError(f"No Yahoo market data available for {ticker}")
            
            return YahooMarketData(
                market_cap=market_data.get('market_cap'),
                shares_outstanding=market_data.get('shares_outstanding'),
                current_price=market_data.get('current_price'),
                volume=market_data.get('volume'),  # May not be available
                raw_data=market_data
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo market data for {ticker}: {e}")
            raise DataFetchError(f"Yahoo market data fetch failed: {str(e)}")
    
    def _integrate_data_sources(self, ticker: str, fmp_data: FMPRatiosData, 
                               yahoo_data: YahooMarketData) -> MergedFinancialData:
        """
        Integrate FMP ratios with Yahoo market data.
        
        Strategic advantage: No complex transformation needed - 
        FMP provides calculation-ready ratios.
        """
        return MergedFinancialData(
            ticker=ticker,
            timestamp=datetime.now().isoformat(),
            
            # Z-Score ratios (pre-calculated by FMP)
            working_capital_ratio=fmp_data.working_capital_ratio,
            retained_earnings_ratio=fmp_data.retained_earnings_ratio,
            ebit_ratio=fmp_data.ebit_ratio,
            asset_turnover=fmp_data.asset_turnover,
            
            # Market data (from Yahoo)
            market_cap=yahoo_data.market_cap,
            shares_outstanding=yahoo_data.shares_outstanding,
            current_price=yahoo_data.current_price,
            
            # Additional ratios for context
            current_ratio=fmp_data.current_ratio,
            debt_to_equity=fmp_data.debt_to_equity,
            
            # Raw data for debugging/validation
            raw_fmp_data=fmp_data.raw_ratios,
            raw_yahoo_data=yahoo_data.raw_data
        )
    
    def _safe_get_ratio(self, data: Dict[str, Any], key: str) -> Optional[float]:
        """Safely extract ratio value with validation."""
        try:
            value = data.get(key)
            if value is None:
                return None
            
            # Convert to float and validate
            float_value = float(value)
            
            # Basic sanity checks for financial ratios
            if abs(float_value) > 1000:  # Extreme values flag
                logger.warning(f"Extreme ratio value for {key}: {float_value}")
            
            return float_value
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid ratio value for {key}: {value}, error: {e}")
            return None


# Main integration function for external use
@rate_limiter.rate_limited("data_integration")
async def merge_financial_data(ticker: str) -> MergedFinancialData:
    """
    Public interface for merging FMP and Yahoo data.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        MergedFinancialData ready for Z-Score calculation
        
    Strategic Advantage:
        Uses FMP pre-calculated ratios eliminating complex field mapping.
    """
    merger = DataMerger()
    return await merger.merge_financial_data(ticker)


def validate_data_completeness(data: MergedFinancialData) -> DataQualityReport:
    """
    Validate merged data has required fields for Z-Score calculation.
    
    Args:
        data: Merged financial data
        
    Returns:
        DataQualityReport with validation results
    """
    missing_fields = []
    warnings = []
    
    # Check Z-Score essential ratios
    if data.working_capital_ratio is None:
        missing_fields.append("working_capital_ratio")
    
    if data.retained_earnings_ratio is None:
        missing_fields.append("retained_earnings_ratio")
        
    if data.ebit_ratio is None:
        missing_fields.append("ebit_ratio")
        
    if data.asset_turnover is None:
        missing_fields.append("asset_turnover")
    
    # Check market data for model selection
    if data.market_cap is None:
        warnings.append("Market cap missing - may affect model selection")
        
    if data.shares_outstanding is None:
        warnings.append("Shares outstanding missing - may affect equity calculations")
    
    # Data quality assessment
    is_complete = len(missing_fields) == 0
    has_warnings = len(warnings) > 0
    
    return DataQualityReport(
        ticker=data.ticker,
        is_complete=is_complete,
        missing_fields=missing_fields,
        warnings=warnings,
        quality_score=1.0 - (len(missing_fields) * 0.25 + len(warnings) * 0.1),
        recommendation="Ready for Z-Score calculation" if is_complete else "Missing critical ratios"
    )
