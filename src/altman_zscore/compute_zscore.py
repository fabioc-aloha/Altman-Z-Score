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

from typing import Dict, Any, Optional

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

    Args:
        working_capital (float): Working capital
        retained_earnings (float): Retained earnings
        ebit (float): Earnings before interest and taxes
        market_value_equity (float): Market value of equity
        total_assets (float): Total assets
        total_liabilities (float): Total liabilities
        sales (float): Sales/revenue

    Returns:
        ZScoreResult: Object containing the computed Z-Score and component values
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

    Args:
        working_capital (float): Working capital
        retained_earnings (float): Retained earnings
        ebit (float): Earnings before interest and taxes
        market_value_equity (float): Market value of equity
        total_assets (float): Total assets
        total_liabilities (float): Total liabilities
        sales (float): Sales/revenue

    Returns:
        ZScoreResult: Object containing the computed Z-Score and component values
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

    Args:
        working_capital (float): Working capital
        retained_earnings (float): Retained earnings
        ebit (float): Earnings before interest and taxes
        book_value_equity (float): Book value of equity
        total_assets (float): Total assets
        total_liabilities (float): Total liabilities
        sales (float): Sales/revenue

    Returns:
        ZScoreResult: Object containing the computed Z-Score and component values
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

    Args:
        working_capital (float): Working capital
        retained_earnings (float): Retained earnings
        ebit (float): Earnings before interest and taxes
        market_value_equity (float): Market value of equity
        total_assets (float): Total assets
        total_liabilities (float): Total liabilities
        sales (float): Sales/revenue

    Returns:
        ZScoreResult: Object containing the computed Z-Score and component values
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

    Args:
        working_capital (float): Working capital
        retained_earnings (float): Retained earnings
        ebit (float): Earnings before interest and taxes
        market_value_equity (float): Market value of equity
        total_assets (float): Total assets
        total_liabilities (float): Total liabilities
        sales (float): Sales/revenue

    Returns:
        ZScoreResult: Object containing the computed Z-Score and component values
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
    Compute the Altman Z-Score for a given set of financial metrics and model.

    Args:
        metrics (dict): Financial metrics (see FinancialMetrics)
        model (str): Z-Score model name (e.g., 'original', 'private', 'tech')
    Returns:
        ZScoreResult: Object with z_score and all intermediate values
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
    if model == "tech":
        # Tech model: use public model formula, with different thresholds
        X1 = safe_div(metrics["current_assets"] - metrics["current_liabilities"], metrics["total_assets"])
        X2 = safe_div(metrics["retained_earnings"], metrics["total_assets"])
        X3 = safe_div(metrics["ebit"], metrics["total_assets"])
        X4 = safe_div(metrics.get("market_value_equity", 1e9), metrics.get("total_liabilities", metrics["current_liabilities"]))
        if None in (X1, X2, X3, X4):
            raise ValueError("Division by zero in one or more Z-Score components (tech model)")
        X1 = X1 if X1 is not None else 0.0
        X2 = X2 if X2 is not None else 0.0
        X3 = X3 if X3 is not None else 0.0
        X4 = X4 if X4 is not None else 0.0
        z = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4        # Thresholds based on company maturity (example logic)
        if metrics.get("company_maturity") == "young":
            thresholds = {"safe": 1.5, "grey": 0.5, "distress": 0.5}
        else:
            thresholds = {"safe": 2.6, "grey": 1.1, "distress": 1.1}
            
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
    # If model is not one of the implemented models, raise error
    raise NotImplementedError(f"Model '{model}' not implemented yet.")

# --- Calibration and model selection ---
def determine_zscore_model(profile: Any) -> str:
    """
    Select the correct Altman Z-Score model based on company profile attributes.

    Args:
        profile (Any): Company profile object with at least 'industry' and 'is_public' attributes. May also have 'is_emerging_market'.

    Returns:
        str: Model string ('original', 'private', 'service', 'public', or 'em')
            - 'original': Public manufacturing/industrial
            - 'private': Private manufacturing/industrial
            - 'service': Service/financial/tech (public or private)
            - 'public': Public non-manufacturing/tech
            - 'em': Emerging market
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

def select_zscore_model_by_sic(sic_code: str, is_public: bool = True, maturity: Optional[str] = None) -> str:
    """
    Select the Altman Z-Score model type based on SIC code, public/private status, and optional maturity.

    Args:
        sic_code (str): SIC code as a string (empty string for missing/unknown)
        is_public (bool, optional): Whether the company is public. Defaults to True.
        maturity (Optional[str], optional): Optional maturity string (e.g., 'private', 'emerging'). Not currently used in logic.

    Returns:
        str: Model type ('original', 'private', 'service', 'public', 'tech', 'em')
            - 'original': Public manufacturing/industrial (SIC 2000-3999)
            - 'private': Private manufacturing/industrial (SIC 2000-3999)
            - 'tech': Tech/software (SIC 3570-3579, 3670-3679, 7370-7379)
            - 'service': Financial/general services (SIC 6000-8999)
            - fallback: 'original' for missing/invalid SIC or unclassified
    """
    if sic_code.strip() == "":
        return 'original'  # fallback to original if SIC is missing or empty
    try:
        sic = int(str(sic_code))
    except Exception:
        return 'original'  # fallback to original if SIC is invalid
    # Manufacturing (Original/Private): 2000-3999
    if 2000 <= sic <= 3999:
        return 'original' if is_public else 'private'
    # Tech: 3570-3579, 3670-3679, 7370-7379
    if (3570 <= sic <= 3579) or (3670 <= sic <= 3679) or (7370 <= sic <= 7379):
        return 'tech' if is_public else 'private'
    # Financial Services: 6000-6999
    if 6000 <= sic <= 6999:
        return 'service' if is_public else 'private'
    # General Services: 7000-8999
    if 7000 <= sic <= 8999:
        return 'service' if is_public else 'private'
    # Emerging markets (if flagged elsewhere)
    # Add more rules as needed
    return 'original'  # fallback

# --- For testability, add unit tests and docstring examples in a separate test module ---
