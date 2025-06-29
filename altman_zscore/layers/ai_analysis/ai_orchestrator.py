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
                                           include_data_quality: bool = True,
                                           include_peer_analysis: bool = True,
                                           include_sentiment: bool = True,
                                           include_risk_analysis: bool = True,
                                           generate_final_commentary: bool = True) -> ComprehensiveAIAnalysis:
        """
        Perform comprehensive AI-enhanced analysis on financial data.
        
        Args:
            financial_data: Merged financial data to analyze
            include_data_quality: Enable AI data quality checking
            include_peer_analysis: Enable peer comparison analysis
            include_sentiment: Enable sentiment analysis
            include_risk_analysis: Enable risk factor analysis
            generate_final_commentary: Generate LLM-powered final commentary
            
        Returns:
            ComprehensiveAIAnalysis: Complete AI analysis results
            
        Raises:
            AIAnalysisError: If critical AI analysis fails
        """
        try:
            logger.info(f"Starting comprehensive AI analysis for {financial_data.ticker}")
            
            # Initialize results structure
            analysis_results = ComprehensiveAIAnalysis(
                ticker=financial_data.ticker,
                analysis_timestamp=datetime.now(),
                data_quality=None,
                ai_recommendations=[]
            )
            
            # Phase 1: Data Quality Analysis
            if include_data_quality:
                logger.info(f"Running data quality analysis for {financial_data.ticker}")
                analysis_results.data_quality = await self.data_quality_checker.analyze_data_quality(financial_data)
                
                # Add data quality recommendations
                if analysis_results.data_quality.overall_quality_score < 70:
                    analysis_results.ai_recommendations.append(
                        f"Data quality score ({analysis_results.data_quality.overall_quality_score:.1f}/100) "
                        f"indicates {analysis_results.data_quality.reliability_rating} reliability. "
                        f"Consider additional verification before investment decisions."
                    )
            
            # Phase 2: Peer Analysis
            if include_peer_analysis and self.peer_analyzer:
                logger.info(f"Running peer analysis for {financial_data.ticker}")
                try:
                    analysis_results.peer_analysis = await self.peer_analyzer.analyze_peers(financial_data)
                    analysis_results.ai_recommendations.append(
                        f"Peer analysis: {analysis_results.peer_analysis.relative_position} vs industry average. "
                        f"{analysis_results.peer_analysis.investment_implication}"
                    )
                except Exception as e:
                    logger.warning(f"Peer analysis failed for {financial_data.ticker}: {str(e)}")
                    analysis_results.ai_recommendations.append("Peer analysis unavailable due to technical issues.")
            
            # Phase 3: Sentiment Analysis
            if include_sentiment and self.sentiment_analyzer:
                logger.info(f"Running sentiment analysis for {financial_data.ticker}")
                try:
                    analysis_results.sentiment_analysis = await self.sentiment_analyzer.analyze_sentiment(financial_data)
                    sentiment_desc = self._describe_sentiment(analysis_results.sentiment_analysis.overall_sentiment_score)
                    analysis_results.ai_recommendations.append(
                        f"Market sentiment: {sentiment_desc} ({analysis_results.sentiment_analysis.sentiment_trend}). "
                        f"{analysis_results.sentiment_analysis.investment_implication}"
                    )
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed for {financial_data.ticker}: {str(e)}")
                    analysis_results.ai_recommendations.append("Sentiment analysis unavailable due to technical issues.")
            
            # Phase 4: Risk Analysis
            if include_risk_analysis and self.risk_analyzer:
                logger.info(f"Running risk analysis for {financial_data.ticker}")
                try:
                    analysis_results.risk_analysis = await self.risk_analyzer.analyze_risks(financial_data)
                    risk_desc = self._describe_risk(analysis_results.risk_analysis.overall_risk_score)
                    analysis_results.ai_recommendations.append(
                        f"Risk assessment: {risk_desc} ({analysis_results.risk_analysis.risk_trajectory}). "
                        f"{analysis_results.risk_analysis.investment_implication}"
                    )
                except Exception as e:
                    logger.warning(f"Risk analysis failed for {financial_data.ticker}: {str(e)}")
                    analysis_results.ai_recommendations.append("Risk analysis unavailable due to technical issues.")
            
            # Calculate overall AI confidence
            analysis_results.overall_ai_confidence = self._calculate_overall_confidence(analysis_results)
            
            # Generate dashboard summary for integration
            analysis_results.dashboard_summary = self._generate_dashboard_summary(analysis_results)
            
            # Generate LLM final commentary
            if generate_final_commentary:
                analysis_results.llm_final_commentary = await self._generate_final_commentary(analysis_results, financial_data)
            
            logger.info(f"Comprehensive AI analysis complete for {financial_data.ticker}: "
                       f"{analysis_results.overall_ai_confidence:.1%} confidence, "
                       f"{len(analysis_results.ai_recommendations)} recommendations")
            
            return analysis_results
            
        except Exception as e:
            error_msg = f"Comprehensive AI analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    def _calculate_overall_confidence(self, analysis: ComprehensiveAIAnalysis) -> float:
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
    
    async def _generate_final_commentary(self, analysis: ComprehensiveAIAnalysis, 
                                       financial_data: MergedFinancialData) -> Optional[str]:
        """
        Generate comprehensive LLM-powered final commentary using the professional financial analysis prompt.
        
        Args:
            analysis: Complete AI analysis results
            financial_data: Original financial data
            
        Returns:
            LLM-generated final commentary
        """
        try:
            # Load the comprehensive financial analysis prompt
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_fin_analysis.md"
            
            if not prompt_path.exists():
                logger.warning(f"Financial analysis prompt not found at {prompt_path}")
                return self._generate_fallback_commentary(analysis)
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
            
            # Prepare comprehensive analysis data for injection
            analysis_data = self._prepare_data_injection_for_prompt(analysis, financial_data)
            
            # Combine the prompt with the data injection
            full_prompt = f"""
{base_prompt}

## INJECTED DATA FOR ANALYSIS

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
    
    def _prepare_data_injection_for_prompt(self, analysis: ComprehensiveAIAnalysis, 
                                         financial_data: MergedFinancialData) -> str:
        """
        Prepare comprehensive data injection for the financial analysis prompt.
        
        Args:
            analysis: AI analysis results
            financial_data: Financial data
            
        Returns:
            Formatted data injection string
        """
        data_sections = []
        
        # Company Overview
        data_sections.append(f"COMPANY: {analysis.ticker}")
        data_sections.append(f"ANALYSIS_DATE: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        data_sections.append(f"AI_CONFIDENCE: {analysis.overall_ai_confidence:.1%}")
        
        # Financial Data Context
        if financial_data:
            data_sections.append("\n### FINANCIAL DATA CONTEXT")
            data_sections.append(f"Market Cap: {f'${financial_data.market_cap:,.0f}' if financial_data.market_cap else 'N/A'}")
            data_sections.append(f"Current Price: {f'${financial_data.current_price:.2f}' if financial_data.current_price else 'N/A'}")
            data_sections.append(f"Shares Outstanding: {f'{financial_data.shares_outstanding:,.0f}' if financial_data.shares_outstanding else 'N/A'}")
            
            # Financial Ratios
            if financial_data.current_ratio:
                data_sections.append(f"Current Ratio: {financial_data.current_ratio:.2f}")
            if financial_data.debt_to_equity:
                data_sections.append(f"Debt-to-Equity: {financial_data.debt_to_equity:.2f}")
            if financial_data.working_capital_ratio:
                data_sections.append(f"Working Capital Ratio: {financial_data.working_capital_ratio:.3f}")
            if financial_data.retained_earnings_ratio:
                data_sections.append(f"Retained Earnings Ratio: {financial_data.retained_earnings_ratio:.3f}")
            if financial_data.ebit_ratio:
                data_sections.append(f"EBIT Ratio: {financial_data.ebit_ratio:.3f}")
            if financial_data.asset_turnover:
                data_sections.append(f"Asset Turnover: {financial_data.asset_turnover:.3f}")
        
        # Data Quality Assessment
        if analysis.data_quality:
            data_sections.append("\n### AI DATA QUALITY ASSESSMENT")
            data_sections.append(f"Overall Quality Score: {analysis.data_quality.overall_quality_score}/100")
            data_sections.append(f"Reliability Rating: {analysis.data_quality.reliability_rating}")
            data_sections.append(f"Completeness Score: {analysis.data_quality.completeness_score:.1f}")
            data_sections.append(f"Consistency Score: {analysis.data_quality.consistency_score:.1f}")
            data_sections.append(f"Anomalies Detected: {len(analysis.data_quality.anomalies_detected)}")
            
            if analysis.data_quality.anomalies_detected:
                data_sections.append("Key Anomalies:")
                for anomaly in analysis.data_quality.anomalies_detected[:3]:  # Top 3 anomalies
                    data_sections.append(f"  - {anomaly.description} (Severity: {anomaly.severity})")
        
        # Peer Analysis Results
        if analysis.peer_analysis:
            data_sections.append("\n### AI PEER ANALYSIS")
            data_sections.append(f"Relative Position: {analysis.peer_analysis.relative_position}")
            data_sections.append(f"Industry Average Z-Score: {analysis.peer_analysis.industry_average_z_score:.2f}")
            data_sections.append(f"Peers Identified: {len(analysis.peer_analysis.identified_peers)}")
            
            if analysis.peer_analysis.identified_peers:
                peer_tickers = [peer.ticker for peer in analysis.peer_analysis.identified_peers[:5]]
                data_sections.append(f"Key Peers: {', '.join(peer_tickers)}")
            
            data_sections.append(f"Investment Implication: {analysis.peer_analysis.investment_implication}")
            data_sections.append(f"Confidence: {analysis.peer_analysis.confidence:.1%}")
        
        # Sentiment Analysis Results
        if analysis.sentiment_analysis:
            data_sections.append("\n### AI SENTIMENT ANALYSIS")
            sentiment_desc = self._describe_sentiment(analysis.sentiment_analysis.overall_sentiment_score)
            data_sections.append(f"Overall Sentiment: {sentiment_desc} ({analysis.sentiment_analysis.overall_sentiment_score:.2f})")
            data_sections.append(f"Sentiment Trend: {analysis.sentiment_analysis.sentiment_trend}")
            
            if analysis.sentiment_analysis.fundamental_sentiment_divergence:
                data_sections.append(f"Divergence Analysis: {analysis.sentiment_analysis.fundamental_sentiment_divergence}")
            
            data_sections.append(f"Investment Implication: {analysis.sentiment_analysis.investment_implication}")
            data_sections.append(f"Confidence: {analysis.sentiment_analysis.confidence:.1%}")
        
        # Risk Analysis Results
        if analysis.risk_analysis:
            data_sections.append("\n### AI RISK ANALYSIS")
            risk_desc = self._describe_risk(analysis.risk_analysis.overall_risk_score)
            data_sections.append(f"Overall Risk Level: {risk_desc} ({analysis.risk_analysis.overall_risk_score:.2f})")
            data_sections.append(f"Risk Trajectory: {analysis.risk_analysis.risk_trajectory}")
            data_sections.append(f"Key Risk Themes: {', '.join(analysis.risk_analysis.key_risk_themes)}")
            data_sections.append(f"Risk Factors Identified: {len(analysis.risk_analysis.identified_risks)}")
            
            if analysis.risk_analysis.identified_risks:
                data_sections.append("Top Risk Factors:")
                for risk in analysis.risk_analysis.identified_risks[:3]:  # Top 3 risks
                    data_sections.append(f"  - {risk.risk_id}: {risk.description} (Severity: {risk.severity}, Probability: {risk.probability:.1%})")
            
            data_sections.append(f"Investment Implication: {analysis.risk_analysis.investment_implication}")
            data_sections.append(f"Confidence: {analysis.risk_analysis.confidence:.1%}")
        
        # Key AI Recommendations
        if analysis.ai_recommendations:
            data_sections.append("\n### KEY AI RECOMMENDATIONS")
            for i, rec in enumerate(analysis.ai_recommendations, 1):
                data_sections.append(f"{i}. {rec}")
        
        # Raw Financial Data Context (if available)
        if financial_data.raw_fmp_data:
            data_sections.append("\n### ADDITIONAL CONTEXT")
            data_sections.append("Raw financial data available for detailed analysis")
            
            # Add company profile data if available
            if 'profile' in financial_data.raw_fmp_data:
                profiles = financial_data.raw_fmp_data['profile']
                if profiles and len(profiles) > 0:
                    profile = profiles[0] if isinstance(profiles, list) else profiles
                    if profile.get('sector'):
                        data_sections.append(f"Sector: {profile['sector']}")
                    if profile.get('industry'):
                        data_sections.append(f"Industry: {profile['industry']}")
                    if profile.get('description'):
                        # Truncate description to first 200 characters
                        desc = profile['description'][:200] + "..." if len(profile['description']) > 200 else profile['description']
                        data_sections.append(f"Business Description: {desc}")
        
        return "\n".join(data_sections)
