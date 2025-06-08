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

def find_matching_field(field_name: str, available_fields: List[str], sample_values: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Find the best matching field from available fields for a given canonical field."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Finding match for {field_name} in {len(available_fields)} fields")
    if sample_values:
        logger.debug(f"Sample values available for {len(sample_values)} fields")
    
    # Special handling for retained_earnings
    if field_name == "retained_earnings":
        logger.debug("Processing retained_earnings field")
        # Try direct match first
        for raw_field in available_fields:
            if raw_field in ["Retained Earnings", "RetainedEarnings"]:
                logger.debug(f"Found direct match: {raw_field}")
                # Skip if value is 0 (treat as missing)
                if sample_values and sample_values.get(raw_field) in [0, "0", "0.0"]:
                    logger.debug(f"Skipping {raw_field} because value is 0")
                    continue
                return raw_field
                
        # Try fallback fields
        logger.debug("Trying fallback fields for retained_earnings")
        fallback_fields = [
            "Retained Profits",
            "Accumulated Earnings",
            "Accumulated Profits",
            "Earnings Reserve",
            "Reservas de Lucros",
            "Lucros Acumulados",
            "Reservas"
        ]
        for raw_field in available_fields:
            if raw_field in fallback_fields:
                logger.debug(f"Found fallback match: {raw_field}")
                # Skip if value is 0
                if sample_values and sample_values.get(raw_field) in [0, "0", "0.0"]:
                    logger.debug(f"Skipping fallback {raw_field} because value is 0")
                    continue
                return raw_field
                
        # Try inferring from equity fields
        logger.debug("Trying to infer retained_earnings from equity fields")
        equity_field = None
        paid_in_capital_field = None
        for raw_field in available_fields:
            if raw_field in ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"]:
                equity_field = raw_field
                logger.debug(f"Found equity field: {raw_field}")
            elif raw_field == "Additional Paid In Capital":
                paid_in_capital_field = raw_field
                logger.debug(f"Found paid in capital field: {raw_field}")
        
        # If we have both fields and their values are available, infer retained earnings
        if equity_field and paid_in_capital_field and sample_values:
            logger.debug("Have both equity and paid in capital fields with sample values")
            equity_val = sample_values.get(equity_field)
            paid_in_val = sample_values.get(paid_in_capital_field)
            logger.debug(f"Values - Equity: {equity_val}, Paid in capital: {paid_in_val}")
            if equity_val not in [None, 0, "0", "0.0"] and paid_in_val not in [None, 0, "0", "0.0"]:
                logger.debug(f"Inferring retained_earnings from {equity_field} - {paid_in_capital_field}")
                # Return a special field name that the LLM can use to indicate inference
                return f"INFERRED:{equity_field}:{paid_in_capital_field}"
        else:
            logger.debug("Missing required fields or values for inference")
                
        return None
        
    # Direct mapping for other fields
    logger.debug(f"Trying direct mapping for {field_name}")
    for pattern in FIELD_MAPPING.get(field_name, []):
        for raw_field in available_fields:
            if raw_field == pattern:
                logger.debug(f"Direct match found: {raw_field}")
                return raw_field
                
    # Try synonyms
    logger.debug(f"Trying synonyms for {field_name}")
    for syn in FIELD_SYNONYMS.get(field_name, []):
        for raw_field in available_fields:
            if raw_field == syn:
                logger.debug(f"Synonym match found: {raw_field}")
                return raw_field
                
    logger.debug(f"No match found for {field_name}")
    return None
