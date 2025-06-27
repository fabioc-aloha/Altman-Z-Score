"""
Unit tests for Risk-Return Analysis Engine

Tests the advanced risk-return analysis capabilities including
risk scoring, recommendation generation, and portfolio analysis.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, Mock

from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculationResult
from altman_zscore.layers.analysis.risk_return_engine import (
    RiskReturnAnalyzer,
    RiskLevel,
    RecommendationAction,
    RiskMetrics,
    RecommendationResult,
    analyze_single_security
)


@pytest.mark.unit
class TestRiskReturnAnalyzer:
    """Test RiskReturnAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = RiskReturnAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'zscore_calculator')
        assert hasattr(self.analyzer, 'risk_thresholds')
        assert hasattr(self.analyzer, 'sector_benchmarks')
    
    def test_bankruptcy_probability_calculation(self):
        """Test bankruptcy probability calculation from Z-Score"""
        # Safe zone (Z > 3.0)
        prob_safe = self.analyzer._calculate_bankruptcy_probability(3.5)
        assert 0.02 <= prob_safe <= 0.05
        
        # Grey zone (1.8 < Z < 3.0)
        prob_grey = self.analyzer._calculate_bankruptcy_probability(2.2)
        assert 0.05 < prob_grey < 0.35
        
        # Distress zone (Z < 1.8)
        prob_distress = self.analyzer._calculate_bankruptcy_probability(1.0)
        assert prob_distress >= 0.35
    
    def test_financial_strength_calculation(self):
        """Test financial strength score calculation"""
        # Strong financial data
        strong_data = MergedFinancialData(
            ticker="STRONG",
            timestamp="2023-12-31",
            ebit_ratio=0.20,
            current_ratio=2.5,
            debt_to_equity=0.3,
            data_quality_score=0.95
        )
        
        # Mock Z-Score result
        mock_zscore = ZScoreCalculationResult(
            ticker="STRONG",
            z_score=3.5,
            model_used="original",
            risk_category="Safe",
            component_values={},
            calculation_timestamp="2023-12-31",
            data_quality_score=0.95,
            warnings=[],
            metadata={}
        )
        
        strength = self.analyzer._calculate_financial_strength(strong_data, mock_zscore)
        assert 0.8 <= strength <= 1.0
        
        # Weak financial data
        weak_data = MergedFinancialData(
            ticker="WEAK",
            timestamp="2023-12-31",
            ebit_ratio=-0.05,
            current_ratio=0.8,
            debt_to_equity=3.0,
            data_quality_score=0.6
        )
        
        mock_zscore_weak = ZScoreCalculationResult(
            ticker="WEAK",
            z_score=1.0,
            model_used="original", 
            risk_category="Distress",
            component_values={},
            calculation_timestamp="2023-12-31",
            data_quality_score=0.6,
            warnings=["Low data quality"],
            metadata={}
        )
        
        strength_weak = self.analyzer._calculate_financial_strength(weak_data, mock_zscore_weak)
        assert 0.0 <= strength_weak <= 0.4
    
    def test_liquidity_risk_calculation(self):
        """Test liquidity risk score calculation"""
        # Good liquidity
        good_liquidity = MergedFinancialData(
            ticker="LIQUID",
            timestamp="2023-12-31",
            current_ratio=2.5,
            working_capital_ratio=0.3
        )
        
        liquidity_risk = self.analyzer._calculate_liquidity_risk(good_liquidity)
        assert 0.0 <= liquidity_risk <= 0.3
        
        # Poor liquidity
        poor_liquidity = MergedFinancialData(
            ticker="ILLIQUID",
            timestamp="2023-12-31",
            current_ratio=0.7,
            working_capital_ratio=-0.1
        )
        
        liquidity_risk_high = self.analyzer._calculate_liquidity_risk(poor_liquidity)
        assert 0.5 <= liquidity_risk_high <= 1.0
    
    def test_operational_risk_calculation(self):
        """Test operational risk score calculation"""
        # Efficient operations
        efficient_ops = MergedFinancialData(
            ticker="EFFICIENT",
            timestamp="2023-12-31",
            asset_turnover=1.5,
            ebit_ratio=0.20
        )
        
        op_risk = self.analyzer._calculate_operational_risk(efficient_ops)
        assert 0.0 <= op_risk <= 0.3
        
        # Inefficient operations
        inefficient_ops = MergedFinancialData(
            ticker="INEFFICIENT",
            timestamp="2023-12-31",
            asset_turnover=0.3,
            ebit_ratio=-0.05
        )
        
        op_risk_high = self.analyzer._calculate_operational_risk(inefficient_ops)
        assert 0.7 <= op_risk_high <= 1.0
    
    def test_market_risk_calculation(self):
        """Test market risk score calculation"""
        # Large cap (low market risk)
        large_cap = MergedFinancialData(
            ticker="LARGECAP",
            timestamp="2023-12-31",
            market_cap=50_000_000_000  # $50B
        )
        
        market_risk_low = self.analyzer._calculate_market_risk(large_cap)
        assert 0.0 <= market_risk_low <= 0.3
        
        # Micro cap (high market risk)
        micro_cap = MergedFinancialData(
            ticker="MICROCAP",
            timestamp="2023-12-31",
            market_cap=100_000_000  # $100M
        )
        
        market_risk_high = self.analyzer._calculate_market_risk(micro_cap)
        assert 0.6 <= market_risk_high <= 1.0
    
    def test_peer_comparison_score(self):
        """Test sector peer comparison scoring"""
        # Above average Z-Score for technology sector
        above_avg_score = self.analyzer._calculate_peer_comparison_score(4.0, "technology")
        assert above_avg_score > 0
        
        # Below average Z-Score for technology sector
        below_avg_score = self.analyzer._calculate_peer_comparison_score(2.0, "technology")
        assert below_avg_score < 0
        
        # Average Z-Score
        avg_score = self.analyzer._calculate_peer_comparison_score(3.2, "technology")
        assert abs(avg_score) < 0.1  # Should be close to zero
    
    @pytest.mark.asyncio
    async def test_calculate_risk_metrics(self):
        """Test comprehensive risk metrics calculation"""
        # Create test data
        test_data = MergedFinancialData(
            ticker="TEST",
            timestamp="2023-12-31",
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            asset_turnover=1.0,
            current_ratio=2.0,
            debt_to_equity=0.5,
            market_cap=5_000_000_000,
            data_quality_score=0.9
        )
        
        # Mock Z-Score result
        mock_zscore = ZScoreCalculationResult(
            ticker="TEST",
            z_score=2.5,
            model_used="original",
            risk_category="Gray Zone",
            component_values={},
            calculation_timestamp="2023-12-31",
            data_quality_score=0.9,
            warnings=[],
            metadata={}
        )
        
        risk_metrics = await self.analyzer._calculate_risk_metrics(
            test_data, mock_zscore, "technology"
        )
        
        # Validate risk metrics structure
        assert isinstance(risk_metrics, RiskMetrics)
        assert risk_metrics.z_score == 2.5
        assert risk_metrics.risk_category == "Gray Zone"
        assert 0.0 <= risk_metrics.bankruptcy_probability <= 1.0
        assert 0.0 <= risk_metrics.financial_strength_score <= 1.0
        assert 0.0 <= risk_metrics.liquidity_risk_score <= 1.0
        assert 0.0 <= risk_metrics.operational_risk_score <= 1.0
        assert 0.0 <= risk_metrics.market_risk_score <= 1.0
        assert 0.0 <= risk_metrics.overall_risk_score <= 1.0
        assert 0.0 <= risk_metrics.confidence_level <= 1.0
        assert risk_metrics.peer_comparison_score is not None
    
    @pytest.mark.asyncio
    async def test_generate_recommendation_strong_buy(self):
        """Test recommendation generation for strong buy scenario"""
        # High-quality company data
        excellent_data = MergedFinancialData(
            ticker="EXCELLENT",
            timestamp="2023-12-31",
            working_capital_ratio=1.5,
            retained_earnings_ratio=0.4,
            ebit_ratio=0.25,
            asset_turnover=1.2,
            current_ratio=2.5,
            debt_to_equity=0.2,
            market_cap=20_000_000_000,
            data_quality_score=0.95
        )
        
        # Create excellent risk metrics
        excellent_metrics = RiskMetrics(
            z_score=4.0,
            risk_category="Safe",
            bankruptcy_probability=0.03,
            financial_strength_score=0.95,
            liquidity_risk_score=0.1,
            operational_risk_score=0.1,
            market_risk_score=0.2,
            overall_risk_score=0.2,
            confidence_level=0.95
        )
        
        recommendation = await self.analyzer._generate_recommendation(
            excellent_data, excellent_metrics, None
        )
        
        assert recommendation.action == RecommendationAction.STRONG_BUY
        assert recommendation.risk_level == RiskLevel.CONSERVATIVE
        assert recommendation.confidence >= 0.9
        assert len(recommendation.reasoning) > 0
        assert "excellent" in recommendation.reasoning[0].lower() or "good" in recommendation.reasoning[0].lower()
    
    @pytest.mark.asyncio
    async def test_generate_recommendation_strong_sell(self):
        """Test recommendation generation for strong sell scenario"""
        # Poor quality company data
        poor_data = MergedFinancialData(
            ticker="POOR",
            timestamp="2023-12-31",
            working_capital_ratio=-0.2,
            retained_earnings_ratio=-0.1,
            ebit_ratio=-0.1,
            asset_turnover=0.3,
            current_ratio=0.6,
            debt_to_equity=5.0,
            market_cap=50_000_000,
            data_quality_score=0.5
        )
        
        # Create poor risk metrics
        poor_metrics = RiskMetrics(
            z_score=0.8,
            risk_category="Distress",
            bankruptcy_probability=0.8,
            financial_strength_score=0.1,
            liquidity_risk_score=0.9,
            operational_risk_score=0.9,
            market_risk_score=0.8,
            overall_risk_score=0.85,
            confidence_level=0.6
        )
        
        recommendation = await self.analyzer._generate_recommendation(
            poor_data, poor_metrics, None
        )
        
        assert recommendation.action == RecommendationAction.STRONG_SELL
        assert recommendation.risk_level == RiskLevel.SPECULATIVE
        assert len(recommendation.reasoning) > 0
        assert "high" in recommendation.reasoning[0].lower() or "distress" in recommendation.reasoning[0].lower()
    
    @pytest.mark.asyncio
    async def test_full_analyze_security_workflow(self):
        """Test complete analyze_security workflow"""
        # Create realistic test data
        test_data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            working_capital_ratio=1.1,
            retained_earnings_ratio=0.45,
            ebit_ratio=0.25,
            asset_turnover=0.85,
            current_ratio=1.5,
            debt_to_equity=0.3,
            market_cap=3_000_000_000_000,
            data_quality_score=0.95
        )
        
        # Mock the Z-Score calculator
        mock_zscore_result = ZScoreCalculationResult(
            ticker="AAPL",
            z_score=3.2,
            model_used="original",
            risk_category="Safe",
            component_values={},
            calculation_timestamp="2023-12-31",
            data_quality_score=0.95,
            warnings=[],
            metadata={}
        )
        
        with patch.object(self.analyzer.zscore_calculator, 'calculate_zscore', 
                         return_value=mock_zscore_result):
            
            result = await self.analyzer.analyze_security(
                test_data, sector="technology"
            )
        
        # Validate recommendation result
        assert isinstance(result, RecommendationResult)
        assert result.ticker == "AAPL"
        assert isinstance(result.action, RecommendationAction)
        assert isinstance(result.risk_level, RiskLevel)
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reasoning) > 0
        assert isinstance(result.risk_metrics, RiskMetrics)
        assert result.portfolio_weight_suggestion is not None
        assert 0.0 <= result.portfolio_weight_suggestion <= 0.2
    
    @pytest.mark.asyncio
    async def test_add_portfolio_context(self):
        """Test portfolio context addition"""
        # Create base recommendation
        base_recommendation = RecommendationResult(
            ticker="TEST",
            action=RecommendationAction.BUY,
            confidence=0.8,
            target_price=None,
            stop_loss=None,
            risk_level=RiskLevel.MODERATE,
            time_horizon="Medium-term",
            reasoning=["Good financial health"],
            risk_metrics=RiskMetrics(
                z_score=2.5,
                risk_category="Gray Zone",
                bankruptcy_probability=0.1,
                financial_strength_score=0.7,
                liquidity_risk_score=0.3,
                operational_risk_score=0.2,
                market_risk_score=0.4,
                overall_risk_score=0.3,
                confidence_level=0.8
            )
        )
        
        enhanced_recommendation = await self.analyzer._add_portfolio_context(
            base_recommendation, "technology"
        )
        
        assert enhanced_recommendation.portfolio_weight_suggestion == 0.10  # Moderate risk = 10%
        assert len(enhanced_recommendation.correlation_risks) > 0
        assert "technology" in enhanced_recommendation.correlation_risks[0]


