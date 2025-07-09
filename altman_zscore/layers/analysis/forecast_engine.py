"""
Z-Score Forecast Engine - Analysis Layer

Predicts future Z-Scores based on analyst estimates from FMP API.
Uses consensus analyst forecasts to project Z-Score trends and financial health.

Key Features:
- Uses FMP analyst estimates for revenue, EBITDA, EBIT, net income
- Calculates projected financial ratios for Z-Score components
- Provides multi-period Z-Score forecasts (quarterly/annual)
- Includes confidence intervals based on analyst consensus ranges
- Supports all Z-Score models (original, retail, financial, etc.)
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ...common.logging_config import get_logger
from ...common.exceptions import AnalysisError
from ..models.zscore_calculator import ZScoreCalculator
from ..models.model_types import ModelType

logger = get_logger(__name__)


@dataclass
class ForecastPeriod:
    """Represents a single forecast period with analyst estimates."""
    date: str
    symbol: str
    
    # Revenue estimates
    estimated_revenue_low: float
    estimated_revenue_high: float
    estimated_revenue_avg: float
    
    # EBITDA estimates  
    estimated_ebitda_low: float
    estimated_ebitda_high: float
    estimated_ebitda_avg: float
    
    # EBIT estimates
    estimated_ebit_low: float
    estimated_ebit_high: float
    estimated_ebit_avg: float
    
    # Net income estimates
    estimated_net_income_low: float
    estimated_net_income_high: float
    estimated_net_income_avg: float
    
    # EPS estimates
    estimated_eps_low: float
    estimated_eps_high: float  
    estimated_eps_avg: float
    
    # SG&A estimates
    estimated_sga_low: float
    estimated_sga_high: float
    estimated_sga_avg: float
    
    # Number of analysts
    num_analysts_revenue: int
    num_analysts_eps: int
    
    @classmethod
    def from_fmp_data(cls, fmp_estimate: Dict[str, Any]) -> 'ForecastPeriod':
        """Create ForecastPeriod from FMP analyst estimate data."""
        return cls(
            date=fmp_estimate.get('date', ''),
            symbol=fmp_estimate.get('symbol', ''),
            estimated_revenue_low=fmp_estimate.get('estimatedRevenueLow', 0),
            estimated_revenue_high=fmp_estimate.get('estimatedRevenueHigh', 0),
            estimated_revenue_avg=fmp_estimate.get('estimatedRevenueAvg', 0),
            estimated_ebitda_low=fmp_estimate.get('estimatedEbitdaLow', 0),
            estimated_ebitda_high=fmp_estimate.get('estimatedEbitdaHigh', 0),
            estimated_ebitda_avg=fmp_estimate.get('estimatedEbitdaAvg', 0),
            estimated_ebit_low=fmp_estimate.get('estimatedEbitLow', 0),
            estimated_ebit_high=fmp_estimate.get('estimatedEbitHigh', 0),
            estimated_ebit_avg=fmp_estimate.get('estimatedEbitAvg', 0),
            estimated_net_income_low=fmp_estimate.get('estimatedNetIncomeLow', 0),
            estimated_net_income_high=fmp_estimate.get('estimatedNetIncomeHigh', 0),
            estimated_net_income_avg=fmp_estimate.get('estimatedNetIncomeAvg', 0),
            estimated_eps_low=fmp_estimate.get('estimatedEpsLow', 0),
            estimated_eps_high=fmp_estimate.get('estimatedEpsHigh', 0),
            estimated_eps_avg=fmp_estimate.get('estimatedEpsAvg', 0),
            estimated_sga_low=fmp_estimate.get('estimatedSgaExpenseLow', 0),
            estimated_sga_high=fmp_estimate.get('estimatedSgaExpenseHigh', 0),
            estimated_sga_avg=fmp_estimate.get('estimatedSgaExpenseAvg', 0),
            num_analysts_revenue=fmp_estimate.get('numberAnalystEstimatedRevenue', 0),
            num_analysts_eps=fmp_estimate.get('numberAnalystsEstimatedEps', 0)
        )


@dataclass
class ZScoreForecast:
    """Represents a Z-Score forecast for a specific period."""
    period_date: str
    symbol: str
    
    # Z-Score predictions (low, high, average based on analyst ranges)
    z_score_low: float
    z_score_high: float  
    z_score_avg: float
    
    # Component ratio forecasts
    working_capital_ratio: float
    retained_earnings_ratio: float
    ebit_ratio: float
    market_equity_ratio: float
    asset_turnover: float
    
    # Model information
    model_type: str
    confidence_level: float  # Based on analyst consensus
    
    # Supporting data
    num_analysts: int
    forecast_period: str  # e.g., "FY 2025", "Q3 2025"


class ZScoreForecastEngine:
    """
    Engine for generating Z-Score forecasts based on analyst estimates.
    
    This engine takes analyst estimates and projects future Z-Scores by:
    1. Extracting current balance sheet baseline ratios
    2. Applying analyst revenue/income forecasts to income statement components
    3. Estimating balance sheet changes based on historical patterns
    4. Calculating projected Z-Score components
    5. Generating confidence intervals from analyst estimate ranges
    """
    
    def __init__(self):
        """Initialize the forecast engine."""
        self.calculator = ZScoreCalculator()
        
    def generate_forecasts(
        self,
        symbol: str,
        analyst_estimates: List[Dict[str, Any]],
        current_financials: Dict[str, Any],
        model_type: Optional[ModelType] = None,
        periods: int = 4
    ) -> List[ZScoreForecast]:
        """
        Generate Z-Score forecasts based on analyst estimates.
        
        Args:
            symbol: Stock ticker symbol
            analyst_estimates: Raw analyst estimate data from FMP API
            current_financials: Current financial data for baseline calculations
            model_type: Specific Z-Score model to use (auto-detect if None)
            periods: Number of forward periods to forecast
            
        Returns:
            List of Z-Score forecasts sorted by date
        """
        try:
            logger.info(f"Generating Z-Score forecasts for {symbol} using {len(analyst_estimates)} analyst estimates")
            
            # Convert FMP data to ForecastPeriod objects
            forecast_periods = []
            for estimate in analyst_estimates[:periods]:  # Limit to requested periods
                try:
                    forecast_period = ForecastPeriod.from_fmp_data(estimate)
                    forecast_periods.append(forecast_period)
                except Exception as e:
                    logger.warning(f"Skipping invalid analyst estimate: {e}")
                    continue
            
            if not forecast_periods:
                raise AnalysisError(f"No valid analyst estimates found for {symbol}")
            
            # Extract baseline financial ratios from current data
            baseline_ratios = self._extract_baseline_ratios(current_financials)
            
            # Generate forecasts for each period
            forecasts = []
            for period in forecast_periods:
                try:
                    forecast = self._generate_period_forecast(
                        period, baseline_ratios, model_type
                    )
                    forecasts.append(forecast)
                    logger.debug(f"Generated forecast for {period.date}: Z-Score {forecast.z_score_avg:.2f}")
                except Exception as e:
                    logger.warning(f"Failed to generate forecast for period {period.date}: {e}")
                    continue
            
            logger.info(f"Successfully generated {len(forecasts)} Z-Score forecasts for {symbol}")
            return forecasts
            
        except Exception as e:
            logger.error(f"Failed to generate Z-Score forecasts for {symbol}: {e}")
            raise AnalysisError(f"Z-Score forecast generation failed: {e}")
    
    def _extract_baseline_ratios(self, current_financials: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract baseline financial ratios from current financial data.
        
        These ratios are used as starting points for projecting future values.
        """
        try:
            # Extract key balance sheet items for baseline calculations
            balance_sheet = current_financials.get('balance_sheet', {})
            income_statement = current_financials.get('income_statement', {})
            
            if not balance_sheet or not income_statement:
                raise AnalysisError("Missing balance sheet or income statement data for baseline calculations")
            
            # Calculate current asset-based ratios (these tend to be more stable)
            total_assets = balance_sheet.get('totalAssets', 0)
            total_liabilities = balance_sheet.get('totalLiabilities', 0)
            shareholders_equity = balance_sheet.get('totalStockholdersEquity', 0)
            
            if total_assets <= 0:
                raise AnalysisError("Invalid total assets value for baseline calculations")
            
            # These ratios will be used to project future balance sheet values
            baseline = {
                'asset_liability_ratio': total_liabilities / total_assets if total_assets > 0 else 0.5,
                'equity_asset_ratio': shareholders_equity / total_assets if total_assets > 0 else 0.5,
                'revenue_asset_multiple': income_statement.get('revenue', 0) / total_assets if total_assets > 0 else 1.0,
            }
            
            logger.debug(f"Extracted baseline ratios: {baseline}")
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to extract baseline ratios: {e}")
            # Return reasonable defaults if extraction fails
            return {
                'asset_liability_ratio': 0.6,  # 60% liabilities typical
                'equity_asset_ratio': 0.4,    # 40% equity typical  
                'revenue_asset_multiple': 1.0   # 1x asset turnover typical
            }
    
    def _generate_period_forecast(
        self,
        period: ForecastPeriod,
        baseline_ratios: Dict[str, float],
        model_type: Optional[ModelType]
    ) -> ZScoreForecast:
        """
        Generate Z-Score forecast for a single period.
        
        This involves:
        1. Projecting total assets based on revenue growth
        2. Estimating balance sheet components using baseline ratios
        3. Calculating Z-Score component ratios
        4. Computing Z-Score using appropriate model
        """
        try:
            # Project total assets based on revenue and historical asset turnover
            projected_revenue = period.estimated_revenue_avg
            asset_turnover_baseline = baseline_ratios.get('revenue_asset_multiple', 1.0)
            projected_total_assets = projected_revenue / asset_turnover_baseline if asset_turnover_baseline > 0 else projected_revenue
            
            # Project balance sheet components using baseline ratios
            projected_liabilities = projected_total_assets * baseline_ratios.get('asset_liability_ratio', 0.6)
            projected_equity = projected_total_assets * baseline_ratios.get('equity_asset_ratio', 0.4)
            
            # Estimate working capital (simplified: assume 10% of revenue)
            projected_working_capital = projected_revenue * 0.10
            
            # Calculate Z-Score components using analyst estimates
            
            # X1: Working Capital / Total Assets
            working_capital_ratio = projected_working_capital / projected_total_assets if projected_total_assets > 0 else 0
            
            # X2: Retained Earnings / Total Assets (estimate based on net income)
            # Assume retained earnings grow by 70% of net income (30% dividends)
            retained_earnings_addition = period.estimated_net_income_avg * 0.7
            retained_earnings_ratio = retained_earnings_addition / projected_total_assets if projected_total_assets > 0 else 0
            
            # X3: EBIT / Total Assets
            ebit_ratio = period.estimated_ebit_avg / projected_total_assets if projected_total_assets > 0 else 0
            
            # X4: Market Equity / Total Liabilities (assume stable market-to-book ratio)
            # This is challenging to predict without stock price forecasts, use book value
            market_equity_ratio = projected_equity / projected_liabilities if projected_liabilities > 0 else 1.0
            
            # X5: Sales / Total Assets (Asset Turnover)
            asset_turnover = projected_revenue / projected_total_assets if projected_total_assets > 0 else 0
            
            # Calculate Z-Score using the specified model
            if model_type is None:
                model_type = ModelType.ORIGINAL  # Default to original model
            
            # Create simplified financial data structure for Z-Score calculation
            projected_financials = {
                'working_capital_ratio': working_capital_ratio,
                'retained_earnings_ratio': retained_earnings_ratio, 
                'ebit_ratio': ebit_ratio,
                'market_equity_ratio': market_equity_ratio,
                'asset_turnover': asset_turnover
            }
            
            # Calculate Z-Score for average estimates
            z_score_avg = self._calculate_zscore_from_components(projected_financials, model_type)
            
            # Calculate Z-Score ranges using low/high estimates
            z_score_low = self._calculate_zscore_range(period, baseline_ratios, model_type, 'low')
            z_score_high = self._calculate_zscore_range(period, baseline_ratios, model_type, 'high')
            
            # Calculate confidence level based on analyst consensus
            confidence = self._calculate_confidence_level(period)
            
            # Determine forecast period label
            forecast_period_label = self._get_period_label(period.date)
            
            return ZScoreForecast(
                period_date=period.date,
                symbol=period.symbol,
                z_score_low=z_score_low,
                z_score_high=z_score_high,
                z_score_avg=z_score_avg,
                working_capital_ratio=working_capital_ratio,
                retained_earnings_ratio=retained_earnings_ratio,
                ebit_ratio=ebit_ratio,
                market_equity_ratio=market_equity_ratio,
                asset_turnover=asset_turnover,
                model_type=model_type.value,
                confidence_level=confidence,
                num_analysts=max(period.num_analysts_revenue, period.num_analysts_eps),
                forecast_period=forecast_period_label
            )
            
        except Exception as e:
            logger.error(f"Failed to generate period forecast for {period.date}: {e}")
            raise AnalysisError(f"Period forecast calculation failed: {e}")
    
    def _calculate_zscore_from_components(
        self, 
        components: Dict[str, float], 
        model_type: ModelType
    ) -> float:
        """Calculate Z-Score from component ratios using specified model."""
        try:
            # Use the existing Z-Score calculator with projected components
            if model_type == ModelType.ORIGINAL:
                z_score = (
                    1.2 * components['working_capital_ratio'] +
                    1.4 * components['retained_earnings_ratio'] +
                    3.3 * components['ebit_ratio'] +
                    0.6 * components['market_equity_ratio'] +
                    1.0 * components['asset_turnover']
                )
            elif model_type == ModelType.FINANCIAL:
                # Financial institution model (simplified)
                z_score = (
                    1.0 * components['working_capital_ratio'] +
                    1.4 * components['retained_earnings_ratio'] +
                    3.3 * components['ebit_ratio'] +
                    0.6 * components['market_equity_ratio']
                    # No asset turnover component for financial institutions
                )
            elif model_type == ModelType.RETAIL:
                # Retail model with inventory consideration (simplified)
                z_score = (
                    1.2 * components['working_capital_ratio'] +
                    1.4 * components['retained_earnings_ratio'] +
                    3.3 * components['ebit_ratio'] +
                    0.6 * components['market_equity_ratio'] +
                    1.0 * components['asset_turnover']
                    # Additional inventory turnover component would be added here
                )
            else:
                # Default to original model
                z_score = (
                    1.2 * components['working_capital_ratio'] +
                    1.4 * components['retained_earnings_ratio'] +
                    3.3 * components['ebit_ratio'] +
                    0.6 * components['market_equity_ratio'] +
                    1.0 * components['asset_turnover']
                )
            
            return max(0, z_score)  # Ensure non-negative Z-Score
            
        except Exception as e:
            logger.error(f"Z-Score calculation failed: {e}")
            return 0.0
    
    def _calculate_zscore_range(
        self, 
        period: ForecastPeriod, 
        baseline_ratios: Dict[str, float], 
        model_type: ModelType, 
        estimate_type: str
    ) -> float:
        """Calculate Z-Score using low or high analyst estimates."""
        try:
            # Select appropriate estimates based on type
            if estimate_type == 'low':
                revenue = period.estimated_revenue_low
                ebit = period.estimated_ebit_low
                net_income = period.estimated_net_income_low
            else:  # high
                revenue = period.estimated_revenue_high
                ebit = period.estimated_ebit_high
                net_income = period.estimated_net_income_high
            
            # Recalculate components with range estimates
            asset_turnover_baseline = baseline_ratios.get('revenue_asset_multiple', 1.0)
            total_assets = revenue / asset_turnover_baseline if asset_turnover_baseline > 0 else revenue
            
            working_capital = revenue * 0.10
            retained_earnings_addition = net_income * 0.7
            
            components = {
                'working_capital_ratio': working_capital / total_assets if total_assets > 0 else 0,
                'retained_earnings_ratio': retained_earnings_addition / total_assets if total_assets > 0 else 0,
                'ebit_ratio': ebit / total_assets if total_assets > 0 else 0,
                'market_equity_ratio': (total_assets * baseline_ratios.get('equity_asset_ratio', 0.4)) / 
                                     (total_assets * baseline_ratios.get('asset_liability_ratio', 0.6)) if total_assets > 0 else 1.0,
                'asset_turnover': revenue / total_assets if total_assets > 0 else 0
            }
            
            return self._calculate_zscore_from_components(components, model_type)
            
        except Exception as e:
            logger.error(f"Z-Score range calculation failed for {estimate_type}: {e}")
            return 0.0
    
    def _calculate_confidence_level(self, period: ForecastPeriod) -> float:
        """
        Calculate confidence level based on analyst consensus and range.
        
        Higher confidence when:
        - More analysts agree
        - Smaller range between high/low estimates
        """
        try:
            # Base confidence on number of analysts (more analysts = higher confidence)
            num_analysts = max(period.num_analysts_revenue, period.num_analysts_eps)
            analyst_confidence = min(0.5 + (num_analysts * 0.05), 0.9)  # Cap at 90%
            
            # Factor in estimate range (smaller range = higher confidence)
            if period.estimated_revenue_avg > 0:
                revenue_range = abs(period.estimated_revenue_high - period.estimated_revenue_low) / period.estimated_revenue_avg
                range_confidence = max(0.3, 1.0 - revenue_range)  # Min 30% confidence
            else:
                range_confidence = 0.5
            
            # Combine both factors
            combined_confidence = (analyst_confidence + range_confidence) / 2
            
            return round(combined_confidence, 2)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5  # Default 50% confidence
    
    def _get_period_label(self, date_str: str) -> str:
        """Convert date string to human-readable period label."""
        try:
            # Parse date and create fiscal year/quarter label
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Determine if it's a fiscal year end (typically September for many companies)
            if date_obj.month in [9, 12]:  # September or December year-ends
                return f"FY {date_obj.year}"
            else:
                # Determine quarter
                quarter = (date_obj.month - 1) // 3 + 1
                return f"Q{quarter} {date_obj.year}"
                
        except Exception:
            return date_str  # Return original if parsing fails
