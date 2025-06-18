"""
Financials data fetching utilities for Altman Z-Score analysis.

Clean architecture: SEC EDGAR for financial facts, Yahoo Finance for market data only.
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


def extract_quarters_from_sec_facts(sec_facts: Dict[str, Any], fields_to_fetch: list, 
                                    start_date: str = None, end_date: str = None) -> list:
    """
    Extract quarterly financial data from SEC facts.
    
    Args:
        sec_facts: SEC facts dictionary from get_company_facts
        fields_to_fetch: List of field names needed for Z-Score calculation
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        
    Returns:
        List of quarterly data dictionaries with period_end and financial fields
    """
    logger = logging.getLogger("altman_zscore.extract_quarters_from_sec_facts")
    
    if not sec_facts or "facts" not in sec_facts:
        return []
        
    facts = sec_facts["facts"]
    us_gaap = facts.get("us-gaap", {})
    
    # Build a mapping of quarters using common period endings
    quarter_data = {}
    
    # Iterate through all US GAAP concepts
    for concept_name, concept_data in us_gaap.items():
        units = concept_data.get("units", {})
        
        # Look for USD values (most financial data is in USD)
        usd_values = units.get("USD", [])
        
        for entry in usd_values:
            # Only process quarterly data (has start and end dates, and frame info)
            if not entry.get("end") or not entry.get("start") or not entry.get("frame"):
                continue
                
            # Filter quarterly frames (Q1, Q2, Q3, Q4)
            frame = entry.get("frame", "")
            if not any(q in frame for q in ["Q1", "Q2", "Q3", "Q4"]):
                continue
                
            period_end = entry["end"]
            
            # Apply date filters if provided
            if start_date and period_end < start_date:
                continue
            if end_date and period_end > end_date:
                continue
                
            # Initialize quarter if not exists
            if period_end not in quarter_data:
                quarter_data[period_end] = {"period_end": period_end}
                
            # Store the value (use the most recent filing for each concept)
            value = entry.get("val")
            if value is not None:
                quarter_data[period_end][concept_name] = value
    
    # Convert to list and sort by period_end
    quarters = list(quarter_data.values())
    quarters.sort(key=lambda x: x["period_end"], reverse=True)
    
    logger.info(f"Extracted {len(quarters)} quarters from SEC facts")
    return quarters


def apply_ai_field_mapping(sec_quarters: list, fields_to_fetch: list, ticker: str) -> list:
    """
    Apply AI-powered field mapping to map SEC GAAP concepts to Z-Score fields.
    
    Args:
        sec_quarters: List of quarterly data from SEC facts
        fields_to_fetch: Required Z-Score field names
        ticker: Stock ticker for context
        
    Returns:
        List of quarters with mapped fields
    """
    logger = logging.getLogger("altman_zscore.apply_ai_field_mapping")
    
    if not sec_quarters:
        return []
    
    # Collect all available SEC concepts for mapping
    all_sec_fields = set()
    sample_values = {}
    
    for quarter in sec_quarters:
        for field, value in quarter.items():
            if field != "period_end" and value is not None:
                all_sec_fields.add(field)
                if field not in sample_values:
                    sample_values[field] = value
    
    raw_fields = list(all_sec_fields)
    
    # Use AI to map SEC concepts to Z-Score fields
    direct_mapping = {}
    try:
        client = AzureOpenAIClient()
        ai_mapping = client.suggest_field_mapping(raw_fields, fields_to_fetch, sample_values, ticker=ticker)
        if ai_mapping:
            for field, mapped in ai_mapping.items():
                if isinstance(mapped, dict):
                    direct_mapping[field] = mapped.get("FoundField")
                else:
                    direct_mapping[field] = mapped
        logger.info(f"AI mapping successful for {ticker}: {len(direct_mapping)} fields mapped")
    except Exception as e:
        logger.warning(f"AI field mapping failed for {ticker}: {e}. Using empty mapping.")
    
    # Apply mapping to each quarter
    mapped_quarters = []
    for quarter in sec_quarters:
        mapped_quarter = {"period_end": quarter["period_end"]}
        field_mapping = {}
        missing = []
        
        for field in fields_to_fetch:
            val = None
            mapped_field = None
            raw_field = direct_mapping.get(field)
            
            if raw_field and isinstance(raw_field, str):
                if raw_field.startswith("INFERRED:"):
                    # Handle inferred calculations (e.g., retained earnings)
                    _, equity_field, paid_in_field = raw_field.split(":")
                    try:
                        equity_val = quarter.get(equity_field)
                        paid_in_val = quarter.get(paid_in_field)
                        if equity_val is not None and paid_in_val is not None:
                            equity_dec = safe_to_decimal(str(equity_val))
                            paid_in_dec = safe_to_decimal(str(paid_in_val))
                            if equity_dec is not None and paid_in_dec is not None:
                                val = equity_dec - paid_in_dec
                                mapped_field = f"Inferred from {equity_field} minus {paid_in_field}"
                    except Exception as e:
                        logger.warning(f"Failed to calculate inferred value for {field}: {e}")
                        missing.append(field)
                        continue
                else:
                    # Direct field mapping
                    mapped_field = raw_field
                    val = quarter.get(raw_field)
                    if val is not None:
                        val = safe_to_decimal(str(val))
            
            if val is None or val in [0, Decimal("0")]:
                missing.append(field)
            else:
                mapped_quarter[field] = val
                field_mapping[field] = mapped_field
        
        if mapped_quarter.keys() != {"period_end"}:  # Has some data
            mapped_quarter["field_mapping"] = json.dumps(field_mapping, default=str)
            mapped_quarters.append(mapped_quarter)
    
    logger.info(f"Applied field mapping to {len(mapped_quarters)} quarters for {ticker}")
    return mapped_quarters


def fetch_market_data_from_yahoo(ticker: str, output_dir: str) -> Dict[str, Any]:
    """
    Fetch market data from Yahoo Finance: prices, shares outstanding, market cap, etc.
    
    Args:
        ticker: Stock ticker symbol
        output_dir: Directory to save market data files
        
    Returns:
        Dictionary containing market data
    """
    logger = logging.getLogger("altman_zscore.fetch_market_data_from_yahoo")
    
    try:
        yf_data = fetch_yfinance_full(ticker)
        
        if not yf_data:
            logger.warning(f"[{ticker}] No Yahoo Finance data available")
            return {}
        
        # Save market data files
        market_data = {}
        
        # Save analyst recommendations
        recommendations = yf_data.get("recommendations")
        if recommendations is not None and not (isinstance(recommendations, pd.DataFrame) and recommendations.empty):
            try:
                if isinstance(recommendations, pd.DataFrame):
                    rec_data = recommendations.to_dict('records')
                else:
                    rec_data = recommendations
                
                rec_path = os.path.join(output_dir, "recommendations.json")
                with open(rec_path, "w", encoding="utf-8") as f:
                    json.dump(rec_data, f, indent=2, ensure_ascii=False, default=str)
                market_data["recommendations"] = rec_data
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
                market_data["major_holders"] = holders_data
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
                market_data["institutional_holders"] = inst_data
                logger.debug(f"Saved institutional holders to {inst_path}")
            except Exception as e:
                logger.warning(f"Failed to save institutional holders for {ticker}: {e}")
                
        # Save historical prices
        historical_prices = yf_data.get("historical_prices")
        if historical_prices is not None and not (isinstance(historical_prices, pd.DataFrame) and historical_prices.empty):
            try:
                prices_path = os.path.join(output_dir, "historical_prices.csv")
                if isinstance(historical_prices, pd.DataFrame):
                    historical_prices.to_csv(prices_path)
                market_data["historical_prices"] = "saved_to_csv"
                logger.debug(f"Saved historical prices to {prices_path}")
            except Exception as e:
                logger.warning(f"Failed to save historical prices for {ticker}: {e}")
        
        # Save dividends and splits
        dividends = yf_data.get("dividends")
        if dividends is not None and not (isinstance(dividends, pd.Series) and dividends.empty):
            try:
                div_path = os.path.join(output_dir, "dividends.csv")
                if isinstance(dividends, pd.Series):
                    dividends.to_csv(div_path)
                market_data["dividends"] = "saved_to_csv"
                logger.debug(f"Saved dividends to {div_path}")
            except Exception as e:
                logger.warning(f"Failed to save dividends for {ticker}: {e}")
        
        splits = yf_data.get("splits")
        if splits is not None and not (isinstance(splits, pd.Series) and splits.empty):
            try:
                splits_path = os.path.join(output_dir, "splits.csv")
                if isinstance(splits, pd.Series):
                    splits.to_csv(splits_path)
                market_data["splits"] = "saved_to_csv"
                logger.debug(f"Saved splits to {splits_path}")
            except Exception as e:
                logger.warning(f"Failed to save splits for {ticker}: {e}")
        
        # Extract key market info for Z-Score calculation
        info = yf_data.get("info", {})
        market_data.update({
            "market_cap": info.get("marketCap"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "current_price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "enterprise_value": info.get("enterpriseValue"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash")
        })
        
        logger.info(f"[{ticker}] Successfully fetched market data from Yahoo Finance")
        return market_data
        
    except Exception as e:
        logger.error(f"[{ticker}] Failed to fetch market data from Yahoo: {e}")
        return {}


@exponential_retry(
    max_retries=3,
    base_delay=1.0,
    backoff_factor=2.0,
    exceptions=NETWORK_EXCEPTIONS
)
def fetch_financials(ticker: str, end_date: str, zscore_model: str, start_date: str = None) -> Optional[Dict[str, Any]]:
    """
    Fetch quarterly financials using SEC EDGAR for financial facts and Yahoo Finance for market data.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        end_date (str): End date for financials.
        zscore_model (str): Z-Score model name (determines required fields).
        start_date (str, optional): Start date for financials (if provided, filters quarters).

    Returns:
        dict or None: {"quarters": [dict, ...]} if data found, else None.

    Notes:
        - Uses SEC EDGAR for financial facts (balance sheet, income statement)
        - Uses Yahoo Finance for market data (prices, shares outstanding, market cap)
        - Implements AI-powered field mapping to bridge SEC concepts to Z-Score fields
        - Saves all raw and processed data to disk for reproducibility
        - Logs all errors and warnings for traceability
    """
    logger = logging.getLogger("altman_zscore.fetch_financials")

    if zscore_model not in MODEL_FIELDS:
        logger.error(f"Invalid Z-Score model {zscore_model}")
        return None

    output_dir = get_output_dir(ticker)
    fields_to_fetch = list(MODEL_FIELDS[zscore_model]) if zscore_model in MODEL_FIELDS else list(MODEL_FIELDS["original"])
    if "sales" not in fields_to_fetch:
        fields_to_fetch.append("sales")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- 1. SEC EDGAR for Financial Facts ---
    sec_quarters = []
    try:
        from altman_zscore.api.sec_client import SECClient
        sec_client = SECClient()
        cik = sec_client.lookup_cik(ticker)
        sec_facts = sec_client.get_company_facts(cik) if cik else None
        
        # Save raw SEC facts
        try:
            with open(os.path.join(output_dir, "sec_facts_raw.json"), "w", encoding="utf-8") as f:
                json.dump(sec_facts, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"[{ticker}] Could not save raw SEC facts: {e}")
        
        # Extract quarters from SEC facts
        if sec_facts and sec_facts.get('facts'):
            sec_quarters = extract_quarters_from_sec_facts(sec_facts, fields_to_fetch, start_date, end_date)
            logger.info(f"[{ticker}] Extracted {len(sec_quarters)} quarters from SEC facts")
            
            # Apply AI field mapping to SEC data
            sec_quarters = apply_ai_field_mapping(sec_quarters, fields_to_fetch, ticker)
        else:
            logger.warning(f"[{ticker}] No SEC company facts available")
            
    except Exception as sec_e:
        logger.warning(f"[{ticker}] SEC EDGAR extraction failed: {sec_e}")

    # --- 2. Yahoo Finance for Market Data ---
    market_data = fetch_market_data_from_yahoo(ticker, output_dir)

    # --- 3. Combine and Validate ---
    if not sec_quarters:
        logger.error(f"[{ticker}] No financial data available from SEC EDGAR")
        return {
            "error": "No financial data available from SEC EDGAR. SEC data is required for financial analysis.",
            "quarters": [],
            "missing_fields_by_quarter": []
        }

    # Save processed SEC quarters
    try:
        with open(os.path.join(output_dir, "financials_quarterly.json"), "w", encoding="utf-8") as f:
            json.dump(sec_quarters, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        logger.warning(f"[{ticker}] Could not save processed quarters: {e}")

    # Validate that we have meaningful financial data
    if sec_quarters:
        non_asset_fields = [f for f in fields_to_fetch if f not in ("total_assets", "current_assets", "current_liabilities", "total_liabilities")]
        all_zero = True
        for q in sec_quarters:
            if any(q.get(f, 0) not in (0, None, Decimal("0")) for f in non_asset_fields):
                all_zero = False
                break
        
        if all_zero:
            logger.error(f"[{ticker}] SEC data contains only balance sheet items; no income statement data found")
            return {
                "error": "SEC data for this ticker does not contain the required income statement fields (e.g., sales, EBIT, retained earnings). Only balance sheet data is available. No Z-Score can be computed.",
                "quarters": sec_quarters,
                "missing_fields_by_quarter": []
            }

    logger.info(f"[{ticker}] Successfully fetched financials: {len(sec_quarters)} quarters from SEC, market data from Yahoo")
    return {
        "quarters": sec_quarters,
        "market_data": market_data,
        "missing_fields_by_quarter": []  # Could be enhanced to track missing fields per quarter
    }


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
    return fetch_financials(ticker, end_date, zscore_model, start_date)
