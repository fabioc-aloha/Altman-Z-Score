"""
AI Peer Analyzer - Intelligent peer company comparison and benchmarking

This module uses LLM-powered analysis to identify relevant peer companies
and provide intelligent comparative analysis for investment decisions.

Key Features:
- LLM-based peer company identification
- Comparative Z-Score analysis
- Industry positioning assessment
- Relative investment attractiveness scoring
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
class PeerCompanyProfile:
    """Profile of a peer company for comparison."""
    ticker: str
    company_name: str
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    similarity_score: float = 0.0
    reasoning: str = ""


@dataclass
class PeerAnalysisResult:
    """Results of peer company analysis."""
    target_ticker: str
    identified_peers: List[PeerCompanyProfile]
    peer_z_scores: Dict[str, float]
    industry_average_z_score: float
    relative_position: str  # 'above_average', 'average', 'below_average'
    investment_implication: str
    confidence: float
    analysis_timestamp: datetime


class AIPeerAnalyzer:
    """
    AI-powered peer company analysis and benchmarking.
    
    Uses LLM analysis to identify relevant peers and provide
    comparative investment insights.
    """
    
    def __init__(self):
        """Initialize the AI peer analyzer."""
        self.llm_client = LLMClient()
        logger.info("AI Peer Analyzer initialized")
    
    async def analyze_peers(self, financial_data: MergedFinancialData) -> PeerAnalysisResult:
        """
        Perform comprehensive peer analysis for a company.
        
        Args:
            financial_data: Target company's financial data
            
        Returns:
            PeerAnalysisResult: Complete peer analysis results
            
        Raises:
            AIAnalysisError: If peer analysis fails
        """
        try:
            logger.info(f"Starting AI peer analysis for {financial_data.ticker}")
            
            # Step 1: Identify peer companies using LLM
            peer_companies = await self._identify_peer_companies(financial_data)
            
            # Step 2: Get basic peer profiles (simulated for now)
            peer_profiles = await self._get_peer_profiles(peer_companies, financial_data)
            
            # Step 3: Calculate comparative metrics (simulated Z-scores for demonstration)
            peer_z_scores = await self._calculate_peer_z_scores(peer_profiles)
            
            # Step 4: Perform relative positioning analysis
            relative_analysis = await self._analyze_relative_position(
                financial_data.ticker, peer_z_scores, financial_data
            )
            
            result = PeerAnalysisResult(
                target_ticker=financial_data.ticker,
                identified_peers=peer_profiles,
                peer_z_scores=peer_z_scores,
                industry_average_z_score=relative_analysis['industry_average'],
                relative_position=relative_analysis['position'],
                investment_implication=relative_analysis['implication'],
                confidence=relative_analysis['confidence'],
                analysis_timestamp=datetime.now()
            )
            
            logger.info(f"Peer analysis complete for {financial_data.ticker}: "
                       f"identified {len(peer_profiles)} peers, "
                       f"relative position: {result.relative_position}")
            
            return result
            
        except Exception as e:
            error_msg = f"Peer analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    async def _identify_peer_companies(self, financial_data: MergedFinancialData) -> List[str]:
        """
        Use LLM to identify relevant peer companies.
        
        Args:
            financial_data: Target company financial data
            
        Returns:
            List of peer company tickers
        """
        # Extract comprehensive financial data
        total_assets = None
        revenue = None
        sector = None
        industry = None
        current_ratio = None
        debt_to_equity = None
        gross_margin = None
        operating_margin = None
        
        if financial_data.raw_fmp_data and 'balance_sheet' in financial_data.raw_fmp_data:
            bs_data = financial_data.raw_fmp_data['balance_sheet']
            total_assets = bs_data.get('totalAssets')
            if isinstance(bs_data, list) and len(bs_data) > 0:
                bs_latest = bs_data[0]
                total_assets = bs_latest.get('totalAssets')
        
        if financial_data.raw_fmp_data and 'income_statement' in financial_data.raw_fmp_data:
            is_data = financial_data.raw_fmp_data['income_statement']
            if isinstance(is_data, list) and len(is_data) > 0:
                is_latest = is_data[0]
                revenue = is_latest.get('revenue')
                gross_profit = is_latest.get('grossProfit')
                operating_income = is_latest.get('operatingIncome')
                if revenue and gross_profit:
                    gross_margin = (gross_profit / revenue) * 100
                if revenue and operating_income:
                    operating_margin = (operating_income / revenue) * 100
            elif isinstance(is_data, dict):
                revenue = is_data.get('revenue')
                
        if financial_data.raw_fmp_data and 'profile' in financial_data.raw_fmp_data:
            profiles = financial_data.raw_fmp_data['profile']
            if profiles and len(profiles) > 0:
                profile = profiles[0] if isinstance(profiles, list) else profiles
                sector = profile.get('sector', 'Unknown')
                industry = profile.get('industry', 'Unknown')
        
        # Get additional ratios if available
        current_ratio = financial_data.current_ratio
        debt_to_equity = financial_data.debt_to_equity
        
        # Load prompt template from file
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_peer_identification.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            # Fallback to a simple prompt
            prompt_template = """As a financial analyst, identify 5-7 publicly traded peer companies for {ticker}.
            
