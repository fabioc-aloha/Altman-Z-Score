"""
Financials data fetching utilities for Altman Z-Score analysis.

Provides functions to fetch quarterly financials for a given ticker using SEC EDGAR (primary) and yfinance (fallback), with robust error handling, field mapping, and data validation.
"""

# All imports should be at the top of the file, per Python best practices.
import decimal
from decimal import Decimal
import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional, Union, TypedDict

import pandas as pd
import yfinance as yf
import requests

from altman_zscore.api.openai_client import AzureOpenAIClient
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.computation.constants import FIELD_MAPPING, MODEL_FIELDS
from altman_zscore.data_fetching.sec_edgar import fetch_sec_edgar_data, find_xbrl_tag
from altman_zscore.data_fetching.executives import fetch_company_officers, fetch_executive_data
from altman_zscore.data_fetching.financials_core import df_to_dict_str_keys, find_matching_field
from altman_zscore.utils.retry import exponential_retry

# Network exceptions to retry on
NETWORK_EXCEPTIONS = (
    requests.exceptions.RequestException,  # All requests exceptions
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)
from altman_zscore.api.yahoo_helpers import fetch_yfinance_data, fetch_yfinance_full
from altman_zscore.utils.error_helpers import DataFetchingError, raise_with_context

def merge_quarters_by_period(existing_quarters, new_quarters):
    """Merge quarterly data from different sources by period end date."""
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
def fetch_financials(ticker: str, end_date: str, zscore_model: str) -> Optional[Dict[str, Any]]:
    """Fetch 12 quarters of real financials for the given ticker using SEC EDGAR (primary) and yfinance (fallback).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        end_date (str): End date for financials (ignored in MVP, uses all available).
        zscore_model (str): Z-Score model name (determines required fields).

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
        if not cik:
            logger.error(f"[{ticker}] SEC EDGAR: No CIK found for ticker.")
            raise ValueError(f"No CIK found for ticker {ticker}")
        facts = sec_client.get_company_facts(cik)
        quarters = []
        missing_fields_by_quarter = []
        periods = {}
        for field in fields_to_fetch:
            xbrl_names = FIELD_MAPPING.get(field, [])
            for xbrl_name in xbrl_names:
                fact = facts.get("facts", {}).get("us-gaap", {}).get(xbrl_name)
                if not fact:
                    continue
                for item in fact.get("units", {}).values():
                    for entry in item:
                        end = entry.get("end")
                        val = entry.get("val")
                        if not end or val is None:
                            continue
                        if end not in periods:
                            periods[end] = {}
                        periods[end][field] = Decimal(str(val))
        critical_fields = ["total_assets", "current_assets", "current_liabilities", "retained_earnings"]
        for period_end, data in periods.items():
            missing = [f for f in critical_fields if f not in data or data[f] is None]
            # Allow up to 2 missing critical fields for partial analysis
            if len(missing) > 2:
                logger.warning(f"[{ticker}] {period_end}: Skipping SEC quarter due to missing: {', '.join(missing)}")
                continue
            # Fill missing fields with 0 and mark as missing
            for f in fields_to_fetch:
                if f not in data or data[f] is None:
                    data[f] = Decimal("0")
            data["period_end"] = period_end
            quarters.append(data)
            missing_fields_by_quarter.append(missing)
        quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
        if quarters:
            # After collecting quarters, check if all non-asset/liability fields are zero for every quarter (SEC fallback)
            non_asset_fields = [f for f in fields_to_fetch if f not in ("total_assets", "current_assets", "current_liabilities", "total_liabilities")]
            all_zero = True
            for q in quarters:
                if any(Decimal(str(q.get(f, 0))) != 0 for f in non_asset_fields):
                    all_zero = False
                    break
            if all_zero:
                logger.error(f"[{ticker}] SEC EDGAR: Only balance sheet data available; all income statement fields are zero. No Z-Score can be computed.")
                return {
                    "error": "SEC EDGAR filings for this ticker do not contain the required income statement fields (e.g., sales, EBIT, retained earnings). Only balance sheet data is available. No Z-Score can be computed.",
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
            logger.error(f"[{ticker}] SEC EDGAR: No usable financial data found.")
            # If SEC fails, fall through to yfinance fallback
    except Exception as sec_e:
        logger.warning(f"[{ticker}] SEC EDGAR failed: {sec_e}. Falling back to yfinance.")

    # --- yfinance fallback ---
    try:
        yf_data = fetch_yfinance_full(ticker)
        if yf_data is not None:
            bs = yf_data["balance_sheet"]
            is_ = yf_data["income_statement"]
            info = yf_data["info"]
            if isinstance(bs, pd.DataFrame) and not bs.empty and isinstance(is_, pd.DataFrame) and not is_.empty:
                raw_data = {
                    "balance_sheet": df_to_dict_str_keys(bs),
                    "income_statement": df_to_dict_str_keys(is_),
                }
                with open(os.path.join(output_dir, "financials_raw.json"), "w", encoding="utf-8") as f:
                    json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)
                quarters = []
                common_periods = [p for p in bs.columns if p in is_.columns]
                missing_fields_by_quarter = []
                direct_mapping = {}
                available_bs_keys = set(str(idx) for idx in bs.index)
                available_is_keys = set(str(idx) for idx in is_.index)
                all_available_keys = available_bs_keys.union(available_is_keys)
                for field in fields_to_fetch:
                    matched_field = find_matching_field(field, list(all_available_keys))
                    if matched_field:
                        direct_mapping[field] = matched_field
                ai_field_mapping = os.getenv("AI_FIELD_MAPPING", "false").lower() == "true"
                ai_mapping = None
                if ai_field_mapping:
                    missing_fields = [f for f in fields_to_fetch if f not in direct_mapping]
                    if missing_fields:
                        try:
                            raw_fields = list(all_available_keys)
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
                            ai_mapping = client.suggest_field_mapping(raw_fields, missing_fields, sample_values)
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
                            if raw_field and raw_field.startswith("INFERRED:"):
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
                            quarters.append(q)
                            missing_fields_by_quarter.append(missing)
                    except Exception as e:
                        logger.warning(f"Failed to process period {period}: {e}")
                        continue
                quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
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
        logger.error(f"[{ticker}] Exception in yfinance fallback: {e}")
        print(f"[ERROR] Could not fetch financials for {ticker}: {e}")
        raise_with_context(DataFetchingError, f"Could not fetch financials for {ticker}", str(e))
    return None

def safe_to_decimal(value) -> Optional[Decimal]:
    """Safely convert a value to Decimal, handling various formats.
    
    Args:
        value: Value to convert (can be string, float, int, or Decimal)
        
    Returns:
        Decimal value or None if conversion fails
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
    except (decimal.InvalidOperation, ValueError, TypeError) as e:
        return None
