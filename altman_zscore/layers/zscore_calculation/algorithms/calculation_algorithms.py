"""
Z-Score Calculation Algorithms

This module contains the specific mathematical algorithms for different
Altman Z-Score models, separated from the main calculator logic.

Key Features:
- Clean separation of calculation algorithms
- Model-specific implementations
- Consistent calculation interfaces
- Easy testing and validation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from dataclasses import dataclass

from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.common.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CalculationResult:
    """Result of a Z-Score calculation algorithm."""
    z_score: float
    component_values: Dict[str, float]
    warnings: list
    metadata: Dict[str, Any]


class ZScoreAlgorithm(ABC):
    """Abstract base class for Z-Score calculation algorithms."""
    
    def __init__(self, model_name: str):
        """Initialize algorithm with model name."""
        self.model_name = model_name
        self.logger = get_logger(f"{self.__class__.__name__}_{model_name}")
    
    @abstractmethod
    def calculate(self, data: MergedFinancialData) -> CalculationResult:
        """
        Calculate Z-Score using this algorithm.
        
        Args:
            data: Merged financial data
            
        Returns:
            Calculation result with Z-Score and components
        """
        pass
    
    @abstractmethod
    def get_required_fields(self) -> list:
        """Get list of required financial data fields."""
        pass
    
    def validate_data(self, data: MergedFinancialData) -> Tuple[bool, list]:
        """
        Validate that required data is available.
        
        Args:
            data: Financial data to validate
            
        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []
        required_fields = self.get_required_fields()
        
        for field in required_fields:
            if not hasattr(data, field) or getattr(data, field) is None:
                warnings.append(f"Missing required field: {field}")
        
        return len(warnings) == 0, warnings


class OriginalAltmanAlgorithm(ZScoreAlgorithm):
    """
    Original Altman Z-Score algorithm for manufacturing companies.
    
    Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets  
    C = EBIT / Total Assets
    D = Market Value Equity / Total Liabilities
    E = Sales / Total Assets
    """
    
    def __init__(self):
        super().__init__("original_altman")
    
    def get_required_fields(self) -> list:
        """Get required fields for original Altman model."""
        return [
            'total_current_assets', 'total_current_liabilities',
            'retained_earnings', 'total_assets',
            'ebit', 'total_liabilities',
            'revenue'
        ]
    
    def calculate(self, data: MergedFinancialData) -> CalculationResult:
        """Calculate original Altman Z-Score."""
        warnings = []
        
        # Validate data
        is_valid, validation_warnings = self.validate_data(data)
        warnings.extend(validation_warnings)
        
        if not is_valid:
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True}
            )
        
        try:
            # Calculate components
            working_capital = data.total_current_assets - data.total_current_liabilities
            
            # Component A: Working Capital / Total Assets
            component_a = working_capital / data.total_assets if data.total_assets != 0 else 0
            
            # Component B: Retained Earnings / Total Assets
            component_b = data.retained_earnings / data.total_assets if data.total_assets != 0 else 0
            
            # Component C: EBIT / Total Assets
            component_c = data.ebit / data.total_assets if data.total_assets != 0 else 0
            
            # Component D: Market Value Equity / Total Liabilities
            market_value_equity = getattr(data, 'market_cap', None)
            if market_value_equity is None:
                # Fallback: Use shares outstanding * price if available
                shares = getattr(data, 'shares_outstanding', None)
                price = getattr(data, 'price', None)
                if shares and price:
                    market_value_equity = shares * price
                else:
                    # Use book value as proxy
                    market_value_equity = getattr(data, 'total_stockholders_equity', data.total_assets - data.total_liabilities)
                    warnings.append("Market value equity not available, using book value as proxy")
            
            component_d = market_value_equity / data.total_liabilities if data.total_liabilities != 0 else 0
            
            # Component E: Sales / Total Assets  
            component_e = data.revenue / data.total_assets if data.total_assets != 0 else 0
            
            # Calculate final Z-Score
            z_score = (1.2 * component_a + 
                      1.4 * component_b + 
                      3.3 * component_c + 
                      0.6 * component_d + 
                      1.0 * component_e)
            
            component_values = {
                'working_capital_ratio': component_a,
                'retained_earnings_ratio': component_b,
                'ebit_ratio': component_c,
                'market_equity_ratio': component_d,
                'asset_turnover': component_e,
                'working_capital': working_capital,
                'market_value_equity': market_value_equity
            }
            
            metadata = {
                'model_coefficients': [1.2, 1.4, 3.3, 0.6, 1.0],
                'component_labels': ['A', 'B', 'C', 'D', 'E'],
                'calculation_method': 'original_altman'
            }
            
            return CalculationResult(
                z_score=z_score,
                component_values=component_values,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            warnings.append(f"Calculation error: {str(e)}")
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True, 'error': str(e)}
            )


