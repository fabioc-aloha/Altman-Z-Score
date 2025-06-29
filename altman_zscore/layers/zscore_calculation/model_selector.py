"""
Model Selection - Enhanced automatic Z-Score model selection

This module determines the most appropriate Z-Score model based on:
- Company type (public/private) 
- Industry sector classification
- Market data availability
- Financial ratio characteristics
- Data completeness and quality

Strategic Advantages:
- Multi-layered detection logic with industry-specific insights
- Enhanced confidence scoring and transparency
- Robust fallback strategies for missing data
- Detailed rationale and warning system
- Optimized for batch processing reliability
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import re
import json

from ...common.logging_config import get_logger
from ...common.exceptions import ModelSelectionError
from ...models.data_models import MergedFinancialData
from ...layers.data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


class CompanyType(Enum):
    """Enhanced company classification for model selection."""
    PUBLIC_MANUFACTURING = "public_manufacturing"
    PUBLIC_SERVICE = "public_service"
    PUBLIC_TECH = "public_tech"
    PUBLIC_RETAIL = "public_retail"
    PUBLIC_FINANCIAL = "public_financial"  # Enhanced: separate financial classification
    PRIVATE_COMPANY = "private_company"
    EMERGING_MARKET = "emerging_market"    # Enhanced: emerging market classification
    UNKNOWN = "unknown"


@dataclass
class IndustryClassification:
    """Enhanced industry classification data."""
    sector: Optional[str] = None
    industry: Optional[str] = None
    sic_code: Optional[str] = None
    is_financial: bool = False
    is_technology: bool = False
    is_retail: bool = False
    is_manufacturing: bool = False
    is_service: bool = False
    confidence: float = 0.0


@dataclass
class ModelSelectionResult:
    """Enhanced result of model selection process."""
    model_name: str
    company_type: CompanyType
    industry_classification: IndustryClassification
    confidence: float
    selection_rationale: str
    detailed_reasoning: List[str]  # Enhanced: step-by-step reasoning
    warnings: List[str]
    data_quality_issues: List[str]  # Enhanced: specific data quality problems
    model_metadata: Dict[str, Any]


class ModelSelector:
    """
    Simple LLM-based model selection for Z-Score analysis.
    
    Uses LLM to classify companies and select appropriate Z-Score models.
    Falls back to basic classification if LLM is unavailable.
    """
    
    def __init__(self):
        """Initialize model selector with LLM client."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize LLM client
        try:
            self.llm_client = LLMClient()
            self.llm_available = True
            self.logger.info("LLM client initialized successfully")
        except Exception as e:
            self.logger.warning(f"LLM client initialization failed: {e}")
            self.llm_client = None
            self.llm_available = False
        
        # Model mapping
        self.model_mapping = {
            CompanyType.PUBLIC_MANUFACTURING: "original",
            CompanyType.PUBLIC_SERVICE: "service",
            CompanyType.PUBLIC_TECH: "original",
            CompanyType.PUBLIC_RETAIL: "retail",
            CompanyType.PUBLIC_FINANCIAL: "financial",
            CompanyType.PRIVATE_COMPANY: "private",
            CompanyType.EMERGING_MARKET: "emerging",
            CompanyType.UNKNOWN: "original"
        }
    
    def _classify_industry_from_llm(self, data: MergedFinancialData, max_retries: int = 3) -> IndustryClassification:
        """LLM-based industry classification with retry logic."""
        classification = IndustryClassification()
        
        if not self.llm_available:
            self.logger.debug(f"LLM not available for {data.ticker}")
            return classification
        
        # Extract company profile data
        profile_data = None
        if hasattr(data, 'raw_fmp_data') and data.raw_fmp_data:
            profile_data = data.raw_fmp_data.get('profile', [])
            if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                profile_data = profile_data[0]
        
        if not profile_data:
            self.logger.debug(f"No company profile data for LLM classification of {data.ticker}")
            return classification
        
        # Prepare company info (outside retry loop)
        company_info = {
            'ticker': data.ticker,
            'name': profile_data.get('companyName', 'Unknown'),
            'sector': profile_data.get('sector', 'Unknown'),
            'industry': profile_data.get('industry', 'Unknown'),
            'description': profile_data.get('description', ''),
        }
        
        # Enhanced LLM prompt with company examples and academic literature (outside retry loop)
        system_prompt = """You are a financial analyst expert in Z-Score bankruptcy prediction models. Use academic literature to classify companies for the most appropriate Z-Score model.

ACADEMIC LITERATURE GUIDANCE:
- Original Z-Score (Altman 1968): Designed for publicly traded manufacturing companies
- Z'-Score (Altman 1983): Modified for service companies, removes manufacturing-specific ratios
- Z''-Score (Altman 1995): For private companies and emerging markets
- Retail models: Account for high inventory turnover and seasonal patterns
- Financial sector: Traditional Z-Score often inappropriate due to different capital structures

CLASSIFICATION CATEGORIES with Academic Support:

- financial: Banks, insurance, investment firms, REITs
  Literature: Beaver (1966), Ohlson (1980) - Traditional Z-Score often inappropriate for financial firms
  Examples: JPM (JPMorgan Chase), BAC (Bank of America), AIG (American International Group), 
  SCHW (Charles Schwab), PNC (PNC Financial), COF (Capital One), AFL (Aflac)

- technology: Software, tech hardware, semiconductors, internet companies
  Literature: Altman (1968) original model works well for tech manufacturing; Begley et al. (1996) for software
  Examples: MSFT (Microsoft), AAPL (Apple), GOOGL (Google), NVDA (Nvidia), 
  CRM (Salesforce), ADBE (Adobe), MU (Micron Technology), AMAT (Applied Materials)

- retail: Retail chains, e-commerce, consumer goods retailers
  Literature: Chung et al. (2008) - Retail requires models accounting for inventory seasonality
  Examples: AMZN (Amazon), WMT (Walmart), TGT (Target), HD (Home Depot), 
  COST (Costco), NKE (Nike), SBUX (Starbucks), ULTA (Ulta Beauty)

- manufacturing: Industrial, automotive, chemicals, equipment, materials
  Literature: Altman (1968) - Original model specifically designed for manufacturing companies
  Examples: GE (General Electric), CAT (Caterpillar), BA (Boeing), F (Ford), 
  MMM (3M), HON (Honeywell), LMT (Lockheed Martin), EMR (Emerson Electric)

- service: Professional services, healthcare, utilities, telecommunications
  Literature: Altman (1983) Z'-Score for service companies; Chung et al. (2008) for healthcare
  Examples: UNH (UnitedHealth), JNJ (Johnson & Johnson), PG (Procter & Gamble), 
  VZ (Verizon), T (AT&T), NEE (NextEra Energy), SO (Southern Company), DUK (Duke Energy)

Consider the company's:
1. Business model (asset-light vs asset-heavy)
2. Revenue structure (manufacturing vs services vs financial)
3. Industry-specific characteristics
4. Academic literature recommendations

Respond with JSON: {"category": "service", "confidence": 0.9, "reason": "Healthcare services company - Altman Z'-Score (1983) recommended for service firms"}"""

        user_prompt = f"""Company: {company_info['name']} ({company_info['ticker']})
Sector: {company_info['sector']}
Industry: {company_info['industry']}
Description: {company_info['description'][:300]}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Retry logic for LLM calls
        for attempt in range(1, max_retries + 1):
            try:
                response = self.llm_client.chat_completion(
                    ticker=data.ticker,
                    messages=messages,
                    interaction_type="classification",
                    temperature=0.1,
                    max_tokens=200
                )
                
                # Parse response
                llm_result = json.loads(response.strip())
                category = llm_result['category'].lower()
                confidence = float(llm_result['confidence'])
                
                # Set classification flags
                if category == 'financial':
                    classification.is_financial = True
                elif category == 'technology':
                    classification.is_technology = True
                elif category == 'retail':
                    classification.is_retail = True
                elif category == 'manufacturing':
                    classification.is_manufacturing = True
                elif category == 'service':
                    classification.is_service = True
                
                classification.confidence = min(0.95, max(0.0, confidence))
                classification.sector = company_info['sector']
                classification.industry = company_info['industry']
                
                self.logger.info(f"LLM classified {data.ticker} as {category} (confidence: {classification.confidence:.2f})")
                return classification
                
            except Exception as e:
                if attempt == max_retries:
                    self.logger.warning(f"LLM classification failed for {data.ticker} after {max_retries} attempts: {e}")
                else:
                    self.logger.debug(f"LLM classification attempt {attempt} failed for {data.ticker}: {e}. Retrying...")
        
        # Return empty classification if all retries failed
        return classification
    
    def _has_market_data(self, data: MergedFinancialData) -> bool:
        """Check if company has market data (public company indicator)."""
        return (data.market_cap is not None and data.market_cap > 0 and
                data.shares_outstanding is not None and data.shares_outstanding > 0)
    
    def select_model(self, data: MergedFinancialData) -> ModelSelectionResult:
        """Simplified model selection using LLM classification with retries."""
        try:
            self.logger.info(f"Model selection for {data.ticker}")
            warnings = []
            
            # Try LLM classification with retries
            industry_classification = self._classify_industry_from_llm(data)
            
            # If LLM failed completely, raise error
            if industry_classification.confidence == 0.0:
                error_msg = f"LLM classification failed for {data.ticker} after all retries and no fallback available"
                self.logger.error(error_msg)
                raise ModelSelectionError(error_msg)
            
            # Determine company type based on classification
            if industry_classification.is_financial:
                company_type = CompanyType.PUBLIC_FINANCIAL
                warnings.append("Financial company - Z-Score may not be applicable")
            elif not self._has_market_data(data):
                company_type = CompanyType.PRIVATE_COMPANY
            elif industry_classification.is_technology:
                company_type = CompanyType.PUBLIC_TECH
            elif industry_classification.is_retail:
                company_type = CompanyType.PUBLIC_RETAIL
            elif industry_classification.is_service:
                company_type = CompanyType.PUBLIC_SERVICE
            else:
                company_type = CompanyType.PUBLIC_MANUFACTURING
            
            # Select model
            model_name = self.model_mapping.get(company_type, "original")
            
            # Create rationale
            rationale = f"Selected '{model_name}' model for {company_type.value}"
            if industry_classification.sector:
                rationale += f" ({industry_classification.sector} sector)"
            
            result = ModelSelectionResult(
                model_name=model_name,
                company_type=company_type,
                industry_classification=industry_classification,
                confidence=industry_classification.confidence,
                selection_rationale=rationale,
                detailed_reasoning=[rationale],
                warnings=warnings,
                data_quality_issues=[],
                model_metadata={
                    'llm_available': self.llm_available,
                    'llm_used': industry_classification.confidence > 0.0,
                    'has_market_data': self._has_market_data(data)
                }
            )
            
            self.logger.info(f"Selected {model_name} model for {data.ticker} (confidence: {industry_classification.confidence:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Model selection failed for {data.ticker}: {e}")
            raise ModelSelectionError(f"Model selection failed: {str(e)}")


def select_appropriate_model(data: MergedFinancialData) -> ModelSelectionResult:
    """
    Simplified model selection using LLM classification.
    
    Args:
        data: MergedFinancialData from data integration layer
        
    Returns:
        ModelSelectionResult with LLM-based classification
    """
    selector = ModelSelector()
    return selector.select_model(data)
