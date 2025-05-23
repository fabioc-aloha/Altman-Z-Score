"""
Analysis strategy module for determining the appropriate Z-score model and data requirements.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from decimal import Decimal

from .company_profile import (
    CompanyProfile, CompanyStage, IndustryGroup,
    MarketCategory, TechSubsector
)
from .models import ModelThresholds

@dataclass
class DataRequirements:
    """Required financial data fields for analysis."""
    required_fields: Set[str]
    optional_fields: Set[str]
    alternative_fields: Dict[str, List[str]]  # primary field -> list of alternatives
    calculated_fields: Set[str]  # fields that need to be calculated

@dataclass
class ZScoreStrategy:
    """Complete strategy for Z-score analysis."""
    model_thresholds: ModelThresholds
    data_requirements: DataRequirements
    adjustments: List[str]  # List of adjustments to apply
    validation_rules: Dict[str, Dict]  # Field-specific validation rules

class StrategySelector:
    """
    Determines the appropriate Z-score analysis strategy based on company profile.
    """
    def __init__(self):
        """Initialize with default strategies."""
        self._init_data_requirements()
        
    def _init_data_requirements(self):
        """Initialize standard data requirements for different models."""
        self.basic_requirements = DataRequirements(
            required_fields={
                "total_assets", "total_liabilities", "retained_earnings",
                "working_capital", "ebit", "total_equity", "sales"
            },
            optional_fields={
                "market_cap", "rd_expense", "cash_flow_operations"
            },
            alternative_fields={
                "working_capital": ["current_assets", "current_liabilities"],
                "ebit": ["operating_income", "net_income_loss"]
            },
            calculated_fields={
                "working_capital", "market_value_equity"
            }
        )
        
    def get_tech_strategy(self, profile: CompanyProfile) -> ZScoreStrategy:
        """Get strategy for technology companies."""
        if profile.company_stage == CompanyStage.EARLY:
            thresholds = ModelThresholds.tech_early_stage()
            # Add R&D adjustment for early stage
            adjustments = ["rd_capitalization", "operating_lease_capitalization"]
        elif profile.company_stage == CompanyStage.GROWTH:
            thresholds = ModelThresholds.tech_growth_stage()
            adjustments = ["rd_adjustment", "operating_lease_capitalization"]
        else:
            # Mature tech companies
            thresholds = ModelThresholds.non_manufacturing()
            adjustments = ["operating_lease_capitalization"]
            
        return ZScoreStrategy(
            model_thresholds=thresholds,
            data_requirements=self.basic_requirements,
            adjustments=adjustments,
            validation_rules=self._get_tech_validation_rules()
        )
    
    def get_manufacturing_strategy(self, profile: CompanyProfile) -> ZScoreStrategy:
        """Get strategy for manufacturing companies."""
        thresholds = ModelThresholds.original()
        adjustments = ["inventory_adjustment", "operating_lease_capitalization"]
        
        if profile.market_category == MarketCategory.EMERGING:
            # Adjust thresholds for emerging markets
            thresholds = ModelThresholds.emerging_markets()
            adjustments.append("country_risk_adjustment")
        
        return ZScoreStrategy(
            model_thresholds=thresholds,
            data_requirements=self.basic_requirements,
            adjustments=adjustments,
            validation_rules=self._get_manufacturing_validation_rules()
        )
    
    def select_strategy(self, profile: CompanyProfile) -> ZScoreStrategy:
        """
        Select the appropriate analysis strategy based on company profile.
        
        Args:
            profile: CompanyProfile object containing company characteristics
            
        Returns:
            ZScoreStrategy object with selected model and requirements
        """
        if profile.is_excluded:
            raise ValueError(f"Company {profile.ticker} is excluded: {profile.exclusion_reason}")
        
        if profile.is_tech_or_ai:
            return self.get_tech_strategy(profile)
        elif profile.is_manufacturing:
            return self.get_manufacturing_strategy(profile)
        else:
            # Default to non-manufacturing model for service companies
            return ZScoreStrategy(
                model_thresholds=ModelThresholds.non_manufacturing(),
                data_requirements=self.basic_requirements,
                adjustments=["operating_lease_capitalization"],
                validation_rules=self._get_default_validation_rules()
            )
    
    def _get_tech_validation_rules(self) -> Dict:
        """Get validation rules for technology companies."""
        return {
            "rd_expense": {
                "min_value": 0,
                "max_percent_revenue": 0.5
            },
            "operating_margin": {
                "min_value": -1.0  # Allow negative margins for early stage
            }
        }
    
    def _get_manufacturing_validation_rules(self) -> Dict:
        """Get validation rules for manufacturing companies."""
        return {
            "inventory": {
                "min_percent_assets": 0.05,
                "max_percent_assets": 0.5
            },
            "operating_margin": {
                "min_value": -0.2  # Stricter margin requirements
            }
        }
    
    def _get_default_validation_rules(self) -> Dict:
        """Get default validation rules."""
        return {
            "operating_margin": {
                "min_value": -0.5
            }
        }
