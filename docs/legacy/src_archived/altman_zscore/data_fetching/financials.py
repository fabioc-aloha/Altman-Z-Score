"""
Financials data fetching utilities for Altman Z-Score analysis.

DEPRECATED: This file is part of the legacy SEC EDGAR architecture.
New development should use: altman_zscore/layers/data_fetch/fmp_fetcher.py
"""

# All imports should be at the top of the file, per Python best practices.
import decimal
from decimal import Decimal
import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

import pandas as pd
import requests
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
    
    # DEBUG: Log the start_date parameter
    logger.info(f"extract_quarters_from_sec_facts called with start_date={start_date}, end_date={end_date}")
    
    if not sec_facts or "facts" not in sec_facts:
        return []
        
    facts = sec_facts["facts"]
    us_gaap = facts.get("us-gaap", {})
    
    # Build a mapping of quarters using common period endings
    quarter_data = {}
    
    # Iterate through all US GAAP concepts
    for concept_name, concept_data in us_gaap.items():
        units = concept_data.get("units", {})
        usd_values = units.get("USD", [])
        for entry in usd_values:
            if not entry.get("end"):                continue
            period_end = entry["end"]
            period_end_str = str(period_end)
            # Determine period type
            frame = entry.get("frame", "") or ""
            fp = entry.get("fp", "") or ""
            # Only accept quarterly data (ignore annual FY)
            # Accept only quarterly data: look for Q1-Q4 marks in fp or frame
            has_quarterly_frame = any(q in frame for q in ["Q1", "Q2", "Q3", "Q4"])
            has_quarterly_fp = fp in ["Q1", "Q2", "Q3", "Q4"]
            if not (has_quarterly_frame or has_quarterly_fp):
                continue
            
            value = entry.get("val")
            if value is not None:
                # Only add to quarter_data if it's quarterly
                # Initialize quarter if not exists
                if period_end not in quarter_data:
                    quarter_data[period_end] = {"period_end": period_end}
                quarter_data[period_end][concept_name] = value
    
    # Convert to list of quarters and sort by period_end descending
    quarters = list(quarter_data.values())
    logger.info(f"Total quarters before filtering: {len(quarters)}")
    
    # Sort and apply date range filters
    quarters.sort(key=lambda x: x['period_end'], reverse=True)
    # Filter by start_date and end_date if provided
    if start_date or end_date:
        start_dt = None
        end_dt = None
        try:
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                logger.info(f"Parsed start_date to: {start_dt}")
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                logger.info(f"Parsed end_date to: {end_dt}")
        except Exception as e:
            logger.warning(f"Invalid date filter format: {e}")
        filtered = []
        for q in quarters:
            pe = q.get('period_end')
            try:
                # Parse period_end to date
                pe_dt = datetime.strptime(str(pe)[:10], "%Y-%m-%d").date()
            except Exception:
                continue
            # Apply filters
            if start_dt and pe_dt < start_dt:
                logger.debug(f"Filtering out quarter {pe} (before start_date {start_dt})")
                continue
            if end_dt and pe_dt > end_dt:
                logger.debug(f"Filtering out quarter {pe} (after end_date {end_dt})")
                continue
            filtered.append(q)
        logger.info(f"Filtered to {len(filtered)} quarterly periods after date filtering")
        quarters = filtered
    logger.info(f"Extracted {len(quarters)} quarterly periods from SEC facts")
    return quarters


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
    DEPRECATED: Legacy SEC EDGAR-based financial data fetcher.
    
    This function is part of the legacy architecture that used SEC EDGAR for financial data.
    It has been deprecated in favor of the new FMP-based pipeline.
    
    Please use: altman_zscore.main_pipeline.AltmanZScorePipeline instead.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        end_date (str): End date for financials.
        zscore_model (str): Z-Score model name (determines required fields).
        start_date (str, optional): Start date for financials (if provided, filters quarters).

    Returns:
        dict: Error message indicating this function is deprecated.

    Notes:
        - DEPRECATED: This function has been replaced by FMP-based pipeline
        - Please use: altman_zscore.main_pipeline.AltmanZScorePipeline instead
    """
    logger = logging.getLogger("altman_zscore.fetch_financials")
    logger.warning(f"[{ticker}] DEPRECATED: fetch_financials() is deprecated. Please use altman_zscore.main_pipeline.AltmanZScorePipeline instead.")
    
    return {
        "error": "DEPRECATED: This function has been replaced by the FMP-based pipeline. Please use altman_zscore.main_pipeline.AltmanZScorePipeline.",
        "quarters": [],
        "message": "SEC EDGAR functionality has been eliminated in favor of FMP pre-calculated ratios."
    }
