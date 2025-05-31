from decimal import Decimal

from ..models.financial_metrics import ZScoreResult
from ..utils.financial_metrics import FinancialMetricsCalculator
from .constants import Z_SCORE_THRESHOLDS, MODEL_COEFFICIENTS


def altman_zscore_service(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    coeffs = MODEL_COEFFICIENTS["service"]
    X1 = calc.safe_divide(wc_dec, ta_dec)
    X2 = calc.safe_divide(re_dec, ta_dec)
    X3 = calc.safe_divide(ebit_dec, ta_dec)
    X4 = calc.safe_divide(mve_dec, tl_dec)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (service model)")
    X1 = X1 if X1 is not None else Decimal(0)
    X2 = X2 if X2 is not None else Decimal(0)
    X3 = X3 if X3 is not None else Decimal(0)
    X4 = X4 if X4 is not None else Decimal(0)
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
    )
    thresholds = Z_SCORE_THRESHOLDS["service"]
    if z > Decimal(str(thresholds["safe"])):
        diagnostic = "Safe Zone"
    elif z < Decimal(str(thresholds["distress"])):
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    return ZScoreResult(
        z_score=z,
        model="service",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


def altman_zscore_original(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))
    coeffs = MODEL_COEFFICIENTS["original"]
    X1 = calc.safe_divide(wc_dec, ta_dec)
    X2 = calc.safe_divide(re_dec, ta_dec)
    X3 = calc.safe_divide(ebit_dec, ta_dec)
    X4 = calc.safe_divide(mve_dec, tl_dec)
    X5 = calc.safe_divide(sales_dec, ta_dec)
    if None in (X1, X2, X3, X4, X5):
        raise ValueError("Division by zero in one or more Z-Score components (original model)")
    X1 = X1 if X1 is not None else Decimal(0)
    X2 = X2 if X2 is not None else Decimal(0)
    X3 = X3 if X3 is not None else Decimal(0)
    X4 = X4 if X4 is not None else Decimal(0)
    X5 = X5 if X5 is not None else Decimal(0)
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
        + coeffs["E"] * X5
    )
    thresholds = Z_SCORE_THRESHOLDS["original"]
    if z > Decimal(str(thresholds["safe"])):
        diagnostic = "Safe Zone"
    elif z < Decimal(str(thresholds["distress"])):
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


def altman_zscore_private(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    book_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    bve_dec = Decimal(str(book_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))
    coeffs = MODEL_COEFFICIENTS["private"]
    X1 = calc.safe_divide(wc_dec, ta_dec)
    X2 = calc.safe_divide(re_dec, ta_dec)
    X3 = calc.safe_divide(ebit_dec, ta_dec)
    X4 = calc.safe_divide(bve_dec, tl_dec)
    X5 = calc.safe_divide(sales_dec, ta_dec)
    if None in (X1, X2, X3, X4, X5):
        raise ValueError("Division by zero in one or more Z-Score components (private model)")
    X1 = X1 if X1 is not None else Decimal(0)
    X2 = X2 if X2 is not None else Decimal(0)
    X3 = X3 if X3 is not None else Decimal(0)
    X4 = X4 if X4 is not None else Decimal(0)
    X5 = X5 if X5 is not None else Decimal(0)
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
        + coeffs["E"] * X5
    )
    thresholds = Z_SCORE_THRESHOLDS["private"]
    if z > Decimal(str(thresholds["safe"])):
        diagnostic = "Safe Zone"
    elif z < Decimal(str(thresholds["distress"])):
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


def altman_zscore_public(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    coeffs = MODEL_COEFFICIENTS["public"] if "public" in MODEL_COEFFICIENTS else MODEL_COEFFICIENTS["service"]
    X1 = calc.safe_divide(wc_dec, ta_dec)
    X2 = calc.safe_divide(re_dec, ta_dec)
    X3 = calc.safe_divide(ebit_dec, ta_dec)
    X4 = calc.safe_divide(mve_dec, tl_dec)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (public model)")
    X1 = X1 if X1 is not None else Decimal(0)
    X2 = X2 if X2 is not None else Decimal(0)
    X3 = X3 if X3 is not None else Decimal(0)
    X4 = X4 if X4 is not None else Decimal(0)
    z = (
        coeffs["A"] * X1
        + coeffs["B"] * X2
        + coeffs["C"] * X3
        + coeffs["D"] * X4
    )
    thresholds = Z_SCORE_THRESHOLDS["public"]
    if z > Decimal(str(thresholds["safe"])):
        diagnostic = "Safe Zone"
    elif z < Decimal(str(thresholds["distress"])):
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    return ZScoreResult(
        z_score=z,
        model="public",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


def altman_zscore_em(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float,
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    coeffs = MODEL_COEFFICIENTS["em"]
    X1 = calc.safe_divide(wc_dec, ta_dec)
    X2 = calc.safe_divide(re_dec, ta_dec)
    X3 = calc.safe_divide(ebit_dec, ta_dec)
    X4 = calc.safe_divide(mve_dec, tl_dec)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (EM model)")
    X1 = X1 if X1 is not None else Decimal(0)
    X2 = X2 if X2 is not None else Decimal(0)
    X3 = X3 if X3 is not None else Decimal(0)
    X4 = X4 if X4 is not None else Decimal(0)
    z = (
        coeffs["A"]
        + coeffs["B"] * X1
        + coeffs["C"] * X2
        + coeffs["D"] * X3
        + coeffs["E"] * X4
    )
    thresholds = Z_SCORE_THRESHOLDS["em"]
    if z > Decimal(str(thresholds["safe"])):
        diagnostic = "Safe Zone"
    elif z < Decimal(str(thresholds["distress"])):
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
