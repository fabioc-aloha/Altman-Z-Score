"""
AI Analysis Orchestrator - Simplified Direct LLM Approach

REDESIGNED APPROACH: Generate AI Final Commentary directly from comprehensive
raw data (Z-Score, market, financial) without intermediate AI component analysis.

This simplifies the pipeline to focus exclusively on LLM-powered investment
analysis using comprehensive, multi-quarter financial and market data.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError
from ...models.data_models import MergedFinancialData
from ..data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


@dataclass
class ComprehensiveAIAnalysis:
    """Simplified AI analysis results focused on direct LLM commentary."""
    ticker: str
    analysis_timestamp: datetime
    
    # Simplified metrics
    overall_ai_confidence: float = 0.85  # High confidence for direct LLM analysis
    ai_recommendations: List[str] = None
    
    # Dashboard Integration Data (simplified)
    dashboard_summary: Optional[Dict[str, Any]] = None
    
    # Primary output: LLM Final Commentary
    llm_final_commentary: Optional[str] = None


class AIAnalysisOrchestrator:
    """
    Simplified AI Analysis Orchestrator for direct LLM commentary generation.
    
    REDESIGNED APPROACH: Skip all intermediate AI component analysis and generate
    final commentary directly from comprehensive raw data sources.
    
    OPTIMIZATION NOTE: Model selection optimization implemented in main pipeline
    to reduce Azure OpenAI calls from 8 per-quarter calls to 1 call per ticker.
    """
    
    def __init__(self):
        """Initialize the simplified AI analysis orchestrator."""
        self.llm_client = LLMClient()
        logger.info("Simplified AI Analysis Orchestrator initialized - direct LLM approach")
    
    async def perform_comprehensive_analysis(self, 
                                           financial_data: MergedFinancialData,
                                           zscore_results: Optional[List] = None,
                                           market_analysis = None) -> ComprehensiveAIAnalysis:
        """
        Perform simplified AI analysis focused on direct LLM commentary generation.
        
        SIMPLIFIED APPROACH: Skip all intermediate AI component analysis and generate
        final commentary directly from comprehensive raw data sources.
        
        Args:
            financial_data: Merged financial data to analyze
            zscore_results: Multi-quarter Z-Score calculations (for final commentary)
            market_analysis: Technical analysis, valuation metrics (for final commentary)
            
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
                ai_recommendations=[]
            )
            
            # Generate simplified dashboard summary
            analysis_results.dashboard_summary = self._generate_simplified_dashboard_summary(analysis_results)
            
            # Generate LLM final commentary directly from comprehensive raw data
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
                z_score = getattr(result, 'z_score', None)
                z_score_display = f"{z_score:.2f}" if z_score is not None else "N/A"
                data_sections.append(f"  - Z-Score: {z_score_display}")
                data_sections.append(f"  - Risk Category: {getattr(result, 'risk_category', 'Unknown')}")
                
                # Component values breakdown
                if hasattr(result, 'component_values') and result.component_values:
                    cv = result.component_values
                    wcr = getattr(cv, 'working_capital_ratio', None)
                    rer = getattr(cv, 'retained_earnings_ratio', None)
                    ebitr = getattr(cv, 'ebit_ratio', None)
                    mvr = getattr(cv, 'market_value_ratio', None)
                    at = getattr(cv, 'asset_turnover', None)
                    
                    wcr_display = f"{wcr:.3f}" if wcr is not None else "N/A"
                    rer_display = f"{rer:.3f}" if rer is not None else "N/A"
                    ebitr_display = f"{ebitr:.3f}" if ebitr is not None else "N/A"
                    mvr_display = f"{mvr:.3f}" if mvr is not None else "N/A"
                    at_display = f"{at:.3f}" if at is not None else "N/A"
                    
                    data_sections.append(f"  - Working Capital/Total Assets: {wcr_display}")
                    data_sections.append(f"  - Retained Earnings/Total Assets: {rer_display}")
                    data_sections.append(f"  - EBIT/Total Assets: {ebitr_display}")
                    data_sections.append(f"  - Market Value Equity/Book Value Debt: {mvr_display}")
                    data_sections.append(f"  - Sales/Total Assets: {at_display}")
                
                # Financial data for this period
                if hasattr(result, 'revenue') and result.revenue:
                    data_sections.append(f"  - Revenue: ${result.revenue:,.0f}")
                if hasattr(result, 'total_assets') and result.total_assets:
                    data_sections.append(f"  - Total Assets: ${result.total_assets:,.0f}")
                if hasattr(result, 'working_capital') and result.working_capital:
                    data_sections.append(f"  - Working Capital: ${result.working_capital:,.0f}")
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
                
                week_52_low = getattr(tech, 'week_52_low', None) or 0
                week_52_high = getattr(tech, 'week_52_high', None) or 0
                rsi = getattr(tech, 'rsi', None) or 0
                sma_50 = getattr(tech, 'sma_50', None) or 0
                sma_200 = getattr(tech, 'sma_200', None) or 0
                avg_volume = getattr(tech, 'avg_volume', None) or 0
                
                data_sections.append(f"  - 52-Week Range: ${week_52_low:.2f} - ${week_52_high:.2f}")
                data_sections.append(f"  - RSI (14-day): {rsi:.1f}")
                data_sections.append(f"  - 50-Day Moving Average: ${sma_50:.2f}")
                data_sections.append(f"  - 200-Day Moving Average: ${sma_200:.2f}")
                data_sections.append(f"  - Average Volume: {avg_volume:,.0f}")
            
            # Valuation Metrics
            if hasattr(market_analysis, 'valuation_metrics') and market_analysis.valuation_metrics:
                val = market_analysis.valuation_metrics
                data_sections.append("Valuation Metrics:")
                
                pe_ratio = getattr(val, 'pe_ratio', None) or 0
                price_to_book = getattr(val, 'price_to_book', None) or 0
                ev_ebitda = getattr(val, 'ev_ebitda', None) or 0
                price_to_sales = getattr(val, 'price_to_sales', None) or 0
                dividend_yield = getattr(val, 'dividend_yield', None) or 0
                
                data_sections.append(f"  - P/E Ratio: {pe_ratio:.2f}")
                data_sections.append(f"  - Price/Book Ratio: {price_to_book:.2f}")
                data_sections.append(f"  - EV/EBITDA: {ev_ebitda:.2f}")
                data_sections.append(f"  - Price/Sales: {price_to_sales:.2f}")
                data_sections.append(f"  - Dividend Yield: {dividend_yield:.2%}")
            
            # Risk-Return Profile
            if hasattr(market_analysis, 'risk_return_profile') and market_analysis.risk_return_profile:
                risk = market_analysis.risk_return_profile
                data_sections.append("Risk-Return Profile:")
                
                beta = getattr(risk, 'beta', None) or 0
                volatility_30d = getattr(risk, 'volatility_30d', None) or 0
                sharpe_ratio = getattr(risk, 'sharpe_ratio', None) or 0
                max_drawdown = getattr(risk, 'max_drawdown', None) or 0
                
                data_sections.append(f"  - Beta: {beta:.2f}")
                data_sections.append(f"  - Volatility (30-day): {volatility_30d:.2%}")
                data_sections.append(f"  - Sharpe Ratio: {sharpe_ratio:.2f}")
                data_sections.append(f"  - Max Drawdown: {max_drawdown:.2%}")
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
            if financial_data.current_ratio is not None:
                data_sections.append(f"  - Current Ratio: {financial_data.current_ratio:.2f}")
            if financial_data.debt_to_equity is not None:
                data_sections.append(f"  - Debt-to-Equity: {financial_data.debt_to_equity:.2f}")
            if financial_data.working_capital_ratio is not None:
                data_sections.append(f"  - Working Capital Ratio: {financial_data.working_capital_ratio:.3f}")
            if financial_data.retained_earnings_ratio is not None:
                data_sections.append(f"  - Retained Earnings Ratio: {financial_data.retained_earnings_ratio:.3f}")
            if financial_data.ebit_ratio is not None:
                data_sections.append(f"  - EBIT Ratio: {financial_data.ebit_ratio:.3f}")
            if financial_data.asset_turnover is not None:
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
