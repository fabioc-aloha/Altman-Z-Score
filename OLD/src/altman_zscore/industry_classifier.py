"""Module for classifying companies by industry and determining appropriate Z-score model."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any # Ensure Any is imported
import requests
import logging
import os
import time
import urllib.parse

# Define the base URL for SEC EDGAR API
DATA_EDGAR_BASE = "https://data.sec.gov/submissions"

logger = logging.getLogger(__name__)

def get_fallback_classification(ticker: str) -> 'CompanyProfile':
    """
    Get a fallback classification when SEC data is not available.
    Uses basic ticker patterns to guess industry.
    """
    # Default to OTHER and DEVELOPED
    industry_group = IndustryGroup.OTHER
    market_category = MarketCategory.DEVELOPED
    tech_subsector = None
    
    # Common ticker patterns
    if any(ticker.startswith(prefix) for prefix in ["BABA", "PDD", "TCEHY", "NIO"]):
        market_category = MarketCategory.EMERGING
    
    if any(ticker.endswith(suffix) for suffix in [".AI", "AI", "ML"]):
        industry_group = IndustryGroup.AI
        tech_subsector = TechSubsector.AI_ML
    elif ticker in ["MSFT", "ORCL", "CRM", "ADBE", "NOW", "SNOW"]:
        industry_group = IndustryGroup.TECH
        tech_subsector = TechSubsector.SAAS
    elif ticker in ["AAPL", "NVDA", "AMD", "TSM"]:
        industry_group = IndustryGroup.TECH
        tech_subsector = TechSubsector.HARDWARE
    elif ticker in ["F", "GM", "BA", "CAT"]:
        industry_group = IndustryGroup.MANUFACTURING
    
    return CompanyProfile(
        ticker=ticker,
        cik="0" * 10,  # Placeholder CIK
        name=ticker, # Fallback name
        industry_group=industry_group,
        market_category=market_category,
        tech_subsector=tech_subsector,
        gaap_type="us-gaap", # Default
        country="Unknown", # Fallback
        exchange="Unknown" # Fallback
        # rd_intensity and is_public will use dataclass defaults
    )

class IndustryGroup(Enum):
    """Major industry groups for model selection."""
    TECH = "Technology"
    AI = "Artificial Intelligence"
    MANUFACTURING = "Manufacturing"
    FINANCIAL = "Financial Services"
    SERVICE = "Service"
    OTHER = "Other"

class MarketCategory(Enum):
    """Market categorization for model selection."""
    DEVELOPED = "Developed Markets"
    EMERGING = "Emerging Markets"

class TechSubsector(Enum):
    """Technology industry subsectors for more specific analysis."""
    SAAS = "Software as a Service"
    AI_ML = "Artificial Intelligence/Machine Learning"
    HARDWARE = "Hardware/Semiconductors"
    CLOUD = "Cloud Infrastructure"
    ECOMMERCE = "E-commerce/Internet"
    CYBERSECURITY = "Cybersecurity"
    FINTECH = "Financial Technology"
    OTHER_TECH = "Other Technology"

@dataclass
class CompanyProfile:
    """Class representing a company's industry profile and characteristics."""
    ticker: str
    cik: str
    name: str # Added
    industry_group: IndustryGroup
    market_category: MarketCategory
    gaap_type: str = "us-gaap" # Added with default
    tech_subsector: Optional[TechSubsector] = None
    country: Optional[str] = None # Added
    exchange: Optional[str] = None # Added
    rd_intensity: float = 0.0
    is_public: bool = True
    
    @property
    def is_tech_or_ai(self) -> bool:
        """Check if company is in tech or AI sector."""
        return self.industry_group in (IndustryGroup.TECH, IndustryGroup.AI)
    
    @property
    def is_manufacturing(self) -> bool:
        """Check if company is in manufacturing sector."""
        return self.industry_group == IndustryGroup.MANUFACTURING
    
    @property
    def is_emerging_market(self) -> bool:
        """Check if company is in emerging markets."""
        return self.market_category == MarketCategory.EMERGING

