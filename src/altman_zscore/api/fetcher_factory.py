"""Factory for creating industry-specific financial data fetchers."""

from typing import Dict, Type

from ..company_profile import CompanyProfile, IndustryGroup  # Ensure these symbols exist
from .base_fetcher import BaseFinancialFetcher
from .manufacturing_fetcher import ManufacturingFinancialFetcher
from .service_fetcher import ServiceFinancialFetcher
from .tech_fetcher import TechFinancialFetcher

# Fetcher registry
FETCHERS: Dict[str, Type[BaseFinancialFetcher]] = {
    "TECH": TechFinancialFetcher,
    "MANUFACTURING": ManufacturingFinancialFetcher,
    "SERVICE": ServiceFinancialFetcher,
}


def create_fetcher(company_profile: CompanyProfile) -> BaseFinancialFetcher:
    """Create appropriate financial data fetcher based on company profile.

    Args:
        company_profile: Profile containing company classification

    Returns:
        Industry-specific financial data fetcher

    Note:
        If a company doesn't fit into the main industry categories, the base fetcher
        is used which provides common financial metrics applicable to all industries.
    """
    if company_profile.industry_group == IndustryGroup.TECH or company_profile.industry_group == IndustryGroup.AI:
        industry = "TECH"
    elif company_profile.industry_group == IndustryGroup.MANUFACTURING:
        industry = "MANUFACTURING"
    elif company_profile.industry_group == IndustryGroup.SERVICE:
        industry = "SERVICE"
    else:
        # For unknown or other industries, use base fetcher
        return BaseFinancialFetcher()

    # Use registered fetcher for known industries
    fetcher_class = FETCHERS.get(industry, BaseFinancialFetcher)
    return fetcher_class()
