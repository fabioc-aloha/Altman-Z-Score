"""Module for computing Altman Z-Score and related metrics."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from .config import ZSCORE_PARAMS, ZSCORE_THRESHOLDS


@dataclass
class FinancialMetrics:
    """Container for financial metrics used in Z-score calculation."""
    current_assets: float
    current_liabilities: float
    total_assets: float
    retained_earnings: float
    ebit: float
    total_liabilities: float
    sales: float
    market_value_equity: float
    date: datetime

    @classmethod
    def from_dict(cls, fin: Dict[str, float], mve: float, date: datetime) -> 'FinancialMetrics':
        """Create FinancialMetrics from a dictionary of financial data."""
        return cls(
            current_assets=fin["CA"],
            current_liabilities=fin["CL"],
            total_assets=fin["TA"],
            retained_earnings=fin["RE"],
            ebit=fin["EBIT"],
            total_liabilities=fin["TL"],
            sales=fin["Sales"],
            market_value_equity=mve,
            date=date
        )


@dataclass
class ZScoreComponents:
    """Container for individual Z-score components and final score."""
    working_capital_ratio: float  # X1
    retained_earnings_ratio: float  # X2
    ebit_ratio: float  # X3
    market_value_ratio: float  # X4
    asset_turnover: float  # X5
    z_score: float
    diagnostic: str
    date: datetime

    @property
    def as_dict(self) -> Dict[str, float]:
        """Convert components to a dictionary."""
        return {
            "A": self.working_capital_ratio,
            "B": self.retained_earnings_ratio,
            "C": self.ebit_ratio,
            "D": self.market_value_ratio,
            "E": self.asset_turnover,
            "Z-Score": self.z_score,
            "Diagnostic": self.diagnostic,
            "Date": self.date
        }


class ZScoreCalculator:
    """Class for calculating Altman Z-Score and performing trend analysis."""
    
    def __init__(self):
        """Initialize the calculator with default parameters."""
        self.history: List[ZScoreComponents] = []
    
    def compute_components(self, metrics: FinancialMetrics) -> ZScoreComponents:
        """Compute Z-score components from financial metrics."""
        # Calculate individual components
        x1 = (metrics.current_assets - metrics.current_liabilities) / metrics.total_assets
        x2 = metrics.retained_earnings / metrics.total_assets
        x3 = metrics.ebit / metrics.total_assets
        x4 = metrics.market_value_equity / metrics.total_liabilities
        x5 = metrics.sales / metrics.total_assets
        
        # Calculate Z-score
        z_score = (
            ZSCORE_PARAMS['X1_WEIGHT'] * x1 +
            ZSCORE_PARAMS['X2_WEIGHT'] * x2 +
            ZSCORE_PARAMS['X3_WEIGHT'] * x3 +
            ZSCORE_PARAMS['X4_WEIGHT'] * x4 +
            ZSCORE_PARAMS['X5_WEIGHT'] * x5
        )
        
        # Determine diagnostic zone
        diagnostic = (
            "Safe Zone" if z_score > ZSCORE_THRESHOLDS['SAFE'] else
            "Grey Zone" if z_score >= ZSCORE_THRESHOLDS['GREY'] else
            "Distress Zone"
        )
        
        # Create and store components
        components = ZScoreComponents(
            working_capital_ratio=x1,
            retained_earnings_ratio=x2,
            ebit_ratio=x3,
            market_value_ratio=x4,
            asset_turnover=x5,
            z_score=z_score,
            diagnostic=diagnostic,
            date=metrics.date
        )
        self.history.append(components)
        return components
    
    def analyze_trend(self, periods: int = 4) -> Optional[pd.DataFrame]:
        """Analyze Z-score trend over the specified number of periods."""
        if len(self.history) < 2:
            return None
            
        # Convert history to DataFrame
        df = pd.DataFrame([comp.as_dict for comp in self.history])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Calculate period-over-period changes
        df['Z-Score Change'] = df['Z-Score'].diff()
        df['Trend'] = df['Z-Score Change'].apply(
            lambda x: 'Improving' if x > 0 else 'Deteriorating' if x < 0 else 'Stable'
        )
        
        return df.tail(periods)
