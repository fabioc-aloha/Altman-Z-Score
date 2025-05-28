from typing import Dict
from altman_zscore.models.financial_metrics import ZScoreResult

def safe_div(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator

def altman_zscore_service(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(market_value_equity, total_liabilities)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (service model)")
    X1 = X1 if X1 is not None else 0.0
    X2 = X2 if X2 is not None else 0.0
    X3 = X3 if X3 is not None else 0.0
    X4 = X4 if X4 is not None else 0.0
    z = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    thresholds = {"safe": 2.6, "grey": 1.1, "distress": 1.1}
    if z > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z < thresholds["distress"]:
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
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(market_value_equity, total_liabilities)
    X5 = safe_div(sales, total_assets)
    if None in (X1, X2, X3, X4, X5):
        raise ValueError("Division by zero in one or more Z-Score components (original model)")
    X1 = X1 if X1 is not None else 0.0
    X2 = X2 if X2 is not None else 0.0
    X3 = X3 if X3 is not None else 0.0
    X4 = X4 if X4 is not None else 0.0
    X5 = X5 if X5 is not None else 0.0
    z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    thresholds = {"safe": 2.99, "grey": 1.81, "distress": 1.81}
    if z > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z < thresholds["distress"]:
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
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(book_value_equity, total_liabilities)
    X5 = safe_div(sales, total_assets)
    if None in (X1, X2, X3, X4, X5):
        raise ValueError("Division by zero in one or more Z-Score components (private model)")
    X1 = X1 if X1 is not None else 0.0
    X2 = X2 if X2 is not None else 0.0
    X3 = X3 if X3 is not None else 0.0
    X4 = X4 if X4 is not None else 0.0
    X5 = X5 if X5 is not None else 0.0
    z = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
    thresholds = {"safe": 2.9, "grey": 1.23, "distress": 1.23}
    if z > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z < thresholds["distress"]:
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
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(market_value_equity, total_liabilities)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (public model)")
    X1 = X1 if X1 is not None else 0.0
    X2 = X2 if X2 is not None else 0.0
    X3 = X3 if X3 is not None else 0.0
    X4 = X4 if X4 is not None else 0.0
    z = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    thresholds = {"safe": 2.6, "grey": 1.1, "distress": 1.1}
    if z > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z < thresholds["distress"]:
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
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(market_value_equity, total_liabilities)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (EM model)")
    X1 = X1 if X1 is not None else 0.0
    X2 = X2 if X2 is not None else 0.0
    X3 = X3 if X3 is not None else 0.0
    X4 = X4 if X4 is not None else 0.0
    z = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    thresholds = {"safe": 2.6, "grey": 1.1, "distress": 1.1}
    if z > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z < thresholds["distress"]:
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
