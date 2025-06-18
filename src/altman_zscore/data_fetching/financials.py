"""
Financials data fetching utilities for Altman Z-Score analysis.

Provides functions to fetch quarterly financials for a given ticker using SEC EDGAR (primary) and yfinance (fallback), with robust error handling, AI-powered field mapping, and data validation.
"""

# All imports should be at the top of the file, per Python best practices.
import decimal
from decimal import Decimal
import os
import logging
import json
from typing import Dict, Any, Optional

import pandas as pd
import requests

from altman_zscore.api.openai_client import AzureOpenAIClient
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.computation.constants import MODEL_FIELDS
from altman_zscore.data_fetching.financials_core import df_to_dict_str_keys
from altman_zscore.utils.retry import exponential_retry

# Network exceptions to retry on
NETWORK_EXCEPTIONS = (
    requests.exceptions.RequestException,  # All requests exceptions
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)
from altman_zscore.api.yahoo_helpers import fetch_yfinance_full
from altman_zscore.utils.error_helpers import DataFetchingError, raise_with_context

def merge_quarters_by_period(existing_quarters, new_quarters):
    """
    Merge quarterly financial data from different sources by period end date.

    For each period, updates existing data with any new non-None values from new_quarters.
    Field mappings are merged if present. Returns a sorted list of merged quarters.

    Args:
        existing_quarters (list[dict]): List of existing quarter dicts (must have 'period_end').
        new_quarters (list[dict]): List of new quarter dicts to merge in.

    Returns:
        list[dict]: Sorted list of merged quarter dicts by period_end.
    """
    period_map = {q["period_end"]: q for q in existing_quarters}
    
    for new_q in new_quarters:
        period = new_q["period_end"]
        if period in period_map:
            # Update existing quarter with any new non-None values
            for field, value in new_q.items():
                if field != "period_end" and value is not None:
                    if field == "field_mapping":
                        # Merge field mappings
                        existing_map = json.loads(period_map[period].get("field_mapping", "{}"))
                        new_map = json.loads(value)
                        existing_map.update(new_map)
                        period_map[period]["field_mapping"] = json.dumps(existing_map)
                    else:
                        period_map[period][field] = value
        else:
            period_map[period] = new_q
            
    # Convert back to list and sort by period
    merged = list(period_map.values())
    return sorted(merged, key=lambda x: x["period_end"])

