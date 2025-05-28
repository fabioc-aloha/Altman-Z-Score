"""
Market price data fetching utilities for Altman Z-Score analysis.

This module provides functions to retrieve historical stock price data
using yfinance API, with retry logic and validation to handle edge cases.
It supports fetching prices for specific dates and calculating price changes.

Note: This code follows PEP 8 style guidelines.
"""
import warnings
import yfinance as yf
from datetime import datetime, timedelta
import logging
from time import sleep
import pandas as pd
import numpy as np
import os
import json
from altman_zscore.utils.paths import get_output_dir

# Filter out yfinance warnings related to auto_adjust changes
warnings.filterwarnings('ignore', category=UserWarning, module='yfinance')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

# DEPRECATED: All price data fetching and saving functions have been moved to data_fetching/prices.py
# Please import from altman_zscore.data_fetching.prices instead.

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
        
    try:
        # Convert target date to datetime
        target = pd.to_datetime(target_date)
        
        # Find the closest date using pandas date index
        closest_idx = df.index.get_indexer([target], method='nearest')[0]
        
        # Since yfinance now uses auto_adjust=True by default, we use Adj Close
        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            
        price = df[close_col].iloc[closest_idx]  # Get scalar value
        return float(price)  # Convert to native Python float
        
    except Exception as e:
        raise ValueError(f"Error getting closest price: {str(e)}")

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
    Get market value for a ticker on a given date.
    Tries different methods: total value, shares * price
    
    Args:
        ticker: Stock symbol
        date: Date in YYYY-MM-DD format
        
    Returns:
        float: Market value in millions of USD
        
    Raises:
        ValueError: If value cannot be calculated
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        shares = None
        # Get shares outstanding from most recent quarter
        try:
            financials = ticker_obj.quarterly_balance_sheet
            if not financials.empty:
                shares = financials.iloc[0].get('CommonStockSharesOutstanding')
        except Exception:
            pass  # Continue to alternative methods

        # Try enterprise value method first
        if not shares:  # Skip if we already have shares
            fast_info = getattr(ticker_obj, 'fast_info', None)
            if fast_info:
                ev = getattr(fast_info, 'enterprise_value', None)
                debt = getattr(fast_info, 'total_debt', 0) or 0
                cash = getattr(fast_info, 'total_cash', 0) or 0
                
                if ev is not None and all(isinstance(v, (int, float)) for v in [ev, debt, cash]):
                    market_cap = float(ev) - float(debt) + float(cash)
                    if market_cap > 0:
                        df = get_market_data(ticker, date)
                        # Since yfinance now uses auto_adjust=True by default, we use Adj Close
                        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
                        if close_col not in df.columns:
                            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
                        current_price = ticker_obj.info.get("regularMarketPrice")
                        if current_price:
                            historical_price = df[close_col].iloc[0]
                            return float(market_cap * (historical_price / current_price))
        
        if shares:
            # Get closing price for the date
            df = get_market_data(ticker, date)
            # Since yfinance now uses auto_adjust=True by default, we use Adj Close
            close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            if close_col not in df.columns:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            price = df[close_col].iloc[0]
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
        
    Notes:
        Uses pandas recommended float conversion to avoid FutureWarning.
        Values are extracted from DataFrames using .iloc[0] to ensure scalar values.
    """
    df = yf.download(ticker,
                     start=start_date,
                     end=end_date,
                     progress=False)
    
    if df is None or df.empty:
        raise ValueError(f"No price data available for {ticker}")
    
    try:
        # Since yfinance now uses auto_adjust=True by default, we use Adj Close
        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            
        # Use float(ser.iloc[0]) to avoid FutureWarning
        # and ensure type safety
        start_price = float(df[close_col].iloc[0])
        end_price = float(df[close_col].iloc[-1])
        return start_price, end_price
    except (IndexError, KeyError) as e:
        raise ValueError(f"Error accessing price data for {ticker}: {str(e)}")

def get_quarterly_prices(ticker: str, quarters_list) -> pd.DataFrame:
    """
    Get stock prices for a list of quarter end dates.
    
    Args:
        ticker: Stock symbol
        quarters_list: List of quarter end dates (can be strings or datetime)
        
    Returns:
        pd.DataFrame: DataFrame with 'quarter_end' and 'price' columns
        
    Raises:
        ValueError: If prices cannot be fetched
    """
    results = []
    for quarter_end in quarters_list:
        quarter_date = None  # Initialize quarter_date to avoid unbound variable issue
        try:
            # Ensure date is in string format (YYYY-MM-DD) without time component
            if isinstance(quarter_end, str):
                # Remove any time component if present
                quarter_date = quarter_end.split()[0]
            else:
                # For datetime objects, format to string without time component
                quarter_date = pd.to_datetime(quarter_end).strftime('%Y-%m-%d')
                
            # Get market data for the quarter end date
            df = get_market_data(ticker, quarter_date)
            price = get_closest_price(df, quarter_date)
            
            results.append({
                'quarter_end': pd.to_datetime(quarter_date),
                'price': price
            })
        except Exception as e:
            # Use quarter_end if quarter_date is None (conversion failed)
            error_date = quarter_date if quarter_date else str(quarter_end)
            print(f"[WARN] Could not fetch price for {ticker} on {error_date}: {str(e)}")
    
    if not results:
        raise ValueError(f"Could not fetch any prices for {ticker}")
    
    return pd.DataFrame(results)

def get_monthly_price_stats(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get monthly price statistics (average, min, max) for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        pd.DataFrame: DataFrame with columns:
            - month (datetime): First day of each month
            - avg_price (float): Average closing price for the month
            - min_price (float): Minimum closing price for the month
            - max_price (float): Maximum closing price for the month
            - days_with_data (int): Number of trading days with data
            
    Raises:
        ValueError: If no data is available for the specified period
    """
    # Validate dates
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    if end < start:
        raise ValueError(f"End date {end_date} is before start date {start_date}")
    
    # Initialize df to None before the try block
    df = None
    
    try:
        # Fetch daily data with retries
        for attempt in range(3):
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    break
                if attempt < 2:
                    sleep(2 ** attempt)  # Exponential backoff
            except Exception:
                if attempt < 2:
                    sleep(2 ** attempt)
                continue
                
        # Verify we have valid data
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(f"No price data available for {ticker} between {start_date} and {end_date}")
            
        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            # Find the Close or Adj Close column
            close_cols = [c for c in df.columns if c[0] in ('Close', 'Adj Close')]
            if not close_cols:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            close_col = close_cols[0]  # Use the first one found
            df = df[close_col]  # Select just the close price series
        else:
            # For single-level columns, keep original logic
            close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            if close_col not in df.columns:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            df = df[close_col]
            
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
            
        # Create month column for grouping (first day of each month)
        month_series = df.index.to_period('M').astype(str)
        month_dates = pd.to_datetime(month_series) + pd.offsets.MonthBegin(0)
        
        # Calculate monthly statistics
        monthly_stats = pd.DataFrame({
            'month': month_dates,
            'price': df
        }).groupby('month').agg({
            'price': ['mean', 'min', 'max', 'count']
        }).reset_index()
        
        # Flatten the multi-level columns and rename
        monthly_stats.columns = ['month', 'avg_price', 'min_price', 'max_price', 'days_with_data']
        
        # Validate results
        if monthly_stats.empty:
            raise ValueError(f"No monthly statistics could be calculated for {ticker}")
            
        return monthly_stats
        
    except Exception as e:
        raise ValueError(f"Error fetching monthly price statistics for {ticker}: {str(e)}")

