"""
zscore_model_base.py
--------------------
Abstract base class for Z-Score models.

This module defines the abstract base class for Z-Score models, specifying the required
interface for model implementations (calculation and interpretation methods).

Classes:
    ZScoreModel: Abstract base class for Z-Score models.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

class ZScoreModel(ABC):
    """
    Abstract base class for Z-Score models.

    Methods:
        calculate_zscore(financial_data): Calculate the Z-Score for given financial data.
        interpret_score(score): Interpret the calculated Z-Score.
    """

    @classmethod
    def validate_data(cls, financial_data: Dict) -> Dict:
        """
        Validate financial data for this model type.
        
        Args:
            financial_data: Dictionary containing financial metrics
            
        Returns:
            Dict: Validated financial data
            
        Raises:
            ValueError: If validation fails
        """
        from .model_validators import validate_financial_data
        return validate_financial_data(cls.__name__.lower(), financial_data)

    @abstractmethod
    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the Z-Score for given financial data"""

    @abstractmethod
    def interpret_score(self, score: Decimal) -> str:
        """Interpret the calculated Z-Score"""

    def _calculate_zscore_impl(self, financial_data: Dict) -> Decimal:
        """
        Implementation of Z-Score calculation with validated data.
        """
