#!/usr/bin/env python3
"""
Retail Z-Score Model Validation Configuration
============================================

Centralized configuration for retail model validation framework.
This module contains all validation settings, company categories, and
configuration parameters used across the validation suite.
"""

from pathlib import Path
from typing import Dict, List

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
PORTFOLIO_FILE = PROJECT_ROOT / "portfolios" / "retail_backtest_portfolio.txt"
VALIDATION_ROOT = PROJECT_ROOT / "retail_validation"
RESULTS_DIR = VALIDATION_ROOT / "results"
SCRIPTS_DIR = VALIDATION_ROOT / "scripts"

# Default validation settings
DEFAULT_OUTPUT_DIR = "retail_validation/results"
DEFAULT_QUARTERS = 4
DEFAULT_YEARS_RANGE = "2015-2025"

# Delisted company handling options
BANKRUPTCY_VALIDATION_APPROACH = "hybrid"  # Options: "historical", "synthetic", "proxy", "hybrid", "standard"
USE_AVAILABLE_TICKERS_ONLY = True  # Skip unavailable tickers without failing
INCLUDE_SYNTHETIC_DATA = False  # Whether to include synthetically generated bankruptcy cases
HISTORICAL_DATA_SOURCE = None  # Set to database connection or None if unavailable
USE_SEC_EDGAR = True  # Use SEC EDGAR as historical data source for delisted companies
SEC_EDGAR_CACHE_DIR = VALIDATION_ROOT / "cache" / "sec_edgar"  # Cache directory for SEC EDGAR data

# Known bankruptcy dates for historical validation
BANKRUPTCY_DATES = {
    'TOY': '2017-09-18',    # Toys"R"Us
    'SHLDQ': '2018-10-15',  # Sears Holdings
    'JCPNQ': '2020-05-15',  # JCPenney
    'NMRCQ': '2020-05-07',  # Neiman Marcus
    'BRKSQ': '2020-07-08',  # Brooks Brothers
    'PIRRQ': '2020-05-18',  # Pier 1 Imports
    'BONTQ': '2018-02-04',  # Bon-Ton Stores
    'RSHCQ': '2015-02-05',  # RadioShack (first bankruptcy)
    'TSAQ': '2016-05-18',   # Sports Authority
    'PSDSQ': '2017-04-04',  # Payless ShoeSource
    'F21Q': '2019-09-29',   # Forever 21
    'GYMQ': '2017-06-11',   # Gymboree (first bankruptcy)
}

# Company categories for validation analysis
# These are used to categorize companies for different validation scenarios
COMPANY_CATEGORIES = {
    'failed': [
        'TOY', 'SHLDQ', 'JCPNQ', 'NMRCQ', 'BRKSQ', 'PIRRQ', 'C21Q', 
        'BONTQ', 'GORDQ', 'HHGQ', 'RSHCQ', 'TSAQ', 'GMTNQ', 'PSDSQ', 
        'BKSQ', 'BYRAQ', 'F21Q', 'CHRLQ', 'DBNQ', 'GYMQ'
    ],
    'distressed': [
        'BBBY', 'PRTY', 'GME', 'EXPR', 'BIG', 'REV', 'M', 'JWN', 
        'DDS', 'BBWI', 'AEO', 'ANF', 'URBN', 'GPS', 'FL'
    ],
    'recovery': [
        'BBY', 'TGT', 'DKS', 'BURL', 'TJX', 'AZO', 'ORLY', 'AAP', 'LOW'
    ],
    'stable': [
        'AMZN', 'COST', 'WMT', 'BJ', 'HD', 'DG', 'DLTR', 'SHW'
    ],
    'seasonal': [
        'SPIR', 'JWN', 'ROST', 'TSCO', 'BGFV', 'SBH', 'POOL', 'BBW', 
        'AM', 'PRTY'
    ]
}

