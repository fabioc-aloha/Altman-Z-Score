"""
Model Selection - Automatic Z-Score model selection based on company characteristics

This module determines the most appropriate Z-Score model based on:
- Company type (public/private)
- Market data availability
- Industry sector
- Data completeness

Strategic Advantage:
- Automatic model selection eliminates manual configuration
- Data-driven decisions based on available financial information
- Handles edge cases and data limitations gracefully
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from ...common.logging_config import get_logger
from ...common.exceptions import ModelSelectionError
from ...models.data_models import MergedFinancialData

logger = get_logger(__name__)


class CompanyType(Enum):
    """Company classification for model selection."""
    PUBLIC_MANUFACTURING = "public_manufacturing"
    PUBLIC_SERVICE = "public_service"
    PUBLIC_TECH = "public_tech"
    PUBLIC_RETAIL = "public_retail"
    PRIVATE_COMPANY = "private_company"
    FINANCIAL_COMPANY = "financial_company"  # Special case - excluded
    UNKNOWN = "unknown"


@dataclass
class ModelSelectionResult:
    """Result of model selection process."""
    model_name: str
    company_type: CompanyType
    confidence: float
    selection_rationale: str
    warnings: list[str]
    model_metadata: Dict[str, Any]


class ModelSelector:
    """
    Automatic model selection based on company characteristics.
    
    Selection Logic:
    1. Check for financial sector exclusion
    2. Determine public vs private based on market data
    3. Classify company type based on financial metrics
    4. Select most appropriate Z-Score model
    """
    
    def __init__(self):
        """Initialize model selector."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Model mapping based on company characteristics
        self.model_mapping = {
            CompanyType.PUBLIC_MANUFACTURING: "original",
            CompanyType.PUBLIC_SERVICE: "public_service", 
            CompanyType.PUBLIC_TECH: "original",
            CompanyType.PUBLIC_RETAIL: "retail",
            CompanyType.PRIVATE_COMPANY: "private",
            CompanyType.UNKNOWN: "original"  # Default fallback
        }
    
    def _has_market_data(self, data: MergedFinancialData) -> bool:
        """Check if company has sufficient market data (indicating public company)."""
        return (
            data.market_cap is not None and 
            data.market_cap > 0 and
            data.shares_outstanding is not None and
            data.shares_outstanding > 0
        )
    
    def _classify_company_type(self, data: MergedFinancialData) -> CompanyType:
        """
        Classify company type based on financial characteristics.
        
        Args:
            data: Merged financial data
            
        Returns:
            CompanyType classification
        """
        # Check if company has market data (public vs private)
        is_public = self._has_market_data(data)
        
        if not is_public:
            self.logger.info(f"Classified {data.ticker} as private company (no market data)")
            return CompanyType.PRIVATE_COMPANY
        
        # For public companies, classify by business characteristics
        try:
            # High inventory suggests retail/manufacturing
            if data.inventory_ratio and data.inventory_ratio > 0.15:
                self.logger.info(f"Classified {data.ticker} as retail (high inventory ratio: {data.inventory_ratio:.3f})")
                return CompanyType.PUBLIC_RETAIL
            
            # High asset turnover suggests service business
            if data.asset_turnover and data.asset_turnover > 1.5:
                self.logger.info(f"Classified {data.ticker} as service (high asset turnover: {data.asset_turnover:.3f})")
                return CompanyType.PUBLIC_SERVICE
            
            # Low asset turnover with high margins suggests tech
            if (data.asset_turnover and data.asset_turnover < 0.8 and 
                data.ebit_ratio and data.ebit_ratio > 0.15):
                self.logger.info(f"Classified {data.ticker} as tech (low turnover, high margins)")
                return CompanyType.PUBLIC_TECH
            
            # Default to manufacturing model for public companies
            self.logger.info(f"Classified {data.ticker} as manufacturing (default)")
            return CompanyType.PUBLIC_MANUFACTURING
            
        except Exception as e:
            self.logger.warning(f"Error in company classification for {data.ticker}: {e}")
            return CompanyType.UNKNOWN
    
    def _check_sector_exclusions(self, data: MergedFinancialData) -> Optional[str]:
        """
        Check if company belongs to excluded sectors.
        
        Args:
            data: Merged financial data
            
        Returns:
            Exclusion reason if applicable, None otherwise
        """
        # Note: In a full implementation, this would check SIC codes or industry classification
        # For now, we'll use financial ratios as proxies
        
        # Very high debt-to-equity might indicate financial company
        if data.debt_to_equity and data.debt_to_equity > 10.0:
            return "Possible financial sector company (very high debt ratio)"
        
        # Very low asset turnover with high leverage might indicate financial company
        if (data.asset_turnover and data.asset_turnover < 0.1 and
            data.debt_to_equity and data.debt_to_equity > 5.0):
            return "Possible financial sector company (low turnover, high leverage)"
        
        return None
    
    def _calculate_selection_confidence(self, data: MergedFinancialData, company_type: CompanyType) -> float:
        """
        Calculate confidence score for model selection.
        
        Args:
            data: Merged financial data
            company_type: Classified company type
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have market data
        if self._has_market_data(data):
            confidence += 0.2
        
        # Increase confidence if we have complete financial ratios
        ratio_completeness = 0
        for ratio in [data.working_capital_ratio, data.retained_earnings_ratio, 
                     data.ebit_ratio, data.asset_turnover]:
            if ratio is not None:
                ratio_completeness += 0.25
        
        confidence += ratio_completeness * 0.3
        
        # Decrease confidence for edge cases
        if company_type == CompanyType.UNKNOWN:
            confidence *= 0.6
        
        return min(1.0, confidence)
    
    def select_model(self, data: MergedFinancialData) -> ModelSelectionResult:
        """
        Select the most appropriate Z-Score model for the company.
        
        Args:
            data: Merged financial data
            
        Returns:
            ModelSelectionResult with selected model and metadata
        """
        try:
            self.logger.info(f"Starting model selection for {data.ticker}")
            warnings = []
            
            # Check for sector exclusions
            exclusion_reason = self._check_sector_exclusions(data)
            if exclusion_reason:
                warnings.append(f"Potential sector exclusion: {exclusion_reason}")
            
            # Classify company type
            company_type = self._classify_company_type(data)
            
            # Select model based on classification
            model_name = self.model_mapping.get(company_type, "original")
            
            # Calculate confidence
            confidence = self._calculate_selection_confidence(data, company_type)
            
            # Create selection rationale
            rationale = f"Selected '{model_name}' model for {company_type.value} company"
            if company_type == CompanyType.PRIVATE_COMPANY:
                rationale += " (no market data available)"
            elif company_type == CompanyType.PUBLIC_RETAIL:
                rationale += f" (inventory ratio: {data.inventory_ratio:.3f})"
            elif company_type == CompanyType.PUBLIC_SERVICE:
                rationale += f" (asset turnover: {data.asset_turnover:.3f})"
            
            result = ModelSelectionResult(
                model_name=model_name,
                company_type=company_type,
                confidence=confidence,
                selection_rationale=rationale,
                warnings=warnings,
                model_metadata={
                    'has_market_data': self._has_market_data(data),
                    'data_quality_score': data.data_quality_score,
                    'ratio_completeness': sum(1 for x in [data.working_capital_ratio, 
                                                         data.retained_earnings_ratio,
                                                         data.ebit_ratio, 
                                                         data.asset_turnover] if x is not None) / 4
                }
            )
            
            self.logger.info(f"Model selection complete for {data.ticker}: {model_name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Model selection failed for {data.ticker}: {e}")
            raise ModelSelectionError(f"Model selection failed: {str(e)}")


# Main integration function for external use
def select_appropriate_model(data: MergedFinancialData) -> ModelSelectionResult:
    """
    Public interface for automatic model selection.
    
    Args:
        data: MergedFinancialData from data integration layer
        
    Returns:
        ModelSelectionResult with selected model and rationale
        
    Strategic Advantage:
        Automatic model selection based on company characteristics eliminates
        manual configuration and ensures optimal model choice for each company.
    """
    selector = ModelSelector()
    return selector.select_model(data)
