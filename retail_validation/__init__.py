"""
Retail Z-Score Model Validation Framework
=========================================

Centralized validation framework for the novel retail Z-Score model.
This package provides comprehensive testing, analysis, and reporting
capabilities for academic and production validation.

Modules:
    config.validation_config: Centralized configuration and settings
    scripts.validate_retail_model: Main validation script
"""

__version__ = "2.0.0"
__author__ = "Altman Z-Score Project"
__description__ = "Retail Z-Score Model Validation Framework"

# Import key components for easy access
try:
    from .config.validation_config import (
        get_validation_summary,
        load_portfolio_tickers,
        get_category_for_ticker,
        COMPANY_CATEGORIES,
        VALIDATION_TESTS,
        PORTFOLIO_FILE
    )
    
    __all__ = [
        "get_validation_summary",
        "load_portfolio_tickers", 
        "get_category_for_ticker",
        "COMPANY_CATEGORIES",
        "VALIDATION_TESTS",
        "PORTFOLIO_FILE"
    ]
    
except ImportError:
    # Handle import errors gracefully
    __all__ = []

print(f"Retail Validation Framework v{__version__} loaded")