def save_price_data_to_disk(df: pd.DataFrame, ticker: str, output_dir: str, file_prefix: str) -> tuple[str, str]:
    """
    Save price data DataFrame to disk in CSV and JSON formats.
    
    Args:
        df (pd.DataFrame): DataFrame containing price data
        ticker (str): Ticker symbol
        output_dir (str): Output directory path
        file_prefix (str): Prefix for the output filename
    
    Returns:
        tuple[str, str]: Tuple containing paths to the CSV and JSON files
    
    Raises:
        IOError: If there's an error saving the files
    """
    if df is None or df.empty:
        raise ValueError("No price data to save")
    
    # Get output directory
    output_dir = get_output_dir()
    
    # Define file paths
    csv_path = os.path.join(output_dir, f"{file_prefix}_{ticker.lower()}.csv")
    json_path = os.path.join(output_dir, f"{file_prefix}_{ticker.lower()}.json")
    
    try:
        # Convert datetime columns to string for JSON serialization
        df_copy = df.copy()
        datetime_cols = [col for col in df_copy.columns if pd.api.types.is_datetime64_any_dtype(df_copy[col])]
        for col in datetime_cols:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
            
        # Save to CSV
        df_copy.to_csv(csv_path, index=False)
        
        # Save to JSON (orient='records' for list of objects)
        with open(json_path, 'w') as f:
            json_str = df_copy.to_json(orient='records', date_format='iso')
            # Parse and re-dump to format the JSON with indentation
            json.dump(json.loads(json_str), f, indent=2)
            
        return csv_path, json_path
    except Exception as e:
        raise IOError(f"Error saving price data to disk: {str(e)}")
