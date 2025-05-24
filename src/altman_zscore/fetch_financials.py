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
        "total_assets": [
            "Total Assets",
            "Total Assets Net Minority Interest",
            "Total Assets Including Net Minority Interest"
        ],
        "current_assets": [
            "Current Assets",
            "Total Current Assets"
        ],
        "current_liabilities": [
            "Current Liabilities",
            "Total Current Liabilities"
        ],
        "retained_earnings": [
            "Retained Earnings",
            "Retained Earnings Total Equity"
        ],
        "total_liabilities": [
            "Total Liab",
            "Total Liabilities",
            "Total Liabilities Net Minority Interest",
            "Total Liabilities Including Net Minority Interest"
        ],
        "book_value_equity": [
            "Total Stockholder Equity",
            "Total Equity Gross Minority Interest",
            "Total Equity",
            "Total Shareholder Equity"
        ],
        "ebit": [
            "Ebit",
            "EBIT",
            "Earnings Before Interest and Taxes"
        ],
        "sales": [
            "Total Revenue",
            "Revenue",
            "Sales Revenue Net"
        ],
    }
    fields_to_fetch = model_fields.get(zscore_model, model_fields["original"])
    try:
        yf_ticker = yf.Ticker(ticker)
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        # Save the balance sheet index for troubleshooting
        with open("output/bs_index_{}_{}.txt".format(ticker.upper(), end_date), "w") as f:
            f.write("\n".join(str(idx) for idx in bs.index))
        # Save the balance sheet and income statement columns for troubleshooting
        with open(f"output/bs_columns_{ticker.upper()}_{end_date}.txt", "w") as f:
            f.write("\n".join(str(col) for col in bs.columns))
        with open(f"output/is_columns_{ticker.upper()}_{end_date}.txt", "w") as f:
            f.write("\n".join(str(col) for col in is_.columns))
        quarters = []
        # Only process periods present in both balance sheet and income statement
        common_periods = [p for p in bs.columns if p in is_.columns]
        for period in common_periods:
            period_str = str(period)
            q = {"period_end": period_str}
            missing = []
            available_bs_keys = set(str(idx) for idx in bs.index)
            available_is_keys = set(str(idx) for idx in is_.index)
            # Extract only fields required for the selected model
            for key in fields_to_fetch:
                names = required_fields[key]
                val = None
                found_name = None
                for name in names:
                    if name in bs.index and key not in ["ebit", "sales"]:
                        v = bs.at[name, period]
                        if v is not None and v == v:  # not NaN
                            val = float(v)
                            found_name = name
                            break
                    if name in is_.index and key in ["ebit", "sales"]:
                        v = is_.at[name, period]
                        if v is not None and v == v:
                            val = float(v)
                            found_name = name
                            break
                # Fallback: try partial match if not found
                if val is None:
                    search_space = available_bs_keys if key not in ["ebit", "sales"] else available_is_keys
                    for candidate in search_space:
                        for name in names:
                            if name.lower() in candidate.lower():
                                if key not in ["ebit", "sales"]:
                                    v = bs.at[candidate, period]
                                else:
                                    v = is_.at[candidate, period]
                                if v is not None and v == v:
                                    val = float(v)
                                    found_name = candidate
                                    logger.warning(f"[{ticker}] {period_str}: Used fallback field '{candidate}' for '{key}' (expected one of {names})")
                                    break
                        if val is not None:
                            break
                if val is None:
                    missing.append(key)
                    val = 0.0
                q[key] = val  # type: ignore
            # Add raw payload for diagnostics
            try:
                q["raw_payload"] = json.dumps({
                    "balance_sheet": bs[period].dropna().to_dict() if period in bs.columns else {},
                    "income_statement": is_[period].dropna().to_dict() if period in is_.columns else {},
                    "available_bs_keys": list(available_bs_keys),
                    "available_is_keys": list(available_is_keys)
                })
            except Exception as e:
                q["raw_payload"] = json.dumps({"error": f"Failed to extract raw payload: {e}"})
            if missing:
                logger.warning(f"[{ticker}] {period_str}: Missing fields: {', '.join(missing)}. Available BS keys: {sorted(available_bs_keys)}. Available IS keys: {sorted(available_is_keys)}")
            quarters.append(q)
        quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
        if quarters:
            return {"quarters": quarters}
        else:
            raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")
    except Exception as e:
        raise RuntimeError(f"Error fetching financials for {ticker}: {e}")
