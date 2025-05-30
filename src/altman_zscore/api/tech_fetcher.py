"""Tech industry specific financial data fetcher."""

from typing import Dict, List

from bs4 import BeautifulSoup

from ..data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel, ValidationRule
from .base_fetcher import BaseFinancialFetcher, FinancialValue


class TechFinancialFetcher(BaseFinancialFetcher):
    """Financial data fetcher specialized for tech companies."""

    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get tech industry specific metrics from the filing.

        Args:
            soup: BeautifulSoup object of the filing HTML

        Returns:
            Dictionary of tech-specific metrics
        """
        from ..fetch_financials import find_with_period, find_xbrl_tag

        metrics = {}

        # Try to get R&D expenses
        rd_concepts = [
            "us-gaap:ResearchAndDevelopmentExpense",
            "us-gaap:TechnologyAndDevelopmentExpense",
            "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ]
        if rd := find_xbrl_tag(soup, rd_concepts):
            metrics["research_and_development_expense"] = rd  # Match the test's field name

        # Try to get revenue growth from sequential periods
        revenue_concepts = [
            "us-gaap:Revenues",
            "us-gaap:RevenuesFromContractWithCustomerExcludingAssessedTax",
            "us-gaap:RevenuesNetOfInterestExpense",
            "us-gaap:Revenues",
        ]
        dated_revenues = find_with_period(soup, revenue_concepts)
        if len(dated_revenues) >= 2:
            # Sort by date descending
            dated_revenues.sort(key=lambda x: x[0], reverse=True)
            current, prior = dated_revenues[0][1], dated_revenues[1][1]
            if prior > 0:
                metrics["revenue_growth"] = (current - prior) / prior

        # Try to get subscription revenue for SaaS
        subscription_concepts = [
            "us-gaap:SubscriptionRevenue",
            "us-gaap:CloudServicesRevenue",
            "us-gaap:RecurringRevenue",
            "us-gaap:SubscriptionAndTransactionBasedRevenue",
        ]
        if subs := find_xbrl_tag(soup, subscription_concepts):
            metrics["subscription_revenue"] = subs

        return metrics

    def validate_data(self, data: Dict[str, FinancialValue], profile) -> List[ValidationIssue]:
        """Validate tech company metrics."""
        # Create a fresh validator for tech-specific rules
        validator = FinancialDataValidator()

        # Add tech-specific validation rules
        rules = [
            ValidationRule(
                field="revenue_margin",
                description="Tech companies should maintain high gross margins (>50%)",
                level=ValidationLevel.WARNING,
                min_value=0.50,
                required=False,
                allow_zero=False,
                allow_negative=False,
            ),
            ValidationRule(
                field="research_and_development_expense",
                description="R&D expenses should be at least 10% of revenue for tech companies",
                level=ValidationLevel.WARNING,
                ratio_denominator="revenue",
                ratio_min=0.10,
                required=False,
                allow_zero=False,
                allow_negative=False,
            ),
            ValidationRule(
                field="subscription_revenue",
                description="SaaS companies should have >60% recurring revenue",
                level=ValidationLevel.WARNING,
                ratio_denominator="revenue",
                ratio_min=0.60,
                required=False,
            ),
            ValidationRule(
                field="revenue_growth",
                description="Tech companies should maintain strong growth (>20% YoY)",
                level=ValidationLevel.WARNING,
                min_value=0.20,
                required=False,
                allow_zero=False,
                allow_negative=False,
            ),
        ]

        # Add rules to validator
        for rule in rules:
            validator.add_rule(rule)

        # Call validate_data on the parent class first to include base rules
        issues = super().validate_data(data, profile)

        # Add tech-specific validation issues
        issues.extend(validator.validate(data))
        return issues
