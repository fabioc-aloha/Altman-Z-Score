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
import logging
from tqdm import tqdm
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from .config import OUTPUT_DIR
from .cik_mapping import get_cik_mapping
from .industry_classifier import CompanyProfile, TechSubsector
from .api.fetcher_factory import create_fetcher
from .data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel

T = TypeVar('T', bound=PageElement)

# Configure logging to only show warnings and errors
logging.getLogger().setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

EDGAR_BASE = "https://www.sec.gov"
DATA_EDGAR_BASE = "https://data.sec.gov"

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
        logging.warning(f"Error finding tag {tag_name}: {str(e)}")
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
        logging.warning(f"Error finding tags {tag_name}: {str(e)}")
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
            logging.warning(f"Could not parse date string: {text}")
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
        "Accept": "application/json, text/html, */*",
        "Host": base_url.replace("https://", ""),
        "Connection": "close"
    }
    
    for attempt in range(API_CONFIG['sec_edgar']['max_retries']):  # Implement retry logic
        try:
            response = requests.get(url, headers=headers, timeout=API_CONFIG['sec_edgar']['timeout'])
            
            # Handle rate limiting explicitly
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', API_CONFIG['sec_edgar']['default_retry_after']))
                logging.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            
            # Validate response headers
            content_type = response.headers.get('Content-Type', '')
            if ('application/json' not in content_type and 
                'text/html' not in content_type):
                raise ValueError(f"Unexpected content type: {content_type}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == API_CONFIG['sec_edgar']['max_retries'] - 1:  # Last attempt
                raise ValueError(f"Failed to fetch data from SEC EDGAR after {API_CONFIG['sec_edgar']['max_retries']} attempts: {str(e)}")
            wait_time = API_CONFIG['sec_edgar']['retry_base'] ** attempt  # Exponential backoff
            logging.warning(f"Request failed, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    last_request_time = time.time()
    return response

def find_latest_10q(filings: dict, before_date: str) -> Optional[dict]:
    """Find the latest 10-Q filing before the given date."""
    target_date = datetime.strptime(before_date, "%Y-%m-%d")
    
    recent = filings.get("filings", {}).get("recent", {})
    if not recent:
        return None
        
    form_types = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    
    latest_10q = None
    latest_date = None
    
    for form, date, acc, doc in zip(form_types, dates, accessions, primary_docs):
        if form == "10-Q":
            filing_date = datetime.strptime(date, "%Y-%m-%d")
            if filing_date <= target_date:
                if not latest_date or filing_date > latest_date:
                    latest_date = filing_date
                    latest_10q = {
                        "accessionNumber": acc,
                        "primaryDocument": doc,
                        "filingDate": date
                    }
    
    return latest_10q

def find_xbrl_tag(soup: BeautifulSoup, concepts: List[str]) -> float:
    """Find and parse XBRL tag value."""
    for concept in concepts:
        # First try exact tag match
        tag = safe_find_tag(soup, 'ix:nonfraction', {'name': concept})
        if tag and (val := safe_text_to_float(safe_get_tag_text(tag))):
            return val
    
    # If we haven't found a valid value, log it and return 0
    logging.warning(f"No valid value found for concepts: {concepts}")
    return 0.0

def find_with_period(soup: BeautifulSoup, concepts: List[str]) -> List[Tuple[datetime, float]]:
    """Find XBRL tags with their period dates and values."""
    dated_values: List[Tuple[datetime, float]] = []
    
    for concept in concepts:
        # Find all tags with matching name
        for tag in safe_find_all_tags(soup, 'ix:nonfraction', {'name': concept}):
            value = safe_text_to_float(safe_get_tag_text(tag))
            if value is None:
                continue
                
            context_ref = tag.get('contextref')
            if not context_ref:
                continue
            
            # Find context element
            context = safe_find_tag(soup, 'xbrli:context', {'id': context_ref})
            if not context:
                continue
            
            # Try to find period end date
            period = safe_find_tag(context, 'xbrli:period')
            if not period:
                continue
            
            # Try both enddate and instant
            date_el = safe_find_tag(period, 'xbrli:enddate') or safe_find_tag(period, 'xbrli:instant')
            date_text = safe_get_tag_text(date_el)
            if date := safe_parse_date(date_text):
                dated_values.append((date, value))
    
    return sorted(dated_values, key=lambda x: x[0], reverse=True)

def parse_financials(url: str, company_profile: Optional[CompanyProfile] = None) -> Dict[str, float]:
    """Parse financial data from the filing."""
    try:
        response = make_sec_request(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get base financial metrics
        metrics = parse_xbrl_data(html_content)
        
        # Use industry-specific fetcher if we have a company profile
        additional_metrics = {}
        if company_profile:
            fetcher = create_fetcher(company_profile)
            additional_metrics = fetcher.get_industry_metrics(soup)
        
        # Combine all metrics
        combined_metrics = {**metrics, **additional_metrics}
        
        # Validate if we have a company profile
        if company_profile:
            fetcher = create_fetcher(company_profile)
            validation_issues = fetcher.validate_data(combined_metrics, company_profile)
            
            # Log validation issues
            for issue in validation_issues:
                level = logging.ERROR if issue.level == ValidationLevel.ERROR else logging.WARNING
                msg = f"{issue.field}: {issue.issue}"
                if issue.value is not None:
                    msg += f" (value: {issue.value})"
                if issue.expected_range:
                    msg += f" (expected: {issue.expected_range})"
                logging.log(level, msg)
            
            # Only raise for ERROR level issues
            error_issues = [i for i in validation_issues if i.level == ValidationLevel.ERROR]
            if error_issues:
                raise ValueError(f"Validation errors found: {', '.join(i.issue for i in error_issues)}")
        
        return combined_metrics
        
    except Exception as e:
        raise ValueError(f"Error parsing financials: {str(e)}")

def parse_xbrl_data(html_content: str) -> Dict[str, float]:
    """Parse XBRL data from the filing."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Core financial metric concepts
    concepts_map = {
        "CA": [
            "us-gaap:AssetsCurrent",
            "us-gaap:CurrentAssets",
            "us-gaap:AssetsNetCurrent",
            "us-gaap:TotalCurrentAssets"
        ],
        "CL": [
            "us-gaap:LiabilitiesCurrent",
            "us-gaap:CurrentLiabilities",
            "us-gaap:LiabilitiesNetCurrent",
            "us-gaap:TotalCurrentLiabilities"
        ],
        "TA": [
            "us-gaap:Assets",
            "us-gaap:TotalAssets",
            "us-gaap:AssetsTotal",
            "us-gaap:AssetsNet"
        ],
        "RE": [
            "us-gaap:RetainedEarnings",
            "us-gaap:RetainedEarningsAccumulatedDeficit",
            "us-gaap:AccumulatedRetainedEarnings"
        ],
        "EBIT": [
            "us-gaap:OperatingIncomeLoss",
            "us-gaap:IncomeLossFromOperations",
            "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
        ],
        "TL": [
            "us-gaap:Liabilities",
            "us-gaap:TotalLiabilities",
            "us-gaap:LiabilitiesTotal"
        ],
        "Sales": [
            "us-gaap:Revenues",
            "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "us-gaap:SalesRevenueNet",
            "us-gaap:RevenueFromContractWithCustomer"
        ]
    }
    
    return {key: find_xbrl_tag(soup, concepts) for key, concepts in concepts_map.items()}

def fetch_filing_url(cik: str, filing_type: str, period_end: str) -> str:
    """Get the latest 10-Q filing URL before the given date."""
    logging.basicConfig(level=logging.DEBUG)
    cik = cik.zfill(10)
    logging.debug(f"Fetching {filing_type} for CIK={cik} before {period_end}")
    
    try:
        # Get company submissions
        submissions_url = f"{DATA_EDGAR_BASE}/submissions/CIK{cik}.json"
        response = make_sec_request(submissions_url, DATA_EDGAR_BASE)
        filings = response.json()
        
        # Find the latest 10-Q
        latest_10q = find_latest_10q(filings, period_end)
        if not latest_10q:
            raise ValueError(f"No {filing_type} found for CIK={cik} before {period_end}")
        
        # Construct filing URL
        acc_no = latest_10q["accessionNumber"].replace("-", "")
        doc = latest_10q["primaryDocument"]
        filing_url = f"{EDGAR_BASE}/Archives/edgar/data/{int(cik)}/{acc_no}/{doc}"
        
        return filing_url
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Company with CIK {cik} not found in EDGAR. The company might be too new, delisted, or the CIK might be incorrect.")
        raise ValueError(f"Error accessing SEC EDGAR: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error fetching filing URL: {str(e)}")

def fetch_batch_financials(
    tickers: list[str], 
    period_end: str, 
    company_profiles: Optional[Dict[str, CompanyProfile]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch financial data for multiple tickers in batch.
    
    Args:
        tickers (list[str]): List of stock tickers to fetch data for
        period_end (str): End date for the period to fetch data for
        company_profiles (Optional[Dict[str, CompanyProfile]]): Pre-classified company profiles 
            to optimize fetching of industry-specific metrics
        
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping tickers to their financial data and validation status
    """
    # Get CIK mappings for all tickers
    cik_map = get_cik_mapping(tickers)
    if not cik_map:
        raise ValueError("No valid CIK numbers found for any tickers")
        
    results = {}
    success_count = 0
    error_count = 0
    
    progress_bar = tqdm(tickers, desc="Fetching financials", ncols=100)
    for ticker in progress_bar:
        try:
            if ticker not in cik_map:
                progress_bar.write(f"Warning: No CIK found for {ticker}, skipping")
                error_count += 1
                results[ticker] = {
                    "success": False,
                    "data": None,
                    "error": "No CIK found",
                    "validation_status": "error"
                }
                continue
                
            cik = cik_map[ticker]
            filing_url = fetch_filing_url(cik, "10-Q", period_end)
            
            # Check if we have a company profile for industry-specific tags
            profile = company_profiles.get(ticker) if company_profiles else None
            
            # Get metrics with validation
            try:
                financials = parse_financials(filing_url, company_profile=profile)
                # If we got here, validation passed
                results[ticker] = {
                    "success": True,
                    "data": financials,
                    "error": None,
                    "validation_status": "valid",
                    "fetch_time": datetime.now().isoformat()
                }
                success_count += 1
                
            except ValueError as ve:
                if "Validation errors found" in str(ve):
                    # Validation error
                    results[ticker] = {
                        "success": False,
                        "data": None,
                        "error": str(ve),
                        "validation_status": "invalid",
                        "fetch_time": datetime.now().isoformat()
                    }
                else:
                    raise  # Re-raise other value errors
                    
            progress_bar.set_postfix({"success": success_count, "errors": error_count})
            
        except Exception as e:
            logging.warning(f"Failed to fetch financials for {ticker}: {e}")
            results[ticker] = {
                "success": False,
                "data": None,
                "error": str(e),
                "validation_status": "error",
                "fetch_time": datetime.now().isoformat()
            }
            error_count += 1
            progress_bar.set_postfix({"success": success_count, "errors": error_count})
            
    progress_bar.close()
    print(f"\nCompleted: {success_count} succeeded, {error_count} failed")
            
    return results



def fetch_financials(cik: str, filing_type: str, period_end: str) -> Dict[str, Any]:
    """
    Fetch financial data for a company from SEC EDGAR.
    
    Args:
        cik (str): Company CIK number
        filing_type (str): Type of filing to fetch (e.g., '10-Q')
        period_end (str): End date for the period to fetch data for
        
    Returns:
        Dict[str, Any]: Dictionary containing financial data
    """
    try:
        # Find the filing URL from submissions
        submissions_url = f"{DATA_EDGAR_BASE}/submissions/CIK{cik.zfill(10)}.json"
        response = make_sec_request(submissions_url, DATA_EDGAR_BASE)
        filings = response.json()
        
        # Find the latest 10-Q
        latest_10q = find_latest_10q(filings, period_end)
        if not latest_10q:
            raise ValueError(f"No {filing_type} found for CIK={cik} before {period_end}")
        
        # Construct filing URL
        acc_no = latest_10q["accessionNumber"].replace("-", "")
        doc = latest_10q["primaryDocument"]
        filing_url = f"{EDGAR_BASE}/Archives/edgar/data/{int(cik)}/{acc_no}/{doc}"
        
        # Parse financials from the filing
        financial_data = parse_financials(filing_url)
        
        # Add metadata
        result = {
            'data': financial_data,
            'meta': {
                'filing_url': filing_url,
                'cik': cik,
                'filing_type': filing_type,
                'period_end': period_end,
                'fetch_time': datetime.now().isoformat()
            }
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error fetching financials for CIK {cik}: {str(e)}")
        raise

def get_tech_rd_expenses(html_content: str) -> Optional[float]:
    """Parse R&D expenses specifically for tech companies."""
    soup = BeautifulSoup(html_content, 'html.parser')
    concepts = [
        'us-gaap:ResearchAndDevelopmentExpense',
        'us-gaap:TechnologyAndDevelopmentExpense',
        'us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost'
    ]
    
    for concept in concepts:
        tag = safe_find_tag(soup, 'ix:nonfraction', {'name': concept})
        if tag and (val := safe_text_to_float(safe_get_tag_text(tag))):
            return val
    return None

def get_tech_revenue_growth(html_content: str) -> Optional[float]:
    """Calculate revenue growth for tech companies."""
    soup = BeautifulSoup(html_content, 'html.parser')
    concepts = [
        'us-gaap:RevenuesFromContractWithCustomerExcludingAssessedTax',
        'us-gaap:RevenuesNetOfInterestExpense',
        'us-gaap:Revenues'
    ]
    
    # Get revenue values across periods
    dated_values = find_with_period(soup, concepts)
    
    # Calculate growth if we have at least two periods
    if len(dated_values) >= 2:
        sorted_values = sorted(dated_values, key=lambda x: x[0], reverse=True)
        current_revenue = sorted_values[0][1]
        prior_revenue = sorted_values[1][1]
        if prior_revenue > 0:
            return (current_revenue - prior_revenue) / prior_revenue
            
    return None

def get_tech_subscription_revenue(html_content: str) -> Optional[float]:
    """Parse subscription revenue for SaaS companies."""
    soup = BeautifulSoup(html_content, 'html.parser')
    concepts = [
        'us-gaap:SubscriptionRevenue',
        'us-gaap:CloudServicesRevenue',
        'us-gaap:RecurringRevenue',
        'us-gaap:SubscriptionAndTransactionBasedRevenue'
    ]
    
    for concept in concepts:
        tag = safe_find_tag(soup, 'ix:nonfraction', {'name': concept})
        if tag and (val := safe_text_to_float(safe_get_tag_text(tag))):
            return val
    return None

def get_manufacturing_turnover(html_content: str) -> Optional[float]:
    """Calculate inventory turnover for manufacturing companies."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    cogs_concepts = [
        'us-gaap:CostOfGoodsAndServicesSold',
        'us-gaap:CostOfRevenue',
        'us-gaap:CostOfGoodsSold'
    ]
    inventory_concepts = [
        'us-gaap:InventoryNet',
        'us-gaap:Inventories',
        'us-gaap:InventoryGross'
    ]
    
    cogs = find_xbrl_tag(soup, cogs_concepts)
    inventory = find_xbrl_tag(soup, inventory_concepts)
    
    if cogs and inventory and inventory > 0:
        return cogs / inventory
    return None

def get_manufacturing_capex(html_content: str) -> Optional[float]:
    """Parse capital expenditure for manufacturing companies."""
    soup = BeautifulSoup(html_content, 'html.parser')
    concepts = [
        'us-gaap:PaymentsToAcquirePropertyPlantAndEquipment',
        'us-gaap:CapitalExpendituresIncurredButNotYetPaid',
        'us-gaap:PaymentsToAcquireProductiveAssets'
    ]
    
    for concept in concepts:
        tag = safe_find_tag(soup, 'ix:nonfraction', {'name': concept})
        if tag and (val := safe_text_to_float(safe_get_tag_text(tag))):
            return abs(val)  # CapEx is usually reported as negative in cash flow
    return None



class SECRequestError(Exception):
    """Base exception for SEC EDGAR request errors."""
    pass

class SECRateLimitError(SECRequestError):
    """Exception raised when hitting SEC EDGAR rate limits."""
    pass

class SECParseError(SECRequestError):
    """Exception raised when failing to parse SEC EDGAR data."""
    pass
