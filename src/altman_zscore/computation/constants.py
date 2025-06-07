"""
Constants and mappings for Altman Z-Score computation in Altman Z-Score analysis.

Defines canonical field mappings, model fields, coefficients, thresholds, aliases, error messages, and other shared constants for all Z-Score model variants.
"""

# constants.py

from decimal import Decimal
from typing import Dict, List

# -------------------------------------------------------------------
# 1) FIELD_MAPPING: Maps canonical field names to possible XBRL/financial statement labels.
# Used for extracting and standardizing raw data fields from various sources.
# -------------------------------------------------------------------
FIELD_MAPPING: Dict[str, List[str]] = {
    'total_assets': [
        'Total Assets',
        'Assets',
        'AssetsTotal'
    ],
    'current_assets': [
        'Current Assets',
        'AssetsCurrent'
    ],
    'current_liabilities': [
        'Current Liabilities',
        'LiabilitiesCurrent'
    ],
    'retained_earnings': [
        'Retained Earnings',
        'RetainedEarnings'
    ],
    'total_liabilities': [
        'Total Liabilities Net Minority Interest',
        'Total Liabilities',
        'Liabilities'
    ],
    'book_value_equity': [
        'Common Stock Equity',
        'Stockholders Equity',
        'Total Equity Gross Minority Interest'
    ],
    'ebit': [
        'EBIT',
        'Operating Income',
        'OperatingIncome'
    ],
    'sales': [
        'Total Revenue',
        'Revenues',
        'Sales',
        'Revenue',
        'Operating Revenue'
    ]
}

# -------------------------------------------------------------------
# 2) MODEL_FIELDS: Lists required canonical fields for each Z-Score model variant.
# Used for validation and computation logic.
# -------------------------------------------------------------------
MODEL_FIELDS: Dict[str, List[str]] = {
    # 2.1 Public manufacturing (Original Z-Score, five-ratio)
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
    # 2.2 Private manufacturing (Z′-Score, five-ratio)
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
    # 2.3 Public non-manufacturing (Zʺ-Public, four-ratio)
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
    # 2.4 Private non-manufacturing (Zʺ-Private, four-ratio)
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
    # 2.5 Tech (alias for public non-manufacturing; Zʺ-Public weights)
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
    # 2.6 Emerging Markets (Z_EM, four-ratio + intercept, uses book equity)
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
    # (Optional: Any `sic_<code>` overrides can be added here if required)
}

# -------------------------------------------------------------------
# 3) MODEL_COEFFICIENTS: Coefficient weights for each Z-Score model variant.
# Keys A-E correspond to X1-X5 ratios in the Altman Z-Score formula.
# For EM, 'A' is the intercept.
# -------------------------------------------------------------------
MODEL_COEFFICIENTS: Dict[str, Dict[str, Decimal]] = {
    # 3.1 Original Z-Score (1968, Public Manufacturing, 5-ratio)
    "original": {
        "A": Decimal("1.20"),   # X1 = (Current Assets - Current Liabilities) / Total Assets
        "B": Decimal("1.40"),   # X2 = Retained Earnings / Total Assets
        "C": Decimal("3.30"),   # X3 = EBIT / Total Assets
        "D": Decimal("0.60"),   # X4 = Market Value of Equity / Total Liabilities
        "E": Decimal("1.00"),   # X5 = Sales / Total Assets
    },
    # 3.2 Z′-Score (1983, Private Manufacturing, 5-ratio)
    "private": {
        "A": Decimal("0.717"),  # X1 = (Current Assets - Current Liabilities) / Total Assets
        "B": Decimal("0.847"),  # X2 = Retained Earnings / Total Assets
        "C": Decimal("3.107"),  # X3 = EBIT / Total Assets
        "D": Decimal("0.420"),  # X4 = Book Value of Equity / Total Liabilities
        "E": Decimal("0.998"),  # X5 = Sales / Total Assets
    },
    # 3.3 Zʺ-Public (1995, Public Non-Manufacturing, 4-ratio)
    "service": {
        "A": Decimal("6.56"),   # X1 = (Current Assets - Current Liabilities) / Total Assets
        "B": Decimal("3.26"),   # X2 = Retained Earnings / Total Assets
        "C": Decimal("6.72"),   # X3 = EBIT / Total Assets
        "D": Decimal("1.05"),   # X4 = Market Value of Equity / Total Liabilities
        "E": Decimal("0.00"),   # (unused in 4-ratio)
    },
    # 3.4 Zʺ-Private (1995, Private Non-Manufacturing, 4-ratio)
    "service_private": {
        "A": Decimal("6.56"),   # X1 = (Current Assets - Current Liabilities) / Total Assets
        "B": Decimal("3.26"),   # X2 = Retained Earnings / Total Assets
        "C": Decimal("6.72"),   # X3 = EBIT / Total Assets
        "D": Decimal("1.05"),   # X4 = Book Value of Equity / Total Liabilities
        "E": Decimal("0.00"),   # (unused in 4-ratio)
    },
    # 3.5 Tech (alias for Zʺ-Public; identical coefficients)
    "tech": {
        "A": Decimal("6.56"),
        "B": Decimal("3.26"),
        "C": Decimal("6.72"),
        "D": Decimal("1.05"),
        "E": Decimal("0.00"),
    },
    # 3.6 Z_EM-Score (1995 EM-Adjusted, four-ratio + 3.25 intercept, book equity)
    "em": {
        "A": Decimal("3.25"),   # intercept
        "B": Decimal("6.56"),   # X1 weight
        "C": Decimal("3.26"),   # X2 weight
        "D": Decimal("6.72"),   # X3 weight
        "E": Decimal("1.05"),   # X4 weight (BVE/TL)
    },
    # (Optional: Add any `sic_<code>` overrides below)
}

