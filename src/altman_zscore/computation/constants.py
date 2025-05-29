# Centralized constants for Altman Z-Score models
from decimal import Decimal

Z_SCORE_THRESHOLDS = {
    "original": {"safe": Decimal('2.99'), "grey": Decimal('1.81'), "distress": Decimal('1.81')},
    "private": {"safe": Decimal('2.9'), "grey": Decimal('1.23'), "distress": Decimal('1.23')},
    "public": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
    "service": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
    "em": {"safe": Decimal('2.6'), "grey": Decimal('1.1'), "distress": Decimal('1.1')},
}

# Add model mappings or other constants here as needed.