@pytest.mark.integration
class TestRiskReturnIntegration:
    """Test risk-return analysis integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_analyze_single_security_public_interface(self):
        """Test public interface for single security analysis"""
        # Create test data
        test_data = MergedFinancialData(
            ticker="MSFT",
            timestamp="2023-12-31",
            working_capital_ratio=1.3,
            retained_earnings_ratio=0.5,
            ebit_ratio=0.35,
            asset_turnover=0.6,
            current_ratio=2.8,
            debt_to_equity=0.4,
            market_cap=2_800_000_000_000,
            data_quality_score=0.98
        )
        
        # This will use real Z-Score calculation
        result = await analyze_single_security(test_data, sector="technology")
        
        # Validate result
        assert isinstance(result, RecommendationResult)
        assert result.ticker == "MSFT"
        assert result.action in [action for action in RecommendationAction]
        assert result.risk_level in [level for level in RiskLevel]
        assert 0.0 <= result.confidence <= 1.0
        assert result.risk_metrics.z_score > 0  # Should have valid Z-Score
    
    @pytest.mark.asyncio
    async def test_multiple_sector_analysis(self):
        """Test analysis across different sectors"""
        # Technology company
        tech_data = MergedFinancialData(
            ticker="GOOGL",
            timestamp="2023-12-31",
            working_capital_ratio=1.8,
            retained_earnings_ratio=0.6,
            ebit_ratio=0.25,
            asset_turnover=0.7,
            market_cap=1_500_000_000_000,
            data_quality_score=0.95
        )
        
        # Manufacturing company
        manufacturing_data = MergedFinancialData(
            ticker="CAT",
            timestamp="2023-12-31",
            working_capital_ratio=0.9,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.12,
            asset_turnover=1.2,
            market_cap=150_000_000_000,
            data_quality_score=0.90
        )
        
        # Analyze both
        tech_result = await analyze_single_security(tech_data, sector="technology")
        manufacturing_result = await analyze_single_security(manufacturing_data, sector="manufacturing")
        
        # Both should provide valid recommendations
        assert isinstance(tech_result, RecommendationResult)
        assert isinstance(manufacturing_result, RecommendationResult)
        
        # Tech company should likely have better metrics (higher margins, lower operational risk)
        assert tech_result.risk_metrics.financial_strength_score >= manufacturing_result.risk_metrics.financial_strength_score
    
    @pytest.mark.asyncio
    async def test_edge_case_handling(self):
        """Test handling of edge cases and missing data"""
        # Company with minimal data
        minimal_data = MergedFinancialData(
            ticker="MINIMAL",
            timestamp="2023-12-31",
            working_capital_ratio=0.5,
            # Most other fields missing
            data_quality_score=0.3
        )
        
        # Should still provide analysis (with lower confidence)
        result = await analyze_single_security(minimal_data)
        
        assert isinstance(result, RecommendationResult)
        assert result.confidence < 0.7  # Should have lower confidence
        assert len(result.reasoning) > 0
        assert "data" in " ".join(result.reasoning).lower()  # Should mention data limitations
