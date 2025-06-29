"""
Dashboard Layout Manager

Manages dashboard layouts and subplot configurations based on available analysis components.
Provides flexible layout creation for different analysis scenarios.
"""

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import Any, Optional, Tuple
from enum import Enum

from ....common.logging_config import get_logger

logger = get_logger(__name__)


class LayoutType(Enum):
    """Enumeration of available dashboard layout types."""
    FULL_ENHANCED = "full_enhanced"  # Market + AI analysis
    MARKET_ONLY = "market_only"      # Market analysis without AI
    AI_ONLY = "ai_only"              # AI analysis without market
    BASIC = "basic"                  # Z-Score only


class DashboardLayoutManager:
    """
    Manages dashboard layout creation and configuration.
    
    Provides different layout configurations based on available analysis components
    and ensures consistent subplot organization across different scenarios.
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def determine_layout_type(self, market_analysis: Any, comprehensive_ai_analysis: Any) -> LayoutType:
        """
        Determine the appropriate layout type based on available analysis components.
        
        Args:
            market_analysis: Market analysis results (optional)
            comprehensive_ai_analysis: AI analysis results (optional)
            
        Returns:
            LayoutType: The appropriate layout type
        """
        if market_analysis and comprehensive_ai_analysis:
            return LayoutType.FULL_ENHANCED
        elif market_analysis:
            return LayoutType.MARKET_ONLY
        elif comprehensive_ai_analysis:
            return LayoutType.AI_ONLY
        else:
            return LayoutType.BASIC
    
    def create_dashboard_layout(self, layout_type: LayoutType) -> Tuple[go.Figure, dict]:
        """
        Create a dashboard layout based on the specified type.
        
        Args:
            layout_type: The type of layout to create
            
        Returns:
            Tuple of (Figure, layout_config) where layout_config contains
            positioning information for different chart components
        """
        if layout_type == LayoutType.FULL_ENHANCED:
            return self._create_full_enhanced_layout()
        elif layout_type == LayoutType.MARKET_ONLY:
            return self._create_market_only_layout()
        elif layout_type == LayoutType.AI_ONLY:
            return self._create_ai_only_layout()
        else:
            return self._create_basic_layout()
    
    def _create_full_enhanced_layout(self) -> Tuple[go.Figure, dict]:
        """Create layout for full enhanced dashboard with both market and AI analysis."""
        fig = make_subplots(
            rows=5, cols=3,
            subplot_titles=(
                'Z-Score Analysis', 'Component Breakdown', 'Investment Recommendation',
                'AI Data Quality', 'AI Peer Analysis', 'AI Sentiment Analysis',
                'AI Risk Assessment', 'Technical Indicators', 'Valuation Metrics',
                'Performance Metrics', 'Risk-Return Analysis', 'AI Confidence',
                'Z-Score & Price Trend', '', ''
            ),
            specs=[
                [{"type": "xy"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "indicator"}, {"type": "bar"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "xy"}, {"type": "indicator"}],
                [{"type": "xy", "secondary_y": True, "colspan": 3}, None, None]
            ],
            row_heights=[0.2, 0.2, 0.2, 0.2, 0.2],
            vertical_spacing=0.06
        )
        
        layout_config = {
            'title_suffix': ' | Full AI-Enhanced Analysis',
            'height': 1600,
            'positions': {
                'zscore_gauge': (1, 1),
                'component_breakdown': (1, 2),
                'investment_recommendation': (1, 3),
                'ai_data_quality': (2, 1),
                'ai_peer_analysis': (2, 2),
                'ai_sentiment': (2, 3),
                'ai_risk': (3, 1),
                'technical_indicators': (3, 2),
                'valuation_metrics': (3, 3),
                'performance_metrics': (4, 1),
                'risk_return_analysis': (4, 2),
                'ai_confidence': (4, 3),
                'trend_chart': (5, 1)
            }
        }
        
        return fig, layout_config
    
    def _create_market_only_layout(self) -> Tuple[go.Figure, dict]:
        """Create layout for market analysis without AI."""
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=(
                'Z-Score Analysis', 'Component Breakdown', 'Investment Recommendation',
                'Data Quality Metrics', 'Technical Indicators', 'Valuation Metrics',
                'Performance Metrics', 'Risk-Return Analysis', '',
                'Z-Score & Price Trend', '', ''
            ),
            specs=[
                [{"type": "xy"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "xy"}, {"type": "xy"}],
                [{"type": "xy", "secondary_y": True, "colspan": 3}, None, None]
            ],
            row_heights=[0.25, 0.25, 0.25, 0.25],
            vertical_spacing=0.08
        )
        
        layout_config = {
            'title_suffix': ' | Market Analysis Enhanced',
            'height': 1400,
            'positions': {
                'zscore_gauge': (1, 1),
                'component_breakdown': (1, 2),
                'investment_recommendation': (1, 3),
                'data_quality': (2, 1),
                'technical_indicators': (2, 2),
                'valuation_metrics': (2, 3),
                'performance_metrics': (3, 1),
                'risk_return_analysis': (3, 2),
                'trend_chart': (4, 1)
            }
        }
        
        return fig, layout_config
    
    def _create_ai_only_layout(self) -> Tuple[go.Figure, dict]:
        """Create layout for AI analysis without market data."""
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=(
                'Z-Score Analysis', 'Component Breakdown', 'AI Data Quality',
                'AI Peer Analysis', 'AI Sentiment Analysis', 'AI Risk Assessment',
                'AI Confidence', 'Data Quality', '',
                'Z-Score & Price Trend', '', ''
            ),
            specs=[
                [{"type": "xy"}, {"type": "bar"}, {"type": "indicator"}],
                [{"type": "bar"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "bar"}, {"type": "xy"}],
                [{"type": "xy", "secondary_y": True, "colspan": 3}, None, None]
            ],
            row_heights=[0.25, 0.25, 0.25, 0.25],
            vertical_spacing=0.08
        )
        
        layout_config = {
            'title_suffix': ' | AI-Enhanced',
            'height': 1400,
            'positions': {
                'zscore_gauge': (1, 1),
                'component_breakdown': (1, 2),
                'ai_data_quality': (1, 3),
                'ai_peer_analysis': (2, 1),
                'ai_sentiment': (2, 2),
                'ai_risk': (2, 3),
                'ai_confidence': (3, 1),
                'data_quality': (3, 2),
                'trend_chart': (4, 1)
            }
        }
        
        return fig, layout_config
    
    def _create_basic_layout(self) -> Tuple[go.Figure, dict]:
        """Create basic layout for Z-Score only analysis."""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Z-Score Analysis', 'Component Breakdown',
                'Data Quality Metrics', 'Risk Zone Analysis',
                'Z-Score & Price Trend', ''
            ),
            specs=[
                [{"type": "xy"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "xy"}],
                [{"type": "xy", "secondary_y": True, "colspan": 2}, None]
            ],
            row_heights=[0.3, 0.3, 0.4],
            vertical_spacing=0.08
        )
        
        layout_config = {
            'title_suffix': '',
            'height': 1000,
            'positions': {
                'zscore_gauge': (1, 1),
                'component_breakdown': (1, 2),
                'data_quality': (2, 1),
                'risk_zone_chart': (2, 2),
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
            title=f"Altman Z-Score Analysis Dashboard - {ticker}{layout_config['title_suffix']}",
            height=layout_config['height'],
            showlegend=True
        )
        
        # Configure x-axis font sizes to prevent label overlap
        fig.update_xaxes(tickfont=dict(size=10))
        
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
