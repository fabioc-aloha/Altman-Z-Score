"""
Computation logic for Altman Z-Score calculation in Altman Z-Score analysis.

Provides the main compute_zscore() function, which dispatches to the correct model formula and returns a ZScoreResult with all relevant metadata.
"""

import logging
from typing import Dict, Optional

from altman_zscore.computation.constants import MODEL_COEFFICIENTS, Z_SCORE_THRESHOLDS
from altman_zscore.computation.formulas import (
    altman_zscore_original,
    altman_zscore_private,
    altman_zscore_service,
    altman_zscore_retail
)
from altman_zscore.computation.model_selection import (
    canonicalize_model_key,
    select_zscore_model,
    get_model_selection_context
)
from altman_zscore.models.financial_metrics import ZScoreResult

logger = logging.getLogger(__name__)


def compute_zscore(
    metrics: Dict[str, float],
    model_key: str = "original",
    override_context: Optional[Dict] = None,
    sic_code: Optional[int] = None,
    is_public: bool = True
) -> ZScoreResult:
    """Compute Z-Score using the selected model and return a ZScoreResult.

    Args:
        metrics (dict): Financial metrics dictionary
        model_key (str, optional): Initial model suggestion (can be overridden by SIC/profile)
        override_context (dict, optional): Context for model selection overrides
        sic_code (int, optional): Company SIC code for model selection
        is_public (bool): Whether the company is public

    Returns:
        ZScoreResult: Result object with z_score, model, components, diagnostic, and context

    Raises:
        NotImplementedError: If the requested model is not implemented
    """
    # Initialize context
    context = override_context or {}
    
    # Perform model selection if SIC code is provided
    if sic_code is not None:
        model_key = select_zscore_model(
            sic_code=sic_code,
            is_public=is_public
        )
        selection_context = get_model_selection_context(
            sic_code=sic_code,
            is_public=is_public,
            selected_model=model_key
        )
        context.update(selection_context)
        logger.info(f"Model selected: {model_key} ({', '.join(selection_context['selection_reason'])})")
    
    # Canonicalize the model key
    model_key = canonicalize_model_key(model_key)
    # Compute derived working_capital if missing
    if "working_capital" not in metrics and "current_assets" in metrics and "current_liabilities" in metrics:
        try:
            metrics["working_capital"] = float(metrics.get("current_assets", 0)) - float(metrics.get("current_liabilities", 0))
        except Exception:
            metrics["working_capital"] = None
    # Get model coefficients and thresholds
    coefficients = MODEL_COEFFICIENTS.get(model_key)
    thresholds = Z_SCORE_THRESHOLDS.get(model_key)
    
    if coefficients is None:
        raise NotImplementedError(f"Model '{model_key}' not implemented")

    # Compute Z-Score using the appropriate model
    if model_key in ["service", "tech"]:
        result = altman_zscore_service(metrics)
    elif model_key == "service_private":
        result = altman_zscore_service(metrics, use_book_value=True)
    elif model_key == "private":
        result = altman_zscore_private(metrics)
    elif model_key == "retail":
        result = altman_zscore_retail(metrics)
    else:  # "original" and any SIC-specific models
        result = altman_zscore_original(metrics)

    # Extract z_score and components from the result
    z_score = result.z_score
    components = result.components

    # Update context with model details
    context.update({
        "model_key": model_key,
        "coefficients": coefficients,
        "thresholds": thresholds
    })    # Determine diagnostic based on thresholds
    if z_score > thresholds["SAFE"]:
        diagnostic = "Safe Zone"
    elif z_score < thresholds["DISTRESS"]:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"

    return ZScoreResult(
        z_score=z_score,
        model=model_key,
        components=components,
        diagnostic=diagnostic,
        thresholds=thresholds,
        override_context=context
    )


def determine_zscore_zone(z_score, model_key="original"):
    """
    Determine the zone classification for a given Z-Score and model.

    Args:
        z_score: Numeric Z-Score value (float, int, or Decimal).
        model_key: Z-Score model key to use thresholds from.
    Returns:
        str: 'SAFE', 'DISTRESS', or 'GREY' based on thresholds.
    """
    from altman_zscore.computation.model_selection import canonicalize_model_key
    mk = canonicalize_model_key(model_key)
    thresholds = Z_SCORE_THRESHOLDS.get(mk, Z_SCORE_THRESHOLDS.get("original"))
    # Compare using Decimal semantics if possible
    try:
        score = z_score
        # Convert if not Decimal
        from decimal import Decimal as _D
        if not isinstance(score, _D):
            score = _D(str(score))
    except Exception:
        score = z_score
    if score > thresholds["SAFE"]:
        return "SAFE"
    elif score < thresholds["DISTRESS"]:
        return "DISTRESS"
    else:
        return "GREY"
