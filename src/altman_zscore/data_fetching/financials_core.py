"""
Core financials logic for modularized financials pipeline in Altman Z-Score analysis.

Provides helpers for DataFrame-to-dict conversion. Field mapping is now handled by Azure OpenAI.
"""
from decimal import Decimal
from typing import Dict, Any, List
import pandas as pd
import decimal  # Added to reference decimal.InvalidOperation

def df_to_dict_str_keys(df: pd.DataFrame) -> Dict[str, Dict[str, Decimal]]:
    """Convert DataFrame to dictionary with string keys and Decimal values.

    Args:
        df (pd.DataFrame): DataFrame to convert.

    Returns:
        dict: Dictionary with string row/column keys and Decimal values.
    """
    if not isinstance(df, pd.DataFrame):
        return {}
    result: Dict[str, Dict[str, Decimal]] = {}
    for row_key, row in df.to_dict().items():
        row_clean: Dict[str, Decimal] = {}
        for col_key, val in row.items():
            key_str = str(col_key)
            if pd.notna(val):
                try:
                    dec_val = Decimal(str(val))
                except (decimal.InvalidOperation, ValueError, TypeError):
                    # Fallback to zero if conversion fails
                    dec_val = Decimal("0")
            else:
                dec_val = Decimal("0")
            row_clean[key_str] = dec_val
        result[str(row_key)] = row_clean
    return result