class AltmanZPrimeAlgorithm(ZScoreAlgorithm):
    """
    Altman Z' algorithm for non-manufacturing companies.
    
    Z' = 0.717*A + 0.847*B + 3.107*C + 0.420*D + 0.998*E
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Book Value Equity / Total Liabilities
    E = Sales / Total Assets
    """
    
    def __init__(self):
        super().__init__("altman_z_prime")
    
    def get_required_fields(self) -> list:
        """Get required fields for Z' model."""
        return [
            'total_current_assets', 'total_current_liabilities',
            'retained_earnings', 'total_assets',
            'ebit', 'total_liabilities',
            'total_stockholders_equity', 'revenue'
        ]
    
    def calculate(self, data: MergedFinancialData) -> CalculationResult:
        """Calculate Altman Z' Score."""
        warnings = []
        
        # Validate data
        is_valid, validation_warnings = self.validate_data(data)
        warnings.extend(validation_warnings)
        
        if not is_valid:
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True}
            )
        
        try:
            # Calculate components
            working_capital = data.total_current_assets - data.total_current_liabilities
            
            # Component A: Working Capital / Total Assets
            component_a = working_capital / data.total_assets if data.total_assets != 0 else 0
            
            # Component B: Retained Earnings / Total Assets
            component_b = data.retained_earnings / data.total_assets if data.total_assets != 0 else 0
            
            # Component C: EBIT / Total Assets
            component_c = data.ebit / data.total_assets if data.total_assets != 0 else 0
            
            # Component D: Book Value Equity / Total Liabilities (not market value)
            book_value_equity = data.total_stockholders_equity
            component_d = book_value_equity / data.total_liabilities if data.total_liabilities != 0 else 0
            
            # Component E: Sales / Total Assets
            component_e = data.revenue / data.total_assets if data.total_assets != 0 else 0
            
            # Calculate final Z' Score using Z' coefficients
            z_score = (0.717 * component_a + 
                      0.847 * component_b + 
                      3.107 * component_c + 
                      0.420 * component_d + 
                      0.998 * component_e)
            
            component_values = {
                'working_capital_ratio': component_a,
                'retained_earnings_ratio': component_b,
                'ebit_ratio': component_c,
                'book_equity_ratio': component_d,
                'asset_turnover': component_e,
                'working_capital': working_capital,
                'book_value_equity': book_value_equity
            }
            
            metadata = {
                'model_coefficients': [0.717, 0.847, 3.107, 0.420, 0.998],
                'component_labels': ['A', 'B', 'C', 'D', 'E'],
                'calculation_method': 'altman_z_prime'
            }
            
            return CalculationResult(
                z_score=z_score,
                component_values=component_values,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Z' calculation failed: {e}")
            warnings.append(f"Calculation error: {str(e)}")
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True, 'error': str(e)}
            )


