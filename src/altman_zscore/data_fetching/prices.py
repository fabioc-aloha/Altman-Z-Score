"""
Price and market data fetching and saving utilities for Altman Z-Score analysis.

Provides functions to fetch, process, and save market price data for tickers, with robust error handling and fallback logic.
"""

import json
import warnings
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import yfinance as yf

from altman_zscore.utils.paths import get_output_dir
from altman_zscore.utils.io import save_dataframe, get_output_file_path

# Filter out yfinance warnings related to auto_adjust changes
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")
warnings.filterwarnings("ignore", message=".*auto_adjust.*")


def get_last_business_day(date_str: str) -> str:
    """Return the last business day (weekday) on or before the given date.

    Args:
        date_str (str): Date string in YYYY-MM-DD format.

    Returns:
        str: Last business day in YYYY-MM-DD format.
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() > 4:
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")


def get_market_data(ticker: str, date: str, days_buffer: int = 5) -> pd.DataFrame:
    """Fetch market data for a ticker around a target date using yfinance.

    Args:
        ticker (str): Stock ticker symbol.
        date (str): Target date in YYYY-MM-DD format.
        days_buffer (int, optional): Number of days before/after to include (default: 5).

    Returns:
        pd.DataFrame: DataFrame of market data.

    Raises:
        ValueError: If no data is available or download fails.
    """
    if not isinstance(date, str):
        raise ValueError("date must be a string in YYYY-MM-DD format")
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    start_date = (date_obj - timedelta(days=days_buffer)).strftime("%Y-%m-%d")
    end_date = (date_obj + timedelta(days=days_buffer)).strftime("%Y-%m-%d")
    df = pd.DataFrame()
    last_error = None
    for attempt in range(3):
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
            if isinstance(df, pd.DataFrame) and not df.empty and len(df.index) > 0:
                return df
            if attempt < 2:
                days_buffer *= 2
                start_date = (date_obj - timedelta(days=days_buffer)).strftime("%Y-%m-%d")
                end_date = (date_obj + timedelta(days=days_buffer)).strftime("%Y-%m-%d")
                sleep(2**attempt)
                continue
        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                sleep(2**attempt)
                continue
    error_msg = f"No market data available for {ticker} around {date}"
    if last_error:
        error_msg += f": {last_error}"
    raise ValueError(error_msg)


def get_market_data_with_fallback(ticker: str, date: str, days_buffer: int = 5) -> pd.DataFrame:
    """Try to fetch market data from yfinance, then fallback to other sources if needed.

    Args:
        ticker (str): Stock ticker symbol.
        date (str): Target date in YYYY-MM-DD format.
        days_buffer (int, optional): Number of days before/after to include (default: 5).

    Returns:
        pd.DataFrame: DataFrame of market data.

    Raises:
        ValueError: If all sources fail.
    """
    try:
        df = get_market_data(ticker, date, days_buffer)
        df._source = "yfinance"
        return df
    except Exception as e:
        # Try Alpha Vantage fallback (pseudo-code, requires API key and implementation)
        # try:
        #     df = get_alpha_vantage_data(ticker, date, days_buffer)
        #     df._source = 'alphavantage'
        #     return df
        # except Exception:
        #     pass
        # Try Stooq fallback (pseudo-code, requires implementation)
        # try:
        #     df = get_stooq_data(ticker, date, days_buffer)
        #     df._source = 'stooq'
        #     return df
        # except Exception:
        #     pass
        raise ValueError(f"All market data sources failed for {ticker} around {date}: {e}")


def get_closest_price(df: pd.DataFrame, target_date: str) -> float:
    """Get the price closest to the target date from a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame of price data.
        target_date (str): Target date in YYYY-MM-DD format.

    Returns:
        float: Closest price value.

    Raises:
        ValueError: If no price data is available or columns are missing.
    """
    if df.empty:
        raise ValueError("No price data available")
    try:
        target = pd.to_datetime(target_date)
        closest_idx = df.index.get_indexer([target], method="nearest")[0]
        close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
        price = df[close_col].iloc[closest_idx]
        # Fix for FutureWarning: float on single-element Series
        if isinstance(price, pd.Series):
            price = price.iloc[0]
        return float(price)
    except Exception as e:
        raise ValueError(f"Error getting closest price: {str(e)}")


def get_quarter_price_change(ticker: str, start: str, end: str) -> float:
    """Calculate the percentage price change for a ticker between two dates.

    Args:
        ticker (str): Stock ticker symbol.
        start (str): Start date in YYYY-MM-DD format.
        end (str): End date in YYYY-MM-DD format.

    Returns:
        float: Percentage price change.

    Raises:
        ValueError: If calculation fails.
    """
    start = get_last_business_day(start)
    end = get_last_business_day(end)
    try:
        df = get_market_data(ticker, start, days_buffer=10)
        start_price = get_closest_price(df, start)
        end_price = get_closest_price(df, end)
        return (end_price - start_price) / start_price * 100
    except Exception as e:
        raise ValueError(f"Error calculating price change for {ticker}: {str(e)}")


def get_market_value(ticker: str, date: str) -> float:
    """Estimate the market value of a ticker on a given date.

    Args:
        ticker (str): Stock ticker symbol.
        date (str): Target date in YYYY-MM-DD format.

    Returns:
        float: Estimated market value.

    Raises:
        ValueError: If calculation or data retrieval fails.
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        shares = None
        try:
            financials = ticker_obj.quarterly_balance_sheet
            if not financials.empty:
                shares = financials.iloc[0].get("CommonStockSharesOutstanding")
        except Exception:
            pass
        if not shares:
            fast_info = getattr(ticker_obj, "fast_info", None)
            if fast_info:
                ev = getattr(fast_info, "enterprise_value", None)
                debt = getattr(fast_info, "total_debt", 0) or 0
                cash = getattr(fast_info, "total_cash", 0) or 0
                if ev is not None and all(isinstance(v, (int, float)) for v in [ev, debt, cash]):
                    market_cap = float(ev) - float(debt) + float(cash)
                    if market_cap > 0:
                        df = get_market_data(ticker, date)
                        close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
                        if close_col not in df.columns:
                            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
                        current_price = ticker_obj.info.get("regularMarketPrice")
                        if current_price:
                            historical_price = df[close_col].iloc[0]
                            return float(market_cap * (historical_price / current_price))
        if shares:
            df = get_market_data(ticker, date)
            close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
            if close_col not in df.columns:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            price = df[close_col].iloc[0]
            return float(shares * price)
        raise ValueError(f"Could not fetch shares outstanding or market cap for {ticker}")
    except Exception as e:
        raise ValueError(f"Error calculating market value for {ticker}: {str(e)}")


