"""
Financials data fetching utilities for Altman Z-Score analysis.
"""

# All imports should be at the top of the file, per Python best practices.
import os
from altman_zscore.api.openai_client import AzureOpenAIClient
from altman_zscore.utils.paths import get_output_dir

def fetch_financials(ticker: str, end_date: str, zscore_model: str):
    """
    Fetch 12 quarters of real financials for the given ticker using yfinance (primary) and SEC EDGAR (fallback).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        end_date (str): End date for financials (ignored in MVP, use all available)
        zscore_model (str): Z-Score model name (determines required fields)
        output_dir (str, optional): Directory to save output files. Defaults to './output'.
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
            "Total Assets Including Net Minority Interest",
            "Assets",  # AAPL fallback
            "Assets Total"  # AAPL fallback
        ],
        "current_assets": [
            "Current Assets",
            "Total Current Assets",
            "Assets Current"  # AAPL fallback
        ],
        "current_liabilities": [
            "Current Liabilities",
            "Total Current Liabilities",
            "Liabilities Current"  # AAPL fallback
        ],
        "retained_earnings": [
            "Retained Earnings",
            "Retained Earnings Total Equity",
            "Gains Losses Not Affecting Retained Earnings",  # TSLA-specific
            "Other Equity Adjustments",  # TSLA sometimes uses this
            "Retained Earnings Accumulated Deficit"  # AAPL fallback
        ],
        "total_liabilities": [
            "Total Liab",
            "Total Liabilities",
            "Total Liabilities Net Minority Interest",
            "Total Liabilities Including Net Minority Interest",
            "Total Non Current Liabilities Net Minority Interest"
        ],
        "book_value_equity": [
            "Total Stockholder Equity",
            "Total Equity Gross Minority Interest",
            "Total Equity",
            "Total Shareholder Equity",
            "Stockholders Equity",  # TSLA
            "Common Stock Equity",   # TSLA
            "Tangible Book Value",   # TSLA (sometimes used)
            "Net Tangible Assets"    # TSLA (sometimes used)
        ],
        "ebit": [
            "Ebit",
            "EBIT",
            "Earnings Before Interest and Taxes",
            "Operating Income",
            "Operating Revenue",  # TSLA
            "Total Operating Income As Reported",  # TSLA
            "Gross Profit"  # fallback for TSLA if no EBIT/Operating Income
        ],
        "sales": [
            "Total Revenue",
            "Revenue",
            "Sales Revenue Net",
            "Operating Revenue"
        ],
    }
    fields_to_fetch = model_fields.get(zscore_model, model_fields["original"])

    # AI-powered field mapping integration (AI-only, no static fallback)
    ai_field_mapping = os.getenv("AI_FIELD_MAPPING", "false").lower() == "true"
    ai_mapping = None
    if ai_field_mapping:
        try:
            import yfinance as yf
            yf_ticker = yf.Ticker(ticker)
            bs = yf_ticker.quarterly_balance_sheet
            is_ = yf_ticker.quarterly_financials
            raw_fields = list(set([str(idx) for idx in bs.index] + [str(idx) for idx in is_.index]))
            canonical_fields = fields_to_fetch
            sample_values = {}
            for f in raw_fields:
                v = None
                if f in bs.index and bs.shape[1] > 0:
                    v = bs.iloc[bs.index.get_loc(f), 0]
                elif f in is_.index and is_.shape[1] > 0:
                    v = is_.iloc[is_.index.get_loc(f), 0]
                if v is not None:
                    sample_values[f] = v
            client = AzureOpenAIClient()
            ai_mapping = client.suggest_field_mapping(raw_fields, canonical_fields, sample_values)
            # Log and print the AI mapping for diagnostics
            print(f"[AI Mapping] Canonical to raw field mapping for {ticker}: {ai_mapping}")
            print(f"[AI Mapping] Available raw fields: {raw_fields}")
            for canon, raw in (ai_mapping or {}).items():
                print(f"[AI Mapping] {canon} -> {raw}")
            # Log the AI mapping for diagnostics
            import logging
            logger = logging.getLogger("altman_zscore.fetch_financials")
            logger.info(f"[AI Mapping] Canonical to raw field mapping for {ticker}: {ai_mapping}")
            for canon, raw in (ai_mapping or {}).items():
                logger.info(f"[AI Mapping] {canon} -> {raw}")
        except Exception as e:
            import logging
            logging.getLogger("altman_zscore.fetch_financials").warning(f"AI field mapping failed: {e}. All fields will be treated as missing.")
            ai_mapping = None

    try:
        yf_ticker = yf.Ticker(ticker)
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        # Log what periods/columns are present
        logger.info(f"[{ticker}] Balance sheet columns: {list(bs.columns)}")
        logger.info(f"[{ticker}] Income statement columns: {list(is_.columns)}")
        quarters = []
        common_periods = [p for p in bs.columns if p in is_.columns]
        # Track missing fields for each quarter for partial analysis and reporting
        missing_fields_by_quarter = []
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
            
            # Check for minimum required data for this quarter
            # Define critical fields without which we should skip the quarter
            critical_fields = ["total_assets", "current_assets", "current_liabilities", "retained_earnings"]
            critical_missing = []
            
            # Early check for critical fields
            for key in critical_fields:
                if key not in fields_to_fetch:
                    continue
                ai_raw_field = None
                if ai_mapping and key in ai_mapping and ai_mapping[key]:
                    ai_raw_field = ai_mapping[key]["FoundField"] if isinstance(ai_mapping[key], dict) else ai_mapping[key]
                found = False
                # Only use AI-mapped field
                if ai_raw_field:
                    if ai_raw_field in bs.index and key not in ["ebit", "sales"]:
                        v = bs.at[ai_raw_field, period]
                        if v is not None and v == v and float(v) != 0:  # not NaN and not zero
                            found = True
                    elif ai_raw_field in is_.index and key in ["ebit", "sales"]:
                        v = is_.at[ai_raw_field, period]
                        if v is not None and v == v and float(v) != 0:  # not NaN and not zero
                            found = True
                if not found:
                    critical_missing.append(key)

            # Skip this quarter if critical fields are missing
            if critical_missing:
                logger.warning(f"[{ticker}] {period_str}: Skipping quarter due to critical missing fields: {', '.join(critical_missing)}")
                continue

            # Extract only fields required for the selected model (AI-only)
            field_mapping = {}
            for key in fields_to_fetch:
                ai_raw_field = None
                if ai_mapping and key in ai_mapping and ai_mapping[key]:
                    ai_raw_field = ai_mapping[key]["FoundField"] if isinstance(ai_mapping[key], dict) else ai_mapping[key]
                val = None
                found_name = None
                # Only use AI-mapped field
                if ai_raw_field:
                    if ai_raw_field in bs.index and key not in ["ebit", "sales"]:
                        v = bs.at[ai_raw_field, period]
                        if v is not None and v == v:
                            val = float(v)
                            found_name = ai_raw_field
                    elif ai_raw_field in is_.index and key in ["ebit", "sales"]:
                        v = is_.at[ai_raw_field, period]
                        if v is not None and v == v:
                            val = float(v)
                            found_name = ai_raw_field
                # If not found by AI, treat as missing
                if val is None:
                    missing.append(key)
                    val = 0.0
                q[key] = val  # type: ignore
                # Add to field_mapping for reporting
                field_mapping[key] = {
                    "canonical_field": key,
                    "mapped_raw_field": found_name,
                    "value": val,
                    "missing": val == 0.0 or found_name is None
                }
            import json
            q["field_mapping"] = json.dumps(field_mapping)
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
            # Track missing fields for each quarter for partial analysis and reporting
            missing_fields_by_quarter.append(missing)
        quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
        if quarters:
            # Only now, after confirming valid data, write diagnostics/output files
            with open(get_output_dir(f"bs_index.txt", ticker=ticker), "w") as f:
                f.write("\n".join(str(idx) for idx in bs.index))
            with open(get_output_dir(f"is_index.txt", ticker=ticker), "w") as f:
                f.write("\n".join(str(idx) for idx in is_.index))
            return {"quarters": quarters, "missing_fields_by_quarter": missing_fields_by_quarter}
        else:
            logger.error(f"[{ticker}] No usable financial data found after processing. Data may be present but missing required fields.")
            raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")
    except Exception as e:
        logger.error(f"[{ticker}] Exception in fetch_financials: {e}")
        print(f"[ERROR] Could not fetch financials for {ticker}: {e}")
        return None
