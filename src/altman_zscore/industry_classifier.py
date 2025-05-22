"""Module for classifying companies by industry and determining appropriate Z-score model."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
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
        industry_group=industry_group,
        market_category=market_category,
        tech_subsector=tech_subsector
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
    industry_group: IndustryGroup
    market_category: MarketCategory
    tech_subsector: Optional[TechSubsector] = None
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

def classify_company(cik: str, ticker: str) -> CompanyProfile:
    """
    Classify a company by industry and determine model parameters.
    
    Args:
        cik: The company's CIK number
        ticker: The company's ticker symbol
        
    Returns:
        CompanyProfile: A profile object with industry and model parameters
    """
    try:
        # Format CIK for SEC API (10 digits with leading zeros)
        padded_cik = cik.zfill(10)
        url = f"{DATA_EDGAR_BASE}/CIK{padded_cik}.json"
        
        response = make_sec_request(url)
        data = response.json()
        
        # Get SIC code and description
        sic = str(data.get("sic", ""))
        business_desc = str(data.get("sicDescription", "")).lower()
        flags = data.get("flags", {})
        
        # Initialize defaults
        market_category = MarketCategory.DEVELOPED
        industry_group = IndustryGroup.OTHER
        tech_subsector = None
        rd_intensity = 0.0
        
        # Determine market category
        if flags.get("foreignPrivateIssuer", False) or any(term in business_desc.lower() for term in [
            "china", "emerging market", "developing economy", "adr", "foreign"
        ]):
            market_category = MarketCategory.EMERGING
        
        # Classify industry based on SIC code and description
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
            industry_group=industry_group,
            market_category=market_category,
            tech_subsector=tech_subsector,
            rd_intensity=rd_intensity
        )
        
    except Exception as e:
        logger.warning(f"Failed to classify company {ticker} (CIK: {cik}) via SEC: {str(e)}")
        logger.info(f"Using fallback classification for {ticker}")
        return get_fallback_classification(ticker)

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
