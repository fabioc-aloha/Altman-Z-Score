# fetch_prices.py
import warnings
import yfinance as yf
from datetime import datetime, timedelta
import logging
from time import sleep
import pandas as pd
from .api.yahoo_client import YahooFinanceClient, YahooFinanceError, YahooFinanceRateError
import requests # Added import for requests.exceptions.HTTPError

# Configure a specific logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set desired level for this logger
# Add a handler if not already configured by root logger, or to ensure output
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False # Prevent duplicate messages if root logger also has a handler

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
    
    # Initialize Yahoo Finance client with proper rate limiting
    client = YahooFinanceClient()
    
    last_error = None
    max_attempts = 3
    
    # Convert start and end dates to datetime
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    for attempt in range(max_attempts):
        try:
            # Get historical prices using the client
            df = client.get_historical_prices(
                ticker,
                start_dt,
                end_dt
            )
            
            # Verify we have valid data
            if not df.empty and len(df.index) > 0:
                return df
            
            # If we don't have data and have more attempts, increase buffer
            if attempt < max_attempts - 1:
                days_buffer *= 2
                start_dt = date_obj - timedelta(days=days_buffer)
                end_dt = date_obj + timedelta(days=days_buffer)
                sleep(2 ** attempt)  # Exponential backoff
                continue
                
        except YahooFinanceRateError as e:
            # Rate limit hit - wait and retry
            last_error = f"Rate limit error: {str(e)}"
            sleep(2 ** (attempt + 2))  # Longer wait for rate limits
            continue
            
        except YahooFinanceError as e:
            last_error = f"Yahoo Finance error: {str(e)}"
            if attempt < max_attempts - 1:
                sleep(2 ** attempt)  # Exponential backoff
                continue
            break  # Exit on persistent errors after max attempts
            
        except Exception as e:
            last_error = str(e)
            if attempt < max_attempts - 1:
                sleep(2 ** attempt)  # Exponential backoff
                continue
            break
    
    # If we get here, all attempts failed
    error_msg = f"No market data available for {ticker} around {date}"
    if last_error:
        error_msg += f": {last_error}"
    raise ValueError(error_msg)

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
    
    # Ensure df.index is a DatetimeIndex first.
    # yfinance history usually returns a DatetimeIndex, but let's be safe.
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception as e:
            raise ValueError(f"Could not convert DataFrame index to DatetimeIndex: {e}")

    # Now that we are sure df.index is a DatetimeIndex, we can safely access .dt properties or .tz
    # Convert target date to pandas Timestamp (timezone-naive by default)
    target_dt_naive = datetime.strptime(target_date, "%Y-%m-%d")
    target = pd.Timestamp(target_dt_naive)
    
    # Make df.index timezone-naive if it's timezone-aware to match target
    current_df_index = df.index
    if current_df_index.tz is not None:
        df.index = current_df_index.tz_localize(None)
    
    # Calculate the absolute difference in days using vectorized operations
    import numpy as np
    # Both df.index and target should now be timezone-naive
    time_deltas = (df.index - target).values.astype('timedelta64[D]')
    days_diff = np.abs(time_deltas.astype(float))
    
    # Get the index of minimum difference
    closest_idx = days_diff.argmin()
    
    # Get the Close price and convert to float
    price = df["Close"].iloc[closest_idx]
    if isinstance(price, pd.Series):
        price = price.iloc[0]
    return float(price)

def get_quarter_price_change(ticker: str, start: str, end: str) -> float | None:
    """
    Returns percentage price change for ticker from start to end date.
    Handles weekends and retries with expanded date range if needed.
    Returns None if data cannot be retrieved.
    """
    # Adjust for weekends
    start = get_last_business_day(start)
    end = get_last_business_day(end)
    
    try:
        # Get market data with a wider range to ensure we have data
        df = get_market_data(ticker, start, days_buffer=10) # This can raise ValueError
        
        # Get closest prices to start and end dates
        start_price = get_closest_price(df, start) # This can raise ValueError
        end_price = get_closest_price(df, end)   # This can raise ValueError
        
        if start_price == 0: # Avoid division by zero
            logger.warning(f"[{ticker}] Start price is zero on {start}, cannot calculate price change.")
            return None
            
        return (end_price - start_price) / start_price * 100
    except ValueError as e: # Catch ValueErrors from get_market_data or get_closest_price
        logger.warning(f"Error calculating price change for {ticker} ({start} to {end}): {str(e)}")
        return None
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error calculating price change for {ticker}: {str(e)}")
        return None

