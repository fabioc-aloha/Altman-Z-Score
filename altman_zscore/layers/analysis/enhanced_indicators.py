"""
Enhanced Financial Indicators - Advanced Analytics Layer

This module calculates advanced financial health indicators that go beyond
the basic Altman Z-Score to provide deeper insights into:
- Cash flow quality
- Earnings quality  
- Capital allocation efficiency
- Management effectiveness
- Competitive positioning

These indicators are designed to work with existing data structures
and provide additional context for AI-powered analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from ...common.logging_config import get_logger
from ...models.data_models import MergedFinancialData

logger = get_logger(__name__)


@dataclass
class CashFlowQualityMetrics:
    """Advanced cash flow quality indicators."""
    free_cash_flow_yield: Optional[float] = None
    cash_flow_to_debt_ratio: Optional[float] = None
    cash_conversion_efficiency: Optional[float] = None
    working_capital_velocity: Optional[float] = None
    operating_cash_flow_ratio: Optional[float] = None
    capex_intensity: Optional[float] = None
    fcf_to_revenue_ratio: Optional[float] = None


@dataclass
class EarningsQualityMetrics:
    """Earnings quality and sustainability indicators."""
    accruals_ratio: Optional[float] = None
    earnings_persistence_score: Optional[float] = None
    revenue_quality_score: Optional[float] = None
    margin_stability_score: Optional[float] = None
    earnings_smoothness: Optional[float] = None
    quality_of_earnings_score: Optional[float] = None


@dataclass
class CapitalAllocationMetrics:
    """Capital allocation efficiency indicators."""
    roic: Optional[float] = None  # Return on Invested Capital
    capital_intensity_ratio: Optional[float] = None
    asset_quality_score: Optional[float] = None
    rd_efficiency: Optional[float] = None
    capex_efficiency: Optional[float] = None
    reinvestment_rate: Optional[float] = None


@dataclass
class CompetitivePositioningMetrics:
    """Competitive positioning and market dynamics."""
    gross_margin_vs_peers: Optional[float] = None
    asset_turnover_vs_peers: Optional[float] = None
    roa_vs_peers: Optional[float] = None
    pricing_power_indicator: Optional[float] = None
    market_share_stability: Optional[float] = None
    competitive_moat_score: Optional[float] = None


@dataclass
class EnhancedFinancialIndicators:
    """Comprehensive enhanced financial indicators."""
    ticker: str
    analysis_date: str
    cash_flow_quality: CashFlowQualityMetrics
    earnings_quality: EarningsQualityMetrics
    capital_allocation: CapitalAllocationMetrics
    competitive_positioning: CompetitivePositioningMetrics
    overall_quality_score: Optional[float] = None
    risk_adjusted_score: Optional[float] = None
    warnings: List[str] = None


class EnhancedIndicatorsCalculator:
    """
    Calculator for advanced financial health indicators.
    
    Provides deeper insights beyond basic Z-Score components by analyzing:
    - Cash flow quality and sustainability
    - Earnings quality and persistence
    - Capital allocation efficiency
    - Competitive positioning strength
    """
    
    def __init__(self):
        """Initialize the enhanced indicators calculator."""
        self.logger = get_logger(self.__class__.__name__)
    
    def calculate_all_indicators(
        self, 
        financial_data: MergedFinancialData,
        quarterly_data: Optional[List[Dict]] = None
    ) -> EnhancedFinancialIndicators:
        """
        Calculate comprehensive enhanced financial indicators.
        
        Args:
            financial_data: Latest financial data
            quarterly_data: Historical quarterly data for trend analysis
            
        Returns:
            Enhanced financial indicators with quality scores
        """
        try:
            # Calculate each category of indicators
            cash_flow_quality = self._calculate_cash_flow_quality(financial_data)
            earnings_quality = self._calculate_earnings_quality(financial_data, quarterly_data)
            capital_allocation = self._calculate_capital_allocation(financial_data)
            competitive_positioning = self._calculate_competitive_positioning(financial_data)
            
            # Calculate overall scores
            overall_quality_score = self._calculate_overall_quality_score(
                cash_flow_quality, earnings_quality, capital_allocation, competitive_positioning
            )
            
            risk_adjusted_score = self._calculate_risk_adjusted_score(
                overall_quality_score, financial_data
            )
            
            return EnhancedFinancialIndicators(
                ticker=financial_data.ticker,
                analysis_date=financial_data.timestamp,
                cash_flow_quality=cash_flow_quality,
                earnings_quality=earnings_quality,
                capital_allocation=capital_allocation,
                competitive_positioning=competitive_positioning,
                overall_quality_score=overall_quality_score,
                risk_adjusted_score=risk_adjusted_score,
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate enhanced indicators for {financial_data.ticker}: {str(e)}")
            return self._create_default_indicators(financial_data.ticker, financial_data.timestamp)
    
    def _calculate_cash_flow_quality(self, data: MergedFinancialData) -> CashFlowQualityMetrics:
        """Calculate cash flow quality metrics."""
        try:
            raw_data = data.raw_fmp_data or {}
            ratios = raw_data.get('ratios', {})
            income_stmt = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            
            # Free Cash Flow Yield = FCF / Enterprise Value
            fcf_per_share = ratios.get('freeCashFlowPerShare', 0)
            shares_outstanding = data.shares_outstanding or 1
            free_cash_flow = fcf_per_share * shares_outstanding if fcf_per_share else None
            enterprise_value = ratios.get('enterpriseValueMultiple', 0) * income_stmt.get('ebitda', 0)
            
            free_cash_flow_yield = None
            if free_cash_flow and enterprise_value and enterprise_value > 0:
                free_cash_flow_yield = free_cash_flow / enterprise_value
            
            # Cash Flow to Debt Ratio
            cash_flow_to_debt_ratio = ratios.get('cashFlowToDebtRatio')
            
            # Cash Conversion Efficiency (approximation)
            net_income = income_stmt.get('netIncome', 0)
            operating_cash_flow = ratios.get('operatingCashFlowPerShare', 0) * shares_outstanding if ratios.get('operatingCashFlowPerShare') else 0
            cash_conversion_efficiency = None
            if net_income and net_income > 0:
                cash_conversion_efficiency = operating_cash_flow / net_income
            
            # Working Capital Velocity
            revenue = income_stmt.get('revenue', 0)
            current_assets = balance_sheet.get('totalCurrentAssets', 0)
            current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
            working_capital = current_assets - current_liabilities
            working_capital_velocity = None
            if working_capital and working_capital > 0:
                working_capital_velocity = revenue / working_capital
            
            # Operating Cash Flow Ratio
            operating_cash_flow_ratio = ratios.get('operatingCashFlowSalesRatio')
            
            # CapEx Intensity
            revenue = income_stmt.get('revenue', 0)
            # Estimate CapEx from depreciation (rough approximation)
            depreciation = income_stmt.get('depreciationAndAmortization', 0)
            capex_intensity = None
            if revenue and revenue > 0 and depreciation:
                capex_intensity = depreciation / revenue  # Rough proxy
            
            # FCF to Revenue Ratio
            fcf_to_revenue_ratio = None
            if free_cash_flow and revenue and revenue > 0:
                fcf_to_revenue_ratio = free_cash_flow / revenue
            
            return CashFlowQualityMetrics(
                free_cash_flow_yield=free_cash_flow_yield,
                cash_flow_to_debt_ratio=cash_flow_to_debt_ratio,
                cash_conversion_efficiency=cash_conversion_efficiency,
                working_capital_velocity=working_capital_velocity,
                operating_cash_flow_ratio=operating_cash_flow_ratio,
                capex_intensity=capex_intensity,
                fcf_to_revenue_ratio=fcf_to_revenue_ratio
            )
            
        except Exception as e:
            self.logger.warning(f"Error calculating cash flow quality metrics: {str(e)}")
            return CashFlowQualityMetrics()
    
    def _calculate_earnings_quality(
        self, 
        data: MergedFinancialData, 
        quarterly_data: Optional[List[Dict]] = None
    ) -> EarningsQualityMetrics:
        """Calculate earnings quality and sustainability metrics."""
        try:
            raw_data = data.raw_fmp_data or {}
            ratios = raw_data.get('ratios', {})
            income_stmt = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            
            # Accruals Ratio = (Net Income - Operating Cash Flow) / Total Assets
            net_income = income_stmt.get('netIncome', 0)
            operating_cash_flow = ratios.get('operatingCashFlowPerShare', 0) * (data.shares_outstanding or 1)
            total_assets = balance_sheet.get('totalAssets', 0)
            
            accruals_ratio = None
            if total_assets and total_assets > 0:
                accruals_ratio = (net_income - operating_cash_flow) / total_assets
            
            # Revenue Quality Score (approximation based on recurring nature)
            # Using gross margin stability as proxy
            gross_margin = ratios.get('grossProfitMargin')
            revenue_quality_score = min(gross_margin * 2, 1.0) if gross_margin else None
            
            # Margin Stability Score (requires historical data)
            margin_stability_score = None
            if quarterly_data and len(quarterly_data) >= 4:
                # Calculate coefficient of variation for gross margins over time
                margins = []
                for quarter in quarterly_data[-8:]:  # Last 8 quarters
                    if 'component_values' in quarter:
                        # Approximate gross margin from available data
                        ebit_ratio = quarter['component_values'].get('ebit_ratio', 0)
                        if ebit_ratio:
                            margins.append(ebit_ratio)
                
                if len(margins) >= 4:
                    margin_std = np.std(margins)
                    margin_mean = np.mean(margins)
                    if margin_mean > 0:
                        coefficient_of_variation = margin_std / margin_mean
                        margin_stability_score = max(0, 1 - coefficient_of_variation)
            
            # Earnings Smoothness (coefficient of variation of quarterly earnings)
            earnings_smoothness = None
            if quarterly_data and len(quarterly_data) >= 4:
                # Use Z-Score as proxy for earnings consistency
                z_scores = [q.get('z_score', 0) for q in quarterly_data[-8:]]
                if len(z_scores) >= 4:
                    z_score_std = np.std(z_scores)
                    z_score_mean = np.mean(z_scores)
                    if z_score_mean > 0:
                        earnings_smoothness = max(0, 1 - (z_score_std / z_score_mean) * 0.1)
            
            # Quality of Earnings Score (composite)
            quality_components = []
            if accruals_ratio is not None:
                quality_components.append(max(0, 1 - abs(accruals_ratio) * 5))  # Lower accruals = higher quality
            if revenue_quality_score is not None:
                quality_components.append(revenue_quality_score)
            if margin_stability_score is not None:
                quality_components.append(margin_stability_score)
            if earnings_smoothness is not None:
                quality_components.append(earnings_smoothness)
            
            quality_of_earnings_score = np.mean(quality_components) if quality_components else None
            
            return EarningsQualityMetrics(
                accruals_ratio=accruals_ratio,
                revenue_quality_score=revenue_quality_score,
                margin_stability_score=margin_stability_score,
                earnings_smoothness=earnings_smoothness,
                quality_of_earnings_score=quality_of_earnings_score
            )
            
        except Exception as e:
            self.logger.warning(f"Error calculating earnings quality metrics: {str(e)}")
            return EarningsQualityMetrics()
    
    def _calculate_capital_allocation(self, data: MergedFinancialData) -> CapitalAllocationMetrics:
        """Calculate capital allocation efficiency metrics."""
        try:
            raw_data = data.raw_fmp_data or {}
            ratios = raw_data.get('ratios', {})
            income_stmt = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            
            # Return on Invested Capital (ROIC)
            roic = ratios.get('returnOnCapitalEmployed')  # Close approximation
            
            # Capital Intensity Ratio
            revenue = income_stmt.get('revenue', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            capital_intensity_ratio = None
            if revenue and revenue > 0:
                capital_intensity_ratio = total_assets / revenue
            
            # Asset Quality Score (Tangible Assets / Total Assets)
            intangible_assets = balance_sheet.get('intangibleAssets', 0)
            goodwill = balance_sheet.get('goodwill', 0)
            total_intangibles = intangible_assets + goodwill
            asset_quality_score = None
            if total_assets and total_assets > 0:
                asset_quality_score = max(0, 1 - (total_intangibles / total_assets))
            
            # R&D Efficiency (for tech companies)
            rd_expenses = income_stmt.get('researchAndDevelopmentExpenses', 0)
            rd_efficiency = None
            if rd_expenses and rd_expenses > 0 and revenue and revenue > 0:
                # R&D efficiency = Revenue per R&D dollar
                rd_efficiency = revenue / rd_expenses
            
            # CapEx Efficiency (approximation)
            depreciation = income_stmt.get('depreciationAndAmortization', 0)
            capex_efficiency = None
            if depreciation and depreciation > 0 and revenue and revenue > 0:
                capex_efficiency = revenue / depreciation  # Rough proxy
            
            # Reinvestment Rate
            net_income = income_stmt.get('netIncome', 0)
            reinvestment_rate = None
            if net_income and net_income > 0 and depreciation:
                # Simplified: (CapEx + R&D) / Net Income
                reinvestment = depreciation + rd_expenses  # Approximation
                reinvestment_rate = reinvestment / net_income
            
            return CapitalAllocationMetrics(
                roic=roic,
                capital_intensity_ratio=capital_intensity_ratio,
                asset_quality_score=asset_quality_score,
                rd_efficiency=rd_efficiency,
                capex_efficiency=capex_efficiency,
                reinvestment_rate=reinvestment_rate
            )
            
        except Exception as e:
            self.logger.warning(f"Error calculating capital allocation metrics: {str(e)}")
            return CapitalAllocationMetrics()
    
    def _calculate_competitive_positioning(self, data: MergedFinancialData) -> CompetitivePositioningMetrics:
        """Calculate competitive positioning metrics."""
        try:
            raw_data = data.raw_fmp_data or {}
            ratios = raw_data.get('ratios', {})
            
            # For now, we'll use absolute values as we don't have peer data
            # In future enhancement, these would be relative to industry medians
            
            gross_margin = ratios.get('grossProfitMargin')
            asset_turnover = ratios.get('assetTurnover')
            roa = ratios.get('returnOnAssets')
            
            # Pricing Power Indicator (gross margin as proxy)
            pricing_power_indicator = gross_margin
            
            # Competitive Moat Score (composite of margins, returns, and efficiency)
            moat_components = []
            if gross_margin is not None:
                moat_components.append(min(gross_margin * 2, 1.0))  # Scale to 0-1
            if roa is not None:
                moat_components.append(min(roa * 5, 1.0))  # Scale to 0-1
            if asset_turnover is not None:
                moat_components.append(min(asset_turnover * 2, 1.0))  # Scale to 0-1
            
            competitive_moat_score = np.mean(moat_components) if moat_components else None
            
            return CompetitivePositioningMetrics(
                gross_margin_vs_peers=gross_margin,  # Absolute value for now
                asset_turnover_vs_peers=asset_turnover,  # Absolute value for now
                roa_vs_peers=roa,  # Absolute value for now
                pricing_power_indicator=pricing_power_indicator,
                competitive_moat_score=competitive_moat_score
            )
            
        except Exception as e:
            self.logger.warning(f"Error calculating competitive positioning metrics: {str(e)}")
            return CompetitivePositioningMetrics()
    
    def _calculate_overall_quality_score(
        self,
        cash_flow: CashFlowQualityMetrics,
        earnings: EarningsQualityMetrics,
        capital: CapitalAllocationMetrics,
        competitive: CompetitivePositioningMetrics
    ) -> Optional[float]:
        """Calculate overall financial quality score."""
        try:
            scores = []
            
            # Cash Flow Quality (weight: 30%)
            cf_components = []
            if cash_flow.cash_flow_to_debt_ratio is not None:
                cf_components.append(min(cash_flow.cash_flow_to_debt_ratio / 2, 1.0))
            if cash_flow.operating_cash_flow_ratio is not None:
                cf_components.append(cash_flow.operating_cash_flow_ratio)
            if cash_flow.cash_conversion_efficiency is not None:
                cf_components.append(min(abs(cash_flow.cash_conversion_efficiency), 1.0))
            
            if cf_components:
                scores.append(('cash_flow', np.mean(cf_components), 0.3))
            
            # Earnings Quality (weight: 25%)
            if earnings.quality_of_earnings_score is not None:
                scores.append(('earnings', earnings.quality_of_earnings_score, 0.25))
            
            # Capital Allocation (weight: 25%)
            cap_components = []
            if capital.roic is not None:
                cap_components.append(min(capital.roic * 5, 1.0))
            if capital.asset_quality_score is not None:
                cap_components.append(capital.asset_quality_score)
            if capital.rd_efficiency is not None and capital.rd_efficiency > 0:
                cap_components.append(min(capital.rd_efficiency / 10, 1.0))
            
            if cap_components:
                scores.append(('capital', np.mean(cap_components), 0.25))
            
            # Competitive Positioning (weight: 20%)
            if competitive.competitive_moat_score is not None:
                scores.append(('competitive', competitive.competitive_moat_score, 0.2))
            
            if not scores:
                return None
            
            # Calculate weighted average
            total_weight = sum(weight for _, _, weight in scores)
            weighted_sum = sum(score * weight for _, score, weight in scores)
            
            return weighted_sum / total_weight if total_weight > 0 else None
            
        except Exception as e:
            self.logger.warning(f"Error calculating overall quality score: {str(e)}")
            return None
    
    def _calculate_risk_adjusted_score(
        self, 
        quality_score: Optional[float], 
        data: MergedFinancialData
    ) -> Optional[float]:
        """Calculate risk-adjusted quality score."""
        try:
            if quality_score is None:
                return None
            
            # Risk adjustment factors
            risk_factors = []
            
            raw_data = data.raw_fmp_data or {}
            ratios = raw_data.get('ratios', {})
            
            # Leverage risk
            debt_equity_ratio = ratios.get('debtEquityRatio', 0)
            leverage_risk = max(0, 1 - debt_equity_ratio * 2)  # Lower debt = lower risk
            risk_factors.append(leverage_risk)
            
            # Liquidity risk
            current_ratio = ratios.get('currentRatio', 1)
            liquidity_risk = min(current_ratio / 2, 1.0)  # Higher current ratio = lower risk
            risk_factors.append(liquidity_risk)
            
            # Profitability risk
            net_margin = ratios.get('netProfitMargin', 0)
            profitability_risk = min(net_margin * 10, 1.0) if net_margin > 0 else 0
            risk_factors.append(profitability_risk)
            
            # Calculate risk adjustment
            risk_adjustment = np.mean(risk_factors) if risk_factors else 0.5
            
            return quality_score * risk_adjustment
            
        except Exception as e:
            self.logger.warning(f"Error calculating risk-adjusted score: {str(e)}")
            return quality_score
    
    def _create_default_indicators(self, ticker: str, timestamp: str) -> EnhancedFinancialIndicators:
        """Create default indicators structure when calculation fails."""
        return EnhancedFinancialIndicators(
            ticker=ticker,
            analysis_date=timestamp,
            cash_flow_quality=CashFlowQualityMetrics(),
            earnings_quality=EarningsQualityMetrics(),
            capital_allocation=CapitalAllocationMetrics(),
            competitive_positioning=CompetitivePositioningMetrics(),
            warnings=["Failed to calculate enhanced indicators - using defaults"]
        )


def format_enhanced_indicators_for_llm(indicators: EnhancedFinancialIndicators) -> Dict[str, Any]:
    """
    Format enhanced indicators for LLM injection.
    
    Args:
        indicators: Enhanced financial indicators
        
    Returns:
        Formatted dictionary for LLM prompt injection
    """
    return {
        'ticker': indicators.ticker,
        'analysis_date': indicators.analysis_date,
        'cash_flow_quality': {
            'free_cash_flow_yield': indicators.cash_flow_quality.free_cash_flow_yield,
            'cash_flow_to_debt_ratio': indicators.cash_flow_quality.cash_flow_to_debt_ratio,
            'cash_conversion_efficiency': indicators.cash_flow_quality.cash_conversion_efficiency,
            'working_capital_velocity': indicators.cash_flow_quality.working_capital_velocity,
            'operating_cash_flow_ratio': indicators.cash_flow_quality.operating_cash_flow_ratio,
            'interpretation': 'Higher ratios indicate better cash flow quality and conversion efficiency'
        },
        'earnings_quality': {
            'accruals_ratio': indicators.earnings_quality.accruals_ratio,
            'quality_of_earnings_score': indicators.earnings_quality.quality_of_earnings_score,
            'margin_stability_score': indicators.earnings_quality.margin_stability_score,
            'earnings_smoothness': indicators.earnings_quality.earnings_smoothness,
            'interpretation': 'Lower accruals and higher stability scores indicate higher earnings quality'
        },
        'capital_allocation': {
            'roic': indicators.capital_allocation.roic,
            'asset_quality_score': indicators.capital_allocation.asset_quality_score,
            'rd_efficiency': indicators.capital_allocation.rd_efficiency,
            'reinvestment_rate': indicators.capital_allocation.reinvestment_rate,
            'interpretation': 'Higher ROIC and efficiency ratios indicate better capital allocation'
        },
        'competitive_positioning': {
            'competitive_moat_score': indicators.competitive_positioning.competitive_moat_score,
            'pricing_power_indicator': indicators.competitive_positioning.pricing_power_indicator,
            'interpretation': 'Higher scores indicate stronger competitive positioning and pricing power'
        },
        'overall_scores': {
            'overall_quality_score': indicators.overall_quality_score,
            'risk_adjusted_score': indicators.risk_adjusted_score,
            'interpretation': 'Composite scores ranging from 0-1, higher is better'
        },
        'warnings': indicators.warnings or []
    }
