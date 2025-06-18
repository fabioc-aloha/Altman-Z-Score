import os
from enum import Enum
from typing import Optional, Tuple
import logging
import yfinance as yf
import json
import requests

from altman_zscore.api.sec_client import SECClient
from altman_zscore.utils.paths import get_output_dir
from .company_profile_helpers import (
    find_field,
    get_industry_group,
    classify_maturity
)

logger = logging.getLogger(__name__)

"""
company_profile.py
------------------
Company profile classification and lookup utilities for Altman Z-Score model selection.
Currently limited to U.S.-based companies only.

This module provides logic to classify companies by ticker using SEC EDGAR and Yahoo Finance,
with robust fallback for delisted/edge-case tickers. Used for model selection and reporting.
"""


class IndustryGroup(Enum):
    """
    Enum for high-level industry group classification.
    """
    TECH = "Technology"
    AI = "Artificial Intelligence"
    MANUFACTURING = "Manufacturing"
    FINANCIAL = "Financial Services"
    SERVICE = "Service"
    OTHER = "Other"


class TechSubsector(Enum):
    """
    Enum for technology subsector classification.
    """
    SAAS = "Software as a Service"
    AI_ML = "Artificial Intelligence/Machine Learning"
    HARDWARE = "Hardware/Semiconductors"
    CLOUD = "Cloud Infrastructure"
    ECOMMERCE = "E-commerce/Internet"
    CYBERSECURITY = "Cybersecurity"
    FINTECH = "Financial Technology"
    OTHER_TECH = "Other Technology"


def is_us_company(ticker: str) -> Tuple[bool, str]:
    """
    Determine if a company is U.S.-based using various indicators.
    Currently required for U.S.-only analysis scope.

    Args:
        ticker (str): Company ticker symbol

    Returns:
        Tuple[bool, str]: (is_us_company, reason_if_not)
    """
    try:
        # Get company info from Yahoo Finance
        yf_info = yf.Ticker(ticker).info
        
        # Check country
        country = find_field(yf_info, ["country", "incorporationCountry", "headquartersCountry"])
        if country and country.lower() != "united states":
            return False, f"Non-U.S. company: Based in {country}"
            
        # Check exchange to identify ADRs and foreign listings
        exchange = find_field(yf_info, ["exchange", "fullExchangeName"])
        if exchange:
            exchange = exchange.lower()
            # Check for ADR indicators
            if any(x in ticker.upper() for x in [".AD", "-AD", " ADR", ".ADR", "-ADR"]):
                return False, "Non-U.S. company: ADR (American Depositary Receipt)"
            if exchange in ["pink", "otc", "grey"]:
                if any(x in ticker.upper() for x in ["F:", ".F", "-F", " F"]):
                    return False, "Non-U.S. company: Foreign company on OTC market"
                    
        # Check SEC filing type if available
        sec_filetype = find_field(yf_info, ["secFilings", "mostRecentFilingType", "secFilingType"])
        if sec_filetype and "20-F" in sec_filetype:
            return False, "Non-U.S. company: Files Form 20-F (Foreign Private Issuer)"

        # If all checks pass, assume it's a U.S. company
        return True, ""
        
    except Exception as e:
        logger.warning(f"Error checking if {ticker} is a U.S. company: {str(e)}")
        # If we can't determine, assume it's U.S. to avoid false negatives
        return True, ""