Company Profile: {ticker}
Market Cap: {market_cap}
Sector: {sector}
Industry: {industry}

Provide ticker symbols with brief explanations."""

        # Format values for display
        total_assets_str = f"${total_assets:,.0f}" if total_assets is not None else 'N/A'
        revenue_str = f"${revenue:,.0f}" if revenue is not None else 'N/A'
        market_cap_str = f"${financial_data.market_cap:,.0f}" if financial_data.market_cap is not None else 'N/A'
        current_ratio_str = f'{current_ratio:.2f}' if current_ratio else 'N/A'
        debt_to_equity_str = f'{debt_to_equity:.2f}' if debt_to_equity else 'N/A'
        gross_margin_str = f'{gross_margin:.1f}%' if gross_margin else 'N/A'
        operating_margin_str = f'{operating_margin:.1f}%' if operating_margin else 'N/A'
        
        # Format the prompt with actual data
        prompt = prompt_template.format(
            ticker=financial_data.ticker,
            total_assets=total_assets_str,
            revenue=revenue_str,
            market_cap=market_cap_str,
            sector=sector or 'Unknown',
            industry=industry or 'Unknown',
            current_ratio=current_ratio_str,
            debt_to_equity=debt_to_equity_str,
            gross_margin=gross_margin_str,
            operating_margin=operating_margin_str
        )
        
        try:
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                financial_data.ticker,
                messages,
                "peer_identification"
            )
            
            # Parse ticker symbols from response
            peer_tickers = []
            for line in response.split('\n'):
                line = line.strip()
                if ':' in line and len(line) > 0:
                    ticker = line.split(':')[0].strip()
                    if ticker and len(ticker) <= 6:  # Reasonable ticker length
                        peer_tickers.append(ticker)
            
            logger.info(f"LLM identified {len(peer_tickers)} peer companies for {financial_data.ticker}")
            return peer_tickers[:7]  # Limit to 7 peers max
            
        except Exception as e:
            logger.warning(f"LLM peer identification failed for {financial_data.ticker}: {str(e)}")
            # Fallback to default peers (this would be enhanced with industry lookup)
            return ["SPY", "QQQ", "IWM"]  # Market benchmarks as fallback
    
    async def _get_peer_profiles(self, peer_tickers: List[str], 
                                target_data: MergedFinancialData) -> List[PeerCompanyProfile]:
        """
        Get basic profiles for identified peer companies.
        
        Args:
            peer_tickers: List of peer company tickers
            target_data: Target company data for comparison
            
        Returns:
            List of peer company profiles
        """
        profiles = []
        
        for ticker in peer_tickers:
            # In a full implementation, this would fetch real data
            # For now, we'll create simulated profiles
            profile = PeerCompanyProfile(
                ticker=ticker,
                company_name=f"{ticker} Corp",  # Would be fetched from data source
                similarity_score=0.85,  # Would be calculated based on actual metrics
                reasoning=f"Selected as peer for {target_data.ticker} based on industry alignment"
            )
            profiles.append(profile)
        
        return profiles
    
    async def _calculate_peer_z_scores(self, peer_profiles: List[PeerCompanyProfile]) -> Dict[str, float]:
        """
        Calculate Z-scores for peer companies (simulated for demonstration).
        
        Args:
            peer_profiles: List of peer company profiles
            
        Returns:
            Dictionary mapping ticker to Z-score
        """
        # In a full implementation, this would:
        # 1. Fetch financial data for each peer
        # 2. Calculate actual Z-scores using the same methodology
        # 3. Handle missing data and calculation errors
        
        peer_z_scores = {}
        for profile in peer_profiles:
            # Simulated Z-scores for demonstration
            # In reality, these would be calculated from actual financial data
            import random
            random.seed(hash(profile.ticker))  # Consistent "random" values
            peer_z_scores[profile.ticker] = random.uniform(0.5, 4.0)
        
        return peer_z_scores
    
    async def _analyze_relative_position(self, target_ticker: str, 
                                       peer_z_scores: Dict[str, float],
                                       financial_data: MergedFinancialData) -> Dict[str, Any]:
        """
        Analyze target company's position relative to peers.
        
        Args:
            target_ticker: Target company ticker
            peer_z_scores: Z-scores of peer companies
            financial_data: Target company financial data
            
        Returns:
            Relative position analysis
        """
        if not peer_z_scores:
            return {
                'industry_average': 2.0,
                'position': 'unknown',
                'implication': 'Insufficient peer data for comparison',
                'confidence': 0.3
            }
        
        # Calculate industry metrics
        industry_average = sum(peer_z_scores.values()) / len(peer_z_scores)
        
        # Simulate target Z-score (in reality, this would come from actual calculation)
        import random
        random.seed(hash(target_ticker))
        target_z_score = random.uniform(1.0, 3.5)
        
        # Determine relative position
        if target_z_score > industry_average * 1.2:
            position = 'above_average'
            implication = f'{target_ticker} shows stronger financial health than industry peers'
        elif target_z_score < industry_average * 0.8:
            position = 'below_average'
            implication = f'{target_ticker} shows weaker financial health relative to peers'
        else:
            position = 'average'
            implication = f'{target_ticker} demonstrates typical financial health for the industry'
        
        # Generate LLM-powered investment implication
        enhanced_implication = await self._generate_investment_implication(
            target_ticker, target_z_score, industry_average, position
        )
        
        return {
            'industry_average': industry_average,
            'position': position,
            'implication': enhanced_implication or implication,
            'confidence': 0.75  # Moderate confidence for simulated analysis
        }
    
    async def _generate_investment_implication(self, ticker: str, target_z_score: float,
                                             industry_average: float, position: str) -> Optional[str]:
        """
        Generate LLM-powered investment implications from peer analysis.
        
        Args:
            ticker: Target company ticker
            target_z_score: Company's Z-score
            industry_average: Industry average Z-score
            position: Relative position (above/below/average)
            
        Returns:
            Investment implication narrative
        """
        # Load prompt template from file
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_peer_investment_analysis.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            # Fallback to a simple prompt
            prompt_template = """As a financial analyst, provide investment implications for {ticker} based on peer comparison:
            
Peer Analysis Results:
- {ticker} Z-Score: {target_z_score}
- Industry Average Z-Score: {industry_average}
- Relative Position: {position}

Provide brief investment implications and key considerations."""

        # Calculate additional metrics for the prompt
        z_score_gap = ((target_z_score - industry_average) / industry_average * 100) if industry_average != 0 else 0
        sector_strength = 'strength' if industry_average > 2.5 else 'weakness' if industry_average < 1.8 else 'mixed conditions'
        performance_vs_peers = 'outperformance' if target_z_score > industry_average else 'underperformance' if target_z_score < industry_average else 'alignment'
        
        # Format the prompt with actual data
        prompt = prompt_template.format(
            ticker=ticker,
            target_z_score=f"{target_z_score:.2f}",
            industry_average=f"{industry_average:.2f}",
            position=position.replace('_', ' ').title(),
            z_score_gap=f"{z_score_gap:+.1f}",
            sector_strength=sector_strength,
            performance_vs_peers=performance_vs_peers
        )
        
        try:
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                ticker,
                messages,
                "investment_implication"
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate investment implication for {ticker}: {str(e)}")
            return None