# -------------------------------------------------------------------
# 4) Z_SCORE_THRESHOLDS: Distress, Grey, and Safe cutoffs for each model.
# Used to interpret the computed Z-Score.
# -------------------------------------------------------------------
Z_SCORE_THRESHOLDS: Dict[str, Dict[str, Decimal]] = {
    # 4.1 Original Z-Score (1968, Public Manufacturing)
    "original": {
        "safe": Decimal("2.99"),
        "grey": Decimal("1.81"),
        "distress": Decimal("1.81"),
    },
    # 4.2 Z′-Score (1983, Private Manufacturing)
    "private": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
    # 4.3 Zʺ-Public (1995, Public Non-Manufacturing)
    "service": {
        "safe": Decimal("2.90"),
        "grey": Decimal("1.23"),
        "distress": Decimal("1.23"),
    },
    # 4.4 Zʺ-Private (1995, Private Non-Manufacturing)
    "service_private": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
    # 4.5 Tech (alias for Zʺ-Public)
    "tech": {
        "safe": Decimal("2.90"),
        "grey": Decimal("1.23"),
        "distress": Decimal("1.23"),
    },
    # 4.6 Z_EM-Score (1995 EM-Adjusted)
    "em": {
        "safe": Decimal("2.60"),
        "grey": Decimal("1.10"),
        "distress": Decimal("1.10"),
    },
    # (Optional: Add any `sic_<code>` overrides below)
}

# -------------------------------------------------------------------
# 5) MODEL_ALIASES: Maps legacy or alternative model keys to canonical keys.
# Ensures backward compatibility and normalization of model selection.
# -------------------------------------------------------------------
MODEL_ALIASES: Dict[str, str] = {
    "public_service": "service",      # alias → service
    "private_mfg": "private",         # alias → private
    "emerging": "em",                 # alias → em
    "public": "service",              # alias → service
    # (If needed, you can add more aliases here)
}

# -------------------------------------------------------------------
# 6) EMERGING_MARKETS: List of country codes considered 'emerging markets'.
# Used for model selection and reporting.
# -------------------------------------------------------------------
EMERGING_MARKETS: List[str] = [
    "ID", "TR", "PL", "TH", "PH", "EG", "NG", "PK", "VN", "AR", "CO", "MY", "CL", "PE"
]

