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

# Function moved to top for proper definition
def df_to_dict_str_keys(df: pd.DataFrame) -> Dict[str, Dict[str, Decimal]]:
    """Convert DataFrame to dictionary with string keys and Decimal values."""
    if not isinstance(df, pd.DataFrame):
        return {}
    return {
        str(row_key): {str(col_key): Decimal(str(val)) if pd.notna(val) else Decimal("0") for col_key, val in row.items()}
        for row_key, row in df.to_dict().items()
    }

def find_matching_field(field_name: str, available_fields: List[str]) -> Optional[str]:
    """Find a matching field name in available fields using direct mapping."""
    if field_name in FIELD_MAPPING:
        # Try exact matches first
        if field_name in available_fields:
            return field_name
        # Then try the mapped fields
        for mapped_name in FIELD_MAPPING[field_name]:
            if mapped_name in available_fields:
                return mapped_name
            # Try case-insensitive match
            for available_field in available_fields:
                if mapped_name.lower() == available_field.lower():
                    return available_field
    return None

def find_xbrl_tag(soup, tag_names):
    """Find XBRL tag value from a list of possible tag names."""
    for name in tag_names:
        tag = soup.find(name.replace(":", "_"))
        if tag:
            try:
                return float(tag.text)
            except (ValueError, TypeError):
                continue
    return None

def fetch_sec_edgar_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch company information from SEC EDGAR for the given ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Company information if available, else None.
    """
    try:
        # Example URL for SEC EDGAR API (replace with actual endpoint if available)
        edgar_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=exclude&start=0&count=40&output=atom"
        headers = {"User-Agent": "Altman-Z-Score-Pipeline"}
        response = requests.get(edgar_url, headers=headers)
        response.raise_for_status()

        # Parse the response (this is an example, actual parsing depends on the API response format)
        company_data = {
            "ticker": ticker,
            "edgar_url": edgar_url,
            "response_text": response.text,  # Save raw response for debugging
        }
        return company_data
    except Exception as e:
        logging.warning(f"Failed to fetch SEC EDGAR data for {ticker}: {e}")
        return None

def fetch_financials(ticker: str, end_date: str, zscore_model: str) -> Optional[Dict[str, Any]]:
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
    logger = logging.getLogger("altman_zscore.fetch_financials")

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
        yf_ticker = yf.Ticker(ticker)
        bs = yf_ticker.quarterly_balance_sheet
        is_ = yf_ticker.quarterly_financials
        
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
                json.dump(raw_data, f, indent=4, ensure_ascii=False, default=str)

            # Fetch and save additional company information from yfinance
            try:
                company_info = yf_ticker.info
                with open(os.path.join(output_dir, "company_info.json"), "w", encoding="utf-8") as f:
                    json.dump(company_info, f, indent=4, ensure_ascii=False, default=str)

                major_holders = yf_ticker.major_holders.to_json()
                with open(os.path.join(output_dir, "major_holders.json"), "w", encoding="utf-8") as f:
                    f.write(json.dumps(json.loads(major_holders), indent=4))

                institutional_holders = yf_ticker.institutional_holders.to_json()
                with open(os.path.join(output_dir, "institutional_holders.json"), "w", encoding="utf-8") as f:
                    f.write(json.dumps(json.loads(institutional_holders), indent=4))

                if isinstance(yf_ticker.recommendations, pd.DataFrame):
                    recommendations = yf_ticker.recommendations.to_json()
                    with open(os.path.join(output_dir, "recommendations.json"), "w", encoding="utf-8") as f:
                        f.write(json.dumps(json.loads(recommendations), indent=4))
            except Exception as e:
                logger.warning(f"[{ticker}] Failed to fetch additional company information from yfinance: {e}")

            # Fetch and save additional company information from SEC EDGAR
            try:
                sec_edgar_data = fetch_sec_edgar_data(ticker)
                if sec_edgar_data:
                    with open(os.path.join(output_dir, "sec_edgar_company_info.json"), "w", encoding="utf-8") as f:
                        json.dump(sec_edgar_data, f, indent=4, ensure_ascii=False, default=str)
            except Exception as e:
                logger.warning(f"[{ticker}] Failed to fetch additional company information from SEC EDGAR: {e}")

            # Fetch and save additional data from yfinance
            try:
                # Fetch historical prices
                historical_prices = yf_ticker.history(period="max")
                historical_prices.to_csv(os.path.join(output_dir, "historical_prices.csv"))

                # Fetch dividends
                dividends = yf_ticker.dividends
                dividends.to_csv(os.path.join(output_dir, "dividends.csv"))

                # Fetch stock splits
                splits = yf_ticker.splits
                splits.to_csv(os.path.join(output_dir, "splits.csv"))
            except Exception as e:
                logger.warning(f"[{ticker}] Failed to fetch additional data from yfinance: {e}")

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
        return None
