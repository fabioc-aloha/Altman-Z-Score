"""
Base class for financial data fetchers in Altman Z-Score analysis.

Defines the abstract base class and shared logic for industry-specific financial data fetchers, including basic metric extraction and validation.
"""

from abc import ABC
from decimal import Decimal
from typing import Dict, Union

from bs4 import BeautifulSoup

from ..validation.data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel
from ..data_fetching.sec_edgar import find_xbrl_tag
from ..company.company_profile import CompanyProfile

# Define a type for financial values that can be float or Decimal
FinancialValue = Union[float, Decimal]


class BaseFinancialFetcher(ABC):
    """Base class for industry-specific financial data fetchers.

    Methods:
        get_industry_metrics(soup):
            Extract basic financial metrics common across industries.
        validate_data(data, company_profile):
            Validate the extracted financial data.
    """

    def __init__(self):
        """Initialize the fetcher with a validator."""
        self.validator = FinancialDataValidator()

    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get basic financial metrics that are common across industries.

        This base implementation extracts fundamental financial metrics that are
        relevant for any industry. Specialized fetchers can extend this by
        overriding the method and adding industry-specific metrics.

        Args:
            soup (BeautifulSoup): BeautifulSoup object of the filing HTML.

        Returns:
            dict: Dictionary of basic financial metrics including:
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
            data (dict): Financial data to validate (can be floats or Decimals).
            company_profile (CompanyProfile): Company profile for industry context.

        Returns:
            list: List of validation issues.
        """
        issues = []
        # Base validation logic for key metrics
        if "revenue_margin" in data:
            val = data["revenue_margin"]
            if val is None or val < 0:
                issues.append(ValidationIssue(
                    field="revenue_margin",
                    issue="Revenue margin should be positive",
                    level=ValidationLevel.ERROR,
                    value=val
                ))
        if "operating_margin" in data:
            val = data["operating_margin"]
            if val is not None:
                if val < -0.2 or val > 0.4:
                    issues.append(ValidationIssue(
                        field="operating_margin",
                        issue="Operating margin is outside reasonable range (-0.2 to 0.4)",
                        level=ValidationLevel.WARNING,
                        value=val
                    ))
        if "return_on_assets" in data:
            val = data["return_on_assets"]
            if val is not None:
                if val < -0.1 or val > 0.3:
                    issues.append(ValidationIssue(
                        field="return_on_assets",
                        issue="Return on assets is outside reasonable range (-0.1 to 0.3)",
                        level=ValidationLevel.WARNING,
                        value=val
                    ))
        # Use the built-in validator for required fields and suspicious values
        issues.extend(self.validator.validate(data))
        return issues
