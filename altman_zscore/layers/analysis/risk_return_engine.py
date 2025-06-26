"""
Risk-Return Analysis Engine - v4.2.0 Enterprise Feature

Advanced risk-return analysis with recommendation scoring, benchmarking,
and portfolio optimization capabilities. This module represents the next
evolution of the Altman Z-Score analysis system.

Strategic Value:
- Multi-dimensional risk assessment beyond traditional Z-Score
- Portfolio-level risk optimization recommendations  
- Sector-specific benchmarking and peer analysis
- Real-time risk monitoring and alert capabilities
- Investment decision support with confidence scoring
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import statistics
from enum import Enum

from ...common.logging_config import get_logger
from ...common.exceptions import AnalysisError, ValidationError
from ...models.data_models import MergedFinancialData, ZScoreResult
from ..zscore_calculation.zscore_calculator import ZScoreCalculator, ZScoreCalculationResult

logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk level classification for portfolio management."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


class RecommendationAction(Enum):
    """Investment recommendation actions."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    MONITOR = "monitor"


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for a security."""
    z_score: float
    risk_category: str
    bankruptcy_probability: float
    financial_strength_score: float
    liquidity_risk_score: float
    operational_risk_score: float
    market_risk_score: float
    overall_risk_score: float
    confidence_level: float
    
    # Advanced metrics
    volatility_score: Optional[float] = None
    trend_analysis_score: Optional[float] = None
    peer_comparison_score: Optional[float] = None


@dataclass
class RecommendationResult:
    """Investment recommendation with supporting analysis."""
    ticker: str
    action: RecommendationAction
    confidence: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    risk_level: RiskLevel
    time_horizon: str
    reasoning: List[str]
    risk_metrics: RiskMetrics
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Portfolio context
    portfolio_weight_suggestion: Optional[float] = None
    correlation_risks: List[str] = field(default_factory=list)


@dataclass
class PortfolioRiskProfile:
    """Portfolio-level risk assessment."""
    total_holdings: int
    average_z_score: float
    risk_distribution: Dict[str, float]
    concentration_risk: float
    diversification_score: float
    overall_portfolio_risk: RiskLevel
    recommendations: List[str]
    rebalancing_suggestions: List[Dict[str, Any]]


class RiskReturnAnalyzer:
    """
    Advanced Risk-Return Analysis Engine
    
    Provides comprehensive investment analysis combining:
    - Traditional Z-Score bankruptcy risk assessment
    - Modern portfolio theory metrics
    - Sector-specific benchmarking
    - Real-time market risk factors
    - AI-powered recommendation engine
    """
    
    def __init__(self):
        """Initialize the risk-return analyzer."""
        self.logger = get_logger(self.__class__.__name__)
        self.zscore_calculator = ZScoreCalculator()
        
        # Risk assessment parameters
        self.risk_thresholds = {
            'bankruptcy_probability': {
                'safe': 0.05,      # < 5% bankruptcy probability
                'caution': 0.15,   # 5-15% bankruptcy probability  
                'high_risk': 0.35, # 15-35% bankruptcy probability
                'distress': 1.0    # > 35% bankruptcy probability
            },
            'financial_strength': {
                'excellent': 0.9,
                'good': 0.7,
                'fair': 0.5,
                'poor': 0.3
            }
        }
        
        # Sector benchmarks (can be expanded)
        self.sector_benchmarks = {
            'technology': {'avg_z_score': 3.2, 'volatility': 0.35},
            'healthcare': {'avg_z_score': 2.8, 'volatility': 0.25},
            'manufacturing': {'avg_z_score': 2.1, 'volatility': 0.30},
            'retail': {'avg_z_score': 1.8, 'volatility': 0.40},
            'energy': {'avg_z_score': 1.5, 'volatility': 0.50},
            'financial': {'avg_z_score': 2.5, 'volatility': 0.45}
        }
    
    async def analyze_security(
        self, 
        data: MergedFinancialData,
        market_context: Optional[Dict[str, Any]] = None,
        sector: Optional[str] = None
    ) -> RecommendationResult:
        """
        Perform comprehensive risk-return analysis for a single security.
        
        Args:
            data: Merged financial data
            market_context: Additional market information
            sector: Industry sector for benchmarking
            
        Returns:
            RecommendationResult with investment recommendation
        """
        try:
            self.logger.info(f"Starting risk-return analysis for {data.ticker}")
            
            # Step 1: Calculate Z-Score and bankruptcy risk
            zscore_result = self.zscore_calculator.calculate_zscore(data)
            
            # Step 2: Calculate comprehensive risk metrics
            risk_metrics = await self._calculate_risk_metrics(data, zscore_result, sector)
            
            # Step 3: Generate investment recommendation
            recommendation = await self._generate_recommendation(
                data, risk_metrics, market_context
            )
            
            # Step 4: Add portfolio context
            recommendation = await self._add_portfolio_context(recommendation, sector)
            
            self.logger.info(
                f"Analysis complete for {data.ticker}: "
                f"{recommendation.action.value} (confidence: {recommendation.confidence:.2f})"
            )
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Risk-return analysis failed for {data.ticker}: {e}")
            raise AnalysisError(f"Risk-return analysis failed: {str(e)}")
    
    async def _calculate_risk_metrics(
        self, 
        data: MergedFinancialData, 
        zscore_result: ZScoreCalculationResult,
        sector: Optional[str] = None
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        
        # Bankruptcy probability from Z-Score
        bankruptcy_prob = self._calculate_bankruptcy_probability(zscore_result.z_score)
        
        # Financial strength score
        financial_strength = self._calculate_financial_strength(data, zscore_result)
        
        # Liquidity risk
        liquidity_risk = self._calculate_liquidity_risk(data)
        
        # Operational risk
        operational_risk = self._calculate_operational_risk(data)
        
        # Market risk
        market_risk = self._calculate_market_risk(data)
        
        # Overall risk score (weighted combination)
        overall_risk = self._calculate_overall_risk_score(
            bankruptcy_prob, financial_strength, liquidity_risk, 
            operational_risk, market_risk
        )
        
        # Confidence level based on data quality and completeness
        confidence = self._calculate_confidence_level(data, zscore_result)
        
        # Sector-specific adjustments
        peer_comparison = None
        if sector and sector in self.sector_benchmarks:
            peer_comparison = self._calculate_peer_comparison_score(
                zscore_result.z_score, sector
            )
        
        return RiskMetrics(
            z_score=zscore_result.z_score,
            risk_category=zscore_result.risk_category,
            bankruptcy_probability=bankruptcy_prob,
            financial_strength_score=financial_strength,
            liquidity_risk_score=liquidity_risk,
            operational_risk_score=operational_risk,
            market_risk_score=market_risk,
            overall_risk_score=overall_risk,
            confidence_level=confidence,
            peer_comparison_score=peer_comparison
        )
    
    def _calculate_bankruptcy_probability(self, z_score: float) -> float:
        """
        Convert Z-Score to bankruptcy probability using empirical research.
        
        Based on Altman's research:
        - Z > 2.99: ~2-5% probability
        - 1.81 < Z < 2.99: ~10-20% probability  
        - Z < 1.81: ~80-90% probability
        """
        if z_score >= 3.0:
            return max(0.02, 0.05 * (3.5 - z_score))  # 2-5% range
        elif z_score >= 1.8:
            # Linear interpolation between 5% and 35%
            return 0.05 + (2.99 - z_score) * 0.25
        else:
            # High risk zone
            return min(0.90, 0.35 + (1.8 - z_score) * 0.30)
    
    def _calculate_financial_strength(
        self, 
        data: MergedFinancialData, 
        zscore_result: ZScoreCalculationResult
    ) -> float:
        """Calculate financial strength score (0-1 scale)."""
        
        factors = []
        
        # Z-Score contribution (40% weight)
        if zscore_result.z_score >= 3.0:
            zscore_factor = 1.0
        elif zscore_result.z_score >= 1.8:
            zscore_factor = 0.3 + (zscore_result.z_score - 1.8) * 0.58  # 0.3 to 0.88
        else:
            zscore_factor = max(0.1, zscore_result.z_score / 1.8 * 0.3)
        
        factors.append(('zscore', zscore_factor, 0.4))
        
        # Profitability (20% weight)
        ebit_factor = min(1.0, max(0.0, (data.ebit_ratio or 0) * 10)) if data.ebit_ratio else 0.5
        factors.append(('profitability', ebit_factor, 0.2))
        
        # Liquidity (20% weight)
        current_ratio_factor = min(1.0, max(0.0, (data.current_ratio or 1.0) / 2.0)) if data.current_ratio else 0.5
        factors.append(('liquidity', current_ratio_factor, 0.2))
        
        # Leverage (20% weight)
        debt_factor = max(0.0, 1.0 - (data.debt_to_equity or 0.5) / 2.0) if data.debt_to_equity else 0.5
        factors.append(('leverage', debt_factor, 0.2))
        
        # Weighted average
        weighted_score = sum(score * weight for _, score, weight in factors)
        
        return min(1.0, max(0.0, weighted_score))
    
    def _calculate_liquidity_risk(self, data: MergedFinancialData) -> float:
        """Calculate liquidity risk score (0-1, higher = more risk)."""
        
        risk_factors = []
        
        # Current ratio (lower = higher risk)
        if data.current_ratio:
            if data.current_ratio >= 2.0:
                current_risk = 0.1
            elif data.current_ratio >= 1.0:
                current_risk = 0.1 + (2.0 - data.current_ratio) * 0.4  # 0.1 to 0.5
            else:
                current_risk = 0.5 + (1.0 - data.current_ratio) * 0.5  # 0.5 to 1.0
        else:
            current_risk = 0.5  # Unknown, moderate risk
        
        risk_factors.append(current_risk)
        
        # Working capital ratio
        if data.working_capital_ratio:
            if data.working_capital_ratio >= 0.2:
                wc_risk = 0.1
            elif data.working_capital_ratio >= 0:
                wc_risk = 0.1 + (0.2 - data.working_capital_ratio) * 2.0  # 0.1 to 0.5
            else:
                wc_risk = 0.8  # Negative working capital = high risk
        else:
            wc_risk = 0.5
        
        risk_factors.append(wc_risk)
        
        # Return average risk
        return statistics.mean(risk_factors)
    
    def _calculate_operational_risk(self, data: MergedFinancialData) -> float:
        """Calculate operational risk score (0-1, higher = more risk)."""
        
        risk_factors = []
        
        # Asset turnover efficiency
        if data.asset_turnover:
            if data.asset_turnover >= 1.0:
                turnover_risk = 0.2
            elif data.asset_turnover >= 0.5:
                turnover_risk = 0.2 + (1.0 - data.asset_turnover) * 0.6  # 0.2 to 0.8
            else:
                turnover_risk = 0.8 + (0.5 - data.asset_turnover) * 0.4  # 0.8 to 1.0
        else:
            turnover_risk = 0.6
        
        risk_factors.append(turnover_risk)
        
        # Profitability stability
        if data.ebit_ratio:
            if data.ebit_ratio >= 0.15:
                profit_risk = 0.1
            elif data.ebit_ratio >= 0:
                profit_risk = 0.1 + (0.15 - data.ebit_ratio) * 2.0  # 0.1 to 0.4
            else:
                profit_risk = 0.9  # Negative EBIT = high operational risk
        else:
            profit_risk = 0.5
        
        risk_factors.append(profit_risk)
        
        return statistics.mean(risk_factors)
    
    def _calculate_market_risk(self, data: MergedFinancialData) -> float:
        """Calculate market risk score (0-1, higher = more risk)."""
        
        risk_factors = []
        
        # Market capitalization risk (smaller = higher risk)
        if data.market_cap:
            if data.market_cap >= 10_000_000_000:  # $10B+ = large cap
                market_cap_risk = 0.2
            elif data.market_cap >= 2_000_000_000:  # $2B+ = mid cap
                market_cap_risk = 0.4
            elif data.market_cap >= 300_000_000:    # $300M+ = small cap
                market_cap_risk = 0.6
            else:                                   # < $300M = micro cap
                market_cap_risk = 0.9
        else:
            market_cap_risk = 0.8  # Private/unknown = high market risk
        
        risk_factors.append(market_cap_risk)
        
        # Add more market risk factors as data becomes available
        # (volatility, beta, sector concentration, etc.)
        
        return statistics.mean(risk_factors)
    
    def _calculate_overall_risk_score(
        self, 
        bankruptcy_prob: float,
        financial_strength: float,
        liquidity_risk: float,
        operational_risk: float,
        market_risk: float
    ) -> float:
        """Calculate weighted overall risk score."""
        
        # Weights for different risk components
        weights = {
            'bankruptcy': 0.3,
            'financial_strength': 0.25,
            'liquidity': 0.2,
            'operational': 0.15,
            'market': 0.1
        }
        
        # Convert financial strength to risk (inverse)
        financial_risk = 1.0 - financial_strength
        
        overall_risk = (
            bankruptcy_prob * weights['bankruptcy'] +
            financial_risk * weights['financial_strength'] +
            liquidity_risk * weights['liquidity'] +
            operational_risk * weights['operational'] +
            market_risk * weights['market']
        )
        
        return min(1.0, max(0.0, overall_risk))
    
    def _calculate_confidence_level(
        self, 
        data: MergedFinancialData, 
        zscore_result: ZScoreCalculationResult
    ) -> float:
        """Calculate confidence level for the analysis."""
        
        confidence_factors = []
        
        # Data quality score
        if data.data_quality_score:
            confidence_factors.append(data.data_quality_score)
        
        # Data completeness
        required_fields = ['working_capital_ratio', 'retained_earnings_ratio', 
                          'ebit_ratio', 'asset_turnover']
        available_fields = sum(1 for field in required_fields 
                             if getattr(data, field) is not None)
        completeness = available_fields / len(required_fields)
        confidence_factors.append(completeness)
        
        # Z-Score calculation warnings
        warning_penalty = len(zscore_result.warnings) * 0.1
        warning_factor = max(0.5, 1.0 - warning_penalty)
        confidence_factors.append(warning_factor)
        
        return statistics.mean(confidence_factors)
    
    def _calculate_peer_comparison_score(self, z_score: float, sector: str) -> float:
        """Calculate how the security compares to sector peers."""
        
        sector_avg = self.sector_benchmarks[sector]['avg_z_score']
        
        # Normalize comparison (-1 to +1 scale)
        if z_score >= sector_avg:
            # Above average performance
            excess = z_score - sector_avg
            return min(1.0, excess / 2.0)  # Cap at +1.0
        else:
            # Below average performance  
            deficit = sector_avg - z_score
            return max(-1.0, -deficit / 2.0)  # Cap at -1.0
    
    async def _generate_recommendation(
        self,
        data: MergedFinancialData,
        risk_metrics: RiskMetrics,
        market_context: Optional[Dict[str, Any]]
    ) -> RecommendationResult:
        """Generate investment recommendation based on risk analysis."""
        
        reasoning = []
        
        # Primary recommendation based on overall risk
        if risk_metrics.overall_risk_score <= 0.3:
            if risk_metrics.z_score >= 3.0:
                action = RecommendationAction.STRONG_BUY
                reasoning.append(f"Excellent financial health (Z-Score: {risk_metrics.z_score:.2f})")
            else:
                action = RecommendationAction.BUY
                reasoning.append(f"Good financial stability (Z-Score: {risk_metrics.z_score:.2f})")
        elif risk_metrics.overall_risk_score <= 0.5:
            action = RecommendationAction.HOLD
            reasoning.append(f"Moderate risk profile (Overall risk: {risk_metrics.overall_risk_score:.2f})")
        elif risk_metrics.overall_risk_score <= 0.7:
            action = RecommendationAction.SELL
            reasoning.append(f"Elevated risk concerns (Overall risk: {risk_metrics.overall_risk_score:.2f})")
        else:
            action = RecommendationAction.STRONG_SELL
            reasoning.append(f"High financial distress risk (Overall risk: {risk_metrics.overall_risk_score:.2f})")
        
        # Risk level classification
        if risk_metrics.overall_risk_score <= 0.25:
            risk_level = RiskLevel.CONSERVATIVE
        elif risk_metrics.overall_risk_score <= 0.5:
            risk_level = RiskLevel.MODERATE
        elif risk_metrics.overall_risk_score <= 0.75:
            risk_level = RiskLevel.AGGRESSIVE
        else:
            risk_level = RiskLevel.SPECULATIVE
        
        # Additional reasoning factors
        if risk_metrics.bankruptcy_probability > 0.2:
            reasoning.append(f"High bankruptcy probability: {risk_metrics.bankruptcy_probability:.1%}")
        
        if risk_metrics.liquidity_risk_score > 0.7:
            reasoning.append("Significant liquidity concerns identified")
        
        if risk_metrics.peer_comparison_score and risk_metrics.peer_comparison_score > 0.3:
            reasoning.append("Above-average performance vs sector peers")
        elif risk_metrics.peer_comparison_score and risk_metrics.peer_comparison_score < -0.3:
            reasoning.append("Below-average performance vs sector peers")
        
        # Time horizon based on risk level
        time_horizons = {
            RiskLevel.CONSERVATIVE: "Long-term (2-5 years)",
            RiskLevel.MODERATE: "Medium-term (1-3 years)",
            RiskLevel.AGGRESSIVE: "Short-term (6-18 months)",
            RiskLevel.SPECULATIVE: "Very short-term (1-6 months)"
        }
        
        return RecommendationResult(
            ticker=data.ticker,
            action=action,
            confidence=risk_metrics.confidence_level,
            target_price=None,  # Can be enhanced with valuation models
            stop_loss=None,     # Can be enhanced with technical analysis
            risk_level=risk_level,
            time_horizon=time_horizons[risk_level],
            reasoning=reasoning,
            risk_metrics=risk_metrics
        )
    
    async def _add_portfolio_context(
        self, 
        recommendation: RecommendationResult,
        sector: Optional[str]
    ) -> RecommendationResult:
        """Add portfolio-level context to the recommendation."""
        
        # Portfolio weight suggestion based on risk level
        weight_suggestions = {
            RiskLevel.CONSERVATIVE: 0.15,  # Up to 15% allocation
            RiskLevel.MODERATE: 0.10,      # Up to 10% allocation
            RiskLevel.AGGRESSIVE: 0.05,    # Up to 5% allocation
            RiskLevel.SPECULATIVE: 0.02    # Up to 2% allocation
        }
        
        recommendation.portfolio_weight_suggestion = weight_suggestions[recommendation.risk_level]
        
        # Correlation risks (placeholder for future enhancement)
        if sector:
            recommendation.correlation_risks.append(f"Sector concentration risk: {sector}")
        
        return recommendation


# Utility functions for external integration
async def analyze_single_security(
    data: MergedFinancialData,
    sector: Optional[str] = None
) -> RecommendationResult:
    """Public interface for single security analysis."""
    analyzer = RiskReturnAnalyzer()
    return await analyzer.analyze_security(data, sector=sector)


async def analyze_portfolio(securities: List[MergedFinancialData]) -> PortfolioRiskProfile:
    """Analyze portfolio-level risk (future enhancement)."""
    # Placeholder for portfolio analysis implementation
    analyzer = RiskReturnAnalyzer()
    
    # This would implement portfolio-level analysis
    # Including correlation analysis, diversification metrics,
    # and portfolio optimization recommendations
    
    raise NotImplementedError("Portfolio analysis coming in future release")
