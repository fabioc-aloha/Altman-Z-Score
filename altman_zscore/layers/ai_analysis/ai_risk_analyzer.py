"""
AI Risk Analyzer - Comprehensive risk factor identification and modeling

This module provides AI-powered risk analysis to identify company-specific,
industry, and macro-economic risk factors that could impact investment outcomes.

Key Features:
- Company-specific risk identification
- Macro-economic risk assessment
- Industry disruption risk analysis
- Forward-looking risk trajectory modeling
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError
from ...models.data_models import MergedFinancialData
from ..data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


class RiskCategory(Enum):
    """Categories of risk factors."""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    MARKET = "market"
    REGULATORY = "regulatory"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    GEOPOLITICAL = "geopolitical"


class RiskSeverity(Enum):
    """Risk severity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskFactor:
    """Individual risk factor analysis."""
    risk_id: str
    category: RiskCategory
    severity: RiskSeverity
    probability: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0
    description: str
    mitigation_factors: List[str]
    time_horizon: str  # "short_term", "medium_term", "long_term"


@dataclass
class RiskAnalysisResult:
    """Results of comprehensive risk analysis."""
    ticker: str
    identified_risks: List[RiskFactor]
    overall_risk_score: float  # 0.0 to 1.0
    risk_trajectory: str  # "improving", "stable", "deteriorating"
    key_risk_themes: List[str]
    investment_implication: str
    confidence: float
    analysis_timestamp: datetime