class CompanyProfile:
    """
    Represents a company profile for Altman Z-Score model selection.
    Currently limited to U.S.-based companies only.

    Attributes:
        ticker (str): Stock ticker symbol (uppercase).
        industry (str): Industry string or SIC code.
        is_public (bool): Whether the company is public.
        industry_group (IndustryGroup): Enum for industry group.
        tech_subsector (TechSubsector): Enum for tech subsector (if applicable).
        country (str): Country of headquarters (must be "United States").
        exchange (str): Exchange name.
        founding_year (Optional[int]): Year the company was founded.
        ipo_date (Optional[str]): IPO date (YYYY-MM-DD) if available.
        maturity (str): Company maturity (e.g., 'early-stage', 'growth', 'mature').
    """
    
    def __init__(
        self,
        ticker,
        industry=None,
        is_public=True,
        industry_group=None,
        tech_subsector=None,
        country=None,
        exchange=None,
        founding_year=None,
        ipo_date=None,
        maturity=None,
        cik=None,
        sic=None,
        error=None,
    ):
        """Initialize company profile with U.S. company validation."""
        self.ticker = ticker.upper() if ticker else None
        self.industry = industry
        self.is_public = is_public
        self.industry_group = industry_group or IndustryGroup.OTHER
        self.tech_subsector = tech_subsector
        self.country = country or "US"  # Default to US as we only support US companies
        self.exchange = exchange
        self.founding_year = founding_year
        self.ipo_date = ipo_date
        self.maturity = maturity or "unknown"
        self.cik = cik
        self.sic = sic
        self.error = error
        
        # For existing tickers, validate U.S. company
        if ticker and not error:
            is_us, reason = is_us_company(self.ticker)
            if not is_us:
                raise ValueError(f"Company {self.ticker} is not supported: {reason}")
            
    @staticmethod
    def classify_maturity(founding_year, ipo_date, current_year=None):
        """
        Classify company maturity based on founding year, IPO date, and current year.

        Args:
            founding_year (int or None): Year the company was founded.
            ipo_date (str or None): IPO date (YYYY-MM-DD) if available.
            current_year (int or None): Current year (optional, defaults to system year).
        Returns:
            str: Maturity classification (e.g., 'early-stage', 'growth', 'mature').
        """
        return classify_maturity(founding_year, ipo_date, current_year)

    @staticmethod
    def from_ticker(ticker):
        """
        Classify company by ticker using SEC EDGAR first, then Yahoo Finance as fallback.
        Robustly supports delisted/edge-case tickers by extracting company profile from most recent SEC filing if needed.

        Args:
            ticker (str): Stock ticker symbol.
        Returns:
            CompanyProfile or None: Populated profile if found, else None.
        Notes:
            This method attempts multiple data sources in order of reliability:
                1. SEC EDGAR (preferred for US tickers)
                2. Yahoo Finance (fallback)
                3. Most recent SEC filing (for delisted/edge-case tickers)
            All steps are logged for traceability and debugging.
        """
        # 1. Try SEC EDGAR for US tickers
        try:
            sec_client = SECClient()
            cik = sec_client.lookup_cik(ticker)
            if cik:
                profile = classify_company_by_sec(cik, ticker)
                if profile and profile.industry_group is not None:
                    return profile
        except Exception as e:
            logger.error(f"[CompanyProfile] SEC EDGAR failed for {ticker}: {e}")
            
        # 2. Try yfinance as fallback with retry
        try:
            from altman_zscore.utils.retry import exponential_retry

            # Create retry-wrapped functions for network operations
            @exponential_retry(max_retries=3, base_delay=1.0, backoff_factor=2.0)
            def _get_ticker_info():
                yf_ticker = yf.Ticker(ticker)
                return yf_ticker.info

            # First check if it's a U.S. company
            is_us, reason = is_us_company(ticker)
            if not is_us:
                logger.error(f"[CompanyProfile] {ticker}: {reason}")
                raise ValueError(f"Non-U.S. company not supported: {reason}")

            # Fetch info with retry
            yf_info = _get_ticker_info()
            output_path = get_output_dir("yf_info.json", ticker=ticker)
            with open(output_path, "w") as f:
                json.dump(yf_info, f, indent=2)

            # Dynamically resolve fields
            industry = find_field(yf_info, ["industry", "industryKey", "industryDisp", "sector", "sectorKey", "sectorDisp"])
            country = find_field(yf_info, ["country", "countryKey", "countryDisp"])
            exchange = find_field(yf_info, ["exchange", "fullExchangeName", "exchangeTimezoneName"])
            founding_year = find_field(yf_info, ["founded", "startYear", "foundingYear"])
            ipo_date = find_field(yf_info, ["ipoDate", "ipoYear", "ipo"])
            is_public = True
            maturity = classify_maturity(founding_year, ipo_date)

            if industry:
                # Map to enums if possible
                ig = get_industry_group(industry)
                return CompanyProfile(
                    ticker,
                    industry,
                    is_public,
                    ig,
                    country=country,
                    exchange=exchange,
                    founding_year=founding_year,
                    ipo_date=ipo_date,
                    maturity=maturity,
                )
            else:
                logger.error(f"[CompanyProfile] No industry/sector found for {ticker}")
                raise ValueError(f"Could not determine industry for {ticker}")

        except Exception as e:
            logger.error(f"[CompanyProfile] Profile creation failed for {ticker}: {e}")
            raise
        # 3. If yfinance returns no industry/sector, try to fetch the most recent SEC filing for the ticker (even if delisted)
        try:
            # Try to get a historical CIK from local mapping or fallback file
            cik = lookup_cik(ticker)
            if cik:
                # Try to fetch company info from the last available SEC filing
                profile = classify_company_by_sec(cik, ticker)
                if profile and (profile.industry or profile.industry_group):
                    return profile
            # If still no CIK, try to scrape the most recent SEC filing for the ticker
            # (This is a last-ditch effort for delisted/edge-case tickers)
            # Use SEC EDGAR search API to find the most recent filing for the ticker
            from altman_zscore.api.sec_client import SECClient
            search_url = (
                f"{SECClient.BROWSE_EDGAR_URL}?CIK={ticker}&owner=exclude&action=getcompany&count=1"
            )
            headers = {
                "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"],
                "From": os.getenv("SEC_API_EMAIL", ""),
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            cik = None
            if resp.status_code == 200:
                # Use extract_cik_from_sec_html for CIK extraction from SEC HTML
                cik = extract_cik_from_sec_html(resp.text)
                if cik:
                    # print(f"[DEBUG] Fallback SEC HTML CIK for {ticker}: {cik}")
                    profile = classify_company_by_sec(cik, ticker)
                    if profile and (profile.industry or profile.industry_group):
                        return profile
                else:
                    # print(f"[DEBUG] SEC HTML for {ticker} did not yield CIK. First 500 chars:\n{resp.text[:500]}")
                    pass
            # FINAL fallback: search SEC's company_tickers.json for a historical match
            if not cik:
                try:
                    url = SECClient.COMPANY_TICKERS_URL
                    headers = {
                        "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"],
                        "From": os.getenv("SEC_API_EMAIL", ""),
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    for entry in data.values():
                        if entry["ticker"].upper() == ticker.upper():
                            cik = str(entry["cik_str"]).zfill(10)
                            # print(f"[DEBUG] Fallback company_tickers.json CIK for {ticker}: {cik}")
                            profile = classify_company_by_sec(cik, ticker)
                            if profile and (profile.industry or profile.industry_group):
                                return profile
                    logger.error(f"[ERROR] Ticker {ticker} not found in SEC company_tickers.json (delisted or never listed)")
                except Exception as e:
                    logger.error(f"[CompanyProfile] Could not fetch company_tickers.json for {ticker}: {e}")
        except Exception as e:
            logger.error(f"[CompanyProfile] Could not fetch historical CIK/profile for {ticker}: {e}")
        # No static fallback
        import inspect

        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        # Try to find the calling function and its arguments
        missing_quarter = None
        for f in outer_frames:
            args, _, _, values = inspect.getargvalues(f.frame)
            if "quarter" in args:
                missing_quarter = values.get("quarter", None)
                break
        if missing_quarter:
            logger.error(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance) for quarter {missing_quarter}")
        else:
            logger.error(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance)")
        return None

    def __str__(self):
        """
        Return a string representation of the CompanyProfile.

        Returns:
            str: String summary of the company profile.
        """
        # Fix F541: f-string is missing placeholders
        return f"CompanyProfile(ticker={self.ticker}, industry={self.industry}, is_public={self.is_public})"


