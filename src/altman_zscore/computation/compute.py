from typing import Dict, Optional

from altman_zscore.computation.constants import MODEL_COEFFICIENTS, MODEL_METADATA, Z_SCORE_THRESHOLDS
from altman_zscore.computation.formulas import (
    altman_zscore_em,
    altman_zscore_original,
    altman_zscore_private,
    altman_zscore_public,
    altman_zscore_service,
)
from altman_zscore.models.financial_metrics import ZScoreResult


def compute_zscore(
    metrics: Dict[str, float], model_key: str = "original", override_context: Optional[Dict] = None
) -> ZScoreResult:
    """
    Compute Z-Score using the selected model, logging all model/threshold overrides and assumptions.
    Returns a ZScoreResult with model, coefficients, thresholds, and context for reporting.
    """
    if override_context is None:
        override_context = {}
    # Log model/threshold selection
    coefficients = MODEL_COEFFICIENTS.get(model_key, MODEL_COEFFICIENTS["original"])
    thresholds = Z_SCORE_THRESHOLDS.get(model_key, Z_SCORE_THRESHOLDS["original"])
    model_meta = MODEL_METADATA.get(model_key, MODEL_METADATA["original"])
    override_context["model_key"] = model_key
    override_context["coefficients"] = coefficients
    override_context["thresholds"] = thresholds
    override_context["model_metadata"] = model_meta
    # Call the correct formula (for now, use the classic functions, but pass coefficients for future extensibility)
    if model_key == "original":
        result = altman_zscore_original(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key == "service":
        result = altman_zscore_service(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key == "private":
        result = altman_zscore_private(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            book_value_equity=metrics.get("book_value_equity", metrics.get("market_value_equity", 1e9)),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key == "public":
        result = altman_zscore_public(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key == "em":
        result = altman_zscore_em(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key == "tech":
        # Use the service/non-manufacturing model for tech companies
        result = altman_zscore_service(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
    elif model_key.startswith("sic_"):
        # Use the original formula but log the override
        result = altman_zscore_original(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
        override_context["sic_override"] = True
    elif model_key in MODEL_COEFFICIENTS:
        # Dynamically handle any new/custom model key using the original formula and log the override
        result = altman_zscore_original(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"],
        )
        override_context["dynamic_model_override"] = True
    else:
        raise NotImplementedError(f"Model '{model_key}' not implemented yet.")
    # Attach context for reporting
    result.override_context = override_context
    return result
