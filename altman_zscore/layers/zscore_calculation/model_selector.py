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

- technology: Software, tech hardware, semiconductors, internet companies, semiconductor equipment
  Literature: Altman (1968) original model works well for tech manufacturing; Begley et al. (1996) for software
  Examples: MSFT (Microsoft), AAPL (Apple), GOOGL (Google), NVDA (Nvidia), 
  CRM (Salesforce), ADBE (Adobe), MU (Micron Technology), AMAT (Applied Materials), ASML (ASML Holding)

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
    
    def _classify_industry_fallback(self, data: MergedFinancialData) -> IndustryClassification:
        """
        Fallback industry classification using rule-based logic when LLM is unavailable.
        Uses company profile data, SIC codes, and sector information.
        """
        classification = IndustryClassification()
        
        # Extract company profile data
        profile_data = None
        if hasattr(data, 'raw_fmp_data') and data.raw_fmp_data:
            profile_data = data.raw_fmp_data.get('profile', [])
            if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                profile_data = profile_data[0]
        
        if not profile_data:
            self.logger.warning(f"No company profile data for fallback classification of {data.ticker}")
            classification.confidence = 0.3  # Low confidence without data
            return classification
        
        # Extract key information
        sector = profile_data.get('sector', '').lower()
        industry = profile_data.get('industry', '').lower()
        company_name = profile_data.get('companyName', '').lower()
        description = profile_data.get('description', '').lower()
        
        # Rule-based classification
        confidence = 0.8  # High confidence for rule-based classification
        
        # Financial sector detection
        financial_keywords = ['bank', 'financial', 'insurance', 'reit', 'trust', 'credit', 'investment', 'asset management']
        if (sector and any(keyword in sector for keyword in ['financial', 'insurance'])) or \
           (industry and any(keyword in industry for keyword in financial_keywords)) or \
           any(keyword in company_name for keyword in ['bank', 'financial', 'insurance']):
            classification.is_financial = True
            classification.sector = sector
            classification.industry = industry
            classification.confidence = confidence
            return classification
        
        # Technology sector detection (enhanced)
        tech_keywords = ['technology', 'software', 'semiconductor', 'computer', 'internet', 'tech', 'digital', 'cloud', 'equipment']
        tech_industries = ['semiconductor', 'software', 'internet', 'computer', 'digital', 'cloud', 'equipment', 'electronics']
        if (sector and any(keyword in sector for keyword in ['technology', 'communication'])) or \
           (industry and any(keyword in industry for keyword in tech_keywords)) or \
           (industry and any(keyword in industry for keyword in tech_industries)) or \
           any(keyword in company_name for keyword in ['tech', 'software', 'systems']) or \
           ('semiconductor' in industry.lower() and 'equipment' in industry.lower()) or \
           ('asml' in company_name.lower()):  # Special case for ASML
            classification.is_technology = True
            classification.sector = sector
            classification.industry = industry
            classification.confidence = confidence
            return classification
        
        # Retail sector detection
        retail_keywords = ['retail', 'store', 'shopping', 'consumer', 'apparel', 'clothing', 'e-commerce', 'ecommerce']
        if (sector and any(keyword in sector for keyword in ['consumer', 'retail'])) or \
           (industry and any(keyword in industry for keyword in retail_keywords)) or \
           any(keyword in company_name for keyword in ['retail', 'store']) or \
           any(keyword in description for keyword in ['retail', 'e-commerce', 'online shopping']):
            classification.is_retail = True
            classification.sector = sector
            classification.industry = industry
            classification.confidence = confidence
            return classification
        
        # Service sector detection
        service_keywords = ['service', 'consulting', 'healthcare', 'education', 'professional', 'utility', 'telecom']
        if (sector and any(keyword in sector for keyword in ['healthcare', 'utilities', 'service'])) or \
           (industry and any(keyword in industry for keyword in service_keywords)) or \
           any(keyword in description for keyword in ['service', 'consulting', 'professional']):
            classification.is_service = True
            classification.sector = sector
            classification.industry = industry
            classification.confidence = confidence
            return classification
        
        # Manufacturing detection (default for industrial/materials)
        manufacturing_keywords = ['manufacturing', 'industrial', 'materials', 'chemical', 'automotive', 'aerospace', 'defense']
        if (sector and any(keyword in sector for keyword in ['industrial', 'materials', 'energy'])) or \
           (industry and any(keyword in industry for keyword in manufacturing_keywords)) or \
           any(keyword in description for keyword in ['manufacturing', 'production', 'industrial']):
            classification.is_manufacturing = True
            classification.sector = sector
            classification.industry = industry
            classification.confidence = confidence
            return classification
        
        # Default case - assume manufacturing with lower confidence
        classification.is_manufacturing = True
        classification.sector = sector or "Unknown"
        classification.industry = industry or "Unknown"
        classification.confidence = 0.5  # Lower confidence for default assignment
        
        self.logger.info(f"Fallback classification for {data.ticker}: manufacturing (default, confidence: {classification.confidence:.2f})")
        return classification

    def _has_market_data(self, data: MergedFinancialData) -> bool:
        """Check if market data is available for public company classification."""
        return (hasattr(data, 'market_cap') and data.market_cap is not None and data.market_cap > 0) or \
               (hasattr(data, 'market_equity_ratio') and data.market_equity_ratio is not None and data.market_equity_ratio > 0)

    def _determine_geographic_context(self, data: MergedFinancialData) -> str:
        """Determine if company is from emerging market based on available data."""
        # Extract country information if available
        if hasattr(data, 'raw_fmp_data') and data.raw_fmp_data:
            profile_data = data.raw_fmp_data.get('profile', [])
            if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                country = profile_data[0].get('country', '').upper()
                
                # Emerging market countries (simplified list)
                emerging_markets = {
                    'BRAZIL', 'MEXICO', 'ARGENTINA', 'CHILE', 'COLOMBIA',
                    'CHINA', 'INDIA', 'SOUTH KOREA', 'TAIWAN', 'THAILAND', 'MALAYSIA', 'INDONESIA',
                    'RUSSIA', 'POLAND', 'CZECH REPUBLIC', 'HUNGARY',
                    'SOUTH AFRICA', 'EGYPT', 'NIGERIA',
                    'TURKEY', 'ISRAEL'
                }
                
                if country in emerging_markets:
                    return 'emerging'
        
        return 'developed'

    def select_model(self, data: MergedFinancialData) -> ModelSelectionResult:
        """Enhanced model selection with LLM, fallback, and geographic context."""
        try:
            self.logger.info(f"Enhanced model selection for {data.ticker}")
            warnings = []
            data_quality_issues = []
            detailed_reasoning = []
            
            # Step 1: Try LLM classification first
            industry_classification = self._classify_industry_from_llm(data)
            
            # Step 2: If LLM failed, use fallback classification
            if industry_classification.confidence == 0.0:
                self.logger.info(f"LLM classification unavailable for {data.ticker}, using fallback method")
                industry_classification = self._classify_industry_fallback(data)
                detailed_reasoning.append("Used rule-based classification (LLM unavailable)")
            else:
                detailed_reasoning.append(f"Used LLM classification (confidence: {industry_classification.confidence:.2f})")
            
            # Step 3: If all classification failed, raise error
            if industry_classification.confidence == 0.0:
                error_msg = f"All classification methods failed for {data.ticker}"
                self.logger.error(error_msg)
                raise ModelSelectionError(error_msg)
            
            # Step 4: Check geographic context for emerging markets
            geo_context = self._determine_geographic_context(data)
            if geo_context == 'emerging':
                detailed_reasoning.append("Company from emerging market - considering emerging markets model")
            
            # Step 5: Check data availability
            has_market_data = self._has_market_data(data)
            if not has_market_data:
                detailed_reasoning.append("Market data unavailable - preferring book value models")
                data_quality_issues.append("Market value data not available")
            
            # Step 6: Enhanced company type determination with priority logic
            company_type = self._determine_company_type_enhanced(
                industry_classification, has_market_data, geo_context, detailed_reasoning, warnings
            )
            
            # Step 7: Select model based on company type
            model_name = self.model_mapping.get(company_type, "original")
            
            # Step 8: Create comprehensive rationale
            rationale = self._create_selection_rationale(
                model_name, company_type, industry_classification, has_market_data, geo_context
            )
            
            # Step 9: Final confidence adjustment
            final_confidence = self._calculate_final_confidence(
                industry_classification.confidence, has_market_data, geo_context
            )
            
            result = ModelSelectionResult(
                model_name=model_name,
                company_type=company_type,
                industry_classification=industry_classification,
                confidence=final_confidence,
                selection_rationale=rationale,
                detailed_reasoning=detailed_reasoning,
                warnings=warnings,
                data_quality_issues=data_quality_issues,
                model_metadata={
                    'llm_available': self.llm_available,
                    'llm_used': industry_classification.confidence > 0.0,
                    'has_market_data': has_market_data,
                    'geographic_context': geo_context,
                    'classification_method': 'llm' if industry_classification.confidence > 0.5 else 'fallback'
                }
            )
            
            self.logger.info(f"Selected {model_name} model for {data.ticker} (final confidence: {final_confidence:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Model selection failed for {data.ticker}: {e}")
            raise ModelSelectionError(f"Model selection failed: {str(e)}")

    def _determine_company_type_enhanced(self, industry_classification: IndustryClassification, 
                                        has_market_data: bool, geo_context: str, 
                                        detailed_reasoning: List[str], warnings: List[str]) -> CompanyType:
        """Enhanced company type determination with priority logic."""
        
        # Priority 1: Financial institutions (special handling)
        if industry_classification.is_financial:
            warnings.append("Financial company - Z-Score may not be applicable")
            detailed_reasoning.append("Financial institution detected - using financial model with warnings")
            return CompanyType.PUBLIC_FINANCIAL
        
        # Priority 2: Emerging markets (geographic priority overrides industry for emerging model)
        if geo_context == 'emerging':
            detailed_reasoning.append("Emerging market company - using emerging markets model")
            return CompanyType.EMERGING_MARKET
        
        # Priority 3: Private companies (no market data)
        if not has_market_data:
            detailed_reasoning.append("No market data available - classified as private company")
            return CompanyType.PRIVATE_COMPANY
        
        # Priority 4: Public companies by industry (for developed markets with market data)
        if industry_classification.is_retail:
            detailed_reasoning.append("Retail company with market data - using retail model")
            return CompanyType.PUBLIC_RETAIL
        elif industry_classification.is_service:
            detailed_reasoning.append("Service company with market data - using service model")
            return CompanyType.PUBLIC_SERVICE
        elif industry_classification.is_technology:
            detailed_reasoning.append("Technology company with market data - using original model")
            return CompanyType.PUBLIC_TECH
        elif industry_classification.is_manufacturing:
            detailed_reasoning.append("Manufacturing company with market data - using original model")
            return CompanyType.PUBLIC_MANUFACTURING
        
        # Default: Unknown type -> manufacturing (most conservative choice)
        detailed_reasoning.append("Industry unclear - defaulting to manufacturing (original model)")
        return CompanyType.PUBLIC_MANUFACTURING

    def _create_selection_rationale(self, model_name: str, company_type: CompanyType, 
                                   industry_classification: IndustryClassification, 
                                   has_market_data: bool, geo_context: str) -> str:
        """Create comprehensive rationale for model selection."""
        rationale_parts = []
        
        rationale_parts.append(f"Selected '{model_name}' model for {company_type.value}")
        
        if industry_classification.sector:
            rationale_parts.append(f"({industry_classification.sector} sector")
            if industry_classification.industry:
                rationale_parts[-1] += f", {industry_classification.industry} industry)"
            else:
                rationale_parts[-1] += ")"
        
        if geo_context == 'emerging':
            rationale_parts.append("Emerging market context considered")
        
        if not has_market_data:
            rationale_parts.append("Book value used (market data unavailable)")
        
        return ". ".join(rationale_parts)

    def _calculate_final_confidence(self, base_confidence: float, has_market_data: bool, geo_context: str) -> float:
        """Calculate final confidence score considering all factors."""
        confidence = base_confidence
        
        # Adjust for data availability
        if not has_market_data:
            confidence *= 0.9  # Slight reduction for missing market data
        
        # Adjust for geographic context
        if geo_context == 'emerging':
            confidence *= 0.95  # Slight reduction for emerging market complexity
        
        # Ensure confidence stays within bounds
        return min(0.95, max(0.1, confidence))


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
