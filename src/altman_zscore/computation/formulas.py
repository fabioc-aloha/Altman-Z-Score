# formulas.py

from decimal import Decimal
from typing import Dict

from ..models.financial_metrics import ZScoreResult
from ..utils.financial_metrics import FinancialMetricsCalculator
from .constants import MODEL_COEFFICIENTS, Z_SCORE_THRESHOLDS


def _safe_decimal_div(numerator: Decimal, denominator: Decimal) -> Decimal:
    """
    Wrapper around FinancialMetricsCalculator.safe_divide(...) that returns a Decimal
    and never None. If safe_divide(...) yields None (e.g., division by zero),
    return Decimal("0").
    """
    result = FinancialMetricsCalculator.safe_divide(numerator, denominator)
    return result if result is not None else Decimal("0")


# -------------------------------------------------------------------
# 1) Original Z-Score (1968, Public Manufacturing, five-ratio)
# -------------------------------------------------------------------
def altman_zscore_original(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    """
    Compute Altman Original Z-Score for public manufacturing companies.
    Five-factor model:
      X1 = (Current Assets - Current Liabilities) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets
    Coefficients: A=1.20, B=1.40, C=3.30, D=0.60, E=1.00
    Thresholds: distress ≤ 1.81, grey (1.81, 2.99], safe > 2.99
    """
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS["original"]

    # Convert inputs to Decimal
    ta = Decimal(str(total_assets))
    wc = Decimal(str(working_capital))
    re = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve = Decimal(str(market_value_equity))
    tl = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))

    # Compute ratios X1..X5, replacing None with Decimal("0")
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(mve, tl)
    X5 = _safe_decimal_div(sales_dec, ta)

    # Calculate Z-Score: Z = A*X1 + B*X2 + C*X3 + D*X4 + E*X5
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
        + coeffs["E"] * X5
    )

    thresholds = Z_SCORE_THRESHOLDS["original"]
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
        model="original",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


# -------------------------------------------------------------------
# 2) Z′-Score (1983, Private Manufacturing, five-ratio)
# -------------------------------------------------------------------
def altman_zscore_private(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    book_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
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

    ta = Decimal(str(total_assets))
    wc = Decimal(str(working_capital))
    re = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    bve = Decimal(str(book_value_equity))
    tl = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))

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
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    equity: float,
    total_assets: float,
    total_liabilities: float,
    model_key: str = "service",
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
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS[model_key]

    ta = Decimal(str(total_assets))
    wc = Decimal(str(working_capital))
    re = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    equity_dec = Decimal(str(equity))
    tl = Decimal(str(total_liabilities))

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
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    book_value_equity: float,
    total_assets: float,
    total_liabilities: float,
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

    ta = Decimal(str(total_assets))
    wc = Decimal(str(working_capital))
    re = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    bve = Decimal(str(book_value_equity))
    tl = Decimal(str(total_liabilities))

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