def get_start_end_prices(ticker: str, start_date: str, end_date: str) -> tuple[float, float]:
    """Fetch the start and end prices for a ticker between two dates.

    Args:
        ticker (str): Stock ticker symbol.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        tuple[float, float]: Tuple containing start and end prices.

    Raises:
        ValueError: If no data is available or access to data fails.
    """
    df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise ValueError(f"No price data available for {ticker}")
    try:
        close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
        if close_col not in df.columns:
            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
        start_price = df[close_col].iloc[0]
        if isinstance(start_price, pd.Series):
            start_price = start_price.iloc[0]
        end_price = df[close_col].iloc[-1]
        if isinstance(end_price, pd.Series):
            end_price = end_price.iloc[0]
        return float(start_price), float(end_price)
    except (IndexError, KeyError) as e:
        raise ValueError(f"Error accessing price data for {ticker}: {str(e)}")


def get_weekly_price_stats(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get weekly OHLC price statistics for a stock.

    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        pd.DataFrame: DataFrame with columns:
            - week (datetime): First day of each week (Monday)
            - open_price (float): First close price of the week
            - high_price (float): Highest price of the week
            - low_price (float): Lowest price of the week
            - close_price (float): Last close price of the week
            - days_with_data (int): Number of trading days with data

    Raises:
        ValueError: If no data is available for the specified period
    """
    # Validate dates
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    if end < start:
        raise ValueError(f"End date {end_date} is before start date {start_date}")

    df = None
    try:
        # Fetch daily data with retries
        for attempt in range(3):
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    break
                if attempt < 2:
                    sleep(2**attempt)
            except Exception:
                if attempt < 2:
                    sleep(2**attempt)
                continue

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(f"No price data available for {ticker} between {start_date} and {end_date}")

        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            def find_col(name_opts):
                for opt in name_opts:
                    cols = [c for c in df.columns if c[0] == opt]
                    if cols:
                        return cols[0]
                return None

            open_col = find_col(["Open"])
            high_col = find_col(["High"])
            low_col = find_col(["Low"])
            close_col = find_col(["Adj Close", "Close"])
            if not all([open_col, high_col, low_col, close_col]):
                raise ValueError("Required OHLC columns not found in data")
            df = df[[open_col, high_col, low_col, close_col]]
            df.columns = ["Open", "High", "Low", "Close"]
        else:
            open_col = "Open"
            high_col = "High"
            low_col = "Low"
            close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
            for col in [open_col, high_col, low_col, close_col]:
                if col not in df.columns:
                    raise ValueError("Required OHLC columns not found in data")
            df = df[[open_col, high_col, low_col, close_col]]

        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index = pd.to_datetime(df.index)
        week_periods = df.index.to_period("W")
        df = df.assign(week_period=week_periods)

        weekly_stats = (
            df.groupby("week_period")
            .agg(
                open_price=("Open", "first"),
                high_price=("High", "max"),
                low_price=("Low", "min"),
                close_price=("Close", "last"),
                days_with_data=("Close", "count"),
            )
            .reset_index()
        )

        weekly_stats["week"] = weekly_stats["week_period"].apply(lambda x: x.start_time.date())

        if not isinstance(weekly_stats, pd.DataFrame):
            raise ValueError("Expected weekly_stats to be a DataFrame")

        weekly_stats = weekly_stats.loc[:, ["week", "open_price", "high_price", "low_price", "close_price", "days_with_data"]]

        # Validate results
        if weekly_stats.empty:
            raise ValueError(f"No weekly statistics could be calculated for {ticker}")

        return pd.DataFrame(weekly_stats)  # Ensure the return type is a DataFrame

    except Exception as e:
        raise ValueError(f"Error fetching weekly price statistics for {ticker}: {str(e)}")


def save_price_data_to_disk(df: pd.DataFrame, ticker: str, file_prefix: str) -> tuple[str, str]:
    """Save price data to disk as CSV and JSON files.

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        ticker (str): Stock ticker symbol.
        file_prefix (str): Prefix for output file names.

    Returns:
        tuple[str, str]: Tuple containing CSV and JSON file paths.

    Raises:
        ValueError: If no data is available to save.
        IOError: If file saving fails.
    """
    if df is None or df.empty:
        raise ValueError("No price data to save")
    csv_path = get_output_file_path(ticker, file_prefix, ext="csv")
    json_path = get_output_file_path(ticker, file_prefix, ext="json")
    try:
        df_copy = df.copy()
        datetime_cols = [col for col in df_copy.columns if pd.api.types.is_datetime64_any_dtype(df_copy[col])]
        for col in datetime_cols:
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")
        save_dataframe(df_copy, csv_path, fmt="csv")
        save_dataframe(df_copy, json_path, fmt="json")
        return csv_path, json_path
    except Exception as e:
        raise IOError(f"Error saving price data to disk: {str(e)}")
