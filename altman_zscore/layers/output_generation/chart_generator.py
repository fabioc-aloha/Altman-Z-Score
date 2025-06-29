"""
Chart Generator - Legacy compatibility wrapper

This module provides backward compatibility while transitioning to the new modular chart system.
New code should use DashboardGenerator from dashboard_generator.py directly.

The old monolithic chart_generator.py has been refactored into multiple focused modules:
- dashboard_generator.py: Main dashboard orchestrator
- charts/: Directory containing modular chart components
  - base.py: Base functionality for all components
  - zscore_components.py: Z-Score specific charts
  - market_components.py: Market analysis charts
  - performance.py: Performance and risk-return analysis
  - ai_components.py: AI analysis charts
  - trend_analysis.py: Trend and time series charts
  - data_quality.py: Data quality visualization
  - layout_manager.py: Dashboard layout management

This approach provides:
- Single responsibility principle for each component
- Easier testing and maintenance
- Better code organization
- Reduced coupling between chart types
"""

def _get_dashboard_generator():
    """Lazy import to avoid circular dependency."""
    from .dashboard_generator import DashboardGenerator
    return DashboardGenerator

# Maintain backward compatibility by exposing ChartGenerator as an alias
ChartGenerator = _get_dashboard_generator()

# For convenience, also expose the main class directly
__all__ = ['ChartGenerator']
