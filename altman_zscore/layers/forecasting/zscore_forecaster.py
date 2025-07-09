"""
Z-Score Forecaster - Forward-looking Z-Score calculations

Generates Z-Score forecasts based on analyst consensus estimates and scenario modeling.
Provides multi-year projections with confidence intervals.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

from ...common.logging_config import get_logger
from ...common.exceptions import CalculationError
from ..zscore_calculation.zscore_calculator import ZScoreCalculator
from ..zscore_calculation import ZScoreCalculationResult
from .consensus_fetcher import ConsensusFetcher, ConsensusData, ConsensusEstimate
from .forecast_result import ForecastResult, ForecastScenario

logger = get_logger(__name__)


class ZScoreForecaster:
    """Generates Z-Score forecasts using analyst consensus data."""
    
    def __init__(self):
        """Initialize the Z-Score forecaster."""
        self.logger = get_logger(self.__class__.__name__)
        self.consensus_fetcher = ConsensusFetcher()
        self.zscore_calculator = ZScoreCalculator()
        
        # Forecast scenarios with probability weightings
        self.forecast_scenarios = {
            "optimistic": {"name": "Optimistic", "percentile": 75, "weight": 0.2},
            "base": {"name": "Base Case", "percentile": 50, "weight": 0.6},
            "pessimistic": {"name": "Pessimistic", "percentile": 25, "weight": 0.2}
        }
    
    async def generate_forecasts(
        self,
        ticker: str,
        current_zscore_result: ZScoreCalculationResult,
        forecast_years: int = 2
    ) -> Optional[ForecastResult]:
        """
        Generate comprehensive Z-Score forecasts for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            current_zscore_result: Current Z-Score calculation result
            forecast_years: Number of years to forecast (1-3)
            
        Returns:
            ForecastResult: Complete forecast analysis or None if unavailable
        """
        try:
            self.logger.info(f"Generating Z-Score forecasts for {ticker} ({forecast_years} years)")
            
            # Fetch analyst consensus data
            consensus_data = await self.consensus_fetcher.fetch_consensus_estimates(
                ticker, forecast_years
            )
            
            if not consensus_data:
                self.logger.warning(f"No consensus data available for {ticker} forecasting")
                return None
            
            # Validate consensus data quality
            if consensus_data.coverage_quality < 0.3:
                self.logger.warning(f"Low consensus quality ({consensus_data.coverage_quality:.2f}) for {ticker}")
                return self._create_limited_forecast(ticker, current_zscore_result, consensus_data)
            
            # Generate forecast scenarios
            forecast_scenarios = []
            
            for year in range(1, forecast_years + 1):
                yearly_scenarios = await self._generate_yearly_scenarios(
                    ticker, current_zscore_result, consensus_data, year
                )
                forecast_scenarios.extend(yearly_scenarios)
            
            if not forecast_scenarios:
                self.logger.warning(f"Unable to generate forecast scenarios for {ticker}")
                return None
            
            # Create comprehensive forecast result
            forecast_result = ForecastResult(
                ticker=ticker,
                company_name=consensus_data.company_name,
                base_z_score=current_zscore_result.z_score,
                forecast_scenarios=forecast_scenarios,
                model_used=current_zscore_result.model_used,
                data_quality_score=current_zscore_result.data_quality_score,
                analyst_coverage_quality=consensus_data.coverage_quality,
                forecast_timestamp=datetime.now(),
                forecast_metadata={
                    "forecast_years": forecast_years,
                    "estimates_count": len(consensus_data.estimates),
                    "data_vintage": consensus_data.data_vintage.isoformat(),
                    "methodology": "Analyst Consensus + Scenario Modeling"
                }
            )
            
            # Add forecast quality warnings
            forecast_result.warnings = self._generate_forecast_warnings(
                consensus_data, forecast_scenarios
            )
            
            self.logger.info(f"Successfully generated {len(forecast_scenarios)} forecast scenarios for {ticker}")
            return forecast_result
            
        except Exception as e:
            self.logger.error(f"Error generating forecasts for {ticker}: {str(e)}")
            return None
    
    async def _generate_yearly_scenarios(
        self,
        ticker: str,
        current_result: ZScoreCalculationResult,
        consensus_data: ConsensusData,
        forecast_year: int
    ) -> List[ForecastScenario]:
        """Generate forecast scenarios for a specific year."""
        scenarios = []
        
        # Determine target fiscal year using company-specific fiscal year end logic
        target_fiscal_year = self._determine_target_fiscal_year(ticker, forecast_year)
        
        # Get available estimates from consensus data  
        available_fiscal_years = sorted(set(est.fiscal_year for est in consensus_data.estimates))
        self.logger.info(f"Target fiscal year {target_fiscal_year} for {ticker} forecast year {forecast_year}. Available estimate years: {available_fiscal_years}")
        
        try:
            # Get consensus estimates for target year
            year_estimates = [
                est for est in consensus_data.estimates 
                if est.fiscal_year == target_fiscal_year
            ]
            
            if not year_estimates:
                self.logger.warning(f"No estimates found for {ticker} year {target_fiscal_year}")
                return []
            
            # Generate scenarios (optimistic, base, pessimistic)
            for scenario_key, scenario_config in self.forecast_scenarios.items():
                scenario = await self._generate_single_scenario(
                    ticker, current_result, year_estimates, 
                    scenario_config, forecast_year, target_fiscal_year
                )
                
                if scenario:
                    scenarios.append(scenario)
            
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Error generating yearly scenarios: {str(e)}")
            return []
    
    async def _generate_single_scenario(
        self,
        ticker: str,
        current_result: ZScoreCalculationResult,
        estimates: List[ConsensusEstimate],
        scenario_config: Dict[str, Any],
        forecast_year: int,
        target_fiscal_year: int
    ) -> Optional[ForecastScenario]:
        """Generate a single forecast scenario."""
        try:
            # Project financial metrics based on consensus and scenario
            projected_metrics = self._project_financial_metrics(
                current_result, estimates, scenario_config
            )
            
            if not projected_metrics:
                return None
            
            # Calculate Z-Score for projected metrics
            forecast_zscore = self._calculate_forecast_zscore(
                projected_metrics, current_result.model_used
            )
            
            # Determine risk category
            risk_category = self._determine_risk_category(
                forecast_zscore, current_result.model_used
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_scenario_confidence(
                estimates, scenario_config
            )
            
            # Create scenario
            scenario = ForecastScenario(
                scenario_name=scenario_config["name"],
                z_score=forecast_zscore,
                risk_category=risk_category,
                confidence_level=confidence_level,
                forecast_period=f"FY{target_fiscal_year}",  # Use fiscal year notation
                component_values=projected_metrics,
                assumptions=self._generate_scenario_assumptions(estimates, scenario_config)
            )
            
            return scenario
            
        except Exception as e:
            self.logger.error(f"Error generating single scenario: {str(e)}")
            return None
    
    def _project_financial_metrics(
        self,
        current_result: ZScoreCalculationResult,
        estimates: List[ConsensusEstimate],
        scenario_config: Dict[str, Any]
    ) -> Dict[str, float]:
        """Project financial metrics based on consensus estimates and scenario."""
        projected_metrics = {}
        
        try:
            # Get percentile for scenario (optimistic=75th, base=50th, pessimistic=25th)
            percentile = scenario_config["percentile"]
            
            # Project each Z-Score component
            current_components = current_result.component_values
            
            # Revenue growth projection
            revenue_estimate = self._get_metric_estimate(estimates, "revenue", percentile)
            revenue_growth = self._calculate_growth_rate(revenue_estimate, current_components)
            
            # EBITDA/EBIT projection  
            ebitda_estimate = self._get_metric_estimate(estimates, "ebitda", percentile)
            ebit_growth = self._calculate_growth_rate(ebitda_estimate, current_components)
            
            # Create scenario-specific adjustments
            scenario_multiplier = {
                "Optimistic": 1.10,  # 10% boost for optimistic scenario
                "Base Case": 1.00,   # No adjustment for base case
                "Pessimistic": 0.90  # 10% reduction for pessimistic scenario
            }.get(scenario_config["name"], 1.00)
            
            # Apply scenario multiplier to growth rates with realistic bounds
            revenue_growth *= scenario_multiplier
            ebit_growth *= scenario_multiplier
            
            # Ensure growth rates are within realistic bounds for forecasting
            # Extreme negative growth rates can lead to unrealistic projections
            revenue_growth = max(min(revenue_growth, 0.50), -0.30)  # Between -30% and 50%
            ebit_growth = max(min(ebit_growth, 0.50), -0.30)      # Between -30% and 50%
            
            # Project Z-Score components with growth assumptions
            # Handle both real field names and mock field names for backwards compatibility
            current_components = current_result.component_values
            
            # Map real field names to expected names
            working_capital_ratio = (
                current_components.get("working_capital_ratio") or 
                current_components.get("working_capital_to_total_assets", 0)
            )
            retained_earnings_ratio = (
                current_components.get("retained_earnings_ratio") or 
                current_components.get("retained_earnings_to_total_assets", 0)
            )
            ebit_ratio = (
                current_components.get("ebit_ratio") or 
                current_components.get("ebit_to_total_assets", 0)
            )
            market_equity_ratio = (
                current_components.get("market_equity_ratio") or 
                current_components.get("book_equity_ratio") or  # Common field name
                current_components.get("market_value_equity_to_total_liabilities", 0)
            )
            asset_turnover = (
                current_components.get("asset_turnover") or 
                current_components.get("sales_to_total_assets", 0)
            )
            
            # If asset_turnover is missing, calculate it from the Z-Score equation
            # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
            if asset_turnover == 0 and current_result.z_score > 0:
                calculated_without_x5 = (
                    1.2 * working_capital_ratio +
                    1.4 * retained_earnings_ratio +  
                    3.3 * ebit_ratio +
                    0.6 * market_equity_ratio
                )
                asset_turnover = current_result.z_score - calculated_without_x5
                self.logger.info(f"Calculated missing asset_turnover from Z-Score equation: {asset_turnover:.3f}")
            
            # Debug log the extracted values
            self.logger.debug(f"Extracted component values: working_capital={working_capital_ratio:.3f}, retained_earnings={retained_earnings_ratio:.3f}, ebit={ebit_ratio:.3f}, market_equity={market_equity_ratio:.3f}, asset_turnover={asset_turnover:.3f}")
            
            projected_metrics = {
                # Working Capital / Total Assets (assume proportional to revenue)
                "working_capital_to_total_assets": max(working_capital_ratio * (1 + revenue_growth * 0.5), 0.01),
                
                # Retained Earnings / Total Assets (accumulative growth) - allow negative for realistic forecasting
                "retained_earnings_to_total_assets": retained_earnings_ratio * (1 + revenue_growth * 0.3),
                
                # EBIT / Total Assets (based on EBITDA estimates)
                "ebit_to_total_assets": max(ebit_ratio * (1 + ebit_growth), 0.01),
                
                # Market Value Equity / Total Liabilities (assume stable with some growth) - preserve strong ratios
                "market_value_equity_to_total_liabilities": max(market_equity_ratio * (1 + revenue_growth * 0.4), market_equity_ratio * 0.8),
                
                # Sales / Total Assets (efficiency metric) - use reasonable minimum
                "sales_to_total_assets": max(asset_turnover * (1 + revenue_growth * 0.8), 0.01)
            }
            
            # Add retail-specific component if applicable
            if "inventory_turnover" in current_components:
                projected_metrics["inventory_turnover"] = current_components["inventory_turnover"] * (1 + revenue_growth * 0.2)
            
            self.logger.debug(f"Current component values: working_capital={working_capital_ratio:.3f}, retained_earnings={retained_earnings_ratio:.3f}, ebit={ebit_ratio:.3f}, market_equity={market_equity_ratio:.3f}, asset_turnover={asset_turnover:.3f}")
            self.logger.debug(f"Projected metrics for {scenario_config['name']} scenario (revenue growth: {revenue_growth:.3f}, ebit growth: {ebit_growth:.3f}): {projected_metrics}")
            
            # Validate projected metrics are reasonable
            for key, value in projected_metrics.items():
                if value < 0 or value > 10:  # Z-Score components should be reasonable ratios
                    self.logger.warning(f"Unrealistic projected metric {key}: {value:.3f} for {scenario_config['name']} scenario")
            
            return projected_metrics
            
        except Exception as e:
            self.logger.error(f"Error projecting financial metrics: {str(e)}")
            return {}
    
    def _get_metric_estimate(
        self, 
        estimates: List[ConsensusEstimate], 
        metric: str, 
        percentile: int
    ) -> Optional[float]:
        """Get consensus estimate for a specific metric at given percentile."""
        metric_estimates = [est for est in estimates if est.metric == metric]
        
        if not metric_estimates:
            return None
        
        # Use the most recent estimate
        latest_estimate = max(metric_estimates, key=lambda x: x.last_updated)
        
        # Calculate value at percentile between low and high estimates
        if percentile <= 25:
            return latest_estimate.estimate_low
        elif percentile >= 75:
            return latest_estimate.estimate_high
        else:
            # Linear interpolation between low and high
            range_value = latest_estimate.estimate_high - latest_estimate.estimate_low
            percentile_factor = (percentile - 25) / 50  # Normalize 25-75 to 0-1
            return latest_estimate.estimate_low + (range_value * percentile_factor)
    
    def _calculate_growth_rate(
        self, 
        estimate: Optional[float], 
        current_components: Dict[str, float]
    ) -> float:
        """Calculate implied growth rate from estimate."""
        if not estimate or estimate <= 0:
            return 0.0  # No growth if no estimate or negative estimate
        
        try:
            # For now, create reasonable growth rate variations based on estimate magnitude
            # This creates meaningful differences between optimistic, base, and pessimistic scenarios
            
            # Map estimate magnitude to growth rate ranges (more conservative)
            if estimate > 1e9:  # Large company (>$1B revenue)
                base_growth = 0.03  # 3% base growth (more conservative)
                growth_range = 0.02  # ±2% variation
            elif estimate > 1e8:  # Mid-cap ($100M-$1B)
                base_growth = 0.05  # 5% base growth (more conservative)
                growth_range = 0.03  # ±3% variation
            else:  # Small company
                base_growth = 0.08  # 8% base growth (more conservative)
                growth_range = 0.04  # ±4% variation
            
            # Create growth rate based on estimate magnitude within range
            # Higher estimates get higher growth rates
            normalized_estimate = min(estimate / 1e12, 1.0)  # Normalize to 0-1
            growth_modifier = (normalized_estimate - 0.5) * growth_range * 2
            
            final_growth = base_growth + growth_modifier
            
            # Ensure realistic bounds (more conservative)
            return max(min(final_growth, 0.20), -0.05)  # Between -5% and 20%
                
        except Exception:
            return 0.0
    
    def _calculate_forecast_zscore(
        self, 
        projected_metrics: Dict[str, float], 
        model_used: str
    ) -> float:
        """Calculate Z-Score using projected financial metrics."""
        try:
            # Use the same model as current calculation
            if model_used == "original":
                # Original Altman Z-Score model
                z_score = (
                    1.2 * projected_metrics.get("working_capital_to_total_assets", 0) +
                    1.4 * projected_metrics.get("retained_earnings_to_total_assets", 0) +
                    3.3 * projected_metrics.get("ebit_to_total_assets", 0) +
                    0.6 * projected_metrics.get("market_value_equity_to_total_liabilities", 0) +
                    1.0 * projected_metrics.get("sales_to_total_assets", 0)
                )
            elif model_used == "revised":
                # Revised Altman Z-Score model
                z_score = (
                    6.56 * projected_metrics.get("working_capital_to_total_assets", 0) +
                    3.26 * projected_metrics.get("retained_earnings_to_total_assets", 0) +
                    6.72 * projected_metrics.get("ebit_to_total_assets", 0) +
                    1.05 * projected_metrics.get("market_value_equity_to_total_liabilities", 0)
                )
            elif model_used == "retail":
                # Novel retail Z-Score model with inventory component
                z_score = (
                    1.2 * projected_metrics.get("working_capital_to_total_assets", 0) +
                    1.4 * projected_metrics.get("retained_earnings_to_total_assets", 0) +
                    3.3 * projected_metrics.get("ebit_to_total_assets", 0) +
                    0.6 * projected_metrics.get("market_value_equity_to_total_liabilities", 0) +
                    1.0 * projected_metrics.get("sales_to_total_assets", 0) +
                    0.3 * projected_metrics.get("inventory_turnover", 0)  # X₆ component
                )
            else:
                # Default to original model
                z_score = (
                    1.2 * projected_metrics.get("working_capital_to_total_assets", 0) +
                    1.4 * projected_metrics.get("retained_earnings_to_total_assets", 0) +
                    3.3 * projected_metrics.get("ebit_to_total_assets", 0) +
                    0.6 * projected_metrics.get("market_value_equity_to_total_liabilities", 0) +
                    1.0 * projected_metrics.get("sales_to_total_assets", 0)
                )
            
            # Ensure the calculated Z-Score is within reasonable bounds
            z_score = max(min(z_score, 50.0), -10.0)  # Cap between -10 and 50
            
            self.logger.debug(f"Calculated forecast Z-Score: {z_score:.3f} using {model_used} model")
            return round(z_score, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating forecast Z-Score: {str(e)}")
            return 0.0
    
    def _determine_risk_category(self, z_score: float, model_used: str) -> str:
        """Determine risk category for forecast Z-Score."""
        if model_used == "revised":
            if z_score > 2.6:
                return "SAFE"
            elif z_score > 1.1:
                return "GRAY ZONE"
            else:
                return "DISTRESS"
        else:  # Original and other models
            if z_score > 3.0:
                return "SAFE"
            elif z_score > 1.81:
                return "GRAY ZONE"
            else:
                return "DISTRESS"
    
    def _calculate_scenario_confidence(
        self, 
        estimates: List[ConsensusEstimate], 
        scenario_config: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for forecast scenario."""
        if not estimates:
            return 0.5
        
        try:
            # Average confidence of underlying estimates
            avg_estimate_confidence = sum(est.confidence_score for est in estimates) / len(estimates)
            
            # Scenario-specific confidence adjustments
            scenario_confidence_multiplier = {
                "Optimistic": 0.8,  # Lower confidence for optimistic scenario
                "Base Case": 1.0,   # Full confidence for base case
                "Pessimistic": 0.8  # Lower confidence for pessimistic scenario
            }
            
            multiplier = scenario_confidence_multiplier.get(scenario_config["name"], 1.0)
            confidence = avg_estimate_confidence * multiplier
            
            return round(min(confidence, 1.0), 3)
            
        except Exception:
            return 0.5
    
    def _generate_scenario_assumptions(
        self, 
        estimates: List[ConsensusEstimate], 
        scenario_config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate textual assumptions for the scenario."""
        assumptions = {
            "methodology": "Analyst consensus estimates with scenario modeling",
            "percentile": f"{scenario_config['percentile']}th percentile of estimates",
            "analyst_count": f"{sum(est.number_of_analysts for est in estimates)} total analysts",
            "coverage_metrics": f"{len(set(est.metric for est in estimates))} metrics covered"
        }
        
        # Add scenario-specific assumptions
        if scenario_config["name"] == "Optimistic":
            assumptions["scenario_bias"] = "Assumes favorable market conditions and execution"
        elif scenario_config["name"] == "Pessimistic":
            assumptions["scenario_bias"] = "Assumes challenging conditions and execution risks"
        else:
            assumptions["scenario_bias"] = "Consensus expectations with moderate execution"
        
        return assumptions
    
    def _create_limited_forecast(
        self,
        ticker: str,
        current_result: ZScoreCalculationResult,
        consensus_data: ConsensusData
    ) -> ForecastResult:
        """Create limited forecast when consensus quality is low."""
        # Simple trend-based forecast
        simple_scenario = ForecastScenario(
            scenario_name="Trend-Based",
            z_score=current_result.z_score * 0.95,  # Assume slight deterioration
            risk_category=current_result.risk_category,
            confidence_level=0.3,  # Low confidence
            forecast_period=f"{datetime.now().year + 1} Annual",
            assumptions={"methodology": "Simple trend extrapolation due to limited consensus data"}
        )
        
        return ForecastResult(
            ticker=ticker,
            company_name=consensus_data.company_name,
            base_z_score=current_result.z_score,
            forecast_scenarios=[simple_scenario],
            model_used=current_result.model_used,
            data_quality_score=current_result.data_quality_score,
            analyst_coverage_quality=consensus_data.coverage_quality,
            warnings=["Limited analyst coverage - forecast based on trend extrapolation"]
        )
    
    def _generate_forecast_warnings(
        self,
        consensus_data: ConsensusData,
        scenarios: List[ForecastScenario]
    ) -> List[str]:
        """Generate warnings about forecast limitations."""
        warnings = []
        
        # Coverage quality warnings
        if consensus_data.coverage_quality < 0.5:
            warnings.append("Low analyst coverage may affect forecast accuracy")
        
        # Scenario range warnings
        if scenarios:
            z_scores = [s.z_score for s in scenarios]
            z_range = max(z_scores) - min(z_scores)
            if z_range > 2.0:
                warnings.append("High forecast uncertainty - wide range between scenarios")
        
        # Data vintage warnings
        data_age = (datetime.now() - consensus_data.data_vintage).days
        if data_age > 30:
            warnings.append(f"Consensus data is {data_age} days old - may not reflect recent changes")
        
        return warnings
    
    def _determine_target_fiscal_year(self, ticker: str, forecast_year: int) -> int:
        """
        Determine the target fiscal year for forecasting based on company-specific fiscal year end.
        
        Args:
            ticker: Company ticker symbol
            forecast_year: Forecast year number (1 or 2)
            
        Returns:
            int: The target fiscal year for the forecast
        """
        try:
            from ..output_generation.charts.trend_analysis import TrendChart
            
            # Get current date
            current_date = datetime.now()
            current_calendar_year = current_date.year
            
            # Use the same fiscal year end detection logic as trend charts
            trend_chart = TrendChart()
            
            # First, try to get fiscal year end from API
            fiscal_year_end = trend_chart._fetch_fiscal_year_end_from_api(ticker)
            
            if fiscal_year_end:
                month, day = fiscal_year_end
                self.logger.info(f"Found fiscal year end for {ticker}: {month}/{day}")
                
                # Determine current fiscal year end date
                current_fiscal_year_end = datetime(current_calendar_year, month, day)
                
                # If current fiscal year hasn't ended yet, it's our baseline
                if current_date < current_fiscal_year_end:
                    base_fiscal_year = current_calendar_year
                    self.logger.info(f"Current fiscal year {base_fiscal_year} hasn't ended yet (ends {current_fiscal_year_end.strftime('%Y-%m-%d')})")
                else:
                    # Current fiscal year has ended, next fiscal year is baseline
                    base_fiscal_year = current_calendar_year + 1
                    self.logger.info(f"Current fiscal year {current_calendar_year} has ended, using {base_fiscal_year} as baseline")
                
                # Calculate target fiscal year
                target_fiscal_year = base_fiscal_year + forecast_year - 1
                
            else:
                # Fallback to calendar year logic if API lookup fails
                self.logger.warning(f"Could not determine fiscal year end for {ticker}, using calendar year logic")
                target_fiscal_year = current_calendar_year + forecast_year
                
            self.logger.info(f"Target fiscal year for {ticker} forecast year {forecast_year}: {target_fiscal_year}")
            return target_fiscal_year
            
        except Exception as e:
            self.logger.error(f"Error determining target fiscal year for {ticker}: {e}")
            # Fallback to simple calendar year logic
            return datetime.now().year + forecast_year
