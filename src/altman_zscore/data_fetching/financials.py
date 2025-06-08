"""
Financials data fetching utilities for Altman Z-Score analysis.

Provides functions to fetch quarterly financials for a given ticker using SEC EDGAR (primary) and yfinance (fallback), with robust error handling, AI-powered field mapping, and data validation.
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
import numpy as np

from altman_zscore.api.openai_client import AzureOpenAIClient
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.computation.constants import MODEL_FIELDS
from altman_zscore.data_fetching.executives import fetch_company_officers, fetch_executive_data
from altman_zscore.data_fetching.financials_core import df_to_dict_str_keys
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

        # Get all available US-GAAP fields
        us_gaap_facts = facts.get("facts", {}).get("us-gaap", {})
        raw_fields = list(us_gaap_facts.keys())
        ai_mapping = {}
        
        try:
            # Get sample values for context
            sample_values = {}
            for field in raw_fields:
                fact = us_gaap_facts[field]
                if not fact or "units" not in fact:
                    continue
                for values in fact["units"].values():
                    if values:
                        sample_values[field] = values[0].get("val")
                        break
            
            # Use AI to map fields
            client = AzureOpenAIClient()
            ai_mapping = client.suggest_field_mapping(raw_fields, fields_to_fetch, sample_values)
            if not ai_mapping:
                logger.warning(f"[{ticker}] AI field mapping returned no results.")
        except Exception as e:
            logger.warning(f"AI field mapping failed: {e}. Will use only available fields.")

        direct_mapping = {}
        if ai_mapping:
            for canonical, mapped in ai_mapping.items():
                if isinstance(mapped, dict):
                    direct_mapping[canonical] = mapped.get("FoundField")
                else:
                    direct_mapping[canonical] = mapped        # Process each mapped field
        for field in fields_to_fetch:
            raw_field = direct_mapping.get(field)
            if not raw_field:
                continue
            fact = us_gaap_facts.get(raw_field)
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
                    periods[end]["field_mapping"] = raw_field
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
        # Always save raw DataFrames for debugging, even if empty
        bs = yf_data["balance_sheet"] if yf_data else None
        is_ = yf_data["income_statement"] if yf_data else None
        info = yf_data["info"] if yf_data else None
        raw_data = {
            "balance_sheet": df_to_dict_str_keys(bs) if isinstance(bs, pd.DataFrame) else {},
            "income_statement": df_to_dict_str_keys(is_) if isinstance(is_, pd.DataFrame) else {},
        }
        with open(os.path.join(output_dir, "financials_raw.json"), "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)
        if not (isinstance(bs, pd.DataFrame) and not bs.empty and isinstance(is_, pd.DataFrame) and not is_.empty):
            logger.warning(f"[{{ticker}}] yfinance: One or both DataFrames are empty. balance_sheet empty: {{bs is not None and bs.empty}}, income_statement empty: {{is_ is not None and is_.empty}}")
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
            # Always use AI mapping for all fields
            missing_fields = [f for f in fields_to_fetch]
            try:
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
    # Always return a dict with 'quarters' and 'error' if no data found
    logger.error(f"[{ticker}] No usable financial data found from SEC or Yahoo. Returning empty result.")
    return {"quarters": [], "error": "No usable financial data found from SEC or Yahoo."}

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

def fetch_and_reconcile_financials(ticker: str, end_date: str, zscore_model: str) -> Optional[Dict[str, Any]]:
    """
    Fetch raw financials from both SEC EDGAR and Yahoo Finance, reconcile using LLM, and return a canonical dataset.
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        end_date (str): End date for financials (ignored in MVP, uses all available).
        zscore_model (str): Z-Score model name (determines required fields).
    Returns:
        dict or None: Canonical dataset as returned by LLM, or None on error.
    """
    import pprint
    import time
    logger = logging.getLogger("altman_zscore.fetch_and_reconcile_financials")
    output_dir = get_output_dir(ticker)
    # Fetch SEC EDGAR data (raw)
    try:
        from altman_zscore.api.sec_client import SECClient
        sec_client = SECClient()
        cik = sec_client.lookup_cik(ticker)
        sec_facts = sec_client.get_company_facts(cik) if cik else None        # Save raw SEC facts before any filtering/processing
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        try:
            with open(os.path.join(output_dir, "sec_facts_raw.json"), "w", encoding="utf-8") as f:
                json.dump(sec_facts, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"[{ticker}] Could not save raw SEC facts: {e}")
    except Exception as e:
        logger.warning(f"[{ticker}] SEC EDGAR fetch failed: {e}")
        sec_facts = None
    
    # Fetch Yahoo Finance data (raw)
    try:
        yf_data = fetch_yfinance_full(ticker)
        # Save raw Yahoo data before any filtering/processing
        def serialize_yf_data(yf_data):
            if not yf_data:
                return None
            result = {}
            for k, v in yf_data.items():
                if isinstance(v, pd.DataFrame):
                    # Use the same serialization method as financials_raw.json for consistency
                    result[k] = df_to_dict_str_keys(v)
                elif hasattr(v, 'to_dict'):
                    try:
                        result[k] = v.to_dict()
                    except Exception:
                        result[k] = str(v)
                else:
                    try:
                        json.dumps(v)  # test if serializable
                        result[k] = v
                    except Exception:
                        result[k] = str(v)
            return result
        try:
            with open(os.path.join(output_dir, "yahoo_raw.json"), "w", encoding="utf-8") as f:
                json.dump(serialize_yf_data(yf_data), f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"[{ticker}] Could not save raw Yahoo data: {e}")
    except Exception as e:
        logger.warning(f"[{ticker}] Yahoo Finance fetch failed: {e}")
        yf_data = None
    # Prepare prompt for LLM reconciliation
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "prompt_reconcile_financials.md")
    if not os.path.exists(prompt_path):
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "prompt_reconcile_financials.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    # Only include the last 8 periods and required fields for each source
    required_fields = [
        "total_assets", "current_assets", "current_liabilities", "total_liabilities",
        "retained_earnings", "ebit", "sales"
    ]
    def filter_sec_facts(sec_facts):
        if not sec_facts:
            return None
        us_gaap = sec_facts.get("facts", {}).get("us-gaap", {})
        field_data = {}
        for field in required_fields:
            fact = us_gaap.get(field)
            if not fact or "units" not in fact:
                continue
            for unit, values in fact["units"].items():
                for entry in values:
                    end = entry.get("end")
                    val = entry.get("val")
                    if end and val is not None:
                        field_data.setdefault(field, {})[str(end)] = val
        all_periods = set()
        for d in field_data.values():
            all_periods.update(d.keys())
        last_periods = sorted(all_periods)[-8:]
        compact = {}
        for period in last_periods:        compact[str(period)] = {field: field_data.get(field, {}).get(period) for field in required_fields}
        return compact
    
    def filter_yf_data(yf_data):
        if not yf_data:
            return None
        bs = yf_data.get("balance_sheet")
        is_ = yf_data.get("income_statement")
        # Only keep periods present in both
        if not (isinstance(bs, pd.DataFrame) and not bs.empty and isinstance(is_, pd.DataFrame) and not is_.empty):
            return None
        periods = [p for p in bs.columns if p in is_.columns]
        last_periods = periods[-8:]
        
        # Field mapping from required fields to actual DataFrame field names
        field_mapping = {
            "total_assets": "Total Assets",
            "current_assets": "Current Assets", 
            "current_liabilities": "Current Liabilities",
            "total_liabilities": "Total Liabilities Net Minority Interest",
            "retained_earnings": "Retained Earnings",
            "ebit": "EBIT",
            "sales": "Total Revenue"
        }
        
        compact = {}
        for period in last_periods:
            period_str = str(period)
            compact[period_str] = {}
            for field in required_fields:
                val = None
                mapped_field = field_mapping.get(field, field)
                if mapped_field in bs.index:
                    val = bs.loc[mapped_field, period] if period in bs.columns else None
                elif mapped_field in is_.index:
                    val = is_.loc[mapped_field, period] if period in is_.columns else None
                compact[period_str][field] = val
        return compact
    filtered_sec = filter_sec_facts(sec_facts)
    filtered_yf = filter_yf_data(yf_data)
    sec_json = json.dumps(filtered_sec, indent=2, ensure_ascii=False) if filtered_sec else "null"
    yf_json = json.dumps(filtered_yf, indent=2, ensure_ascii=False) if filtered_yf else "null"
    # Save filtered data for debugging
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(os.path.join(output_dir, "sec_filtered.json"), "w", encoding="utf-8") as f:
            f.write(sec_json)
        with open(os.path.join(output_dir, "yahoo_filtered.json"), "w", encoding="utf-8") as f:
            f.write(yf_json)
    except Exception as e:
        logger.warning(f"[{ticker}] Could not save filtered SEC/Yahoo data: {e}")
    prompt = prompt_template.replace("{sec_data}", sec_json).replace("{yahoo_data}", yf_json)
    # Save prompt for debugging
    try:
        with open(os.path.join(output_dir, "reconcile_prompt.txt"), "w", encoding="utf-8") as f:
            f.write(prompt)
    except Exception as e:
        logger.warning(f"[{ticker}] Could not save LLM prompt: {e}")
    # Send prompt to LLM and get response
    try:
        client = AzureOpenAIClient()
        logger.info(f"[{ticker}] Sending financial reconciliation request to LLM.")
        start_time = time.time()
        messages = [
            {"role": "system", "content": "You are a financial data expert."},
            {"role": "user", "content": prompt},
        ]
        response = client.chat_completion(messages, temperature=0.0, max_tokens=2048)
        elapsed_time = time.time() - start_time
        logger.info(f"[{ticker}] LLM reconciliation completed in {elapsed_time:.2f} seconds.")
        if response and "choices" in response and len(response["choices"]) > 0:
            logger.info(f"[{ticker}] Reconciliation response received.")
            reconciliation_result = response["choices"][0]["message"].get("content", "").strip()
            logger.info(f"[{ticker}] Reconciliation result: {reconciliation_result}")
            # Remove Markdown code block markers if present
            if reconciliation_result.startswith("```json"):
                reconciliation_result = reconciliation_result[len("```json"):].strip()
            if reconciliation_result.startswith("```"):
                reconciliation_result = reconciliation_result[len("```"):].strip()
            if reconciliation_result.endswith("```"):
                reconciliation_result = reconciliation_result[:-3].strip()
            # Attempt to parse JSON response
            try:
                result_json = json.loads(reconciliation_result)
                logger.info(f"[{ticker}] Successfully parsed reconciliation JSON.")
                # Save reconciliation result
                with open(os.path.join(output_dir, "reconciliation_result.json"), "w", encoding="utf-8") as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False, default=str)
                return result_json
            except json.JSONDecodeError as e:
                logger.warning(f"[{ticker}] JSON decoding error in reconciliation response: {e}")
                logger.warning(f"[{ticker}] Reconciliation response text: {reconciliation_result}")
                raise ValueError(f"JSON decoding error in reconciliation response: {e}")
            except Exception as e:
                logger.error(f"[{ticker}] Unexpected error while processing reconciliation response: {e}")
                raise e
        else:
            logger.warning(f"[{ticker}] No valid response from LLM for reconciliation.")
            raise ValueError("No valid response from LLM for reconciliation.")
    except Exception as e:
        logger.error(f"[{ticker}] Exception during financial reconciliation: {e}")
        raise e
    return None
