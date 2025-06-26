"""
Yahoo Finance client for Altman Z-Score pipeline (MVP scaffold).
"""

import time
import logging
from typing import Tuple, Optional
import yfinance as yf
from altman_zscore.utils.paths import get_output_dir

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    def __init__(self):
        """Initialize the Yahoo Finance client with retry settings."""
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _get_ticker_with_retry(self, ticker: str) -> Optional[yf.Ticker]:
        """Get ticker object with retry logic. Only logs an error if all retries fail."""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                ticker_obj = yf.Ticker(ticker)
                # Force a simple API call to test the connection
                _ = ticker_obj.fast_info
                if attempt > 0:
                    logger.debug(f"Successfully connected to Yahoo Finance API on attempt {attempt + 1}")
                return ticker_obj
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    logger.debug(f"Attempt {attempt + 1}/{self.max_retries} failed: {last_error}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        # Only log error when all retries have failed
        logger.error(f"Failed to initialize ticker after {self.max_retries} attempts. Last error: {last_error}")
        return None

    def get_market_cap_on_date(self, ticker: str, date, span_days=30, save_to_file=False) -> Tuple[Optional[float], Optional[str]]:
        """
        Fetch market cap for a ticker on a given date using yfinance with retry logic.
        Args:
            ticker: Stock symbol
            date: Target date
            span_days: Window of days to search around the target date
            save_to_file: Whether to save results to disk
        Returns:
            Tuple of (market_cap, actual_date) or (None, None) if unavailable
        """
        import datetime

        ticker_obj = self._get_ticker_with_retry(ticker)
        if not ticker_obj:
            return None, None

        try:
            # Try a window of +/- span_days
            start = date - datetime.timedelta(days=span_days)
            end = date + datetime.timedelta(days=span_days)
            hist = ticker_obj.history(period="1d", start=start, end=end)
            
            if not hist.empty:
                # Find the row closest to the requested date, but prefer the most recent previous trading day
                hist = hist.sort_index()
                # Only consider dates <= requested date, if available
                prior_dates = [d for d in hist.index if d.date() <= date]
                if prior_dates:
                    closest_idx = max(prior_dates)
                else:
                    # If no prior dates, use the closest available
                    closest_idx = min(hist.index, key=lambda d: abs(d.date() - date))
                
                # Try multiple methods to get shares outstanding
                shares = (
                    ticker_obj.info.get("sharesOutstanding") or
                    ticker_obj.info.get("currentPrice", 0) and ticker_obj.info.get("marketCap", 0) / ticker_obj.info.get("currentPrice", 0)
                )
                
                close = hist.loc[closest_idx]["Close"]
                if shares and close:
                    actual_date = closest_idx.date()
                    result = {"market_cap": float(shares) * float(close), "actual_date": str(actual_date)}
                    if save_to_file:
                        self._save_to_json(result, ticker, "market_cap.json")
                    return result["market_cap"], actual_date

            # Fallback to current market cap if historical calculation fails
            mcap = ticker_obj.info.get("marketCap")
            if mcap:
                result = {"market_cap": float(mcap), "actual_date": None}
                if save_to_file:
                    self._save_to_json(result, ticker, "market_cap.json")
                return float(mcap), None

        except Exception as e:
            logger.error(f"Error fetching market cap for {ticker}: {str(e)}")

        return None, None

    def _save_to_json(self, data: dict, ticker: str, filename: str) -> None:
        """Save data to JSON file."""
        import json
        out_path = get_output_dir(filename, ticker=ticker)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
