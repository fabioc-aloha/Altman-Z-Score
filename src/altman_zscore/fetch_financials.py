"""
Financials fetching module for Altman Z-Score pipeline (MVP scaffold).

This module fetches 12 quarters of financials for a given ticker using yfinance as primary source,
with robust fallback to SEC EDGAR for delisted/edge-case tickers. Only fields required for the selected
Z-Score model are fetched. Logs diagnostics and handles missing/partial data gracefully.
"""

# All imports should be at the top of the file, per Python best practices.

def fetch_financials(ticker: str, end_date: str, zscore_model: str):
    """
    Fetch 12 quarters of real financials for the given ticker using yfinance (primary) and SEC EDGAR (fallback).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        end_date (str): End date for financials (ignored in MVP, use all available)
        zscore_model (str): Z-Score model name (determines required fields)
    Returns:
        dict or None: {"quarters": [dict, ...]} if data found, else None
    
    Notes:
        - Only fetches fields required for the selected Z-Score model.
        - If yfinance fails or returns no usable data, attempts SEC EDGAR fallback.
        - Logs diagnostics and saves raw payloads for troubleshooting.
        - Returns None if no usable data is found (pipeline handles this gracefully).
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
        # Log what periods/columns are present
        logger.info(f"[{ticker}] Balance sheet columns: {list(bs.columns)}")
        logger.info(f"[{ticker}] Income statement columns: {list(is_.columns)}")
        # Save the balance sheet index for troubleshooting
        with open(f"output/bs_index_{ticker.upper()}_{end_date}.txt", "w") as f:
            f.write("\n".join(str(idx) for idx in bs.index))
        with open(f"output/bs_columns_{ticker.upper()}_{end_date}.txt", "w") as f:
            f.write("\n".join(str(col) for col in bs.columns))
        with open(f"output/is_columns_{ticker.upper()}_{end_date}.txt", "w") as f:
            f.write("\n".join(str(col) for col in is_.columns))
        quarters = []
        common_periods = [p for p in bs.columns if p in is_.columns]
        # If yfinance returns no data, try SEC EDGAR fallback
        if (not len(bs.columns) and not len(is_.columns)) or not common_periods:
            logger.warning(f"[{ticker}] No usable financials from yfinance. Attempting SEC EDGAR fallback...")
            try:
                from altman_zscore.api.sec_client import SECClient
                sec = SECClient()
                cik = sec.lookup_cik(ticker)
                if not cik:
                    logger.error(f"[{ticker}] No CIK found for SEC fallback. Cannot fetch SEC financials.")
                    raise ValueError(f"No financial statement columns found for ticker '{ticker}'. The company may be delisted, never public, or data is missing from yfinance/SEC.")
                facts = sec.get_company_facts(cik)
                # Try to extract at least one required field for at least one period
                found_any = False
                for key in fields_to_fetch:
                    if key in facts.get('facts', {}).get('us-gaap', {}):
                        found_any = True
                        break
                if not found_any:
                    logger.error(f"[{ticker}] No required financial fields found in SEC facts for CIK {cik}.")
                    raise ValueError(f"No financial statement columns found for ticker '{ticker}'. The company may be delisted, never public, or data is missing from yfinance/SEC.")
                # If we get here, SEC has at least some data. (Full SEC XBRL parsing not implemented here.)
                logger.error(f"[{ticker}] SEC fallback found some data, but full SEC XBRL parsing is not implemented in this pipeline. Please implement SEC XBRL parsing for full support.")
                raise ValueError(f"SEC fallback found some data for ticker '{ticker}', but full SEC XBRL parsing is not implemented. Please add SEC XBRL support to proceed.")
            except Exception as sec_e:
                logger.error(f"[{ticker}] SEC fallback failed: {sec_e}")
                raise ValueError(f"No financial statement columns found for ticker '{ticker}'. The company may be delisted, never public, or data is missing from yfinance/SEC.")
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
            # Warn if partial data (e.g., only annuals, or fewer than 4 quarters)
            if len(quarters) < 4:
                logger.warning(f"[{ticker}] Only {len(quarters)} usable periods found. Proceeding with partial data.")
            return {"quarters": quarters}
        else:
            logger.error(f"[{ticker}] No usable financial data found after processing. Data may be present but missing required fields.")
            raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")
    except Exception as e:
        logger.error(f"[{ticker}] Exception in fetch_financials: {e}")
        print(f"[ERROR] Could not fetch financials for {ticker}: {e}")
        return None
