"""
Z-Score Calculation Layer

This layer handles the calculation of Altman Z-Scores from integrated financial data.
Integrates with existing Z-Score models and provides automatic model selection.

Modules:
- zscore_calculator.py: Main Z-Score calculation engine
- model_selector.py: Automatic model selection based on company characteristics
- validation.py: Z-Score result validation and sanity checks
"""

from .zscore_calculator import ZScoreCalculator, ZScoreCalculationResult, calculate_zscore_from_merged_data
from .model_selector import ModelSelector, select_appropriate_model

__all__ = [
    'ZScoreCalculator',
    'ZScoreCalculationResult',
    'calculate_zscore_from_merged_data',
    'ModelSelector', 
    'select_appropriate_model'
]

__version__ = "1.0.0"
