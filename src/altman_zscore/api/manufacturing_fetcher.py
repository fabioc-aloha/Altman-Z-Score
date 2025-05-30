"""Manufacturing industry specific financial data fetcher."""

from typing import Dict, List

from bs4 import BeautifulSoup

from ..data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel
from ..data_fetching.financials import find_xbrl_tag  # Ensure this module exists
from .base_fetcher import BaseFinancialFetcher, FinancialValue


class ManufacturingFinancialFetcher(BaseFinancialFetcher):
    """Financial data fetcher specialized for manufacturing companies."""

    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get manufacturing industry specific metrics from the filing.

        Args:
            soup: BeautifulSoup object of the filing HTML

        Returns:
            Dictionary of manufacturing-specific metrics
        """

        metrics = {}

        # Try to get inventory turnover components
        cogs_concepts = [
            "us-gaap:CostOfGoodsAndServicesSold",
            "us-gaap:CostOfRevenue",
            "us-gaap:CostOfGoodsSold",
        ]
        inventory_concepts = [
            "us-gaap:InventoryNet",
            "us-gaap:Inventories",
            "us-gaap:InventoryGross",
        ]

        cogs = find_xbrl_tag(soup, cogs_concepts)
        inventory = find_xbrl_tag(soup, inventory_concepts)
        if cogs and inventory and inventory > 0:
            metrics["inventory_turnover"] = cogs / inventory

        # Try to get CapEx
        capex_concepts = [
            "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",
            "us-gaap:CapitalExpendituresIncurredButNotYetPaid",
            "us-gaap:PaymentsToAcquireProductiveAssets",
            "us-gaap:CapitalExpendituresIncurred",  # Additional common tag
        ]
        if capex := find_xbrl_tag(soup, capex_concepts):
            capex_value = abs(capex)  # CapEx is usually reported as negative
            total_assets = find_xbrl_tag(soup, ["us-gaap:Assets", "us-gaap:TotalAssets"])
            if total_assets and total_assets > 0:
                metrics["capex"] = capex_value
                # Also compute and store the ratio for validation
                metrics["capex_ratio"] = capex_value / total_assets

        return metrics

    def validate_data(self, data: Dict[str, FinancialValue], company_profile) -> List[ValidationIssue]:
        """Validate manufacturing specific metrics."""
        # Only use the base validator and parent class validation
        return super().validate_data(data, company_profile)