# -------------------------------------------------------------------
# 7) CALIBRATION_UPDATE: Metadata for the latest model coefficient update.
# Used for auditability and transparency in model versioning.
# -------------------------------------------------------------------
CALIBRATION_UPDATE: Dict[str, str] = {
    "last_update": "2025-05-29",
    "update_notes": "Initial v2.4 canonical key structure. All weights validated against Altman literature.",
    "update_source": "SEC EDGAR / Compustat / Salomon Smith Barney (1995 EM publication).",
}

# -------------------------------------------------------------------
# 8) ERROR MESSAGES: Centralized error message strings for DRY compliance.
# Used throughout the pipeline for consistent error reporting.
# -------------------------------------------------------------------
ERROR_MSG_TICKER_NOT_FOUND = "Ticker not found in Yahoo Finance"
ERROR_MSG_SYMBOL_NOT_FOUND = "Ticker symbol not found in Yahoo Finance"
ERROR_MSG_DELISTED = "Delisted according to Yahoo Finance"
ERROR_MSG_NO_TRADING = "No recent trading data available"
ERROR_MSG_KNOWN_BANKRUPTCY = "Known bankruptcy case (filed on {date})"
ERROR_MSG_COMPANY_NOT_FOUND_SEC = "Company not found in SEC EDGAR database"
ERROR_MSG_ERROR_RETRIEVING = "Error retrieving data: {error}"
ERROR_MSG_ALL_FIELDS_MISSING = "All required fields are missing or zero (possible empty or placeholder quarter)"
ERROR_MSG_MISSING_FIELD = "Missing required field: {field}"
ERROR_MSG_NEGATIVE_ASSETS = "Total assets is negative (suspicious)"
ERROR_MSG_NEGATIVE_SALES = "Sales is negative (suspicious)"
ERROR_MSG_LIABILITIES_RATIO = "Total liabilities > 10x total assets (possible data error)"
ERROR_MSG_STATUS_CHECK_FAILED = "Company status check failed"

# -------------------------------------------------------------------
# 9) STATUS MESSAGE TEMPLATES: Centralized user-facing status messages for DRY compliance.
# Used for reporting company status to users.
# -------------------------------------------------------------------
STATUS_MSG_BANKRUPT = "{ticker} has filed for bankruptcy{bankruptcy_info}."
STATUS_MSG_DELISTED = "{ticker} has been delisted{delisting_info}."
STATUS_MSG_NOT_FOUND = "The ticker '{ticker}' does not appear to exist."
STATUS_MSG_INACTIVE = "{ticker} exists but is not currently active. {status_reason}"
STATUS_MSG_ACTIVE = "{ticker} appears to be an active company."

# -------------------------------------------------------------------
# 10) FIELD_SYNONYMS: Maps alternate field names to canonical field names for DRY compliance.
# Used to standardize field names from various data sources.
# -------------------------------------------------------------------
FIELD_SYNONYMS: Dict[str, str] = {
    # Assets
    "Assets": "total_assets",
    "Total Assets": "total_assets",
    "AssetsTotal": "total_assets",
    # Current Assets
    "Current Assets": "current_assets",
    "AssetsCurrent": "current_assets",
    # Current Liabilities
    "Current Liabilities": "current_liabilities",
    "LiabilitiesCurrent": "current_liabilities",
    # Retained Earnings
    "Retained Earnings": "retained_earnings",
    "RetainedEarnings": "retained_earnings",
    # Total Liabilities
    "Total Liabilities Net Minority Interest": "total_liabilities",
    "Total Liabilities": "total_liabilities",
    "Liabilities": "total_liabilities",
    # Book Value Equity
    "Common Stock Equity": "book_value_equity",
    "Stockholders Equity": "book_value_equity",
    "Total Equity Gross Minority Interest": "book_value_equity",
    # EBIT
    "EBIT": "ebit",
    "Operating Income": "ebit",
    "OperatingIncome": "ebit",
    # Sales/Revenue
    "Total Revenue": "sales",
    "Revenues": "sales",
    "Sales": "sales",
    "Revenue": "sales",
    "Operating Revenue": "sales",
    # Market Value Equity (if used)
    "Market Value of Equity": "market_value_equity",
    # Add more synonyms as needed for new data sources or edge cases
}

