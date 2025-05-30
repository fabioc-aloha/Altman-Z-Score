from dataclasses import dataclass, field
from typing import Dict, Any
from decimal import Decimal

@dataclass
class FinancialMetrics:
    """
    Container for financial metrics required for Z-Score computation.
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
    """
    Container for Altman Z-Score calculation results.
    
    Attributes:
        z_score: Calculated Z-Score value
        model: Model type used (e.g., 'original', 'private', 'service')
        components: Dictionary of component values (X1, X2, etc.)
        diagnostic: Risk assessment string (e.g., 'Safe', 'Grey Zone', 'Distress')
        thresholds: Risk thresholds for the model
        override_context: Context for any model/threshold overrides
    """
    z_score: Decimal
    model: str
    components: Dict[str, Decimal]
    diagnostic: str
    thresholds: Dict[str, Decimal]  # Changed from float to Decimal for type safety and precision
    override_context: Dict[str, Any] = field(default_factory=dict)  # For logging model/threshold overrides and assumptions
