"""
Computation logic for Altman Z-Score calculation in Altman Z-Score analysis.

Provides the main compute_zscore() function, which dispatches to the correct model formula and returns a ZScoreResult with all relevant metadata.
"""

from typing import Dict, Optional

from altman_zscore.computation.constants import MODEL_COEFFICIENTS, Z_SCORE_THRESHOLDS
from altman_zscore.computation.formulas import (
    altman_zscore_em,
    altman_zscore_original,
    altman_zscore_private,
    altman_zscore_service,
)
from altman_zscore.computation.model_selection import canonicalize_model_key
from altman_zscore.models.financial_metrics import ZScoreResult


def compute_zscore(
    metrics: Dict[str, float],
    model_key: str = "original",
    override_context: Optional[Dict] = None
) -> ZScoreResult:
    """Compute Z-Score using the selected model and return a ZScoreResult.

    Args:
        metrics (dict): Must contain keys like:
            - current_assets
            - current_liabilities
            - retained_earnings
            - ebit
            - total_assets
            - (market_value_equity or book_value_equity)
            - total_liabilities (optional; if missing, uses current_liabilities)
            - sales (only used by original/private)
        model_key (str, optional): Which Z-Score variant to apply. One of:
            "original", "private", "service", "service_private", "tech", "em", or "sic_XXXX" override.
        override_context (dict, optional): If provided, will be populated with:
            - "model_key"
            - "coefficients"
            - "thresholds"
            - any dynamic overrides (e.g. "sic_override", "dynamic_model_override")

    Returns:
        ZScoreResult: Result object with z_score, model, components, diagnostic, thresholds, and override_context.

    Raises:
        NotImplementedError: If the requested model is not implemented.
    """
    if override_context is None:
        override_context = {}

    # 0) Canonicalize model_key to ensure legacy aliases are converted
    model_key = canonicalize_model_key(model_key)

    # 1) Record metadata for whichever model_key was passed
    coefficients = MODEL_COEFFICIENTS.get(model_key, MODEL_COEFFICIENTS["original"])
    thresholds = Z_SCORE_THRESHOLDS.get(model_key, Z_SCORE_THRESHOLDS["original"])

    override_context["model_key"] = model_key
    override_context["coefficients"] = coefficients
    override_context["thresholds"] = thresholds

    # 2) Build working_capital and total_liabilities
    working_capital = metrics["current_assets"] - metrics["current_liabilities"]
    total_liabilities = metrics.get("total_liabilities", metrics["current_liabilities"])

    # 3) Dispatch to the correct formula
    if model_key == "original":
        result = altman_zscore_original(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics["market_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            sales=metrics["sales"],
        )

    elif model_key == "private":
        result = altman_zscore_private(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            book_value_equity=metrics["book_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            sales=metrics["sales"],
        )

    elif model_key in ("service", "tech"):
        # Public non-manufacturing (use market value of equity)
        result = altman_zscore_service(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            equity=metrics["market_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            model_key="service",
        )

    elif model_key in ("service_private", "private_service"):
        # Private non-manufacturing (use book value of equity)
        result = altman_zscore_service(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            equity=metrics["book_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            model_key="service_private",
        )

    elif model_key == "em":
        # Emerging-market adjusted (four-ratio + intercept, uses book-value equity)
        result = altman_zscore_em(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            book_value_equity=metrics["book_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
        )

    elif model_key.startswith("sic_"):
        # SIC-specific override: call original formula but flag it
        result = altman_zscore_original(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics["market_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            sales=metrics["sales"],
        )
        override_context["sic_override"] = True

    elif model_key in MODEL_COEFFICIENTS:
        # Present in MODEL_COEFFICIENTS but not explicitly handled: fallback to original
        result = altman_zscore_original(
            working_capital=working_capital,
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics["market_value_equity"],
            total_assets=metrics["total_assets"],
            total_liabilities=total_liabilities,
            sales=metrics["sales"],
        )
        override_context["dynamic_model_override"] = True

    else:
        raise NotImplementedError(f"Model '{model_key}' not implemented.")

    # 4) Attach the override_context for reporting/tracing
    result.override_context = override_context
    return result
