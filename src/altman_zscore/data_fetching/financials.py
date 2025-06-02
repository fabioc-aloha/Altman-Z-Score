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
        from altman_zscore.api.sec_client import SECClient
        client = SECClient()
        company_data = client.get_company_info(ticker, save_to_file=True)
        if company_data is None:
            return None

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
            return None

def fetch_company_officers(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch company officers information using yfinance.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Company officers information if available, else None

    Notes:
        - Fetches officer information from yfinance info property
        - Returns None if no officer data is found
        - Logs any errors during fetch
    """
    logger = logging.getLogger("altman_zscore.fetch_company_officers")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            logger.warning(f"No company info found for {ticker}")
            return None

        # Extract officers if available
        officers = info.get('companyOfficers') or info.get('officers') or []

        # Format officer data
        formatted_officers = []
        for officer in officers:
            formatted_officer = {
                'name': officer.get('name'),
                'title': officer.get('title'),
                'yearBorn': officer.get('yearBorn'),
                'age': officer.get('age'),
                'totalPay': officer.get('totalPay'),
            }
            formatted_officers.append(formatted_officer)

        if not formatted_officers:
            logger.warning(f"No officer data found for {ticker}")
            return None

        # Save the data
        output_dir = get_output_dir(ticker)
        officers_file = os.path.join(output_dir, "company_officers.json")
        with open(officers_file, 'w', encoding='utf-8') as f:
            json.dump({'officers': formatted_officers}, f, indent=4, ensure_ascii=False)

        return {'officers': formatted_officers}

    except Exception as e:
        logger.error(f"Error fetching company officers for {ticker}: {e}")
        return None

def fetch_executive_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch executive data from both yfinance (primary) and SEC EDGAR (supplementary).
    Merges data from both sources when available.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Executive data if available, else None

    Notes:
        - Uses yfinance as primary source for current officers
        - Uses SEC EDGAR DEF 14A filings for additional/historical data
        - Merges data when available from both sources
        - Returns None if no data is found from either source
    """
    logger = logging.getLogger("altman_zscore.fetch_executive_data")
    output_dir = get_output_dir(ticker)

    try:
        # 1. First try yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        yf_officers = []

        if info:
            # Extract officers if available
            officers = info.get('companyOfficers') or info.get('officers') or []
            for officer in officers:
                formatted_officer = {
                    'name': officer.get('name'),
                    'title': officer.get('title'),
                    'yearBorn': officer.get('yearBorn'),
                    'age': officer.get('age'),
                    'totalPay': officer.get('totalPay'),
                    'source': 'yfinance'
                }
                yf_officers.append(formatted_officer)

        # 2. Try SEC EDGAR
        sec_officers = []
        try:
            from altman_zscore.api.sec_client import SECClient
            from bs4 import BeautifulSoup, Tag  # Import Tag for type hints
            client = SECClient()
            
            # First get CIK
            cik = client.lookup_cik(ticker)
            if cik:
                # Get company submissions
                url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
                response = requests.get(url, 
                    headers={'User-Agent': f'altman-zscore-analyzer ({os.getenv("SEC_API_EMAIL")})'})
                
                if response.ok:
                    data = response.json()
                    filings = data.get('filings', {}).get('recent', {})
                    
                    if filings:
                        form_types = filings.get('form', [])
                        accession_numbers = filings.get('accessionNumber', [])
                        primary_docs = filings.get('primaryDocument', [])
                        filing_dates = filings.get('filingDate', [])

                        # Find latest DEF 14A filing
                        def_14a_indices = [i for i, form in enumerate(form_types) if form == 'DEF 14A']
                        if def_14a_indices:
                            latest_def_14a_idx = def_14a_indices[0]
                            accession_number = accession_numbers[latest_def_14a_idx].replace('-', '')
                            primary_doc = primary_docs[latest_def_14a_idx]
                            filing_date = filing_dates[latest_def_14a_idx]

                            # Get the filing content
                            filing_url = f"https://www.sec.gov/Archives/{cik}/{accession_number}/{primary_doc}"
                            response = requests.get(filing_url, 
                                headers={'User-Agent': f'altman-zscore-analyzer ({os.getenv("SEC_API_EMAIL")})'})
                            
                            if response.ok:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Find table with executive information
                                exec_keywords = ['executive', 'officer', 'compensation']
                                tables = soup.find_all('table')
                                
                                for table in tables:
                                    if not isinstance(table, Tag):
                                        continue
                                        
                                    # Check if this table has executive info
                                    table_text = table.get_text().lower()
                                    if not any(keyword in table_text for keyword in exec_keywords):
                                        continue
                                    
                                    rows = table.find_all('tr')
                                    if not rows or len(rows) < 2:  # Need at least header + one row
                                        continue

                                    # Check header row
                                    header = rows[0]
                                    if not isinstance(header, Tag):
                                        continue
                                        
                                    header_cells = header.find_all(['th', 'td'])
                                    header_text = ' '.join(cell.get_text().lower() for cell in header_cells if isinstance(cell, Tag))
                                    
                                    # Look for name/title columns
                                    if not ('name' in header_text and any(word in header_text for word in ['title', 'position'])):
                                        continue

                                    # Process data rows
                                    for row in rows[1:]:
                                        if not isinstance(row, Tag):
                                            continue
                                            
                                        cells = row.find_all(['td', 'th'])
                                        if len(cells) >= 2:
                                            name = cells[0].get_text().strip() if isinstance(cells[0], Tag) else ""
                                            title = cells[1].get_text().strip() if isinstance(cells[1], Tag) else ""
                                            
                                            # Try to find compensation in remaining cells
                                            compensation = None
                                            for cell in cells[2:]:
                                                if not isinstance(cell, Tag):
                                                    continue
                                                    
                                                text = cell.get_text().strip()
                                                if any(x in text.lower() for x in ['total', 'compensation', 'salary']):
                                                    try:
                                                        comp_str = ''.join(c for c in text if c.isdigit() or c == '.')
                                                        compensation = float(comp_str) if comp_str else None
                                                        break
                                                    except ValueError:
                                                        pass

                                            if name and title:
                                                officer = {
                                                    'name': name,
                                                    'title': title,
                                                    'totalPay': compensation,
                                                    'filingDate': filing_date,
                                                    'source': 'sec_edgar'
                                                }
                                                sec_officers.append(officer)

        except Exception as e:
            logger.warning(f"Error fetching SEC EDGAR executive data for {ticker}: {e}")

        # 3. Merge both sources
        all_officers = []
        seen_names = set()

        # Add yfinance officers first (they're usually more current)
        for officer in yf_officers:
            name = officer['name']
            if name not in seen_names:
                seen_names.add(name)
                all_officers.append(officer)

        # Add SEC officers if they don't exist in yfinance data
        for officer in sec_officers:
            name = officer['name']
            if name not in seen_names:
                seen_names.add(name)
                all_officers.append(officer)

        if not all_officers:
            logger.warning(f"No executive data found for {ticker} from either source")
            return None

        # Save the combined data
        result = {'officers': all_officers}
        officers_file = os.path.join(output_dir, "company_officers.json")
        with open(officers_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        return result

    except Exception as e:
        logger.error(f"Error fetching executive data for {ticker}: {e}")
        return None
