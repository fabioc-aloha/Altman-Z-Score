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

    @abstractmethod
    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the Z-Score for given financial data"""

    @abstractmethod
    def interpret_score(self, score: Decimal) -> str:
        """Interpret the calculated Z-Score"""
