"""
Core calculation module for Altman Z-Score analysis.

This module contains the calculation logic and model selection for Z-Score analysis,
but is NOT the main entry point. Users should run analyze.py in the root directory.

Key Components:
- Z-Score calculation with multiple model support
- Industry-specific model selection
- Component validation and diagnostics
- Industry comparison functionality
- Tech sector calibrations

Models Supported:
1. Original (1968) - For public manufacturing companies
2. Private Company (1983) - For private manufacturing firms
3. Service Company (1995) - For non-manufacturing/service businesses
4. Emerging Markets - For companies in emerging markets

Tech Industry Calibrations:
- SaaS-specific adjustments
- AI/ML company considerations
- Hardware tech company handling
- Growth stage adaptations

Use analyze.py to run the full analysis pipeline, which will use this module
for calculations after data is fetched and validated.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import pandas as pd
import logging
from .config import ZSCORE_MODELS, ZScoreModel, DEFAULT_ZSCORE_MODEL
from .industry_classifier import (
    CompanyProfile, classify_company, IndustryGroup,
    TechSubsector, determine_company_stage
)
from .models import ModelThresholds
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class FinancialMetrics:
    """Container for financial metrics used in Z-score calculation."""
    current_assets: float
    current_liabilities: float
    total_assets: float
    retained_earnings: float
    ebit: float
    total_liabilities: float
    sales: float
    market_value_equity: float
    date: datetime

    @classmethod
    def from_dict(cls, fin: Dict[str, float], mve: float, date: datetime) -> 'FinancialMetrics':
        """Create FinancialMetrics from a dictionary of financial data."""
        return cls(
            current_assets=fin["CA"],
            current_liabilities=fin["CL"],
            total_assets=fin["TA"],
            retained_earnings=fin["RE"],
            ebit=fin["EBIT"],
            total_liabilities=fin["TL"],
            sales=fin["Sales"],
            market_value_equity=mve,
            date=date
        )


@dataclass
class ZScoreComponents:
    """Container for individual Z-score components and final score."""
    working_capital_ratio: float  # X1
    retained_earnings_ratio: float  # X2
    ebit_ratio: float  # X3
    market_value_ratio: float  # X4
    asset_turnover: float  # X5
    z_score: float
    diagnostic: str
    date: datetime
    model: ZScoreModel
    industry_metrics: Optional[Dict[str, float]] = None
    tech_insights: Optional[List[str]] = None

    @property
    def as_dict(self) -> Dict[str, Any]:
        """Convert components to a dictionary."""
        return {
            'Working Capital/Total Assets': self.working_capital_ratio,
            'Retained Earnings/Total Assets': self.retained_earnings_ratio,
            'EBIT/Total Assets': self.ebit_ratio,
            'Market Value of Equity/Total Liabilities': self.market_value_ratio,
            'Sales/Total Assets': self.asset_turnover,
            'Z-Score': self.z_score,
            'Diagnostic': self.diagnostic,
            'Date': self.date,
            'Model': self.model.value
        }


def compute_zscore(metrics: FinancialMetrics, model: ZScoreModel = DEFAULT_ZSCORE_MODEL) -> ZScoreComponents:
    """
    Compute Altman Z-Score for a company using specified model.
    
    Args:
        metrics (FinancialMetrics): Financial metrics for the company
        model (ZScoreModel): Z-score model to use (default: ORIGINAL)
        
    Returns:
        ZScoreComponents: Calculated Z-score components and final score
        
    Model Selection Guide:
        - ORIGINAL: For public manufacturing companies in developed markets
          * Most widely used and validated
          * Best for established public companies
          * Uses market value of equity
        
        - PRIVATE: For private manufacturing companies
          * Revised weights to work without market data
          * Uses book value instead of market value
          * Adjusted thresholds for private company characteristics
        
        - SERVICE: For non-manufacturing/service companies
          * Removes asset turnover ratio (X5)
          * Adjusted weights for service sector characteristics
          * Suitable for tech companies, financial services, etc.
        
        - EM: For companies in emerging markets
          * Modified to account for market volatility
          * Adjusted thresholds for emerging market conditions
          * More conservative in bankruptcy prediction
        
    Example:
        # Determine the appropriate model
        model = determine_zscore_model(
            is_public=True,
            is_manufacturing=False,  # Tech company
            is_emerging_market=False
        )
        
        # Calculate Z-score
        z_score = compute_zscore(metrics, model)
    """
    # Get model parameters
    params = ZSCORE_MODELS[model]
    
    # Calculate working capital
    working_capital = metrics.current_assets - metrics.current_liabilities
    
    # Calculate ratios
    x1 = working_capital / metrics.total_assets
    x2 = metrics.retained_earnings / metrics.total_assets
    x3 = metrics.ebit / metrics.total_assets
    x4 = metrics.market_value_equity / metrics.total_liabilities
    x5 = metrics.sales / metrics.total_assets if model != ZScoreModel.SERVICE else 0
    
    # Calculate Z-score
    z_score = (
        params["X1"] * x1 +
        params["X2"] * x2 +
        params["X3"] * x3 +
        params["X4"] * x4 +
        params["X5"] * x5
    )
    
    # Determine diagnostic
    thresholds = params["thresholds"]
    if z_score > thresholds["safe"]:
        diagnostic = "Safe Zone"
    elif z_score < thresholds["distress"]:
        diagnostic = "Distress Zone"
    else:
        diagnostic = "Grey Zone"
    
    return ZScoreComponents(
        working_capital_ratio=x1,
        retained_earnings_ratio=x2,
        ebit_ratio=x3,
        market_value_ratio=x4,
        asset_turnover=x5,
        z_score=z_score,
        diagnostic=diagnostic,
        date=metrics.date,
        model=model
    )


class ZScoreCalculator:
    """Class for calculating Altman Z-Score and performing trend analysis."""
    
    def __init__(self, model: ZScoreModel = DEFAULT_ZSCORE_MODEL):
        """Initialize the calculator with the specified model."""
        self.model = model
        self.history: List[ZScoreComponents] = []
    
    def add_calculation(self, metrics: FinancialMetrics) -> ZScoreComponents:
        """Add a new Z-score calculation to the history."""
        components = compute_zscore(metrics, self.model)
        self.history.append(components)
        return components
    
    def analyze_trend(self, periods: int = 4) -> Optional[pd.DataFrame]:
        """Analyze Z-score trend over the specified number of periods."""
        if len(self.history) < 2:
            return None
            
        # Convert history to DataFrame
        df = pd.DataFrame([comp.as_dict for comp in self.history])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Calculate period-over-period changes
        df['Z-Score Change'] = df['Z-Score'].diff()
        df['Trend'] = df['Z-Score Change'].apply(
            lambda x: 'Improving' if x > 0 else 'Deteriorating' if x < 0 else 'Stable'
        )
        
        return df.tail(periods)


class IndustryComparison:
    """Class for comparing Z-scores within industry sectors."""
    
    def __init__(self):
        self._industry_data: Dict[str, List[float]] = {}
        self._tech_subsector_data: Dict[str, List[float]] = {}
    
    def add_score(self, score: float, profile: CompanyProfile):
        """Add a Z-score to the industry database."""
        industry = profile.industry_group.value
        if industry not in self._industry_data:
            self._industry_data[industry] = []
        self._industry_data[industry].append(score)
        
        if profile.tech_subsector:
            subsector = profile.tech_subsector.value
            if subsector not in self._tech_subsector_data:
                self._tech_subsector_data[subsector] = []
            self._tech_subsector_data[subsector].append(score)
    
    def get_industry_metrics(self, profile: CompanyProfile, score: float) -> Dict[str, float]:
        """Get comparison metrics for a company's industry."""
        industry = profile.industry_group.value
        industry_scores = self._industry_data.get(industry, [])
        
        subsector_metrics = {}
        if profile.tech_subsector:
            subsector = profile.tech_subsector.value
            subsector_scores = self._tech_subsector_data.get(subsector, [])
            if subsector_scores:
                subsector_metrics = {
                    'subsector_median': float(pd.Series(subsector_scores).median()),
                    'subsector_percentile': float(pd.Series(subsector_scores).rank(pct=True).iloc[-1]),
                    'subsector_count': len(subsector_scores)
                }
        
        if not industry_scores:
            return {'industry_count': 0, **subsector_metrics}
        
        return {
            'industry_median': float(pd.Series(industry_scores).median()),
            'industry_percentile': float(pd.Series(industry_scores).rank(pct=True).iloc[-1]),
            'industry_count': len(industry_scores),
            **subsector_metrics
        }
    
    def get_tech_specific_insights(self, profile: CompanyProfile, score: float) -> List[str]:
        """Get specific insights for tech companies."""
        insights = []
        
        if not profile.is_tech_or_ai:
            return insights
            
        # Compare with industry
        metrics = self.get_industry_metrics(profile, score)
        
        # R&D intensity analysis
        if profile.rd_intensity:
            if profile.rd_intensity > 0.15:  # High R&D investment
                insights.append(
                    "High R&D investment (>15% of revenue) suggests strong "
                    "focus on innovation and future growth potential."
                )
            elif profile.rd_intensity < 0.05:  # Low R&D investment
                insights.append(
                    "Low R&D investment (<5% of revenue) may indicate mature "
                    "products or potential underinvestment in innovation."
                )
        
        # Subsector comparison
        if metrics.get('subsector_count', 0) > 0 and profile.tech_subsector:
            percentile = metrics.get('subsector_percentile', 0)
            subsector_name = profile.tech_subsector.value
            if percentile > 0.75:
                insights.append(
                    f"Strong performance within {subsector_name} "
                    f"subsector (top {int((1-percentile)*100)}%)."
                )
            elif percentile < 0.25:
                insights.append(
                    f"Underperforming compared to {subsector_name} "
                    f"peers (bottom {int(percentile*100)}%)."
                )
        
        return insights

