# fetch_financials.py
"""
Data fetching module for the Altman Z-Score analysis pipeline.

This module is responsible for retrieving financial data from SEC EDGAR, NOT for
running the analysis directly. It provides:

- Financial data fetching from SEC EDGAR
- Industry-specific data parsing
- XBRL data extraction
- Rate limiting compliance
- Validation of financial metrics

Use analyze.py in the root directory to run the full analysis pipeline.
"""

import os
import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from typing import Optional, Union, List, Tuple, Dict, Any, TypeVar, cast
import time
import logging # Keep standard logging import
from tqdm import tqdm
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin 
from .config import OUTPUT_DIR # Assuming LOG_LEVEL from config is handled by main.py's setup
from .cik_mapping import get_cik_mapping
from .industry_classifier import CompanyProfile, TechSubsector
from .api.fetcher_factory import create_fetcher
from .data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel

T = TypeVar('T', bound=PageElement)

# Get a logger for this module
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

EDGAR_BASE = "https://www.sec.gov"
DATA_EDGAR_BASE = "https://data.sec.gov"

# Helper function to construct absolute URLs robustly
def _make_absolute_url(base_for_relative: str, path_or_url: str) -> str:
    """
    Constructs an absolute URL.
    - If path_or_url is already absolute (starts with http/https), it's returned.
    - If path_or_url is an absolute path (starts with '/'), it's joined with the scheme and netloc of EDGAR_BASE.
    - If path_or_url is relative, it's joined with base_for_relative.
    """
    if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
        return path_or_url
    
    if path_or_url.startswith('/'):
        # It's an absolute path from the server root, use EDGAR_BASE as the true base
        return urljoin(EDGAR_BASE, path_or_url)
    
    # It's a relative path, use the provided base_for_relative
    return urljoin(base_for_relative, path_or_url)

# Helper functions for BeautifulSoup operations
def safe_text_to_float(text: Optional[str]) -> Optional[float]:
    """Safely convert text to float, handling common formatting."""
    if not text:
        return None
    try:
        # Remove commas and whitespace
        cleaned = str(text).replace(',', '').strip()
        # Handle parentheses for negative numbers
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = f"-{cleaned[1:-1]}"
        return float(cleaned)
    except (ValueError, TypeError, AttributeError):
        return None

def safe_get_tag_text(element: Optional[Union[Tag, str]]) -> Optional[str]:
    """Safely get text from a BeautifulSoup tag."""
    if element is None:
        return None
    if isinstance(element, str):
        return element
    return element.text.strip() if hasattr(element, 'text') else None

def safe_find_tag(element: Union[BeautifulSoup, Tag], tag_name: str, 
                 attrs: Optional[Dict[str, Any]] = None) -> Optional[Tag]:
    """Safely find a tag in BeautifulSoup element."""
    if not element:
        return None
    try:
        result = element.find(tag_name, attrs or {})
        return cast(Optional[Tag], result)
    except Exception as e:
        logger.warning(f"Error finding tag {tag_name}: {str(e)}")
        return None

def safe_find_all_tags(element: Union[BeautifulSoup, Tag], tag_name: str, 
                      attrs: Optional[Dict[str, Any]] = None) -> List[Tag]:
    """Safely find all matching tags in BeautifulSoup element."""
    if not element:
        return []
    try:
        results = element.find_all(tag_name, attrs or {})
        return cast(List[Tag], results)
    except Exception as e:
        logger.warning(f"Error finding tags {tag_name}: {str(e)}")
        return []

def safe_parse_date(text: Optional[str]) -> Optional[datetime]:
    """Safely parse a date string into datetime object."""
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(text, "%Y%m%d")
        except ValueError:
            logger.warning(f"Could not parse date string: {text}")
            return None

# API Configuration
API_CONFIG = {
    'sec_edgar': {
        'request_interval': 0.1,  # 100ms between requests
        'max_retries': 3,
        'retry_base': 2,  # For exponential backoff
        'default_retry_after': 10,
        'batch_size': 5,
        'timeout': 10
    },
    'yahoo_finance': {
        'request_interval': 2.0,  # 2000ms between requests
        'max_retries': 3,
        'retry_base': 2,
        'default_retry_after': 30,
        'timeout': 20
    }
}

last_request_time = 0

