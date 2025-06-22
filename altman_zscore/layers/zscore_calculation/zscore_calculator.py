"""
Z-Score Calculator - Direct calculation from MergedFinancialData

Strategic Advantages:
- Direct calculation from FMP standardized financial data
- No field mapping complexity 
- No legacy module dependencies
- Automatic model selection based on company characteristics
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

from ...common.logging_config import get_logger
from ...common.exceptions import CalculationError
from ...models.data_models import MergedFinancialData
from .model_selector import ModelSelector, CompanyType


logger = get_logger(__name__)


@dataclass
class ZScoreCalculationResult:
    """Result of Z-Score calculation."""
    ticker: str
    z_score: float
    model_used: str
    risk_category: str
    component_values: Dict[str, float]
    calculation_timestamp: str
    data_quality_score: float
    warnings: List[str]
    metadata: Dict[str, Any]


class ZScoreCalculator:
    """
    Direct Z-Score calculator using MergedFinancialData.
    
    This implementation calculates Z-Scores directly from the standardized
    financial data structure, eliminating the need for complex field mapping.
    """
    
    def __init__(self):
        """Initialize the Z-Score calculator."""
        self.logger = get_logger(self.__class__.__name__)
        self.model_selector = ModelSelector()
        
        # Z-Score thresholds for risk categorization
        self.risk_thresholds = {
            "original": {"safe": 2.99, "gray": 1.81},
            "public_service": {"safe": 2.6, "gray": 1.1},
            "private": {"safe": 2.9, "gray": 1.23},
            "retail": {"safe": 2.85, "gray": 1.75}
        }
    
    def _calculate_original_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate original Altman Z-Score for manufacturing companies.
        
        Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        
        Where:
        A = Working Capital / Total Assets
        B = Retained Earnings / Total Assets  
        C = EBIT / Total Assets
        D = Market Value Equity / Total Liabilities
        E = Sales / Total Assets
        """
        components = {}
        
        # Component A: Working Capital / Total Assets
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            # Calculate from raw data if available
            raw_data = data.raw_fmp_data or {}
            current_assets = raw_data.get('current_assets', 0)
            current_liabilities = raw_data.get('current_liabilities', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets
        
        # Component B: Retained Earnings / Total Assets
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            # Calculate from raw data
            raw_data = data.raw_fmp_data or {}
            retained_earnings = raw_data.get('retained_earnings', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['retained_earnings_ratio'] = retained_earnings / total_assets
        
        # Component C: EBIT / Total Assets
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            # Calculate from raw data
            raw_data = data.raw_fmp_data or {}
            ebit = raw_data.get('ebit', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['ebit_ratio'] = ebit / total_assets
        
        # Component D: Market Value Equity / Total Liabilities
        if data.market_cap and data.raw_fmp_data:
            total_liabilities = data.raw_fmp_data.get('total_liabilities', 1)
            components['market_equity_ratio'] = data.market_cap / total_liabilities
        else:
            components['market_equity_ratio'] = 0.0
        
        # Component E: Sales / Total Assets (Asset Turnover)
        if data.asset_turnover is not None:
            components['asset_turnover'] = data.asset_turnover
        else:
            # Calculate from raw data
            raw_data = data.raw_fmp_data or {}
            revenue = raw_data.get('revenue', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['asset_turnover'] = revenue / total_assets
        
        # Calculate Z-Score
        z_score = (
            1.2 * components.get('working_capital_ratio', 0) +
            1.4 * components.get('retained_earnings_ratio', 0) +
            3.3 * components.get('ebit_ratio', 0) +
            0.6 * components.get('market_equity_ratio', 0) +
            1.0 * components.get('asset_turnover', 0)
        )
        
        components['z_score'] = z_score
        return components
    
    def _calculate_service_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate Z-Score for service companies (no sales component).
        
        Z = 6.56*A + 3.26*B + 6.72*C + 1.05*D
        """
        components = {}
        
        # Same ratios as original but different weights
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            current_assets = raw_data.get('current_assets', 0)
            current_liabilities = raw_data.get('current_liabilities', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets
        
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            retained_earnings = raw_data.get('retained_earnings', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['retained_earnings_ratio'] = retained_earnings / total_assets
        
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            ebit = raw_data.get('ebit', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['ebit_ratio'] = ebit / total_assets
        
        if data.market_cap and data.raw_fmp_data:
            book_value = data.raw_fmp_data.get('book_value_equity', 1)
            components['market_to_book_ratio'] = data.market_cap / book_value
        else:
            components['market_to_book_ratio'] = 0.0
        
        # Calculate service Z-Score
        z_score = (
            6.56 * components.get('working_capital_ratio', 0) +
            3.26 * components.get('retained_earnings_ratio', 0) +
            6.72 * components.get('ebit_ratio', 0) +
            1.05 * components.get('market_to_book_ratio', 0)
        )
        
        components['z_score'] = z_score
        return components
    
    def _calculate_private_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate Z-Score for private companies (no market data).
        
        Z = 0.717*A + 0.847*B + 3.107*C + 0.420*D + 0.998*E
        """
        components = {}
        
        # Use book values instead of market values
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            current_assets = raw_data.get('current_assets', 0)
            current_liabilities = raw_data.get('current_liabilities', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets
        
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            retained_earnings = raw_data.get('retained_earnings', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['retained_earnings_ratio'] = retained_earnings / total_assets
        
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            ebit = raw_data.get('ebit', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['ebit_ratio'] = ebit / total_assets
        
        # Book value equity / Total Liabilities (instead of market value)
        if data.raw_fmp_data:
            book_value = data.raw_fmp_data.get('book_value_equity', 0)
            total_liabilities = data.raw_fmp_data.get('total_liabilities', 1)
            components['book_equity_ratio'] = book_value / total_liabilities
        else:
            components['book_equity_ratio'] = 0.0
        
        if data.asset_turnover is not None:
            components['asset_turnover'] = data.asset_turnover
        else:
            raw_data = data.raw_fmp_data or {}
            revenue = raw_data.get('revenue', 0)
            total_assets = raw_data.get('total_assets', 1)
            components['asset_turnover'] = revenue / total_assets
        
        # Calculate private Z-Score
        z_score = (
            0.717 * components.get('working_capital_ratio', 0) +
            0.847 * components.get('retained_earnings_ratio', 0) +
            3.107 * components.get('ebit_ratio', 0) +
            0.420 * components.get('book_equity_ratio', 0) +
            0.998 * components.get('asset_turnover', 0)
        )
        
        components['z_score'] = z_score
        return components
    
    def _categorize_risk(self, z_score: float, model: str) -> str:
        """Categorize bankruptcy risk based on Z-Score and model."""
        thresholds = self.risk_thresholds.get(model, self.risk_thresholds["original"])
        
        if z_score >= thresholds["safe"]:
            return "Safe"
        elif z_score >= thresholds["gray"]:
            return "Gray Zone"
        else:
            return "Distress"
    
    def _validate_calculation_data(self, data: MergedFinancialData) -> List[str]:
        """Validate input data and return list of warnings."""
        warnings = []
        
        if not data.raw_fmp_data:
            warnings.append("No raw financial data available - calculation may be incomplete")
        
        if data.working_capital_ratio is None and not data.raw_fmp_data:
            warnings.append("Working capital ratio not available")
        
        if data.ebit_ratio is None and not data.raw_fmp_data:
            warnings.append("EBIT ratio not available")
        
        if data.market_cap is None or data.market_cap <= 0:
            warnings.append("Market data not available - may affect model selection")
        
        return warnings
    
    def calculate_zscore(self, data: MergedFinancialData) -> ZScoreCalculationResult:
        """
        Calculate Z-Score from MergedFinancialData.
        
        Args:
            data: Merged financial data structure
            
        Returns:
            ZScoreCalculationResult with calculation details
        """
        self.logger.info(f"Calculating Z-Score for {data.ticker}")
        
        # Validate input data
        warnings = self._validate_calculation_data(data)
        
        # Select appropriate model
        try:
            model_selection = self.model_selector.select_model(data)
            model_name = model_selection.model_name
            
            self.logger.info(f"Selected {model_name} model for {data.ticker}")
            
        except Exception as e:
            self.logger.warning(f"Model selection failed for {data.ticker}: {e}")
            model_name = "original"  # Default fallback
            warnings.append(f"Using default model due to selection error: {e}")
        
        # Calculate Z-Score based on selected model
        try:
            if model_name == "original":
                components = self._calculate_original_zscore(data)
            elif model_name == "public_service":
                components = self._calculate_service_zscore(data)
            elif model_name == "private":
                components = self._calculate_private_zscore(data)
            else:
                # Default to original for unimplemented models
                self.logger.warning(f"Model {model_name} not fully implemented, using original")
                components = self._calculate_original_zscore(data)
                model_name = "original"
                warnings.append(f"Model {model_name} not implemented, used original instead")
            
            z_score = components['z_score']
            risk_category = self._categorize_risk(z_score, model_name)
              # Calculate data quality score
            data_quality = data.data_quality_score if data.data_quality_score is not None else 0.8
            
            result = ZScoreCalculationResult(
                ticker=data.ticker,
                z_score=z_score,
                model_used=model_name,
                risk_category=risk_category,
                component_values=components,
                calculation_timestamp=datetime.now().isoformat(),
                data_quality_score=data_quality,
                warnings=warnings,
                metadata={
                    "calculation_method": "direct_from_merged_data",
                    "components_calculated": len(components),
                    "model_selection_confidence": getattr(model_selection, 'confidence', 0.8) if 'model_selection' in locals() else 0.8
                }
            )
            
            self.logger.info(f"Z-Score calculation completed for {data.ticker}: {z_score:.3f} ({risk_category})")
            return result
            
        except Exception as e:
            error_msg = f"Z-Score calculation failed for {data.ticker}: {e}"
            self.logger.error(error_msg)
            raise CalculationError(error_msg) from e


async def calculate_zscore_from_merged_data(data: MergedFinancialData) -> ZScoreCalculationResult:
    """
    Async interface for Z-Score calculation.
    
    Args:
        data: Merged financial data structure
        
    Returns:
        ZScoreCalculationResult
    """
    calculator = ZScoreCalculator()
    
    # Run calculation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, calculator.calculate_zscore, data)