def determine_zscore_model(profile: CompanyProfile) -> Tuple[ZScoreModel, str]:
    """
    Determine the appropriate Z-score model based on company characteristics.
    
    Args:
        profile (CompanyProfile): Company classification profile
        
    Returns:
        Tuple[ZScoreModel, str]: Selected model and reason for selection
        
    Notes:
        Model Selection Priority:
        1. Tech/AI Companies:
           - Use SERVICE model with tech-adjusted thresholds
           - Focus on intangible assets and R&D
        
        2. Market Category:
           - Emerging markets use EM model regardless of sector
           - Developed markets proceed to sector analysis
        
        3. Sector:
           - Manufacturing uses ORIGINAL (public) or PRIVATE
           - Service/Financial uses SERVICE model
    """
    reason = ""
    
    # First check market category - Emerging markets always use EM model
    if profile.is_emerging_market:
        reason = (
            "Selected EM model due to emerging market status. "
            "This model is calibrated for higher market volatility."
        )
        return ZScoreModel.EM, reason

    # For developed markets, handle tech/AI companies
    if profile.is_tech_or_ai:
        if profile.tech_subsector in (TechSubsector.HARDWARE, TechSubsector.OTHER_TECH):
            reason = (
                "Selected ORIGINAL model for hardware/mixed tech company. "
                "This company has significant physical assets."
            )
            return ZScoreModel.ORIGINAL, reason
        else:
            reason = (
                "Selected SERVICE model for software/service tech company. "
                "This model better accounts for intangible value and R&D."
            )
            return ZScoreModel.SERVICE, reason
    
    # Handle manufacturing companies
    if profile.is_manufacturing:
        if profile.is_public:
            reason = (
                "Selected ORIGINAL model for public manufacturing company. "
                "This is the classic model with extensive validation."
            )
            return ZScoreModel.ORIGINAL, reason
        else:
            reason = (
                "Selected PRIVATE model for private manufacturing company. "
                "This model is adjusted for private company characteristics."
            )
            return ZScoreModel.PRIVATE, reason
    
    # Handle service companies
    if profile.industry_group == IndustryGroup.SERVICE:
        reason = (
            "Selected SERVICE model for pure service company. "
            "This model excludes asset turnover ratio and adjusts other weights."
        )
        return ZScoreModel.SERVICE, reason
        
    # Default to SERVICE model for anything else
    reason = (
        "Selected SERVICE model (default). "
        "This model is most adaptable to modern business models."
    )
    return ZScoreModel.SERVICE, reason


