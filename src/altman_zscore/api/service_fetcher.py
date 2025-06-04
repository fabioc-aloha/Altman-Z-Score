"""Service industry specific financial data fetcher."""

from typing import Dict, List

from bs4 import BeautifulSoup

from ..data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel
from ..data_fetching.sec_edgar import find_xbrl_tag
from .base_fetcher import BaseFinancialFetcher, FinancialValue


class ServiceFinancialFetcher(BaseFinancialFetcher):
    """Financial data fetcher specialized for service companies."""

    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get service industry specific metrics from the filing.

        Args:
            soup: BeautifulSoup object of the filing HTML

        Returns:
            Dictionary of service-specific metrics
        """
        # Get base metrics first
        metrics = super().get_industry_metrics(soup)

        # Service-specific metrics
        employee_comp_concepts = [
            "us-gaap:SalariesWagesAndBenefits",
            "us-gaap:EmployeeRelatedCostsAndProfessionalFees",
            "us-gaap:LaborAndRelatedExpense",
        ]
        revenue_concepts = [
            "us-gaap:Revenues",
            "us-gaap:RevenuesFromContractWithCustomerExcludingAssessedTax",
            "us-gaap:RevenuesNetOfInterestExpense",
            "us-gaap:SalesRevenueNet",
        ]

        # Get employee productivity ratio
        emp_comp = find_xbrl_tag(soup, employee_comp_concepts)
        revenue = find_xbrl_tag(soup, revenue_concepts)
        if emp_comp and revenue and emp_comp > 0:
            metrics["revenue_per_employee_cost"] = revenue / emp_comp

        # Get service delivery efficiency
        expense_concepts = [
            "us-gaap:ServiceCost",
            "us-gaap:CostOfServices",
            "us-gaap:ServiceExpense",
        ]
        expenses = find_xbrl_tag(soup, expense_concepts)
        if expenses and revenue and revenue > 0:
            metrics["service_delivery_efficiency"] = 1 - (expenses / revenue)

        # Get recurring revenue components
        recurring_concepts = [
            "us-gaap:ContractWithCustomerLiabilityRevenue",
            "us-gaap:RecurringRevenue",
            "us-gaap:SubscriptionRevenue",
        ]
        recurring = find_xbrl_tag(soup, recurring_concepts)
        if recurring and revenue and revenue > 0:
            metrics["recurring_revenue_ratio"] = recurring / revenue

        return metrics

    def validate_data(self, data: Dict[str, FinancialValue], company_profile) -> List[ValidationIssue]:
        """Validate service company metrics."""
        issues = super().validate_data(data, company_profile)
        # Service-specific validation logic
        if "revenue_per_employee_cost" in data:
            val = data["revenue_per_employee_cost"]
            if val is not None and val < 2.0:
                issues.append(ValidationIssue(
                    field="revenue_per_employee_cost",
                    issue="Revenue should be at least 2x employee costs for profitability",
                    level=ValidationLevel.WARNING,
                    value=val
                ))
        if "service_delivery_efficiency" in data:
            val = data["service_delivery_efficiency"]
            if val is not None and val < 0.25:
                issues.append(ValidationIssue(
                    field="service_delivery_efficiency",
                    issue="Service delivery efficiency should be at least 25%",
                    level=ValidationLevel.WARNING,
                    value=val
                ))
        return issues
