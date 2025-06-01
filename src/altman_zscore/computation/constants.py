# constants.py

from decimal import Decimal
from typing import Dict, List

# -------------------------------------------------------------------
# 1) FIELD_MAPPING: Possible XBRL labels for each canonical field name.
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
# 2) MODEL_FIELDS: Required fields (canonical names) for each model key.
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
# 3) MODEL_COEFFICIENTS: Weights (and intercept for EM) for each model.
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
# 5) MODEL_ALIASES: Map legacy or alternative keys to canonical keys.
# -------------------------------------------------------------------
MODEL_ALIASES: Dict[str, str] = {
    "public_service": "service",      # alias → service
    "private_mfg": "private",         # alias → private
    "emerging": "em",                 # alias → em
    "public": "service",              # alias → service
    # (If needed, you can add more aliases here)
}

# -------------------------------------------------------------------
# 6) EMERGING_MARKETS: Country codes considered "emerging market".
# -------------------------------------------------------------------
EMERGING_MARKETS: List[str] = [
    "ID", "TR", "PL", "TH", "PH", "EG", "NG", "PK", "VN", "AR", "CO", "MY", "CL", "PE"
]

# -------------------------------------------------------------------
# 7) CALIBRATION_UPDATE: Metadata for the latest coefficient update.
# -------------------------------------------------------------------
CALIBRATION_UPDATE: Dict[str, str] = {
    "last_update": "2025-05-29",
    "update_notes": "Initial v2.4 canonical key structure. All weights validated against Altman literature.",
    "update_source": "SEC EDGAR / Compustat / Salomon Smith Barney (1995 EM publication).",
}

