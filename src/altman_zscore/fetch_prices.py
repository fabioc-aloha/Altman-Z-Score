# fetch_prices.py
import warnings
import yfinance as yf
from datetime import datetime, timedelta
import logging
from time import sleep
import pandas as pd

# Filter out yfinance warnings related to auto_adjust changes
warnings.filterwarnings('ignore', category=UserWarning, module='yfinance')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

def get_last_business_day(date_str: str) -> str:
    """Convert a date string to the last business day if it falls on a weekend."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() > 4:  # 5 is Saturday, 6 is Sunday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

def get_market_data(ticker: str, date: str, days_buffer: int = 5) -> pd.DataFrame:
    """
    Get market data for a stock with retry logic and date buffer.
    Returns data frame with market data.
    
    Args:
        ticker: Stock symbol
        date: Target date in YYYY-MM-DD format
        days_buffer: Number of days to look before and after target date
    
    Returns:
        pd.DataFrame: DataFrame containing market data
        
    Raises:
        ValueError: If no data is available or if there's an error fetching data.
    """
    if not isinstance(date, str):
        raise ValueError("date must be a string in YYYY-MM-DD format")
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    start_date = (date_obj - timedelta(days=days_buffer)).strftime("%Y-%m-%d")
    end_date = (date_obj + timedelta(days=days_buffer)).strftime("%Y-%m-%d")
    
    df = pd.DataFrame()  # Initialize empty DataFrame
    
    last_error = None
    
    for attempt in range(3):
        try:
            # Download data
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            # Verify we have valid data
            if isinstance(df, pd.DataFrame) and not df.empty and len(df.index) > 0:
                return df
            
            # If we don't have data and have more attempts, increase buffer
            if attempt < 2:
                days_buffer *= 2
                start_date = (date_obj - timedelta(days=days_buffer)).strftime("%Y-%m-%d")
                end_date = (date_obj + timedelta(days=days_buffer)).strftime("%Y-%m-%d")
                sleep(2 ** attempt)  # Exponential backoff
                continue
                
        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                sleep(2 ** attempt)  # Exponential backoff
                continue
    
    # If we get here, all attempts failed
    error_msg = f"No market data available for {ticker} around {date}"
    if last_error:
        error_msg += f": {last_error}"
    raise ValueError(error_msg)
    
    raise ValueError(f"No market data available for {ticker} around {date}")

def get_closest_price(df: pd.DataFrame, target_date: str) -> float:
    """
    Get the closing price closest to the target date.
    
    Args:
        df: DataFrame with price data, must not be None or empty
        target_date: Date string in YYYY-MM-DD format
        
    Returns:
        float: The closest available closing price
        
    Raises:
        ValueError: If no price data is available
    """
    if df.empty:
        raise ValueError("No price data available")
    
    # Convert target date to pandas Timestamp for efficient comparison
    target = pd.Timestamp(target_date)
    
    # Ensure index is DatetimeIndex (more efficient than pd.to_datetime)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.DatetimeIndex(df.index)
    
    # Calculate the absolute difference in days using vectorized operations
    import numpy as np
    time_deltas = (df.index - pd.Timestamp(target)).values.astype('timedelta64[D]')
    days_diff = np.abs(time_deltas.astype(float))
    
    # Get the index of minimum difference
    closest_idx = days_diff.argmin()
    
    # Get the Close price and convert to float using pandas recommended method
    price = df["Close"].iloc[closest_idx]  # Get scalar value
    if isinstance(price, pd.Series):
        price = price.iloc[0]  # Convert Series to scalar if needed
    return float(price)

def get_quarter_price_change(ticker: str, start: str, end: str) -> float:
    """
    Returns percentage price change for ticker from start to end date.
    Handles weekends and retries with expanded date range if needed.
    """
    # Adjust for weekends
    start = get_last_business_day(start)
    end = get_last_business_day(end)
    
    try:
        # Get market data with a wider range to ensure we have data
        df = get_market_data(ticker, start, days_buffer=10)
        
        # Get closest prices to start and end dates
        start_price = get_closest_price(df, start)
        end_price = get_closest_price(df, end)
        
        return (end_price - start_price) / start_price * 100
    except Exception as e:
        raise ValueError(f"Error calculating price change for {ticker}: {str(e)}")

def get_market_value(ticker: str, date: str) -> float:
    """
    Get market value (shares * price) for a company on a specific date.
    """
    ticker_obj = yf.Ticker(ticker)
    
    try:
        # Try multiple methods to get market value
        
        # Method 1: Market Cap from info
        market_cap = ticker_obj.info.get("marketCap")
        if market_cap:
            # Get historical price for date adjustment
            current_price = ticker_obj.info.get("regularMarketPrice")
            if current_price:
                df = get_market_data(ticker, date)
                historical_price = get_closest_price(df, date)
                return float(market_cap * (historical_price / current_price))
        
        # Method 2: Daily Performance Data (updated daily by Yahoo)
        info = ticker_obj.info
        if "marketCap" in info and info["marketCap"] is not None:
            market_cap = float(info["marketCap"])
            if "regularMarketPrice" in info and info["regularMarketPrice"] is not None:
                current_price = float(info["regularMarketPrice"])
                if current_price > 0:
                    df = get_market_data(ticker, date)
                    historical_price = get_closest_price(df, date)
                    return float(market_cap * (historical_price / current_price))
        
        # Method 3: Shares * Price approach
        shares = None
        
        # Try direct shares outstanding
        shares = ticker_obj.info.get("sharesOutstanding")
        if not shares:
            shares = ticker_obj.info.get("impliedSharesOutstanding")
            
        # Try quarterly data
        if not shares:
            try:
                quarterly = ticker_obj.quarterly_balance_sheet
                if not quarterly.empty:
                    shares_cols = [col for col in quarterly.index if 'shares' in str(col).lower()]
                    if shares_cols:
                        shares = float(quarterly.loc[shares_cols[0]].iloc[0])
            except Exception:
                pass
                
        # Try float shares
        if not shares:
            shares = ticker_obj.info.get("floatShares")
            
        if not shares:
            # Try enterprise value approach
            ev = ticker_obj.info.get("enterpriseValue")
            debt = ticker_obj.info.get("totalDebt", 0)
            cash = ticker_obj.info.get("totalCash", 0)
            if ev is not None:
                market_cap = ev - debt + cash
                if market_cap > 0:
                    current_price = ticker_obj.info.get("regularMarketPrice")
                    if current_price:
                        df = get_market_data(ticker, date)
                        historical_price = get_closest_price(df, date)
                        return float(market_cap * (historical_price / current_price))
        
        if shares:
            # Get closing price for the date
            df = get_market_data(ticker, date)
            price = get_closest_price(df, date)
            return float(shares * price)
            
        raise ValueError(f"Could not fetch shares outstanding or market cap for {ticker}")
    except Exception as e:
        raise ValueError(f"Error calculating market value for {ticker}: {str(e)}")

def get_start_end_prices(ticker: str, start_date: str, end_date: str) -> tuple[float, float]:
    """
    Get start and end prices for a ticker between two dates.
    
    Args:
        ticker: Stock symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        tuple[float, float]: A tuple containing (start_price, end_price)
        
    Raises:
        ValueError: If no data is available or if there's an error accessing price data
    """
    df = yf.download(ticker,
                     start=start_date,
                     end=end_date,
                     progress=False)
    
    if df is None or df.empty:
        raise ValueError(f"No price data available for {ticker}")
    
    try:
        # Use float(ser.iloc[0]) to avoid FutureWarning
        # and ensure type safety
        start_price = float(df['Close'].iloc[0].iloc[0])
        end_price = float(df['Close'].iloc[-1].iloc[0])
        return start_price, end_price
    except (IndexError, KeyError) as e:
        raise ValueError(f"Error accessing price data for {ticker}: {str(e)}")
