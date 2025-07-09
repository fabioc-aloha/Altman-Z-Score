"""
Forecasting Layer - Z-Score Forecasting based on Analyst Consensus

This layer provides forward-looking Z-Score calculations using expert consensus
estimates for key financial metrics.

Key Features:
- Analyst consensus data integration
- Multi-year Z-Score projections
- Confidence intervals for forecasts
- Scenario analysis capabilities
"""

from .consensus_fetcher import ConsensusFetcher
from .zscore_forecaster import ZScoreForecaster
from .forecast_result import ForecastResult

__all__ = ['ConsensusFetcher', 'ZScoreForecaster', 'ForecastResult']
