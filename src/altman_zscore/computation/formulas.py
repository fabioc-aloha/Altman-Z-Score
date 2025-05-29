from typing import Dict
from decimal import Decimal
from altman_zscore.models.financial_metrics import ZScoreResult
from altman_zscore.computation.constants import Z_SCORE_THRESHOLDS
from altman_zscore.utils.financial_metrics import FinancialMetricsCalculator

def altman_zscore_service(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
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
    z = Decimal('6.56')*X1 + Decimal('3.26')*X2 + Decimal('6.72')*X3 + Decimal('1.05')*X4
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
        thresholds=thresholds
    )

def altman_zscore_original(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))
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
    z = Decimal('1.2')*X1 + Decimal('1.4')*X2 + Decimal('3.3')*X3 + Decimal('0.6')*X4 + Decimal('1.0')*X5
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
        thresholds=thresholds
    )

def altman_zscore_private(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    book_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    bve_dec = Decimal(str(book_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
    sales_dec = Decimal(str(sales))
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
    z = Decimal('0.717')*X1 + Decimal('0.847')*X2 + Decimal('3.107')*X3 + Decimal('0.420')*X4 + Decimal('0.998')*X5
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
        thresholds=thresholds
    )

def altman_zscore_public(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
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
    z = Decimal('6.56')*X1 + Decimal('3.26')*X2 + Decimal('6.72')*X3 + Decimal('1.05')*X4
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
        thresholds=thresholds
    )

def altman_zscore_em(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    calc = FinancialMetricsCalculator
    wc_dec = Decimal(str(working_capital))
    re_dec = Decimal(str(retained_earnings))
    ebit_dec = Decimal(str(ebit))
    mve_dec = Decimal(str(market_value_equity))
    ta_dec = Decimal(str(total_assets))
    tl_dec = Decimal(str(total_liabilities))
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
    z = Decimal('3.25') + Decimal('6.56')*X1 + Decimal('3.26')*X2 + Decimal('6.72')*X3 + Decimal('1.05')*X4
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
        thresholds=thresholds
    )