# Validation test configurations
VALIDATION_TESTS = {
    'bankruptcy_prediction': {
        'description': 'Test bankruptcy prediction accuracy',
        'target_categories': ['failed'],
        'success_threshold': 0.80,  # 80% accuracy target
        'risk_zones': ['Distress', 'Gray Zone']
    },
    'early_warning': {
        'description': 'Test early warning detection capability',
        'target_categories': ['distressed'],
        'lead_time_target': 24,  # months
        'sensitivity_threshold': 0.75
    },
    'false_positive': {
        'description': 'Test false positive rates on stable companies',
        'target_categories': ['stable'],
        'max_false_positive_rate': 0.15,  # 15% maximum
        'safe_zone_threshold': 2.99
    },
    'seasonal_stability': {
        'description': 'Test seasonal pattern handling',
        'target_categories': ['seasonal'],
        'max_quarterly_variation': 0.50,  # 50% max variation
        'normalization_effectiveness': 0.30
    },
    'inventory_impact': {
        'description': 'Test inventory component effectiveness',
        'target_categories': ['all'],
        'min_component_impact': 0.10,  # 10% minimum impact
        'high_efficiency_threshold': 0.8,
        'low_efficiency_threshold': 0.5
    }
}

# Model comparison settings
MODEL_COMPARISON = {
    'baseline_models': ['original', 'private'],
    'retail_model': 'retail',
    'metrics': [
        'accuracy',
        'sensitivity',
        'specificity',
        'precision',
        'f1_score',
        'auc_roc'
    ]
}

# Report generation settings
REPORT_CONFIG = {
    'formats': ['markdown', 'json', 'csv'],
    'include_charts': True,
    'include_company_details': True,
    'include_model_comparison': True,
    'academic_format': True
}

# Quick test portfolio for development
QUICK_TEST_COMPANIES = [
    # Stable retailers
    'AMZN', 'COST', 'HD', 'WMT', 'TGT',
    # Distressed retailers (check current status)
    'GME', 'EXPR', 'BIG',
    # E-commerce/Online retail
    'SHOP', 'ETSY',
    # Seasonal/Specialty retail
    'SPIR', 'BBW'
]

def get_category_for_ticker(ticker: str) -> str:
    """
    Determine which category a ticker belongs to.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Category name or 'other' if not found
    """
    for category, tickers in COMPANY_CATEGORIES.items():
        if ticker in tickers:
            return category
    return 'other'

def load_portfolio_tickers(portfolio_file: str = None) -> List[str]:
    """
    Load ticker symbols from portfolio file.
    
    Args:
        portfolio_file: Path to portfolio file (defaults to retail backtest portfolio)
        
    Returns:
        List of ticker symbols
    """
    if portfolio_file is None:
        portfolio_file = PORTFOLIO_FILE
    
    tickers = []
    try:
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Handle potential inline comments
                    ticker = line.split('#')[0].strip()
                    if ticker and len(ticker) <= 10:  # Basic ticker validation
                        tickers.append(ticker)
    except FileNotFoundError:
        print(f"Portfolio file {portfolio_file} not found")
        return []
    
    return tickers

def get_validation_summary() -> Dict:
    """
    Get a summary of validation configuration.
    
    Returns:
        Dictionary with validation summary information
    """
    portfolio_tickers = load_portfolio_tickers()
    
    return {
        'total_companies': len(portfolio_tickers),
        'categories': {
            category: len(tickers) 
            for category, tickers in COMPANY_CATEGORIES.items()
        },
        'validation_tests': len(VALIDATION_TESTS),
        'portfolio_file': str(PORTFOLIO_FILE),
        'results_directory': str(RESULTS_DIR),
        'quick_test_companies': len(QUICK_TEST_COMPANIES)
    }

if __name__ == "__main__":
    # Print configuration summary when run directly
    summary = get_validation_summary()
    print("Retail Z-Score Validation Configuration Summary")
    print("=" * 50)
    print(f"Total Companies: {summary['total_companies']}")
    print(f"Portfolio File: {summary['portfolio_file']}")
    print(f"Results Directory: {summary['results_directory']}")
    print("\nCategory Distribution:")
    for category, count in summary['categories'].items():
        print(f"  {category.capitalize()}: {count} companies")
    print(f"\nValidation Tests: {summary['validation_tests']}")
    print(f"Quick Test Companies: {summary['quick_test_companies']}")
