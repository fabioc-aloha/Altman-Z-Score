"""
AI Insights Generator - Generate intelligent investment narratives

This module combines Z-Score analysis with market intelligence to generate
comprehensive, AI-powered investment narratives and insights.

Key Features:
- Risk-adjusted narrative tone based on Z-Score categories
- Integration of fundamental and market analysis
- Actionable investment recommendations
- Professional-grade analysis suitable for decision-making
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError
from ...layers.data_fetch.llm_client import LLMClient
from ...layers.zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class AIInsightsGenerator:
    """Generate AI-powered investment insights and narratives."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize AI insights generator.
        
        Args:
            output_base_path: Base directory for output files
        """
        self.output_base_path = Path(output_base_path)
        self.llm_client = LLMClient()
    
    async def generate_comprehensive_insights(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Optional[str]:
        """
        Generate comprehensive AI-powered investment insights.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated comprehensive insights
        """
        try:
            logger.info(f"Generating comprehensive AI insights for {zscore_result.ticker}")
            
            # Prepare comprehensive analysis context
            analysis_context = self._prepare_analysis_context(zscore_result, market_analysis)
            
            # Generate comprehensive investment narrative
            prompt = self._build_comprehensive_prompt(analysis_context)
            
            insights = await self.llm_client.generate_completion(
                prompt=prompt,
                ticker=zscore_result.ticker,
                interaction_type="comprehensive_investment_analysis",
                max_tokens=2000
            )
            
            if insights:
                logger.info(f"Generated comprehensive insights for {zscore_result.ticker} ({len(insights)} characters)")
                return insights
            else:
                logger.warning(f"No insights generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate comprehensive insights for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_executive_summary(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Optional[str]:
        """
        Generate concise executive summary with key insights.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated executive summary
        """
        try:
            logger.info(f"Generating executive summary for {zscore_result.ticker}")
            
            # Prepare summary context
            analysis_context = self._prepare_analysis_context(zscore_result, market_analysis)
            
            # Generate executive summary
            prompt = self._build_executive_summary_prompt(analysis_context)
            
            summary = await self.llm_client.generate_completion(
                prompt=prompt,
                ticker=zscore_result.ticker,
                interaction_type="executive_summary",
                max_tokens=500
            )
            
            if summary:
                logger.info(f"Generated executive summary for {zscore_result.ticker} ({len(summary)} characters)")
                return summary
            else:
                logger.warning(f"No executive summary generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate executive summary for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_investment_narrative(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Optional[str]:
        """
        Generate focused investment narrative with market context.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated investment narrative
        """
        try:
            logger.info(f"Generating investment narrative for {zscore_result.ticker}")
            
            # Prepare narrative context
            analysis_context = self._prepare_analysis_context(zscore_result, market_analysis)
            
            # Generate investment narrative
            prompt = self._build_investment_narrative_prompt(analysis_context)
            
            narrative = await self.llm_client.generate_completion(
                prompt=prompt,
                ticker=zscore_result.ticker,
                interaction_type="investment_narrative",
                max_tokens=1000
            )
            
            if narrative:
                logger.info(f"Generated investment narrative for {zscore_result.ticker} ({len(narrative)} characters)")
                return narrative
            else:
                logger.warning(f"No investment narrative generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate investment narrative for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_risk_assessment_narrative(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Optional[str]:
        """
        Generate focused risk assessment narrative.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated risk assessment narrative
        """
        try:
            logger.info(f"Generating risk assessment narrative for {zscore_result.ticker}")
            
            analysis_context = self._prepare_analysis_context(zscore_result, market_analysis)
            prompt = self._build_risk_assessment_prompt(analysis_context)
            
            risk_narrative = await self.llm_client.generate_completion(
                prompt=prompt,
                ticker=zscore_result.ticker,
                interaction_type="risk_assessment",
                max_tokens=600
            )
            
            if risk_narrative:
                logger.info(f"Generated risk assessment for {zscore_result.ticker} ({len(risk_narrative)} characters)")
                return risk_narrative
            else:
                logger.warning(f"No risk assessment generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate risk assessment for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_market_context_narrative(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Optional[str]:
        """
        Generate market context and timing narrative.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated market context narrative
        """
        if not market_analysis:
            logger.info(f"No market analysis available for market context narrative for {zscore_result.ticker}")
            return None
            
        try:
            logger.info(f"Generating market context narrative for {zscore_result.ticker}")
            
            analysis_context = self._prepare_analysis_context(zscore_result, market_analysis)
            prompt = self._build_market_context_prompt(analysis_context)
            
            market_narrative = await self.llm_client.generate_completion(
                prompt=prompt,
                ticker=zscore_result.ticker,
                interaction_type="market_context",
                max_tokens=600
            )
            
            if market_narrative:
                logger.info(f"Generated market context for {zscore_result.ticker} ({len(market_narrative)} characters)")
                return market_narrative
            else:
                logger.warning(f"No market context generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate market context for {zscore_result.ticker}: {str(e)}")
            return None
    
    def _prepare_analysis_context(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis = None
    ) -> Dict[str, Any]:
        """Prepare comprehensive analysis context for AI prompts."""
        
        context = {
            # Z-Score Analysis
            'ticker': zscore_result.ticker,
            'z_score': zscore_result.z_score,
            'risk_category': zscore_result.risk_category,
            'model_used': zscore_result.model_used,
            'data_quality_score': zscore_result.data_quality_score,
            'component_values': zscore_result.component_values,
            'warnings': zscore_result.warnings,
            'calculation_timestamp': zscore_result.calculation_timestamp,
            
            # Market Analysis (if available)
            'has_market_analysis': market_analysis is not None,
        }
        
        if market_analysis:
            # Investment Recommendation
            rec = market_analysis.investment_recommendation
            context.update({
                'recommendation_action': rec.action,
                'recommendation_confidence': rec.confidence,
                'recommendation_rationale': rec.rationale,
                'target_price': rec.target_price,
                'stop_loss': rec.stop_loss,
            })
            
            # Technical Analysis
            tech = market_analysis.technical_analysis
            context.update({
                'rsi_14': tech.rsi_14,
                'macd_signal': tech.macd_signal,
                'bollinger_signal': tech.bollinger_signal,
                'momentum_score': tech.momentum_score,
                'trend_direction': tech.trend_direction,
            })
            
            # Valuation Analysis
            val = market_analysis.valuation_analysis
            context.update({
                'current_price': val.current_price,
                'market_cap': val.market_cap,
                'pe_ratio': val.pe_ratio,
                'pb_ratio': val.pb_ratio,
                'ps_ratio': val.ps_ratio,
                'dividend_yield': val.dividend_yield,
            })
            
            # Performance Analysis
            perf = market_analysis.performance_analysis
            context.update({
                'return_1d': perf.return_1d,
                'return_1m': perf.return_1m,
                'return_3m': perf.return_3m,
                'return_1y': perf.return_1y,
                'volatility_1m': perf.volatility_1m,
                'volatility_1y': perf.volatility_1y,
            })
            
            # Risk Analysis
            risk = market_analysis.risk_analysis
            context.update({
                'beta': risk.beta,
                'sharpe_ratio': risk.sharpe_ratio,
                'max_drawdown': risk.max_drawdown,
                'risk_score': risk.risk_score,
            })
        
        return context
    
    def _build_comprehensive_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt."""
        
        risk_tone = self._get_risk_tone(context['risk_category'])
        
        prompt = f"""You are an expert financial analyst providing comprehensive investment analysis for {context['ticker']}.

FINANCIAL HEALTH ANALYSIS:
- Altman Z-Score: {context['z_score']:.2f}
- Risk Category: {context['risk_category']}
- Model Used: {context['model_used']}
- Data Quality: {context['data_quality_score']:.1f}%

COMPONENT BREAKDOWN:
"""
        
        for component, value in context['component_values'].items():
            prompt += f"- {component}: {value}\n"
        
        if context['has_market_analysis']:
            prompt += f"""
MARKET ANALYSIS:
- Investment Recommendation: {context['recommendation_action']} (Confidence: {context['recommendation_confidence']:.1%})
- Current Price: ${context['current_price']:.2f}
- Market Cap: ${context['market_cap']/1e9:.1f}B
- P/E Ratio: {context['pe_ratio']:.1f}
- 1-Year Return: {context['return_1y']*100:.1f}%
- Beta: {context['beta']:.2f}
- RSI: {context['rsi_14']:.1f}
- Technical Trend: {context['trend_direction']}

RECOMMENDATION RATIONALE:
{context['recommendation_rationale']}
"""
        
        prompt += f"""
ANALYSIS REQUIREMENTS:
1. Provide a comprehensive investment analysis combining fundamental (Z-Score) and market perspectives
2. Use {risk_tone} tone appropriate for {context['risk_category']} risk category
3. Address both financial health and market dynamics
4. Provide actionable insights for investors
5. Include risk considerations and potential catalysts
6. Keep analysis professional and data-driven
7. Length: 800-1200 words

Generate a comprehensive investment analysis that combines fundamental strength analysis with market intelligence to provide actionable investment insights."""
        
        return prompt
    
    def _build_executive_summary_prompt(self, context: Dict[str, Any]) -> str:
        """Build executive summary prompt."""
        
        risk_tone = self._get_risk_tone(context['risk_category'])
        
        prompt = f"""Provide a concise executive summary for {context['ticker']} investment analysis.

KEY METRICS:
- Z-Score: {context['z_score']:.2f} ({context['risk_category']})
"""
        
        if context['has_market_analysis']:
            prompt += f"- Recommendation: {context['recommendation_action']} ({context['recommendation_confidence']:.1%} confidence)\n"
            prompt += f"- Current Price: ${context['current_price']:.2f}\n"
            prompt += f"- 1Y Return: {context['return_1y']*100:.1f}%\n"
        
        prompt += f"""
REQUIREMENTS:
1. Use {risk_tone} tone for {context['risk_category']} risk category
2. Summarize the investment thesis in 2-3 key points
3. Highlight the most critical risks and opportunities
4. Provide clear actionable conclusion
5. Length: 150-250 words
6. Written for executive decision-makers

Generate a concise executive summary that captures the essential investment insights."""
        
        return prompt
    
    def _build_investment_narrative_prompt(self, context: Dict[str, Any]) -> str:
        """Build investment narrative prompt."""
        
        risk_tone = self._get_risk_tone(context['risk_category'])
        
        prompt = f"""Create an investment narrative for {context['ticker']} that tells the story of this investment opportunity.

COMPANY PROFILE:
- Ticker: {context['ticker']}
- Financial Health: Z-Score {context['z_score']:.2f} ({context['risk_category']})
"""
        
        if context['has_market_analysis']:
            prompt += f"- Market Position: {context['recommendation_action']} recommendation\n"
            prompt += f"- Valuation: P/E {context['pe_ratio']:.1f}, Market Cap ${context['market_cap']/1e9:.1f}B\n"
            prompt += f"- Performance: {context['return_1y']*100:.1f}% 1-year return\n"
        
        prompt += f"""
NARRATIVE REQUIREMENTS:
1. Tell the investment story from fundamental health perspective
2. Use {risk_tone} tone appropriate for {context['risk_category']} risk level
3. Weave together financial health, market dynamics, and investment thesis
4. Address "why this investment now" question
5. Include both opportunities and risks in the narrative
6. Make it engaging but factual and data-driven
7. Length: 400-600 words

Create a compelling investment narrative that combines financial analysis with market insights."""
        
        return prompt
    
    def _build_risk_assessment_prompt(self, context: Dict[str, Any]) -> str:
        """Build risk assessment prompt."""
        
        prompt = f"""Provide a focused risk assessment for {context['ticker']} based on fundamental and market analysis.

RISK PROFILE:
- Z-Score Risk Level: {context['risk_category']} (Score: {context['z_score']:.2f})
- Data Quality: {context['data_quality_score']:.1f}%
"""
        
        if context['warnings']:
            prompt += "\nDATA WARNINGS:\n"
            for warning in context['warnings']:
                prompt += f"- {warning}\n"
        
        if context['has_market_analysis']:
            prompt += f"""
MARKET RISK INDICATORS:
- Beta: {context['beta']:.2f} (Market sensitivity)
- Volatility (1Y): {context['volatility_1y']*100:.1f}%
- Max Drawdown: {context['max_drawdown']*100:.1f}%
- Sharpe Ratio: {context['sharpe_ratio']:.2f}
- Risk Score: {context['risk_score']*10:.1f}/10
"""
        
        risk_tone = self._get_risk_tone(context['risk_category'])
        
        prompt += f"""
ASSESSMENT REQUIREMENTS:
1. Use {risk_tone} tone appropriate for {context['risk_category']} risk level
2. Identify the 3-4 most significant risks
3. Assess probability and potential impact of each risk
4. Consider both fundamental and market-based risks
5. Provide risk mitigation suggestions for investors
6. Include early warning indicators to monitor
7. Length: 300-400 words
8. Focus on actionable risk insights

Generate a comprehensive risk assessment that helps investors understand and manage investment risks."""
        
        return prompt
    
    def _build_market_context_prompt(self, context: Dict[str, Any]) -> str:
        """Build market context prompt."""
        
        prompt = f"""Analyze the market context and timing for {context['ticker']} investment decision.

CURRENT MARKET POSITION:
- Price: ${context['current_price']:.2f}
- Market Cap: ${context['market_cap']/1e9:.1f}B
- Recent Performance: {context['return_1m']*100:.1f}% (1M), {context['return_1y']*100:.1f}% (1Y)

TECHNICAL INDICATORS:
- RSI: {context['rsi_14']:.1f} ({self._interpret_rsi(context['rsi_14'])})
- MACD Signal: {context['macd_signal']}
- Bollinger Bands: {context['bollinger_signal']}
- Trend Direction: {context['trend_direction']}

VALUATION CONTEXT:
- P/E Ratio: {context['pe_ratio']:.1f}
- P/B Ratio: {context['pb_ratio']:.1f}
- P/S Ratio: {context['ps_ratio']:.1f}
"""
        
        if context['dividend_yield']:
            prompt += f"- Dividend Yield: {context['dividend_yield']*100:.1f}%\n"
        
        prompt += f"""
MARKET TIMING ANALYSIS:
1. Assess current valuation relative to historical ranges
2. Evaluate technical momentum and entry/exit signals
3. Consider market cycle positioning
4. Analyze risk-reward at current levels
5. Identify potential catalysts or headwinds
6. Provide timing recommendations (immediate vs. wait for better entry)
7. Length: 300-400 words
8. Focus on actionable market timing insights

Generate market context analysis that helps with investment timing decisions."""
        
        return prompt
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI values."""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        elif rsi > 60:
            return "Bullish"
        elif rsi < 40:
            return "Bearish"
        else:
            return "Neutral"
    
    def _get_risk_tone(self, risk_category: str) -> str:
        """Get appropriate tone based on risk category."""
        if risk_category == "Distress":
            return "cautious and risk-focused"
        elif risk_category == "Gray":
            return "balanced and measured"
        else:  # Safe
            return "optimistic but prudent"
