"""
Price and market data fetching and saving utilities for Altman Z-Score analysis.
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

def get_last_business_day(date_str: str) -> str:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    while date.weekday() > 4:
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

def get_market_data(ticker: str, date: str, days_buffer: int = 5) -> pd.DataFrame:
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
                sleep(2 ** attempt)
                continue
        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                sleep(2 ** attempt)
                continue
    error_msg = f"No market data available for {ticker} around {date}"
    if last_error:
        error_msg += f": {last_error}"
    raise ValueError(error_msg)

def get_closest_price(df: pd.DataFrame, target_date: str) -> float:
    if df.empty:
        raise ValueError("No price data available")
    try:
        target = pd.to_datetime(target_date)
        closest_idx = df.index.get_indexer([target], method='nearest')[0]
        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
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
    try:
        ticker_obj = yf.Ticker(ticker)
        shares = None
        try:
            financials = ticker_obj.quarterly_balance_sheet
            if not financials.empty:
                shares = financials.iloc[0].get('CommonStockSharesOutstanding')
        except Exception:
            pass
        if not shares:
            fast_info = getattr(ticker_obj, 'fast_info', None)
            if fast_info:
                ev = getattr(fast_info, 'enterprise_value', None)
                debt = getattr(fast_info, 'total_debt', 0) or 0
                cash = getattr(fast_info, 'total_cash', 0) or 0
                if ev is not None and all(isinstance(v, (int, float)) for v in [ev, debt, cash]):
                    market_cap = float(ev) - float(debt) + float(cash)
                    if market_cap > 0:
                        df = get_market_data(ticker, date)
                        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
                        if close_col not in df.columns:
                            raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
                        current_price = ticker_obj.info.get("regularMarketPrice")
                        if current_price:
                            historical_price = df[close_col].iloc[0]
                            return float(market_cap * (historical_price / current_price))
        if shares:
            df = get_market_data(ticker, date)
            close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            if close_col not in df.columns:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            price = df[close_col].iloc[0]
            return float(shares * price)
        raise ValueError(f"Could not fetch shares outstanding or market cap for {ticker}")
    except Exception as e:
        raise ValueError(f"Error calculating market value for {ticker}: {str(e)}")

def get_start_end_prices(ticker: str, start_date: str, end_date: str) -> tuple[float, float]:
    df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise ValueError(f"No price data available for {ticker}")
    try:
        close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
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

def get_quarterly_prices(ticker: str, quarters_list) -> pd.DataFrame:
    results = []
    for quarter_end in quarters_list:
        quarter_date = None
        try:
            if isinstance(quarter_end, str):
                quarter_date = quarter_end.split()[0]
            else:
                quarter_date = pd.to_datetime(quarter_end).strftime('%Y-%m-%d')
            df = get_market_data(ticker, quarter_date)
            price = get_closest_price(df, quarter_date)
            results.append({
                'quarter_end': pd.to_datetime(quarter_date),
                'price': price
            })
        except Exception as e:
            error_date = quarter_date if quarter_date else str(quarter_end)
            print(f"[WARN] Could not fetch price for {ticker} on {error_date}: {str(e)}")
    if not results:
        raise ValueError(f"Could not fetch any prices for {ticker}")
    return pd.DataFrame(results)

def get_monthly_price_stats(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    if end < start:
        raise ValueError(f"End date {end_date} is before start date {start_date}")
    df = None
    try:
        for attempt in range(3):
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    break
                if attempt < 2:
                    sleep(2 ** attempt)
            except Exception:
                if attempt < 2:
                    sleep(2 ** attempt)
                continue
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(f"No price data available for {ticker} between {start_date} and {end_date}")
        if isinstance(df.columns, pd.MultiIndex):
            close_cols = [c for c in df.columns if c[0] in ('Close', 'Adj Close')]
            if not close_cols:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            close_col = close_cols[0]
            df = df[close_col]
        else:
            close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            if close_col not in df.columns:
                raise ValueError("Neither 'Close' nor 'Adj Close' column found in data")
            df = df[close_col]
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        month_series = df.index.to_period('M').astype(str)
        month_dates = pd.to_datetime(month_series) + pd.offsets.MonthBegin(0)
        monthly_stats = pd.DataFrame({
            'month': month_dates,
            'price': df
        }).groupby('month').agg({
            'price': ['mean', 'min', 'max', 'count']
        }).reset_index()
        monthly_stats.columns = ['month', 'avg_price', 'min_price', 'max_price', 'days_with_data']
        if monthly_stats.empty:
            raise ValueError(f"No monthly statistics could be calculated for {ticker}")
        return monthly_stats
    except Exception as e:
        raise ValueError(f"Error fetching monthly price statistics for {ticker}: {str(e)}")

def save_price_data_to_disk(df: pd.DataFrame, ticker: str, file_prefix: str) -> tuple[str, str]:
    if df is None or df.empty:
        raise ValueError("No price data to save")
        
    csv_path = get_output_dir(f"{file_prefix}.csv", ticker=ticker)
    json_path = get_output_dir(f"{file_prefix}.json", ticker=ticker)
    try:
        df_copy = df.copy()
        datetime_cols = [col for col in df_copy.columns if pd.api.types.is_datetime64_any_dtype(df_copy[col])]
        for col in datetime_cols:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
        df_copy.to_csv(csv_path, index=False)
        with open(json_path, 'w') as f:
            json_str = df_copy.to_json(orient='records', date_format='iso')
            json.dump(json.loads(json_str), f, indent=2)
        return csv_path, json_path
    except Exception as e:
        raise IOError(f"Error saving price data to disk: {str(e)}")