def validate_model_selection(
    model: ZScoreModel,
    metrics: FinancialMetrics,
    profile: CompanyProfile
) -> List[str]:
    """
    Validate the selected model against company metrics and profile.
    
    Args:
        model: Selected Z-score model
        metrics: Company financial metrics
        profile: Company classification profile
    
    Returns:
        List[str]: List of warnings if any validation issues found
    """
    warnings = []
    
    # Calculate key ratios for validation
    working_capital = metrics.current_assets - metrics.current_liabilities
    working_capital_ratio = working_capital / metrics.total_assets
    retained_earnings_ratio = metrics.retained_earnings / metrics.total_assets
    ebit_ratio = metrics.ebit / metrics.total_assets
    market_value_ratio = metrics.market_value_equity / metrics.total_liabilities
    asset_turnover = metrics.sales / metrics.total_assets
    
    # Check for tech/AI specific issues
    if profile.is_tech_or_ai:
        if metrics.market_value_equity < metrics.total_assets * 0.5:
            warnings.append(
                "Market value is unusually low for a tech company. "
                "Consider examining intangible assets and R&D investments."
            )
        if asset_turnover > 2.0 and profile.tech_subsector not in (TechSubsector.HARDWARE, TechSubsector.OTHER_TECH):
            warnings.append(
                "High asset turnover for a software/service tech company. "
                "Verify if significant physical assets are present."
            )

    # Manufacturing company checks
    if profile.is_manufacturing:
        if working_capital_ratio < 0.1:
            warnings.append(
                "Low working capital ratio for a manufacturing company. "
                "May indicate liquidity constraints."
            )

    # Emerging market checks
    if profile.is_emerging_market and model != ZScoreModel.EM:
        warnings.append(
            "Not using EM model for emerging market company. "
            "This may affect accuracy."
        )
    
    # Model-specific validations
    if model == ZScoreModel.ORIGINAL and not profile.is_public:
        warnings.append(
            "Using ORIGINAL model for non-public company. "
            "Consider using PRIVATE model instead."
        )
    elif model == ZScoreModel.SERVICE and asset_turnover > 2.0:
        warnings.append(
            "High asset turnover for SERVICE model. "
            "Consider if ORIGINAL model would be more appropriate."
        )
    
    # Check for extreme values
    ratios = [
        working_capital_ratio,
        retained_earnings_ratio,
        ebit_ratio,
        market_value_ratio,
        asset_turnover
    ]
    
    if any(abs(ratio) > 10 for ratio in ratios):
        warnings.append(
            "Warning: Extreme values detected in ratios. "
            "Verify financial data accuracy."
        )
    
    # Model-specific validations
    if model == ZScoreModel.SERVICE:
        if asset_turnover > 2 and profile.is_tech_or_ai:
            warnings.append(
                "Warning: High asset turnover for tech company. "
                "Verify if significant physical assets are present."
            )
    
    return warnings

