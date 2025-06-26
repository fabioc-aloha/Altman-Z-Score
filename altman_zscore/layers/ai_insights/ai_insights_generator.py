"""
AI Insights Generator - Natural language investment narratives

This module generates AI-powered investment insights combining Z-Score analysis
with market intelligence to provide comprehensive, risk-aware investment narratives.

Key Features:
- Natural language investment summaries
- Risk-category-aware tone adaptation
- Market context integration
- Investment recommendation explanations
- Professional narrative generation
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..data_fetch.llm_client import LLMClient
from ..zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class AIInsightsGenerator:
    """Generator for AI-powered investment insights and narratives."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize AI insights generator.
        
        Args:
            output_base_path: Base directory for output files
        """
        self.output_base_path = output_base_path
        self.llm_client = LLMClient()  # Uses default config from environment
    
    async def generate_investment_narrative(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis=None
    ) -> Optional[str]:
        """
        Generate comprehensive investment narrative combining Z-Score and market analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated investment narrative
        """
        try:
            # Create comprehensive data context for AI analysis
            context_data = self._prepare_analysis_context(zscore_result, market_analysis)
            
            # Generate the narrative using AI
            narrative = await self._generate_narrative_with_ai(context_data)
            
            logger.info(f"Investment narrative generated for {zscore_result.ticker}")
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to generate investment narrative for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_executive_summary(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis=None
    ) -> Optional[str]:
        """
        Generate concise executive summary for quick decision-making.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated executive summary
        """
        try:
            context_data = self._prepare_analysis_context(zscore_result, market_analysis)
            summary = await self._generate_executive_summary_with_ai(context_data)
            
            logger.info(f"Executive summary generated for {zscore_result.ticker}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary for {zscore_result.ticker}: {str(e)}")
            return None
    
    async def generate_risk_assessment_narrative(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis=None
    ) -> Optional[str]:
        """
        Generate focused risk assessment narrative.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Optional[str]: AI-generated risk assessment
        """
        try:
            context_data = self._prepare_analysis_context(zscore_result, market_analysis)
            risk_narrative = await self._generate_risk_assessment_with_ai(context_data)
            
            logger.info(f"Risk assessment narrative generated for {zscore_result.ticker}")
            return risk_narrative
            
        except Exception as e:
            logger.error(f"Failed to generate risk assessment for {zscore_result.ticker}: {str(e)}")
            return None
    
    def _prepare_analysis_context(
        self, 
        zscore_result: ZScoreCalculationResult,
        market_analysis=None
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive context data for AI analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results
            
        Returns:
            Dict[str, Any]: Structured context data
        """
        context = {
            # Basic company information
            "ticker": zscore_result.ticker,
            "analysis_date": zscore_result.calculation_timestamp,
            
            # Z-Score analysis
            "z_score": zscore_result.z_score,
            "risk_category": zscore_result.risk_category,
            "model_used": zscore_result.model_used,            "data_quality_score": zscore_result.data_quality_score,
            "component_values": zscore_result.component_values,
            "warnings": zscore_result.warnings,
            
            # Market analysis (if available)
            "has_market_analysis": market_analysis is not None
        }
        
        if market_analysis:
            rec = market_analysis.risk_return_profile if market_analysis.risk_return_profile else None
            tech = market_analysis.technical_analysis
            val = market_analysis.valuation_metrics
            perf = market_analysis.market_performance
            risk = market_analysis.risk_return_profile
            
            context.update({
                # Investment recommendation
                "investment_action": rec.investment_rating if rec else "N/A",
                "investment_confidence": rec.confidence_level if rec else 0.0,
                "overall_risk_category": rec.overall_risk_category if rec else "unknown",
                "key_risks": rec.key_risks if rec else [],
                "key_opportunities": rec.key_opportunities if rec else [],
                  # Technical analysis
                "rsi": tech.indicators.rsi if tech and tech.indicators and hasattr(tech.indicators, 'rsi') else None,
                "macd_signal": tech.overall_signal if tech else None,
                "momentum_score": tech.momentum_score if tech else None,
                "trend_direction": tech.price_trend if tech else None,
                  # Valuation metrics
                "current_price": tech.current_price if tech else None,
                "market_cap": val.market_cap,
                "pe_ratio": val.pe_ratio,
                "pb_ratio": val.pb_ratio,
                "ps_ratio": val.ps_ratio,
                "dividend_yield": val.dividend_yield,
                
                # Performance metrics
                "return_1d": perf.return_1d,
                "return_1m": perf.return_1m,
                "return_3m": perf.return_3m,
                "return_1y": perf.return_1y,
                  # Risk metrics
                "beta": perf.beta if perf else None,
                "volatility_risk": risk.volatility_risk if risk else None, 
                "sharpe_ratio": perf.sharpe_ratio if perf else None,
                "max_drawdown": perf.max_drawdown if perf else None,
                "overall_risk_score": risk.overall_risk_score if risk else None            })
        
        return context
    
    async def _generate_narrative_with_ai(self, context_data: Dict[str, Any]) -> Optional[str]:
        """Generate comprehensive investment narrative using AI."""
        
        prompt = self._create_investment_narrative_prompt(context_data)
        
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.chat_completion(
                ticker=context_data["ticker"],
                messages=messages,
                interaction_type="investment_narrative"
            )
            return response
        except Exception as e:
            logger.error(f"AI narrative generation failed: {str(e)}")
            return None
    
    async def _generate_executive_summary_with_ai(self, context_data: Dict[str, Any]) -> Optional[str]:
        """Generate executive summary using AI."""
        
        prompt = self._create_executive_summary_prompt(context_data)
        
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.chat_completion(
                ticker=context_data["ticker"],
                messages=messages,
                interaction_type="executive_summary"
            )
            return response
        except Exception as e:
            logger.error(f"AI executive summary generation failed: {str(e)}")
            return None
    
    async def _generate_risk_assessment_with_ai(self, context_data: Dict[str, Any]) -> Optional[str]:
        """Generate risk assessment narrative using AI."""
        
        prompt = self._create_risk_assessment_prompt(context_data)
        
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.chat_completion(
                ticker=context_data["ticker"],
                messages=messages,
                interaction_type="risk_assessment"
            )
            return response
        except Exception as e:
            logger.error(f"AI risk assessment generation failed: {str(e)}")
            return None
    
    def _create_investment_narrative_prompt(self, context: Dict[str, Any]) -> str:
        """Create comprehensive investment narrative prompt."""
        
        risk_tone = self._get_risk_appropriate_tone(context["risk_category"])
        
        prompt = f"""# Investment Analysis Narrative for {context['ticker']}

You are an expert financial analyst generating a comprehensive investment narrative. Analyze the provided data and create a professional, well-structured investment analysis.

## Company Data:
- Ticker: {context['ticker']}
- Analysis Date: {context['analysis_date']}

## Fundamental Analysis (Altman Z-Score):
- Z-Score: {context['z_score']:.2f}
- Risk Category: {context['risk_category']}
- Model Used: {context['model_used']}
- Data Quality: {context['data_quality_score']:.1f}%

## Component Breakdown:
{self._format_components(context['component_values'])}

{self._add_market_analysis_section(context) if context['has_market_analysis'] else ''}

## Analysis Requirements:

1. **Tone**: Use {risk_tone} tone appropriate for {context['risk_category']} risk category
2. **Structure**: Provide clear sections for fundamental health, market position, and investment outlook
3. **Integration**: Combine Z-Score insights with market analysis for comprehensive view
4. **Actionable**: Include specific investment implications and key factors to monitor

## Output Format:
Generate a professional investment narrative (500-800 words) with:

1. **Executive Summary** (2-3 sentences)
2. **Fundamental Health Assessment** (Z-Score analysis)
3. **Market Position & Valuation** (if market data available)
4. **Investment Outlook & Recommendations**
5. **Key Risks & Monitoring Points**

Focus on actionable insights that help investors make informed decisions. Be specific about the investment implications of the Z-Score and market analysis findings."""

        return prompt
    
    def _create_executive_summary_prompt(self, context: Dict[str, Any]) -> str:
        """Create executive summary prompt."""
        
        prompt = f"""# Executive Summary for {context['ticker']}

Generate a concise executive summary (150-200 words) for investment decision-makers.

## Key Data:
- Z-Score: {context['z_score']:.2f} ({context['risk_category']})
{f"- Investment Recommendation: {context['investment_action']} (Confidence: {context['investment_confidence']*100:.0f}%)" if context['has_market_analysis'] and context.get('investment_confidence') else ''}
{f"- Current Price: ${context['current_price']:.2f}" if context.get('current_price') else ''}
{f"- 1Y Return: {context['return_1y']*100:.1f}%" if context.get('return_1y') else ''}

## Requirements:
1. **Clear Investment Thesis**: State the primary investment case in 1-2 sentences
2. **Key Metrics**: Highlight the most important financial and market metrics
3. **Risk Assessment**: Summarize key risks and opportunities
4. **Action Items**: Provide clear next steps for investors

Keep it concise, factual, and actionable for busy executives."""

        return prompt
    
    def _create_risk_assessment_prompt(self, context: Dict[str, Any]) -> str:
        """Create risk assessment prompt."""
        
        prompt = f"""# Risk Assessment for {context['ticker']}

Generate a focused risk assessment narrative (300-400 words) analyzing investment risks.

## Risk Context:
- Z-Score Risk Category: {context['risk_category']}
- Financial Health Score: {context['z_score']:.2f}
{f"- Market Volatility: {context['volatility_risk']*100:.1f}%" if context.get('volatility_risk') else ''}
{f"- Beta: {context['beta']:.2f}" if context.get('beta') else ''}

## Analysis Focus:
1. **Fundamental Risks**: Based on Z-Score and component analysis
2. **Market Risks**: Volatility, correlation, and systematic risks
3. **Operational Risks**: Business model and industry factors
4. **Risk Mitigation**: Factors that could improve the risk profile

Provide specific, actionable risk insights for portfolio management."""

        return prompt
    
    def _get_risk_appropriate_tone(self, risk_category: str) -> str:
        """Get appropriate tone based on risk category."""
        tone_map = {
            "Safe": "optimistic and growth-focused",
            "Grey": "balanced and measured", 
            "Distress": "cautionary and urgent"
        }
        return tone_map.get(risk_category, "balanced")
    
    def _format_components(self, components: Dict[str, Any]) -> str:
        """Format component values for display."""
        formatted = []
        for component, value in components.items():
            if isinstance(value, (int, float)):
                formatted.append(f"- {component}: {value:.3f}")
            else:
                formatted.append(f"- {component}: {value}")
        return "\n".join(formatted)
    
    def _add_market_analysis_section(self, context: Dict[str, Any]) -> str:
        """Add market analysis section to prompt if available."""
        if not context['has_market_analysis']:
            return ""        
        section = f"""
## Market Analysis:
{f"- Investment Recommendation: {context['investment_action']} (Confidence: {context['investment_confidence']*100:.0f}%)" if context.get('investment_confidence') else ''}
{f"- Current Price: ${context['current_price']:.2f}" if context.get('current_price') else ''}
{f"- Market Cap: ${context['market_cap']/1e9:.1f}B" if context.get('market_cap') else ''}
{f"- P/E Ratio: {context['pe_ratio']:.1f}" if context.get('pe_ratio') else ''}
{f"- 1Y Return: {context['return_1y']*100:.1f}%" if context.get('return_1y') else ''}
{f"- Volatility: {context['volatility_risk']*100:.1f}%" if context.get('volatility_risk') else ''}
{f"- RSI: {context['rsi']:.1f}" if context.get('rsi') else ''}
{f"- Technical Trend: {context['trend_direction']}" if context.get('trend_direction') else ''}
"""
        return section
