"""
GenAI Health Metrics
====================

This module calculates year-to-date (YTD) returns for a collection of public
generative AI-related companies using `yfinance` for data retrieval. It also
combines these returns with precomputed Altman Z-scores to provide a basic
financial health diagnostic.

Dependencies:
- pandas
- yfinance

Usage as a script will download price data for a set of default tickers
(between 2025-01-02 and 2025-05-20), merge the data with sample Z-scores,
print the results, and export them to `genai_health.csv` and
`genai_health.xlsx`.
"""

import pandas as pd
import yfinance as yf
from typing import Dict, Iterable, Optional


def calculate_ytd_returns(
    tickers: Optional[Iterable[str]] = None,
    start_date: str = "2025-01-02",
    end_date: str = "2025-05-20",
) -> pd.DataFrame:
    """Return YTD performance for the supplied tickers.

    Parameters
    ----------
    tickers : iterable of str, optional
        List of ticker symbols. Defaults to a set of top Gen-AI companies.
    start_date : str
        Start date in ``YYYY-MM-DD`` format.
    end_date : str
        End date in ``YYYY-MM-DD`` format.

    Returns
    -------
    pandas.DataFrame
        Columns: ``Ticker``, ``Start Price``, ``End Price``, ``YTD % Change``.
        Missing data results in ``None`` values.
    """

    default_tickers = [
        "MSFT","GOOGL","AMZN","META","IBM","ORCL","CRM","ADBE","SNOW","PLTR",
        "AI","SOUN","UPST","TWLO","OTEX","SPLK","ESTC","AYX","DDOG","PATH",
        "NOW","DOCU","INTU","SHOP","ZM","PINS","SNAP","LYFT","UBER","DASH",
        "CRWD","FTNT","PANW","CHKP","INTC","NVDA","AMD","AVGO","MU","TSM",
        "QCOM","MRVL","ANET","SMCI","NTES","BIDU","0700.HK","BABA"
    ]
    tickers = list(tickers) if tickers is not None else default_tickers

    # Request historical prices grouped by ticker to simplify lookup
    try:
        data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            group_by="ticker",
            progress=False,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to download prices: {exc}") from exc

    records = []
    for ticker in tickers:
        try:
            df = data[ticker]
            price_start = df.loc[start_date, "Close"]
            price_end = df.loc[end_date, "Close"]
            ytd_return = (price_end - price_start) / price_start * 100
            record = {
                "Ticker": ticker,
                "Start Price": float(price_start),
                "End Price": float(price_end),
                "YTD % Change": round(float(ytd_return), 2),
            }
        except Exception:
            record = {
                "Ticker": ticker,
                "Start Price": None,
                "End Price": None,
                "YTD % Change": None,
            }
        records.append(record)

    return pd.DataFrame(records)


def merge_z_and_diagnostic(df: pd.DataFrame, z_scores: Dict[str, float]) -> pd.DataFrame:
    """Merge Altman Z-scores with return data and add diagnostics.

    Parameters
    ----------
    df : pandas.DataFrame
        Output of :func:`calculate_ytd_returns`.
    z_scores : dict
        Mapping of ticker symbol to Altman Z-score.

    Returns
    -------
    pandas.DataFrame
        Input ``df`` augmented with ``Z-Score`` and ``Diagnostic`` columns.
    """

    def classify(z: Optional[float]) -> Optional[str]:
        if z is None:
            return None
        if z > 2.99:
            return "Safe Zone"
        if 1.81 <= z <= 2.99:
            return "Grey Zone"
        return "Distress Zone"

    df = df.copy()
    df["Z-Score"] = df["Ticker"].map(z_scores)
    df["Diagnostic"] = df["Z-Score"].apply(classify)
    return df


if __name__ == "__main__":
    # Sample Altman Z-scores for each ticker (placeholder values)
    sample_z_scores = {
        "MSFT": 3.5, "GOOGL": 3.2, "AMZN": 2.7, "META": 2.5, "IBM": 1.9,
        "ORCL": 3.1, "CRM": 2.3, "ADBE": 3.0, "SNOW": 1.6, "PLTR": 2.0,
        "AI": 1.4, "SOUN": 1.2, "UPST": 2.2, "TWLO": 2.0, "OTEX": 3.4,
        "SPLK": 2.6, "ESTC": 1.9, "AYX": 2.1, "DDOG": 2.8, "PATH": 1.7,
        "NOW": 3.3, "DOCU": 1.5, "INTU": 3.6, "SHOP": 2.9, "ZM": 1.8,
        "PINS": 2.1, "SNAP": 1.3, "LYFT": 1.0, "UBER": 2.4, "DASH": 2.2,
        "CRWD": 3.2, "FTNT": 3.5, "PANW": 3.4, "CHKP": 3.0, "INTC": 2.5,
        "NVDA": 4.0, "AMD": 3.1, "AVGO": 3.7, "MU": 2.2, "TSM": 3.8,
        "QCOM": 3.3, "MRVL": 2.6, "ANET": 3.2, "SMCI": 2.4, "NTES": 3.0,
        "BIDU": 2.2, "0700.HK": 3.1, "BABA": 2.7,
    }

    returns_df = calculate_ytd_returns()
    merged_df = merge_z_and_diagnostic(returns_df, sample_z_scores)

    pd.set_option("display.max_rows", None)
    print(merged_df.to_string(index=False))

    merged_df.to_csv("genai_health.csv", index=False)
    merged_df.to_excel("genai_health.xlsx", index=False)