def make_sec_request(url: str, base_url: str = EDGAR_BASE) -> requests.Response:
    """Make a rate-limited request to SEC EDGAR."""
    global last_request_time
    
    # Get user agent from environment variable
    user_agent = os.getenv('SEC_USER_AGENT') or os.getenv('SEC_EDGAR_USER_AGENT')
    if not user_agent:
        raise ValueError("Neither SEC_USER_AGENT nor SEC_EDGAR_USER_AGENT environment variable is set")
    
    # Ensure proper time between requests
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < API_CONFIG['sec_edgar']['request_interval']:
        time.sleep(API_CONFIG['sec_edgar']['request_interval'] - time_since_last_request)
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/html, application/xml, text/xml, */*", # Added XML types
        "Host": base_url.replace("https://", ""),
        "Connection": "close"
    }
    
    for attempt in range(API_CONFIG['sec_edgar']['max_retries']):  # Implement retry logic
        try:
            response = requests.get(url, headers=headers, timeout=API_CONFIG['sec_edgar']['timeout'])
            
            # Handle rate limiting explicitly
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', API_CONFIG['sec_edgar']['default_retry_after']))
                logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            
            # Validate response headers
            content_type = response.headers.get('Content-Type', '').lower() # Convert to lower for case-insensitive check
            # Allow JSON, HTML, and XML content types
            if not any(ct in content_type for ct in ['application/json', 'text/html', 'application/xml', 'text/xml']):
                # Check if the URL itself ends with .xml, which implies we expect XML
                # This is a fallback if the Content-Type header is not explicit enough but the URL indicates XML
                if url.lower().endswith('.xml') and 'xml' in content_type:
                    pass # It's an XML file, and content_type confirms it (even if not strictly application/xml or text/xml)
                else:
                    raise ValueError(f"Unexpected content type: {content_type} for URL: {url}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == API_CONFIG['sec_edgar']['max_retries'] - 1:  # Last attempt
                raise ValueError(f"Failed to fetch data from SEC EDGAR after {API_CONFIG['sec_edgar']['max_retries']} attempts: {str(e)}")
            wait_time = API_CONFIG['sec_edgar']['retry_base'] ** attempt  # Exponential backoff
            logger.warning(f"Request failed, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    last_request_time = time.time()
    return response

def find_latest_filing(filings: dict, before_date: str, filing_types_to_check: List[str]) -> Optional[dict]:
    """Find the latest specified filing type before the given date."""
    target_date = datetime.strptime(before_date, "%Y-%m-%d")
    
    recent = filings.get("filings", {}).get("recent", {})
    if not recent:
        return None
        
    form_types_from_data = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    
    latest_filing_found = None
    latest_date_found = None
    
    for form, date_str, acc_num, doc_name in zip(form_types_from_data, dates, accessions, primary_docs):
        if form in filing_types_to_check: # Check against the list of allowed filing types
            filing_date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if filing_date_obj <= target_date:
                if not latest_date_found or filing_date_obj > latest_date_found:
                    latest_date_found = filing_date_obj
                    latest_filing_found = {
                        "accessionNumber": acc_num,
                        "primaryDocument": doc_name,
                        "filingDate": date_str,
                        "formType": form # Store the type of form found
                    }
    
    return latest_filing_found

def find_latest_10q(filings: dict, before_date: str) -> Optional[dict]:
    """Find the latest 10-Q or equivalent (e.g., 20-F, 6-K, 10-K) filing before the given date."""
    # Preference order can be implicitly handled if data is sorted, or explicitly if needed.
    # For now, any of these recent ones will be fine.
    # Common forms: 10-Q (quarterly), 10-K (annual), 20-F (foreign annual), 6-K (foreign interim)
    # 8-K is for current reports, might sometimes have financials but less consistently structured for this purpose.
    # We prioritize quarterly/interim (10-Q, 6-K) then annual (10-K, 20-F) if quarterly is not found,
    # but find_latest_filing currently just finds the most recent of any of these.
    # This might need refinement if a specific order of preference is critical beyond recency.
    return find_latest_filing(filings, before_date, ["10-Q", "6-K", "20-F", "10-K"])

def find_xbrl_tag(soup: BeautifulSoup, concepts: List[str]) -> Optional[float]:
    """Find and parse XBRL tag value, handling multiple periods and contexts."""
    values = []
    logger.debug(f"Searching for concepts: {concepts}")
    
    for concept in concepts:
        base_name = concept.split(':')[-1]
        concept_variations = list(set([
            concept, base_name, f"us-gaap:{base_name}", f"ifrs-full:{base_name}",
            f"ifrs:{base_name}", f"dei:{base_name}"
        ]))
        logger.debug(f"Variations for {concept}: {concept_variations}")

        for current_concept_variation in concept_variations:
            for tag_name in ['ix:nonfraction', 'ix:nonFraction', 'xbrli:nonfraction', 'xbrli:nonFraction', 'nonfraction', 'nonFraction']:
                for tag in safe_find_all_tags(soup, tag_name, {'name': current_concept_variation}):
                    if not tag: continue
                    context_ref = tag.get('contextref')
                    if not context_ref: 
                        logger.debug(f"Tag {current_concept_variation} found but no contextref. Tag: {tag.prettify()}")
                        continue
                    logger.debug(f"Found tag for {current_concept_variation} with contextref: {context_ref}")

                    context = None
                    for ctx_tag_name in ['xbrli:context', 'context']:
                        context = safe_find_tag(soup, ctx_tag_name, {'id': context_ref})
                        if context: break
                    if not context: 
                        logger.debug(f"Context {context_ref} not found for {current_concept_variation}.")
                        continue

                    period = None
                    for p_tag_name in ['xbrli:period', 'period']:
                        period = safe_find_tag(context, p_tag_name)
                        if period: break
                    if not period: 
                        logger.debug(f"Period not found in context {context_ref} for {current_concept_variation}.")
                        continue

                    end_date_el = None
                    for d_tag_name in ['xbrli:instant', 'instant', 'xbrli:enddate', 'enddate']:
                        end_date_el = safe_find_tag(period, d_tag_name)
                        if end_date_el: break
                    if not end_date_el or not safe_get_tag_text(end_date_el): 
                        logger.debug(f"End date not found or empty in period for context {context_ref} of {current_concept_variation}.")
                        continue
                    
                    logger.debug(f"Context {context_ref} for {current_concept_variation} has end date: {safe_get_tag_text(end_date_el)}")

                    scenario = None
                    for s_tag_name in ['xbrli:scenario', 'scenario']:
                        scenario = safe_find_tag(context, s_tag_name)
                        if scenario: break
                    
                    if scenario:
                        logger.debug(f"Context {context_ref} for {current_concept_variation} has scenario: {scenario.prettify()[:100]}")
                        pass 

                    text_val = safe_get_tag_text(tag)
                    if text_val:
                        if tag.get('sign') == '-': text_val = f"-{text_val}"
                        if (val := safe_text_to_float(text_val)) is not None:
                            scale = 1
                            if (scale_attr := tag.get('scale')) is not None:
                                try:
                                    if isinstance(scale_attr, (str, int, float)):
                                        scale_int = int(float(scale_attr))
                                        scale = 10 ** scale_int
                                    else:
                                        logger.warning(f"Invalid scale attribute value: {scale_attr} for concept {current_concept_variation}")
                                except (ValueError, TypeError, OverflowError) as e_scale:
                                    logger.warning(f"Error processing scale attribute '{scale_attr}' for {current_concept_variation}: {e_scale}")
                            adjusted_val = val * scale
                            end_date_text = safe_get_tag_text(end_date_el)
                            if end_date_text:
                                logger.debug(f"Adding value for {current_concept_variation}: {adjusted_val} (scaled from {val}, scale {scale_attr}) for date {end_date_text}")
                                values.append((end_date_text.strip(), adjusted_val))
                            else:
                                logger.warning(f"End date element for {current_concept_variation} has no text.")
    if not values: 
        logger.debug(f"No values found for concepts: {concepts}")
        return None
    
    logger.debug(f"Found values before date sorting for {concepts}: {values}")
    valid_date_values = []
    for date_str, value in values:
        dt_obj = None
        for fmt in ("%Y-%m-%d", "%Y%m%d"): # Added %Y%m%d as a common alternative
            try:
                dt_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        if dt_obj:
            valid_date_values.append((dt_obj, value))
        else:
            logger.warning(f"Could not parse date string '{date_str}' for sorting values for {concepts}")
    
    if not valid_date_values: 
        logger.debug(f"No valid date values after parsing for {concepts}")
        return None

    valid_date_values.sort(key=lambda x: x[0], reverse=True)
    logger.debug(f"Sorted values for {concepts}: {valid_date_values}. Returning: {valid_date_values[0][1]}")
    return valid_date_values[0][1]

def _get_xbrl_instance_url(cik_padded: str, acc_no: str, primary_doc_name: str, filing_dir_url: str) -> Optional[str]:
    """
    Determines the URL of the XBRL instance document for a given filing.
    """
    logger.debug(f"Attempting to find XBRL instance for CIK {cik_padded}, acc_no {acc_no}, primary_doc {primary_doc_name}, dir_url {filing_dir_url}")

    try:
        dir_response = make_sec_request(filing_dir_url)
        dir_soup = BeautifulSoup(dir_response.text, 'html.parser')
    except Exception as e:
        logger.warning(f"Failed to fetch or parse directory listing {filing_dir_url}: {e}")
        return None
        
    potential_xbrl_hrefs: List[str] = []
    for link_tag in dir_soup.find_all('a', href=True):
        if not isinstance(link_tag, Tag): continue
        href_attr = link_tag.get('href')
        actual_href = href_attr[0] if isinstance(href_attr, list) else href_attr
        if (isinstance(actual_href, str) and actual_href.endswith('.xml') and
            not any(x.lower() in actual_href.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml'])):
            potential_xbrl_hrefs.append(actual_href) 
    logger.debug(f"Potential XBRL hrefs from directory listing: {potential_xbrl_hrefs}")

    if primary_doc_name.endswith('.xml') and not any(x.lower() in primary_doc_name.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml']):
        logger.debug(f"Primary document {primary_doc_name} is an XML file, considering it as XBRL instance.")
        return _make_absolute_url(filing_dir_url, primary_doc_name)

    if potential_xbrl_hrefs:
        if len(potential_xbrl_hrefs) == 1:
            chosen_href = potential_xbrl_hrefs[0]
            logger.debug(f"Found single potential XBRL file in directory: {chosen_href}")
            return _make_absolute_url(filing_dir_url, chosen_href)
        
        filtered_list = [h for h in potential_xbrl_hrefs if not any(kwd.lower() in h.lower() for kwd in ['schema', 'xsd', 'cal', 'def', 'lab', 'pre', 'filingsummary.xml'])] # Ensure filingsummary is filtered here too
        if not filtered_list:
            logger.debug("Filtering removed all potential XBRL files, reverting to full list for choice (excluding FilingSummary if possible).")
            filtered_list = [h for h in potential_xbrl_hrefs if 'filingsummary.xml' not in h.lower()]
            if not filtered_list: 
                 filtered_list = potential_xbrl_hrefs
        
        preferred_candidates = []
        for h_pref in filtered_list:
            primary_doc_name_base = primary_doc_name.split('.')[0] 
            if acc_no in h_pref or cik_padded in h_pref or primary_doc_name_base in h_pref:
                preferred_candidates.append(h_pref)
        
        if preferred_candidates:
            chosen_href = min(preferred_candidates, key=len)
            logger.debug(f"Multiple potential XBRL files. Preferred heuristic choice: {chosen_href} from list: {preferred_candidates}")
        elif filtered_list: 
            chosen_href = min(filtered_list, key=len) 
            logger.debug(f"Multiple potential XBRL files. Fallback heuristic choice (shortest): {chosen_href} from list: {filtered_list}")
        else: 
            logger.warning(f"XBRL selection logic failed to choose from {potential_xbrl_hrefs} for {cik_padded}, acc {acc_no}")
            return None

        return _make_absolute_url(filing_dir_url, chosen_href)

    if primary_doc_name.endswith(('.htm', '.html')):
        logger.debug(f"Primary document {primary_doc_name} is HTML. Parsing for XBRL link...")
        primary_doc_full_url = _make_absolute_url(filing_dir_url, primary_doc_name)
        try:
            primary_doc_response = make_sec_request(primary_doc_full_url)
            primary_soup = BeautifulSoup(primary_doc_response.text, 'html.parser')
        except Exception as e:
            logger.warning(f"Failed to fetch or parse HTML primary document {primary_doc_full_url}: {e}")
            return None

        for a_tag in primary_soup.find_all('a', href=True):
            if not isinstance(a_tag, Tag): continue
            href_attr = a_tag.get('href')
            actual_href_from_html = href_attr[0] if isinstance(href_attr, list) else href_attr
            if (isinstance(actual_href_from_html, str) and actual_href_from_html.endswith('.xml') and
                not any(x.lower() in actual_href_from_html.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml'])):
                tag_text_element = getattr(a_tag, 'string', None)
                tag_text = str(tag_text_element).strip() if tag_text_element else ""
                
                if "INSTANCE" in tag_text.upper() or "XBRL" in tag_text.upper() or not tag_text: 
                    logger.debug(f"Found XBRL link in HTML primary document: {actual_href_from_html} (Text: \\'{tag_text}\\')")
                    return _make_absolute_url(primary_doc_full_url, actual_href_from_html) # Use primary_doc_full_url as base for relative links from HTML
    
    logger.warning(f"Could not reliably determine XBRL instance URL for {cik_padded}, acc {acc_no} using primary_doc {primary_doc_name} and dir {filing_dir_url}.")
    return None

def parse_financials(soup: BeautifulSoup, profile: CompanyProfile, filing_date_str: str) -> Dict[str, Any]:
    """
    Parses the BeautifulSoup object of an XBRL document to extract financial data.
    """
    concepts_to_find = {
        "current_assets": ["AssetsCurrent"],
        "current_liabilities": ["LiabilitiesCurrent"],
        "retained_earnings": ["RetainedEarningsAccumulatedDeficit", "RetainedEarnings"],
        "ebit": ["OperatingIncomeLoss", "EarningsBeforeInterestAndTaxes", "ProfitLossBeforeTax", "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"],
        "total_assets": ["Assets"],
        "total_liabilities": ["Liabilities"],
        "sales_revenue": ["Revenues", "SalesRevenueNet", "Revenue", "SalesRevenueServicesNet"]
    }

    raw_data: Dict[str, Optional[float]] = {}
    logger.info(f"Starting financial data parsing for filing date {filing_date_str}")
    for key, concept_list in concepts_to_find.items():
        logger.debug(f"Attempting to find XBRL tag for: {key} (concepts: {concept_list})")
        raw_data[key] = find_xbrl_tag(soup, concept_list)
        logger.info(f"Raw data for {key}: {raw_data[key]}")

    key_map = {
        "current_assets": "CA",
        "current_liabilities": "CL",
        "retained_earnings": "RE",
        "ebit": "EBIT",
        "total_assets": "TA",
        "total_liabilities": "TL",
        "sales_revenue": "Sales"
    }
    
    transformed_data: Dict[str, Any] = {key_map[k]: v for k, v in raw_data.items() if k in key_map}
    transformed_data["filing_date_actual"] = filing_date_str 
    logger.info(f"Transformed financial data: {transformed_data}")
    return transformed_data

def fetch_financials(
    tickers: List[str], 
    period_end_date: str, 
    company_profiles: Dict[str, CompanyProfile],
    cik_map: Dict[str, str] 
) -> Dict[str, Dict[str, Any]]:
    """
    Fetches financial data for a list of tickers for a given period.
    """
    results: Dict[str, Dict[str, Any]] = {}
    progress_bar = tqdm(tickers, desc="Fetching financials", unit="ticker", leave=False)

    for ticker in progress_bar:
        progress_bar.set_postfix_str(f"Current: {ticker}")
        cik = cik_map.get(ticker)
        profile = company_profiles.get(ticker)

        if not cik or not profile:
            results[ticker] = {"success": False, "error": f"Missing CIK or profile for {ticker}"}
            logger.warning(f"[{ticker}] Skipping: Missing CIK or profile.")
            continue

        try:
            cik_padded = cik.zfill(10)
            submissions_url = f"{DATA_EDGAR_BASE}/submissions/CIK{cik_padded}.json"
            logger.debug(f"[{ticker}] Fetching submissions from: {submissions_url}")
            response = make_sec_request(submissions_url, DATA_EDGAR_BASE)
            filings_json = response.json()
            
            annual_filing_types = ["10-K", "20-F"]
            latest_filing_doc = find_latest_filing(filings_json, period_end_date, annual_filing_types)
            filing_type_preference = "Annual (10-K/20-F)"

            if not latest_filing_doc:
                logger.info(f"[{ticker}] No {filing_type_preference} found before {period_end_date}. Trying broader search including quarterly/interim.")
                broader_filing_types = ["10-Q", "6-K"] + annual_filing_types
                latest_filing_doc = find_latest_filing(filings_json, period_end_date, broader_filing_types)
                filing_type_preference = "Any (10-K/20-F/10-Q/6-K)"


            if not latest_filing_doc:
                error_msg = f"No suitable filing found for {ticker} (CIK {cik}) before {period_end_date} (preference: {filing_type_preference})"
                results[ticker] = {"success": False, "error": error_msg}
                logger.warning(f"[{ticker}] {error_msg}")
                continue

            acc_no_raw = latest_filing_doc["accessionNumber"]
            acc_no = acc_no_raw.replace("-", "")
            primary_doc_name = latest_filing_doc["primaryDocument"]
            actual_filing_date = latest_filing_doc["filingDate"]
            form_type = latest_filing_doc["formType"]
            
            logger.info(f"[{ticker}] Selected filing: {form_type} ({actual_filing_date}), Acc#: {acc_no_raw}, Primary Doc: {primary_doc_name}")
            
            filing_dir_url = f"{EDGAR_BASE}/Archives/edgar/data/{int(cik_padded)}/{acc_no}/" # int(cik_padded) is correct as CIKs can be < 10 digits before padding
            logger.debug(f"[{ticker}] Filing directory URL: {filing_dir_url}")
            
            xbrl_instance_url = _get_xbrl_instance_url(cik_padded, acc_no, primary_doc_name, filing_dir_url)

            if not xbrl_instance_url:
                error_msg = f"Could not determine XBRL instance URL for {ticker}, filing {acc_no_raw} ({form_type})"
                results[ticker] = {"success": False, "error": error_msg}
                logger.warning(f"[{ticker}] {error_msg}")
                continue
            
            logger.info(f"[{ticker}] Attempting to fetch XBRL from: {xbrl_instance_url}")
            xbrl_response = make_sec_request(xbrl_instance_url) # Base URL will be inferred by make_sec_request if xbrl_instance_url is absolute
            content_type = xbrl_response.headers.get('Content-Type', '').lower()

            if 'xml' not in content_type:
                if 'html' in content_type:
                    logger.debug(f"[{ticker}] URL {xbrl_instance_url} returned HTML. Parsing for XML link...")
                    temp_soup = BeautifulSoup(xbrl_response.text, 'html.parser')
                    found_link_in_html = False
                    for link_tag_html in temp_soup.find_all('a', href=True):
                        if not isinstance(link_tag_html, Tag): continue
                        href_attr_html = link_tag_html.get('href')
                        actual_href_html = href_attr_html[0] if isinstance(href_attr_html, list) else href_attr_html
                        if isinstance(actual_href_html, str) and actual_href_html.endswith('.xml') and not any(x.lower() in actual_href_html.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml']):
                            # Construct full URL for the linked XML
                            linked_xbrl_url = _make_absolute_url(xbrl_instance_url, actual_href_html) # Use xbrl_instance_url as base for relative links
                            
                            logger.debug(f"[{ticker}] Found XML link in HTML page: {linked_xbrl_url}. Fetching...")
                            xbrl_response = make_sec_request(linked_xbrl_url) 
                            new_content_type = xbrl_response.headers.get('Content-Type', '').lower()
                            if 'xml' not in new_content_type:
                                error_msg = f"Linked document {linked_xbrl_url} from HTML page is not XML: {new_content_type}"
                                results[ticker] = {"success": False, "error": error_msg}
                                logger.warning(f"[{ticker}] {error_msg}")
                                break 
                            found_link_in_html = True
                            logger.debug(f"[{ticker}] Successfully fetched XML from linked URL: {linked_xbrl_url}")
                            break 
                    
                    if not found_link_in_html and ('xml' not in xbrl_response.headers.get('Content-Type', '').lower()):
                        error_msg = f"XBRL URL {xbrl_instance_url} returned HTML, and no valid XML link found within."
                        results[ticker] = {"success": False, "error": error_msg}
                        logger.warning(f"[{ticker}] {error_msg}")
                        continue 
                else: 
                    error_msg = f"Unexpected content type for XBRL from {xbrl_instance_url}: {content_type}"
                    results[ticker] = {"success": False, "error": error_msg}
                    logger.warning(f"[{ticker}] {error_msg}")
                    continue 
            
            if 'xml' not in xbrl_response.headers.get('Content-Type', '').lower():
                if not results.get(ticker, {}).get("error"): # Avoid overwriting more specific error
                    error_msg = f"Final check: content from {xbrl_instance_url} (or linked) is not XML. Last content type: {xbrl_response.headers.get('Content-Type', '')}"
                    results[ticker] = {"success": False, "error": error_msg}
                    logger.warning(f"[{ticker}] {error_msg}")
                continue

            logger.debug(f"[{ticker}] Parsing XBRL content from {xbrl_instance_url if 'xml' in content_type else linked_xbrl_url }...")
            xbrl_soup = BeautifulSoup(xbrl_response.text, 'xml') 
            
            financial_data_points = parse_financials(xbrl_soup, profile, actual_filing_date)
            
            required_keys_for_zscore = ["TA", "CL", "CA", "RE", "EBIT", "Sales"] 
            missing_critical_keys = [k_short for k_short in required_keys_for_zscore if financial_data_points.get(k_short) is None]
            
            if missing_critical_keys:
                logger.debug(f"[{ticker}] Data found before missing critical key check: {financial_data_points}")
                error_msg = f"Missing critical financial data (e.g., {', '.join(missing_critical_keys)}) for {ticker} from {form_type} ({actual_filing_date})"
                results[ticker] = {"success": False, "error": error_msg, "data": financial_data_points} 
                logger.warning(f"[{ticker}] {error_msg}")
                continue

            results[ticker] = {"success": True, "data": financial_data_points, "filing_type_used": form_type, "filing_date_used": actual_filing_date}
            logger.info(f"[{ticker}] Successfully fetched and parsed financials from {form_type} ({actual_filing_date})")

        except requests.exceptions.RequestException as e:
            err_str = f"RequestException for {ticker}: {str(e)}"
            results[ticker] = {"success": False, "error": err_str}
            logger.error(f"[{ticker}] {err_str}")
        except json.JSONDecodeError as e: 
            err_str = f"JSONDecodeError for {ticker} (submissions API): {str(e)}. Response text: {response.text[:200] if 'response' in locals() else 'N/A'}"
            results[ticker] = {"success": False, "error": err_str}
            logger.error(f"[{ticker}] {err_str}")
        except ValueError as e: 
            err_str = f"ValueError for {ticker}: {str(e)}"
            results[ticker] = {"success": False, "error": err_str}
            logger.error(f"[{ticker}] {err_str}")
        except Exception as e:
            import traceback
            err_str_tb = traceback.format_exc()
            user_err_str = f"Unexpected error for {ticker}: {str(e)}"
            results[ticker] = {"success": False, "error": user_err_str}
            logger.error(f"[{ticker}] {user_err_str}\\nTraceback:\\n{err_str_tb}")
            
    progress_bar.close()
    return results

def debug_fetch_xbrl_snippet(cik: str, filing_type: str = "20-F", period_end_date: str = "2025-03-31", lines: int = 200) -> None:
    """
    Fetches the latest specified filing for a CIK, downloads its XBRL instance document,
    and prints the first N lines of its content for debugging purposes.
    """
    if not os.getenv('SEC_USER_AGENT') and not os.getenv('SEC_EDGAR_USER_AGENT'):
        print("ERROR: SEC_USER_AGENT or SEC_EDGAR_USER_AGENT environment variable is not set.")
        return

    print(f"--- Debugging XBRL for CIK: {cik}, Filing Type: {filing_type}, Before: {period_end_date} ---")
    logger.info(f"--- Debugging XBRL for CIK: {cik}, Filing Type: {filing_type}, Before: {period_end_date} ---")
    try:
        cik_padded = cik.zfill(10)
        submissions_url = f"{DATA_EDGAR_BASE}/submissions/CIK{cik_padded}.json"
        logger.info(f"Fetching submissions from: {submissions_url}")
        response = make_sec_request(submissions_url, DATA_EDGAR_BASE)
        filings_json = response.json()

        latest_filing_doc = find_latest_filing(filings_json, period_end_date, [filing_type])

        if not latest_filing_doc:
            logger.warning(f"No {filing_type} found for CIK {cik_padded} before {period_end_date}.")
            # Attempt with broader types if specific one not found
            logger.info(f"Attempting broader search for CIK {cik_padded}...")
            latest_filing_doc = find_latest_filing(filings_json, period_end_date, ["10-K", "20-F", "10-Q", "6-K"])
            if not latest_filing_doc:
                logger.error(f"No suitable filing found even with broader search for CIK {cik_padded} before {period_end_date}.")
                print(f"No suitable filing found for CIK {cik_padded} before {period_end_date} even with broader search.")
                return
            else:
                logger.info(f"Found alternative filing: {latest_filing_doc.get('formType')} for CIK {cik_padded}")
                print(f"Found alternative filing: {latest_filing_doc.get('formType')} for CIK {cik_padded}")


        acc_no_raw = latest_filing_doc["accessionNumber"]
        acc_no = acc_no_raw.replace("-", "")
        primary_doc_name = latest_filing_doc["primaryDocument"]
        form_type_found = latest_filing_doc["formType"] # Get the actual form type found
        
        logger.info(f"Selected filing: {form_type_found} ({latest_filing_doc['filingDate']}), Acc#: {acc_no_raw}, Primary Doc: {primary_doc_name}")
        print(f"Selected filing: {form_type_found} ({latest_filing_doc['filingDate']}), Acc#: {acc_no_raw}, Primary Doc: {primary_doc_name}")

        filing_dir_url = f"{EDGAR_BASE}/Archives/edgar/data/{int(cik_padded)}/{acc_no}/"
        
        # Use the robust _get_xbrl_instance_url function
        xbrl_instance_url = _get_xbrl_instance_url(cik_padded, acc_no, primary_doc_name, filing_dir_url)

        if not xbrl_instance_url:
            logger.error(f"Could not determine XBRL instance document URL for {acc_no_raw} using _get_xbrl_instance_url.")
            print(f"Could not determine XBRL instance document URL for {acc_no_raw} using _get_xbrl_instance_url.")
            return

        logger.info(f"Fetching XBRL instance document from: {xbrl_instance_url}")
        print(f"Fetching XBRL instance document from: {xbrl_instance_url}")
        xbrl_response = make_sec_request(xbrl_instance_url)
        
        content_type = xbrl_response.headers.get('Content-Type', '').lower()
        final_xbrl_text = xbrl_response.text

        if 'xml' not in content_type:
            if 'html' in content_type:
                logger.info("Received HTML, attempting to find XML link within...")
                print("Received HTML, attempting to find XML link within...")
                temp_soup = BeautifulSoup(xbrl_response.text, 'html.parser')
                found_link_in_html = False
                for link_tag in temp_soup.find_all('a', href=True):
                    if not isinstance(link_tag, Tag): continue
                    href_attr = link_tag.get('href')
                    actual_href = href_attr[0] if isinstance(href_attr, list) else href_attr

                    if isinstance(actual_href, str) and actual_href.endswith('.xml') and not any(x.lower() in actual_href.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml']):
                        linked_xbrl_url = _make_absolute_url(xbrl_instance_url, actual_href)
                        
                        logger.info(f"Found XML link in HTML page: {linked_xbrl_url}")
                        print(f"Found XML link in HTML page: {linked_xbrl_url}")
                        xbrl_response_linked = make_sec_request(linked_xbrl_url)
                        new_content_type = xbrl_response_linked.headers.get('Content-Type', '').lower()
                        if 'xml' not in new_content_type:
                            logger.error(f"Linked document {linked_xbrl_url} is also not XML: {new_content_type}. Aborting.")
                            print(f"Linked document {linked_xbrl_url} is also not XML: {new_content_type}. Aborting.")
                            return
                        final_xbrl_text = xbrl_response_linked.text
                        found_link_in_html = True
                        break
                if not found_link_in_html:
                    logger.error("No XML link found within the HTML page. Aborting.")
                    print("No XML link found within the HTML page. Aborting.")
                    return
            else: 
                logger.error(f"Unexpected content type for XBRL document: {content_type}. Aborting.")
                print(f"Unexpected content type for XBRL document: {content_type}. Aborting.")
                return

        print(f"--- Start of XBRL data (first {lines} lines) from {xbrl_instance_url if 'xml' in content_type else linked_xbrl_url} ---")
        for i, line_content in enumerate(final_xbrl_text.splitlines()):
            if i < lines:
                print(line_content)
            else:
                break
        print(f"--- End of XBRL data snippet ---")
        
        # Also try parsing with BeautifulSoup and finding a known tag
        print(f"--- Attempting to parse with BeautifulSoup and find 'Assets' concept ---")
        try:
            xbrl_soup_debug = BeautifulSoup(final_xbrl_text, 'xml')
            assets_value = find_xbrl_tag(xbrl_soup_debug, ["Assets"])
            if assets_value is not None:
                print(f"Successfully parsed 'Assets': {assets_value}")
            else:
                print("'Assets' concept not found or value is None.")
            
            # You can add more concepts here for debugging
            # sales_value = find_xbrl_tag(xbrl_soup_debug, ["Revenues", "SalesRevenueNet"])
            # print(f"'Sales/Revenues' concept value: {sales_value}")

        except Exception as e_parse:
            print(f"Error parsing XBRL with BeautifulSoup or finding concept: {e_parse}")


    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e.response.status_code} for URL: {e.request.url}", exc_info=True)
        print(f"HTTP Error: {e.response.status_code} for URL: {e.request.url}")
        print(f"Response content: {e.response.text[:500]}") 
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {str(e)}", exc_info=True)
        print(f"Request Exception: {str(e)}")
    except json.JSONDecodeError as e: 
        logger.error(f"JSON Decode Error: {str(e)}. Content: {response.text[:500] if 'response' in locals() else 'N/A'}", exc_info=True)
        print(f"JSON Decode Error: {str(e)}. Content: {response.text[:500] if 'response' in locals() else 'N/A'}")
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}", exc_info=True)
        print(f"ValueError: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        import traceback
        print(f"An unexpected error occurred: {str(e)}\\n{traceback.format_exc()}")