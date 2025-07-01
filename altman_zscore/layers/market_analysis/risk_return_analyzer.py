"""
Risk-Return Analyzer - Combined fundamental and market risk assessment

Provides comprehensive risk-return analysis including:
- Integration of Z-Score fundamental risk with market risk
- Risk categorization and scoring
- Return potential assessment
- Investment recommendations with confidence levels
- Key risks and opportunities identification
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ...common.logging_config import get_logger
from ...models.market_models import (
    RiskReturnProfile, TechnicalAnalysis, ValuationMetrics, 
    MarketPerformance, AnalysisParameters
)

logger = get_logger(__name__)


class RiskReturnAnalyzer:
    """Risk-return analysis combining fundamental and market factors."""
    
    def __init__(self, parameters: Optional[AnalysisParameters] = None):
        """
        Initialize risk-return analyzer.
        
        Args:
            parameters: Analysis parameters, uses defaults if None
        """
        self.params = parameters or AnalysisParameters()
    
    def analyze_risk_return(
        self, 
        ticker: str,
        z_score: float,
        z_score_category: str,
        technical_analysis: Optional[TechnicalAnalysis] = None,
        valuation_metrics: Optional[ValuationMetrics] = None,
        market_performance: Optional[MarketPerformance] = None
    ) -> RiskReturnProfile:
        """
        Perform comprehensive risk-return analysis.
        
        Args:
            ticker: Stock ticker symbol
            z_score: Altman Z-Score value
            z_score_category: Z-Score risk category
            technical_analysis: Technical analysis results
            valuation_metrics: Valuation analysis results
            market_performance: Performance analysis results
            
        Returns:
            RiskReturnProfile with complete risk-return assessment
        """
        try:
            logger.info(f"Starting risk-return analysis for {ticker}")
            
            # Calculate fundamental risk score
            fundamental_risk = self._calculate_fundamental_risk(z_score, z_score_category, valuation_metrics)
            
            # Calculate market risk score
            market_risk = self._calculate_market_risk(technical_analysis, market_performance)
            
            # Calculate combined risk
            overall_risk = self._calculate_overall_risk(fundamental_risk, market_risk)
            
            # Assess return potential
            return_potential = self._assess_return_potential(
                valuation_metrics, technical_analysis, market_performance
            )
            
            # Generate investment recommendation
            recommendation = self._generate_recommendation(
                overall_risk, return_potential, z_score, technical_analysis, valuation_metrics
            )
            
            # Identify key risks and opportunities
            risks_opportunities = self._identify_risks_opportunities(
                z_score, z_score_category, technical_analysis, valuation_metrics, market_performance
            )
            
            # Calculate Z-Score to price correlation if possible
            zscore_correlation = self._calculate_zscore_price_correlation(
                market_performance, z_score
            )
            
            return RiskReturnProfile(
                ticker=ticker,
                analysis_date=datetime.now(),
                z_score=z_score,
                z_score_risk_category=z_score_category,
                fundamental_risk_score=fundamental_risk['score'],
                market_risk_score=market_risk['score'],
                volatility_risk=market_risk['volatility_risk'],
                liquidity_risk=market_risk['liquidity_risk'],
                overall_risk_score=overall_risk['score'],
                overall_risk_category=overall_risk['category'],
                growth_potential=return_potential['growth_potential'],
                dividend_income=return_potential['dividend_income'],
                total_return_potential=return_potential['total_return_potential'],
                risk_adjusted_score=recommendation['risk_adjusted_score'],
                investment_rating=recommendation['rating'],
                confidence_level=recommendation['confidence'],
                key_risks=risks_opportunities['risks'],
                key_opportunities=risks_opportunities['opportunities'],
                zscore_price_correlation=zscore_correlation
            )
            
        except Exception as e:
            logger.error(f"Risk-return analysis failed for {ticker}: {e}")
            # Return a basic risk profile with available data
            return RiskReturnProfile(
                ticker=ticker,
                analysis_date=datetime.now(),
                z_score=z_score,
                z_score_risk_category=z_score_category,
                fundamental_risk_score=0.5,
                market_risk_score=0.5,
                volatility_risk=0.5,
                liquidity_risk=0.5,
                overall_risk_score=0.5,
                overall_risk_category='medium',
                growth_potential=0.0,
                dividend_income=0.0,
                total_return_potential=0.0,
                risk_adjusted_score=0.0,
                investment_rating='hold',
                confidence_level=0.1,
                key_risks=['Analysis incomplete due to data limitations'],
                key_opportunities=[],
                zscore_price_correlation=None
            )
    
    def _calculate_fundamental_risk(
        self, 
        z_score: float, 
        z_score_category: str, 
        valuation_metrics: Optional[ValuationMetrics]
    ) -> Dict[str, float]:
        """Calculate fundamental risk score from Z-Score and valuation."""
        
        # Base risk from Z-Score
        if z_score_category.lower() == 'safe':
            base_risk = 0.2
        elif z_score_category.lower() == 'gray':
            base_risk = 0.5
        elif z_score_category.lower() == 'distress':
            base_risk = 0.8
        else:
            # Calculate from Z-Score value
            if z_score >= 3.0:
                base_risk = 0.2
            elif z_score >= 1.8:
                base_risk = 0.5
            else:
                base_risk = 0.8
        
        # Adjust for valuation metrics
        valuation_adjustment = 0.0
        
        if valuation_metrics:
            # High P/E increases risk
            if valuation_metrics.pe_ratio and valuation_metrics.pe_ratio > 40:
                valuation_adjustment += 0.1
            elif valuation_metrics.pe_ratio and valuation_metrics.pe_ratio < 10:
                valuation_adjustment -= 0.05  # Low P/E reduces risk slightly
            
            # High PEG increases risk
            if valuation_metrics.peg_ratio and valuation_metrics.peg_ratio > 2.0:
                valuation_adjustment += 0.1
            elif valuation_metrics.peg_ratio and valuation_metrics.peg_ratio < 1.0:
                valuation_adjustment -= 0.05
            
            # Overvaluation increases risk
            if valuation_metrics.relative_valuation == 'overvalued':
                valuation_adjustment += 0.1
            elif valuation_metrics.relative_valuation == 'undervalued':
                valuation_adjustment -= 0.05
        
        final_risk = max(0.0, min(1.0, base_risk + valuation_adjustment))
        
        return {'score': final_risk}
    
    def _calculate_market_risk(
        self, 
        technical_analysis: Optional[TechnicalAnalysis],
        market_performance: Optional[MarketPerformance]
    ) -> Dict[str, float]:
        """Calculate market risk from technical and performance data."""
        
        volatility_risk = 0.5  # Default medium risk
        liquidity_risk = 0.3   # Default low-medium risk
        
        # Volatility risk from technical analysis
        if technical_analysis:
            if technical_analysis.volatility_rank == 'high':
                volatility_risk = 0.8
            elif technical_analysis.volatility_rank == 'medium':
                volatility_risk = 0.5
            elif technical_analysis.volatility_rank == 'low':
                volatility_risk = 0.3
            
            if technical_analysis.volatility_30d:
                # Annualized volatility > 40% is high risk
                if technical_analysis.volatility_30d > 0.4:
                    volatility_risk = max(volatility_risk, 0.8)
                elif technical_analysis.volatility_30d < 0.2:
                    volatility_risk = min(volatility_risk, 0.3)
        
        # Liquidity risk from market performance
        if market_performance:
            # Beta affects risk
            if market_performance.beta and market_performance.beta > 1.5:
                volatility_risk += 0.1  # High beta increases volatility risk
            elif market_performance.beta and market_performance.beta < 0.5:
                volatility_risk -= 0.1  # Low beta decreases volatility risk
            
            # Max drawdown affects risk
            if market_performance.max_drawdown and market_performance.max_drawdown < -0.3:
                volatility_risk += 0.1  # Large drawdowns increase risk
        
        # Overall market risk score
        market_risk_score = (volatility_risk * 0.7) + (liquidity_risk * 0.3)
        market_risk_score = max(0.0, min(1.0, market_risk_score))
        
        return {
            'score': market_risk_score,
            'volatility_risk': max(0.0, min(1.0, volatility_risk)),
            'liquidity_risk': liquidity_risk
        }
    
    def _calculate_overall_risk(self, fundamental_risk: Dict, market_risk: Dict) -> Dict[str, Any]:
        """Calculate overall risk combining fundamental and market factors."""
        
        # Weight fundamental risk more heavily (60/40 split)
        overall_score = (fundamental_risk['score'] * 0.6) + (market_risk['score'] * 0.4)
        
        # Risk categories
        if overall_score <= 0.33:
            category = 'low'
        elif overall_score <= 0.66:
            category = 'medium'
        else:
            category = 'high'
        
        return {
            'score': overall_score,
            'category': category
        }
    
    def _assess_return_potential(
        self,
        valuation_metrics: Optional[ValuationMetrics],
        technical_analysis: Optional[TechnicalAnalysis],
        market_performance: Optional[MarketPerformance]
    ) -> Dict[str, Optional[float]]:
        """Assess return potential from various factors."""
        
        growth_potential = 0.0
        dividend_income = 0.0
        
        # Growth potential from valuation
        if valuation_metrics:
            # Analyst upside
            if valuation_metrics.upside_potential:
                growth_potential += valuation_metrics.upside_potential * 0.5  # 50% weight to analyst targets
            
            # Undervaluation upside
            if valuation_metrics.relative_valuation == 'undervalued':
                growth_potential += 0.1  # 10% upside for undervaluation
            
            # PEG ratio upside
            if valuation_metrics.peg_ratio and valuation_metrics.peg_ratio < 1.0:
                growth_potential += 0.05  # 5% upside for attractive PEG
            
            # Dividend income
            if valuation_metrics.dividend_yield:
                dividend_income = valuation_metrics.dividend_yield
        
        # Technical momentum contribution
        if technical_analysis:
            if technical_analysis.overall_signal == 'buy':
                growth_potential += 0.05
            elif technical_analysis.overall_signal == 'sell':
                growth_potential -= 0.05
            
            # Momentum score contribution
            if technical_analysis.momentum_score:
                growth_potential += technical_analysis.momentum_score * 0.03
        
        # Performance momentum
        if market_performance:
            # Relative performance momentum
            if market_performance.benchmark_3m and market_performance.benchmark_3m > 0.05:
                growth_potential += 0.02  # Positive momentum
            elif market_performance.benchmark_3m and market_performance.benchmark_3m < -0.05:
                growth_potential -= 0.02  # Negative momentum
        
        # Total return potential
        total_return_potential = growth_potential + dividend_income
        
        return {
            'growth_potential': growth_potential,
            'dividend_income': dividend_income,
            'total_return_potential': total_return_potential
        }
    
    def _generate_recommendation(
        self,
        overall_risk: Dict,
        return_potential: Dict,
        z_score: float,
        technical_analysis: Optional[TechnicalAnalysis],
        valuation_metrics: Optional[ValuationMetrics]
    ) -> Dict[str, Any]:
        """Generate investment recommendation and confidence level."""
        
        risk_score = overall_risk['score']
        return_score = return_potential['total_return_potential'] or 0.0
        
        # Risk-adjusted score (return per unit of risk)
        if risk_score > 0:
            risk_adjusted_score = return_score / risk_score
        else:
            risk_adjusted_score = return_score
        
        # Base recommendation logic
        recommendation_score = 0.0
        confidence_factors = []
        
        # Z-Score contribution
        if z_score >= 3.0:
            recommendation_score += 0.3
            confidence_factors.append("Strong Z-Score")
        elif z_score >= 1.8:
            recommendation_score += 0.1
            confidence_factors.append("Moderate Z-Score")
        else:
            recommendation_score -= 0.3
            confidence_factors.append("Weak Z-Score")
        
        # Return potential contribution
        if return_score > 0.15:  # 15%+ expected return
            recommendation_score += 0.3
            confidence_factors.append("High return potential")
        elif return_score > 0.05:  # 5%+ expected return
            recommendation_score += 0.1
            confidence_factors.append("Moderate return potential")
        elif return_score < -0.05:
            recommendation_score -= 0.2
            confidence_factors.append("Negative return expectation")
        
        # Risk adjustment
        if risk_score > 0.7:  # High risk
            recommendation_score -= 0.2
            confidence_factors.append("High risk concern")
        elif risk_score < 0.3:  # Low risk
            recommendation_score += 0.1
            confidence_factors.append("Low risk profile")
        
        # Technical signal contribution
        if technical_analysis:
            if technical_analysis.overall_signal == 'buy':
                recommendation_score += 0.1
                confidence_factors.append("Positive technical signals")
            elif technical_analysis.overall_signal == 'sell':
                recommendation_score -= 0.1
                confidence_factors.append("Negative technical signals")
        
        # Valuation contribution
        if valuation_metrics:
            if valuation_metrics.relative_valuation == 'undervalued':
                recommendation_score += 0.1
                confidence_factors.append("Attractive valuation")
            elif valuation_metrics.relative_valuation == 'overvalued':
                recommendation_score -= 0.1
                confidence_factors.append("Rich valuation")
        
        # Convert to rating
        if recommendation_score >= 0.4:
            rating = 'strong_buy'
        elif recommendation_score >= 0.2:
            rating = 'buy'
        elif recommendation_score >= -0.1:
            rating = 'hold'
        elif recommendation_score >= -0.3:
            rating = 'sell'
        else:
            rating = 'strong_sell'
        
        # Confidence level based on data availability and consistency
        confidence = 0.5  # Base confidence
        
        # Increase confidence with more data
        if technical_analysis:
            confidence += 0.1
        if valuation_metrics:
            confidence += 0.1
        if len(confidence_factors) >= 4:
            confidence += 0.1
        
        # Decrease confidence for conflicting signals
        positive_factors = len([f for f in confidence_factors if any(word in f.lower() 
                               for word in ['strong', 'high', 'positive', 'attractive', 'low risk'])])
        negative_factors = len([f for f in confidence_factors if any(word in f.lower() 
                               for word in ['weak', 'negative', 'rich', 'high risk'])])
        
        if abs(positive_factors - negative_factors) < 2:  # Conflicting signals
            confidence -= 0.1
        
        confidence = max(0.1, min(1.0, confidence))
        
        return {
            'risk_adjusted_score': risk_adjusted_score,
            'rating': rating,
            'confidence': confidence
        }
    
    def _identify_risks_opportunities(
        self,
        z_score: float,
        z_score_category: str,
        technical_analysis: Optional[TechnicalAnalysis],
        valuation_metrics: Optional[ValuationMetrics],
        market_performance: Optional[MarketPerformance]
    ) -> Dict[str, List[str]]:
        """Identify key risks and opportunities."""
        
        risks = []
        opportunities = []
        
        # Z-Score based risks/opportunities
        if z_score < 1.8:
            risks.append("High bankruptcy risk based on Z-Score")
        elif z_score >= 3.0:
            opportunities.append("Strong fundamental health (Z-Score)")
        
        # Technical risks/opportunities
        if technical_analysis:
            if technical_analysis.volatility_rank == 'high':
                risks.append("High price volatility")
            
            if technical_analysis.price_trend == 'downtrend':
                risks.append("Negative price trend")
            elif technical_analysis.price_trend == 'uptrend':
                opportunities.append("Positive price momentum")
            
            # RSI signals
            if technical_analysis.indicators.rsi:
                if technical_analysis.indicators.rsi > 70:
                    risks.append("Overbought conditions (RSI)")
                elif technical_analysis.indicators.rsi < 30:
                    opportunities.append("Oversold conditions - potential bounce")
        
        # Valuation risks/opportunities
        if valuation_metrics:
            if valuation_metrics.pe_ratio and valuation_metrics.pe_ratio > 40:
                risks.append("Very high P/E ratio")
            elif valuation_metrics.pe_ratio and valuation_metrics.pe_ratio < 10:
                opportunities.append("Low P/E ratio - potential value")
            
            if valuation_metrics.peg_ratio and valuation_metrics.peg_ratio > 2.0:
                risks.append("High PEG ratio - expensive growth")
            elif valuation_metrics.peg_ratio and valuation_metrics.peg_ratio < 1.0:
                opportunities.append("Attractive PEG ratio - growth at reasonable price")
            
            if valuation_metrics.relative_valuation == 'overvalued':
                risks.append("Overvalued relative to sector peers")
            elif valuation_metrics.relative_valuation == 'undervalued':
                opportunities.append("Undervalued relative to sector peers")
            
            if valuation_metrics.dividend_yield and valuation_metrics.dividend_yield > 0.04:
                opportunities.append("Attractive dividend yield")
            
            if valuation_metrics.upside_potential and valuation_metrics.upside_potential > 0.15:
                opportunities.append("Significant analyst upside potential")
        
        # Performance risks/opportunities
        if market_performance:
            if market_performance.max_drawdown and market_performance.max_drawdown < -0.3:
                risks.append("Large historical drawdowns")
            
            if market_performance.beta and market_performance.beta > 1.5:
                risks.append("High market beta - amplified market movements")
            elif market_performance.beta and market_performance.beta < 0.8:
                opportunities.append("Low market beta - defensive characteristics")
            
            if market_performance.benchmark_3m and market_performance.benchmark_3m > 0.1:
                opportunities.append("Outperforming market benchmark")
            elif market_performance.benchmark_3m and market_performance.benchmark_3m < -0.1:
                risks.append("Underperforming market benchmark")
            
            if market_performance.sharpe_ratio and market_performance.sharpe_ratio > 1.0:
                opportunities.append("Good risk-adjusted returns")
            elif market_performance.sharpe_ratio and market_performance.sharpe_ratio < 0:
                risks.append("Poor risk-adjusted returns")
        
        return {
            'risks': risks,
            'opportunities': opportunities
        }
    
    def _calculate_zscore_price_correlation(
        self, 
        market_performance: Optional[MarketPerformance], 
        z_score: float
    ) -> Optional[float]:
        """Calculate correlation between Z-Score and recent price performance."""
        
        # This is a simplified implementation
        # In practice, you'd want historical Z-Score data to calculate true correlation
        
        if not market_performance or not market_performance.return_1y:
            return None
        
        # Approximate correlation based on Z-Score category and performance
        annual_return = market_performance.return_1y
        
        # Expected correlation patterns:
        # High Z-Score (safe) + positive returns = positive correlation
        # Low Z-Score (distress) + negative returns = positive correlation
        # Contrarian patterns would show negative correlation
        
        if z_score >= 3.0:  # Safe zone
            if annual_return > 0.1:  # 10%+ return
                estimated_correlation = 0.3  # Moderate positive
            elif annual_return < -0.1:  # -10% return
                estimated_correlation = -0.2  # Weak negative
            else:
                estimated_correlation = 0.1  # Weak positive
        elif z_score <= 1.8:  # Distress zone
            if annual_return > 0.1:  # Strong recovery
                estimated_correlation = -0.4  # Contrarian signal
            elif annual_return < -0.1:  # Continued decline
                estimated_correlation = 0.4  # Confirming signal
            else:
                estimated_correlation = 0.0  # No clear pattern
        else:  # Gray zone
            estimated_correlation = 0.0  # Neutral
        
        return estimated_correlation
    
    def get_risk_return_summary(self, risk_return_profile: RiskReturnProfile) -> Dict[str, Any]:
        """
        Generate a summary of risk-return analysis.
        
        Args:
            risk_return_profile: Completed risk-return analysis
            
        Returns:
            Dictionary with risk-return summary and investment thesis
        """
        summary = {
            'ticker': risk_return_profile.ticker,
            'analysis_date': risk_return_profile.analysis_date,
            'investment_rating': risk_return_profile.investment_rating.upper(),
            'confidence_level': f"{risk_return_profile.confidence_level:.0%}",
            'risk_assessment': {},
            'return_assessment': {},
            'key_points': {},
            'investment_thesis': ""
        }
        
        # Risk assessment
        summary['risk_assessment'] = {
            'Overall Risk': risk_return_profile.overall_risk_category.title(),
            'Z-Score Category': risk_return_profile.z_score_risk_category.title(),
            'Risk Score': f"{risk_return_profile.overall_risk_score:.2f}/1.0"
        }
        
        # Return assessment
        return_assessment = {}
        if risk_return_profile.total_return_potential:
            return_assessment['Total Return Potential'] = f"{risk_return_profile.total_return_potential:.1%}"
        if risk_return_profile.growth_potential:
            return_assessment['Growth Potential'] = f"{risk_return_profile.growth_potential:.1%}"
        if risk_return_profile.dividend_income:
            return_assessment['Dividend Yield'] = f"{risk_return_profile.dividend_income:.1%}"
        if risk_return_profile.risk_adjusted_score:
            return_assessment['Risk-Adjusted Score'] = f"{risk_return_profile.risk_adjusted_score:.2f}"
        
        summary['return_assessment'] = return_assessment
        
        # Key points
        key_points = {
            'Top Risks': risk_return_profile.key_risks[:3],  # Top 3 risks
            'Top Opportunities': risk_return_profile.key_opportunities[:3]  # Top 3 opportunities
        }
        summary['key_points'] = key_points
        
        # Investment thesis
        rating = risk_return_profile.investment_rating
        risk_cat = risk_return_profile.overall_risk_category
        z_score = risk_return_profile.z_score
        
        thesis_parts = []
        
        # Opening based on rating
        if rating in ['strong_buy', 'buy']:
            thesis_parts.append(f"{risk_return_profile.ticker} presents an attractive investment opportunity")
        elif rating == 'hold':
            thesis_parts.append(f"{risk_return_profile.ticker} is appropriately valued with balanced risk-return profile")
        else:
            thesis_parts.append(f"{risk_return_profile.ticker} faces significant challenges")
        
        # Risk component
        thesis_parts.append(f"with {risk_cat} overall risk")
        
        # Z-Score component
        if z_score >= 3.0:
            thesis_parts.append("supported by strong fundamental health")
        elif z_score >= 1.8:
            thesis_parts.append("despite moderate financial stress indicators")
        else:
            thesis_parts.append("amid concerning financial distress signals")
        
        # Return component
        if risk_return_profile.total_return_potential and risk_return_profile.total_return_potential > 0.1:
            thesis_parts.append("and meaningful return potential")
        elif risk_return_profile.total_return_potential and risk_return_profile.total_return_potential > 0:
            thesis_parts.append("with modest return expectations")
        else:
            thesis_parts.append("but limited return visibility")
        
        summary['investment_thesis'] = ". ".join(thesis_parts) + "."
        
        return summary
