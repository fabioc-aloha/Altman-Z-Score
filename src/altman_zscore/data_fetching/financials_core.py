"""
Core financials logic for modularized financials pipeline in Altman Z-Score analysis.

Provides helpers for DataFrame-to-dict conversion and robust field name matching using canonical mappings and synonyms.
"""
from decimal import Decimal
from typing import Dict, Any, List, Optional
import pandas as pd
from altman_zscore.computation.constants import FIELD_MAPPING, FIELD_SYNONYMS

def df_to_dict_str_keys(df: pd.DataFrame) -> Dict[str, Dict[str, Decimal]]:
    """Convert DataFrame to dictionary with string keys and Decimal values.

    Args:
        df (pd.DataFrame): DataFrame to convert.

    Returns:
        dict: Dictionary with string row/column keys and Decimal values.
    """
    if not isinstance(df, pd.DataFrame):
        return {}
    return {
        str(row_key): {str(col_key): Decimal(str(val)) if pd.notna(val) else Decimal("0") for col_key, val in row.items()}
        for row_key, row in df.to_dict().items()
    }

def find_matching_field(field_name: str, available_fields: List[str]) -> Optional[str]:
    """Find a matching field name in available fields using FIELD_SYNONYMS and FIELD_MAPPING.

    Args:
        field_name (str): Canonical or raw field name to match.
        available_fields (list): List of available field names.

    Returns:
        str or None: The best-matching field name, or None if not found.
    """
    # First, resolve to canonical name if possible
    canonical = FIELD_SYNONYMS.get(field_name, field_name)
    # Try direct canonical match
    if canonical in available_fields:
        return canonical
    # Try mapped fields from FIELD_MAPPING
    if canonical in FIELD_MAPPING:
        for mapped_name in FIELD_MAPPING[canonical]:
            if mapped_name in available_fields:
                return mapped_name
            # Try case-insensitive match
            for available_field in available_fields:
                if mapped_name.lower() == available_field.lower():
                    return available_field
    # Try synonym match for all available fields
    for available_field in available_fields:
        if FIELD_SYNONYMS.get(available_field, available_field) == canonical:
            return available_field
    return None
