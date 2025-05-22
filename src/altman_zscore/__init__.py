"""Altman Z-Score analysis package for financial health assessment.

This package provides modules for Z-Score analysis but is NOT the main entry point.
Users should run analyze.py in the root directory instead.

Package Components:
- compute_zscore: Core Z-Score calculation logic
- fetch_financials: SEC EDGAR data retrieval
- fetch_prices: Market data retrieval
- industry_classifier: Company classification
- config: Configuration and constants
- models: Z-Score model variants
- api: API integration components
- cache: Caching mechanisms
- schemas: Data validation schemas
- utils: Helper utilities

The main analysis pipeline (analyze.py) coordinates these components to:
1. Set up the environment
2. Manage data caching
3. Fetch required data
4. Perform calculations
5. Generate reports

See the README.md for usage instructions and documentation.
"""

from .compute_zscore import FinancialMetrics, ZScoreCalculator
from .config import PORTFOLIO, ZSCORE_MODELS, DEFAULT_ZSCORE_MODEL

__all__ = [
    'FinancialMetrics',
    'ZScoreCalculator',
    'PORTFOLIO',
    'ZSCORE_MODELS',
    'DEFAULT_ZSCORE_MODEL',
]