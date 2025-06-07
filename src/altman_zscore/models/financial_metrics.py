"""
Financial metrics data structures for Z-Score computation in Altman Z-Score analysis.

Defines containers for financial metrics and Z-Score computation results.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict


@dataclass
class FinancialMetrics:
    """Container for financial metrics required for Z-Score computation.

    Attributes:
        current_assets (float): Current assets value.
        current_liabilities (float): Current liabilities value.
        retained_earnings (float): Retained earnings value.
        ebit (float): Earnings before interest and taxes.
        market_value_equity (float): Market value of equity.
        total_assets (float): Total assets value.
        total_liabilities (float): Total liabilities value.
        sales (float): Sales revenue.
        period_end (Any): Period end date or identifier.
    """

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
        """Create FinancialMetrics from a dict (quarterly data), market value equity, and period_end.

        Args:
            q (dict): Dictionary of quarterly financial data.
            mve (float): Market value of equity.
            period_end (Any): Period end date or identifier.

        Returns:
            FinancialMetrics: Instantiated FinancialMetrics object.
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
            period_end=period_end,
        )


@dataclass
class ZScoreResult:
    """Container for Z-Score computation results.

    Attributes:
        z_score (Decimal): Computed Z-Score value.
        model (str): Model identifier.
        components (dict): Dictionary of Z-Score components.
        diagnostic (str): Diagnostic string or label.
        thresholds (dict): Thresholds for Z-Score interpretation.
        override_context (dict): Model/threshold overrides and assumptions.
    """

    z_score: Decimal
    model: str
    components: Dict[str, Decimal]
    diagnostic: str
    thresholds: Dict[str, Decimal]  # Changed from float to Decimal for type safety and precision
    override_context: Dict[str, Any] = field(
        default_factory=dict
    )  # For logging model/threshold overrides and assumptions
