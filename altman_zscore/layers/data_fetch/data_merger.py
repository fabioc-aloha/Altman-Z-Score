"""
Data Merger - Combine FMP financial data with Yahoo market data

This module implements the FMP-first approach by merging:
1. FMP financial data and calculated Z-Score ratios
2. Yahoo Finance market data (prices, market cap, shares outstanding)

Key Strategic Advantages:
- Uses FMP financial statements to calculate Z-Score ratios
- Maintains 48-hour caching performance
- Focuses on integration and quality validation
- Deterministic ratio calculation from source data
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
from .finnhub_fetcher import FinnhubDataFetcher

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
    company_name: Optional[str] = None
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
    
    Strategic Focus: Calculate Z-Score ratios from FMP financial statements
    and integrate with Yahoo market data.
    """
    
    def __init__(self):
        self.fmp_fetcher = FMPDataFetcher()
        self.yahoo_fetcher = YahooDataFetcher()
        self.finnhub_fetcher = FinnhubDataFetcher()

    @rate_limiter.rate_limited("data_merger")
    async def merge_financial_data(self, ticker: str, start_date: Optional[str] = None, quarters: int = 4) -> List[MergedFinancialData]:
        """
        Merge FMP and Yahoo data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Optional start date filter (ignored for current implementation)
            quarters: Number of quarters for analysis (enhanced accounts: 8-20)
            
        Returns:
            List[MergedFinancialData] with integrated ratios and market data (single period for now)
        """
        logger.info(f"Starting data merger for {ticker} (quarters: {quarters})")
        
        # Note: start_date is currently ignored as we use latest financial data
        # Future enhancement could support historical period analysis
        if start_date:
            logger.info(f"Note: start_date {start_date} specified but using latest data")
        
        # Enhanced analysis mode detection
        enhanced_mode = quarters > 4
        if enhanced_mode:
            logger.info(f"Enhanced analysis mode detected: processing {quarters} quarters")
        
        try:
            # Fetch FMP financial data and calculate ratios
            # For enhanced mode, fetch multiple quarters of data
            if enhanced_mode:
                fmp_data_list = await self._fetch_multiple_quarters_fmp_data(ticker, quarters)
                yahoo_data = await self._fetch_yahoo_market_data(ticker)
                
                # Process each quarter and create multiple MergedFinancialData objects
                merged_data_list = []
                for i, fmp_data in enumerate(fmp_data_list):
                    # Fetch company logo and cache locally (only for first iteration)
                    logo_file_path = None
                    logo_url = None
                    if i == 0:  # Only fetch logo once
                        try:
                            logo_file_path = self.finnhub_fetcher.download_and_cache_logo(ticker)
                            if logo_file_path:
                                logger.debug(f"Downloaded and cached logo for {ticker}: {logo_file_path}")
                                logo_url = self.finnhub_fetcher.get_company_logo_url(ticker)
                        except Exception as e:
                            logger.warning(f"Failed to fetch and cache logo for {ticker}: {e}")
                    
                    # Merge the data sources for this quarter
                    merged_data = self._integrate_data_sources(ticker, fmp_data, yahoo_data, logo_url, logo_file_path)
                    
                    # Validate data quality and set quality score
                    quality_report = validate_data_completeness(merged_data)
                    merged_data.data_quality_score = quality_report.quality_score
                    
                    merged_data_list.append(merged_data)
                
                logger.info(f"Successfully merged {len(merged_data_list)} quarters of data for {ticker}")
                return merged_data_list
            else:
                # Standard single-quarter analysis
                fmp_data = await self._fetch_fmp_ratios(ticker)
                
                # Fetch Yahoo market data
                yahoo_data = await self._fetch_yahoo_market_data(ticker)
                
                # Fetch company logo and cache locally (non-blocking, best effort)
                logo_file_path = None
                logo_url = None
                try:
                    # Download and cache logo file
                    logo_file_path = self.finnhub_fetcher.download_and_cache_logo(ticker)
                    if logo_file_path:
                        logger.debug(f"Downloaded and cached logo for {ticker}: {logo_file_path}")
                        # Also get URL for backward compatibility
                        logo_url = self.finnhub_fetcher.get_company_logo_url(ticker)
                    else:
                        logger.debug(f"No logo available for {ticker}")
                except Exception as e:
                    logger.warning(f"Failed to fetch and cache logo for {ticker}: {e}")
                
                # Merge the data sources
                merged_data = self._integrate_data_sources(ticker, fmp_data, yahoo_data, logo_url, logo_file_path)
                
                # Validate data quality and set quality score
                quality_report = validate_data_completeness(merged_data)
                merged_data.data_quality_score = quality_report.quality_score
                
                return [merged_data]  # Return as list for consistency
            
            logger.info(f"Successfully merged data for {ticker} with quality score: {quality_report.quality_score:.2f}")
            return [merged_data]  # Return as list for pipeline compatibility
            
        except Exception as e:
            logger.error(f"Failed to merge data for {ticker}: {e}")
            raise DataFetchError(f"Data merger failed for {ticker}: {str(e)}")

    async def _fetch_fmp_ratios(self, ticker: str) -> FMPRatiosData:
        """Fetch financial data from FMP API and calculate Z-Score ratios."""
        try:
            # Get financial statements and ratios
            ratios = self.fmp_fetcher.get_financial_ratios(ticker, period="annual")
            income_stmt = self.fmp_fetcher.get_income_statement(ticker, period="annual")
            balance_sheet = self.fmp_fetcher.get_balance_sheet(ticker, period="annual")
            company_profile = self.fmp_fetcher.get_company_profile(ticker)
            
            if not ratios or not income_stmt or not balance_sheet:
                raise DataFetchError(f"Incomplete FMP data for {ticker}")
            
            latest_ratios = ratios[0]
            latest_income = income_stmt[0]
            latest_balance = balance_sheet[0]
            
            # Extract company name from profile
            company_name = None
            if company_profile and len(company_profile) > 0:
                company_name = company_profile[0].get('companyName', ticker)
            
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
                company_name=company_name,
                raw_ratios={
                    'ratios': latest_ratios,
                    'income_statement': latest_income,
                    'balance_sheet': latest_balance,
                    'profile': company_profile  # Include profile for enhanced model selection
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
    
    async def _fetch_multiple_quarters_fmp_data(self, ticker: str, quarters: int) -> List[FMPRatiosData]:
        """Fetch multiple quarters of financial data from FMP API."""
        try:
            logger.info(f"Fetching {quarters} quarters of financial data for {ticker}")
            
            # Get multiple periods of financial statements and ratios
            ratios_list = self.fmp_fetcher.get_financial_ratios(ticker, period="quarter", limit=quarters)
            income_list = self.fmp_fetcher.get_income_statement(ticker, period="quarter", limit=quarters)
            balance_list = self.fmp_fetcher.get_balance_sheet(ticker, period="quarter", limit=quarters)
            company_profile = self.fmp_fetcher.get_company_profile(ticker)
            
            if not ratios_list or not income_list or not balance_list:
                raise DataFetchError(f"Incomplete FMP multi-quarter data for {ticker}")
            
            # Extract company name from profile
            company_name = None
            if company_profile and len(company_profile) > 0:
                company_name = company_profile[0].get('companyName', ticker)
            
            fmp_data_list = []
            # Process each quarter (limit to requested quarters or available data)
            max_quarters = min(quarters, len(ratios_list), len(income_list), len(balance_list))
            logger.info(f"Processing {max_quarters} quarters of data for {ticker}")
            
            for i in range(max_quarters):
                ratios = ratios_list[i]
                income_stmt = income_list[i]
                balance_sheet = balance_list[i]
                
                # Calculate Z-Score ratios from raw financial data for this quarter
                total_assets = balance_sheet.get('totalAssets', 0)
                current_assets = balance_sheet.get('totalCurrentAssets', 0)
                current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
                retained_earnings = balance_sheet.get('retainedEarnings', 0)
                ebit = income_stmt.get('operatingIncome', 0)  # EBIT approximation
                revenue = income_stmt.get('revenue', 0)
                
                # Calculate working capital ratio (X1)
                working_capital = current_assets - current_liabilities
                working_capital_ratio = working_capital / total_assets if total_assets > 0 else None
                
                # Calculate retained earnings ratio (X2)
                retained_earnings_ratio = retained_earnings / total_assets if total_assets > 0 else None
                
                # Calculate EBIT ratio (X3)
                ebit_ratio = ebit / total_assets if total_assets > 0 else None
                
                # Calculate sales ratio (X5)
                sales_ratio = revenue / total_assets if total_assets > 0 else None
                
                # Get market value from ratios or calculate fallback
                market_value_equity_ratio = ratios.get('marketCapitalizationToTotalAssets')
                if market_value_equity_ratio is None:
                    # Try alternative calculation
                    market_cap = ratios.get('marketCap')
                    if market_cap and total_assets > 0:
                        market_value_equity_ratio = market_cap / total_assets
                
                # Create FMPRatiosData for this quarter
                period_date = balance_sheet.get('date', 'Unknown')
                fmp_data = FMPRatiosData(
                    working_capital_ratio=working_capital_ratio,
                    retained_earnings_ratio=retained_earnings_ratio,
                    ebit_ratio=ebit_ratio,
                    asset_turnover=sales_ratio,  # Sales to total assets is asset turnover
                    company_name=company_name,
                    raw_ratios={
                        'ratios': ratios,
                        'income_statement': income_stmt,
                        'balance_sheet': balance_sheet,
                        'period_ending': period_date,
                        'market_value_equity_to_total_liabilities': market_value_equity_ratio,
                        'profile': company_profile  # Include profile for enhanced model selection
                    }
                )
                
                fmp_data_list.append(fmp_data)
                
            logger.info(f"Successfully processed {len(fmp_data_list)} quarters for {ticker}")
            return fmp_data_list
            
        except Exception as e:
            logger.error(f"Failed to fetch multiple quarters data for {ticker}: {e}")
            raise DataFetchError(f"Multi-quarter data fetch failed for {ticker}: {str(e)}")
    
    def _integrate_data_sources(self, ticker: str, fmp_data: FMPRatiosData, 
                               yahoo_data: YahooMarketData, logo_url: Optional[str] = None, 
                               logo_file_path: Optional[str] = None) -> MergedFinancialData:
        """
        Integrate FMP ratios with Yahoo market data and Finnhub logo.
        
        Strategic advantage: Uses calculated ratios from FMP financial statements
        combined with Yahoo market data and enhanced with Finnhub company branding.
        """
        # Extract the period date from FMP data, fallback to current time if not available
        period_date = None
        if fmp_data.raw_ratios and 'balance_sheet' in fmp_data.raw_ratios:
            period_date = fmp_data.raw_ratios['balance_sheet'].get('date')
        elif fmp_data.raw_ratios and 'period_ending' in fmp_data.raw_ratios:
            period_date = fmp_data.raw_ratios['period_ending']
        
        # Use period date if available, otherwise current timestamp
        timestamp = period_date if period_date else datetime.now().isoformat()
        
        return MergedFinancialData(
            ticker=ticker,
            timestamp=timestamp,
            
            # Z-Score ratios (calculated from FMP data)
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
            raw_yahoo_data=yahoo_data.raw_data,
            
            # Include company name, logo URL and cached logo file path in metadata
            metadata={
                **({'company_name': fmp_data.company_name} if fmp_data.company_name else {}),
                **({'logo_url': logo_url} if logo_url else {}),
                **({'logo_file_path': logo_file_path} if logo_file_path else {}),
                **({'period_date': period_date} if period_date else {})
            }
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
async def merge_financial_data(ticker: str, start_date: Optional[str] = None, quarters: int = 4) -> List[MergedFinancialData]:
    """
    Public interface for merging FMP and Yahoo data.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Optional start date filter
        quarters: Number of quarters for analysis (enhanced accounts: 8-20)
    
    Returns:
        List[MergedFinancialData] with integrated financial and market data
        
    Strategic Advantage:
        Uses FMP financial statements to calculate Z-Score ratios combined
        with Yahoo market data.
    """
    merger = DataMerger()
    return await merger.merge_financial_data(ticker, start_date, quarters)


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
