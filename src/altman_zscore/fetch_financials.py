# fetch_financials.py
import os
import requests
from bs4 import BeautifulSoup, Tag
import time
import logging
from tqdm import tqdm
import json
from typing import Dict, Any, Tuple, Optional, Union, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .config import OUTPUT_DIR
from .cik_mapping import get_cik_mapping

# Configure logging to only show warnings and errors
logging.getLogger().setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

EDGAR_BASE = "https://www.sec.gov"
DATA_EDGAR_BASE = "https://data.sec.gov"
MIN_REQUEST_INTERVAL = 0.1
last_request_time = 0

def make_sec_request(url: str, base_url: str = EDGAR_BASE) -> requests.Response:
    """Make a rate-limited request to SEC EDGAR."""
    global last_request_time
    
    # Get user agent from environment variable
    user_agent = os.getenv('SEC_USER_AGENT')
    if not user_agent:
        raise ValueError("SEC_USER_AGENT environment variable is required")
    
    # Ensure proper time between requests
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - time_since_last_request)
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/html, */*",
        "Host": base_url.replace("https://", ""),
        "Connection": "close"
    }
    
    for attempt in range(3):  # Implement retry logic
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == 2:  # Last attempt
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
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

def parse_xbrl_data(html_content: str) -> Dict[str, float]:
    """Parse XBRL data from the filing HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    def safe_text_to_float(text: Optional[str]) -> Optional[float]:
        """Safely convert text to float, return None if not possible."""
        if not text:
            return None
        try:
            return float(str(text).replace(',', '').strip())
        except (ValueError, TypeError, AttributeError):
            return None
    
    def try_compute_sum(component_names: List[str], log_missing: bool = False) -> Optional[float]:
        """Try to compute sum of values from component tag names."""
        total = 0.0
        valid = False
        
        for name in component_names:
            tag = soup.find('ix:nonfraction', attrs={'name': name})
            if tag and isinstance(tag, Tag):
                if val := safe_text_to_float(tag.text):
                    total += val
                    valid = True
                    
        return total if valid else None
        
    def try_compute_current_assets() -> Optional[float]:
        """Try to compute current assets from common components."""
        # First try standard total current assets tags
        std_totals = [
            'us-gaap:AssetsCurrent',
            'us-gaap:CurrentAssets',
            'us-gaap:AssetsNetCurrent',
            'us-gaap:TotalCurrentAssets'
        ]
        if val := try_compute_sum(std_totals, log_missing=False):
            logging.info("Found total current assets using standard tags")
            return val
            
        logging.debug("Attempting to compute current assets from components...")
            
        # Try standard components
        std_components = [
            'us-gaap:CashAndCashEquivalentsAtCarryingValue',
            'us-gaap:MarketableSecurities',
            'us-gaap:AccountsReceivableNetCurrent',
            'us-gaap:PrepaidExpenseAndOtherAssetsCurrent',
            'us-gaap:InventoryNet',
            'us-gaap:OtherCurrentAssets',
            'us-gaap:ShortTermInvestments'
        ]
        if val := try_compute_sum(std_components):
            logging.info("Computed current assets using standard components")
            return val
            
        # Try fintech/financial institution specific components
        fin_components = [
            'us-gaap:CashAndDueFromBanks',
            'us-gaap:InterestBearingDepositsInOtherInstitutions',
            'us-gaap:LoansReceivableNetCurrent',
            'us-gaap:LoansHeldForSaleNetCurrent',
            'us-gaap:RestrictedCashAndCashEquivalentsCurrent',
            'us-gaap:FederalFundsSoldAndSecuritiesPurchasedUnderAgreementsToResell',
            'us-gaap:FinancingReceivableNetCurrent',
            'us-gaap:LoanAndLeaseLossAllowance',
            'us-gaap:FinanceReceivablesNetCurrent',
            'us-gaap:TradingAccountAssets',
            'us-gaap:MarginLoansReceivable'
        ]
        if val := try_compute_sum(fin_components):
            logging.info("Computed current assets using fintech/financial components")
            return val
            
        # Try fintech/financial services/lending industry specific components
        fintech_components = [
            'us-gaap:LoanAndLeaseFinancingReceivables',
            'us-gaap:FinancingReceivableNetOfAllowanceForCreditLoss',
            'us-gaap:AvailableForSaleSecuritiesDebt',
            'us-gaap:MarketableSecuritiesShortTerm',
            'us-gaap:CashAndCashEquivalents',
            'us-gaap:AccountsAndNotesReceivableNet',
            'us-gaap:OperatingLeaseRightOfUseAssetsCurrent',
            'us-gaap:RestrictedCash',
            'us-gaap:PrepaidExpensesAndOtherCurrentAssets',
            'us-gaap:InvestmentsShortTerm',
            'us-gaap:LoansAndLeasesReceivable',
            'us-gaap:LoansReceivableNet',
            'us-gaap:FinancingReceivableCurrent'
        ]
        if val := try_compute_sum(fintech_components):
            logging.info("Computed current assets using fintech-specific components")
            return val
            
        # Try alternative components
        alt_components = [
            'us-gaap:AccountsAndNotesReceivableNetCurrent',
            'us-gaap:PrepaidRevenue',
            'us-gaap:AvailableForSaleSecurities',
            'us-gaap:DerivativeAssetsCurrent',
            'us-gaap:InvestedAssets',
            'us-gaap:AssetsCurrent1'
        ]
        if val := try_compute_sum(alt_components):
            logging.info("Computed current assets using alternative components")
            return val
            
        logging.warning("Could not compute current assets from any known components")
        return None

    def find_value(concepts: List[str]) -> float:
        """Find a value in the XBRL document matching any of the given concepts."""
        # First try exact matches
        for concept in concepts:
            tag = soup.find('ix:nonfraction', attrs={'name': concept})
            if tag and isinstance(tag, Tag) and (val := safe_text_to_float(tag.text)):
                return val
                    
        # Try special case computations
        if concepts[0].startswith('us-gaap:AssetsCurrent'):
            if val := try_compute_current_assets():
                return val
                    
        # Try case-insensitive partial matches
        base_concepts = [c.replace('us-gaap:', '').lower() for c in concepts]
        for tag in soup.find_all('ix:nonfraction'):
            if not isinstance(tag, Tag):
                continue
            if not tag.has_attr('name'):
                continue
            if not isinstance(tag.get('name'), str):
                continue
            name_attr = str(tag.get('name')).lower()
            if any(bc in name_attr for bc in base_concepts):
                if (val := safe_text_to_float(tag.text)) is not None:
                    logging.info(f"Found partial match: {name_attr}")
                    return val
            
        missing = ', '.join(concepts)
        logging.error(f"Could not find any of these concepts: {missing}")
        raise ValueError(f"Could not find any of {missing} in filing")
    
    # Map of financial concepts to their potential XBRL tags
    concepts_map = {
        "CA": [
            "us-gaap:AssetsCurrent",
            "us-gaap:CurrentAssets",
            "us-gaap:AssetsNetCurrent",
            "us-gaap:TotalCurrentAssets",
            "us-gaap:AssetsCurrent1",
            "us-gaap:CurrentAssetsTotal"
        ],
        "CL": [
            "us-gaap:LiabilitiesCurrent",
            "us-gaap:CurrentLiabilities",
            "us-gaap:LiabilitiesNetCurrent",
            "us-gaap:TotalCurrentLiabilities",
            "us-gaap:LiabilitiesCurrent1"
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
            "us-gaap:AccumulatedRetainedEarnings",
            "us-gaap:RetainedEarningsAccumulatedEarningsDeficit",
            "us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax"
        ],
        "EBIT": [
            "us-gaap:OperatingIncomeLoss",
            "us-gaap:IncomeLossFromOperations",
            "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
            "us-gaap:ProfitLoss",
            "us-gaap:GrossProfit",
            "us-gaap:IncomeLossFromOperatingActivities"
        ],
        "TL": [
            "us-gaap:Liabilities",
            "us-gaap:TotalLiabilities",
            "us-gaap:LiabilitiesTotal",
            "us-gaap:LiabilitiesAndStockholdersEquity"
        ],
        "Sales": [
            "us-gaap:Revenues",
            "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "us-gaap:SalesRevenueNet",
            "us-gaap:RevenueFromContractWithCustomer",
            "us-gaap:OperatingRevenue",
            "us-gaap:TotalRevenues"
        ]
    }
    
    return {key: find_value(concepts) for key, concepts in concepts_map.items()}

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

def parse_financials(url: str) -> Dict[str, float]:
    """Parse financial data from the filing."""
    try:
        response = make_sec_request(url)
        return parse_xbrl_data(response.text)
    except Exception as e:
        raise ValueError(f"Error parsing financials: {str(e)}")

def fetch_batch_financials(tickers: list[str], period_end: str) -> Dict[str, Dict[str, Any]]:
    """
    Fetch financial data for multiple tickers in batch.
    
    Args:
        tickers (list[str]): List of stock tickers to fetch data for
        period_end (str): End date for the period to fetch data for
        
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping tickers to their financial data
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
                continue
                
            cik = cik_map[ticker]
            filing_url = fetch_filing_url(cik, "10-Q", period_end)
            financials = parse_financials(filing_url)
            results[ticker] = {
                "success": True,
                "data": financials,
                "error": None
            }
            success_count += 1
            progress_bar.set_postfix({"success": success_count, "errors": error_count})
            
        except Exception as e:
            logging.warning(f"Failed to fetch financials for {ticker}: {e}")
            results[ticker] = {
                "success": False,
                "data": None,
                "error": str(e)
            }
            error_count += 1
            progress_bar.set_postfix({"success": success_count, "errors": error_count})
            
    progress_bar.close()
    print(f"\nCompleted: {success_count} succeeded, {error_count} failed")
            
    return results
