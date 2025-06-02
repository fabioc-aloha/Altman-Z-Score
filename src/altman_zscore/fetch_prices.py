"""
Market price data fetching utilities for Altman Z-Score analysis.

This module provides functions to retrieve historical stock price data
using the yfinance API, with retry logic and validation to handle edge cases.
It supports fetching prices for specific dates, calculating price changes, and saving data.

Functions:
    get_last_business_day(date_str): Convert a date string to the last business day if it falls on a weekend.
    get_market_data(ticker, date, days_buffer): Fetch market data for a stock with retry logic and date buffer.
    get_closest_price(df, target_date): Get the closing price closest to the target date.
    get_quarter_price_change(ticker, start, end): Calculate the percentage price change for a stock between two dates.
    get_start_end_prices(ticker, start_date, end_date): Retrieve the start and end prices for a stock between two dates.
    save_price_data_to_disk(df, ticker, file_prefix): Save price data DataFrame to disk in CSV and JSON formats.
"""

import json
import os
import warnings
from datetime import datetime, timedelta
from time import sleep
import time

import pandas as pd
import yfinance as yf

from altman_zscore.utils.paths import get_output_dir

# Filter out yfinance warnings related to auto_adjust changes
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")
warnings.filterwarnings("ignore", message=".*auto_adjust.*")


def get_last_business_day(date_str: str) -> str:
    """
    Convert a date string to the last business day if it falls on a weekend.

    Args:
        date_str (str): Date string in YYYY-MM-DD format.

    Returns:
        str: Adjusted date string representing the last business day.

    Raises:
        ValueError: If the input date string is not in the correct format.
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() > 4:  # 5 is Saturday, 6 is Sunday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")


def get_market_data(ticker: str, date: str, days_buffer: int = 5) -> pd.DataFrame:
    """
    Fetch market data for a stock with retry logic and date buffer.

    Args:
        ticker (str): Stock symbol.
        date (str): Target date in YYYY-MM-DD format.
        days_buffer (int): Number of days to look before and after the target date.

    Returns:
        pd.DataFrame: DataFrame containing market data.

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
                time.sleep(2**attempt)  # Exponential backoff
                continue

        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                time.sleep(2**attempt)  # Exponential backoff
                continue

    # If we get here, all attempts failed
    error_msg = f"No market data available for {ticker} around {date}"
    if last_error:
        error_msg += f": {last_error}"
    raise ValueError(error_msg)


def get_closest_price(df: pd.DataFrame, target_date: str) -> float:
    """
    Get the closing price closest to the target date.

    Args:
        df (pd.DataFrame): DataFrame with price data, must not be None or empty.
        target_date (str): Date string in YYYY-MM-DD format.

    Returns:
        float: The closest available closing price.

    Raises:
        ValueError: If no price data is available or if the target date is invalid.
    """
    if df.empty:
        raise ValueError("No price data available")

    try:
        # Convert target date to datetime
        target = pd.to_datetime(target_date)

        # Find the closest date using pandas date index
        closest_idx = df.index.get_indexer([target], method="nearest")[0]

        # Since yfinance now uses auto_adjust=True by default, we use Adj Close
        close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")

        price = df[close_col].iloc[closest_idx]  # Get scalar value
        return float(price)  # Convert to native Python float

    except Exception as e:
        raise ValueError(f"Error getting closest price: {str(e)}")


def get_quarter_price_change(ticker: str, start: str, end: str) -> float:
    """
    Calculate the percentage price change for a stock between two dates.

    Args:
        ticker (str): Stock symbol.
        start (str): Start date in YYYY-MM-DD format.
        end (str): End date in YYYY-MM-DD format.

    Returns:
        float: Percentage price change between the start and end dates.

    Raises:
        ValueError: If no data is available or if there's an error calculating the price change.
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


def get_start_end_prices(ticker: str, start_date: str, end_date: str) -> tuple[float, float]:
    """
    Retrieve the start and end prices for a stock between two dates.

    Args:
        ticker (str): Stock symbol.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        tuple[float, float]: A tuple containing the start and end prices.

    Raises:
        ValueError: If no data is available or if there's an error accessing price data.
    """
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df is None or df.empty:
        raise ValueError(f"No price data available for {ticker}")

    try:
        # Since yfinance now uses auto_adjust=True by default, we use Adj Close
        close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            # Use float(ser.iloc[0]) to avoid FutureWarning
        # and ensure type safety
        start_price = float(df[close_col].iloc[0])
        end_price = float(df[close_col].iloc[-1])
        return start_price, end_price
    except (IndexError, KeyError) as e:
        raise ValueError(f"Error accessing price data for {ticker}: {str(e)}")


def save_price_data_to_disk(df: pd.DataFrame, ticker: str, file_prefix: str) -> tuple[str, str]:
    """
    Save price data DataFrame to disk in CSV and JSON formats.

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        ticker (str): Stock symbol.
        file_prefix (str): Prefix for the output filename.

    Returns:
        tuple[str, str]: Tuple containing paths to the CSV and JSON files.

    Raises:
        ValueError: If the DataFrame is empty or None.
        IOError: If there's an error saving the files.
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
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")

        # Save to CSV
        df_copy.to_csv(csv_path, index=False)

        # Save to JSON (orient='records' for list of objects)
        with open(json_path, "w") as f:
            json_str = df_copy.to_json(orient="records", date_format="iso")
            # Parse and re-dump to format the JSON with indentation
            json.dump(json.loads(json_str), f, indent=2)

        return csv_path, json_path
    except Exception as e:
        raise IOError(f"Error saving price data to disk: {str(e)}")
