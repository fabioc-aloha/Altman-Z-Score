"""
Core financials logic for modularized financials pipeline.
"""
from decimal import Decimal
from typing import Dict, Any, List, Optional
import pandas as pd
from altman_zscore.computation.constants import FIELD_MAPPING

def df_to_dict_str_keys(df: pd.DataFrame) -> Dict[str, Dict[str, Decimal]]:
    """Convert DataFrame to dictionary with string keys and Decimal values."""
    if not isinstance(df, pd.DataFrame):
        return {}
    return {
        str(row_key): {str(col_key): Decimal(str(val)) if pd.notna(val) else Decimal("0") for col_key, val in row.items()}
        for row_key, row in df.to_dict().items()
    }

def find_matching_field(field_name: str, available_fields: List[str]) -> Optional[str]:
    """Find a matching field name in available fields using direct mapping."""
    if field_name in FIELD_MAPPING:
        # Try exact matches first
        if field_name in available_fields:
            return field_name
        # Then try the mapped fields
        for mapped_name in FIELD_MAPPING[field_name]:
            if mapped_name in available_fields:
                return mapped_name
            # Try case-insensitive match
            for available_field in available_fields:
                if mapped_name.lower() == available_field.lower():
                    return available_field
    return None
