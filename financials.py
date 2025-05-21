import yfinance as yf
import pandas as pd
from typing import Iterable


def fetch_price_as_of(ticker: str, date: str) -> float:
    """Fetch the closing price for a ticker as of a specific date (or closest previous trading day)."""
    try:
        df = yf.download(
            ticker, end=pd.to_datetime(date) + pd.Timedelta(days=1), progress=False
        )
        if df.empty:
            return None
        # Get the last available close price on or before the date
        price = df.loc[df.index <= date, "Close"]
        if not price.empty:
            # Use .iloc[0] if only one value, else .iloc[-1] for the last available
            if len(price) == 1:
                return float(price.iloc[0])
            else:
                return float(price.iloc[-1])
        else:
            return None
    except Exception as e:
        print(f"[WARN] Could not fetch price for {ticker} as of {date}: {e}")
        return None


def analyze_ticker_financial_health(ticker: str, end_date: str) -> dict:
    """
    For a single ticker, determine the financials date, price as of financials date, price as of end date,
    YTD return (from financials date to end date), and Altman Z-score (using financials as of financials date).
    """
    try:
        stock = yf.Ticker(ticker)
        bs = stock.balance_sheet
        is_ = stock.financials
        info = stock.info
        col = bs.columns[0]  # Most recent financials date
        fin_date = str(col.date()) if hasattr(col, "date") else str(col)
        missing = []

        def get_field(df, *names):
            for name in names:
                if name in df.index:
                    return df.loc[name, col]
            missing.extend(names)
            return None

        wc = None
        tca = get_field(
            bs,
            "TotalCurrentAssets",
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Cash Equivalents",
        )
        tcl = get_field(bs, "TotalCurrentLiabilities", "Total Liabilities")
        if tca is not None and tcl is not None:
            wc = tca - tcl
        ta = get_field(bs, "TotalAssets", "Tangible Book Value")
        re = get_field(bs, "RetainedEarnings", "Net Income")
        tl = get_field(bs, "TotalLiab", "Total Debt")
        ebit = get_field(is_, "Ebit", "EBIT", "Operating Income")
        sales = get_field(is_, "TotalRevenue", "Operating Revenue")
        shares = info.get("sharesOutstanding")
        # Prices
        price_start = fetch_price_as_of(ticker, fin_date)
        price_end = fetch_price_as_of(ticker, end_date)
        # YTD return from financials date to end date
        ytd_return = None
        if price_start is not None and price_end is not None and price_start != 0:
            ytd_return = (price_end - price_start) / price_start * 100

        # Altman Z-score
        def safe_float(val):
            try:
                return float(val)
            except Exception:
                return None

        wc = safe_float(wc)
        ta = safe_float(ta)
        re = safe_float(re)
        tl = safe_float(tl)
        ebit = safe_float(ebit)
        sales = safe_float(sales)
        mve = safe_float(
            shares * price_start
            if shares is not None and price_start is not None
            else None
        )
        A = wc / ta if ta not in (None, 0) and wc is not None else None
        B = re / ta if ta not in (None, 0) and re is not None else None
        C = ebit / ta if ta not in (None, 0) and ebit is not None else None
        D = mve / tl if tl not in (None, 0) and mve is not None else None
        E = sales / ta if ta not in (None, 0) and sales is not None else None
        staleness_warning = ""
        try:
            fin_dt = pd.to_datetime(fin_date)
            end_dt = pd.to_datetime(end_date)
            if (end_dt - fin_dt).days > 183:
                staleness_warning = f"[WARN] Financials for {ticker} are more than 6 months older than price end date. "
                print(staleness_warning)
        except Exception:
            pass
        if None in (A, B, C, D, E):
            print(
                f"[WARN] Incomplete or alternative financials for {ticker}, cannot compute Z-score. Missing: {missing}"
            )
            z = None
            missing_fields = ", ".join(set(missing))
        else:
            z = 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E
            missing_fields = ""
        return {
            "Ticker": ticker,
            "Financials Date": fin_date,
            "Start Price": price_start,
            "End Price": price_end,
            "YTD % Change": round(ytd_return, 2) if ytd_return is not None else None,
            "Z-Score": round(z, 2) if z is not None else None,
            "Missing Fields": missing_fields,
            "Staleness Warning": staleness_warning,
        }
    except Exception as e:
        print(f"[WARN] Error analyzing {ticker}: {e}")
        return {
            "Ticker": ticker,
            "Financials Date": None,
            "Start Price": None,
            "End Price": None,
            "YTD % Change": None,
            "Z-Score": None,
            "Missing Fields": str(e),
            "Staleness Warning": "",
        }


def analyze_portfolio_financial_health(
    tickers: Iterable[str], end_date: str
) -> pd.DataFrame:
    records = [analyze_ticker_financial_health(ticker, end_date) for ticker in tickers]
    return pd.DataFrame(records)


