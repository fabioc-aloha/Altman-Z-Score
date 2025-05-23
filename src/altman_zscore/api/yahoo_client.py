"""
Yahoo Finance client for Altman Z-Score pipeline (MVP scaffold).
"""

import yfinance as yf


class YahooFinanceClient:
    def get_market_cap_on_date(self, ticker, date, span_days=30):
        """
        Fetch market cap for a ticker on a given date using yfinance (default session/user agent).
        Tries a window of +/- span_days around the date for available price data.
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
                    if actual_date != date:
                        print(f"[WARN] No price data for {ticker} on {date} (possibly weekend/holiday). Using previous trading day: {actual_date}.")
                    return float(shares) * float(close), actual_date
            mcap = ticker_obj.info.get("marketCap")
            if mcap:
                print(f"[WARN] No price data for {ticker} near {date}. Using latest available market cap.")
                return float(mcap), None
        except Exception as e:
            print(f"[DEBUG] yfinance error for {ticker} on {date}: {e}")
        return None, None
