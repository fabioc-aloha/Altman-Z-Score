"""Service industry specific financial data fetcher."""
from typing import Dict, List
from bs4 import BeautifulSoup
from .base_fetcher import BaseFinancialFetcher, FinancialValue
from ..data_validation import (
    ValidationRule, ValidationLevel, ValidationIssue, FinancialDataValidator
)

class ServiceFinancialFetcher(BaseFinancialFetcher):
    """Financial data fetcher specialized for service companies."""
    
    def get_industry_metrics(self, soup: BeautifulSoup) -> Dict[str, FinancialValue]:
        """Get service industry specific metrics from the filing.
        
        Args:
            soup: BeautifulSoup object of the filing HTML
            
        Returns:
            Dictionary of service-specific metrics
        """
        from ..fetch_financials import find_xbrl_tag, find_with_period
        
        # Get base metrics first
        metrics = super().get_industry_metrics(soup)
        
        # Service-specific metrics
        employee_comp_concepts = [
            'us-gaap:SalariesWagesAndBenefits',
            'us-gaap:EmployeeRelatedCostsAndProfessionalFees',
            'us-gaap:LaborAndRelatedExpense'
        ]
        revenue_concepts = [
            'us-gaap:Revenues',
            'us-gaap:RevenuesFromContractWithCustomerExcludingAssessedTax',
            'us-gaap:RevenuesNetOfInterestExpense',
            'us-gaap:SalesRevenueNet'
        ]
        
        # Get employee productivity ratio
        emp_comp = find_xbrl_tag(soup, employee_comp_concepts)
        revenue = find_xbrl_tag(soup, revenue_concepts)
        if emp_comp and revenue and emp_comp > 0:
            metrics["revenue_per_employee_cost"] = revenue / emp_comp
        
        # Get service delivery efficiency
        expense_concepts = [
            'us-gaap:ServiceCost',
            'us-gaap:CostOfServices',
            'us-gaap:ServiceExpense'
        ]
        expenses = find_xbrl_tag(soup, expense_concepts)
        if expenses and revenue and revenue > 0:
            metrics["service_delivery_efficiency"] = 1 - (expenses / revenue)
        
        # Get recurring revenue components
        recurring_concepts = [
            'us-gaap:ContractWithCustomerLiabilityRevenue',
            'us-gaap:RecurringRevenue',
            'us-gaap:SubscriptionRevenue'
        ]
        recurring = find_xbrl_tag(soup, recurring_concepts)
        if recurring and revenue and revenue > 0:
            metrics["recurring_revenue_ratio"] = recurring / revenue
            
        return metrics

    def validate_data(self, data: Dict[str, FinancialValue], profile) -> List[ValidationIssue]:
        """Validate service company metrics."""
        # Create a validator for service-specific rules
        validator = FinancialDataValidator()
        
        # Add service-specific validation rules
        rules = [
            ValidationRule(
                field="service_cost",
                description="Service costs should be less than 75% of revenue for healthy margins",
                level=ValidationLevel.WARNING,
                ratio_denominator="revenue",
                ratio_min=0,  # Any positive value
                ratio_max=0.75,
                required=True,  # This is a critical service company metric
                allow_zero=False,  # Service costs can't be zero
                allow_negative=False
            ),
            ValidationRule(
                field="revenue_per_employee_cost",
                description="Revenue should be at least 2x employee costs for profitability",
                level=ValidationLevel.WARNING,
                min_value=2.0,
                required=False,
                allow_zero=False,
                allow_negative=False
            ),
            ValidationRule(
                field="service_delivery_efficiency",
                description="Service delivery efficiency should be at least 25%",
                level=ValidationLevel.WARNING,
                min_value=0.25,
                required=False,
                allow_zero=False,
                allow_negative=False
            )
        ]
        
        # Add rules to validator
        for rule in rules:
            validator.add_rule(rule)
        
        # Call validate_data on the parent class first to include base rules
        issues = super().validate_data(data, profile)
        
        # Add service-specific validation issues
        issues.extend(validator.validate(data))
        return issues