def make_sec_request(url: str, max_retries: int = 3, retry_delay: int = 1) -> requests.Response:
    """Make a request to the SEC EDGAR API with retries."""
    headers = {
        'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
        'Accept': 'application/json',
        'Host': 'data.sec.gov'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay * (attempt + 1))
    
    raise requests.RequestException(f"Failed after {max_retries} attempts")

def classify_company(cik: str, ticker: str, config: Optional[Any] = None) -> CompanyProfile: # Added optional config for future use, not currently used by this function for SEC_USER_AGENT
    """
    Classify a company by industry and determine model parameters.
    
    Args:
        cik: The company's CIK number
        ticker: The company's ticker symbol
        config: Optional configuration object (currently unused here but good for consistency)
        
    Returns:
        CompanyProfile: A profile object with industry and model parameters
    """
    try:
        # Format CIK for SEC API (10 digits with leading zeros)
        padded_cik = cik.zfill(10)
        url = f"{DATA_EDGAR_BASE}/CIK{padded_cik}.json"
        
        response = make_sec_request(url)
        data = response.json()
        
        # Initialize defaults
        company_name = data.get("name", ticker) # Get name from SEC data, fallback to ticker
        sic = ""
        business_desc = "".lower()
        flags = {}
        country_of_incorporation = data.get("stateOfIncorporation") or data.get("countryOfIncorporation") # Try to get country
        exchange = data.get("exchanges", [None])[0] # Get primary exchange

        if isinstance(data, dict):
            # Populate from top-level of data if it's a dictionary
            raw_top_sic = data.get("sic")
            if isinstance(raw_top_sic, list) and raw_top_sic:
                sic = str(raw_top_sic[0])
            elif isinstance(raw_top_sic, (str, int)): # SICs can be numbers
                sic = str(raw_top_sic)
            # else sic remains ""

            raw_top_desc = data.get("description")
            business_desc = (str(raw_top_desc) if raw_top_desc is not None else "").lower()
            
            top_flags = data.get("flags")
            if isinstance(top_flags, dict):
                flags = top_flags
            # else flags remains {}

            # Alternative path for newer filings if SIC not found at top level
            # and data itself is a dictionary containing "filings"
            if not sic and "filings" in data: # "filings" in data implies data is a dict here
                filings_data = data.get("filings") # data.get("filings") is safer
                if isinstance(filings_data, dict):
                    recent_data = filings_data.get("recent") # recent_data could be dict, str, None, etc.
                    
                    if isinstance(recent_data, dict): # CRITICAL CHECK: Only proceed if recent_data is a dictionary
                        # Get SIC from recent filings
                        raw_recent_sic = recent_data.get("sic")
                        if isinstance(raw_recent_sic, list) and raw_recent_sic:
                            sic = str(raw_recent_sic[0]) # Update main sic
                        elif isinstance(raw_recent_sic, (str, int)):
                            sic = str(raw_recent_sic) # Update main sic
                        # else sic (which is currently "" from top-level check or previous state) remains as is.
                        
                        # Update business_desc from recent_data if description is present
                        raw_recent_desc = recent_data.get("description")
                        if raw_recent_desc is not None: # If key "description" exists in recent_data
                            business_desc = (str(raw_recent_desc) if raw_recent_desc else "").lower()
                        # else business_desc (from top-level or its previous state) is retained.
        # else: data is not a dict (e.g. JSON response was a string), 
        # so sic, business_desc, flags remain at their initialized defaults ("", "", {})

        # Initialize Z-score model parameters (these are determined after parsing)
        market_category = MarketCategory.DEVELOPED # Default
        # industry_group and tech_subsector will be set based on SIC and business_desc
        rd_intensity = 0.0 # This is not derived from current SEC data parsing

        # Determine market category
        # flags is guaranteed to be a dict here (either from data or default {})
        if flags.get("foreignPrivateIssuer", False) or any(term in business_desc for term in [
            "china", "emerging market", "developing economy", "adr", "foreign"
        ]):
            market_category = MarketCategory.EMERGING
        
        # Classify industry based on SIC code and description
        industry_group = IndustryGroup.OTHER # Default
        tech_subsector = None # Default
        
        if sic: # Proceed with classification only if SIC code is available and not empty
            if sic.startswith(("73", "74")):  # Tech Services
                industry_group = IndustryGroup.TECH
                if "software" in business_desc or "saas" in business_desc:
                    tech_subsector = TechSubsector.SAAS
                elif any(term in business_desc for term in [
                    "ai", "artificial intelligence", "machine learning"
                ]):
                    tech_subsector = TechSubsector.AI_ML
                    industry_group = IndustryGroup.AI
            elif sic.startswith(("20", "30", "40")):  # Manufacturing
                industry_group = IndustryGroup.MANUFACTURING
            elif sic.startswith(("60", "61", "62")):  # Financial
                industry_group = IndustryGroup.FINANCIAL
            elif sic.startswith(("70", "72", "75")):  # Services
                industry_group = IndustryGroup.SERVICE
        
        return CompanyProfile(
            ticker=ticker,
            cik=cik,
            name=company_name,
            industry_group=industry_group,
            market_category=market_category,
            tech_subsector=tech_subsector,
            rd_intensity=rd_intensity, # This is still default 0.0
            gaap_type="us-gaap", # Default, could be refined if SEC data indicates (e.g. IFRS for 20-F)
            country=country_of_incorporation,
            exchange=exchange
        )
        
    except Exception as e:
        logger.warning(f"Failed to classify company {ticker} (CIK: {cik}) via SEC: {str(e)}")
        logger.info(f"Using fallback classification for {ticker}")
        # Fallback needs to provide all new fields
        fallback_profile = get_fallback_classification(ticker) # get_fallback_classification needs to be updated
        return CompanyProfile(
            ticker=ticker,
            cik=fallback_profile.cik, # Use CIK from fallback if available
            name=ticker, # Fallback name
            industry_group=fallback_profile.industry_group,
            market_category=fallback_profile.market_category,
            tech_subsector=fallback_profile.tech_subsector,
            gaap_type="us-gaap", # Default for fallback
            country=None, # Or a default if known for fallbacks
            exchange=None  # Or a default
        )

