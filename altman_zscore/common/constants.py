"""
Constants and configuration for the Altman Z-Score package.

This module contains centralized constants, configuration settings,
and other static data used across the package.
"""

# Directory and file paths
DEFAULT_CACHE_DIR = ".cache"
OUTPUT_DIR = "output"
FIELD_MAPPING_CACHE_PATH = "altman_zscore/cache/field_mapping_cache.json"
FIELD_MAPPING_METADATA_PATH = "altman_zscore/cache/field_mapping_metadata.json"
CIK_CACHE_PATH = ".cache/cik_cache.json"

# API-related constants
SEC_EDGAR_BASE_URL = "https://data.sec.gov/api"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
YAHOO_FINANCE_BASE_URL = "https://query2.finance.yahoo.com/v8/finance"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Rate limiting settings
API_RATE_LIMITS = {
    "sec.gov": 0.1,           # 10 requests per second (100ms between requests)
    "finance.yahoo.com": 0.5,  # 2 requests per second (500ms between requests)
    "finnhub.io": 1.0,         # 1 request per second
    "openai.azure.com": 1.0,   # 1 request per second
    "default": 1.0             # Default for any other domain
}

# Cache settings
CACHE_TTL_DAYS = 30           # Default cache time-to-live in days
CIK_CACHE_TTL_DAYS = 30       # CIK cache time-to-live in days

# Date formats
ISO_DATE_FORMAT = "%Y-%m-%d"
SEC_DATE_FORMAT = "%Y-%m-%d"
YAHOO_DATE_FORMAT = "%Y-%m-%d"

# Z-Score model constants
ZSCORE_MODELS = {
    "original": {
        "name": "Original Z-Score",
        "coefficients": {
            "X1": 1.2,
            "X2": 1.4,
            "X3": 3.3,
            "X4": 0.6,
            "X5": 1.0
        },
        "thresholds": {
            "safe": 2.99,
            "grey_upper": 2.99,
            "grey_lower": 1.81,
            "distress": 1.81
        },
        "description": "Original Altman Z-Score (1968) for public manufacturing companies"
    },
    "private": {
        "name": "Private Company Z'-Score",
        "coefficients": {
            "X1": 0.717,
            "X2": 0.847,
            "X3": 3.107,
            "X4": 0.420,
            "X5": 0.998
        },
        "thresholds": {
            "safe": 2.9,
            "grey_upper": 2.9,
            "grey_lower": 1.23,
            "distress": 1.23
        },
        "description": "Modified Z'-Score for private manufacturing companies"
    },
    "service": {
        "name": "Service/Non-Manufacturing Z''-Score",
        "coefficients": {
            "X1": 6.56,
            "X2": 3.26,
            "X3": 6.72,
            "X4": 1.05
        },
        "thresholds": {
            "safe": 2.6,
            "grey_upper": 2.6,
            "grey_lower": 1.1,
            "distress": 1.1
        },
        "description": "Service and non-manufacturing Z''-Score (no constant)"
    },
    "emerging": {
        "name": "Emerging Markets Z''-Score",
        "coefficients": {
            "X1": 6.56,
            "X2": 3.26,
            "X3": 6.72,
            "X4": 1.05,
            "constant": 3.25
        },
        "thresholds": {
            "safe": 2.6,
            "grey_upper": 2.6,
            "grey_lower": 1.1,
            "distress": 1.1
        },
        "description": "Emerging Markets Z''-Score (with +3.25 constant)"
    },
    "financial": {
        "name": "Financial Institutions Z-Score",
        "coefficients": {
            "X1": 6.56,
            "X2": 3.26,
            "X3": 6.72,
            "X4": 1.05,
            "constant": 3.25
        },
        "thresholds": {
            "safe": 2.6,
            "grey_upper": 2.6,
            "grey_lower": 1.1,
            "distress": 1.1
        },
        "description": "Modified Z-Score for financial institutions"
    },
    "retail": {
        "name": "Retail Industry Model",
        "coefficients": {
            "X1": 1.2,
            "X2": 1.4,
            "X3": 3.3,
            "X4": 0.6,
            "X5": 1.0,
            "X6": 0.5  # Inventory turnover adjustment
        },
        "thresholds": {
            "safe": 2.99,
            "grey_upper": 2.99,
            "grey_lower": 1.81,
            "distress": 1.81
        },
        "description": "Modified Z-Score for retail companies with inventory focus"
    }
}

# SIC code ranges for industry categorization
SIC_CODE_RANGES = {
    "financial": [(6000, 6999)],  # Financial sector
    "retail": [(5200, 5999)],     # Retail trade
    "manufacturing": [(2000, 3999)],  # Manufacturing
    "service": [(7000, 8999)]     # Services
}

# Default settings
DEFAULT_MODEL = "original"
DEFAULT_START_DATE = "2022-01-01"
MINIMUM_QUARTERS_REQUIRED = 4

# This file will be expanded during refactoring with additional constants
