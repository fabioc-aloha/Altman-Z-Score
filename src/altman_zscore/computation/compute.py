from typing import Dict
from altman_zscore.computation.formulas import (
    altman_zscore_original,
    altman_zscore_service,
    altman_zscore_private,
    altman_zscore_public,
    altman_zscore_em
)
from altman_zscore.models.financial_metrics import ZScoreResult

def compute_zscore(metrics: Dict[str, float], model: str = "original") -> ZScoreResult:
    # NOTE: All output file writing should use the centralized get_output_dir(relative_path, ticker) utility
    # from altman_zscore.utils.paths to ensure outputs go to ./output/<TICKER>/ as per project conventions.
    # This function does not write output directly, but any future output should follow this pattern.
    if model == "original":
        return altman_zscore_original(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"]
        )
    if model == "service":
        return altman_zscore_service(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"]
        )
    if model == "private":
        return altman_zscore_private(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            book_value_equity=metrics.get("book_value_equity", metrics.get("market_value_equity", 1e9)),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"]
        )
    if model == "public":
        return altman_zscore_public(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"]
        )
    if model == "em":
        return altman_zscore_em(
            working_capital=metrics["current_assets"] - metrics["current_liabilities"],
            retained_earnings=metrics["retained_earnings"],
            ebit=metrics["ebit"],
            market_value_equity=metrics.get("market_value_equity", 1e9),
            total_assets=metrics["total_assets"],
            total_liabilities=metrics.get("total_liabilities", metrics["current_liabilities"]),
            sales=metrics["sales"]
        )
    if model == "tech":
        # Tech model: use public model formula, with different thresholds
        from decimal import Decimal
        X1 = Decimal(str(metrics["current_assets"] - metrics["current_liabilities"])) / Decimal(str(metrics["total_assets"]))
        X2 = Decimal(str(metrics["retained_earnings"])) / Decimal(str(metrics["total_assets"]))
        X3 = Decimal(str(metrics["ebit"])) / Decimal(str(metrics["total_assets"]))
        X4 = Decimal(str(metrics.get("market_value_equity", 1e9))) / Decimal(str(metrics.get("total_liabilities", metrics["current_liabilities"])))
        if None in (X1, X2, X3, X4):
            raise ValueError("Division by zero in one or more Z-Score components (tech model)")
        X1 = X1 if X1 is not None else Decimal(0)
        X2 = X2 if X2 is not None else Decimal(0)
        X3 = X3 if X3 is not None else Decimal(0)
        X4 = X4 if X4 is not None else Decimal(0)
        z = Decimal('6.56')*X1 + Decimal('3.26')*X2 + Decimal('6.72')*X3 + Decimal('1.05')*X4
        from altman_zscore.computation.constants import Z_SCORE_THRESHOLDS
        if metrics.get("company_maturity") == "young":
            thresholds = {"safe": Decimal('1.5'), "grey": Decimal('0.5'), "distress": Decimal('0.5')}
        else:
            thresholds = Z_SCORE_THRESHOLDS["tech"] if "tech" in Z_SCORE_THRESHOLDS else Z_SCORE_THRESHOLDS["public"]
        if z > thresholds["safe"]:
            diagnostic = "Safe Zone"
        elif z < thresholds["distress"]:
            diagnostic = "Distress Zone"
        else:
            diagnostic = "Grey Zone"
        return ZScoreResult(
            z_score=z,
            model="tech",
            components={"X1": X1, "X2": X2, "X3": X3, "X4": X4},
            diagnostic=diagnostic,
            thresholds=thresholds
        )
    raise NotImplementedError(f"Model '{model}' not implemented yet.")
