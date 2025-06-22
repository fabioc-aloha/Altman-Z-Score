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
def altman_zscore_original(metrics: Dict[str, float]) -> ZScoreResult:
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

    # Extract and validate required fields
    required_fields = [
        "working_capital",
        "retained_earnings",
        "ebit",
        "market_value_equity",
        "total_assets",
        "total_liabilities",
        "sales",
    ]

    working_capital, retained_earnings, ebit, market_value_equity, total_assets, total_liabilities, sales = _extract_metrics(
        metrics, required_fields
    )

    # Convert to Decimal for precise calculations
    ta = Decimal(str(total_assets))
    wc = Decimal(str(working_capital))
    re = Decimal(str(retained_earnings))
    eb = Decimal(str(ebit))
    me = Decimal(str(market_value_equity))
    tl = Decimal(str(total_liabilities))
    sa = Decimal(str(sales))
    
    # Check for non-zero total assets
    if ta == Decimal("0"):
        ta = Decimal("1")  # Prevent division by zero
        
    # Calculate ratios
    X1 = _safe_decimal_div(wc, ta)  # Working Capital/Total Assets
    X2 = _safe_decimal_div(re, ta)  # Retained Earnings/Total Assets
    X3 = _safe_decimal_div(eb, ta)  # EBIT/Total Assets
    X4 = _safe_decimal_div(me, tl)  # Market Value Equity/Total Liabilities
    X5 = _safe_decimal_div(sa, ta)  # Sales/Total Assets

    # Get coefficients
    c = MODEL_COEFFICIENTS["original"]

    # Calculate weighted components
    weighted_components = {
        "X1_WC/TA": X1 * Decimal(str(c["X1"])),
        "X2_RE/TA": X2 * Decimal(str(c["X2"])),
        "X3_EBIT/TA": X3 * Decimal(str(c["X3"])),
        "X4_MVE/TL": X4 * Decimal(str(c["X4"])),
        "X5_S/TA": X5 * Decimal(str(c["X5"]))
    }

    # Calculate Z-Score
    zscore = sum(weighted_components.values())

    # Determine diagnostic zone
    thresholds = Z_SCORE_THRESHOLDS["original"]
    safe_cutoff = thresholds["SAFE"]
    distress_cutoff = thresholds["DISTRESS"]
    if zscore > safe_cutoff:
        diagnostic = "Safe Zone"
    elif zscore < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    result = ZScoreResult(
        z_score=zscore,
        model="original",
        components={
            "X1_WC/TA": X1,
            "X2_RE/TA": X2,
            "X3_EBIT/TA": X3,
            "X4_MVE/TL": X4,
            "X5_S/TA": X5,
        },
        diagnostic=diagnostic,
        thresholds=thresholds,
    )

    return result


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
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(bve, tl)
    X5 = _safe_decimal_div(sales_dec, ta)
    z = (
        coeffs["X1"] * X1
        + coeffs["X2"] * X2
        + coeffs["X3"] * X3
        + coeffs["X4"] * X4
        + coeffs["X5"] * X5
    )

    thresholds = Z_SCORE_THRESHOLDS["private"]
    safe_cutoff = thresholds["SAFE"]
    distress_cutoff = thresholds["DISTRESS"]

    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    components = {
        "X1_WC/TA": X1,
        "X2_RE/TA": X2,
        "X3_EBIT/TA": X3,
        "X4_BVE/TL": X4,
        "X5_S/TA": X5,
    }
    return ZScoreResult(
        z_score=z,
        model="private",
        components=components,
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

    Thresholds (public): distress ≤ 1.10, grey (1.10, 2.60], safe > 2.60
    Thresholds (private): distress ≤ 1.23, grey (1.23, 2.90], safe > 2.90
    """
    import logging
    logger = logging.getLogger(__name__)
    model_key = "service_private" if use_book_value else "service"
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS[model_key]
    logger.debug(f"[altman_zscore_service] Input metrics: {metrics}")
    required_fields = [
        "total_assets",
        "working_capital",
        "retained_earnings",
        "ebit",
        "market_value_equity" if not use_book_value else "book_value_equity",
        "total_liabilities"
    ]
    missing = [f for f in required_fields if f not in metrics or metrics[f] is None]
    if missing:
        logger.error(f"[altman_zscore_service] Missing required fields: {missing}")
        raise ValueError(f"Missing required fields for service model: {missing}")
    try:
        ta = Decimal(str(metrics["total_assets"]))
        wc = Decimal(str(metrics["working_capital"]))
        re = Decimal(str(metrics["retained_earnings"]))
        ebit_dec = Decimal(str(metrics["ebit"]))
        equity_dec = Decimal(str(metrics["market_value_equity"] if not use_book_value else metrics["book_value_equity"]))
        tl = Decimal(str(metrics["total_liabilities"]))
        X1 = _safe_decimal_div(wc, ta)
        X2 = _safe_decimal_div(re, ta)
        X3 = _safe_decimal_div(ebit_dec, ta)
        X4 = _safe_decimal_div(equity_dec, tl)
        logger.debug(f"[altman_zscore_service] Ratios: X1={X1}, X2={X2}, X3={X3}, X4={X4}")
        z = (
            coeffs["X1"] * X1
            + coeffs["X2"] * X2
            + coeffs["X3"] * X3
            + coeffs["X4"] * X4
        )
        logger.debug(f"[altman_zscore_service] Z-Score: {z}")
    except Exception as e:
        logger.error(f"[altman_zscore_service] Error in computation: {e}")
        raise
    thresholds = Z_SCORE_THRESHOLDS[model_key]
    safe_cutoff = thresholds["SAFE"]
    distress_cutoff = thresholds["DISTRESS"]
    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    components = {"X1": X1, "X2": X2, "X3": X3, "X4": X4}
    return ZScoreResult(
        z_score=z,
        model=model_key,
        components=components,
        diagnostic=diagnostic,
        thresholds=thresholds,
    )


# -------------------------------------------------------------------
# 4) Z_EM-Score (2005, EM-Adjusted, five-ratio model)
# -------------------------------------------------------------------
def altman_zscore_em(
    metrics: Dict[str, float]
) -> ZScoreResult:
    """
    Compute Altman Z_EM-Score for emerging market companies (any SIC).

    Five-ratio model:
      X1 = (Current Assets - Current Liabilities) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Book Value of Equity / Total Liabilities
      X5 = Sales / Total Assets
      Z = 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4 + 3.25·X5

    Thresholds: distress ≤ 1.10, grey (1.10, 2.60], safe > 2.60
    """
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS["em"]

    ta = Decimal(str(metrics["total_assets"]))
    wc = Decimal(str(metrics["working_capital"]))
    re = Decimal(str(metrics["retained_earnings"]))
    ebit_dec = Decimal(str(metrics["ebit"]))
    bve = Decimal(str(metrics["book_value_equity"]))
    tl = Decimal(str(metrics["total_liabilities"]))
    sales = Decimal(str(metrics["sales"]))

    # Compute ratios X1..X5, replacing None with Decimal("0")
    X1 = _safe_decimal_div(wc, ta)
    X2 = _safe_decimal_div(re, ta)
    X3 = _safe_decimal_div(ebit_dec, ta)
    X4 = _safe_decimal_div(bve, tl)
    X5 = _safe_decimal_div(sales, ta)

    z = (
        coeffs["X1"] * X1
        + coeffs["X2"] * X2
        + coeffs["X3"] * X3
        + coeffs["X4"] * X4
        + coeffs["X5"] * X5
    )

    thresholds = Z_SCORE_THRESHOLDS["em"]
    safe_cutoff = thresholds["SAFE"]
    distress_cutoff = thresholds["DISTRESS"]

    if z > safe_cutoff:
        diagnostic = "Safe Zone"
    elif z < distress_cutoff:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"

    return ZScoreResult(
        z_score=z,
        model="em",
        components={"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5},
        diagnostic=diagnostic,
        thresholds=thresholds,
    )





# -------------------------------------------------------------------
# 6) Retail Z-Score (Retail-specific with inventory focus)
# -------------------------------------------------------------------
def altman_zscore_retail(metrics: Dict[str, float]) -> ZScoreResult:
    """
    Compute Retail-specific Z-Score for retail companies.

    Six-factor model:
      X1 = (Current Assets - Inventory) / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets
      X6 = Cost of Goods Sold / Average Inventory

    Coefficients: 1.10, 1.40, 3.30, 0.60, 1.20, 0.30

    Thresholds: distress ≤ 1.90, grey (1.90, 3.10], safe > 3.10
    """
    import logging
    logger = logging.getLogger(__name__)
    
    coeffs: Dict[str, Decimal] = MODEL_COEFFICIENTS["retail"]
    # Define thresholds once for retail model
    thresholds = Z_SCORE_THRESHOLDS["retail"]
    safe_cutoff = thresholds["SAFE"]
    distress_cutoff = thresholds["DISTRESS"]
    
    logger.debug(f"[altman_zscore_retail] Input metrics: {metrics}")
      # Check for core fields required by all models
    core_fields = [
        "total_assets",
        "current_assets", 
        "current_liabilities",
        "retained_earnings",
        "ebit",
        "market_value_equity",
        "total_liabilities",
        "sales"
    ]
    
    # Check for retail-specific fields
    retail_fields = [
        "inventory",
        "cost_of_goods_sold",
        "average_inventory"
    ]
    
    missing_core = [f for f in core_fields if f not in metrics or metrics[f] is None]
    missing_retail = [f for f in retail_fields if f not in metrics or metrics[f] is None]
    
    if missing_core:
        logger.error(f"[altman_zscore_retail] Missing core fields: {missing_core}")
        raise ValueError(f"Missing required core fields for retail model: {missing_core}")    
    # If retail fields are missing, fall back to modified original model
    if missing_retail:
        logger.warning(f"[altman_zscore_retail] Missing retail fields {missing_retail}, falling back to modified original model")
        use_retail_formula = False
    else:
        use_retail_formula = True

    try:
        # Compute z and components
        ta = Decimal(str(metrics["total_assets"]))
        ca = Decimal(str(metrics["current_assets"]))
        cl = Decimal(str(metrics["current_liabilities"]))
        re = Decimal(str(metrics["retained_earnings"]))
        ebit_dec = Decimal(str(metrics["ebit"]))
        mve = Decimal(str(metrics["market_value_equity"]))
        tl = Decimal(str(metrics["total_liabilities"]))
        sales_dec = Decimal(str(metrics["sales"]))

        if use_retail_formula:
            # Full retail model with inventory adjustments
            inventory = Decimal(str(metrics["inventory"]))
            cogs = Decimal(str(metrics["cost_of_goods_sold"]))
            avg_inventory = Decimal(str(metrics["average_inventory"]))

            # X1: (Current Assets - Inventory) / Total Assets
            X1 = _safe_decimal_div(ca - inventory, ta)
            
            # X2: Retained Earnings / Total Assets
            X2 = _safe_decimal_div(re, ta)
            
            # X3: EBIT / Total Assets
            X3 = _safe_decimal_div(ebit_dec, ta)
            
            # X4: Market Value of Equity / Total Liabilities
            X4 = _safe_decimal_div(mve, tl)
            
            # X5: Sales / Total Assets
            X5 = _safe_decimal_div(sales_dec, ta)
            
            # X6: Inventory Turnover (Cost of Goods Sold / Average Inventory)
            X6 = _safe_decimal_div(cogs, avg_inventory)
            # Calculate Z-Score
            z = (
                coeffs["X1"] * X1 + coeffs["X2"] * X2 + coeffs["X3"] * X3 +
                coeffs["X4"] * X4 + coeffs["X5"] * X5 + coeffs["X6"] * X6
            )
            components = {"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5, "X6": X6}
        else:
            # Fall back to original-like five-factor retail model: compute base ratios
            wc = ca - cl
            X1 = _safe_decimal_div(wc, ta)
            X2 = _safe_decimal_div(re, ta)
            X3 = _safe_decimal_div(ebit_dec, ta)
            X4 = _safe_decimal_div(mve, tl)
            X5 = _safe_decimal_div(sales_dec, ta)
            z = (coeffs["X1"] * X1 + coeffs["X2"] * X2 + coeffs["X3"] * X3 +
                 coeffs["X4"] * X4 + coeffs["X5"] * X5)
            components = {"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5}
            logger.debug(f"[altman_zscore_retail] Z-Score fallback: {z}")
        
        # Determine diagnostic zone
        if z > safe_cutoff:
            diagnostic = "Safe Zone"
        elif z < distress_cutoff:
            diagnostic = "Distress Zone"
        else:
            diagnostic = "Grey Zone"
        
        return ZScoreResult(
            z_score=z,
            model="retail",
            components=components,
            diagnostic=diagnostic,
            thresholds=thresholds,
        )

    except Exception as e:
        logger.error(f"[altman_zscore_retail] Error in computation: {e}")
        raise
