"""
Abstract base class for Z-Score models.
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

class ZScoreModel(ABC):
    """Abstract base class for Z-Score models"""

    @abstractmethod
    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the Z-Score for given financial data"""

    @abstractmethod
    def interpret_score(self, score: Decimal) -> str:
        """Interpret the calculated Z-Score"""
