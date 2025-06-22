"""
Chart Generator - Create visualizations for Z-Score analysis

This module generates interactive charts and visualizations from Z-Score results,
providing visual insights into financial health and risk assessment.

Key Features:
- Z-Score trend charts with risk zone indicators
- Component breakdown visualizations
- Comparative analysis charts
- Interactive HTML charts with Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class ChartGenerator:
    """Generator for Z-Score visualization charts."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize chart generator.
        
        Args:
            output_base_path: Base directory for output files
        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_zscore_dashboard(self, zscore_result: ZScoreCalculationResult) -> str:
        """
        Generate comprehensive Z-Score dashboard chart.
        
        Args:
            zscore_result: Z-Score calculation result
            
        Returns:
            str: Path to generated HTML chart file
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            chart_path = ticker_dir / f"{zscore_result.ticker}_zscore_dashboard.html"
            
            # Create subplot figure
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Z-Score Overview',
                    'Component Breakdown', 
                    'Risk Zone Analysis',
                    'Data Quality Metrics'
                ),
                specs=[[{"type": "indicator"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "pie"}]]
            )
            
            # Add Z-Score gauge
            self._add_zscore_gauge(fig, zscore_result, row=1, col=1)
            
            # Add component breakdown
            self._add_component_breakdown(fig, zscore_result, row=1, col=2)
            
            # Add risk zone analysis
            self._add_risk_zone_chart(fig, zscore_result, row=2, col=1)
            
            # Add data quality pie chart
            self._add_data_quality_chart(fig, zscore_result, row=2, col=2)
            
            # Update layout
            fig.update_layout(
                title=f"Altman Z-Score Analysis Dashboard - {zscore_result.ticker}",
                height=800,
                showlegend=True
            )
            
            # Save to HTML
            fig.write_html(str(chart_path))
            
            logger.info(f"Z-Score dashboard generated: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            error_msg = f"Failed to generate dashboard for {zscore_result.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _add_zscore_gauge(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add Z-Score gauge indicator."""
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=zscore_result.z_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Z-Score"},
                delta={'reference': 2.99},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': self._get_risk_color(zscore_result.z_score)},
                    'steps': [
                        {'range': [0, 1.8], 'color': "red"},
                        {'range': [1.8, 2.99], 'color': "yellow"},
                        {'range': [2.99, 10], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 2.99
                    }
                }
            ),
            row=row, col=col
        )
    
    def _add_component_breakdown(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add component breakdown bar chart."""
        components = list(zscore_result.component_values.keys())
        values = list(zscore_result.component_values.values())
        
        fig.add_trace(
            go.Bar(
                x=components,
                y=values,
                name="Z-Score Components",
                marker_color='lightblue'
            ),
            row=row, col=col
        )
    
    def _add_risk_zone_chart(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add risk zone scatter plot."""
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
                marker=dict(size=15, color=self._get_risk_color(zscore_result.z_score)),
                name=f"Current Z-Score ({zscore_result.z_score:.2f})"
            ),
            row=row, col=col
        )
    
    def _add_data_quality_chart(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add data quality pie chart."""
        quality_score = zscore_result.data_quality_score
        missing_score = 100 - quality_score
        
        fig.add_trace(
            go.Pie(
                labels=['Data Available', 'Data Missing'],
                values=[quality_score, missing_score],
                marker_colors=['green', 'red']
            ),
            row=row, col=col
        )
    
    def _get_risk_color(self, z_score: float) -> str:
        """Get color based on Z-Score risk level."""
        if z_score < 1.8:
            return "red"
        elif z_score < 2.99:
            return "orange"
        else:
            return "green"
