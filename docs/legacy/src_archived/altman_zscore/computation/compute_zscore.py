"""
Altman Z-Score computation logic and model selection utilities.

This module is now modularized. All core logic has been moved to:
- models/financial_metrics.py (dataclasses)
- computation/formulas.py (Z-Score formulas)
- computation/compute.py (main dispatcher)
- computation/model_selection.py (model selection)
- utils/financial_metrics.py (safe_div and related utilities)

Import from those modules instead. Do NOT add formula logic here.

Functions:
    compute_zscore(metrics, model): Compute the Altman Z-Score for a given set of financial metrics and model.
    ... (other dispatcher/model selection functions documented inline)
"""

from altman_zscore.computation import compute as compute_module
from altman_zscore.computation.model_selection import determine_zscore_model as _determine_zscore_model, select_zscore_model_by_sic as _select_zscore_model_by_sic
from altman_zscore.computation.model_selection import select_zscore_model
from altman_zscore.utils.financial_metrics import FinancialMetricsCalculator
from altman_zscore.models.financial_metrics import ZScoreResult
from typing import Any, Dict, Optional

safe_div = FinancialMetricsCalculator.safe_divide

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
    # Special handling for service models to pass correct equity argument
    if model == "public_service":
        return compute_module.compute_zscore({**metrics, "equity": metrics.get("market_value_equity", 1e9)}, model)
    elif model == "private_service":
        return compute_module.compute_zscore({**metrics, "equity": metrics.get("book_value_equity", metrics.get("market_value_equity", 1e9))}, model)
    else:
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
    return _determine_zscore_model(profile)


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
    return _select_zscore_model_by_sic(sic_code, is_public, maturity)


def select_zscore_model_robust(sic: Optional[int], maturity: Optional[str], is_public: Optional[bool] = True) -> str:
    """
    Robust, literature-aligned Altman Z-Score model selection (see ModelSelection.md).
    Args:
        sic (Optional[int]): SIC code (int or str convertible to int)
        maturity (Optional[str]): 'public', 'private', 'emerging', etc.
        is_public (Optional[bool]): True if public, False if private. Defaults to True.
    Returns:
        str: Model key for MODEL_COEFFICIENTS/Z_SCORE_THRESHOLDS
    """
    # Convert maturity to is_emerging flag
    is_emerging = (maturity == "emerging") if maturity else False
    return select_zscore_model(sic, is_public if is_public is not None else True, is_emerging)


# --- For testability, add unit tests and docstring examples in a separate test module ---