@exponential_retry(
    max_retries=3,
    base_delay=1.0,
    backoff_factor=2.0,
    exceptions=NETWORK_EXCEPTIONS
)
def fetch_financials(ticker: str, end_date: str, zscore_model: str, start_date: str = None) -> Optional[Dict[str, Any]]:
    """
    Fetch up to 12 quarters of financials for the given ticker using SEC EDGAR (primary) and yfinance (fallback).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        end_date (str): End date for financials.
        zscore_model (str): Z-Score model name (determines required fields).
        start_date (str, optional): Start date for financials (if provided, filters quarters).

    Returns:
        dict or None: {"quarters": [dict, ...]} if data found, else None.

    Notes:
        - Tries SEC EDGAR first for financials. If unavailable or incomplete, falls back to yfinance.
        - Implements exponential backoff retry for network-related errors.
        - Retries up to 3 times with exponential delay between attempts.
        - Fetches company info and officers first.
        - Uses AI-powered field mapping if enabled and direct mapping fails.
        - Saves all raw and processed data to disk for reproducibility.
        - Logs all errors and warnings for traceability.
    """
    logger = logging.getLogger("altman_zscore.fetch_financials")

    if zscore_model not in MODEL_FIELDS:
        logger.error(f"Invalid Z-Score model {zscore_model}")
        return None

    output_dir = get_output_dir(ticker)
    fields_to_fetch = list(MODEL_FIELDS[zscore_model]) if zscore_model in MODEL_FIELDS else list(MODEL_FIELDS["original"])
    if "sales" not in fields_to_fetch:
        fields_to_fetch.append("sales")

    # --- SEC EDGAR primary ---
    try:
        from altman_zscore.api.sec_client import SECClient
        sec_client = SECClient()
        cik = sec_client.lookup_cik(ticker)
        sec_facts = sec_client.get_company_facts(cik) if cik else None
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        try:
            with open(os.path.join(output_dir, "sec_facts_raw.json"), "w", encoding="utf-8") as f:
                json.dump(sec_facts, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"[{ticker}] Could not save raw SEC facts: {e}")        # If no SEC facts, continue to yfinance fallback
        if not sec_facts or not sec_facts.get('facts'):
            logger.warning(f"[{ticker}] No SEC company facts; continuing to yfinance fallback.")
    except Exception as sec_e:
        logger.info(f"[{ticker}] SEC EDGAR failed: {sec_e}. Falling back to yfinance.")
        
    # --- yfinance fallback ---
    try:
        yf_data = fetch_yfinance_full(ticker)
        
        # Save additional data fetched from yfinance for LLM context injection
        if yf_data:
            # Save analyst recommendations
            recommendations = yf_data.get("recommendations")
            if recommendations is not None and not (isinstance(recommendations, pd.DataFrame) and recommendations.empty):
                try:
                    # Convert DataFrame to JSON-serializable format if needed
                    if isinstance(recommendations, pd.DataFrame):
                        rec_data = recommendations.to_dict('records')
                    else:
                        rec_data = recommendations
                    
                    rec_path = os.path.join(output_dir, "recommendations.json")
                    with open(rec_path, "w", encoding="utf-8") as f:
                        json.dump(rec_data, f, indent=2, ensure_ascii=False, default=str)
                    logger.debug(f"Saved analyst recommendations to {rec_path}")
                except Exception as e:
                    logger.warning(f"Failed to save recommendations for {ticker}: {e}")
            
            # Save major holders
            major_holders = yf_data.get("major_holders")
            if major_holders is not None and not (isinstance(major_holders, pd.DataFrame) and major_holders.empty):
                try:
                    if isinstance(major_holders, pd.DataFrame):
                        holders_data = major_holders.to_dict('records')
                    else:
                        holders_data = major_holders
                    
                    holders_path = os.path.join(output_dir, "major_holders.json")
                    with open(holders_path, "w", encoding="utf-8") as f:
                        json.dump(holders_data, f, indent=2, ensure_ascii=False, default=str)
                    logger.debug(f"Saved major holders to {holders_path}")
                except Exception as e:
                    logger.warning(f"Failed to save major holders for {ticker}: {e}")
            
            # Save institutional holders
            institutional_holders = yf_data.get("institutional_holders")
            if institutional_holders is not None and not (isinstance(institutional_holders, pd.DataFrame) and institutional_holders.empty):
                try:
                    if isinstance(institutional_holders, pd.DataFrame):
                        inst_data = institutional_holders.to_dict('records')
                    else:
                        inst_data = institutional_holders
                    
                    inst_path = os.path.join(output_dir, "institutional_holders.json")
                    with open(inst_path, "w", encoding="utf-8") as f:
                        json.dump(inst_data, f, indent=2, ensure_ascii=False, default=str)
                    logger.debug(f"Saved institutional holders to {inst_path}")
                except Exception as e:
                    logger.warning(f"Failed to save institutional holders for {ticker}: {e}")
                    
            # Save dividends and splits for completeness
            dividends = yf_data.get("dividends")
            if dividends is not None and not (isinstance(dividends, pd.Series) and dividends.empty):
                try:
                    div_path = os.path.join(output_dir, "dividends.csv")
                    if isinstance(dividends, pd.Series):
                        dividends.to_csv(div_path)
                    logger.debug(f"Saved dividends to {div_path}")
                except Exception as e:
                    logger.warning(f"Failed to save dividends for {ticker}: {e}")
            
            splits = yf_data.get("splits")
            if splits is not None and not (isinstance(splits, pd.Series) and splits.empty):
                try:
                    splits_path = os.path.join(output_dir, "splits.csv")
                    if isinstance(splits, pd.Series):
                        splits.to_csv(splits_path)
                    logger.debug(f"Saved splits to {splits_path}")
                except Exception as e:
                    logger.warning(f"Failed to save splits for {ticker}: {e}")
        
        # Get both quarterly and annual data for comprehensive coverage
        bs_quarterly = yf_data["balance_sheet"] if yf_data else None
        is_quarterly = yf_data["income_statement"] if yf_data else None
        bs_annual = yf_data.get("balance_sheet_annual") if yf_data else None
        is_annual = yf_data.get("income_statement_annual") if yf_data else None
        
        # Combine quarterly and annual data, prioritizing quarterly for recent periods
        bs_combined = None
        is_combined = None
        
        if isinstance(bs_quarterly, pd.DataFrame) and not bs_quarterly.empty:
            bs_combined = bs_quarterly.copy()
        if isinstance(is_quarterly, pd.DataFrame) and not is_quarterly.empty:
            is_combined = is_quarterly.copy()
            
        # Add annual data for historical periods not covered by quarterly data
        if isinstance(bs_annual, pd.DataFrame) and not bs_annual.empty:
            if bs_combined is None:
                bs_combined = bs_annual.copy()
            else:
                # Add annual periods that don't conflict with quarterly data
                for col in bs_annual.columns:
                    if col not in bs_combined.columns:
                        bs_combined[col] = bs_annual[col]
                        
        if isinstance(is_annual, pd.DataFrame) and not is_annual.empty:
            if is_combined is None:
                is_combined = is_annual.copy()
            else:
                # Add annual periods that don't conflict with quarterly data
                for col in is_annual.columns:
                    if col not in is_combined.columns:
                        is_combined[col] = is_annual[col]
        
        # Use combined data as primary datasets
        bs = bs_combined
        is_ = is_combined
        
        # Always save raw DataFrames for debugging, even if empty
        raw_data = {
            "balance_sheet": df_to_dict_str_keys(bs) if isinstance(bs, pd.DataFrame) else {},
            "income_statement": df_to_dict_str_keys(is_) if isinstance(is_, pd.DataFrame) else {},
        }
        with open(os.path.join(output_dir, "financials_raw.json"), "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)
        if not (isinstance(bs, pd.DataFrame) and not bs.empty and isinstance(is_, pd.DataFrame) and not is_.empty):
            logger.warning(f"[{ticker}] yfinance: One or both DataFrames are empty. balance_sheet empty: {bs is not None and bs.empty}, income_statement empty: {is_ is not None and is_.empty}")
        if isinstance(bs, pd.DataFrame) and not bs.empty and isinstance(is_, pd.DataFrame) and not is_.empty:
            raw_data = {
                "balance_sheet": df_to_dict_str_keys(bs),
                "income_statement": df_to_dict_str_keys(is_),
            }
            with open(os.path.join(output_dir, "financials_raw.json"), "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)
            quarters = []
            common_periods = [p for p in bs.columns if p in is_.columns]
            
            # Filter periods by date range if start_date/end_date provided
            if start_date or end_date:
                try:
                    if start_date:
                        start_dt = pd.to_datetime(start_date)
                    else:
                        start_dt = pd.Timestamp.min
                    if end_date:
                        end_dt = pd.to_datetime(end_date)
                    else:
                        end_dt = pd.Timestamp.now()
                        
                    common_periods = [p for p in common_periods if start_dt <= pd.to_datetime(p) <= end_dt]
                except Exception as e:
                    logger.warning(f"Failed to filter periods by date: {e}")
            
            missing_fields_by_quarter = []
            direct_mapping = {}
            available_bs_keys = set(str(idx) for idx in bs.index)
            available_is_keys = set(str(idx) for idx in is_.index)
            all_available_keys = available_bs_keys.union(available_is_keys)
            raw_fields = list(all_available_keys)
            sample_values = {}
            for f in raw_fields:
                v = None
                if f in bs.index and bs.shape[1] > 0:
                    v = bs.iloc[bs.index.get_loc(f), 0]
                elif f in is_.index and is_.shape[1] > 0:
                    v = is_.iloc[is_.index.get_loc(f), 0]
                if v is not None:
                    sample_values[f] = v            # Always use AI mapping for all fields
            missing_fields = [f for f in fields_to_fetch]
            try:
                client = AzureOpenAIClient()
                ai_mapping = client.suggest_field_mapping(raw_fields, missing_fields, sample_values, ticker=ticker)
                if ai_mapping:
                    for field, mapped in ai_mapping.items():
                        if field not in direct_mapping:
                            if isinstance(mapped, dict):
                                direct_mapping[field] = mapped.get("FoundField")
                            else:
                                direct_mapping[field] = mapped
            except Exception as e:
                logger.warning(f"AI field mapping failed: {e}. Will use only direct mapping.")
            for period in common_periods:
                try:
                    logger.debug(f"Processing period {period}")
                    q = {}
                    field_mapping = {}
                    missing = []
                    if isinstance(period, str):
                        q["period_end"] = period.split()[0]
                    else:
                        q["period_end"] = period.strftime("%Y-%m-%d")
                    for field in fields_to_fetch:
                        logger.debug(f"Processing field {field}")
                        val = None
                        mapped_field = None
                        raw_field = direct_mapping.get(field)
                        logger.debug(f"Direct mapping for {field}: {raw_field}")
                        if raw_field and isinstance(raw_field, str) and raw_field.startswith("INFERRED:"):
                            logger.debug(f"Processing inferred field {raw_field}")
                            _, equity_field, paid_in_field = raw_field.split(":")
                            try:
                                logger.debug(f"Checking BS index for fields - equity: {equity_field}, paid_in: {paid_in_field}")
                                logger.debug(f"Available BS fields: {list(bs.index)}")
                                equity_val = bs.loc[equity_field, period] if equity_field in bs.index else None
                                paid_in_val = bs.loc[paid_in_field, period] if paid_in_field in bs.index else None
                                logger.debug(f"Got raw values - Equity: {equity_val} ({type(equity_val)}), Paid in: {paid_in_val} ({type(paid_in_val)})")
                                if equity_val is not None and paid_in_val is not None:
                                    equity_dec = safe_to_decimal(str(equity_val))
                                    paid_in_dec = safe_to_decimal(str(paid_in_val))
                                    logger.debug(f"Converted to Decimal - Equity: {equity_dec}, Paid in: {paid_in_dec}")
                                    if equity_dec is not None and paid_in_dec is not None:
                                        val = equity_dec - paid_in_dec
                                        logger.debug(f"Calculated inferred value: {val}")
                                        mapped_field = f"Inferred from {equity_field} minus {paid_in_field}"
                                        logger.debug(f"Using inferred retained earnings value: {val}")
                                        q[field] = val
                                        field_mapping[field] = mapped_field
                                        continue
                                    else:
                                        logger.warning("Failed to convert equity or paid-in capital to Decimal")
                                        missing.append(field)
                                else:
                                    logger.debug("Missing required values for inference")
                                    logger.debug(f"Available fields in BS for period {period}: {list(bs.index)}")
                                    missing.append(field)
                            except Exception as e:
                                logger.warning(f"Failed to calculate inferred value for {field}: {e}")
                                missing.append(field)
                        else:
                            logger.debug(f"Normal field processing for {field}")
                            if raw_field:
                                mapped_field = raw_field
                                try:
                                    if raw_field in bs.index:
                                        val = safe_to_decimal(bs.loc[raw_field, period])
                                        logger.debug(f"Got value from balance sheet: {val}")
                                    elif raw_field in is_.index:
                                        val = safe_to_decimal(is_.loc[raw_field, period])
                                        logger.debug(f"Got value from income statement: {val}")
                                    else:
                                        val = None
                                except Exception as e:
                                    logger.warning(f"Failed to get value for {raw_field}: {e}")
                                    val = None
                                    missing.append(field)
                            else:
                                logger.debug(f"No mapping found for {field}")
                                missing.append(field)
                        if val in [None, 0, Decimal("0")]:
                            logger.debug(f"Skipping {field} because value is None or 0")
                            missing.append(field)
                        else:
                            logger.debug(f"Adding {field} with value {val}")
                            q[field] = val
                            field_mapping[field] = mapped_field
                    if q:
                        q["field_mapping"] = json.dumps(field_mapping, default=str)
                        # Filter by start_date after data is fetched
                        if start_date is None or q["period_end"] >= start_date:
                            quarters.append(q)
                            missing_fields_by_quarter.append(missing)
                except Exception as e:
                    logger.warning(f"Failed to process period {period}: {e}")
                    continue
            
            # Sort quarters by period end date and respect the date range
            quarters = sorted(quarters, key=lambda x: x["period_end"])
            
            if quarters:
                non_asset_fields = [f for f in fields_to_fetch if f not in ("total_assets", "current_assets", "current_liabilities", "total_liabilities")]
                all_zero = True
                for q in quarters:
                    if any(Decimal(str(q.get(f, 0))) != 0 for f in non_asset_fields):
                        all_zero = False
                        break
                if all_zero:
                    logger.error(f"[{ticker}] yfinance fallback: Only balance sheet data available; all income statement fields are zero. No Z-Score can be computed.")
                    return {
                        "error": "yfinance data for this ticker does not contain the required income statement fields (e.g., sales, EBIT, retained earnings). Only balance sheet data is available. No Z-Score can be computed.",
                        "quarters": quarters,
                        "missing_fields_by_quarter": missing_fields_by_quarter
                    }
                output_dir = get_output_dir(None, ticker=ticker)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                with open(os.path.join(output_dir, "financials_quarterly.json"), "w", encoding="utf-8") as f:
                    json.dump(quarters, f, indent=2, ensure_ascii=False, default=str)
                return {"quarters": quarters, "missing_fields_by_quarter": missing_fields_by_quarter}
            else:
                logger.error(f"[{ticker}] No usable financial data found after processing. Data may be present but missing required fields.")
                raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")
    except Exception as e:
        logger.error(f"[{ticker}] Could not fetch financials from SEC or Yahoo: {e}")
        raise_with_context(DataFetchingError, f"Could not fetch financials for {ticker}", str(e))
    # Always return a dict with 'quarters' and 'error' if no data found
    logger.error(f"[{ticker}] No usable financial data found from SEC or Yahoo. Returning empty result.")
    return {"quarters": [], "error": "No usable financial data found from SEC or Yahoo."}

def safe_to_decimal(value) -> Optional[Decimal]:
    """
    Safely convert a value to Decimal, handling various formats and missing values.

    Args:
        value: Value to convert (can be string, float, int, or Decimal).

    Returns:
        Decimal or None: Converted Decimal value, or None if conversion fails or value is missing/NaN.
    """
    if value is None:
        return None
        
    if isinstance(value, Decimal):
        return value
    
    # Return None for NaN values or empty strings to allow inference logic to work
    if pd.isna(value) or (isinstance(value, str) and not value.strip()):
        return None
        
    try:
        if isinstance(value, str):
            # Remove commas and handle scientific notation
            clean_val = value.replace(',', '')
            if 'e' in clean_val.lower():
                # Handle scientific notation by converting to float first
                return Decimal(str(float(clean_val)))
            return Decimal(clean_val)
        elif isinstance(value, (int, float)):
            # Convert through string to handle float precision issues
            return Decimal(str(value))
        else:
            # Try string conversion for other types
            return Decimal(str(value))
    except (decimal.InvalidOperation, ValueError, TypeError):
        return None

def fetch_and_reconcile_financials(ticker: str, end_date: str, zscore_model: str, start_date: str = None) -> Optional[Dict[str, Any]]:
    """
    Fetch and reconcile financials for a ticker using the primary fetch_financials logic.

    Args:
        ticker (str): Stock ticker symbol.
        end_date (str): End date for financials.
        zscore_model (str): Z-Score model name.
        start_date (str, optional): Start date for financials.

    Returns:
        dict or None: {"quarters": [dict, ...]} if data found, else None.
    """
    raw_results = fetch_financials(ticker, end_date, zscore_model, start_date)
    if raw_results and raw_results.get("quarters"):
        # Sort quarters by date and apply date filtering but do not limit to 12 quarters
        quarters = raw_results["quarters"]
        if start_date:
            quarters = [
                q for q in quarters
                if q.get("period_end") and q["period_end"] >= start_date
            ]
        if end_date:
            quarters = [
                q for q in quarters
                if q.get("period_end") and q["period_end"] <= end_date
            ]
        # Sort quarters in reverse chronological order
        quarters.sort(key=lambda x: x["period_end"], reverse=True)
        
        raw_results["quarters"] = quarters
        raw_results["missing_fields_by_quarter"] = raw_results.get("missing_fields_by_quarter", [[]])
        return raw_results
    return None
