"""Tech industry specific financial data fetcher."""

from typing import Dict, List

from bs4 import BeautifulSoup

from ..data_validation import FinancialDataValidator, ValidationIssue, ValidationLevel
from ..data_fetching.sec_edgar import find_xbrl_tag
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
        metrics = {}

        # Try to get R&D expenses
        rd_concepts = [
            "us-gaap:ResearchAndDevelopmentExpense",
            "us-gaap:TechnologyAndDevelopmentExpense",
            "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        ]
        if rd := find_xbrl_tag(soup, rd_concepts):
            metrics["research_and_development_expense"] = rd

        # Try to get revenue growth from sequential periods
        # NOTE: find_with_period is not implemented, so fallback to None for revenue_growth
        # If you want to implement this, you need to parse periods and values from soup
        # For now, skip revenue_growth calculation

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

    def validate_data(self, data: Dict[str, FinancialValue], company_profile) -> List[ValidationIssue]:
        """Validate tech company metrics."""
        issues = super().validate_data(data, company_profile)
        # Tech-specific validation logic
        if "revenue_margin" in data:
            val = data["revenue_margin"]
            if val is not None and val < 0.5:
                issues.append(ValidationIssue(
                    field="revenue_margin",
                    issue="Tech companies should maintain high gross margins (>50%)",
                    level=ValidationLevel.WARNING,
                    value=val
                ))
        if "research_and_development_expense" in data and "revenue" in data:
            rd = data["research_and_development_expense"]
            revenue = data["revenue"]
            try:
                ratio = float(rd) / float(revenue)
            except Exception:
                ratio = None
            if revenue and rd is not None and ratio is not None and ratio < 0.10:
                issues.append(ValidationIssue(
                    field="research_and_development_expense",
                    issue="R&D expenses should be at least 10% of revenue for tech companies",
                    level=ValidationLevel.WARNING,
                    value=rd
                ))
        if "subscription_revenue" in data and "revenue" in data:
            subs = data["subscription_revenue"]
            revenue = data["revenue"]
            try:
                ratio = float(subs) / float(revenue)
            except Exception:
                ratio = None
            if revenue and subs is not None and ratio is not None and ratio < 0.60:
                issues.append(ValidationIssue(
                    field="subscription_revenue",
                    issue="SaaS companies should have >60% recurring revenue",
                    level=ValidationLevel.WARNING,
                    value=subs
                ))
        if "revenue_growth" in data:
            val = data["revenue_growth"]
            if val is not None and val < 0.20:
                issues.append(ValidationIssue(
                    field="revenue_growth",
                    issue="Tech companies should maintain strong growth (>20% YoY)",
                    level=ValidationLevel.WARNING,
                    value=val
                ))
        return issues
