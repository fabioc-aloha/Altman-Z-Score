"""
SEC EDGAR API client module for handling all SEC data fetching operations.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

import requests

from .rate_limiter import RateLimitExceeded, RateLimitStrategy, TokenBucket
from ..company.cik_lookup import COMMON_CIK_MAPPINGS
from ..utils.paths import get_output_dir
from ..utils.error_helpers import AltmanZScoreError
from ..utils.retry import exponential_retry

# Network exceptions to retry on
NETWORK_EXCEPTIONS = (
    requests.exceptions.RequestException,  # All requests exceptions
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)

logger = logging.getLogger(__name__)


class SECError(AltmanZScoreError):
    """Base exception for SEC API errors."""


class SECRateError(SECError):
    """Exception for rate limit errors."""


class SECResponseError(SECError):
    """Exception for response validation errors."""


class SECClient:
    """
    Client for interacting with SEC EDGAR API.
    """
    # Base URLs (will be used as prefixes)
    BASE_URL = "https://data.sec.gov"  # No trailing slash needed 
    BROWSE_EDGAR_URL = "https://www.sec.gov/cgi-bin/browse-edgar"  # Complete URL
    SUBMISSIONS_BASE_URL = "https://data.sec.gov/submissions"  # No trailing slash - add / when using!
    ARCHIVES_BASE_URL = "https://www.sec.gov/Archives"  # No trailing slash - add / when using!
    
    # Endpoint paths (to be appended to BASE_URL)
    COMPANY_SEARCH = "/submissions/CIK{}.json"  # With leading slash for proper URL construction
    COMPANY_FACTS = "/api/xbrl/companyfacts/CIK{}.json"  # With leading slash
    COMPANY_CONCEPT = "/api/xbrl/companyconcept/CIK{}/us-gaap/{}.json"  # With leading slash
    
    # Complete URLs
    COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"  # Complete URL

    # SEC EDGAR requires 100ms between requests (10 requests per second)
    REQUEST_RATE = 10  # requests per second
    MIN_REQUEST_INTERVAL = 0.1  # seconds

    def __init__(self, email: Optional[str] = None):
        """Initialize client with proper authentication headers."""
        # Prefer SEC_EDGAR_USER_AGENT for User-Agent header, fallback to SEC_API_EMAIL for legacy support
        self.user_agent = os.getenv("SEC_EDGAR_USER_AGENT")
        self.email = email or os.getenv("SEC_API_EMAIL")
        
        if not self.user_agent and not self.email:
            raise ValueError(
                "SEC EDGAR User-Agent is required. Set SEC_EDGAR_USER_AGENT or SEC_API_EMAIL in your environment."
            )
            
        # Initialize rate limiter and session
        self.rate_limiter = TokenBucket(
            rate=self.REQUEST_RATE,
            capacity=self.REQUEST_RATE * 2,
            strategy=RateLimitStrategy.WAIT
        )
        self.session = self._create_session()
        self._last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create and configure requests session with proper headers."""
        session = requests.Session()
        
        # Set required headers for SEC EDGAR
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"        }
        
        if self.user_agent:
            # Use the full User-Agent string from environment
            headers["User-Agent"] = self.user_agent
        else:
            # Fallback to legacy format with email
            headers["User-Agent"] = f"AltmanZScore/3.2.0 {self.email}"
        
        session.headers.update(headers)
        return session
        
    def _ensure_rate_limit(self):
        """Ensure we respect SEC EDGAR rate limits."""
        try:
            self.rate_limiter.acquire(tokens=1.0)
        except RateLimitExceeded:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.MIN_REQUEST_INTERVAL:
                sleep_time = self.MIN_REQUEST_INTERVAL - time_since_last
                logger.debug(f"Rate limit hit, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self._last_request_time = time.time()

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        timeout: float = 10.0,
        **kwargs
    ) -> requests.Response:
        """Make an authenticated request to SEC EDGAR API."""
        # Ensure we're respecting rate limits
        self._ensure_rate_limit()
        # Build the full URL - ensure we have proper URL structure
        if endpoint.startswith("http"):
            url = endpoint
        else:
            # Properly join URL parts to avoid issues with slashes
            endpoint = endpoint.lstrip('/')  # Remove leading slash if present
            url = f"{self.BASE_URL}/{endpoint}"
        logger.debug(f"Making SEC API request to URL: {url}")
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            logger.debug(
                f"SEC API Request: {method} {url} "
                f"Headers: {self.session.headers}"
            )            # Raise for 4XX/5XX status codes, but suppress 404 for companyfacts
            if "/companyfacts/" in url and response.status_code == 404:
                logger.info(f"SEC companyfacts not found (404) for {url}; will attempt fallback.")
                # Return a dummy response with empty facts
                class DummyResponse:
                    def json(self_inner):
                        return {"facts": {}}
                return DummyResponse()
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.info(
                    f"SEC API rate limit or authentication issue (401). "
                    f"Falling back to other data sources. "
                    f"URL: {url}"
                )
                # For 401 errors, return None instead of raising to allow fallback
                return None
            raise

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def lookup_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK number for a ticker symbol.

        Args:
            ticker: Stock ticker symbol

        Returns:
            10-digit CIK if found, None otherwise
        """
        try:
            # First check if it's in the common mappings (imported from company_profile)
            upper_ticker = ticker.upper()
            if upper_ticker in COMMON_CIK_MAPPINGS:
                cik = COMMON_CIK_MAPPINGS[upper_ticker]
                logger.debug(f"Found CIK {cik} for ticker {ticker} in common mappings")
                return cik

            # Try the company_tickers.json file endpoint (most reliable)
            logger.debug(f"Looking up CIK for {ticker} via company_tickers.json...")
            resp = self.session.get(self.COMPANY_TICKERS_URL)
            resp.raise_for_status()
            tickers_data = resp.json()
            
            # The company_tickers.json file has numeric indices as keys
            for _, entry in tickers_data.items():
                if entry.get('ticker').upper() == ticker.upper():
                    cik = str(entry.get('cik_str'))
                    logger.debug(f"Found CIK {cik} for ticker {ticker} via company_tickers.json")
                    return cik.zfill(10)
                    
            # Fallback to the browse-edgar endpoint if needed
            logger.debug(f"No match found in company_tickers.json for {ticker}, trying browse-edgar...")
            search_params = {
                "CIK": ticker,
                "Find": "Search",
                "owner": "exclude",
                "action": "getcompany",
            }
            response = self.session.get(self.BROWSE_EDGAR_URL, params=search_params)
            response.raise_for_status()
            content = response.text

            # Try to match CIK from HTML response using different patterns
            cik_patterns = [
                ("CIK=", [" ", "/"]),  # Common on browse-edgar pages
                ("CIK=", ["&"]),  # For URLs
                (">CIK", [" ", "<"]),  # For HTML content
            ]

            for prefix, terminators in cik_patterns:
                cik_start = content.find(prefix)
                if cik_start != -1:
                    cik_start += len(prefix)
                    cik_end = -1
                    for term in terminators:
                        pos = content.find(term, cik_start)
                        if pos != -1 and (cik_end == -1 or pos < cik_end):
                            cik_end = pos

                    if cik_end > cik_start:
                        found_cik = content[cik_start:cik_end].strip()
                        if found_cik.isdigit():
                            return found_cik.zfill(10)

            logger.warning(f"No CIK found for ticker {ticker}")
            return None

        except Exception as e:
            logger.error(f"Error looking up CIK for {ticker}: {str(e)}")
            return None

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def get_company_info(self, ticker_or_cik: str, save_to_file: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get company info from SEC EDGAR. Optionally save to output/{TICKER}/company_info.json.

        Args:
            ticker_or_cik: Stock ticker symbol or CIK number
            save_to_file: If True, save the result to output/{TICKER}/company_info.json

        Returns:
            Company info including CIK if found, None otherwise
        """
        try:
            # Get/validate CIK
            if ticker_or_cik.isdigit():
                cik = ticker_or_cik.zfill(10) 
            else:
                # Lookup from common mappings first
                from altman_zscore.company.cik_lookup import COMMON_CIK_MAPPINGS
                upper_ticker = ticker_or_cik.upper()
                if upper_ticker in COMMON_CIK_MAPPINGS:
                    cik = COMMON_CIK_MAPPINGS[upper_ticker]
                    logger.debug(f"Found CIK {cik} for ticker {ticker_or_cik} in common mappings")
                else:
                    cik = self.lookup_cik(ticker_or_cik)
            
            if not cik:
                logger.error(f"Could not find CIK for {ticker_or_cik}")
                return None

            ticker = ticker_or_cik if not ticker_or_cik.isdigit() else None
            padded_cik = cik.zfill(10)
            
            # Get company details using CIK - ensure properly joined URL
            url = f"{self.BASE_URL}{self.COMPANY_SEARCH.format(padded_cik)}"
            logger.debug(f"Requesting company info from: {url}")
            
            response = self.session.get(url)
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get company info for {ticker_or_cik} (CIK: {padded_cik})")
                logger.error(f"Response status code: {response.status_code}")
                logger.error(f"Response text: {response.text[:1000]}")
                return None

            try:
                company_info = response.json()
                logger.debug(f"SEC API Response structure: {list(company_info.keys())}")
            except ValueError as e:
                logger.error(f"Failed to parse JSON response for {ticker_or_cik}: {str(e)}")
                logger.error(f"Raw response content: {response.text[:1000]}")
                return None

            # Enhanced validation of response structure
            expected_keys = ["cik", "entityType", "sic", "sicDescription", "name", "tickers", "exchanges"]
            found_keys = list(company_info.keys())
            missing_keys = [k for k in expected_keys if k not in found_keys]
            
            if missing_keys:
                logger.warning(f"Missing expected keys in SEC API response: {missing_keys}")
                logger.debug(f"Available keys: {found_keys}")
                
                # Try to find alternative fields
                if "cik" not in company_info:
                    company_info["cik"] = padded_cik
                    
                # Extract from nested structures if needed
                if "name" not in company_info and "company" in company_info:
                    company_info["name"] = company_info["company"].get("name", ticker)

            company_info["cik"] = padded_cik  # Ensure CIK is included
            
            # Save to file if requested
            if save_to_file and ticker:
                import json
                out_path = get_output_dir("company_info.json", ticker=ticker)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(company_info, f, indent=2, ensure_ascii=False)
                logger.debug(f"Saved company info to {out_path}")
                
            return company_info

        except Exception as e:
            logger.error(f"Error getting company info for {ticker_or_cik}: {str(e)}")
            import traceback
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            return None

    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get all company facts (all concepts) for a CIK.

        Args:
            cik: Company CIK number

        Returns:
            Dict with all facts and metadata
        Raises:
            SECError: If request fails
        """
        try:
            padded_cik = cik.zfill(10)
            try:
                response = self._make_request(self.COMPANY_FACTS.format(padded_cik))
                if response is None:
                    # 401 error occurred, fallback gracefully
                    logger.info(f"SEC API unavailable for CIK {cik}; returning empty facts.")
                    return {"facts": {}}
            except requests.exceptions.HTTPError as e:
                # If 404, treat as no data and do not retry
                if e.response is not None and e.response.status_code == 404:
                    logger.info(f"SEC companyfacts not found (404) for CIK {cik}; will attempt fallback.")
                    return {"facts": {}}
                # For other errors, retry
                raise
            return response.json()
        except Exception as e:
            raise SECError(f"Failed to get facts for CIK {cik}: {str(e)}")

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def get_company_concept(self, cik: str, concept: str) -> Dict[str, Any]:
        """
        Get specific company concept data.

        Args:
            cik: Company CIK number (will be zero-padded)
            concept: The US GAAP concept to fetch

        Returns:
            Dict containing concept data
        """
        padded_cik = cik.zfill(10)
        response = self._make_request(self.COMPANY_CONCEPT.format(padded_cik, concept))
        if response is None:
            # 401 error occurred, return empty data
            return {"units": {}}
        return response.json()

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def get_sic_data(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Get company SIC code and industry classification.

        Args:
            cik: Company CIK number

        Returns:
            Dict containing SIC code and industry information
        """
        company_info = self.get_company_info(cik)
        if not company_info or "sicCode" not in company_info:
            return None

        return {
            "sic_code": company_info["sicCode"],
            "industry_code": company_info.get("sicDescription"),
            "sic_category": self._categorize_sic(company_info["sicCode"]),
        }

    def _categorize_sic(self, sic_code: str) -> str:
        """
        Categorize SIC code into broad industry groups.

        Args:
            sic_code: SIC code string

        Returns:
            Industry category string
        """
        sic_num = int(sic_code)

        # Technology and Software
        if sic_num in range(7370, 7380):
            return "TECH"
        # Manufacturing
        elif sic_num in range(2000, 4000):
            return "MANUFACTURING"
        # Financial Services
        elif sic_num in range(6000, 6800):
            return "FINANCIAL"
        # Services
        elif sic_num in range(7000, 8900):
            return "SERVICE"
        else:
            return "OTHER"

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=NETWORK_EXCEPTIONS
    )
    def get_executive_officers(self, ticker: str, cik: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch executive officers information from the latest DEF 14A filing.

        Args:
            ticker (str): Stock ticker symbol
            cik (str, optional): Company CIK. If not provided, will be looked up.

        Returns:
            dict or None: Executive officers information if available, else None
        """
        try:
            if cik is None:
                cik = self.lookup_cik(ticker)
                if not cik:
                    logging.warning(f"No CIK found for ticker {ticker}")
                    return None            # Get latest DEF 14A filing
            url = f"{self.SUBMISSIONS_BASE_URL}/{cik}/index.json"
            response = self._make_request(url)  # Use _make_request instead of direct session.get
            if response is None:
                logging.warning(f"SEC API unavailable for CIK {cik} (401 error)")
                return None
            if not response.ok:
                logging.warning(f"Failed to get filings index for CIK {cik}: {response.status_code}")
                return None

            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            if not filings:
                logging.warning(f"No filings found for CIK {cik}")
                return None

            # Find latest DEF 14A filing
            form_types = filings.get('form', [])
            accession_numbers = filings.get('accessionNumber', [])
            primary_docs = filings.get('primaryDocument', [])

            def_14a_indices = [i for i, form in enumerate(form_types) if form == 'DEF 14A']
            if not def_14a_indices:
                logging.warning(f"No DEF 14 A filings found for CIK {cik}")
                return None

            # Get latest DEF 14A
            latest_def_14a_idx = def_14a_indices[0]
            accession_number = accession_numbers[latest_def_14a_idx].replace('-', '')
            primary_doc = primary_docs[latest_def_14a_idx]            # Get the filing content
            filing_url = f"{self.ARCHIVES_BASE_URL}/{cik}/{accession_number}/{primary_doc}"
            response = self._make_request(filing_url)  # Use _make_request instead of direct session.get
            if response is None:
                logging.warning(f"SEC API unavailable for filing (401 error)")
                return None
            if not response.ok:
                logging.warning(f"Failed to get DEF 14A filing content: {response.status_code}")
                return None

            from bs4 import BeautifulSoup
            from bs4.element import Tag, NavigableString
            soup = BeautifulSoup(response.content, 'html.parser')

            headers = [
                "executive officers",
                "executive officer",
                "named executive officers",
                "executive management",
                "senior management",
            ]
            officers_data = []
            text = soup.get_text().lower()
            comp_headers = [
                "salary",
                "compensation",
                "total compensation",
                "stock awards",
                "option awards",
            ]
            for header in headers:
                if header in text:
                    section = soup.find(string=lambda x: isinstance(x, str) and header in x.lower())
                    if not section:
                        continue
                    # Only traverse parents if not NavigableString
                    current = section
                    for _ in range(3):
                        if hasattr(current, 'parent') and current.parent is not None:
                            current = current.parent
                        else:
                            break
                    # Only call find_all if not NavigableString
                    if not isinstance(current, NavigableString) and isinstance(current, Tag):
                        tables = current.find_all('table')
                        for table in tables:
                            if not isinstance(table, Tag):
                                continue
                            rows = table.find_all('tr')
                            if len(rows) < 2:
                                continue
                            header_row = rows[0].get_text().lower()
                            if any(h in header_row for h in comp_headers):
                                for row in rows[1:]:
                                    if not isinstance(row, Tag):
                                        continue
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        name = cells[0].get_text().strip()
                                        title = cells[1].get_text().strip()
                                        compensation = None
                                        for cell in cells[2:]:
                                            text = cell.get_text().strip()
                                            if any(h in text.lower() for h in ['total', 'compensation', 'salary']):
                                                try:
                                                    comp_str = ''.join(c for c in text if c.isdigit() or c == '.')
                                                    compensation = float(comp_str) if comp_str else None
                                                    break
                                                except (ValueError, TypeError):
                                                    pass
                                        if name and title and not any(o['name'] == name for o in officers_data):
                                            officer = {
                                                'name': name,
                                                'title': title,
                                                'totalPay': compensation
                                            }
                                            officers_data.append(officer)
            if not officers_data:
                logging.warning(f"No executive officer data found in DEF 14A for {ticker}")
                return None
            return {'officers': officers_data}
        except Exception as e:
            logging.error(f"Error fetching executive officers for {ticker}: {e}")
            return None
