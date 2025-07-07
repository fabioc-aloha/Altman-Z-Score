"""
Dashboard Generator - Orchestrates Z-Score dashboard creation

This module provides a clean, modular approach to generating Z-Score dashboards
by combining multiple chart components in a structured layout.

Key Features:
- Modular chart component system
- Flexible dashboard layouts based on available data
- Clean separation of concerns
- Enhanced error handling and logging
"""

import plotly.graph_objects as go
from datetime import datetime
from typing import List, Optional, Any
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..zscore_calculation import ZScoreCalculationResult

# Import chart components
from .charts import (
    ZScoreGauge, ComponentBreakdown, RiskZoneChart,
    InvestmentRecommendation, TechnicalIndicators, ValuationMetrics,
    PerformanceMetrics, RiskReturnAnalysis,
    TrendChart, DashboardLayoutManager
)
from .charts.trend_analysis import AICommentaryAnnotation

logger = get_logger(__name__)


class DashboardGenerator:
    """
    Generator for comprehensive Z-Score analysis dashboards.
    
    Uses modular chart components to create rich, interactive dashboards
    with different layouts based on available analysis data.
    """
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize dashboard generator.
        
        Args:
            output_base_path: Base directory for output files        
        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
        
        # Initialize layout manager
        self.layout_manager = DashboardLayoutManager()
        
        # Initialize chart components
        self.zscore_gauge = ZScoreGauge()
        self.component_breakdown = ComponentBreakdown()
        self.risk_zone_chart = RiskZoneChart()
        
        # Market analysis components
        self.investment_recommendation = InvestmentRecommendation()
        self.technical_indicators = TechnicalIndicators()
        self.valuation_metrics = ValuationMetrics()
        self.performance_metrics = PerformanceMetrics()
        self.risk_return_analysis = RiskReturnAnalysis()
        
        # Trend analysis
        self.trend_chart = TrendChart()
        
        # AI commentary
        self.ai_commentary = AICommentaryAnnotation()
    
    def generate_zscore_dashboard(self, zscore_results, market_analysis=None, 
                                comprehensive_ai_analysis=None, start_date: Optional[str] = None) -> str:
        """
        Generate comprehensive Z-Score dashboard chart using multiple periods for trend,
        enhanced with market analysis insights and AI commentary.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results for enhanced insights
            comprehensive_ai_analysis: Optional comprehensive AI analysis results
            start_date (Optional[str]): Optional start date for filtering results (format: YYYY-MM-DD)
            
        Returns:
            str: Path to generated HTML chart file
        """
        try:
            # Normalize input to list of results
            results = zscore_results if isinstance(zscore_results, list) else [zscore_results]
            latest = results[0]
            ticker_dir = self.output_base_path / latest.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            chart_path = ticker_dir / f"{latest.ticker}_zscore_dashboard.html"
            
            # Check if this is a bankruptcy analysis
            is_bankruptcy_analysis = False
            bankruptcy_date = None
            
            if latest.metadata and 'bankruptcy_analysis' in latest.metadata:
                is_bankruptcy_analysis = True
                bankruptcy_date = latest.metadata.get('bankruptcy_date')
                logger.info(f"Generating bankruptcy analysis dashboard for {latest.ticker} with bankruptcy date: {bankruptcy_date}")
            
            # Create dashboard layout
            fig, layout_config = self.layout_manager.create_dashboard_layout(is_bankruptcy_analysis=is_bankruptcy_analysis)
            
            # Add company name and ticker as title
            company_name = latest.metadata.get('company_name', latest.ticker) if hasattr(latest, 'metadata') and latest.metadata else latest.ticker
            
            # Add special title for bankruptcy analysis
            if is_bankruptcy_analysis:
                title = f"<b>{company_name} ({latest.ticker})</b> - Pre-Bankruptcy Z-Score Analysis"
                subtitle = f"<i>Bankruptcy Date: {bankruptcy_date}</i>"
                
                fig.update_layout(
                    title={
                        'text': f"{title}<br><sup>{subtitle}</sup>",
                        'y': 0.98,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'family': 'Arial', 'size': 24, 'color': '#d32f2f'}
                    }
                )
            else:
                title = f"<b>{company_name} ({latest.ticker})</b> - Z-Score Analysis"
                fig.update_layout(
                    title={
                        'text': title,
                        'y': 0.98,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'family': 'Arial', 'size': 24}
                    }
                )
            
            # Add core components that are always present
            self._add_core_components(fig, layout_config, latest)
            
            # Add analysis-specific components based on available data
            self._add_conditional_components(fig, layout_config, latest, market_analysis, comprehensive_ai_analysis)
            
            # Add trend chart (always present, but position varies by layout)
            self._add_trend_component(fig, layout_config, results, market_analysis, start_date)
            
            # Configure final layout
            self.layout_manager.configure_final_layout(fig, layout_config, latest.ticker)
            
            # Add AI commentary if available - DISABLED
            # if comprehensive_ai_analysis:
            #     self.ai_commentary.add_to_figure(fig, comprehensive_ai_analysis)
            
            # Save to HTML
            fig.write_html(str(chart_path))
            
            logger.info(f"Z-Score dashboard generated: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            import traceback
            logger.error(f"Chart generation error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_msg = f"Failed to generate dashboard for {latest.ticker if hasattr(latest, 'ticker') else 'unknown'}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _add_core_components(self, fig: go.Figure, layout_config: dict, latest: Any) -> None:
        """Add core components that are always present."""
        # Z-Score gauge/analysis
        pos = self.layout_manager.get_component_position(layout_config, 'zscore_gauge')
        if pos:
            self.zscore_gauge.add_to_figure(fig, pos[0], pos[1], zscore_result=latest)
        
        # Component breakdown
        pos = self.layout_manager.get_component_position(layout_config, 'component_breakdown')
        if pos:
            self.component_breakdown.add_to_figure(fig, pos[0], pos[1], zscore_result=latest)
        
        # Risk zone chart (basic layout only)
        pos = self.layout_manager.get_component_position(layout_config, 'risk_zone_chart')
        if pos:
            self.risk_zone_chart.add_to_figure(fig, pos[0], pos[1], zscore_result=latest)
    
    def _add_conditional_components(self, fig: go.Figure, layout_config: dict, latest: Any,
                                  market_analysis: Any, comprehensive_ai_analysis: Any) -> None:
        """Add components based on available analysis data."""
        # Market analysis components
        if market_analysis:
            self._add_market_components(fig, layout_config, market_analysis)
    
    def _add_market_components(self, fig: go.Figure, layout_config: dict, market_analysis: Any) -> None:
        """Add market analysis components."""
        components = [
            ('investment_recommendation', self.investment_recommendation),
            ('technical_indicators', self.technical_indicators),
            ('valuation_metrics', self.valuation_metrics),
            ('performance_metrics', self.performance_metrics),
            ('risk_return_analysis', self.risk_return_analysis)
        ]
        
        for component_name, component in components:
            pos = self.layout_manager.get_component_position(layout_config, component_name)
            if pos:
                component.add_to_figure(fig, pos[0], pos[1], market_analysis=market_analysis)

    def _add_trend_component(self, fig: go.Figure, layout_config: dict, results: List[Any],
                           market_analysis: Any, start_date: Optional[str]) -> None:
        """Add trend chart component."""
        pos = self.layout_manager.get_component_position(layout_config, 'trend_chart')
        if pos:
            self.trend_chart.add_to_figure(
                fig, pos[0], pos[1],
                results=results,
                market_analysis=market_analysis,
                start_date=start_date
            )
