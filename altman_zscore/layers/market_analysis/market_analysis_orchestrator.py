"""
Market Analysis Orchestrator - Coordinates all market analysis components

Provides comprehensive market analysis by orchestrating:
- Technical analysis (price trends, momentum, volatility)
- Valuation analysis (ratios, sector comparison, analyst targets)
- Performance analysis (returns, benchmarks, risk metrics)
- Risk-return analysis (combined fundamental and market assessment)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ..._version import __version__
from ...models.market_models import (
    ComprehensiveMarketAnalysis, TechnicalAnalysis, ValuationMetrics,
    MarketPerformance, RiskReturnProfile, AnalysisParameters
)

from .technical_analyzer import TechnicalAnalyzer
from .valuation_analyzer import ValuationAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .risk_return_analyzer import RiskReturnAnalyzer

logger = get_logger(__name__)


class MarketAnalysisOrchestrator:
    """Orchestrates comprehensive market analysis across all components."""
    
    def __init__(self, parameters: Optional[AnalysisParameters] = None):
        """
        Initialize market analysis orchestrator.
        
        Args:
            parameters: Analysis parameters, uses defaults if None
        """
        self.params = parameters or AnalysisParameters()
        
        # Initialize individual analyzers
        self.technical_analyzer = TechnicalAnalyzer(self.params)
        self.valuation_analyzer = ValuationAnalyzer(self.params)
        self.performance_analyzer = PerformanceAnalyzer(self.params)
        self.risk_return_analyzer = RiskReturnAnalyzer(self.params)
    
    def analyze_ticker(
        self, 
        ticker: str, 
        z_score: float, 
        z_score_category: str,
        period: str = "1y"
    ) -> ComprehensiveMarketAnalysis:
        """
        Perform comprehensive market analysis for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            z_score: Altman Z-Score value
            z_score_category: Z-Score risk category
            period: Analysis period for historical data
            
        Returns:
            ComprehensiveMarketAnalysis with all market analysis components
        """
        try:
            logger.info(f"Starting comprehensive market analysis for {ticker}")
            
            # Initialize analysis results
            technical_analysis = None
            valuation_metrics = None
            market_performance = None
            risk_return_profile = None
            
            analysis_completeness = 0.0
            data_quality_score = 1.0
            
            # Technical Analysis
            try:
                technical_analysis = self.technical_analyzer.analyze_ticker(ticker, period)
                analysis_completeness += 0.25
                logger.info(f"Technical analysis completed for {ticker}")
            except Exception as e:
                logger.warning(f"Technical analysis failed for {ticker}: {e}")
                data_quality_score -= 0.15
            
            # Valuation Analysis
            try:
                valuation_metrics = self.valuation_analyzer.analyze_ticker(ticker)
                analysis_completeness += 0.25
                logger.info(f"Valuation analysis completed for {ticker}")
            except Exception as e:
                logger.warning(f"Valuation analysis failed for {ticker}: {e}")
                data_quality_score -= 0.15
            
            # Performance Analysis
            try:
                market_performance = self.performance_analyzer.analyze_ticker(ticker, period)
                analysis_completeness += 0.25
                logger.info(f"Performance analysis completed for {ticker}")
            except Exception as e:
                logger.warning(f"Performance analysis failed for {ticker}: {e}")
                data_quality_score -= 0.15
            
            # Risk-Return Analysis (requires at least some market data)
            try:
                risk_return_profile = self.risk_return_analyzer.analyze_risk_return(
                    ticker=ticker,
                    z_score=z_score,
                    z_score_category=z_score_category,
                    technical_analysis=technical_analysis,
                    valuation_metrics=valuation_metrics,
                    market_performance=market_performance
                )
                analysis_completeness += 0.25
                logger.info(f"Risk-return analysis completed for {ticker}")
            except Exception as e:
                logger.warning(f"Risk-return analysis failed for {ticker}: {e}")
                data_quality_score -= 0.15
                
                # Create basic risk-return profile
                risk_return_profile = RiskReturnProfile(
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
                    key_risks=['Incomplete market analysis'],
                    key_opportunities=[],
                    zscore_price_correlation=None
                )
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                ticker, z_score, z_score_category, technical_analysis, 
                valuation_metrics, market_performance, risk_return_profile
            )
            
            # Ensure data quality score is within bounds
            data_quality_score = max(0.0, min(1.0, data_quality_score))
            
            return ComprehensiveMarketAnalysis(
                ticker=ticker,
                analysis_date=datetime.now(),
                technical_analysis=technical_analysis,
                valuation_metrics=valuation_metrics,
                market_performance=market_performance,
                risk_return_profile=risk_return_profile,
                investment_thesis=executive_summary['investment_thesis'],
                key_strengths=executive_summary['key_strengths'],
                key_concerns=executive_summary['key_concerns'],
                price_target=executive_summary.get('price_target'),
                target_rationale=executive_summary['target_rationale'],
                data_quality_score=data_quality_score,
                analysis_completeness=analysis_completeness,
                generated_at=datetime.now(),
                generator_version=__version__
            )
            
        except Exception as e:
            logger.error(f"Comprehensive market analysis failed for {ticker}: {e}")
            raise DataFetchError(f"Market analysis failed for {ticker}: {str(e)}")
    
    def _generate_executive_summary(
        self,
        ticker: str,
        z_score: float,
        z_score_category: str,
        technical_analysis: Optional[TechnicalAnalysis],
        valuation_metrics: Optional[ValuationMetrics],
        market_performance: Optional[MarketPerformance],
        risk_return_profile: Optional[RiskReturnProfile]
    ) -> Dict[str, Any]:
        """Generate executive summary and investment thesis."""
        
        key_strengths = []
        key_concerns = []
        price_target = None
        
        # Z-Score based assessment
        if z_score >= 3.0:
            key_strengths.append("Strong fundamental health (Z-Score)")
        elif z_score >= 1.8:
            key_strengths.append("Moderate financial stability")
        else:
            key_concerns.append("Financial distress risk (Z-Score)")
        
        # Technical analysis insights
        if technical_analysis:
            if technical_analysis.price_trend == 'uptrend':
                key_strengths.append("Positive price momentum")
            elif technical_analysis.price_trend == 'downtrend':
                key_concerns.append("Negative price trend")
            
            if len(technical_analysis.buy_signals) > len(technical_analysis.sell_signals):
                key_strengths.append("Bullish technical indicators")
            elif len(technical_analysis.sell_signals) > len(technical_analysis.buy_signals):
                key_concerns.append("Bearish technical signals")
            
            if technical_analysis.volatility_rank == 'high':
                key_concerns.append("High price volatility")
            elif technical_analysis.volatility_rank == 'low':
                key_strengths.append("Low volatility profile")
        
        # Valuation insights
        if valuation_metrics:
            if valuation_metrics.relative_valuation == 'undervalued':
                key_strengths.append("Attractive valuation vs peers")
            elif valuation_metrics.relative_valuation == 'overvalued':
                key_concerns.append("Rich valuation vs sector")
            
            if valuation_metrics.peg_ratio and valuation_metrics.peg_ratio < 1.0:
                key_strengths.append("Growth at reasonable price (PEG)")
            elif valuation_metrics.peg_ratio and valuation_metrics.peg_ratio > 2.0:
                key_concerns.append("Expensive growth premium")
            
            if valuation_metrics.dividend_yield and valuation_metrics.dividend_yield > 0.03:
                key_strengths.append("Attractive dividend yield")
            
            # Price target from analyst estimates
            if valuation_metrics.analyst_price_target:
                price_target = valuation_metrics.analyst_price_target
        
        # Performance insights
        if market_performance:
            if market_performance.benchmark_3m and market_performance.benchmark_3m > 0.05:
                key_strengths.append("Strong relative performance")
            elif market_performance.benchmark_3m and market_performance.benchmark_3m < -0.05:
                key_concerns.append("Underperforming benchmark")
            
            if market_performance.sharpe_ratio and market_performance.sharpe_ratio > 1.0:
                key_strengths.append("Good risk-adjusted returns")
            elif market_performance.sharpe_ratio and market_performance.sharpe_ratio < 0:
                key_concerns.append("Poor risk-adjusted performance")
            
            if market_performance.max_drawdown and market_performance.max_drawdown < -0.25:
                key_concerns.append("Large historical drawdowns")
        
        # Investment thesis generation
        investment_thesis = self._create_investment_thesis(
            ticker, z_score, z_score_category, key_strengths, key_concerns, 
            risk_return_profile
        )
        
        # Price target rationale
        target_rationale = self._create_target_rationale(
            price_target, valuation_metrics, technical_analysis, risk_return_profile
        )
        
        return {
            'investment_thesis': investment_thesis,
            'key_strengths': key_strengths[:5],  # Top 5 strengths
            'key_concerns': key_concerns[:5],    # Top 5 concerns
            'price_target': price_target,
            'target_rationale': target_rationale
        }
    
    def _create_investment_thesis(
        self,
        ticker: str,
        z_score: float,
        z_score_category: str,
        key_strengths: List[str],
        key_concerns: List[str],
        risk_return_profile: Optional[RiskReturnProfile]
    ) -> str:
        """Create comprehensive investment thesis."""
        
        thesis_parts = []
        
        # Opening statement
        if risk_return_profile and risk_return_profile.investment_rating in ['strong_buy', 'buy']:
            thesis_parts.append(f"{ticker} represents an attractive investment opportunity")
        elif risk_return_profile and risk_return_profile.investment_rating == 'hold':
            thesis_parts.append(f"{ticker} presents a balanced risk-return profile")
        else:
            thesis_parts.append(f"{ticker} faces significant investment challenges")
        
        # Fundamental component
        if z_score >= 3.0:
            thesis_parts.append("anchored by strong fundamental health")
        elif z_score >= 1.8:
            thesis_parts.append("with moderate financial stability")
        else:
            thesis_parts.append("despite financial distress concerns")
        
        # Strengths and concerns balance
        strength_count = len(key_strengths)
        concern_count = len(key_concerns)
        
        if strength_count > concern_count + 1:
            thesis_parts.append("The investment case is supported by multiple positive factors")
            if key_strengths[:2]:  # Top 2 strengths
                thesis_parts.append(f"including {key_strengths[0].lower()}")
                if len(key_strengths) > 1:
                    thesis_parts.append(f"and {key_strengths[1].lower()}")
        elif concern_count > strength_count + 1:
            thesis_parts.append("However, several risk factors warrant caution")
            if key_concerns[:2]:  # Top 2 concerns
                thesis_parts.append(f"particularly {key_concerns[0].lower()}")
        else:
            thesis_parts.append("with balanced risk and opportunity factors")
        
        # Risk-return conclusion
        if risk_return_profile:
            if risk_return_profile.overall_risk_category == 'low':
                thesis_parts.append("The investment offers an attractive risk-adjusted profile")
            elif risk_return_profile.overall_risk_category == 'high':
                thesis_parts.append("though investors should carefully consider the elevated risk profile")
            else:
                thesis_parts.append("presenting a moderate risk profile suitable for balanced portfolios")
        
        return ". ".join(thesis_parts) + "."
    
    def _create_target_rationale(
        self,
        price_target: Optional[float],
        valuation_metrics: Optional[ValuationMetrics],
        technical_analysis: Optional[TechnicalAnalysis],
        risk_return_profile: Optional[RiskReturnProfile]
    ) -> str:
        """Create price target rationale."""
        
        if not price_target:
            return "No specific price target available due to insufficient analyst coverage or data limitations."
        
        rationale_parts = []
        rationale_parts.append(f"Price target of ${price_target:.2f}")
        
        # Valuation basis
        if valuation_metrics and valuation_metrics.upside_potential:
            upside_pct = valuation_metrics.upside_potential * 100
            rationale_parts.append(f"implies {upside_pct:+.1f}% upside potential")
        
        # Supporting factors
        support_factors = []
        
        if valuation_metrics:
            if valuation_metrics.relative_valuation == 'undervalued':
                support_factors.append("attractive sector-relative valuation")
            if valuation_metrics.peg_ratio and valuation_metrics.peg_ratio < 1.5:
                support_factors.append("reasonable growth valuation")
        
        if technical_analysis and technical_analysis.price_trend == 'uptrend':
            support_factors.append("positive technical momentum")
        
        if risk_return_profile and risk_return_profile.investment_rating in ['buy', 'strong_buy']:
            support_factors.append("favorable risk-return profile")
        
        if support_factors:
            rationale_parts.append(f"supported by {', '.join(support_factors[:3])}")
        
        return ". ".join(rationale_parts) + "."
    
    def get_analysis_summary(self, comprehensive_analysis: ComprehensiveMarketAnalysis) -> Dict[str, Any]:
        """
        Generate a summary of the comprehensive market analysis.
        
        Args:
            comprehensive_analysis: Complete market analysis results
            
        Returns:
            Dictionary with analysis summary and key insights
        """
        summary = {
            'ticker': comprehensive_analysis.ticker,
            'analysis_date': comprehensive_analysis.analysis_date,
            'overall_rating': 'N/A',
            'confidence_level': 'N/A',
            'data_quality': f"{comprehensive_analysis.data_quality_score:.0%}",
            'analysis_completeness': f"{comprehensive_analysis.analysis_completeness:.0%}",
            'executive_summary': {
                'investment_thesis': comprehensive_analysis.investment_thesis,
                'key_strengths': comprehensive_analysis.key_strengths,
                'key_concerns': comprehensive_analysis.key_concerns,
                'price_target': comprehensive_analysis.price_target
            },
            'component_summaries': {}
        }
        
        # Overall rating from risk-return profile
        if comprehensive_analysis.risk_return_profile:
            summary['overall_rating'] = comprehensive_analysis.risk_return_profile.investment_rating.upper()
            summary['confidence_level'] = f"{comprehensive_analysis.risk_return_profile.confidence_level:.0%}"
        
        # Component summaries
        if comprehensive_analysis.technical_analysis:
            tech_summary = {
                'price_trend': comprehensive_analysis.technical_analysis.price_trend.title(),
                'volatility': comprehensive_analysis.technical_analysis.volatility_rank.title(),
                'overall_signal': comprehensive_analysis.technical_analysis.overall_signal.upper()
            }
            summary['component_summaries']['technical'] = tech_summary
        
        if comprehensive_analysis.valuation_metrics:
            val_summary = {}
            if comprehensive_analysis.valuation_metrics.pe_ratio:
                val_summary['P/E Ratio'] = f"{comprehensive_analysis.valuation_metrics.pe_ratio:.1f}"
            if comprehensive_analysis.valuation_metrics.relative_valuation:
                val_summary['Relative Valuation'] = comprehensive_analysis.valuation_metrics.relative_valuation.title()
            summary['component_summaries']['valuation'] = val_summary
        
        if comprehensive_analysis.market_performance:
            perf_summary = {}
            if comprehensive_analysis.market_performance.return_3m:
                perf_summary['3M Return'] = f"{comprehensive_analysis.market_performance.return_3m:.1%}"
            if comprehensive_analysis.market_performance.benchmark_3m:
                perf_summary['vs Benchmark'] = f"{comprehensive_analysis.market_performance.benchmark_3m:+.1%}"
            summary['component_summaries']['performance'] = perf_summary
        
        if comprehensive_analysis.risk_return_profile:
            risk_summary = {
                'Overall Risk': comprehensive_analysis.risk_return_profile.overall_risk_category.title(),
                'Risk Score': f"{comprehensive_analysis.risk_return_profile.overall_risk_score:.2f}/1.0"
            }
            if comprehensive_analysis.risk_return_profile.total_return_potential:
                risk_summary['Return Potential'] = f"{comprehensive_analysis.risk_return_profile.total_return_potential:.1%}"
            summary['component_summaries']['risk_return'] = risk_summary
        
        return summary
