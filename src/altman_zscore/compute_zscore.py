"""
Altman Z-Score Calculation Scaffold (MVP)

This module provides a clean, testable interface for Altman Z-Score calculation, model selection,
and calibration. It is designed for incremental development and validation against academic sources.

Key responsibilities:
- Define the core Z-Score calculation logic (original, private, service, EM, etc.)
- Provide a pure function interface for Z-Score computation
- Support model calibration by industry and company maturity
- Enable unit testing and validation against published Altman Z-Score examples

TODO:
- Implement each model's formula as a pure function
- Add calibration constants and thresholds (see PLAN.md, PAPER.md, and literature)
- Add docstring examples for each model
- Add unit tests for each model and calibration
"""
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class FinancialMetrics:
    current_assets: float
    current_liabilities: float
    retained_earnings: float
    ebit: float
    market_value_equity: float
    total_assets: float
    total_liabilities: float
    sales: float
    period_end: Any = None

    @staticmethod
    def from_dict(q: Dict[str, Any], mve: float, period_end: Any):
        """
        Create FinancialMetrics from a dict (quarterly data), market value equity, and period_end.
        """
        return FinancialMetrics(
            current_assets=q.get("current_assets", 0.0),
            current_liabilities=q.get("current_liabilities", 0.0),
            retained_earnings=q.get("retained_earnings", 0.0),
            ebit=q.get("ebit", 0.0),
            market_value_equity=mve if mve is not None else 0.0,
            total_assets=q.get("total_assets", 0.0),
            total_liabilities=q.get("total_liabilities", 0.0),
            sales=q.get("sales", 0.0),
            period_end=period_end
        )

@dataclass
class ZScoreResult:
    z_score: float
    model: str
    components: Dict[str, float]
    diagnostic: str
    thresholds: Dict[str, float]

def safe_div(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator

# --- Model formulas ---
def altman_zscore_service(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_assets: float,
    total_liabilities: float,
    sales: float
) -> ZScoreResult:
    """
    Altman Z-Score (Service/Non-Manufacturing, 1993 revision).
    Z = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    X1 = (Current Assets - Current Liabilities) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    (No X5/Sales term)
    """
    X1 = safe_div(working_capital, total_assets)
    X2 = safe_div(retained_earnings, total_assets)
    X3 = safe_div(ebit, total_assets)
    X4 = safe_div(market_value_equity, total_liabilities)
    if None in (X1, X2, X3, X4):
        raise ValueError("Division by zero in one or more Z-Score components (service model)")
    # All are guaranteed float now
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
    """
    Altman Z-Score (Original, 1968) for public manufacturing firms.
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    X1 = (Current Assets - Current Liabilities) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    X5 = Sales / Total Assets

    Example (from Sonos Q1 FY2025, see OneStockAnalysis.md):
        X1 = (453.0 - 286.9) / 453.0 = 0.366
        X2 = -12.8 / 453.0 = -0.028
        X3 = -69.7 / 453.0 = -0.154
        X4 = 1031.5 / 344.5 = 2.994
        X5 = 259.8 / 453.0 = 0.574
        Z = 1.2*0.366 + 1.4*(-0.028) + 3.3*(-0.154) + 0.6*2.994 + 1.0*0.574 = 2.262
    """
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
    """
    Altman Z-Score (Private Manufacturing Firms, 1983 revision).
    Z' = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
    X1 = (Current Assets - Current Liabilities) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Book Value of Equity / Total Liabilities
    X5 = Sales / Total Assets
    Thresholds (typical):
        Safe: >2.9
        Grey: 1.23–2.9
        Distress: <1.23
    """
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
    """
    Altman Z-Score (Public Non-Manufacturing Firms, 1995 revision, aka Z'').
    Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    X1 = (Current Assets - Current Liabilities) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    (No X5/Sales term)
    Thresholds (typical):
        Safe: >2.6
        Grey: 1.1–2.6
        Distress: <1.1
    """
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
    """
    Altman Z-Score (Emerging Market, Z-Score EM, 1995/2000 revision).
    Z = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    X1 = (Current Assets - Current Liabilities) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    (No X5/Sales term)
    Thresholds (typical, per Altman 2005):
        Safe: >2.6
        Grey: 1.1–2.6
        Distress: <1.1
    """
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

def compute_zscore(metrics: Dict[str, float], model: str = "original") -> ZScoreResult:
    """
    Compute Altman Z-Score using the selected model.
    Args:
        metrics: Dict with required fields (see model docstrings)
        model: Which model to use ("original", "private", etc.)
    Returns:
        ZScoreResult
    """
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
    # TODO: Add other models
    raise NotImplementedError(f"Model '{model}' not implemented yet.")

# --- Calibration and model selection stubs ---
def determine_zscore_model(profile: Any) -> str:
    """
    Select the correct Altman Z-Score model based on company profile (industry, maturity, public/private).
    Args:
        profile: Company profile object with at least 'industry' and 'is_public' attributes.
    Returns:
        Model string: 'original', 'private', 'service', 'public', or 'em'
    """
    industry = getattr(profile, 'industry', '').lower() if hasattr(profile, 'industry') else ''
    is_public = getattr(profile, 'is_public', True) if hasattr(profile, 'is_public') else True
    is_emerging = getattr(profile, 'is_emerging_market', False) if hasattr(profile, 'is_emerging_market') else False

    if is_emerging:
        return 'em'
    if industry in ['manufacturing', 'hardware', 'industrial']:
        return 'original' if is_public else 'private'
    if industry in ['service', 'software', 'tech', 'technology']:
        return 'public' if is_public else 'private'
    # Default fallback
    return 'original'

# --- For testability, add unit tests and docstring examples in a separate test module ---
