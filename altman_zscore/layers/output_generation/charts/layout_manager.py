"""
Dashboard Layout Manager

Manages dashboard layout and subplot configuration for the Altman Z-Score analysis.
Provides a single, consistent layout for market analysis components.
"""

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import Tuple, Optional

from ....common.logging_config import get_logger

logger = get_logger(__name__)


class DashboardLayoutManager:
    """
    Manages dashboard layout creation and configuration.
    
    Provides a consistent layout configuration for market analysis components.
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def create_dashboard_layout(self, is_bankruptcy_analysis: bool = False) -> Tuple[go.Figure, dict]:
        """
        Create the standard dashboard layout.
        
        Args:
            is_bankruptcy_analysis: Flag indicating if this is a bankruptcy analysis dashboard
        
        Returns:
            Tuple of (Figure, layout_config) where layout_config contains
            positioning information for different chart components
        """
        # Adjust subplot titles for bankruptcy analysis
        if is_bankruptcy_analysis:
            subplot_titles = (
                'Pre-Bankruptcy Z-Score Components', 'Component Breakdown', 'Investment Recommendation',
                'Technical Indicators', 'Valuation Metrics', 'Performance Metrics',
                'Multi-Quarter Trend Analysis (Pre-Bankruptcy)', '', ''
            )
        else:
            subplot_titles = (
                'Z-Score Components', 'Component Breakdown', 'Investment Recommendation',
                'Technical Indicators', 'Valuation Metrics', 'Performance Metrics',
                'Multi-Quarter Trend Analysis', '', ''
            )
        
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=subplot_titles,
            specs=[
                [{"type": "xy"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "xy", "secondary_y": True, "colspan": 3}, None, None]
            ],
            row_heights=[0.25, 0.25, 0.50],
            vertical_spacing=0.15
        )
        
        # Configure layout based on analysis type
        if is_bankruptcy_analysis:
            title_suffix = ' | Pre-Bankruptcy Analysis'
        else:
            title_suffix = ' | Enhanced Market Analysis'
        
        layout_config = {
            'title_suffix': title_suffix,
            'height': 1050,
            'is_bankruptcy_analysis': is_bankruptcy_analysis,
            'positions': {
                'zscore_gauge': (1, 1),
                'component_breakdown': (1, 2),
                'investment_recommendation': (1, 3),
                'technical_indicators': (2, 1),
                'valuation_metrics': (2, 2),
                'performance_metrics': (2, 3),
                'trend_chart': (3, 1)
            }
        }
        
        return fig, layout_config
    
    def configure_final_layout(self, fig: go.Figure, layout_config: dict, ticker: str) -> None:
        """
        Apply final layout configuration to the figure.
        
        Args:
            fig: The plotly figure to configure
            layout_config: Layout configuration dictionary
            ticker: Stock ticker symbol
        """
        fig.update_layout(
            title={
                'text': f"Altman Z-Score Analysis Dashboard - {ticker}{layout_config['title_suffix']}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            height=layout_config['height'],
            showlegend=False,
            margin=dict(t=80, b=60, l=60, r=60)  # Increased top margin for title spacing
        )
        
        # Configure annotations (subplot titles) to prevent overlap
        fig.update_annotations(font_size=11, yshift=10)
        
        # Configure x-axis font sizes to prevent label overlap
        fig.update_xaxes(tickfont=dict(size=10))
        fig.update_yaxes(tickfont=dict(size=10))
        
        self.logger.info(f"Dashboard layout configured: {layout_config['title_suffix']}")
    
    def get_component_position(self, layout_config: dict, component_name: str) -> Optional[Tuple[int, int]]:
        """
        Get the position (row, col) for a specific component in the layout.
        
        Args:
            layout_config: Layout configuration dictionary
            component_name: Name of the component to find
            
        Returns:
            Tuple of (row, col) if found, None otherwise
        """
        return layout_config.get('positions', {}).get(component_name)
