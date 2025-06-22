"""
Constants and mappings for Altman Z-Score computation in Altman Z-Score analysis.

References:
1. Altman, E.I. (1968) "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy"
2. Altman, E.I. (1983) "Corporate Financial Distress: A Complete Guide to Predicting, Avoiding, and Dealing with Bankruptcy"
3. Altman, E.I. (2002) "Revisiting Credit Scoring Models in a Basel 2 Environment"
4. Altman, E.I. (2005) "An emerging market credit scoring system for corporate bonds"
"""

# constants.py

from decimal import Decimal
from typing import Dict, List

# -------------------------------------------------------------------
# 1) MODEL_FIELDS: Lists required canonical fields for each Z-Score model variant.
# -------------------------------------------------------------------
MODEL_FIELDS: Dict[str, List[str]] = {
    # 1.1 Original Z-Score (Manufacturing)
    "original": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "market_value_equity",
        "ebit",
        "sales",
    ],
    
    # 1.2 Private Company Model (Z′-Score)
    "private": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "book_value_equity",
        "ebit",
        "sales",
    ],
    
    # 1.3 Non-Manufacturing/Service Model (Zʺ-Score)
    "service": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "market_value_equity",
        "ebit",
    ],
      # 1.4 Emerging Markets Model
    "em": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "book_value_equity",
        "ebit",
        "sales",
    ],
    
    # 1.5 Retail Model
    "retail": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "market_value_equity",
        "ebit",
        "sales",
        "inventory",
        "cost_of_goods_sold",
        "average_inventory",
    ]
}

# -------------------------------------------------------------------
# 2) MODEL_COEFFICIENTS: Literature-based coefficient weights
# -------------------------------------------------------------------
MODEL_COEFFICIENTS: Dict[str, Dict[str, Decimal]] = {
    # 2.1 Original Z-Score (1968, Public Manufacturing)
    # Altman (1968) - Original paper coefficients
    "original": {
        "X1": Decimal("1.2"),   # Working Capital/Total Assets
        "X2": Decimal("1.4"),   # Retained Earnings/Total Assets
        "X3": Decimal("3.3"),   # EBIT/Total Assets        
        "X4": Decimal("0.6"),   # Market Value of Equity/Total Liabilities
        "X5": Decimal("1.0"),   # Sales/Total Assets
    },
    
    # 2.2 Z′-Score (Private Manufacturing)
    # Altman (1983) - Private firm modification
    "private": {
        "X1": Decimal("0.717"), # Working Capital/Total Assets
        "X2": Decimal("0.847"), # Retained Earnings/Total Assets
        "X3": Decimal("3.107"), # EBIT/Total Assets
        "X4": Decimal("0.420"), # Book Value of Equity/Total Liabilities
        "X5": Decimal("0.998"), # Sales/Total Assets
    },
    
    # 2.3 Zʺ-Score (Non-Manufacturing)
    # Altman (2002) - Service sector adaptation
    "service": {
        "X1": Decimal("6.56"),  # Working Capital/Total Assets
        "X2": Decimal("3.26"),  # Retained Earnings/Total Assets
        "X3": Decimal("6.72"),  # EBIT/Total Assets        
        "X4": Decimal("1.05"),  # Book Value of Equity/Total Liabilities
    },
      
    # 2.4 Emerging Markets Model
    # Altman (2005) - EM Score
    "em": {
        "X1": Decimal("6.56"),  # Working Capital/Total Assets
        "X2": Decimal("3.26"),  # Retained Earnings/Total Assets
        "X3": Decimal("6.72"),  # EBIT/Total Assets
        "X4": Decimal("1.05"),  # Book Value of Equity/Total Liabilities
        "X5": Decimal("3.25"),  # Sales/Total Assets
    },
    
    # 2.5 Retail Model
    # Based on retail industry adaptations
    "retail": {
        "X1": Decimal("1.10"),  # Quick Ratio ((Current Assets - Inventory)/Current Liabilities)
        "X2": Decimal("1.40"),  # Retained Earnings/Total Assets
        "X3": Decimal("3.30"),  # EBIT/Total Assets
        "X4": Decimal("0.60"),  # Market Value of Equity/Total Liabilities
        "X5": Decimal("1.20"),  # Sales/Total Assets
        "X6": Decimal("0.30"),  # Inventory Turnover
    }
}

# -------------------------------------------------------------------
# 3) MODEL_THRESHOLDS: Literature-based classification thresholds
# -------------------------------------------------------------------
Z_SCORE_THRESHOLDS: Dict[str, Dict[str, Decimal]] = {
    # Original Z-Score thresholds (1968)
    "original": {
        "DISTRESS": Decimal("1.81"),    # Z < 1.81: High probability of bankruptcy
        "SAFE": Decimal("2.99"),        # Z > 2.99: Safe zone
    },
    
    # Private Company Model thresholds (1983)
    "private": {
        "DISTRESS": Decimal("1.23"),    # Z' < 1.23: High probability of bankruptcy
        "SAFE": Decimal("2.90"),        # Z' > 2.90: Safe zone
    },
    
    # Non-Manufacturing/Service Model thresholds (2002)
    "service": {
        "DISTRESS": Decimal("1.10"),    # Z" < 1.10: High probability of bankruptcy
        "SAFE": Decimal("2.60"),        # Z" > 2.60: Safe zone
    },
    
    # Emerging Markets Model thresholds (2005)
    "em": {
        "DISTRESS": Decimal("1.10"),    # EM < 1.10: High probability of default
        "SAFE": Decimal("2.60"),        # EM > 2.60: Safe zone
    },
    
    # Retail Model thresholds (industry-adjusted)
    "retail": {
        "DISTRESS": Decimal("1.90"),    # Modified for retail industry characteristics
        "SAFE": Decimal("3.10"),        # Safe zone
    }
}

