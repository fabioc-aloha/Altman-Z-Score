"""
Company profile analysis module for determining company characteristics and analysis strategy.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class CompanyStage(Enum):
    """Stages of company development."""
    EARLY = "Early Stage"
    GROWTH = "Growth Stage"
    MATURE = "Mature Stage"

class MarketCategory(Enum):
    """Market categorization for model selection."""
    DEVELOPED = "Developed Markets"
    EMERGING = "Emerging Markets"

class IndustryGroup(Enum):
    """Major industry groups for model selection."""
    TECH = "Technology"
    AI = "Artificial Intelligence"
    MANUFACTURING = "Manufacturing"
    FINANCIAL = "Financial Services"
    SERVICE = "Service"
    OTHER = "Other"

class TechSubsector(Enum):
    """Technology industry subsectors for detailed analysis."""
    SAAS = "Software as a Service"
    AI_ML = "Artificial Intelligence/Machine Learning"
    HARDWARE = "Hardware/Semiconductors"
    CLOUD = "Cloud Infrastructure"
    ECOMMERCE = "E-commerce/Internet"
    CYBERSECURITY = "Cybersecurity"
    FINTECH = "Financial Technology"
    OTHER_TECH = "Other Technology"

@dataclass
class CompanyCharacteristics:
    """Detailed company characteristics for analysis."""
    size_category: str
    rd_intensity: float
    market_cap: Optional[Decimal] = None
    revenue_growth: Optional[float] = None
    operating_margin: Optional[float] = None
    debt_ratio: Optional[float] = None

@dataclass
class CompanyProfile:
    """
    Comprehensive company profile for analysis strategy determination.
    
    This class combines various aspects of a company to determine:
    1. Which Z-score model variant to use
    2. What financial data to prioritize
    3. How to adjust thresholds and interpretation
    """
    ticker: str
    cik: str
    industry_group: IndustryGroup
    market_category: MarketCategory
    company_stage: CompanyStage
    tech_subsector: Optional[TechSubsector] = None
    characteristics: Optional[CompanyCharacteristics] = None
    is_excluded: bool = False
    exclusion_reason: Optional[str] = None
    
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
    
    @property
    def requires_rd_adjustment(self) -> bool:
        """Check if R&D adjustments are needed."""
        return (self.is_tech_or_ai and 
                self.characteristics and 
                self.characteristics.rd_intensity > 0.1)

class ProfileAnalyzer:
    """
    Analyzes company characteristics to determine appropriate analysis strategy.
    """
    def __init__(self, sec_client=None, market_data_client=None):
        """Initialize with optional API clients."""
        self.sec_client = sec_client
        self.market_data_client = market_data_client

    def get_company_stage(self, characteristics: CompanyCharacteristics) -> CompanyStage:
        """
        Determine company stage based on characteristics.
        """
        if not characteristics:
            return CompanyStage.MATURE  # Default to mature if no data
            
        # Early stage indicators
        if (characteristics.revenue_growth and characteristics.revenue_growth > 0.5 and
            characteristics.market_cap and characteristics.market_cap < Decimal('1000000000')):
            return CompanyStage.EARLY
            
        # Growth stage indicators
        if (characteristics.revenue_growth and characteristics.revenue_growth > 0.2 and
            characteristics.operating_margin and characteristics.operating_margin > 0):
            return CompanyStage.GROWTH
            
        return CompanyStage.MATURE

    def analyze_profile(self, ticker: str, cik: str) -> CompanyProfile:
        """
        Create a comprehensive company profile for analysis.
        """
        try:
            # Get industry classification and market category
            industry_info = self._get_industry_info(ticker, cik)
            characteristics = self._get_company_characteristics(ticker, cik)
            stage = self.get_company_stage(characteristics)
            
            return CompanyProfile(
                ticker=ticker,
                cik=cik,
                industry_group=industry_info["industry_group"],
                market_category=industry_info["market_category"],
                tech_subsector=industry_info.get("tech_subsector"),
                company_stage=stage,
                characteristics=characteristics
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze profile for {ticker}: {str(e)}")
            return CompanyProfile(
                ticker=ticker,
                cik=cik,
                industry_group=IndustryGroup.OTHER,
                market_category=MarketCategory.DEVELOPED,
                company_stage=CompanyStage.MATURE,
                is_excluded=True,
                exclusion_reason=str(e)
            )

    def _get_industry_info(self, ticker: str, cik: str) -> Dict:
        """
        Get industry classification information using SEC and market data.
        
        Args:
            ticker: Company ticker symbol
            cik: Company CIK number
            
        Returns:
            Dict containing industry classification
        """
        try:
            # Get SEC industry data
            sic_data = self.sec_client.get_sic_data(cik)
            
            # Get market data for additional classification
            market_data = self.market_data_client.get_market_data(ticker)
            
            industry_group = IndustryGroup.OTHER
            market_category = MarketCategory.DEVELOPED
            tech_subsector = None
            
            # Determine industry group
            if sic_data:
                if sic_data["sic_category"] == "TECH":
                    industry_group = IndustryGroup.TECH
                    # Check for AI/ML focus
                    if any(kw in market_data.industry.lower() for kw in ["ai", "artificial intelligence", "machine learning"]):
                        industry_group = IndustryGroup.AI
                        tech_subsector = TechSubsector.AI_ML
                    elif "software" in market_data.industry.lower():
                        tech_subsector = TechSubsector.SAAS
                    elif any(kw in market_data.industry.lower() for kw in ["semiconductor", "hardware"]):
                        tech_subsector = TechSubsector.HARDWARE
                elif sic_data["sic_category"] == "MANUFACTURING":
                    industry_group = IndustryGroup.MANUFACTURING
                elif sic_data["sic_category"] == "SERVICE":
                    industry_group = IndustryGroup.SERVICE
                    
            # Determine market category
            if market_data.country:
                emerging_markets = {"CN", "IN", "BR", "RU", "ZA"}  # Example emerging markets
                if market_data.country in emerging_markets:
                    market_category = MarketCategory.EMERGING
                    
            return {
                "industry_group": industry_group,
                "market_category": market_category,
                "tech_subsector": tech_subsector
            }
        except Exception as e:
            logger.error(f"Error getting industry info for {ticker}: {str(e)}")
            # Return default classification
            return {
                "industry_group": IndustryGroup.OTHER,
                "market_category": MarketCategory.DEVELOPED,
                "tech_subsector": None
            }

    def _get_company_characteristics(self, ticker: str, cik: str) -> CompanyCharacteristics:
        """
        Get detailed company characteristics from market and financial data.
        
        Args:
            ticker: Company ticker symbol
            cik: Company CIK number
            
        Returns:
            CompanyCharacteristics object
        """
        try:
            # Get market data
            market_data = self.market_data_client.get_market_data(ticker)
            
            # Get R&D intensity from SEC data
            try:
                rd_data = self.sec_client.get_company_concept(cik, "ResearchAndDevelopmentExpense")
                recent_rd = Decimal(rd_data["units"]["USD"][-1]["val"])
                revenue_data = self.sec_client.get_company_concept(cik, "Revenues")
                recent_revenue = Decimal(revenue_data["units"]["USD"][-1]["val"])
                rd_intensity = float(recent_rd / recent_revenue)
            except (KeyError, IndexError, ValueError, ZeroDivisionError):
                rd_intensity = 0.0
                
            # Determine size category
            if market_data.market_cap:
                if market_data.market_cap > Decimal("10000000000"):  # $10B
                    size_category = "Large Cap"
                elif market_data.market_cap > Decimal("2000000000"):  # $2B
                    size_category = "Mid Cap"
                else:
                    size_category = "Small Cap"
            else:
                size_category = "Unknown"
                
            return CompanyCharacteristics(
                size_category=size_category,
                rd_intensity=rd_intensity,
                market_cap=market_data.market_cap,
                revenue_growth=market_data.revenue_growth,
                operating_margin=market_data.operating_margin,
                debt_ratio=None  # Will be calculated during financial analysis
            )
        except Exception as e:
            logger.error(f"Error getting characteristics for {ticker}: {str(e)}")
            # Return minimal characteristics
            return CompanyCharacteristics(
                size_category="Unknown",
                rd_intensity=0.0
            )