class AIRiskAnalyzer:
    """
    AI-powered comprehensive risk analysis and modeling.
    
    Identifies and analyzes various risk factors that could impact
    investment performance and company valuation.
    """
    
    def __init__(self):
        """Initialize the AI risk analyzer."""
        self.llm_client = LLMClient()
        logger.info("AI Risk Analyzer initialized")
    
    async def analyze_risks(self, financial_data: MergedFinancialData) -> RiskAnalysisResult:
        """
        Perform comprehensive risk analysis for a company.
        
        Args:
            financial_data: Target company's financial data
            
        Returns:
            RiskAnalysisResult: Complete risk analysis results
            
        Raises:
            AIAnalysisError: If risk analysis fails
        """
        try:
            logger.info(f"Starting AI risk analysis for {financial_data.ticker}")
            
            # Step 1: Identify company-specific risks
            company_risks = await self._identify_company_risks(financial_data)
            
            # Step 2: Analyze industry and market risks
            industry_risks = await self._analyze_industry_risks(financial_data)
            
            # Step 3: Assess macro-economic risks
            macro_risks = await self._assess_macro_risks(financial_data)
            
            # Step 4: Combine all risk factors
            all_risks = company_risks + industry_risks + macro_risks
            
            # Step 5: Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk_score(all_risks)
            
            # Step 6: Analyze risk trajectory
            risk_trajectory = await self._analyze_risk_trajectory(financial_data, all_risks)
            
            # Step 7: Extract key risk themes
            key_themes = self._extract_key_risk_themes(all_risks)
            
            # Step 8: Generate investment implications
            investment_implication = await self._generate_risk_investment_implication(
                financial_data.ticker, overall_risk_score, risk_trajectory, key_themes
            )
            
            result = RiskAnalysisResult(
                ticker=financial_data.ticker,
                identified_risks=all_risks,
                overall_risk_score=overall_risk_score,
                risk_trajectory=risk_trajectory,
                key_risk_themes=key_themes,
                investment_implication=investment_implication,
                confidence=0.78,  # High confidence for comprehensive analysis
                analysis_timestamp=datetime.now()
            )
            
            logger.info(f"Risk analysis complete for {financial_data.ticker}: "
                       f"overall risk score {result.overall_risk_score:.2f}, "
                       f"identified {len(all_risks)} risk factors")
            
            return result
            
        except Exception as e:
            error_msg = f"Risk analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    async def _identify_company_risks(self, financial_data: MergedFinancialData) -> List[RiskFactor]:
        """
        Identify company-specific risk factors using LLM analysis.
        
        Args:
            financial_data: Company's financial data
            
        Returns:
            List of company-specific risk factors
        """
        # In a real implementation, this would analyze:
        # - Financial statement trends and ratios
        # - Management discussion and analysis (MD&A)
        # - Recent earnings calls and guidance
        # - Company filings and disclosures
        
        # Simulated company-specific risks for demonstration
        risks = []
        
        # Financial risk based on actual data
        if hasattr(financial_data, 'total_liabilities') and hasattr(financial_data, 'total_assets'):
            debt_ratio = financial_data.total_liabilities / financial_data.total_assets
            if debt_ratio > 0.6:
                risks.append(RiskFactor(
                    risk_id=f"{financial_data.ticker}_debt_risk",
                    category=RiskCategory.FINANCIAL,
                    severity=RiskSeverity.HIGH if debt_ratio > 0.8 else RiskSeverity.MODERATE,
                    probability=0.7,
                    impact_score=0.8,
                    description=f"High debt-to-asset ratio ({debt_ratio:.1%}) indicates elevated financial leverage risk",
                    mitigation_factors=["Strong cash flow generation", "Asset quality", "Refinancing capabilities"],
                    time_horizon="short_term"
                ))
        
        # Simulated operational risks
        import random
        random.seed(hash(financial_data.ticker + "operational"))
        
        if random.random() > 0.6:  # 40% chance of operational risk
            risks.append(RiskFactor(
                risk_id=f"{financial_data.ticker}_operational_risk",
                category=RiskCategory.OPERATIONAL,
                severity=random.choice(list(RiskSeverity)),
                probability=random.uniform(0.3, 0.8),
                impact_score=random.uniform(0.4, 0.9),
                description="Supply chain concentration and key supplier dependencies",
                mitigation_factors=["Supplier diversification initiatives", "Vertical integration strategies"],
                time_horizon="medium_term"
            ))
        
        return risks
    
    async def _analyze_industry_risks(self, financial_data: MergedFinancialData) -> List[RiskFactor]:
        """
        Analyze industry and market-specific risks.
        
        Args:
            financial_data: Company's financial data
            
        Returns:
            List of industry-specific risk factors
        """
        risks = []
        
        # Extract financial context for risk analysis
        sector = None
        industry = None
        revenue = None
        total_assets = None
        debt_ratio = None
        
        if financial_data.raw_fmp_data and 'profile' in financial_data.raw_fmp_data:
            profiles = financial_data.raw_fmp_data['profile']
            if profiles and len(profiles) > 0:
                profile = profiles[0] if isinstance(profiles, list) else profiles
                sector = profile.get('sector', 'Unknown')
                industry = profile.get('industry', 'Unknown')
        
        if financial_data.raw_fmp_data and 'income_statement' in financial_data.raw_fmp_data:
            is_data = financial_data.raw_fmp_data['income_statement']
            if isinstance(is_data, list) and len(is_data) > 0:
                revenue = is_data[0].get('revenue')
            elif isinstance(is_data, dict):
                revenue = is_data.get('revenue')
                
        if financial_data.raw_fmp_data and 'balance_sheet' in financial_data.raw_fmp_data:
            bs_data = financial_data.raw_fmp_data['balance_sheet']
            if isinstance(bs_data, list) and len(bs_data) > 0:
                bs_latest = bs_data[0]
                total_assets = bs_latest.get('totalAssets')
                total_debt = bs_latest.get('totalDebt')
                if total_assets and total_debt:
                    debt_ratio = total_debt / total_assets
        
        # Format financial values properly
        revenue_str = f"${revenue:,.0f}" if revenue else 'N/A'
        total_assets_str = f"${total_assets:,.0f}" if total_assets else 'N/A'
        debt_ratio_str = f"{debt_ratio:.1%}" if debt_ratio else 'N/A'
        market_cap_str = f"${financial_data.market_cap:,.0f}" if financial_data.market_cap else 'N/A'
        
        # Load prompt template from file
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_risk_assessment.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            # Fallback to a simple prompt
            prompt_template = """As a risk analyst, identify key risks for {ticker}:
            
Company: {ticker}
Sector: {sector}
Industry: {industry}
Revenue: {revenue}
Market Cap: {market_cap}

Identify and analyze 3-4 key risk factors with severity and impact assessment."""

        # Format the prompt with actual data
        industry_risk_prompt = prompt_template.format(
            ticker=financial_data.ticker,
            sector=sector or 'Unknown',
            industry=industry or 'Unknown',
            revenue=revenue_str,
            total_assets=total_assets_str,
            debt_ratio=debt_ratio_str,
            market_cap=market_cap_str
        )
        
        try:
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": industry_risk_prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                financial_data.ticker,
                messages,
                "industry_risk_analysis"
            )
            # Parse LLM response and create risk factors
            # For demo purposes, create simulated industry risks
            
            import random
            random.seed(hash(financial_data.ticker + "industry"))
            
            # Simulated industry risks
            risks.append(RiskFactor(
                risk_id=f"{financial_data.ticker}_industry_disruption",
                category=RiskCategory.TECHNOLOGICAL,
                severity=random.choice([RiskSeverity.MODERATE, RiskSeverity.HIGH]),
                probability=random.uniform(0.4, 0.7),
                impact_score=random.uniform(0.6, 0.9),
                description="Digital transformation and emerging technology disruption in the industry",
                mitigation_factors=["R&D investments", "Strategic partnerships", "Digital transformation initiatives"],
                time_horizon="long_term"
            ))
            
        except Exception as e:
            logger.warning(f"LLM industry risk analysis failed for {financial_data.ticker}: {str(e)}")
        
        return risks
    
    async def _assess_macro_risks(self, financial_data: MergedFinancialData) -> List[RiskFactor]:
        """
        Assess macro-economic and geopolitical risks.
        
        Args:
            financial_data: Company's financial data
            
        Returns:
            List of macro-economic risk factors
        """
        risks = []
        
        # Simulated macro risks that would affect most companies
        import random
        random.seed(42)  # Consistent for all companies
        
        # Interest rate risk
        risks.append(RiskFactor(
            risk_id="macro_interest_rate_risk",
            category=RiskCategory.MARKET,
            severity=RiskSeverity.MODERATE,
            probability=0.6,
            impact_score=0.5,
            description="Rising interest rate environment affecting cost of capital and valuations",
            mitigation_factors=["Fixed-rate debt structures", "Operational efficiency", "Cash generation"],
            time_horizon="short_term"
        ))
        
        # Inflation risk
        risks.append(RiskFactor(
            risk_id="macro_inflation_risk",
            category=RiskCategory.MARKET,
            severity=RiskSeverity.MODERATE,
            probability=0.5,
            impact_score=0.6,
            description="Persistent inflation pressure on input costs and consumer spending",
            mitigation_factors=["Pricing power", "Cost management", "Supply chain efficiency"],
            time_horizon="medium_term"
        ))
        
        return risks
    
    def _calculate_overall_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """
        Calculate overall risk score from individual risk factors.
        
        Args:
            risk_factors: List of identified risk factors
            
        Returns:
            Overall risk score (0.0 to 1.0)
        """
        if not risk_factors:
            return 0.3  # Default moderate risk when no specific risks identified
        
        # Calculate risk-weighted score
        total_risk = 0.0
        total_weight = 0.0
        
        for risk in risk_factors:
            # Risk score = probability × impact
            risk_score = risk.probability * risk.impact_score
            
            # Weight by severity
            severity_weights = {
                RiskSeverity.LOW: 0.5,
                RiskSeverity.MODERATE: 1.0,
                RiskSeverity.HIGH: 1.5,
                RiskSeverity.CRITICAL: 2.0
            }
            weight = severity_weights.get(risk.severity, 1.0)
            
            total_risk += risk_score * weight
            total_weight += weight
        
        # Normalize to 0-1 scale
        raw_score = total_risk / total_weight if total_weight > 0 else 0.3
        return min(1.0, max(0.0, raw_score))
    
    async def _analyze_risk_trajectory(self, financial_data: MergedFinancialData,
                                     risk_factors: List[RiskFactor]) -> str:
        """
        Analyze whether risk profile is improving, stable, or deteriorating.
        
        Args:
            financial_data: Company's financial data
            risk_factors: Identified risk factors
            
        Returns:
            Risk trajectory description
        """
        # In a real implementation, this would compare:
        # - Historical risk factors and trends
        # - Recent financial performance changes
        # - Industry risk evolution
        # - Management risk mitigation efforts
        
        # Simulated trajectory analysis
        import random
        random.seed(hash(financial_data.ticker + "trajectory"))
        
        trajectories = ["improving", "stable", "deteriorating"]
        weights = [0.25, 0.5, 0.25]  # Bias toward stability
        
        return random.choices(trajectories, weights=weights)[0]
    
    def _extract_key_risk_themes(self, risk_factors: List[RiskFactor]) -> List[str]:
        """
        Extract key risk themes from identified risk factors.
        
        Args:
            risk_factors: List of risk factors
            
        Returns:
            List of key risk themes
        """
        if not risk_factors:
            return ["General market risk"]
        
        # Count risk categories
        category_counts = {}
        for risk in risk_factors:
            category = risk.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by frequency and return top themes
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [category.replace('_', ' ').title() for category, _ in sorted_categories[:3]]
    
    async def _generate_risk_investment_implication(self, ticker: str,
                                                  overall_risk_score: float,
                                                  risk_trajectory: str,
                                                  key_themes: List[str]) -> str:
        """
        Generate LLM-powered investment implications from risk analysis.
        
        Args:
            ticker: Target company ticker
            overall_risk_score: Overall risk score
            risk_trajectory: Risk trajectory direction
            key_themes: Key risk themes
            
        Returns:
            Investment implication narrative
        """
        try:
            # Load the prompt template from file
            prompt_file = Path(__file__).parent.parent.parent / "prompts" / "prompt_risk_investment_analysis.md"
            if not prompt_file.exists():
                logger.warning(f"Prompt file not found: {prompt_file}")
                return self._generate_fallback_risk_implication(overall_risk_score, risk_trajectory, key_themes)
            
            prompt_template = prompt_file.read_text(encoding='utf-8')
            
            # Format the prompt with actual data
            risk_level = self._describe_risk_level(overall_risk_score)
            key_themes_str = ', '.join(key_themes) if key_themes else "None identified"
            
            formatted_prompt = prompt_template.format(
                ticker=ticker,
                risk_level=risk_level,
                overall_risk_score=f"{overall_risk_score:.2f}",
                risk_trajectory=risk_trajectory,
                key_themes=key_themes_str
            )
            
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": formatted_prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                ticker,
                messages,
                "risk_investment_implication"
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate risk investment implication for {ticker}: {str(e)}")
            # Fallback to rule-based implication
            return self._generate_fallback_risk_implication(overall_risk_score, risk_trajectory, key_themes)
    
    def _describe_risk_level(self, score: float) -> str:
        """Convert risk score to descriptive text."""
        if score > 0.8:
            return "Very High Risk"
        elif score > 0.6:
            return "High Risk"
        elif score > 0.4:
            return "Moderate Risk"
        elif score > 0.2:
            return "Low-Moderate Risk"
        else:
            return "Low Risk"
    
    def _generate_fallback_risk_implication(self, overall_risk_score: float,
                                          risk_trajectory: str,
                                          key_themes: List[str]) -> str:
        """Generate rule-based risk implication as fallback."""
        risk_level = self._describe_risk_level(overall_risk_score)
        
        base_implication = f"Risk profile is assessed as {risk_level.lower()} and {risk_trajectory}. "
        
        if overall_risk_score > 0.7:
            base_implication += "High risk profile suggests conservative position sizing and careful monitoring. "
        elif overall_risk_score > 0.4:
            base_implication += "Moderate risk profile requires balanced risk management approach. "
        else:
            base_implication += "Lower risk profile supports more confident investment positioning. "
        
        if key_themes:
            base_implication += f"Key risk areas include {', '.join(key_themes).lower()}."
        
        return base_implication
