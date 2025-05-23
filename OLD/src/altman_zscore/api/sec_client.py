"""
SEC EDGAR API client module for handling all SEC data fetching operations.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import os
import logging
import requests
from functools import lru_cache
import urllib.parse
from pydantic import ValidationError

from .rate_limiter import TokenBucket, RateLimitStrategy, RateLimitExceeded
from ..config import MAX_RETRIES, FALLBACK_DELAY
import time
from .metrics import SEC_API_REQUESTS, SEC_API_REQUEST_ERRORS, SEC_API_REQUEST_LATENCY
from json import JSONDecodeError
from ..schemas.edgar import XBRLData

logger = logging.getLogger(__name__)

class SECError(Exception):
    """Base exception for SEC API errors."""
    pass

class SECRateError(SECError):
    """Exception for rate limit errors."""
    pass

class SECResponseError(SECError):
    """Exception for response validation errors."""
    pass

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
        self.email = email or os.getenv("SEC_API_EMAIL")
        if not self.email:
            raise ValueError("SEC API email is required. Set SEC_API_EMAIL environment variable.")
            
        self.rate_limiter = TokenBucket(
            rate=self.REQUEST_RATE,
            capacity=self.REQUEST_RATE * 2,
            strategy=RateLimitStrategy.WAIT
        )
        self.session = self._create_session()
        self._last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": f"altman-zscore-analyzer {self.email}",
            "Accept": "application/json",
        })
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
        Make request to SEC API with rate limiting and retries.
        """
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        for attempt in range(MAX_RETRIES + 1):
            start_time = time.time()
            try:
                # Rate limiting
                self.rate_limiter.acquire(timeout=timeout)
                response = self.session.request(method, url, timeout=timeout, **kwargs)
                if response.status_code == 429:
                    raise SECRateError(f"Rate limit exceeded. Retry after {int(response.headers.get('Retry-After', 10))} seconds.")
                response.raise_for_status()
                # Metrics on success
                SEC_API_REQUESTS.labels(method=method, endpoint=endpoint).inc()
                SEC_API_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
                return response
            except RateLimitExceeded as e:
                SEC_API_REQUEST_ERRORS.labels(method=method, endpoint=endpoint, error=type(e).__name__).inc()
                if attempt >= MAX_RETRIES:
                    raise SECRateError(f"Rate limit exceeded: {str(e)}")
            except SECRateError as e:
                SEC_API_REQUEST_ERRORS.labels(method=method, endpoint=endpoint, error=type(e).__name__).inc()
                if attempt >= MAX_RETRIES:
                    raise
            except requests.exceptions.HTTPError as e:
                SEC_API_REQUEST_ERRORS.labels(method=method, endpoint=endpoint, error=type(e).__name__).inc()
                if attempt >= MAX_RETRIES:
                    status = e.response.status_code if e.response else None
                    if status == 404:
                        raise SECError(f"Resource not found: {url}")
                    raise SECError(f"HTTP error occurred: {str(e)}")
            except requests.exceptions.RequestException as e:
                SEC_API_REQUEST_ERRORS.labels(method=method, endpoint=endpoint, error=type(e).__name__).inc()
                if attempt >= MAX_RETRIES:
                    raise SECError(f"Request failed: {str(e)}")
            # Exponential backoff before retry
            backoff = FALLBACK_DELAY * (2 ** attempt)
            time.sleep(backoff)
        # All retries exhausted
        raise SECError(f"Failed to fetch {endpoint} after {MAX_RETRIES} retries")

    def _request_json(self, endpoint: str, method: str = "GET", timeout: float = 10.0, **kwargs) -> Any:
        """
        Make request and parse JSON, raising SECResponseError on decode failures.
        """
        response = self._make_request(endpoint, method=method, timeout=timeout, **kwargs)
        try:
            return response.json()
        except (ValueError, JSONDecodeError) as e:
            raise SECResponseError(f"Failed to parse JSON from {endpoint}: {e}")

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
                'CIK': ticker,
                'Find': 'Search',
                'owner': 'exclude',
                'action': 'getcompany'
            }
            response = self.session.get(self.BROWSE_EDGAR_URL, params=search_params)
            response.raise_for_status()
            content = response.text
            
            # Extract CIK from search results
            cik_patterns = [
                ('CIK=', ['<', '"', '&']),
                ('CIK:', ['<', '"', '&', ' ']),
                ('CIK Number:', ['<', '"', '&', ' ']),
                ('data-cik="', ['"'])
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

    def get_company_info(self, ticker_or_cik: str) -> Optional[Dict[str, Any]]:
        """
        Get company info from SEC EDGAR.
        
        Args:
            ticker_or_cik: Stock ticker symbol or CIK number
            
        Returns:
            Company info including CIK if found, None otherwise
        """
        try:
            # If input might be a ticker, try to get CIK first
            cik = ticker_or_cik
            if not ticker_or_cik.isdigit():
                cik = self.lookup_cik(ticker_or_cik)
                if not cik:
                    logger.warning(f"No CIK found for ticker {ticker_or_cik}")
                    return None
            
            # Ensure CIK is properly padded
            padded_cik = cik.zfill(10)
            
            # Get company details using CIK
            self._ensure_rate_limit()
            company_info = self._request_json(self.COMPANY_SEARCH.format(padded_cik))
            return company_info.get("company", {})
        except Exception as e:
            logger.error(f"Error fetching company info for {ticker_or_cik}: {str(e)}")
            return None

    @lru_cache(maxsize=1000)
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get company facts from SEC XBRL API.
        """
        padded_cik = cik.zfill(10)
        raw = self._request_json(self.COMPANY_FACTS.format(padded_cik))
        # Validate XBRL response
        try:
            XBRLData.parse_obj(raw)
        except ValidationError as e:
            SEC_API_REQUEST_ERRORS.labels(method='get_company_facts', endpoint=self.COMPANY_FACTS.format(padded_cik), error='ValidationError').inc()
            raise SECResponseError(f"Validation error parsing company facts for CIK {padded_cik}: {e}")
        return raw
