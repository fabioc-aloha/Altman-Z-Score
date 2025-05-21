"""Altman Z-Score analysis package."""

from .compute_zscore import FinancialMetrics, ZScoreCalculator
from .config import PORTFOLIO, ZSCORE_PARAMS, ZSCORE_THRESHOLDS

__all__ = [
    'FinancialMetrics',
    'ZScoreCalculator',
    'PORTFOLIO',
    'ZSCORE_PARAMS',
    'ZSCORE_THRESHOLDS',
]