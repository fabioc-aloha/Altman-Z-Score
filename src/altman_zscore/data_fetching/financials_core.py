"""
Core financials logic for modularized financials pipeline in Altman Z-Score analysis.

Provides helpers for DataFrame-to-dict conversion. Field mapping is now handled by Azure OpenAI.
"""
from decimal import Decimal
from typing import Dict, Any, List
import pandas as pd

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