class AltmanZDoubleAlgorithm(ZScoreAlgorithm):
    """
    Altman Z'' algorithm for emerging markets and developing companies.
    
    Z'' = 3.25 + 6.56*A + 3.26*B + 6.72*C + 1.05*D
    
    Where:
    A = Working Capital / Total Assets
    B = Retained Earnings / Total Assets
    C = EBIT / Total Assets
    D = Book Value Equity / Total Liabilities
    """
    
    def __init__(self):
        super().__init__("altman_z_double_prime")
    
    def get_required_fields(self) -> list:
        """Get required fields for Z'' model."""
        return [
            'total_current_assets', 'total_current_liabilities',
            'retained_earnings', 'total_assets',
            'ebit', 'total_liabilities',
            'total_stockholders_equity'
        ]
    
    def calculate(self, data: MergedFinancialData) -> CalculationResult:
        """Calculate Altman Z'' Score."""
        warnings = []
        
        # Validate data
        is_valid, validation_warnings = self.validate_data(data)
        warnings.extend(validation_warnings)
        
        if not is_valid:
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True}
            )
        
        try:
            # Calculate components
            working_capital = data.total_current_assets - data.total_current_liabilities
            
            # Component A: Working Capital / Total Assets
            component_a = working_capital / data.total_assets if data.total_assets != 0 else 0
            
            # Component B: Retained Earnings / Total Assets
            component_b = data.retained_earnings / data.total_assets if data.total_assets != 0 else 0
            
            # Component C: EBIT / Total Assets
            component_c = data.ebit / data.total_assets if data.total_assets != 0 else 0
            
            # Component D: Book Value Equity / Total Liabilities
            book_value_equity = data.total_stockholders_equity
            component_d = book_value_equity / data.total_liabilities if data.total_liabilities != 0 else 0
            
            # Calculate final Z'' Score with constant term
            z_score = (3.25 + 
                      6.56 * component_a + 
                      3.26 * component_b + 
                      6.72 * component_c + 
                      1.05 * component_d)
            
            component_values = {
                'working_capital_ratio': component_a,
                'retained_earnings_ratio': component_b,
                'ebit_ratio': component_c,
                'book_equity_ratio': component_d,
                'working_capital': working_capital,
                'book_value_equity': book_value_equity
            }
            
            metadata = {
                'model_coefficients': [6.56, 3.26, 6.72, 1.05],
                'constant_term': 3.25,
                'component_labels': ['A', 'B', 'C', 'D'],
                'calculation_method': 'altman_z_double_prime'
            }
            
            return CalculationResult(
                z_score=z_score,
                component_values=component_values,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Z'' calculation failed: {e}")
            warnings.append(f"Calculation error: {str(e)}")
            return CalculationResult(
                z_score=0.0,
                component_values={},
                warnings=warnings,
                metadata={'calculation_failed': True, 'error': str(e)}
            )


class AlgorithmFactory:
    """Factory for creating Z-Score calculation algorithms."""
    
    _algorithms = {
        'original_altman': OriginalAltmanAlgorithm,
        'altman_z_prime': AltmanZPrimeAlgorithm,
        'altman_z_double_prime': AltmanZDoubleAlgorithm
    }
    
    @classmethod
    def create_algorithm(cls, model_name: str) -> ZScoreAlgorithm:
        """
        Create an algorithm instance for the specified model.
        
        Args:
            model_name: Name of the Z-Score model
            
        Returns:
            Algorithm instance
            
        Raises:
            ValueError: If model name is not supported
        """
        # Normalize model name
        normalized_name = model_name.lower().replace(" ", "_").replace("-", "_").replace("'", "").replace('"', "")
        
        if normalized_name not in cls._algorithms:
            available = list(cls._algorithms.keys())
            raise ValueError(f"Unsupported Z-Score model: {model_name}. Available: {available}")
        
        return cls._algorithms[normalized_name]()
    
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available Z-Score models."""
        return list(cls._algorithms.keys())
    
    @classmethod
    def register_algorithm(cls, model_name: str, algorithm_class: type):
        """
        Register a new algorithm class.
        
        Args:
            model_name: Name for the new model
            algorithm_class: Algorithm class to register
        """
        if not issubclass(algorithm_class, ZScoreAlgorithm):
            raise ValueError("Algorithm class must inherit from ZScoreAlgorithm")
        
        cls._algorithms[model_name] = algorithm_class
