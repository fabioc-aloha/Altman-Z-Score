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

from src.altman_zscore.api.cached_field_mapper import CachedFieldMapper
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
    
    # Track annual data separately for backfilling revenue/sales
    annual_data = {}
    
    # Iterate through all US GAAP concepts
    for concept_name, concept_data in us_gaap.items():
        units = concept_data.get("units", {})
        
        # Look for USD values (most financial data is in USD)
        usd_values = units.get("USD", [])
        
        for entry in usd_values:
            # Must have an end date (point in time for balance sheet, period end for income statement)
            if not entry.get("end"):                continue
                
            period_end = entry["end"]
            
            # Apply date filters if provided (but be more generous for quarterly data)
            # Ensure all dates are strings for comparison
            period_end_str = str(period_end) if period_end else ""
            start_date_str = str(start_date) if start_date else ""
            end_date_str = str(end_date) if end_date else ""
            
            if start_date_str and period_end_str < start_date_str:
                continue
            if end_date_str and period_end_str > end_date_str:
                continue
                
            # For quarterly data, accept multiple types of periods
            frame = entry.get("frame", "")
            fp = entry.get("fp", "")
            
            # Accept quarterly data: Q1, Q2, Q3, Q4 in frame OR fp
            has_quarterly_frame = any(q in frame for q in ["Q1", "Q2", "Q3", "Q4"])
            has_quarterly_fp = fp in ["Q1", "Q2", "Q3", "Q4"]  # Include Q4
            
            # Track annual data (FY) separately for backfilling
            is_annual = fp == "FY" or "FY" in frame
            
            # Also accept recent data (last 3 years) to capture any reporting format
            is_recent = period_end_str >= "2021-01-01"
            
            # Accept if it's quarterly, annual, or recent
            if not (has_quarterly_frame or has_quarterly_fp or is_annual or is_recent):
                continue
                
            value = entry.get("val")
            if value is not None:
                # Store annual data separately for revenue backfilling
                if is_annual and concept_name in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
                    year = period_end[:4]  # Extract year from YYYY-MM-DD
                    if year not in annual_data:
                        annual_data[year] = {}
                    annual_data[year][concept_name] = value
                
                # Initialize quarter if not exists
                if period_end not in quarter_data:
                    quarter_data[period_end] = {"period_end": period_end}
                    
                # Store the value (use the most recent filing for each concept)
                quarter_data[period_end][concept_name] = value
    
    # Backfill revenue data for quarters that are missing it
    for period_end, quarter in quarter_data.items():
        year = period_end[:4]
        
        # If this quarter is missing revenue data, try to use annual data
        has_revenue = any(concept in quarter for concept in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"])
        
        if not has_revenue and year in annual_data:
            # Use annual revenue data for this quarter
            for concept_name, value in annual_data[year].items():
                if concept_name not in quarter:
                    quarter[concept_name] = value
                    logger.debug(f"Backfilled {concept_name} for {period_end} with annual value: {value}")
    
    # Convert to list and sort by period_end
    quarters = list(quarter_data.values())
    quarters.sort(key=lambda x: x["period_end"], reverse=True)
    
    # Filter out quarters with insufficient data for Z-Score calculation
    # A valid quarter should have at least 4-5 core financial fields beyond just period_end
    valid_quarters = []
    for quarter in quarters:
        field_count = len([k for k in quarter.keys() if k not in ['period_end']])
        
        # Require at least 4 financial fields for a valid quarter
        # This filters out spurious periods like 2024-05-01 that only have revenue
        if field_count >= 4:
            valid_quarters.append(quarter)
        else:
            logger.debug(f"Filtered out incomplete quarter {quarter['period_end']} with only {field_count} fields: {list(quarter.keys())}")
    
    logger.info(f"Extracted {len(quarters)} total periods, {len(valid_quarters)} valid quarters after filtering")
    return valid_quarters


def apply_cached_field_mapping(sec_quarters: list, fields_to_fetch: list, ticker: str) -> list:
    """
    Apply cached field mapping to map SEC GAAP concepts to Z-Score fields.
    
    Args:
        sec_quarters: List of quarterly data from SEC facts
        fields_to_fetch: Required Z-Score field names
        ticker: Stock ticker for context
        
    Returns:
        List of quarters with mapped fields
    """
    logger = logging.getLogger("altman_zscore.apply_cached_field_mapping")
    
    if not sec_quarters:
        return []
    
    # Try cached field mapping first
    try:
        mapper = CachedFieldMapper()
        mapped_quarters = []
        
        for quarter in sec_quarters:
            mapped_quarter = mapper.map_sec_quarter_to_canonical(quarter, fields_to_fetch, ticker)
            if mapped_quarter and len(mapped_quarter) > 1:  # More than just period_end
                mapped_quarters.append(mapped_quarter)
        
        if mapped_quarters:
            # Check mapping completeness
            total_mappings = 0
            successful_mappings = 0
            
            for quarter in mapped_quarters:
                for field in fields_to_fetch:
                    total_mappings += 1
                    if field in quarter and quarter[field] is not None:
                        successful_mappings += 1
            
            mapping_completeness = successful_mappings / total_mappings if total_mappings > 0 else 0
            logger.info(f"[{ticker}] Cached mapping completeness: {mapping_completeness:.1%} ({successful_mappings}/{total_mappings})")
            
            # If cached mapping is reasonably complete (>50%), use it
            logger.info(f"[{ticker}] Using cached field mapping (completeness: {mapping_completeness:.1%})")
            return mapped_quarters
            
    except Exception as e:
        logger.warning(f"[{ticker}] Cached field mapping failed: {e}")
    
    return []


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
        - Uses cached field mapping only (no LLM/AI mapping)
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
            # Always use cached field mapping
            sec_quarters = apply_cached_field_mapping(sec_quarters, fields_to_fetch, ticker)
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
