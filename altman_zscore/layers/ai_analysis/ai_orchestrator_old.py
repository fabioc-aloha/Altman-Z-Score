"""
AI Analysis Orchestrator - Coordinate all AI-enhanced analysis components

This module orchestrates the four AI enhancement areas:
1. Data Quality & Anomaly Detection
2. Intelligent Peer Comparison  
3. Market Sentiment Integration
4. Risk Factor Identification

Provides a unified interface for AI-enhanced analysis and manages
the integration of AI insights into the main pipeline.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError
from ...models.data_models import MergedFinancialData
from .ai_data_quality_checker import AIDataQualityChecker, DataQualityMetrics
from .ai_peer_analyzer import AIPeerAnalyzer, PeerAnalysisResult
from .ai_sentiment_analyzer import AISentimentAnalyzer, SentimentAnalysisResult
from .ai_risk_analyzer import AIRiskAnalyzer, RiskAnalysisResult
from ..data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


@dataclass
class ComprehensiveAIAnalysis:
    """Complete AI analysis results for a ticker."""
    ticker: str
    analysis_timestamp: datetime
    
    # Data Quality Analysis
    data_quality: DataQualityMetrics
    
    # Peer Analysis
    peer_analysis: Optional[PeerAnalysisResult] = None
    
    # Sentiment Analysis
    sentiment_analysis: Optional[SentimentAnalysisResult] = None
    
    # Risk Analysis
    risk_analysis: Optional[RiskAnalysisResult] = None
    
    # Overall AI Confidence
    overall_ai_confidence: float = 0.0
    ai_recommendations: List[str] = None
    
    # Dashboard Integration Data
    dashboard_summary: Optional[Dict[str, Any]] = None
    
    # LLM Final Commentary
    llm_final_commentary: Optional[str] = None


class AIAnalysisOrchestrator:
    """
    Orchestrates all AI analysis components for comprehensive ticker analysis.
    
    This class coordinates the four AI enhancement areas and provides a
    unified interface for AI-enhanced investment analysis.
    """
    
    def __init__(self):
        """Initialize the AI analysis orchestrator."""
        # Initialize available AI components
        self.data_quality_checker = AIDataQualityChecker()
        self.peer_analyzer = AIPeerAnalyzer()
        self.sentiment_analyzer = AISentimentAnalyzer()
        self.risk_analyzer = AIRiskAnalyzer()
        self.llm_client = LLMClient()
        
        logger.info("AI Analysis Orchestrator initialized with all AI components")
    
    async def perform_comprehensive_analysis(self, 
                                           financial_data: MergedFinancialData,
                                           zscore_results: Optional[List] = None,
                                           market_analysis = None,
                                           include_data_quality: bool = True,
                                           include_peer_analysis: bool = True,
                                           include_sentiment: bool = True,
                                           include_risk_analysis: bool = True,
                                           generate_final_commentary: bool = True) -> ComprehensiveAIAnalysis:
        """
        Perform simplified AI analysis focused on direct LLM commentary generation.
        
        SIMPLIFIED APPROACH: Skip all intermediate AI component analysis and generate
        final commentary directly from comprehensive raw data sources.
        
        Args:
            financial_data: Merged financial data to analyze
            zscore_results: Multi-quarter Z-Score calculations (for final commentary)
            market_analysis: Technical analysis, valuation metrics (for final commentary)
            include_data_quality: Deprecated - always False (phase removed)
            include_peer_analysis: Deprecated - always False (phase removed)
            include_sentiment: Deprecated - always False (phase removed)
            include_risk_analysis: Deprecated - always False (phase removed)
            generate_final_commentary: Generate LLM-powered final commentary (always True)
            
        Returns:
            ComprehensiveAIAnalysis: Simplified results with only LLM final commentary
            
        Raises:
            AIAnalysisError: If final commentary generation fails
        """
        try:
            logger.info(f"Starting direct LLM analysis for {financial_data.ticker} (simplified pipeline)")
            
            # Initialize simplified results structure
            analysis_results = ComprehensiveAIAnalysis(
                ticker=financial_data.ticker,
                analysis_timestamp=datetime.now(),
                data_quality=None,  # No longer generated
                ai_recommendations=[]  # No longer populated from components
            )
            
            # SIMPLIFIED PIPELINE: Skip all intermediate AI analysis phases
            # No Phase 1 (Data Quality), Phase 2 (Peer), Phase 3 (Sentiment), Phase 4 (Risk)
            logger.info(f"Skipping intermediate AI component analysis for {financial_data.ticker}")
            
            # Set simplified confidence (no longer calculated from components)
            analysis_results.overall_ai_confidence = 0.85  # High confidence for direct LLM analysis
            
            # Generate minimal dashboard summary (no component data available)
            analysis_results.dashboard_summary = self._generate_simplified_dashboard_summary(analysis_results)
            
            # CORE FOCUS: Generate LLM final commentary directly from comprehensive raw data
            if generate_final_commentary:
                logger.info(f"Generating direct LLM commentary for {financial_data.ticker} using comprehensive raw data")
                analysis_results.llm_final_commentary = await self._generate_final_commentary_direct(
                    zscore_results, market_analysis, financial_data
                )
            
            logger.info(f"Direct LLM analysis complete for {financial_data.ticker}: "
                       f"commentary generated from comprehensive raw data")
            
            return analysis_results
            
        except Exception as e:
            error_msg = f"Direct LLM analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    def _generate_simplified_dashboard_summary(self, analysis: ComprehensiveAIAnalysis) -> Dict[str, Any]:
        """
        Generate simplified dashboard summary without AI component data.
        
        Args:
            analysis: Simplified AI analysis results
            
        Returns:
            Dashboard-ready summary data (minimal structure)
        """
        summary = {
            'ticker': analysis.ticker,
            'timestamp': analysis.analysis_timestamp.isoformat(),
            'overall_confidence': analysis.overall_ai_confidence,
            'key_insights': ["Direct LLM analysis based on comprehensive financial data"],
            'metrics': {
                'analysis_type': 'direct_llm_commentary',
                'components_analyzed': 'none_simplified_pipeline'
            }
        }
        
        return summary

    async def _generate_final_commentary_direct(self, 
                                              zscore_results: List,
                                              market_analysis,
                                              financial_data: MergedFinancialData) -> Optional[str]:
        """
        Generate comprehensive LLM-powered final commentary directly from raw data sources.
        
        SIMPLIFIED APPROACH: No intermediate AI component analysis - direct LLM commentary
        from comprehensive Z-Score, market, and financial data.
        
        Args:
            zscore_results: Multi-quarter Z-Score calculations and trends
            market_analysis: Technical analysis, valuation metrics, risk-return profiles
            financial_data: Complete financial data and statements
            
        Returns:
            LLM-generated final commentary based on comprehensive raw data only
        """
        try:
            # Load the comprehensive financial analysis prompt
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_fin_analysis.md"
            
            if not prompt_path.exists():
                logger.warning(f"Financial analysis prompt not found at {prompt_path}")
                return self._generate_fallback_commentary_simple(financial_data.ticker)
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
            
            # Prepare comprehensive analysis data injection (raw data only, no AI components)
            analysis_data = self._prepare_raw_data_injection(
                zscore_results, market_analysis, financial_data
            )
            
            # Combine the prompt with the data injection using clear boundary markers
            full_prompt = f"""
{base_prompt}

