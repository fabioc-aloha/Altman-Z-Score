"""Base class for financial data fetchers."""

from abc import ABC
from decimal import Decimal
from typing import Dict, Union

from bs4 import BeautifulSoup

from ..data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel, ValidationRule
from ..fetch_financials import find_xbrl_tag
from ..industry_classifier import CompanyProfile

# Define a type for financial values that can be float or Decimal
FinancialValue = Union[float, Decimal]


class BaseFinancialFetcher(ABC):
    """Base class for industry-specific financial data fetchers."""

    def __init__(self):
        """Initialize the fetcher with a validator."""
        self.validator = FinancialDataValidator()

    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get basic financial metrics that are common across industries.

        This base implementation extracts fundamental financial metrics that are
        relevant for any industry. Specialized fetchers can extend this by
        overriding the method and adding industry-specific metrics.

        Args:
            soup: BeautifulSoup object of the filing HTML

        Returns:
            Dictionary of basic financial metrics including:
            - revenue_margin: Gross margin ratio
            - operating_margin: Operating margin ratio
            - return_on_assets: Return on assets ratio
        """

        metrics = {}

        # Get gross margin components
        revenue_concepts = [
            "us-gaap:Revenues",
            "us-gaap:RevenuesFromContractWithCustomerExcludingAssessedTax",
            "us-gaap:RevenuesNetOfInterestExpense",
            "us-gaap:SalesRevenueNet",
        ]
        cogs_concepts = [
            "us-gaap:CostOfGoodsAndServicesSold",
            "us-gaap:CostOfRevenue",
            "us-gaap:CostOfGoodsSold",
        ]

        revenue = find_xbrl_tag(soup, revenue_concepts)
        cogs = find_xbrl_tag(soup, cogs_concepts)
        if revenue and cogs and revenue > 0:
            metrics["revenue_margin"] = (revenue - cogs) / revenue

        # Get operating margin components
        op_income_concepts = [
            "us-gaap:OperatingIncomeLoss",
            "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
            "us-gaap:IncomeLossFromContinuingOperations",
        ]

        op_income = find_xbrl_tag(soup, op_income_concepts)
        if op_income and revenue and revenue > 0:
            metrics["operating_margin"] = op_income / revenue

        # Get return on assets components
        asset_concepts = ["us-gaap:Assets", "us-gaap:TotalAssets", "us-gaap:AssetsTotal"]
        net_income_concepts = [
            "us-gaap:NetIncomeLoss",
            "us-gaap:ProfitLoss",
            "us-gaap:IncomeLossFromContinuingOperations",
        ]

        assets = find_xbrl_tag(soup, asset_concepts)
        net_income = find_xbrl_tag(soup, net_income_concepts)
        if net_income and assets and assets > 0:
            metrics["return_on_assets"] = net_income / assets

        return metrics

    def validate_data(self, data: Dict[str, FinancialValue], company_profile: CompanyProfile) -> list[ValidationIssue]:
        """Validate the financial data.

        Args:
            data: Financial data to validate (can be floats or Decimals)
            company_profile: Company profile for industry context

        Returns:
            List of validation issues
        """
        # Add basic validation rules
        base_rules = [
            ValidationRule(
                field="revenue_margin",
                description="Revenue margin should be positive",
                level=ValidationLevel.ERROR,
                min_value=0.0,
                required=False,
                allow_zero=False,
                allow_negative=False,
            ),
            ValidationRule(
                field="operating_margin",
                description="Operating margin should be reasonable",
                level=ValidationLevel.WARNING,
                min_value=-0.2,  # Allow some operating losses for growth companies
                max_value=0.4,  # Flag unusually high margins
                required=False,
            ),
            ValidationRule(
                field="return_on_assets",
                description="Return on assets should be reasonable",
                level=ValidationLevel.WARNING,
                min_value=-0.1,  # Allow some losses
                max_value=0.3,  # Flag unusually high returns
                required=False,
            ),
        ]

        # Add rules to validator
        for rule in base_rules:
            self.validator.add_rule(rule)

        return self.validator.validate(data)
