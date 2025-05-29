# Centralized constants for Altman Z-Score models
from decimal import Decimal
from typing import Dict, Any

# --- Metadata for traceability ---
MODEL_METADATA = {
    "original": {
        "version": "2025-05-29",
        "source": "Altman 1968, 2000, 2017; WRDS/Compustat; see altmans.md",
        "notes": "Classic public manufacturing model."
    },
    "private": {
        "version": "2025-05-29",
        "source": "Altman 2000; see altmans.md",
        "notes": "Private firm model."
    },
    "service": {
        "version": "2025-05-29",
        "source": "Altman 1993; see altmans.md",
        "notes": "Service/Non-manufacturing model."
    },
    "em": {
        "version": "2025-05-29",
        "source": "Altman 2017; see altmans.md",
        "notes": "Emerging Markets model."
    },
    # Add more as needed
}

# --- Model coefficients by type (can be extended per SIC/industry) ---
MODEL_COEFFICIENTS: Dict[str, Dict[str, Decimal]] = {
    "original": {
        "A": Decimal('1.2'),
        "B": Decimal('1.4'),
        "C": Decimal('3.3'),
        "D": Decimal('0.6'),
        "E": Decimal('1.0'),
    },
    "private": {
        "A": Decimal('0.717'),
        "B": Decimal('0.847'),
        "C": Decimal('3.107'),
        "D": Decimal('0.420'),
        "E": Decimal('0.998'),
    },
    "service": {
        "A": Decimal('6.56'),
        "B": Decimal('3.26'),
        "C": Decimal('6.72'),
        "D": Decimal('1.05'),
        "E": Decimal('0.0'),
    },
    "em": {
        "A": Decimal('3.25'),
        "B": Decimal('6.56'),
        "C": Decimal('6.72'),
        "D": Decimal('1.05'),
        "E": Decimal('0.0'),
    },
    # Example: per-industry override (SIC 2834 = Pharma)
    "sic_2834": {
        "A": Decimal('1.1'),
        "B": Decimal('1.5'),
        "C": Decimal('3.0'),
        "D": Decimal('0.7'),
        "E": Decimal('1.2'),
        "version": "2025-05-29",
        "source": "Example WRDS/Compustat calibration; update as needed."
    },
    # Add more SIC/industry-specific as needed
}

# --- Z-Score thresholds by model (can be extended per industry/region) ---
Z_SCORE_THRESHOLDS: Dict[str, Dict[str, Decimal]] = {
    "original": {"safe": Decimal('2.99'), "grey": Decimal('1.81'), "distress": Decimal('1.81')},
    "private": {"safe": Decimal('2.9'), "grey": Decimal('1.23'), "distress": Decimal('1.23')},
    "public": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
    "service": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
    "em": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
    # Example: per-industry override
    "sic_2834": {"safe": Decimal('3.1'), "grey": Decimal('2.0'), "distress": Decimal('1.5')},
    # Add more SIC/industry-specific as needed
}

# --- Typical size/leverage ranges for warnings (example values, update as needed) ---
SIZE_WARNINGS = {
    "min_assets": Decimal('1000000'),  # $1M
    "max_assets": Decimal('10000000000'),  # $10B
    "max_leverage": Decimal('10.0'),  # Total Liabilities / Total Assets
}

# --- Emerging Markets (EM) country/region codes (ISO2/3, can be expanded) ---
EMERGING_MARKETS = [
    "CN", "IN", "BR", "RU", "ZA", "MX", "ID", "TR", "PL", "TH", "PH", "EG", "NG", "PK", "VN", "AR", "CO", "MY", "CL", "PE"
]

# --- Calibration update process metadata ---
CALIBRATION_UPDATE = {
    "last_update": "2025-05-29",
    "update_notes": "Initial v2.2 structure. See altmans.md for process.",
    "update_source": "WRDS/Compustat, Altman literature, open data."
}

# All future model changes must be made in this file and referenced throughout the codebase.
