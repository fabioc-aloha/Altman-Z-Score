"""Module for looking up CIK numbers for companies from SEC EDGAR."""
from typing import Dict, Optional
import os
import json
import time
import requests
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CACHE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / '.cache'
CACHE_FILE = CACHE_DIR / 'cik_cache.json'
EDGAR_COMPANY_SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
RATE_LIMIT_DELAY = 0.1  # 100ms between requests to respect SEC rate limits

class CIKLookupError(Exception):
    """Custom exception for CIK lookup errors."""
    pass

def get_user_agent() -> str:
    """Get the user agent string from environment variable."""
    logger.debug("Environment: %s", dict(os.environ))
    try:
        user_agent = os.environ.get('SEC_USER_AGENT') or os.environ.get('SEC_EDGAR_USER_AGENT')
        if not user_agent:
            logger.debug("No user agent found in environment")
            raise KeyError("No user agent found")
        return user_agent
    except KeyError:
        raise CIKLookupError(
            "Neither SEC_USER_AGENT nor SEC_EDGAR_USER_AGENT environment variables are set. "
            "Please set one to 'name email' as per SEC requirements."
        )

def load_cache() -> Dict[str, str]:
    """Load the CIK cache from file."""
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load cache: {e}")
    return {}

def save_cache(cache: Dict[str, str]) -> None:
    """Save the CIK cache to file."""
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")

def lookup_cik(ticker: str) -> Optional[str]:
    """
    Look up a company's CIK number using its ticker symbol.
    
    Args:
        ticker (str): The stock ticker symbol
        
    Returns:
        Optional[str]: The CIK number padded with leading zeros to 10 digits,
                      or None if not found
        
    Raises:
        CIKLookupError: If there's an error during the lookup process
    """
    # First ensure we have valid user agent
    user_agent = get_user_agent()  # This will raise CIKLookupError if no user agent
    
    # Check cache first
    cache = load_cache()
    if ticker in cache:
        return cache[ticker]
    
    # Prepare API request
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'CIK': ticker,
        'company': '', 
        'type': '', 
        'owner': 'include',
        'count': '40',
        'action': 'getcompany'
    }
    
    try:
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Make request
        response = requests.get(
            EDGAR_COMPANY_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        # Extract CIK from response
        content = response.text
        logger.debug(f"Response content for {ticker}: {content[:500]}...")  # Log first 500 chars
        
        # Look for various CIK patterns
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
                    cik = content[cik_start:cik_end].strip()
                    logger.debug(f"Found potential CIK for {ticker}: {cik}")
                    if cik.isdigit():
                        # Pad CIK with leading zeros to 10 digits
                        cik = cik.zfill(10)
                        # Update cache
                        cache[ticker] = cik
                        save_cache(cache)
                        return cik
                    
        return None
        
    except requests.RequestException as e:
        raise CIKLookupError(f"Error looking up CIK for {ticker}: {str(e)}")

def validate_cik(ticker: str, expected_cik: str) -> bool:
    """
    Validate that the looked-up CIK matches the expected CIK.
    
    Args:
        ticker (str): The stock ticker symbol
        expected_cik (str): The expected CIK number
        
    Returns:
        bool: True if the CIK matches, False otherwise
    """
    try:
        looked_up_cik = lookup_cik(ticker)
        if looked_up_cik is None:
            return False
        # Ensure both CIKs are padded to 10 digits for comparison
        expected_cik = expected_cik.zfill(10)
        return looked_up_cik == expected_cik
    except CIKLookupError:
        return False

def validate_portfolio_ciks(portfolio: Dict[str, str]) -> Dict[str, bool]:
    """
    Validate CIKs for a portfolio of companies.
    
    Args:
        portfolio (Dict[str, str]): Dictionary mapping tickers to CIKs
        
    Returns:
        Dict[str, bool]: Dictionary mapping tickers to validation results
    """
    results = {}
    for ticker, cik in portfolio.items():
        logger.info(f"Validating CIK for {ticker}")
        results[ticker] = validate_cik(ticker, cik)
    return results