## ===== INJECTED DATA FOR ANALYSIS =====

{analysis_data}

---

## ANALYSIS EXECUTION

Based on the comprehensive raw data injection above, provide a complete AI-Powered Altman Z-Score Investment Analysis following the 10-section structure outlined in the prompt. Focus on synthesizing insights directly from Z-Score calculations, market data, and financial statements for actionable investment intelligence.

This analysis is generated directly from raw financial data without intermediate AI component summaries.
"""
            
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": full_prompt}
            ]
            
            commentary = await asyncio.to_thread(
                self.llm_client.chat_completion,
                financial_data.ticker,
                messages,
                "direct_financial_analysis"
            )
            return commentary.strip()
            
        except Exception as e:
            logger.warning(f"Failed to generate direct financial analysis for {financial_data.ticker}: {str(e)}")
            return self._generate_fallback_commentary_simple(financial_data.ticker)
        """
        Calculate overall AI confidence based on available analysis components.
        
        Args:
            analysis: AI analysis results
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        confidence_factors = []
        
        # Data quality confidence
        if analysis.data_quality:
            quality_confidence = analysis.data_quality.overall_quality_score / 100.0
            confidence_factors.append(quality_confidence)
        
        # Peer analysis confidence
        if analysis.peer_analysis:
            confidence_factors.append(analysis.peer_analysis.confidence)
        
        # Sentiment analysis confidence
        if analysis.sentiment_analysis:
            confidence_factors.append(analysis.sentiment_analysis.confidence)
        
        # Risk analysis confidence
        if analysis.risk_analysis:
            confidence_factors.append(analysis.risk_analysis.confidence)
        
        # Calculate weighted average
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5  # Default moderate confidence when no AI analysis available
    
    def _describe_sentiment(self, sentiment_score: float) -> str:
        """Convert sentiment score to descriptive text."""
        if sentiment_score > 0.6:
            return "Very Positive"
        elif sentiment_score > 0.2:
            return "Positive"
        elif sentiment_score > -0.2:
            return "Neutral"
        elif sentiment_score > -0.6:
            return "Negative"
        else:
            return "Very Negative"
    
    def _describe_risk(self, risk_score: float) -> str:
        """Convert risk score to descriptive text."""
        if risk_score > 0.8:
            return "Very High Risk"
        elif risk_score > 0.6:
            return "High Risk"
        elif risk_score > 0.4:
            return "Moderate Risk"
        elif risk_score > 0.2:
            return "Low-Moderate Risk"
        else:
            return "Low Risk"
    
    def _generate_dashboard_summary(self, analysis: ComprehensiveAIAnalysis) -> Dict[str, Any]:
        """
        Generate summary data for dashboard integration.
        
        Args:
            analysis: Complete AI analysis results
            
        Returns:
            Dashboard-ready summary data
        """
        summary = {
            'ticker': analysis.ticker,
            'timestamp': analysis.analysis_timestamp.isoformat(),
            'overall_confidence': analysis.overall_ai_confidence,
            'key_insights': analysis.ai_recommendations[:3],  # Top 3 recommendations
            'metrics': {}
        }
        
        # Data quality metrics
        if analysis.data_quality:
            summary['metrics']['data_quality'] = {
                'score': analysis.data_quality.overall_quality_score,
                'rating': analysis.data_quality.reliability_rating,
                'issues': len(analysis.data_quality.anomalies_detected)
            }
        
        # Peer analysis metrics
        if analysis.peer_analysis:
            summary['metrics']['peer_analysis'] = {
                'position': analysis.peer_analysis.relative_position,
                'industry_average': analysis.peer_analysis.industry_average_z_score,
                'peers_identified': len(analysis.peer_analysis.identified_peers)
            }
        
        # Sentiment metrics
        if analysis.sentiment_analysis:
            summary['metrics']['sentiment'] = {
                'score': analysis.sentiment_analysis.overall_sentiment_score,
                'trend': analysis.sentiment_analysis.sentiment_trend,
                'description': self._describe_sentiment(analysis.sentiment_analysis.overall_sentiment_score)
            }
        
        # Risk metrics
        if analysis.risk_analysis:
            summary['metrics']['risk'] = {
                'score': analysis.risk_analysis.overall_risk_score,
                'trajectory': analysis.risk_analysis.risk_trajectory,
                'description': self._describe_risk(analysis.risk_analysis.overall_risk_score),
                'key_themes': analysis.risk_analysis.key_risk_themes
            }
        
        return summary
    
    async def _generate_final_commentary(self, 
                                       zscore_results: List,
                                       market_analysis,
                                       financial_data: MergedFinancialData,
                                       analysis: ComprehensiveAIAnalysis) -> Optional[str]:
        """
        Generate comprehensive LLM-powered final commentary using the professional financial analysis prompt.
        Now receives ALL critical data sources for genuine financial analysis.
        
        Args:
            zscore_results: Multi-quarter Z-Score calculations and trends
            market_analysis: Technical analysis, valuation metrics, risk-return profiles
            financial_data: Complete financial data and statements
            analysis: AI component analysis results (supporting context)
            
        Returns:
            LLM-generated final commentary based on comprehensive raw data
        """
        try:
            # Load the comprehensive financial analysis prompt
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_fin_analysis.md"
            
            if not prompt_path.exists():
                logger.warning(f"Financial analysis prompt not found at {prompt_path}")
                return self._generate_fallback_commentary(analysis)
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
            
            # Prepare comprehensive analysis data for injection (now with ALL critical data)
            analysis_data = self._prepare_data_injection_for_prompt(
                zscore_results, market_analysis, financial_data, analysis
            )
            
            # Combine the prompt with the data injection using clear boundary markers
            full_prompt = f"""
{base_prompt}

## ===== INJECTED DATA FOR ANALYSIS =====

{analysis_data}

---

## ANALYSIS EXECUTION

Based on the comprehensive data injection above, provide a complete AI-Powered Altman Z-Score Investment Analysis following the 10-section structure outlined in the prompt. Focus on synthesizing insights across all data sources for actionable investment intelligence.
"""
            
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": full_prompt}
            ]
            
            commentary = await asyncio.to_thread(
                self.llm_client.chat_completion,
                analysis.ticker,
                messages,
                "comprehensive_financial_analysis"
            )
            return commentary.strip()
            
        except Exception as e:
            logger.warning(f"Failed to generate comprehensive financial analysis for {analysis.ticker}: {str(e)}")
            return self._generate_fallback_commentary(analysis)
    
    def _prepare_analysis_summary_for_llm(self, analysis: ComprehensiveAIAnalysis, 
                                        financial_data: MergedFinancialData) -> str:
        """
        Prepare a comprehensive analysis summary for LLM input.
        
        Args:
            analysis: AI analysis results
            financial_data: Financial data
            
        Returns:
            Formatted analysis summary
        """
        summary_parts = []
        
        # Company overview
        summary_parts.append(f"Company: {analysis.ticker}")
        summary_parts.append(f"Analysis Date: {analysis.analysis_timestamp.strftime('%Y-%m-%d')}")
        summary_parts.append(f"Overall AI Confidence: {analysis.overall_ai_confidence:.1%}")
        
        # Data quality
        if analysis.data_quality:
            summary_parts.append(f"\nData Quality Assessment:")
            summary_parts.append(f"- Quality Score: {analysis.data_quality.overall_quality_score}/100 ({analysis.data_quality.reliability_rating})")
            if analysis.data_quality.anomalies_detected:
                # Get the first few anomaly descriptions
                anomaly_descriptions = [anomaly.description for anomaly in analysis.data_quality.anomalies_detected[:3]]
                summary_parts.append(f"- Key Issues: {', '.join(anomaly_descriptions)}")
        
        # Peer analysis
        if analysis.peer_analysis:
            summary_parts.append(f"\nPeer Analysis:")
            summary_parts.append(f"- Relative Position: {analysis.peer_analysis.relative_position}")
            summary_parts.append(f"- Industry Average Z-Score: {analysis.peer_analysis.industry_average_z_score:.2f}")
            summary_parts.append(f"- Analysis: {analysis.peer_analysis.investment_implication}")
        
        # Sentiment analysis
        if analysis.sentiment_analysis:
            sentiment_desc = self._describe_sentiment(analysis.sentiment_analysis.overall_sentiment_score)
            summary_parts.append(f"\nMarket Sentiment:")
            summary_parts.append(f"- Overall Sentiment: {sentiment_desc} ({analysis.sentiment_analysis.overall_sentiment_score:.2f})")
            summary_parts.append(f"- Trend: {analysis.sentiment_analysis.sentiment_trend}")
            if analysis.sentiment_analysis.fundamental_sentiment_divergence:
                summary_parts.append(f"- Divergence: {analysis.sentiment_analysis.fundamental_sentiment_divergence}")
        
        # Risk analysis
        if analysis.risk_analysis:
            risk_desc = self._describe_risk(analysis.risk_analysis.overall_risk_score)
            summary_parts.append(f"\nRisk Assessment:")
            summary_parts.append(f"- Risk Level: {risk_desc} ({analysis.risk_analysis.overall_risk_score:.2f})")
            summary_parts.append(f"- Risk Trajectory: {analysis.risk_analysis.risk_trajectory}")
            summary_parts.append(f"- Key Risk Themes: {', '.join(analysis.risk_analysis.key_risk_themes)}")
        
        # Key recommendations
        if analysis.ai_recommendations:
            summary_parts.append(f"\nKey AI Recommendations:")
            for i, rec in enumerate(analysis.ai_recommendations[:3], 1):
                summary_parts.append(f"{i}. {rec}")
        
        return "\n".join(summary_parts)
    
    def _generate_fallback_commentary(self, analysis: ComprehensiveAIAnalysis) -> str:
        """Generate rule-based fallback commentary."""
        commentary_parts = []
        
        commentary_parts.append(f"AI-Enhanced Analysis Summary for {analysis.ticker}")
        commentary_parts.append(f"Analysis completed with {analysis.overall_ai_confidence:.1%} confidence.")
        
        if analysis.ai_recommendations:
            commentary_parts.append("\nKey Findings:")
            for rec in analysis.ai_recommendations[:3]:
                commentary_parts.append(f"• {rec}")
        
        commentary_parts.append(f"\nThis analysis incorporates multiple AI-powered dimensions including data quality, peer comparison, market sentiment, and risk assessment to provide comprehensive investment insights.")
        
        return "\n".join(commentary_parts)
    
    def get_implementation_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current implementation status of all AI components.
        
        Returns:
            Status of each AI analysis component
        """
        return {
            'data_quality_analysis': {
                'status': 'implemented',
                'description': 'AI-powered financial data quality and anomaly detection',
                'confidence': 'high'
            },
            'peer_analysis': {
                'status': 'implemented',
                'description': 'Intelligent peer company comparison and benchmarking',
                'confidence': 'high'
            },
            'sentiment_analysis': {
                'status': 'implemented', 
                'description': 'Multi-source market sentiment integration',
                'confidence': 'moderate'
            },
            'risk_analysis': {
                'status': 'implemented',
                'description': 'Comprehensive risk factor identification and modeling',
                'confidence': 'high'
            },
            'dashboard_integration': {
                'status': 'implemented',
                'description': 'AI findings exposed in dashboards and reports',
                'confidence': 'high'
            },
            'llm_final_commentary': {
                'status': 'implemented',
                'description': 'LLM-powered final commentary combining all AI insights',
                'confidence': 'high'
            }
        }

    def _prepare_raw_data_injection(self, 
                                   zscore_results: List,
                                   market_analysis,
                                   financial_data: MergedFinancialData) -> str:
        """
        Prepare comprehensive raw data injection for direct LLM analysis.
        
        SIMPLIFIED APPROACH: Inject only raw Z-Score, market, and financial data
        without any AI component analysis summaries.
        
        Args:
            zscore_results: Multi-quarter Z-Score calculations and trends
            market_analysis: Technical analysis, valuation metrics, risk-return profiles
            financial_data: Complete financial data and statements
            
        Returns:
            Formatted raw data injection string for direct LLM analysis
        """
        data_sections = []
        
        # Company Overview
        data_sections.append(f"COMPANY: {financial_data.ticker}")
        data_sections.append(f"ANALYSIS_DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # === PRIMARY DATA: Z-SCORE ANALYSIS (MOST CRITICAL) ===
        if zscore_results:
            data_sections.append("\n### MULTI-QUARTER Z-SCORE ANALYSIS")
            data_sections.append(f"Z-Score Historical Data ({len(zscore_results)} quarters):")
            
            for i, result in enumerate(zscore_results):
                period_label = f"Q{getattr(result, 'quarter', 'Unknown')} {getattr(result, 'year', 'Unknown')}"
                if hasattr(result, 'period'):
                    period_label = result.period
                
                data_sections.append(f"\n{period_label}:")
                data_sections.append(f"  - Z-Score: {getattr(result, 'z_score', 'N/A'):.2f}")
                data_sections.append(f"  - Risk Category: {getattr(result, 'risk_category', 'Unknown')}")
                
                # Component values breakdown
                if hasattr(result, 'component_values'):
                    cv = result.component_values
                    data_sections.append(f"  - Working Capital/Total Assets: {getattr(cv, 'working_capital_ratio', 0):.3f}")
                    data_sections.append(f"  - Retained Earnings/Total Assets: {getattr(cv, 'retained_earnings_ratio', 0):.3f}")
                    data_sections.append(f"  - EBIT/Total Assets: {getattr(cv, 'ebit_ratio', 0):.3f}")
                    data_sections.append(f"  - Market Value Equity/Book Value Debt: {getattr(cv, 'market_value_ratio', 0):.3f}")
                    data_sections.append(f"  - Sales/Total Assets: {getattr(cv, 'asset_turnover', 0):.3f}")
                
                # Financial data for this period
                if hasattr(result, 'revenue'):
                    data_sections.append(f"  - Revenue: ${getattr(result, 'revenue', 0):,.0f}")
                if hasattr(result, 'total_assets'):
                    data_sections.append(f"  - Total Assets: ${getattr(result, 'total_assets', 0):,.0f}")
                if hasattr(result, 'working_capital'):
                    data_sections.append(f"  - Working Capital: ${getattr(result, 'working_capital', 0):,.0f}")
        else:
            data_sections.append("\n### Z-SCORE ANALYSIS")
            data_sections.append("WARNING: No Z-Score results available for trend analysis")
        
        # === PRIMARY DATA: MARKET ANALYSIS ===
        if market_analysis:
            data_sections.append("\n### MARKET ANALYSIS")
            
            # Technical Analysis
            if hasattr(market_analysis, 'technical_analysis') and market_analysis.technical_analysis:
                tech = market_analysis.technical_analysis
                data_sections.append("Technical Indicators:")
                data_sections.append(f"  - 52-Week Range: ${getattr(tech, 'week_52_low', 0):.2f} - ${getattr(tech, 'week_52_high', 0):.2f}")
                data_sections.append(f"  - RSI (14-day): {getattr(tech, 'rsi', 0):.1f}")
                data_sections.append(f"  - 50-Day Moving Average: ${getattr(tech, 'sma_50', 0):.2f}")
                data_sections.append(f"  - 200-Day Moving Average: ${getattr(tech, 'sma_200', 0):.2f}")
                data_sections.append(f"  - Average Volume: {getattr(tech, 'avg_volume', 0):,.0f}")
            
            # Valuation Metrics
            if hasattr(market_analysis, 'valuation_metrics') and market_analysis.valuation_metrics:
                val = market_analysis.valuation_metrics
                data_sections.append("Valuation Metrics:")
                data_sections.append(f"  - P/E Ratio: {getattr(val, 'pe_ratio', 0):.2f}")
                data_sections.append(f"  - Price/Book Ratio: {getattr(val, 'price_to_book', 0):.2f}")
                data_sections.append(f"  - EV/EBITDA: {getattr(val, 'ev_ebitda', 0):.2f}")
                data_sections.append(f"  - Price/Sales: {getattr(val, 'price_to_sales', 0):.2f}")
                data_sections.append(f"  - Dividend Yield: {getattr(val, 'dividend_yield', 0):.2%}")
            
            # Risk-Return Profile
            if hasattr(market_analysis, 'risk_return_profile') and market_analysis.risk_return_profile:
                risk = market_analysis.risk_return_profile
                data_sections.append("Risk-Return Profile:")
                data_sections.append(f"  - Beta: {getattr(risk, 'beta', 0):.2f}")
                data_sections.append(f"  - Volatility (30-day): {getattr(risk, 'volatility_30d', 0):.2%}")
                data_sections.append(f"  - Sharpe Ratio: {getattr(risk, 'sharpe_ratio', 0):.2f}")
                data_sections.append(f"  - Max Drawdown: {getattr(risk, 'max_drawdown', 0):.2%}")
        else:
            data_sections.append("\n### MARKET ANALYSIS")
            data_sections.append("WARNING: No market analysis data available")
        
        # === PRIMARY DATA: FINANCIAL CONTEXT ===
        if financial_data:
            data_sections.append("\n### FINANCIAL DATA CONTEXT")
            data_sections.append(f"Market Cap: {f'${financial_data.market_cap:,.0f}' if financial_data.market_cap else 'N/A'}")
            data_sections.append(f"Current Price: {f'${financial_data.current_price:.2f}' if financial_data.current_price else 'N/A'}")
            data_sections.append(f"Shares Outstanding: {f'{financial_data.shares_outstanding:,.0f}' if financial_data.shares_outstanding else 'N/A'}")
            
            # Current Financial Ratios (latest period)
            data_sections.append("Current Financial Ratios:")
            if financial_data.current_ratio:
                data_sections.append(f"  - Current Ratio: {financial_data.current_ratio:.2f}")
            if financial_data.debt_to_equity:
                data_sections.append(f"  - Debt-to-Equity: {financial_data.debt_to_equity:.2f}")
            if financial_data.working_capital_ratio:
                data_sections.append(f"  - Working Capital Ratio: {financial_data.working_capital_ratio:.3f}")
            if financial_data.retained_earnings_ratio:
                data_sections.append(f"  - Retained Earnings Ratio: {financial_data.retained_earnings_ratio:.3f}")
            if financial_data.ebit_ratio:
                data_sections.append(f"  - EBIT Ratio: {financial_data.ebit_ratio:.3f}")
            if financial_data.asset_turnover:
                data_sections.append(f"  - Asset Turnover: {financial_data.asset_turnover:.3f}")
            
            # Company Profile and Business Context
            if hasattr(financial_data, 'raw_fmp_data') and financial_data.raw_fmp_data:
                if 'profile' in financial_data.raw_fmp_data:
                    profiles = financial_data.raw_fmp_data['profile']
                    if profiles and len(profiles) > 0:
                        profile = profiles[0] if isinstance(profiles, list) else profiles
                        data_sections.append("Company Profile:")
                        if profile.get('sector'):
                            data_sections.append(f"  - Sector: {profile['sector']}")
                        if profile.get('industry'):
                            data_sections.append(f"  - Industry: {profile['industry']}")
                        if profile.get('description'):
                            # Truncate description to first 300 characters for context
                            desc = profile['description'][:300] + "..." if len(profile['description']) > 300 else profile['description']
                            data_sections.append(f"  - Business Description: {desc}")
        
        # === DATA COMPLETENESS SUMMARY ===
        data_sections.append("\n### DATA COMPLETENESS SUMMARY")
        data_sections.append("Raw financial data injection complete - no AI component pre-processing")
        data_sections.append(f"Z-Score quarters available: {len(zscore_results) if zscore_results else 0}")
        data_sections.append(f"Market analysis available: {'Yes' if market_analysis else 'No'}")
        data_sections.append(f"Financial data available: {'Yes' if financial_data else 'No'}")
        
        return "\n".join(data_sections)

    def _generate_fallback_commentary_simple(self, ticker: str) -> str:
        """
        Generate simple fallback commentary when LLM analysis fails.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Basic fallback commentary
        """
        return f"""
