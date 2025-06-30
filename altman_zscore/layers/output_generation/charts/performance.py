"""
Performance Analysis Chart Components

Chart components for performance metrics and risk-return analysis.
"""

import plotly.graph_objects as go
from typing import Any, Tuple, Optional

from .base import ChartBase
from ....common.logging_config import get_logger

logger = get_logger(__name__)


class PerformanceMetrics(ChartBase):
    """Chart component for performance metrics display."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, market_analysis: Any, **kwargs) -> None:
        """Add performance metrics chart to figure."""
        if not market_analysis or not hasattr(market_analysis, 'market_performance'):
            fig.add_trace(self.create_no_data_bar("Performance Metrics"), row=row, col=col)
            return
            
        perf = market_analysis.market_performance
        
        metrics = ['1D', '1W', '1M', '3M', '6M', '1Y']
        returns = [
            self.safe_get_numeric(perf, 'return_1d') * 100,
            self.safe_get_numeric(perf, 'return_1w') * 100,
            self.safe_get_numeric(perf, 'return_1m') * 100,
            self.safe_get_numeric(perf, 'return_3m') * 100,
            self.safe_get_numeric(perf, 'return_6m') * 100,
            self.safe_get_numeric(perf, 'return_1y') * 100
        ]
        
        colors = ['green' if r > 0 else 'red' for r in returns]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=returns,
                marker_color=colors,
                name='Returns (%)',
                text=[f'{r:.1f}%' for r in returns],
                textposition='auto'
            ),
            row=row, col=col
        )


class RiskReturnAnalysis(ChartBase):
    """Chart component for risk-return scatter plot analysis."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, market_analysis: Any, **kwargs) -> None:
        """Add risk-return scatter plot to figure."""
        if not market_analysis or not hasattr(market_analysis, 'risk_return_profile'):
            self._add_no_data_point(fig, row, col)
            return
            
        risk = market_analysis.risk_return_profile
        perf = getattr(market_analysis, 'market_performance', None)
        
        # Extract actual data - check for None specifically, not falsy values
        volatility_risk = self.safe_get_numeric(risk, 'volatility_risk') if risk else None
        
        # Use the longest available return period
        return_value, return_period = self._get_best_return_period(perf)
        
        # Debug logging to understand data availability
        logger.info(f"Risk-Return Analysis - Volatility: {volatility_risk}, Return {return_period}: {return_value}")
        
        if volatility_risk is not None and return_value is not None:
            x_risk, y_return, color, marker_text = self._prepare_actual_data(
                volatility_risk, return_value, return_period
            )
        else:
            x_risk, y_return, color, marker_text = self._prepare_fallback_data()
        
        fig.add_trace(
            go.Scatter(
                x=[x_risk],
                y=[y_return],
                mode='markers',
                marker=dict(size=15, color=color, symbol='diamond'),
                name='Risk-Return Position',
                text=[marker_text],
                textposition='top center'
            ),
            row=row, col=col
        )
        
        # Add benchmark quadrants
        self._add_quadrant_lines(fig, row, col)
    
    def _get_best_return_period(self, perf: Any) -> Tuple[Optional[float], str]:
        """Get the best available return period from performance data."""
        if not perf:
            return None, ""
            
        return_options = [
            ('return_1y', "1Y"),
            ('return_6m', "6M"),
            ('return_3m', "3M"),
            ('return_1m', "1M"),
            ('return_1w', "1W"),
            ('return_1d', "1D")
        ]
        
        for attr, period in return_options:
            value = self.safe_get_numeric(perf, attr)
            if value != 0:  # Our safe_get_numeric returns 0 for None/invalid
                return value, period
        
        return None, ""
    
    def _prepare_actual_data(self, volatility_risk: float, return_value: float, 
                           return_period: str) -> Tuple[float, float, str, str]:
        """Prepare actual risk-return data for plotting."""
        x_risk = volatility_risk * 100  # Convert 0-1 scale to 0-100%
        y_return = return_value * 100   # Convert decimal to percentage
        
        # Color based on risk-return profile
        if y_return > 10 and x_risk < 25:
            color = 'green'  # High return, low risk
        elif y_return > 0 and x_risk < 30:
            color = 'blue'   # Positive return, moderate risk
        elif y_return < -10:
            color = 'red'    # Negative return
        else:
            color = 'orange' # Neutral
            
        marker_text = f'Risk: {x_risk:.1f}%<br>Return ({return_period}): {y_return:.1f}%'
        logger.info(f"Using actual data: Risk={x_risk:.1f}%, Return ({return_period})={y_return:.1f}%")
        
        return x_risk, y_return, color, marker_text
    
    def _prepare_fallback_data(self) -> Tuple[float, float, str, str]:
        """Prepare fallback data when actual data is missing."""
        x_risk = 50
        y_return = 0
        color = 'gray'
        marker_text = 'Insufficient Data<br>for Risk-Return Analysis'
        logger.info("Using fallback data due to missing values")
        
        return x_risk, y_return, color, marker_text
    
    def _add_no_data_point(self, fig: go.Figure, row: int, col: int) -> None:
        """Add a no-data point to the chart."""
        fig.add_trace(
            go.Scatter(
                x=[50], y=[0],
                mode='markers',
                marker=dict(size=15, color='gray', symbol='diamond'),
                name='No Risk-Return Data',
                text=['No Market Data Available'],
                textposition='top center'
            ),
            row=row, col=col
        )
        self._add_quadrant_lines(fig, row, col)
    
    def _add_quadrant_lines(self, fig: go.Figure, row: int, col: int) -> None:
        """Add quadrant reference lines and labels."""
        try:
            # Add benchmark quadrants with labels
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=col)
            fig.add_vline(x=25, line_dash="dash", line_color="gray", row=row, col=col)
            
            # Add quadrant labels
            fig.add_annotation(
                x=10, y=15, text="Low Risk<br>High Return", 
                showarrow=False, font=dict(size=10, color="green"),
                row=row, col=col
            )
            fig.add_annotation(
                x=40, y=-15, text="High Risk<br>Low Return", 
                showarrow=False, font=dict(size=10, color="red"),
                row=row, col=col
            )
        except Exception:
            # Skip if subplot doesn't support axis operations
            pass
