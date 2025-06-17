"""
Z-Score model formula implementations for Altman Z-Score analysis.

Provides functions for each Altman Z-Score model variant, including original, private, service, and emerging markets, returning ZScoreResult objects with all relevant metadata.
"""

from decimal import Decimal
from typing import Dict

from ..models.financial_metrics import ZScoreResult
from ..utils.financial_metrics import FinancialMetricsCalculator
from .constants import MODEL_COEFFICIENTS, Z_SCORE_THRESHOLDS


def _safe_decimal_div(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Safely divide two Decimals, returning Decimal('0') on error or division by zero."""
    result = FinancialMetricsCalculator.safe_divide(numerator, denominator)
    return result if result is not None else Decimal("0")


def _extract_metrics(metrics: Dict[str, float], required_fields: list) -> tuple:
    """Extract required metrics from the dictionary and convert to float."""
    try:
        return tuple(float(metrics[field]) for field in required_fields)
    except (KeyError, TypeError, ValueError) as e:
        missing = [f for f in required_fields if f not in metrics]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}") from e
        raise


# -------------------------------------------------------------------
# 1) Original Z-Score (1968, Public Manufacturing, five-ratio)
# -------------------------------------------------------------------
def altman_zscore_original(metrics: Dict[str, float]) -> Decimal:
    """
    Compute Altman Original Z-Score for public manufacturing companies.
    
    Required metrics:
        - working_capital or (current_assets and current_liabilities)
        - retained_earnings
        - ebit
        - market_value_equity
        - total_assets
        - total_liabilities
        - sales
    """
    # Calculate working capital if not provided
    if "working_capital" not in metrics and all(k in metrics for k in ["current_assets", "current_liabilities"]):
        metrics["working_capital"] = metrics["current_assets"] - metrics["current_liabilities"]
    
    # Extract required metrics
    required_fields = [
        "working_capital",
        "retained_earnings",
        "ebit",
        "market_value_equity",
        "total_assets",
        "total_liabilities",
        "sales"
    ]
    
    working_capital, retained_earnings, ebit, market_value_equity, total_assets, total_liabilities, sales = _extract_metrics(metrics, required_fields)

    x1 = _safe_decimal_div(Decimal(str(working_capital)), Decimal(str(total_assets)))
    x2 = _safe_decimal_div(Decimal(str(retained_earnings)), Decimal(str(total_assets)))
    x3 = _safe_decimal_div(Decimal(str(ebit)), Decimal(str(total_assets)))
    x4 = _safe_decimal_div(Decimal(str(market_value_equity)), Decimal(str(total_liabilities)))
    x5 = _safe_decimal_div(Decimal(str(sales)), Decimal(str(total_assets)))

    # Get coefficients for original model
    coeffs = MODEL_COEFFICIENTS["original"]
    
    # Calculate Z-Score
    z_score = (
        Decimal(str(coeffs["X1"])) * x1 +
        Decimal(str(coeffs["X2"])) * x2 +
        Decimal(str(coeffs["X3"])) * x3 +
        Decimal(str(coeffs["X4"])) * x4 +
        Decimal(str(coeffs["X5"])) * x5
    )
    
    return z_score


# -------------------------------------------------------------------
# 2) Z′-Score (1983, Private Manufacturing, five-ratio)
# -------------------------------------------------------------------
def altman_zscore_private(
    metrics: Dict[str, float]
) -> ZScoreResult:
    """
    Compute Altman Z′-Score for private manufacturing companies.

    Five-factor model:
      X1 = (Current Assets - Current Liabilities) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Book Value of Equity / Total Liabilities
      X5 = Sales / Total Assets

    Coefficients: A=0.717, B=0.847, C=3.107, D=0.420, E=0.998

    Thresholds: distress ≤ 1.10, grey (1.10, 2.60], safe > 2.60
    """
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS["private"]

    ta = Decimal(str(metrics["total_assets"]))
    wc = Decimal(str(metrics["working_capital"]))
    re = Decimal(str(metrics["retained_earnings"]))
    ebit_dec = Decimal(str(metrics["ebit"]))
    bve = Decimal(str(metrics["book_value_equity"]))
    tl = Decimal(str(metrics["total_liabilities"]))
    sales_dec = Decimal(str(metrics["sales"]))


    # Compute ratios X1..X5, replacing None with Decimal("0")
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(bve, tl)
    X5 = _safe_decimal_div(sales_dec, ta)

    # Calculate Z-Score: Z' = A*X1 + B*X2 + C*X3 + D*X4 + E*X5
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
        + coeffs["E"] * X5
    )

    thresholds = Z_SCORE_THRESHOLDS["private"]
    safe_cutoff = thresholds["safe"]
    distress_cutoff = thresholds["distress"]

    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"

    return ZScoreResult(
        z_score=z,
        model="private",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


# -------------------------------------------------------------------
# 3) Zʺ-Score (1995, Public/Private Non-Manufacturing, four-ratio)
# -------------------------------------------------------------------
def altman_zscore_service(
    metrics: Dict[str, float],
    use_book_value: bool = False
) -> ZScoreResult:
    """
    Compute Altman Zʺ-Score for non-manufacturing companies.

    Four-factor model:
      X1 = (Current Assets - Current Liabilities) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Equity / Total Liabilities
        - For public non-manufacturing ("service"): Equity = Market Value of Equity
        - For private non-manufacturing ("service_private"): Equity = Book Value of Equity
      "tech" is an alias that behaves identically to "service" (public non-manufacturing).

    Coefficients: A=6.56, B=3.26, C=6.72, D=1.05

    Thresholds (public): distress ≤ 1.23, grey (1.23, 2.90], safe > 2.90
    Thresholds (private): distress ≤ 1.10, grey (1.10, 2.60], safe > 2.60
    """
    model_key = "service_private" if use_book_value else "service"
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS[model_key]

    ta = Decimal(str(metrics["total_assets"]))
    wc = Decimal(str(metrics["working_capital"]))
    re = Decimal(str(metrics["retained_earnings"]))
    ebit_dec = Decimal(str(metrics["ebit"]))
    equity_dec = Decimal(str(metrics["market_value_equity"] if not use_book_value else metrics["book_value_equity"]))
    tl = Decimal(str(metrics["total_liabilities"]))


    # Compute ratios X1..X4, replacing None with Decimal("0")
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(equity_dec, tl)

    # Calculate Z-Score: Zʺ = A*X1 + B*X2 + C*X3 + D*X4
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
    )

    thresholds = Z_SCORE_THRESHOLDS[model_key]
    safe_cutoff = thresholds["safe"]
    distress_cutoff = thresholds["distress"]

    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"

    return ZScoreResult(
        z_score=z,
        model=model_key,
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


# -------------------------------------------------------------------
# 4) Z_EM-Score (1995, EM-Adjusted, four-ratio + intercept)
# -------------------------------------------------------------------
def altman_zscore_em(
    metrics: Dict[str, float]
) -> ZScoreResult:
    """
    Compute Altman Z_EM-Score for emerging market companies (any SIC).

    Four-ratio + intercept model:
      X1 = (Current Assets - Current Liabilities) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Book Value of Equity / Total Liabilities
      Z = 3.25 
          + 6.56·X1 
          + 3.26·X2 
          + 6.72·X3 
          + 1.05·X4

    Thresholds: distress ≤ 1.10, grey (1.10, 2.60], safe > 2.60
    """
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS["em"]

    ta = Decimal(str(metrics["total_assets"]))
    wc = Decimal(str(metrics["working_capital"]))
    re = Decimal(str(metrics["retained_earnings"]))
    ebit_dec = Decimal(str(metrics["ebit"]))
    bve = Decimal(str(metrics["book_value_equity"]))
    tl = Decimal(str(metrics["total_liabilities"]))


    # Compute ratios X1..X4, replacing None with Decimal("0")
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(bve, tl)

    # coeffs["A"] is the intercept (3.25)
    z = (
        coeffs["A"]
        + coeffs["B"] * X1
        + coeffs["C"] * X2
        + coeffs["D"] * X3
        + coeffs["E"] * X4
    )

    thresholds = Z_SCORE_THRESHOLDS["em"]
    safe_cutoff = thresholds["safe"]
    distress_cutoff = thresholds["distress"]

    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"

    return ZScoreResult(
        z_score=z,
        model="em",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )
