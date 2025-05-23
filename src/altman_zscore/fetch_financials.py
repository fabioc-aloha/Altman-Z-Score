"""
Financials fetching module for Altman Z-Score pipeline (MVP scaffold).
"""
def fetch_financials(ticker: str, end_date: str, zscore_model: str):
    """
    Fetch 12 quarters of real financials for the given ticker using yfinance.
    Only fetch fields required for the selected Z-Score model.
    If yfinance fails or returns no usable data, log a warning and return an error DataFrame.
    """
    import yfinance as yf
    from datetime import datetime, timedelta
    import logging
    import json
    logger = logging.getLogger("altman_zscore.fetch_financials")
    # Define required fields for each Z-Score model
    model_fields = {
        "original": [
            "total_assets", "current_assets", "current_liabilities", "retained_earnings",
            "total_liabilities", "book_value_equity", "ebit", "sales"
        ],
        "private": [
            "total_assets", "current_assets", "current_liabilities", "retained_earnings",
            "total_liabilities", "book_value_equity", "ebit", "sales"
        ],
        "public": [
            "total_assets", "current_assets", "current_liabilities", "retained_earnings",
            "total_liabilities", "book_value_equity", "ebit", "sales"
        ],
        "service": [
            "total_assets", "current_assets", "current_liabilities", "retained_earnings",
            "total_liabilities", "book_value_equity", "ebit"
        ],
        "emerging": [
            "total_assets", "current_assets", "current_liabilities", "retained_earnings",
            "total_liabilities", "book_value_equity", "ebit", "sales"
        ],
    }
    required_fields = {
        "total_assets": ["Total Assets"],
        "current_assets": ["Current Assets"],
        "current_liabilities": ["Current Liabilities"],
        "retained_earnings": ["Retained Earnings"],
        "total_liabilities": ["Total Liab", "Total Liabilities"],
        "book_value_equity": ["Total Stockholder Equity", "Total Equity Gross Minority Interest", "Total Equity"],
        "ebit": ["Ebit", "EBIT"],
        "sales": ["Total Revenue", "Revenue"],
    }
    fields_to_fetch = model_fields.get(zscore_model, model_fields["original"])
    try:
        yf_ticker = yf.Ticker(ticker)
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        quarters = []
        for period in bs.columns:
            period_str = str(period)
            q = {"period_end": period_str}
            missing = []
            # Extract only fields required for the selected model
            for key in fields_to_fetch:
                names = required_fields[key]
                val = None
                for name in names:
                    if name in bs.index and key not in ["ebit", "sales"]:
                        v = bs.at[name, period]
                        if v is not None and v == v:  # not NaN
                            val = float(v)
                            break
                    if name in is_.index and key in ["ebit", "sales"]:
                        v = is_.at[name, period]
                        if v is not None and v == v:
                            val = float(v)
                            break
                if val is None:
                    missing.append(key)
                    val = 0.0
                q[key] = val  # type: ignore
            # Add raw payload for diagnostics
            try:
                q["raw_payload"] = json.dumps({
                    "balance_sheet": bs[period].dropna().to_dict() if period in bs.columns else {},
                    "income_statement": is_[period].dropna().to_dict() if period in is_.columns else {}
                })
            except Exception as e:
                q["raw_payload"] = json.dumps({"error": f"Failed to extract raw payload: {e}"})
            if missing:
                logger.warning(f"[{ticker}] {period_str}: Missing fields: {', '.join(missing)}")
            quarters.append(q)
        quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
        if quarters:
            return {"quarters": quarters}
        else:
            logger.warning(f"No usable financial data found for {ticker}. The company may not exist or was not listed in the requested period.")
            return {"quarters": []}
    except Exception as e:
        logger.error(f"Error fetching financials for {ticker}: {e}")
        return {"quarters": []}