class CompanyStage(Enum):
    """Company lifecycle stages."""
    EARLY = "Early Stage"
    GROWTH = "Growth Stage"
    MATURE = "Mature Stage"

def determine_company_stage(
    profile: 'CompanyProfile',
    revenue_growth: Optional[float] = None,
    market_cap: Optional[float] = None
) -> CompanyStage:
    """
    Determine company's lifecycle stage based on characteristics and metrics.
    
    Args:
        profile: Company profile object
        revenue_growth: Year-over-year revenue growth rate (if available)
        market_cap: Market capitalization in USD (if available)
    
    Returns:
        CompanyStage indicating lifecycle stage
    """
    # Default to MATURE for manufacturing or non-tech
    if not profile.is_tech_or_ai and not profile.tech_subsector:
        return CompanyStage.MATURE
    
    # For tech companies, use revenue growth if available
    if revenue_growth is not None:
        if revenue_growth > 1.0:  # Over 100% YoY growth
            return CompanyStage.EARLY
        elif revenue_growth > 0.3:  # Over 30% YoY growth
            return CompanyStage.GROWTH
        else:
            return CompanyStage.MATURE
    
    # Fallback to market cap for tech companies
    if market_cap is not None:
        if market_cap < 1e9:  # Under $1B
            return CompanyStage.EARLY
        elif market_cap < 10e9:  # Under $10B
            return CompanyStage.GROWTH
        else:
            return CompanyStage.MATURE
    
    # Default to GROWTH for tech without metrics
    if profile.is_tech_or_ai:
        return CompanyStage.GROWTH
        
    return CompanyStage.MATURE
