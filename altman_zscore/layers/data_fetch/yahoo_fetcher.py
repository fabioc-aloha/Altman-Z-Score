"""
Yahoo Finance Data Fetcher - Layer 1

Yahoo Finance API data fetcher with 48-hour caching for market data.
All API calls are cached to prevent redundant downloads within the TTL period.

This fetcher handles:
- Market cap and price data
- Historical stock prices
- Cur        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached all historical prices for {symbol}")
            return cached_resultstock quotes
- Basic company information

Key Features:
- 48-hour cache TTL for all Yahoo Finance API calls
- Rate limiting integration
- Error handling and retries
- Focus on market data (not financial statements)
"""

import yfinance as yf
import pandas as pd
import time
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from ...common.logging_config import get_logger
from ...common.cache import get_cache, CacheBackend
# from ...common.api_rate_limiter import rate_limiter
from ...common.exceptions import DataFetchError

logger = get_logger(__name__)

# Cache TTL: 48 hours (in seconds)
CACHE_TTL_SECONDS = 48 * 60 * 60


@dataclass
class YahooConfig:
    """Yahoo Finance configuration."""
    timeout: int = 30
    max_retries: int = 3
    session_timeout: int = 300  # 5 minutes
    user_agent: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'YahooConfig':
        """Create config from environment variables."""
        user_agent = os.getenv("YAHOO_FINANCE_USER_AGENT")
        return cls(user_agent=user_agent)