# CIK mappings are now handled by the comprehensive SEC cache system

def lookup_cik(ticker: str) -> Optional[str]:
    """
    Lookup the CIK for a given ticker using a local mapping first, then SEC's public ticker-CIK mapping.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        str or None: 10-digit CIK if found, else None.
    Notes:
        This function uses a local mapping for common tickers to reduce API calls.
        For other tickers, it uses the SECClient to lookup CIKs.
    """
    # Use SEC client which will check the mappings and then fall back to API
    try:
        sec_client = SECClient()
        return sec_client.lookup_cik(ticker)
    except Exception as e:
        logger.error(f"Error looking up CIK for {ticker}: {e}")
        return None


def classify_company_by_sec(cik: str, ticker: str) -> dict:
    """Classify a company using SEC EDGAR API data.
    Currently limited to U.S.-based companies only.
    
    Args:
        cik (str): The company's CIK number
        ticker (str): The company's ticker symbol
        
    Returns:
        dict: Company profile with classification info
    """
    try:
        logger.debug(f"[SEC Classification] Starting for ticker {ticker} (CIK: {cik})")
        sec_client = SECClient()
        
        # Get company info from SEC API
        company_info = sec_client.get_company_info(cik)
        
        if not company_info:
            logger.error(f"[SEC Classification] No data returned for {ticker} (CIK: {cik})")
            return None
        
        # Log response structure for debugging
        logger.debug(f"[SEC Classification] Data keys: {list(company_info.keys())}")
        
        # Extract company data from response structure
        name = None
        sic = None
        sic_desc = None
        exchanges = None
        state = None
        
        # Try to extract data from potential field locations
        if "name" in company_info:
            name = company_info["name"]
        elif "company" in company_info and "name" in company_info["company"]:
            name = company_info["company"]["name"]
            logger.debug(f"[SEC Classification] Found name in nested company object: {name}")
        
        if "sic" in company_info:
            sic = str(company_info["sic"])
        elif "company" in company_info and "sic" in company_info["company"]:
            sic = str(company_info["company"]["sic"])
            logger.debug(f"[SEC Classification] Found SIC in nested company object: {sic}")
        
        if "sicDescription" in company_info:
            sic_desc = company_info["sicDescription"]
        elif "company" in company_info and "sicDescription" in company_info["company"]:
            sic_desc = company_info["company"]["sicDescription"]
            logger.debug(f"[SEC Classification] Found SIC description in nested company object: {sic_desc}")
            
        if "exchanges" in company_info:
            exchanges = company_info["exchanges"]
        elif "company" in company_info and "exchanges" in company_info["company"]:
            exchanges = company_info["company"]["exchanges"]
            logger.debug(f"[SEC Classification] Found exchanges in nested company object: {exchanges}")
        
        if "stateOfIncorporation" in company_info:
            state = company_info["stateOfIncorporation"]
        elif "company" in company_info and "stateOfIncorporation" in company_info["company"]:
            state = company_info["company"]["stateOfIncorporation"]
            logger.debug(f"[SEC Classification] Found state in nested company object: {state}")
        
        # Use ticker as fallback name
        name = name or ticker.upper()
        
        # Set description to SIC code if no description available
        sic_desc = sic_desc or (f"SIC: {sic}" if sic else "Unknown")
        
        # Default values for missing fields
        exchanges = exchanges or ["Unknown"]
        state = state or "US"
        
        # Log extracted data
        logger.debug(f"[SEC Classification] Extracted data for {ticker}:")
        logger.debug(f"  Name: {name}")
        logger.debug(f"  SIC: {sic}")
        logger.debug(f"  SIC Description: {sic_desc}")
        logger.debug(f"  Exchanges: {exchanges}")
        logger.debug(f"  State: {state}")
        
        # Determine industry group from SIC code
        industry_group = IndustryGroup.OTHER
        if sic:
            industry_group_str = get_industry_group(sic)
            try:
                industry_group = IndustryGroup[industry_group_str.upper()]
                logger.debug(f"[SEC Classification] Mapped to industry group: {industry_group}")
            except (KeyError, AttributeError) as e:
                logger.warning(f"[SEC Classification] Could not map industry group '{industry_group_str}' to enum: {str(e)}")
        
        # Create company profile
        profile = CompanyProfile(
            ticker=ticker,
            industry=sic_desc,
            is_public=True,  # Assume true since it's in SEC database
            industry_group=industry_group,
            country="United States",  # Already validated as U.S. company
            exchange=exchanges[0] if exchanges else "Unknown",
            cik=cik,
            sic=sic
        )
        
        logger.info(f"[SEC Classification] Successfully classified {ticker} as {industry_group.value}")
        return profile
    
    except Exception as e:
        logger.error(f"[SEC Classification] Error classifying {ticker}: {str(e)}")
        import traceback
        logger.debug(f"[SEC Classification] Exception traceback: {traceback.format_exc()}")
        return None
