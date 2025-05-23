"""
Yahoo Finance API client for fetching market data.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging
import time
from .metrics import YAHOO_API_REQUESTS, YAHOO_API_REQUEST_ERRORS, YAHOO_API_REQUEST_LATENCY
from ..schemas.yahoo import YahooMarketDataSchema
import yfinance as yf
import pandas as pd
from .rate_limiter import TokenBucket, RateLimitStrategy, RateLimitExceeded

logger = logging.getLogger(__name__)

class YahooFinanceError(Exception):
    """Base exception for Yahoo Finance API errors."""
    pass

class YahooFinanceRateError(YahooFinanceError):
    """Exception for rate limit errors."""
    pass

@dataclass
class MarketData:
    """Container for market-related data."""
    market_cap: Optional[Decimal] = None
    enterprise_value: Optional[Decimal] = None
    revenue_growth: Optional[float] = None
    operating_margin: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None

class YahooFinanceClient:
    """
    Client for fetching market data from Yahoo Finance.
    
    Handles:
    - Market data retrieval
    - Error recovery
    - Data validation
    - Caching (via yfinance)
    - Rate limiting
    """
    
    # Yahoo Finance recommended rate limit is 2000ms between requests
    REQUEST_RATE = 0.5  # requests per second (1/2000ms)
    MIN_REQUEST_INTERVAL = 2.0  # seconds
    
    def __init__(self):
        """Initialize Yahoo Finance client."""
        self.cache = {}  # Simple memory cache for ticker objects
        self.rate_limiter = TokenBucket(
            rate=self.REQUEST_RATE,
            capacity=1,  # Conservative capacity as this is an unofficial API
            strategy=RateLimitStrategy.WAIT
        )
        
    def _wait_for_rate_limit(self, timeout: Optional[float] = None) -> None:
        """
        Wait for rate limit with timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            YahooFinanceRateError: If rate limit timeout occurs
        """
        try:
            self.rate_limiter.acquire(timeout=timeout)
        except RateLimitExceeded as e:
            raise YahooFinanceRateError(f"Rate limit exceeded: {str(e)}")
            
    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """
        Get or create cached ticker object.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            yf.Ticker object
        """
        if symbol not in self.cache:
            self._wait_for_rate_limit()
            self.cache[symbol] = yf.Ticker(symbol)
        return self.cache[symbol]
        
    def get_market_data(self, symbol: str, timeout: float = 20.0) -> MarketData:
        """
        Get comprehensive market data for a company.
        
        Args:
            symbol: Stock symbol
            timeout: Request timeout in seconds
            
        Returns:
            MarketData object containing market information
        """
        start_time = time.time()
        # Fetch raw data
        try:
            # Wait for rate limit
            self._wait_for_rate_limit(timeout)
 
            ticker = self._get_ticker(symbol)
            info = ticker.info
            
            # Parse numeric fields safely
            try:
                market_cap = Decimal(str(info.get("marketCap", 0)))
            except (TypeError, ValueError):
                market_cap = None

            try:
                enterprise_value = Decimal(str(info.get("enterpriseValue", 0)))
            except (TypeError, ValueError):
                enterprise_value = None

            result = MarketData(
                market_cap=market_cap,
                enterprise_value=enterprise_value,
                revenue_growth=info.get("revenueGrowth"),
                operating_margin=info.get("operatingMargins"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                country=info.get("country")
            )
            # Validate with pydantic schema
            try:
                YahooMarketDataSchema(**result.__dict__)
            except Exception as e:
                YAHOO_API_REQUEST_ERRORS.labels(method='get_market_data', symbol=symbol, error='ValidationError').inc()
                raise YahooFinanceError(f"Validation error for market data of {symbol}: {e}")
             # Metrics on success
            YAHOO_API_REQUESTS.labels(method='get_market_data', symbol=symbol).inc()
            YAHOO_API_REQUEST_LATENCY.labels(method='get_market_data', symbol=symbol).observe(time.time() - start_time)
            return result
        except YahooFinanceRateError as e:
            YAHOO_API_REQUEST_ERRORS.labels(method='get_market_data', symbol=symbol, error=type(e).__name__).inc()
            raise
        except Exception as e:
            YAHOO_API_REQUEST_ERRORS.labels(method='get_market_data', symbol=symbol, error=type(e).__name__).inc()
            raise YahooFinanceError(f"Error fetching market data for {symbol}: {str(e)}")
        
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeout: float = 20.0
    ) -> pd.DataFrame:
        """
        Get historical price data.
        
        Args:
            symbol: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            timeout: Request timeout in seconds
            
        Returns:
            DataFrame containing historical price data
        """
        ticker = self._get_ticker(symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval="1d"
        )
        
        if df.empty:
            logger.warning(f"No price data found for {symbol}")
            return pd.DataFrame()
            
        return df
        
    def get_price_on_date(
        self,
        symbol: str,
        date: datetime,
        window_days: int = 5
    ) -> Optional[Decimal]:
        """
        Get closing price on or near a specific date.
        
        Args:
            symbol: Stock symbol
            date: Target date
            window_days: Number of days to look before/after target date
            
        Returns:
            Decimal price if found, None otherwise
        """
        start_date = date - timedelta(days=window_days)
        end_date = date + timedelta(days=window_days)
        
        df = self.get_historical_prices(symbol, start_date, end_date)
        if df.empty:
            return None
            
        # Calculate time difference using datetime values
        target_date = pd.Timestamp(date).to_pydatetime()
        df["date"] = df.index
        df["diff"] = df.index.map(lambda x: abs((x.to_pydatetime() - target_date).total_seconds()))
        closest_row = df.loc[df["diff"].idxmin()]
        
        try:
            return Decimal(str(closest_row["Close"]))
        except (KeyError, ValueError, TypeError):
            return None