class YahooDataFetcher:
    """
    Yahoo Finance data fetcher with caching.
    
    All API calls are cached for 48 hours to prevent redundant downloads.
    Focuses on market data only (prices, market cap, etc.).
    """
    
    def __init__(self, config: Optional[YahooConfig] = None):
        """
        Initialize Yahoo Finance data fetcher.
        
        Args:
            config: Optional Yahoo Finance configuration
        """
        self.config = config or YahooConfig.from_env()
        # Use pickle serialization for pandas DataFrames and complex objects
        self.cache = get_cache("yahoo_api", backend=CacheBackend.FILE, cache_dir=".cache/yahoo", serializer="pickle")
        
        # Set user agent for responsible API usage
        if self.config.user_agent:
            import yfinance as yf
            # Note: yfinance doesn't directly expose session headers, but we can set it globally
            logger.info(f"Yahoo Finance configured with user agent: {self.config.user_agent}")
        
        logger.info("Initialized Yahoo Finance data fetcher")
        
    def __direct_yahoo_call_get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        PRIVATE: Direct Yahoo Finance API call - only for internal use within this module.
        External code should use the cached get_market_data_summary() method instead!
        """
        logger.debug(f"Making direct Yahoo API call for ticker info: {symbol}")
        
        # Basic rate limiting - 0.5 seconds between requests (2 requests per second)
        time.sleep(0.5)
        
        for attempt in range(self.config.max_retries):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info:
                    raise DataFetchError(f"No data returned for {symbol}")
                
                # Check for error indicators
                if info.get('regularMarketPrice') is None and info.get('marketCap') is None:
                    raise DataFetchError(f"Invalid ticker or no market data for {symbol}")
                
                logger.debug(f"Successfully fetched Yahoo Finance info for {symbol}")
                return info
                
            except Exception as e:
                logger.warning(f"Yahoo API attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt == self.config.max_retries - 1:
                    raise DataFetchError(f"Failed to fetch data for {symbol} after {self.config.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return {}
        
    def __direct_yahoo_call_get_history(self, symbol: str, period: str = "max") -> Optional[pd.DataFrame]:
        """
        PRIVATE: Direct Yahoo Finance API call - only for internal use within this module.
        External code should use the cached get_historical_prices() method instead!
        """
        logger.debug(f"Making direct Yahoo API call for {symbol} history")
        
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        try:
            logger.info(f"Making direct API call for {symbol} with period {period}")
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            
            if not history.empty:
                logger.info(f"Successfully fetched {len(history)} historical records for {symbol}")
                return history
            else:
                logger.warning(f"No historical data returned for {symbol} with period {period}")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get historical prices for {symbol}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def __direct_yahoo_call_get_history_range(self, symbol: str, start_date: str, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        PRIVATE: Direct Yahoo Finance API call for date range - only for internal use within this module.
        External code should use the cached get_historical_prices_range() method instead!
        """
        logger.debug(f"Making direct Yahoo API call for {symbol} history range")
        
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        try:
            logger.info(f"Making direct API call for {symbol} from {start_date} to {end_date}")
            ticker = yf.Ticker(symbol)
            history = ticker.history(start=start_date, end=end_date)
            
            if not history.empty:
                logger.info(f"Successfully fetched {len(history)} historical records for {symbol} ({start_date} to {end_date})")
                return history
            else:
                logger.warning(f"No historical data returned for {symbol} from {start_date} to {end_date}")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get historical prices for {symbol} ({start_date} to {end_date}): {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Current price or None if not available
        """
        cache_key = f"yahoo_price:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached current price for {symbol}")
            return cached_result
        
        # Fetch from API
        try:
            info = self.__direct_yahoo_call_get_ticker_info(symbol)
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            
            if price is not None:
                # Cache result
                self.cache.set(cache_key, price, ttl=CACHE_TTL_SECONDS)
                return float(price)
            
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
        
        return None
    
    def get_market_cap(self, symbol: str) -> Optional[int]:
        """
        Get market capitalization with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Market cap in USD or None if not available
        """
        cache_key = f"yahoo_marketcap:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached market cap for {symbol}")
            return cached_result
        
        # Fetch from API
        try:
            info = self.__direct_yahoo_call_get_ticker_info(symbol)
            market_cap = info.get('marketCap')
            
            if market_cap is not None:
                # Cache result
                self.cache.set(cache_key, market_cap, ttl=CACHE_TTL_SECONDS)
                return int(market_cap)
            
        except Exception as e:
            logger.error(f"Failed to get market cap for {symbol}: {e}")
        
        return None
    
    def get_shares_outstanding(self, symbol: str) -> Optional[int]:
        """
        Get shares outstanding with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Shares outstanding or None if not available
        """
        cache_key = f"yahoo_shares:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached shares outstanding for {symbol}")
            return cached_result
        
        # Fetch from API
        try:
            info = self.__direct_yahoo_call_get_ticker_info(symbol)
            shares = info.get('sharesOutstanding') or info.get('impliedSharesOutstanding')
            
            if shares is not None:
                # Cache result
                self.cache.set(cache_key, shares, ttl=CACHE_TTL_SECONDS)
                return int(shares)
            
        except Exception as e:
            logger.error(f"Failed to get shares outstanding for {symbol}: {e}")
        
        return None
      # @rate_limiter.rate_limited("finance.yahoo.com")
    def get_historical_prices(self, symbol: str, period: str = "max") -> Optional[pd.DataFrame]:
        """
        Get historical price data with caching.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
            
        Returns:
            DataFrame with historical prices or None if not available
        """
        cache_key = f"yahoo_history:{symbol}:{period}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached historical prices for {symbol}")
            return cached_result
          # Fetch from API
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        try:
            logger.info(f"Fetching historical data for {symbol} with period {period}")
            history = self.__direct_yahoo_call_get_history(symbol, period)
            
            if history is not None and not history.empty:
                logger.info(f"Successfully fetched {len(history)} historical records for {symbol}")
                # Cache result
                self.cache.set(cache_key, history, ttl=CACHE_TTL_SECONDS)
                return history
            else:
                logger.warning(f"No historical data returned for {symbol} with period {period}")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get historical prices for {symbol}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def get_historical_prices_range(self, symbol: str, start_date: str, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Get historical price data for a specific date range with caching.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to today)
            
        Returns:
            DataFrame with historical prices or None if not available
        """
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        cache_key = f"yahoo_history_range:{symbol}:{start_date}:{end_date}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached historical prices for {symbol} ({start_date} to {end_date})")
            return cached_result
          
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        try:
            logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
            history = self.__direct_yahoo_call_get_history_range(symbol, start_date, end_date)
            
            if history is not None and not history.empty:
                logger.info(f"Successfully fetched {len(history)} historical records for {symbol} ({start_date} to {end_date})")
                # Cache result
                self.cache.set(cache_key, history, ttl=CACHE_TTL_SECONDS)
                return history
            else:
                logger.warning(f"No historical data returned for {symbol} from {start_date} to {end_date}")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get historical prices for {symbol} ({start_date} to {end_date}): {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None

    def get_all_historical_prices(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get all available historical price data with caching.
        This method fetches the maximum available data from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            DataFrame with all available historical prices or None if not available
        """
        cache_key = f"yahoo_history_all:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached all historical prices for {symbol}")
            return cached_result
          
        # Basic rate limiting - 0.5 seconds between requests
        time.sleep(0.5)
        
        try:
            logger.info(f"Fetching all available historical data for {symbol}")
            history = self.__direct_yahoo_call_get_history(symbol, "max")
            
            if history is not None and not history.empty:
                logger.info(f"Successfully fetched all available data: {len(history)} historical records for {symbol}")
                # Cache result
                self.cache.set(cache_key, history, ttl=CACHE_TTL_SECONDS)
                return history
            else:
                logger.warning(f"No historical data returned for {symbol} with max period")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get all historical prices for {symbol}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def get_market_data_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive market data summary with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Market data summary dictionary
        """
        cache_key = f"yahoo_summary:{symbol}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached market data summary for {symbol}")
            return cached_result
        
        # Collect market data
        summary = {
            'symbol': symbol,
            'current_price': self.get_current_price(symbol),
            'market_cap': self.get_market_cap(symbol),
            'shares_outstanding': self.get_shares_outstanding(symbol),
            'last_updated': datetime.now().isoformat()
        }
        
        # Add calculated fields
        if summary['market_cap'] and summary['current_price']:
            try:
                summary['book_value_per_share'] = summary['market_cap'] / summary['shares_outstanding'] if summary['shares_outstanding'] else None
            except (TypeError, ZeroDivisionError):
                summary['book_value_per_share'] = None
        
        # Cache result
        self.cache.set(cache_key, summary, ttl=CACHE_TTL_SECONDS)
        
        return summary

    def get_historical_market_data(self, symbol: str, date_str: str) -> Dict[str, Any]:
        """
        Get historical market data for a specific date.
        
        Args:
            symbol: Stock ticker symbol
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Dictionary with historical market data including price and estimated market cap
        """
        cache_key = f"yahoo_historical_market_data:{symbol}:{date_str}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached historical market data for {symbol} at {date_str}")
            return cached_result
        
        # Parse the target date
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Set up date range to search (7 days before and after target)
        start_date = (target_date - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (target_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        logger.info(f"Fetching historical market data for {symbol} around {date_str}")
        
        try:
            # Get historical prices for this period
            historical_df = self.get_historical_prices_range(symbol, start_date, end_date)
            
            if historical_df is None or historical_df.empty:
                raise DataFetchError(f"No historical data available for {symbol} around {date_str}")
            
            # Convert index to datetime if it's not already
            if not isinstance(historical_df.index, pd.DatetimeIndex):
                historical_df.index = pd.to_datetime(historical_df.index)
            
            # Find the closest date to our target
            closest_date = None
            min_delta = timedelta(days=999)
            
            for date_idx in historical_df.index:
                delta = abs(date_idx - target_date)
                if delta < min_delta:
                    min_delta = delta
                    closest_date = date_idx
            
            if closest_date is None:
                raise DataFetchError(f"Could not find close date match for {symbol} at {date_str}")
            
            # Get the row for this date
            closest_row = historical_df.loc[closest_date]
            
            # Get current data for share count and other info
            current_data = self.get_market_data_summary(symbol)
            
            # Create the historical market data
            historical_price = closest_row.get('Close')
            
            # Estimate historical market cap
            estimated_market_cap = None
            if historical_price is not None and current_data.get('shares_outstanding') is not None:
                # Assumes shares outstanding hasn't changed significantly
                estimated_market_cap = historical_price * current_data.get('shares_outstanding')
            
            # Build the result object
            result = {
                'date': closest_date.strftime("%Y-%m-%d"),
                'target_date': date_str,
                'days_difference': min_delta.days,
                'current_price': historical_price,
                'volume': closest_row.get('Volume'),
                'market_cap': estimated_market_cap,
                'shares_outstanding': current_data.get('shares_outstanding'),
                'is_estimated': True
            }
            
            # Cache the result
            self.cache.set(cache_key, result, ttl=CACHE_TTL_SECONDS)
            
            logger.info(f"Found historical market data for {symbol} at {result['date']} (target: {date_str})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get historical market data for {symbol} at {date_str}: {e}")
            
            # Return current data as fallback, but mark it as fallback
            try:
                current_data = self.get_market_data_summary(symbol)
                current_data['is_fallback'] = True
                current_data['target_date'] = date_str
                current_data['error'] = str(e)
                return current_data
            except:
                raise DataFetchError(f"Could not get historical or current market data for {symbol}")
