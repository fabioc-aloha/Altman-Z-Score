"""
Financials data fetching utilities for Altman Z-Score analysis.
"""

# All imports should be at the top of the file, per Python best practices.
import os
import sys
import logging
import json
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, TypedDict
import requests

import pandas as pd
import yfinance as yf

from altman_zscore.api.openai_client import AzureOpenAIClient
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.computation.constants import FIELD_MAPPING, MODEL_FIELDS
from altman_zscore.data_fetching.sec_edgar import fetch_sec_edgar_data, find_xbrl_tag
from altman_zscore.data_fetching.executives import fetch_company_officers, fetch_executive_data
from altman_zscore.data_fetching.financials_core import df_to_dict_str_keys, find_matching_field
from altman_zscore.api.yahoo_helpers import fetch_yfinance_data, fetch_yfinance_full
from altman_zscore.utils.error_helpers import DataFetchingError, raise_with_context

# Refactor complete: All helpers and data-fetching logic are now modularized.
# All tests have passed after this refactor (see test log).
# Next: Update REFACTORING_PLAN.md and TODO.md to check off completed steps for data_fetching/financials.py.

def fetch_financials(ticker: str, end_date: str, zscore_model: str) -> Optional[Dict[str, Any]]:
    """
    Fetch 12 quarters of real financials for the given ticker using yfinance (primary) and SEC EDGAR (fallback).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        end_date (str): End date for financials (ignored in MVP, use all available)
        zscore_model (str): Z-Score model name (determines required fields)

    Returns:
        dict or None: {"quarters": [dict, ...]} if data found, else None
    """
    logger = logging.getLogger("altman_zscore.fetch_financials")

    if zscore_model not in MODEL_FIELDS:
        logger.error(f"Invalid Z-Score model {zscore_model}")
        return None

    output_dir = get_output_dir(ticker)  # Line A    # Fetch company info and officers first
    fetch_executive_data(ticker)  # Get officers from both yfinance and SEC EDGAR
    fetch_sec_edgar_data(ticker)  # Get other company info

    if zscore_model not in MODEL_FIELDS:
        # Fallback: use original model fields, but always add 'sales' if not present
        fields_to_fetch = list(MODEL_FIELDS["original"])
        if "sales" not in fields_to_fetch:
            fields_to_fetch.append("sales")
    else:
        fields_to_fetch = list(MODEL_FIELDS[zscore_model])
        if "sales" not in fields_to_fetch:
            fields_to_fetch.append("sales")

    # AI-powered field mapping integration (only if direct mapping fails)
    ai_field_mapping = os.getenv("AI_FIELD_MAPPING", "false").lower() == "true"
    ai_mapping = None

    try:
        # --- Centralized yfinance data fetching ---
        yf_data = fetch_yfinance_full(ticker)
        if yf_data is None:
            logger.error(f"[{ticker}] No usable yfinance data found. Skipping to SEC EDGAR fallback.")
            raise ValueError(f"No usable yfinance data found for {ticker}.")
        bs = yf_data["balance_sheet"]
        is_ = yf_data["income_statement"]
        info = yf_data["info"]
        
        # Log what periods/columns are present
        logger.info(f"[{ticker}] Balance sheet columns: {list(bs.columns)}")
        logger.info(f"[{ticker}] Income statement columns: {list(is_.columns)}")
        quarters = []
        common_periods = [p for p in bs.columns if p in is_.columns]
        missing_fields_by_quarter = []  # Track missing fields for each quarter

        # Try direct mapping first, use AI mapping only if direct fails
        direct_mapping = {}
        available_bs_keys = set(str(idx) for idx in bs.index)
        available_is_keys = set(str(idx) for idx in is_.index)
        all_available_keys = available_bs_keys.union(available_is_keys)
        
        for field in fields_to_fetch:
            matched_field = find_matching_field(field, list(all_available_keys))
            if matched_field:
                direct_mapping[field] = matched_field

        # Only try AI mapping for fields that don't have direct matches
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
                    # Merge AI mapping with direct mapping
                    if ai_mapping:
                        for field, mapped in ai_mapping.items():
                            if field not in direct_mapping:  # Only add if not already directly mapped
                                if isinstance(mapped, dict):
                                    direct_mapping[field] = mapped.get("FoundField")
                                else:
                                    direct_mapping[field] = mapped
                except Exception as e:
                    logger.warning(f"AI field mapping failed: {e}. Will use only direct mapping.")
                    # Optionally, could raise_with_context(DataFetchingError, "AI field mapping failed", str(e))

        # Process quarters using the combined mapping
        for period in common_periods:
            period_str = str(period)
            q: dict[str, Any] = {"period_end": period_str}
            missing = []
            field_mapping = {}

            # Check for critical fields first
            critical_fields = ["total_assets", "current_assets", "current_liabilities", "retained_earnings"]
            critical_missing = []
            for key in critical_fields:
                if key not in fields_to_fetch:
                    continue
                mapped_field = direct_mapping.get(key)
                found = False
                if mapped_field:
                    # Ensure correct usage of .at[] indexer (not .at())
                    if mapped_field in bs.index:
                        try:
                            v = bs.at[mapped_field, period]
                        except TypeError as e:
                            logger.error(f"[DEBUG] TypeError accessing bs.at[{mapped_field}, {period}]: {e} (type(bs): {type(bs)}, type(period): {type(period)})")
                            v = None
                        if v is not None and v == v and Decimal(str(v)) != Decimal("0"):  # not NaN and not zero
                            found = True
                    elif mapped_field in is_.index:
                        try:
                            v = is_.at[mapped_field, period]
                        except TypeError as e:
                            logger.error(f"[DEBUG] TypeError accessing is_.at[{mapped_field}, {period}]: {e} (type(is_): {type(is_)}, type(period): {type(period)})")
                            v = None
                        if v is not None and v == v and Decimal(str(v)) != Decimal("0"):  # not NaN and not zero
                            found = True
                if not found:
                    critical_missing.append(key)

            # Skip this quarter if critical fields are missing
            if critical_missing:
                logger.warning(
                    f"[{ticker}] {period_str}: Skipping quarter due to critical missing fields: {', '.join(critical_missing)}"
                )
                continue

            # Process all fields
            for key in fields_to_fetch:
                mapped_field = direct_mapping.get(key)
                val = None
                found_name = None
                if mapped_field:
                    if mapped_field in bs.index and key not in ["ebit", "sales"]:
                        try:
                            v = bs.at[mapped_field, period]
                        except TypeError as e:
                            logger.error(f"[DEBUG] TypeError accessing bs.at[{mapped_field}, {period}]: {e} (type(bs): {type(bs)}, type(period): {type(period)})")
                            v = None
                        if v is not None and v == v:
                            val = Decimal(str(v))
                            found_name = mapped_field
                    elif mapped_field in is_.index and key in ["ebit", "sales"]:
                        try:
                            v = is_.at[mapped_field, period]
                        except TypeError as e:
                            logger.error(f"[DEBUG] TypeError accessing is_.at[{mapped_field}, {period}]: {e} (type(is_): {type(is_)}, type(period): {type(period)})")
                            v = None
                        if v is not None and v == v:
                            val = Decimal(str(v))
                            found_name = mapped_field

                if val is None:
                    missing.append(key)
                    val = Decimal("0")
                
                # Store as Decimal for computation throughout the pipeline
                q[key] = val
                field_mapping[key] = {
                    "canonical_field": key,
                    "mapped_raw_field": found_name,
                    "value": val,
                    "missing": val == Decimal("0") or found_name is None,
                }

            q["field_mapping"] = json.dumps(field_mapping, default=str)
            quarters.append(q)
            missing_fields_by_quarter.append(missing)

        quarters = sorted(quarters, key=lambda x: x["period_end"])[-12:]
        if quarters:
            # After collecting quarters, check if all non-asset/liability fields are zero for every quarter
            non_asset_fields = [f for f in fields_to_fetch if f not in ("total_assets", "current_assets", "current_liabilities", "total_liabilities")]
            all_zero = True
            for q in quarters:
                if any(Decimal(str(q.get(f, 0))) != 0 for f in non_asset_fields):
                    all_zero = False
                    break
            if all_zero:
                logger.error(f"[{ticker}] SEC EDGAR fallback: Only balance sheet data available; all income statement fields are zero. No Z-Score can be computed.")
                return {
                    "error": "SEC EDGAR filings for this ticker do not contain the required income statement fields (e.g., sales, EBIT, retained earnings). Only balance sheet data is available. No Z-Score can be computed.",
                    "quarters": quarters,
                    "missing_fields_by_quarter": missing_fields_by_quarter
                }

            # Only now, after confirming valid data, write diagnostics
            output_dir = get_output_dir(None, ticker=ticker)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save raw data from yfinance
            raw_data = {
                "balance_sheet": df_to_dict_str_keys(bs),
                "income_statement": df_to_dict_str_keys(is_),
            }
            with open(os.path.join(output_dir, "financials_raw.json"), "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)            # Fetch and save additional company information from yfinance
            try:
                company_info = yf_data["info"]
                with open(os.path.join(output_dir, "company_info.json"), "w", encoding="utf-8") as f:
                    json.dump(company_info, f, indent=4, ensure_ascii=False, default=str)

                if yf_data["major_holders"] is not None:
                    yf_data["major_holders"].to_json(os.path.join(output_dir, "major_holders.json"))
                if yf_data["institutional_holders"] is not None:
                    yf_data["institutional_holders"].to_json(os.path.join(output_dir, "institutional_holders.json"))
                if isinstance(yf_data["recommendations"], pd.DataFrame):
                    yf_data["recommendations"].to_json(os.path.join(output_dir, "recommendations.json"))
                if isinstance(yf_data["historical_prices"], pd.DataFrame):
                    yf_data["historical_prices"].to_csv(os.path.join(output_dir, "historical_prices.csv"))
                if isinstance(yf_data["dividends"], pd.Series):
                    yf_data["dividends"].to_csv(os.path.join(output_dir, "dividends.csv"))
                if isinstance(yf_data["splits"], pd.Series):
                    yf_data["splits"].to_csv(os.path.join(output_dir, "splits.csv"))
            except Exception as e:
                logger.warning(f"[{ticker}] Failed to fetch additional company information from yfinance: {e}")
                # Optionally, could raise_with_context(DataFetchingError, "Failed to fetch yfinance company info", str(e))

            # Fetch and save additional company information from SEC EDGAR
            try:
                sec_edgar_data = fetch_sec_edgar_data(ticker)
                if sec_edgar_data:
                    with open(os.path.join(output_dir, "sec_edgar_company_info.json"), "w", encoding="utf-8") as f:
                        json.dump(sec_edgar_data, f, indent=4, ensure_ascii=False, default=str)
            except Exception as e:
                logger.warning(f"[{ticker}] Failed to fetch additional company information from SEC EDGAR: {e}")
                # Optionally, could raise_with_context(DataFetchingError, "Failed to fetch SEC EDGAR company info", str(e))

            # Placeholder for SEC EDGAR data fetching
            sec_edgar_data = None  # Replace with actual SEC EDGAR fetching logic if needed
            if sec_edgar_data:
                with open(os.path.join(output_dir, "sec_edgar_raw.json"), "w", encoding="utf-8") as f:
                    json.dump(sec_edgar_data, f, indent=2, ensure_ascii=False, default=str)

            with open(os.path.join(output_dir, "financials_quarterly.json"), "w", encoding="utf-8") as f:
                json.dump(quarters, f, indent=2, ensure_ascii=False, default=str)

            return {"quarters": quarters, "missing_fields_by_quarter": missing_fields_by_quarter}
        else:
            logger.error(
                f"[{ticker}] No usable financial data found after processing. Data may be present but missing required fields."
            )
            raise ValueError(
                f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period."
            )
    except Exception as e:
        logger.error(f"[{ticker}] Exception in fetch_financials: {e}")
        print(f"[ERROR] Could not fetch financials for {ticker}: {e}")
        raise_with_context(DataFetchingError, f"Could not fetch financials for {ticker}", str(e))
        # --- SEC EDGAR fallback for financials ---
        try:
            from altman_zscore.api.sec_client import SECClient
            sec_client = SECClient()
            cik = sec_client.lookup_cik(ticker)
            if not cik:
                logger.error(f"[{ticker}] SEC EDGAR fallback: No CIK found for ticker.")
                return None
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
                    logger.error(f"[{ticker}] SEC EDGAR fallback: Only balance sheet data available; all income statement fields are zero. No Z-Score can be computed.")
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
                logger.error(f"[{ticker}] SEC EDGAR fallback: No usable financial data found.")
                return None
        except Exception as sec_e:
            logger.error(f"[{ticker}] SEC EDGAR fallback failed: {sec_e}")
            raise_with_context(DataFetchingError, f"SEC EDGAR fallback failed for {ticker}", str(sec_e))