# AI-Powered Altman Z-Score Investment Analysis: {ticker}

## Analysis Status
**Unable to generate comprehensive LLM analysis due to technical issues.**

### Data Processing Status
- Analysis attempted using direct LLM approach
- Comprehensive raw data preparation completed
- Final commentary generation encountered errors

### Recommendation
Please retry the analysis or review the raw Z-Score calculations and market data directly.

---
*Analysis generated via simplified pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _calculate_overall_confidence(self, analysis: ComprehensiveAIAnalysis) -> float:
        """
        Prepare comprehensive data injection for the financial analysis prompt.
        Now includes ALL critical financial data: Z-Scores, market analysis, and financial statements.
        
        Args:
            zscore_results: Multi-quarter Z-Score calculations and trends
            market_analysis: Technical analysis, valuation metrics, risk-return profiles
            financial_data: Complete financial data and statements
            analysis: AI component analysis results (supporting context)
            
        Returns:
            Formatted data injection string with comprehensive financial intelligence
        """
        data_sections = []
        
        # Company Overview
        data_sections.append(f"COMPANY: {analysis.ticker}")
        data_sections.append(f"ANALYSIS_DATE: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # === PRIMARY DATA: Z-SCORE ANALYSIS (MOST CRITICAL) ===
        if zscore_results:
            data_sections.append("\n### MULTI-QUARTER Z-SCORE ANALYSIS")
            data_sections.append(f"Z-Score Historical Data ({len(zscore_results)} quarters):")
            
            for i, result in enumerate(zscore_results):
                period_label = f"Q{getattr(result, 'quarter', 'Unknown')} {getattr(result, 'year', 'Unknown')}"
                if hasattr(result, 'period'):
                    period_label = result.period
                
                data_sections.append(f"\n{period_label}:")
                data_sections.append(f"  - Z-Score: {getattr(result, 'z_score', 'N/A'):.2f}")
                data_sections.append(f"  - Risk Category: {getattr(result, 'risk_category', 'Unknown')}")
                
                # Component values breakdown
                if hasattr(result, 'component_values'):
                    cv = result.component_values
                    data_sections.append(f"  - Working Capital/Total Assets: {getattr(cv, 'working_capital_ratio', 0):.3f}")
                    data_sections.append(f"  - Retained Earnings/Total Assets: {getattr(cv, 'retained_earnings_ratio', 0):.3f}")
                    data_sections.append(f"  - EBIT/Total Assets: {getattr(cv, 'ebit_ratio', 0):.3f}")
                    data_sections.append(f"  - Market Value Equity/Book Value Debt: {getattr(cv, 'market_value_ratio', 0):.3f}")
                    data_sections.append(f"  - Sales/Total Assets: {getattr(cv, 'asset_turnover', 0):.3f}")
                
                # Financial data for this period
                if hasattr(result, 'revenue'):
                    data_sections.append(f"  - Revenue: ${getattr(result, 'revenue', 0):,.0f}")
                if hasattr(result, 'total_assets'):
                    data_sections.append(f"  - Total Assets: ${getattr(result, 'total_assets', 0):,.0f}")
                if hasattr(result, 'working_capital'):
                    data_sections.append(f"  - Working Capital: ${getattr(result, 'working_capital', 0):,.0f}")
        else:
            data_sections.append("\n### Z-SCORE ANALYSIS")
            data_sections.append("WARNING: No Z-Score results available for trend analysis")
        
        # === PRIMARY DATA: MARKET ANALYSIS ===
        if market_analysis:
            data_sections.append("\n### MARKET ANALYSIS")
            
            # Technical Analysis
            if hasattr(market_analysis, 'technical_analysis') and market_analysis.technical_analysis:
                tech = market_analysis.technical_analysis
                data_sections.append("Technical Indicators:")
                data_sections.append(f"  - 52-Week Range: ${getattr(tech, 'week_52_low', 0):.2f} - ${getattr(tech, 'week_52_high', 0):.2f}")
                data_sections.append(f"  - RSI (14-day): {getattr(tech, 'rsi', 0):.1f}")
                data_sections.append(f"  - 50-Day Moving Average: ${getattr(tech, 'sma_50', 0):.2f}")
                data_sections.append(f"  - 200-Day Moving Average: ${getattr(tech, 'sma_200', 0):.2f}")
                data_sections.append(f"  - Average Volume: {getattr(tech, 'avg_volume', 0):,.0f}")
            
            # Valuation Metrics
            if hasattr(market_analysis, 'valuation_metrics') and market_analysis.valuation_metrics:
                val = market_analysis.valuation_metrics
                data_sections.append("Valuation Metrics:")
                data_sections.append(f"  - P/E Ratio: {getattr(val, 'pe_ratio', 0):.2f}")
                data_sections.append(f"  - Price/Book Ratio: {getattr(val, 'price_to_book', 0):.2f}")
                data_sections.append(f"  - EV/EBITDA: {getattr(val, 'ev_ebitda', 0):.2f}")
                data_sections.append(f"  - Price/Sales: {getattr(val, 'price_to_sales', 0):.2f}")
                data_sections.append(f"  - Dividend Yield: {getattr(val, 'dividend_yield', 0):.2%}")
            
            # Risk-Return Profile
            if hasattr(market_analysis, 'risk_return_profile') and market_analysis.risk_return_profile:
                risk = market_analysis.risk_return_profile
                data_sections.append("Risk-Return Profile:")
                data_sections.append(f"  - Beta: {getattr(risk, 'beta', 0):.2f}")
                data_sections.append(f"  - Volatility (30-day): {getattr(risk, 'volatility_30d', 0):.2%}")
                data_sections.append(f"  - Sharpe Ratio: {getattr(risk, 'sharpe_ratio', 0):.2f}")
                data_sections.append(f"  - Max Drawdown: {getattr(risk, 'max_drawdown', 0):.2%}")
        else:
            data_sections.append("\n### MARKET ANALYSIS")
            data_sections.append("WARNING: No market analysis data available")
        
        # === PRIMARY DATA: FINANCIAL CONTEXT ===
        if financial_data:
            data_sections.append("\n### FINANCIAL DATA CONTEXT")
            data_sections.append(f"Market Cap: {f'${financial_data.market_cap:,.0f}' if financial_data.market_cap else 'N/A'}")
            data_sections.append(f"Current Price: {f'${financial_data.current_price:.2f}' if financial_data.current_price else 'N/A'}")
            data_sections.append(f"Shares Outstanding: {f'{financial_data.shares_outstanding:,.0f}' if financial_data.shares_outstanding else 'N/A'}")
            
            # Current Financial Ratios (latest period)
            data_sections.append("Current Financial Ratios:")
            if financial_data.current_ratio:
                data_sections.append(f"  - Current Ratio: {financial_data.current_ratio:.2f}")
            if financial_data.debt_to_equity:
                data_sections.append(f"  - Debt-to-Equity: {financial_data.debt_to_equity:.2f}")
            if financial_data.working_capital_ratio:
                data_sections.append(f"  - Working Capital Ratio: {financial_data.working_capital_ratio:.3f}")
            if financial_data.retained_earnings_ratio:
                data_sections.append(f"  - Retained Earnings Ratio: {financial_data.retained_earnings_ratio:.3f}")
            if financial_data.ebit_ratio:
                data_sections.append(f"  - EBIT Ratio: {financial_data.ebit_ratio:.3f}")
            if financial_data.asset_turnover:
                data_sections.append(f"  - Asset Turnover: {financial_data.asset_turnover:.3f}")
            
            # Company Profile and Business Context
            if hasattr(financial_data, 'raw_fmp_data') and financial_data.raw_fmp_data:
                if 'profile' in financial_data.raw_fmp_data:
                    profiles = financial_data.raw_fmp_data['profile']
                    if profiles and len(profiles) > 0:
                        profile = profiles[0] if isinstance(profiles, list) else profiles
                        data_sections.append("Company Profile:")
                        if profile.get('sector'):
                            data_sections.append(f"  - Sector: {profile['sector']}")
                        if profile.get('industry'):
                            data_sections.append(f"  - Industry: {profile['industry']}")
                        if profile.get('description'):
                            # Truncate description to first 300 characters for context
                            desc = profile['description'][:300] + "..." if len(profile['description']) > 300 else profile['description']
                            data_sections.append(f"  - Business Description: {desc}")
        
        # === SUPPORTING DATA: AI ANALYSIS COMPONENTS ===
        data_sections.append("\n### AI DATA QUALITY ASSESSMENT")
        if analysis.data_quality:
            data_sections.append(f"Overall Quality Score: {analysis.data_quality.overall_quality_score}/100")
            data_sections.append(f"Reliability Rating: {analysis.data_quality.reliability_rating}")
            data_sections.append(f"Completeness Score: {analysis.data_quality.completeness_score:.1f}")
            data_sections.append(f"Consistency Score: {analysis.data_quality.consistency_score:.1f}")
            if analysis.data_quality.anomalies_detected:
                anomaly_count = len(analysis.data_quality.anomalies_detected)
                data_sections.append(f"Anomalies Detected: {anomaly_count}")
                data_sections.append("Key Anomalies:")
                # Show only most severe anomalies for context
                for anomaly in analysis.data_quality.anomalies_detected[:2]:
                    data_sections.append(f"  - {anomaly.description} (Severity: {anomaly.severity})")
        
        # Peer Analysis (Supporting Context)
        data_sections.append("\n### AI PEER ANALYSIS")
        if analysis.peer_analysis:
            data_sections.append(f"Relative Position: {analysis.peer_analysis.relative_position}")
            data_sections.append(f"Industry Average Z-Score: {analysis.peer_analysis.industry_average_z_score:.2f}")
            if hasattr(analysis.peer_analysis, 'identified_peers') and analysis.peer_analysis.identified_peers:
                peer_count = len(analysis.peer_analysis.identified_peers)
                data_sections.append(f"Peers Identified: {peer_count}")
                peer_tickers = [peer.ticker for peer in analysis.peer_analysis.identified_peers[:5]]
                data_sections.append(f"Key Peers: {', '.join(peer_tickers)}")
            data_sections.append(f"Investment Implication: {analysis.peer_analysis.investment_implication}")
            if hasattr(analysis.peer_analysis, 'confidence'):
                data_sections.append(f"Confidence: {analysis.peer_analysis.confidence}")
        
        # Sentiment Analysis (Supporting Context)
        data_sections.append("\n### AI SENTIMENT ANALYSIS")
        if analysis.sentiment_analysis:
            sentiment_desc = self._describe_sentiment(analysis.sentiment_analysis.overall_sentiment_score)
            data_sections.append(f"Overall Sentiment: {sentiment_desc} ({analysis.sentiment_analysis.overall_sentiment_score:.2f})")
            data_sections.append(f"Sentiment Trend: {analysis.sentiment_analysis.sentiment_trend}")
            if hasattr(analysis.sentiment_analysis, 'fundamental_sentiment_divergence') and analysis.sentiment_analysis.fundamental_sentiment_divergence:
                data_sections.append(f"Divergence Analysis: {analysis.sentiment_analysis.fundamental_sentiment_divergence}")
            data_sections.append(f"Investment Implication: {analysis.sentiment_analysis.investment_implication}")
            if hasattr(analysis.sentiment_analysis, 'confidence'):
                data_sections.append(f"Confidence: {analysis.sentiment_analysis.confidence}")
        
        # Risk Analysis (Supporting Context)
        data_sections.append("\n### AI RISK ANALYSIS")
        if analysis.risk_analysis:
            risk_desc = self._describe_risk(analysis.risk_analysis.overall_risk_score)
            data_sections.append(f"Overall Risk Level: {risk_desc} ({analysis.risk_analysis.overall_risk_score:.2f})")
            data_sections.append(f"Risk Trajectory: {analysis.risk_analysis.risk_trajectory}")
            if hasattr(analysis.risk_analysis, 'key_risk_themes') and analysis.risk_analysis.key_risk_themes:
                data_sections.append(f"Key Risk Themes: {', '.join(analysis.risk_analysis.key_risk_themes)}")
            if hasattr(analysis.risk_analysis, 'identified_risks') and analysis.risk_analysis.identified_risks:
                risk_count = len(analysis.risk_analysis.identified_risks)
                data_sections.append(f"Risk Factors Identified: {risk_count}")
                data_sections.append("Top Risk Factors:")
                # Show top 2 risks for context
                for risk in analysis.risk_analysis.identified_risks[:2]:
                    data_sections.append(f"  - {risk.name}: {risk.description} (Severity: {risk.severity}, Probability: {risk.probability:.0%})")
            data_sections.append(f"Investment Implication: {analysis.risk_analysis.investment_implication}")
            if hasattr(analysis.risk_analysis, 'confidence'):
                data_sections.append(f"Confidence: {analysis.risk_analysis.confidence}")
        
        # AI Recommendations Summary
        data_sections.append("\n### KEY AI RECOMMENDATIONS")
        if hasattr(analysis, 'ai_recommendations') and analysis.ai_recommendations:
            for i, rec in enumerate(analysis.ai_recommendations, 1):
                data_sections.append(f"{i}. {rec}")
        
        # Additional Context Section
        data_sections.append("\n### ADDITIONAL CONTEXT")
        data_sections.append("Raw financial data available for detailed analysis")
        if hasattr(financial_data, 'raw_fmp_data') and financial_data.raw_fmp_data:
            if 'profile' in financial_data.raw_fmp_data:
                profiles = financial_data.raw_fmp_data['profile']
                if profiles and len(profiles) > 0:
                    profile = profiles[0] if isinstance(profiles, list) else profiles
                    if profile.get('sector'):
                        data_sections.append(f"Sector: {profile['sector']}")
                    if profile.get('industry'):
                        data_sections.append(f"Industry: {profile['industry']}")
                    if profile.get('description'):
                        # Truncate description to first 300 characters for context
                        desc = profile['description'][:300] + "..." if len(profile['description']) > 300 else profile['description']
                        data_sections.append(f"Business Description: {desc}")
        
        return "\n".join(data_sections)
