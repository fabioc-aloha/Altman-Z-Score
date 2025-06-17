"""
Constants and mappings for Altman Z-Score computation in Altman Z-Score analysis.
Currently limited to U.S.-based companies only.

Defines canonical field mappings, model fields, coefficients, thresholds, aliases, error messages, 
and other shared constants for all Z-Score model variants.
"""

# constants.py

from decimal import Decimal
from typing import Dict, List

# -------------------------------------------------------------------
# 1) MODEL_FIELDS: Lists required canonical fields for each Z-Score model variant.
# -------------------------------------------------------------------
MODEL_FIELDS: Dict[str, List[str]] = {
    # 1.1 Public manufacturing (Original Z-Score, five-ratio)
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
    # 1.2 Private manufacturing (Z′-Score, five-ratio)
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
    # 1.3 Public non-manufacturing (Zʺ-Public, four-ratio)
    "service": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "market_value_equity",
        "ebit",
        "sales",
    ],
    # 1.4 Private non-manufacturing (Zʺ-Private, four-ratio)
    "service_private": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "book_value_equity",
        "ebit",
        "sales",
    ],
    # 1.5 Tech (alias for public non-manufacturing; Zʺ-Public weights)
    "tech": [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "total_liabilities",
        "market_value_equity",
        "ebit",
        "sales",
    ],
    # (Optional: Any `sic_<code>` overrides can be added here if required)
}

# -------------------------------------------------------------------
# 2) MODEL_COEFFICIENTS: Coefficient weights for each Z-Score model variant.
# -------------------------------------------------------------------
MODEL_COEFFICIENTS: Dict[str, Dict[str, Decimal]] = {
    # 2.1 Original Z-Score (1968, Public Manufacturing, 5-ratio)
    "original": {
        "X1": Decimal("1.2"),  # Working Capital/Total Assets
        "X2": Decimal("1.4"),  # Retained Earnings/Total Assets
        "X3": Decimal("3.3"),  # EBIT/Total Assets
        "X4": Decimal("0.6"),  # Market Value of Equity/Total Liabilities
        "X5": Decimal("1.0"),  # Sales/Total Assets
    },
    # 2.2 Z′-Score (Private Manufacturing)
    "private": {
        "X1": Decimal("0.717"),  # Working Capital/Total Assets
        "X2": Decimal("0.847"),  # Retained Earnings/Total Assets
        "X3": Decimal("3.107"),  # EBIT/Total Assets
        "X4": Decimal("0.420"),  # Book Value of Equity/Total Liabilities
        "X5": Decimal("0.998"),  # Sales/Total Assets
    },
    # 2.3 Zʺ-Score (Non-Manufacturing)
    "service": {
        "X1": Decimal("6.56"),   # Working Capital/Total Assets
        "X2": Decimal("3.26"),   # Retained Earnings/Total Assets
        "X3": Decimal("6.72"),   # EBIT/Total Assets
        "X4": Decimal("1.05"),   # Market Value of Equity/Total Liabilities
    },
    # 2.4 Zʺ-Private (Private Non-Manufacturing)
    "service_private": {
        "X1": Decimal("6.56"),   # Working Capital/Total Assets
        "X2": Decimal("3.26"),   # Retained Earnings/Total Assets
        "X3": Decimal("6.72"),   # EBIT/Total Assets
        "X4": Decimal("1.05"),   # Book Value of Equity/Total Liabilities
    },
    # Tech is an alias for service (uses same coefficients)
    "tech": {
        "X1": Decimal("6.56"),   # Working Capital/Total Assets
        "X2": Decimal("3.26"),   # Retained Earnings/Total Assets
        "X3": Decimal("6.72"),   # EBIT/Total Assets
        "X4": Decimal("1.05"),   # Market Value of Equity/Total Liabilities
    },
}

# -------------------------------------------------------------------
# 3) Z_SCORE_THRESHOLDS: Distress, Grey, and Safe cutoffs for each model.
# -------------------------------------------------------------------
Z_SCORE_THRESHOLDS: Dict[str, Dict[str, Decimal]] = {
    # 3.1 Original Z-Score (1968, Public Manufacturing)
    "original": {
        "safe": Decimal("2.99"),
        "grey": Decimal("1.81"),
        "distress": Decimal("1.81"),
    },
    # 3.2 Z′-Score (Private Manufacturing)
    "private": {
        "safe": Decimal("2.90"),
        "grey": Decimal("1.23"),
        "distress": Decimal("1.23"),
    },
    # 3.3 Zʺ-Score (Non-Manufacturing)
    "service": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
    # 3.4 Zʺ-Private (Private Non-Manufacturing)
    "service_private": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
    # Tech uses same thresholds as service
    "tech": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
}

# -------------------------------------------------------------------
# 4) MODEL_ALIASES: Maps legacy or alternative model keys to canonical keys.
# -------------------------------------------------------------------
MODEL_ALIASES: Dict[str, str] = {
    "public_service": "service",      # alias → service
    "private_mfg": "private",         # alias → private
    "public_mfg": "original",         # alias → original
    "manufacturing": "original",      # alias → original
    "non_manufacturing": "service",   # alias → service
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

