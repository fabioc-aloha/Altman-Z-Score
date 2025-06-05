"""
Yahoo Finance client for Altman Z-Score pipeline (MVP scaffold).
"""

import yfinance as yf
from altman_zscore.utils.paths import get_output_dir


class YahooFinanceClient:
    def get_market_cap_on_date(self, ticker, date, span_days=30, save_to_file=False):
        """
        Fetch market cap for a ticker on a given date using yfinance (default session/user agent).
        Tries a window of +/- span_days around the date for available price data.
        Optionally save the result to output/{TICKER}/market_cap.json.
        Returns (market cap as float, actual_date) or (None, None) if unavailable.
        Warns if fallback to a different date is used.
        """
        import datetime

        try:
            ticker_obj = yf.Ticker(ticker)
            # Try a window of +/- span_days
            start = date - datetime.timedelta(days=span_days)
            end = date + datetime.timedelta(days=span_days)
            hist = ticker_obj.history(period="1d", start=start, end=end)
            if not hist.empty:
                # Find the row closest to the requested date, but prefer the most recent previous trading day if possible
                hist = hist.sort_index()
                # Only consider dates <= requested date, if available
                prior_dates = [d for d in hist.index if d.date() <= date]
                if prior_dates:
                    closest_idx = max(prior_dates)
                else:
                    # If no prior dates, use the closest available
                    closest_idx = min(hist.index, key=lambda d: abs(d.date() - date))
                shares = ticker_obj.info.get("sharesOutstanding")
                close = hist.loc[closest_idx]["Close"]
                if shares and close:
                    actual_date = closest_idx.date()
                    result = {"market_cap": float(shares) * float(close), "actual_date": str(actual_date)}
                    if save_to_file:
                        import json
                        out_path = get_output_dir("market_cap.json", ticker=ticker)
                        with open(out_path, "w", encoding="utf-8") as f:
                            json.dump(result, f, indent=2, ensure_ascii=False)
                    return result["market_cap"], actual_date
            mcap = ticker_obj.info.get("marketCap")
            if mcap:
                result = {"market_cap": float(mcap), "actual_date": None}
                if save_to_file:
                    import json
                    out_path = get_output_dir("market_cap.json", ticker=ticker)
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                return float(mcap), None
        except Exception:
            pass
        return None, None
