"""
Z-Score Chart Components

Individual chart components for Z-Score analysis visualization.
Each class handles one specific chart type with single responsibility.
"""

import plotly.graph_objects as go
from typing import List

from .base import ChartBase
from ...zscore_calculation import ZScoreCalculationResult


class ZScoreGauge(ChartBase):
    """Chart component for Z-Score gauge/bar display."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, zscore_result: ZScoreCalculationResult, **kwargs) -> None:
        """Add Z-Score gauge as bar chart to figure."""
        risk_colors = {'Safe': 'green', 'Grey Zone': 'yellow', 'Distress': 'red'}
        color = risk_colors.get(zscore_result.risk_category, 'blue')
        
        fig.add_trace(
            go.Bar(
                x=['Z-Score'],
                y=[zscore_result.z_score],
                marker_color=color,
                name=f'Z-Score: {zscore_result.z_score:.2f}',
                text=[f'{zscore_result.z_score:.2f}<br>{zscore_result.risk_category}'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add risk zone reference lines
        self.add_risk_zone_lines(fig, row, col)


class ComponentBreakdown(ChartBase):
    """Chart component for Z-Score component breakdown."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, zscore_result: ZScoreCalculationResult, **kwargs) -> None:
        """Add component breakdown bar chart to figure."""
        # Filter to only numeric values to avoid formatting errors
        numeric_components = {}
        for key, value in zscore_result.component_values.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_components[key] = value
        
        components = list(numeric_components.keys())
        values = list(numeric_components.values())
        
        # Shorten component names for better display
        short_names = self._get_short_component_names(components)
        
        fig.add_trace(
            go.Bar(
                x=short_names,
                y=values,
                name="Z-Score Components",
                marker_color='lightblue',
                text=[self.format_value(v, 2) for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _get_short_component_names(self, components: List[str]) -> List[str]:
        """Convert component names to shorter display versions."""
        short_names = []
        for comp in components:
            if 'working_capital' in comp:
                short_names.append('Working<br>Capital')
            elif 'retained_earnings' in comp:
                short_names.append('Retained<br>Earnings')
            elif 'ebit' in comp:
                short_names.append('EBIT<br>Ratio')
            elif 'market_equity' in comp:
                short_names.append('Market<br>Equity')
            elif 'asset_turnover' in comp:
                short_names.append('Asset<br>Turnover')
            else:
                short_names.append(comp.replace('_', '<br>'))
        return short_names


class RiskZoneChart(ChartBase):
    """Chart component for risk zone visualization."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, zscore_result: ZScoreCalculationResult, **kwargs) -> None:
        """Add risk zone scatter plot to figure."""
        # Risk zones
        risk_zones = [
            {'name': 'Distress Zone', 'min': 0, 'max': 1.8, 'color': 'red'},
            {'name': 'Grey Zone', 'min': 1.8, 'max': 2.99, 'color': 'orange'},
            {'name': 'Safe Zone', 'min': 2.99, 'max': 10, 'color': 'green'}
        ]
        
        # Add risk zone backgrounds
        for zone in risk_zones:
            fig.add_shape(
                type="rect",
                x0=0, y0=zone['min'], x1=1, y1=zone['max'],
                fillcolor=zone['color'], opacity=0.2,
                row=row, col=col
            )
        
        # Add current Z-Score point
        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[zscore_result.z_score],
                mode='markers',
                marker=dict(size=24, color=self.get_risk_color(zscore_result.z_score)),
                name=f"Current Z-Score ({zscore_result.z_score:.2f})"
            ),
            row=row, col=col
        )
