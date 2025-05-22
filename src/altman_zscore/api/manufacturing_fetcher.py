"""Manufacturing industry specific financial data fetcher."""
from typing import Dict, List
from bs4 import BeautifulSoup
from .base_fetcher import BaseFinancialFetcher, FinancialValue
from ..data_validation import (
    ValidationRule, ValidationLevel, ValidationIssue, FinancialDataValidator
)

class ManufacturingFinancialFetcher(BaseFinancialFetcher):
    """Financial data fetcher specialized for manufacturing companies."""
    
    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get manufacturing industry specific metrics from the filing.
        
        Args:
            soup: BeautifulSoup object of the filing HTML
            
        Returns:
            Dictionary of manufacturing-specific metrics
        """
        from ..fetch_financials import find_xbrl_tag
        
        metrics = {}
        
        # Try to get inventory turnover components
        cogs_concepts = [
            'us-gaap:CostOfGoodsAndServicesSold',
            'us-gaap:CostOfRevenue',
            'us-gaap:CostOfGoodsSold'
        ]
        inventory_concepts = [
            'us-gaap:InventoryNet',
            'us-gaap:Inventories',
            'us-gaap:InventoryGross'
        ]
        
        cogs = find_xbrl_tag(soup, cogs_concepts)
        inventory = find_xbrl_tag(soup, inventory_concepts)
        if cogs and inventory and inventory > 0:
            metrics["inventory_turnover"] = cogs / inventory
        
        # Try to get CapEx
        capex_concepts = [
            'us-gaap:PaymentsToAcquirePropertyPlantAndEquipment',
            'us-gaap:CapitalExpendituresIncurredButNotYetPaid',
            'us-gaap:PaymentsToAcquireProductiveAssets',
            'us-gaap:CapitalExpendituresIncurred'  # Additional common tag
        ]
        if capex := find_xbrl_tag(soup, capex_concepts):
            capex_value = abs(capex)  # CapEx is usually reported as negative
            total_assets = find_xbrl_tag(soup, ['us-gaap:Assets', 'us-gaap:TotalAssets'])
            if total_assets and total_assets > 0:
                metrics["capex"] = capex_value
                # Also compute and store the ratio for validation
                metrics["capex_ratio"] = capex_value / total_assets
            
        return metrics
        
    def validate_data(self, data: Dict[str, FinancialValue], profile) -> List[ValidationIssue]:
        """Validate manufacturing specific metrics."""
        # Create a validator for manufacturing-specific rules
        validator = FinancialDataValidator()
        
        # Add manufacturing-specific validation rules
        rules = [
            ValidationRule(
                field="inventory_turnover",
                description="Inventory turnover rate should be at least 3x for efficient manufacturing",
                level=ValidationLevel.WARNING,
                min_value=3.0,  
                required=False,
                allow_zero=False,
                allow_negative=False
            ),
            ValidationRule(
                field="inventory",
                description="Inventory should be 10-30% of total assets for manufacturing",
                level=ValidationLevel.WARNING,
                ratio_denominator="total_assets",
                ratio_min=0.10,
                ratio_max=0.30,
                required=False
            ),
            ValidationRule(
                field="capex",
                description="Capital expenditure should be at least 5% of total assets for manufacturing companies",
                level=ValidationLevel.WARNING,
                ratio_denominator="total_assets",
                ratio_min=0.05,
                ratio_max=1.0,
                required=False,  # Not required since we're using a ratio rule
                allow_zero=False,  # CapEx shouldn't be zero for manufacturing
                allow_negative=False
            )
        ]
        
        # Add rules to validator
        for rule in rules:
            validator.add_rule(rule)
        
        # Call validate_data on the parent class first to include base rules
        issues = super().validate_data(data, profile)
        
        # Add manufacturing-specific validation issues
        issues.extend(validator.validate(data))
        return issues
