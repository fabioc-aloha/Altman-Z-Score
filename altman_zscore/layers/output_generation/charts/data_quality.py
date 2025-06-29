"""
Data Quality Chart Component

Handles data quality visualization.
"""

import plotly.graph_objects as go

from .base import ChartBase
from ...zscore_calculation import ZScoreCalculationResult


class DataQualityChart(ChartBase):
    """Chart component for data quality metrics."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, zscore_result: ZScoreCalculationResult, **kwargs) -> None:
        """Add data quality bar chart to figure."""
        # Convert decimal to percentage (1.0 -> 100%)
        quality_score = zscore_result.data_quality_score * 100
        missing_score = 100 - quality_score
        
        fig.add_trace(
            go.Bar(
                x=['Data Available', 'Data Missing'],
                y=[quality_score, missing_score],
                marker_color=['green', 'red'],
                name='Data Quality',
                text=[f'{quality_score:.1f}%', f'{missing_score:.1f}%'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
