"""
Altman Z-Score computation logic and model selection utilities.

This module is now modularized. All core logic has been moved to:
- models/financial_metrics.py (dataclasses)
- computation/formulas.py (Z-Score formulas)
- computation/compute.py (main dispatcher)
- computation/model_selection.py (model selection)

Import from those modules instead.
"""
from altman_zscore.models.financial_metrics import FinancialMetrics, ZScoreResult
from altman_zscore.computation.formulas import (
    altman_zscore_original,
    altman_zscore_service,
    altman_zscore_private,
    altman_zscore_public,
    altman_zscore_em,
    safe_div
)
from altman_zscore.computation.compute import compute_zscore
from altman_zscore.computation.model_selection import determine_zscore_model, select_zscore_model_by_sic

# This file is retained for backward compatibility and as a glue module.