def get_market_value(ticker: str, date: str) -> float | None:
    """
    Get market value (shares * price) for a company on a specific date.
    Uses YahooFinanceClient for robust data fetching.
    Prioritizes marketCap from info, then calculates from sharesOutstanding, then fast_info.market_cap.
    Returns None if market value cannot be determined.
    """
    client = YahooFinanceClient()
    last_error_info = "No specific error during info fetch"

    MAX_INFO_FETCH_ATTEMPTS = 3
    INFO_RETRY_BASE_DELAY = getattr(client, 'MIN_REQUEST_INTERVAL', 2.0)

    historical_price = None
    try:
        df_prices = get_market_data(ticker, date, days_buffer=10) # Can raise ValueError
        if df_prices.empty:
            logger.warning(f"[{ticker}] No historical price data found around {date}. Market cap might be based solely on .info or .fast_info.")
        else:
            historical_price = get_closest_price(df_prices, date) # Can raise ValueError
            if pd.isna(historical_price) or historical_price <= 0:
                logger.warning(f"[{ticker}] Invalid or zero historical price ({historical_price}) on {date}. Market cap calculation will rely on .info or .fast_info if sharesOutstanding is used, or direct marketCap values.")
                historical_price = None # Ensure it's None if invalid
            else:
                logger.info(f"[{ticker}] Fetched historical price for {date}: {historical_price}")

    except ValueError as e:
        logger.warning(f"[{ticker}] Could not fetch historical price around {date}: {e}. Proceeding to fetch .info for marketCap.")
        # historical_price remains None

    info = None
    ticker_obj = client._get_ticker(ticker)

    for attempt in range(MAX_INFO_FETCH_ATTEMPTS):
        try:
            if not hasattr(ticker_obj, 'info'):
                logger.error(f"[{ticker}] Ticker object does not have an 'info' attribute. Attempt: {attempt + 1}")
                last_error_info = f"Ticker object for {ticker} invalid (no .info)."
                if attempt < MAX_INFO_FETCH_ATTEMPTS - 1:
                    sleep(INFO_RETRY_BASE_DELAY * (2 ** attempt))
                    ticker_obj = client._get_ticker(ticker) # Re-fetch ticker object
                    continue
                else:
                    break

            current_info = ticker_obj.info
            logger.debug(f"[{ticker}] Fetched ticker_obj.info (Attempt {attempt + 1}/{MAX_INFO_FETCH_ATTEMPTS}) - Type: {type(current_info)}, Value: {str(current_info)[:200]}...")

            if isinstance(current_info, dict):
                info = current_info
                logger.info(f"[{ticker}] Successfully fetched .info as a dictionary.")
                break
            else:
                last_error_info = f".info was not a dictionary (type: {type(current_info)}, value: {str(current_info)[:200]}...). Attempt {attempt + 1}"
                logger.warning(f"[{ticker}] {last_error_info}")
                if attempt < MAX_INFO_FETCH_ATTEMPTS - 1:
                    sleep(INFO_RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                else:
                    logger.error(f"[{ticker}] Failed to fetch valid .info dictionary after {MAX_INFO_FETCH_ATTEMPTS} attempts. Last type: {type(current_info)}")
                    break

        except requests.exceptions.HTTPError as http_err:
            last_error_info = f"HTTPError fetching .info for {ticker}: {http_err}. Attempt {attempt + 1}"
            logger.warning(last_error_info)
            if attempt < MAX_INFO_FETCH_ATTEMPTS - 1:
                sleep(INFO_RETRY_BASE_DELAY * (2 ** attempt))
                continue
            else:
                break
        except Exception as e: # Catching broader exceptions during .info fetch
            last_error_info = f"General error fetching .info for {ticker}: {e}. Attempt {attempt + 1}"
            logger.warning(last_error_info)
            if attempt < MAX_INFO_FETCH_ATTEMPTS - 1:
                sleep(INFO_RETRY_BASE_DELAY * (2 ** attempt))
                continue
            else:
                break
    
    market_cap = None

    # 1. Try marketCap from .info
    if info and isinstance(info, dict):
        market_cap_from_info = info.get('marketCap')
        if market_cap_from_info is not None and isinstance(market_cap_from_info, (int, float)) and market_cap_from_info > 0:
            logger.info(f"[{ticker}] Using marketCap from .info: {market_cap_from_info}")
            market_cap = float(market_cap_from_info)
        else:
            logger.warning(f"[{ticker}] marketCap from .info is invalid or not found (value: {market_cap_from_info}, type: {type(market_cap_from_info)}). Will try other methods.")
    else:
        logger.warning(f"[{ticker}] .info is not a valid dictionary or not available. Skipping direct marketCap from .info. Last .info error/state: {last_error_info}")

    # 2. If market_cap not found or invalid, try sharesOutstanding * historical_price
    if market_cap is None:
        logger.info(f"[{ticker}] Attempting market cap calculation: sharesOutstanding * historical_price.")
        if info and isinstance(info, dict) and historical_price is not None:
            shares_outstanding = info.get('sharesOutstanding')
            logger.info(f"[{ticker}] .info sharesOutstanding: {shares_outstanding} (type: {type(shares_outstanding)}), historical_price: {historical_price}")
            if shares_outstanding is not None and isinstance(shares_outstanding, (int, float)) and shares_outstanding > 0:
                calculated_market_cap = float(shares_outstanding * historical_price)
                logger.info(f"[{ticker}] Using calculated market cap (sharesOutstanding * historical_price): {shares_outstanding} * {historical_price} = {calculated_market_cap}")
                market_cap = calculated_market_cap
            else:
                logger.warning(f"[{ticker}] sharesOutstanding from .info is invalid/not found (value: {shares_outstanding}) or historical_price ({historical_price}) is invalid. Cannot calculate market cap this way.")
        elif not (info and isinstance(info, dict)):
            logger.warning(f"[{ticker}] .info is not a valid dictionary. Cannot use sharesOutstanding. Last .info error/state: {last_error_info}")
        elif historical_price is None:
            logger.warning(f"[{ticker}] Historical price is not available. Cannot use sharesOutstanding.")

    # 3. If still no market_cap, try fast_info.market_cap as a fallback
    if market_cap is None:
        logger.info(f"[{ticker}] Attempting market cap from .fast_info.")
        try:
            # Ensure ticker_obj is valid before accessing fast_info
            if ticker_obj and hasattr(ticker_obj, 'fast_info'):
                fast_market_cap = ticker_obj.fast_info.market_cap
                logger.info(f"[{ticker}] .fast_info.market_cap: {fast_market_cap} (type: {type(fast_market_cap)})")
                if fast_market_cap is not None and isinstance(fast_market_cap, (int, float)) and fast_market_cap > 0:
                    logger.info(f"[{ticker}] Using market_cap from .fast_info: {fast_market_cap}")
                    market_cap = float(fast_market_cap)
                else:
                    logger.warning(f"[{ticker}] market_cap from .fast_info is invalid or not found (value: {fast_market_cap}).")
            else:
                logger.warning(f"[{ticker}] Ticker object or .fast_info attribute not available. Cannot use .fast_info.market_cap.")
        except Exception as e:
            logger.warning(f"[{ticker}] Error accessing .fast_info.market_cap: {e}")

    if market_cap is not None and market_cap > 0:
        logger.info(f"[{ticker}] Successfully determined market_cap: {market_cap}")
        return market_cap
    else:
        error_msg = f"[{ticker}] Failed to retrieve a valid market capitalization on {date} after all attempts. Last .info error/state: {last_error_info}. Historical price was: {historical_price}."
        logger.error(error_msg)
        return None # Return None instead of raising ValueError

def get_start_end_prices(ticker: str, start_date: str, end_date: str) -> tuple[float | None, float | None]:
    """
    Get start and end prices for a ticker between two dates.
    Returns (None, None) if data cannot be retrieved.
    """
    client = YahooFinanceClient()
    
    try:
        # Get historical prices using the client
        df = client.get_historical_prices(
            ticker,
            datetime.strptime(start_date, "%Y-%m-%d"),
            datetime.strptime(end_date, "%Y-%m-%d")
        ) # This can raise YahooFinanceError or YahooFinanceRateError
        
        if df is None or df.empty:
            logger.warning(f"No price data available for {ticker} between {start_date} and {end_date}")
            return None, None
        
        start_price_val = None
        end_price_val = None
        
        try:
            if not df['Close'].empty:
                start_price_val = float(df['Close'].iloc[0])
                end_price_val = float(df['Close'].iloc[-1])
            else:
                logger.warning(f"Price data for {ticker} is empty after fetching.")
                return None, None

            return start_price_val, end_price_val
            
        except (IndexError, KeyError, TypeError) as e: # Added TypeError for float conversion
            logger.warning(f"Error accessing price data for {ticker}: {str(e)}")
            return None, None # Return None for prices on error
            
    except (YahooFinanceRateError, YahooFinanceError) as e: # Catch specific client errors
        logger.warning(f"Yahoo Finance API error for {ticker}: {str(e)}")
        return None, None
    except ValueError as e: # Catch date parsing errors or other ValueErrors
        logger.warning(f"ValueError fetching price data for {ticker}: {str(e)}")
        return None, None
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error fetching start/end prices for {ticker}: {str(e)}")
        return None, None