# Maintain aliases for backward compatibility
MODEL_COEFFICIENTS["service_private"] = MODEL_COEFFICIENTS["private"]
MODEL_COEFFICIENTS["tech"] = MODEL_COEFFICIENTS["service"]
Z_SCORE_THRESHOLDS["service_private"] = Z_SCORE_THRESHOLDS["private"]
Z_SCORE_THRESHOLDS["tech"] = Z_SCORE_THRESHOLDS["service"]

# -------------------------------------------------------------------
# 4) MODEL_ALIASES: Maps legacy or alternative model keys to canonical keys.
# -------------------------------------------------------------------
MODEL_ALIASES: Dict[str, str] = {
    "public_service": "service",      # alias → service (keep service for legacy compatibility)
    "private_mfg": "private",         # alias → private
    "public_mfg": "original",         # alias → original
    "manufacturing": "original",      # alias → original
    "non_manufacturing": "service",   # alias → service
    # "service": "em",                # removed erroneous mapping; service remains canonical
    "emerging": "em",                 # emerging → em
    "tech": "service",               # alias tech → service model
}

# -------------------------------------------------------------------
# 5) STATUS MESSAGES: Standardized status messages for company status checks
# -------------------------------------------------------------------
STATUS_MSG_BANKRUPT = "{ticker} is bankrupt{bankruptcy_info}"
STATUS_MSG_DELISTED = "{ticker} has been delisted{delisting_info}"
STATUS_MSG_NOT_FOUND = "{ticker} not found"
STATUS_MSG_INACTIVE = "{ticker} is not active (reason: {status_reason})"
STATUS_MSG_ACTIVE = "{ticker} is active and trading"

# -------------------------------------------------------------------
# 3) ERROR MESSAGES: Standardized error messages for various conditions
# -------------------------------------------------------------------
ERROR_MSG_TICKER_NOT_FOUND = "Ticker symbol not found"
ERROR_MSG_SYMBOL_NOT_FOUND = "Symbol not found in Yahoo Finance database"
ERROR_MSG_DELISTED = "Company has been delisted"
ERROR_MSG_NO_TRADING = "No recent trading activity found"
ERROR_MSG_KNOWN_BANKRUPTCY = "Company is known to be bankrupt"
ERROR_MSG_COMPANY_NOT_FOUND_SEC = "Company not found in SEC database"
ERROR_MSG_ERROR_RETRIEVING = "Error retrieving company data"
ERROR_MSG_STATUS_CHECK_FAILED = "Failed to check company status"

# Error messages for data validation
ERROR_MSG_ALL_FIELDS_MISSING = "All required fields are missing"
ERROR_MSG_SOME_FIELDS_MISSING = "Some required fields are missing"
ERROR_MSG_MISSING_FIELD = "Required field {} is missing"
ERROR_MSG_INVALID_VALUE = "Invalid value for field {}"
ERROR_MSG_NEGATIVE_ASSETS = "Total assets cannot be negative"
ERROR_MSG_ZERO_ASSETS = "Total assets cannot be zero"
ERROR_MSG_NEGATIVE_LIABILITIES = "Total liabilities cannot be negative"
ERROR_MSG_NEGATIVE_EQUITY = "Equity cannot be negative"
ERROR_MSG_NEGATIVE_SALES = "Sales cannot be negative"
ERROR_MSG_NEGATIVE_EBIT = "EBIT cannot be negative"
ERROR_MSG_NEGATIVE_WORKING_CAPITAL = "Working capital cannot be negative"
ERROR_MSG_DATA_CONSISTENCY = "Data consistency check failed"
ERROR_MSG_VALIDATION_FAILED = "Validation failed: {}"
ERROR_MSG_COMPUTATION_FAILED = "Z-Score computation failed: {}"
ERROR_MSG_QUARTERLY_DATA_MISSING = "No quarterly data available"
ERROR_MSG_FIELD_TYPE_MISMATCH = "Field type mismatch for {}"
ERROR_MSG_FIELD_RANGE_ERROR = "Value out of valid range for {}"
ERROR_MSG_LIABILITIES_RATIO = "Total liabilities cannot exceed total assets"
ERROR_MSG_EQUITY_CALCULATION = "Equity calculation failed: assets - liabilities mismatch"
ERROR_MSG_WORKING_CAPITAL_RATIO = "Working capital ratio outside valid range"
ERROR_MSG_RETAINED_EARNINGS_RATIO = "Retained earnings ratio outside valid range"
ERROR_MSG_EBIT_MARGIN = "EBIT margin outside valid range"
ERROR_MSG_MARKET_CAP_RATIO = "Market cap to liabilities ratio outside valid range"
ERROR_MSG_ASSET_TURNOVER = "Asset turnover ratio outside valid range"