def analyze_ticker_financial_health_last_n_filings(ticker: str, n: int = 3) -> list:
    """
    For a single ticker, analyze the last n financial filings (columns in balance_sheet),
    returning Z-score and price change for each period (from filing to next filing, or today for the most recent).
    Returns a list of dicts (one per period, most recent first).
    """
    try:
        stock = yf.Ticker(ticker)
        bs = stock.balance_sheet
        is_ = stock.financials
        info = stock.info
        cols = list(bs.columns)
        if len(cols) < 2:
            print(f"[WARN] Less than two financial filings for {ticker}.")
            return []
        results = []
        periods = min(n, len(cols))
        for i in range(periods):
            col = cols[i]
            fin_date = str(col.date()) if hasattr(col, "date") else str(col)
            missing = []

            def get_field(df, *names):
                for name in names:
                    if name in df.index:
                        return df.loc[name, col]
                missing.extend(names)
                return None

            wc = None
            tca = get_field(
                bs,
                "TotalCurrentAssets",
                "Cash Cash Equivalents And Short Term Investments",
                "Cash And Cash Equivalents",
            )
            tcl = get_field(bs, "TotalCurrentLiabilities", "Total Liabilities")
            if tca is not None and tcl is not None:
                wc = tca - tcl
            ta = get_field(bs, "TotalAssets", "Tangible Book Value")
            re = get_field(bs, "RetainedEarnings", "Net Income")
            tl = get_field(bs, "TotalLiab", "Total Debt")
            ebit = get_field(is_, "Ebit", "EBIT", "Operating Income")
            sales = get_field(is_, "TotalRevenue", "Operating Revenue")
            shares = info.get("sharesOutstanding")
            # Prices
            price_start = fetch_price_as_of(ticker, fin_date)
            # For price_end, use the next filing's date if available, else today
            if i + 1 < len(cols):
                price_end_date = cols[i + 1]
                price_end_date_str = (
                    str(price_end_date.date())
                    if hasattr(price_end_date, "date")
                    else str(price_end_date)
                )
                price_end = fetch_price_as_of(ticker, price_end_date_str)
            else:
                price_end_date = pd.Timestamp.today()
                price_end_date_str = price_end_date.strftime("%Y-%m-%d")
                price_end = fetch_price_as_of(ticker, price_end_date_str)
            # Return from this filing date to the next (or today)
            pct_change = None
            if price_start is not None and price_end is not None and price_start != 0:
                pct_change = (price_end - price_start) / price_start * 100

            # Altman Z-score
            def safe_float(val):
                try:
                    return float(val)
                except Exception:
                    return None

            wc = safe_float(wc)
            ta = safe_float(ta)
            re = safe_float(re)
            tl = safe_float(tl)
            ebit = safe_float(ebit)
            sales = safe_float(sales)
            mve = safe_float(
                shares * price_start
                if shares is not None and price_start is not None
                else None
            )
            A = wc / ta if ta not in (None, 0) and wc is not None else None
            B = re / ta if ta not in (None, 0) and re is not None else None
            C = ebit / ta if ta not in (None, 0) and ebit is not None else None
            D = mve / tl if tl not in (None, 0) and mve is not None else None
            E = sales / ta if ta not in (None, 0) and sales is not None else None
            staleness_warning = ""
            try:
                fin_dt = pd.to_datetime(fin_date)
                end_dt = (
                    pd.to_datetime(price_end_date)
                    if price_end_date is not None
                    else pd.Timestamp.today()
                )
                if (end_dt - fin_dt).days > 183:
                    staleness_warning = f"[WARN] Financials for {ticker} are more than 6 months older than price end date. "
                    print(staleness_warning)
            except Exception:
                pass
            if None in (A, B, C, D, E):
                print(
                    f"[WARN] Incomplete or alternative financials for {ticker}, cannot compute Z-score. Missing: {missing}"
                )
                z = None
                missing_fields = ", ".join(set(missing))
            else:
                z = 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E
                missing_fields = ""
            results.append(
                {
                    "Ticker": ticker,
                    "Financials Date": fin_date,
                    "Start Price": price_start,
                    "End Price": price_end,
                    "% Change": (
                        round(pct_change, 2) if pct_change is not None else None
                    ),
                    "Z-Score": round(z, 2) if z is not None else None,
                    "Missing Fields": missing_fields,
                    "Staleness Warning": staleness_warning,
                }
            )
        return results
    except Exception as e:
        print(f"[WARN] Error analyzing {ticker}: {e}")
        return []


def analyze_portfolio_financial_health_last_n_filings(
    tickers: Iterable[str], n: int = 3
) -> pd.DataFrame:
    records = []
    for ticker in tickers:
        records.extend(analyze_ticker_financial_health_last_n_filings(ticker, n=n))
    return pd.DataFrame(records)


def analyze_zscore_vs_price_change(df: pd.DataFrame, plot: bool = True):
    """
    Analyze and visualize the relationship between Z-score and % Change in price.
    Prints correlation and shows a scatter plot if plot=True.
    """
    import matplotlib.pyplot as plt

    # Filter out rows with missing Z-Score or % Change
    filtered = df.dropna(subset=["Z-Score", "% Change"])
    if filtered.empty:
        print("No valid data for Z-score vs. price change analysis.")
        return
    corr = filtered["Z-Score"].corr(filtered["% Change"])
    print(f"Correlation between Z-Score and % Price Change: {corr:.3f}")
    if plot:
        plt.figure(figsize=(8, 6))
        plt.scatter(filtered["Z-Score"], filtered["% Change"], alpha=0.7)
        plt.xlabel("Altman Z-Score")
        plt.ylabel("% Price Change (to next filing)")
        plt.title("Z-Score vs. Subsequent Price Change")
        plt.grid(True)
        plt.show()
