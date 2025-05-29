"""
Altman Z-Score computation logic and model selection utilities.

This module is now modularized. All core logic has been moved to:
- models/financial_metrics.py (dataclasses)
- computation/formulas.py (Z-Score formulas)
- computation/compute.py (main dispatcher)
- computation/model_selection.py (model selection)
- utils/financial_metrics.py (safe_div and related utilities)

Import from those modules instead. Do NOT add formula logic here.
"""
from altman_zscore.models.financial_metrics import FinancialMetrics, ZScoreResult
from altman_zscore.computation.formulas import (
    altman_zscore_original,
    altman_zscore_service,
    altman_zscore_private,
    altman_zscore_public,
    altman_zscore_em,
)
from altman_zscore.computation import compute as compute_module
from altman_zscore.computation.model_selection import determine_zscore_model, select_zscore_model_by_sic
from altman_zscore.utils.financial_metrics import FinancialMetricsCalculator
safe_div = FinancialMetricsCalculator.safe_divide
from typing import Dict, Any, Optional
from decimal import Decimal

# All Z-Score formula implementations and safe_div have been removed from this file.
# Use the imported functions above for all Z-Score calculations and utilities.
# Only dispatcher and model selection logic should remain here.

# --- Dispatcher and model selection logic only ---

# Removed duplicate safe_div; use FinancialMetricsCalculator.safe_divide if needed elsewhere.

def compute_zscore(metrics: Dict[str, float], model: str = "original") -> ZScoreResult:
    """
    Compute the Altman Z-Score for a given set of financial metrics and model.

    Args:
        metrics (dict): Financial metrics (see FinancialMetrics)
        model (str): Z-Score model name (e.g., 'original', 'private', 'tech')
    Returns:
        ZScoreResult: Object with z_score and all intermediate values
    """
    # Delegate to computation/compute.py for all model logic, including 'tech'.
    return compute_module.compute_zscore(metrics, model)

# --- Calibration and model selection ---

def determine_zscore_model(profile: Any) -> str:
    """
    Select the correct Altman Z-Score model based on company profile attributes.

    Args:
        profile (Any): Company profile object with at least 'industry' and 'is_public' attributes. May also have 'is_emerging_market'.

    Returns:
        str: Model string ('original', 'private', 'service', 'public', or 'em')
            - 'original': Public manufacturing/industrial
            - 'private': Private manufacturing/industrial
            - 'service': Service/financial/tech (public or private)
            - 'public': Public non-manufacturing/tech
            - 'em': Emerging market
    """
    industry = getattr(profile, 'industry', '').lower() if hasattr(profile, 'industry') else ''
    is_public = getattr(profile, 'is_public', True) if hasattr(profile, 'is_public') else True
    is_emerging = getattr(profile, 'is_emerging_market', False) if hasattr(profile, 'is_emerging_market') else False

    if is_emerging:
        return 'em'
    if industry in ['manufacturing', 'hardware', 'industrial']:
        return 'original' if is_public else 'private'
    if industry in ['service', 'software', 'tech', 'technology']:
        return 'public' if is_public else 'private'
    # Default fallback
    return 'original'

def select_zscore_model_by_sic(sic_code: str, is_public: bool = True, maturity: Optional[str] = None) -> str:
    """
    Select the Altman Z-Score model type based on SIC code, public/private status, and optional maturity.

    Args:
        sic_code (str): SIC code as a string (empty string for missing/unknown)
        is_public (bool, optional): Whether the company is public. Defaults to True.
        maturity (Optional[str], optional): Optional maturity string (e.g., 'private', 'emerging'). Not currently used in logic.

    Returns:
        str: Model type ('original', 'private', 'service', 'public', 'tech', 'em')
            - 'original': Public manufacturing/industrial (SIC 2000-3999)
            - 'private': Private manufacturing/industrial (SIC 2000-3999)
            - 'tech': Tech/software (SIC 3570-3579, 3670-3679, 7370-7379)
            - 'service': Financial/general services (SIC 6000-8999)
            - fallback: 'original' for missing/invalid SIC or unclassified
    """
    if sic_code.strip() == "":
        return 'original'  # fallback to original if SIC is missing or empty
    try:
        sic = int(str(sic_code))
    except Exception:
        return 'original'  # fallback to original if SIC is invalid
    # Manufacturing (Original/Private): 2000-3999
    if 2000 <= sic <= 3999:
        return 'original' if is_public else 'private'
    # Tech: 3570-3579, 3670-3679, 7370-7379
    if (3570 <= sic <= 3579) or (3670 <= sic <= 3679) or (7370 <= sic <= 7379):
        return 'tech' if is_public else 'private'
    # Financial Services: 6000-6999
    if 6000 <= sic <= 6999:
        return 'service' if is_public else 'private'
    # General Services: 7000-8999
    if 7000 <= sic <= 8999:
        return 'service' if is_public else 'private'
    # Emerging markets (if flagged elsewhere)
    # Add more rules as needed
    return 'original'  # fallback

# --- For testability, add unit tests and docstring examples in a separate test module ---