def get_industry_diagnostic(zscore: float, profile: CompanyProfile, 
                        financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get industry-specific diagnostic interpretation of Z-Score.
    
    Args:
        zscore: Calculated Z-Score value
        profile: Company profile with industry classification
        financial_data: Optional financial metrics for stage determination
        
    Returns:
        Dict containing diagnostic status and interpretation
    """
    # Convert to Decimal for threshold comparison
    score = Decimal(str(zscore))
    
    # Get financial metrics for growth determination
    if financial_data is None:
        financial_data = {}
    
    revenue_growth = Decimal(str(financial_data.get('revenue_growth', 0)))
    
    # Select appropriate thresholds based on company profile
    if profile.industry_group == IndustryGroup.TECH:
        if profile.tech_subsector == TechSubsector.AI_ML:
            # Determine stage for AI/ML companies
            if revenue_growth > Decimal('1.0'):
                thresholds = ModelThresholds.tech_early_stage()
                company_type = "tech_early"
            elif revenue_growth > Decimal('0.3'):
                thresholds = ModelThresholds.tech_growth_stage()
                company_type = "tech_growth"
            else:
                thresholds = ModelThresholds.tech_mature_stage()
                company_type = "tech_mature"
        elif profile.tech_subsector == TechSubsector.SAAS:
            thresholds = ModelThresholds.saas_company()
            company_type = "saas"
        else:
            thresholds = ModelThresholds.non_manufacturing()
            company_type = "tech_other"
    elif not profile.is_public:
        thresholds = ModelThresholds.private_company()
        company_type = "private"
    elif profile.is_manufacturing:
        thresholds = ModelThresholds.original()
        company_type = "manufacturing"
    else:
        thresholds = ModelThresholds.non_manufacturing()
        company_type = "non_manufacturing"
    
    return thresholds.get_diagnostic(score, company_type)
