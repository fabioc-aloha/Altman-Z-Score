"""
SEC EDGAR API client module for handling all SEC data fetching operations.
"""

import logging
import os
import time
import urllib.parse
from functools import lru_cache
from typing import Any, Dict, Optional

import requests

from .rate_limiter import RateLimitExceeded, RateLimitStrategy, TokenBucket
from altman_zscore.utils.paths import get_output_dir

logger = logging.getLogger(__name__)


class SECError(Exception):
    """Base exception for SEC API errors."""


class SECRateError(SECError):
    """Exception for rate limit errors."""


class SECResponseError(SECError):
    """Exception for response validation errors."""


class SECClient:
    """
    Client for interacting with SEC EDGAR API.
    """

    BASE_URL = "https://data.sec.gov"
    BROWSE_EDGAR_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
    COMPANY_SEARCH = "/submissions/CIK{}.json"
    COMPANY_FACTS = "/api/xbrl/companyfacts/CIK{}.json"
    COMPANY_CONCEPT = "/api/xbrl/companyconcept/CIK{}/us-gaap/{}.json"

    # SEC EDGAR requires 100ms between requests (10 requests per second)
    REQUEST_RATE = 10  # requests per second
    MIN_REQUEST_INTERVAL = 0.1  # seconds

    def __init__(self, email: Optional[str] = None):
        """Initialize client."""
        # Prefer SEC_EDGAR_USER_AGENT for User-Agent header, fallback to SEC_API_EMAIL for legacy support
        self.user_agent = os.getenv("SEC_EDGAR_USER_AGENT")
        self.email = email or os.getenv("SEC_API_EMAIL")
        if not self.user_agent and not self.email:
            raise ValueError(
                "SEC EDGAR User-Agent is required. Set SEC_EDGAR_USER_AGENT or SEC_API_EMAIL in your environment."
            )
        self.rate_limiter = TokenBucket(
            rate=self.REQUEST_RATE, capacity=self.REQUEST_RATE * 2, strategy=RateLimitStrategy.WAIT
        )
        self.session = self._create_session()
        self._last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        if self.user_agent:
            session.headers.update(
                {
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                }
            )
        else:
            # Fallback for legacy support
            session.headers.update(
                {
                    "User-Agent": f"altman-zscore-analyzer {self.email}",
                    "Accept": "application/json",
                }
            )
        return session

    def _ensure_rate_limit(self):
        """Ensure we respect SEC EDGAR rate limits."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - time_since_last)
        self._last_request_time = time.time()

    def _make_request(self, endpoint: str, method: str = "GET", timeout: float = 10.0, **kwargs) -> requests.Response:
        """
        Make request to SEC API with rate limiting and error handling.

        Args:
            endpoint: API endpoint
            method: HTTP method
            timeout: Request timeout in seconds
            **kwargs: Additional request parameters

        Returns:
            Response from SEC API

        Raises:
            SECRateError: If rate limit is exceeded
            SECResponseError: If response validation fails
            SECError: For other SEC API errors
        """
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)

        try:
            # Wait for rate limit
            self.rate_limiter.acquire(timeout=timeout)

            response = self.session.request(method, url, timeout=timeout, **kwargs)

            # Handle rate limiting responses
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                raise SECRateError(f"Rate limit exceeded. Retry after {retry_after} seconds.")

            response.raise_for_status()

            return response

        except RateLimitExceeded as e:
            raise SECRateError(f"Rate limit exceeded: {str(e)}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise SECError(f"Resource not found: {url}")
            raise SECError(f"HTTP error occurred: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise SECError(f"Request failed: {str(e)}")

    def lookup_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK number for a ticker symbol.

        Args:
            ticker: Stock ticker symbol

        Returns:
            10-digit CIK if found, None otherwise
        """
        self._ensure_rate_limit()
        try:
            search_params = {
                "CIK": ticker,
                "Find": "Search",
                "owner": "exclude",
                "action": "getcompany",
            }
            response = self.session.get(self.BROWSE_EDGAR_URL, params=search_params)
            response.raise_for_status()
            content = response.text

            # Extract CIK from search results
            cik_patterns = [
                ("CIK=", ["<", '"', "&"]),
                ("CIK:", ["<", '"', "&", " "]),
                ("CIK Number:", ["<", '"', "&", " "]),
                ('data-cik="', ['"']),
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
            cik = ticker_or_cik
            ticker = ticker_or_cik.upper() if not ticker_or_cik.isdigit() else None
            if not ticker_or_cik.isdigit():
                cik = self.lookup_cik(ticker_or_cik)
                if not cik:
                    logger.warning(f"No CIK found for ticker {ticker_or_cik}")
                    return None

            # Ensure CIK is properly padded
            padded_cik = cik.zfill(10)

            # Get company details using CIK
            self._ensure_rate_limit()
            response = self._make_request(self.COMPANY_SEARCH.format(padded_cik))
            if response.status_code != 200:
                logger.error(f"Failed to get company info for CIK {padded_cik}")
                return None

            company_info = response.json()
            company_info["cik"] = padded_cik
            if save_to_file and ticker:
                import json
                out_path = get_output_dir("company_info.json", ticker=ticker)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(company_info, f, indent=2, ensure_ascii=False)
            return company_info

        except Exception as e:
            logger.error(f"Error getting company info for {ticker_or_cik}: {str(e)}")
            return None

    @lru_cache(maxsize=1000)
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get company facts from SEC XBRL API.

        Args:
            cik: Company CIK number (will be zero-padded)

        Returns:
            Dict containing company facts
        """
        padded_cik = cik.zfill(10)
        response = self._make_request(self.COMPANY_FACTS.format(padded_cik))
        return response.json()

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
        return response.json()

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
