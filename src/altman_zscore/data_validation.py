"""Data validation module for Altman Z-Score analysis."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Set, Union
from enum import Enum
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationRule:
    """Definition of a validation rule."""
    field: str
    description: str
    level: ValidationLevel
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = True
    allow_zero: bool = False
    allow_negative: bool = False
    ratio_denominator: Optional[str] = None  # For ratio validations
    ratio_min: Optional[float] = None
    ratio_max: Optional[float] = None
    industry_specific: bool = False

@dataclass
class ValidationIssue:
    """Represents a validation issue found in the data."""
    field: str
    issue: str
    level: ValidationLevel
    value: Optional[Union[float, Decimal]] = None
    expected_range: Optional[str] = None

class FinancialDataValidator:
    """Validates financial data for Z-score calculation."""
    
    def __init__(self):
        """Initialize validator with default rules."""
        self.rules = self._get_default_rules()
    
    def add_rule(self, rule: ValidationRule):
        """Add a custom validation rule.
        
        Args:
            rule: The validation rule to add
        """
        self.rules.append(rule)

    def _get_default_rules(self) -> List[ValidationRule]:
        """Get default validation rules."""
        return [
            # Asset-related rules
            ValidationRule(
                field="total_assets",
                description="Total assets must be positive",
                level=ValidationLevel.ERROR,
                min_value=0,
                allow_zero=False
            ),
            ValidationRule(
                field="current_assets",
                description="Current assets must be non-negative",
                level=ValidationLevel.ERROR,
                min_value=0,
                allow_zero=True
            ),
            
            # Liability rules
            ValidationRule(
                field="total_liabilities",
                description="Total liabilities must be positive",
                level=ValidationLevel.ERROR,
                min_value=0,
                allow_zero=False
            ),
            ValidationRule(
                field="current_liabilities",
                description="Current liabilities must be non-negative",
                level=ValidationLevel.ERROR,
                min_value=0,
                allow_zero=True
            ),
            
            # Income/Earnings rules
            ValidationRule(
                field="retained_earnings",
                description="Retained earnings validation",
                level=ValidationLevel.WARNING,
                allow_negative=True
            ),
            ValidationRule(
                field="ebit",
                description="EBIT validation",
                level=ValidationLevel.WARNING,
                allow_negative=True
            ),
            
            # Ratio validations
            ValidationRule(
                field="working_capital",
                description="Working capital ratio",
                level=ValidationLevel.WARNING,
                ratio_denominator="total_assets",
                ratio_min=-0.5,
                ratio_max=0.8,
                allow_negative=True
            ),
            ValidationRule(
                field="equity_ratio",
                description="Equity to assets ratio",
                level=ValidationLevel.WARNING,
                ratio_min=0,
                ratio_max=1,
                allow_negative=False
            )
        ]
    
    def validate_data(
        self, 
        data: Dict[str, Union[float, Decimal]],
        industry: Optional[str] = None
    ) -> List[ValidationIssue]:
        """
        Validate financial data against rules.
        
        Args:
            data: Dictionary of financial data
            industry: Optional industry for industry-specific rules
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check required fields
        missing_fields = self._check_required_fields(data)
        issues.extend(missing_fields)
        
        # Value validations
        value_issues = self._validate_values(data)
        issues.extend(value_issues)
        
        # Ratio validations
        ratio_issues = self._validate_ratios(data)
        issues.extend(ratio_issues)
        
        # Industry-specific validations
        if industry:
            industry_issues = self._validate_industry_specific(data, industry)
            issues.extend(industry_issues)
            
        return issues
    
    def validate(self, data: Dict[str, Union[float, Decimal]]) -> List[ValidationIssue]:
        """Validate financial data against defined rules.
        
        Args:
            data: Dictionary of financial data to validate
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check all rules
        for rule in self.rules:
            # Skip if field is not required and not present
            if not rule.required and rule.field not in data:
                continue
                
            # Get field value
            value = data.get(rule.field)
            if rule.required and value is None:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Required field {rule.field} is missing",
                    level=ValidationLevel.ERROR
                ))
                continue
                
            # Skip further validation if value is None
            if value is None:
                continue
                
            # Convert to float for comparison
            try:
                float_value = float(value)
            except (TypeError, ValueError):
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Value {value} for field {rule.field} cannot be converted to number",
                    level=ValidationLevel.ERROR,
                    value=value
                ))
                continue

            # Check ratio validation if defined
            if rule.ratio_denominator and rule.ratio_denominator in data:
                denom_value = float(data[rule.ratio_denominator])
                if denom_value != 0:  # Avoid division by zero
                    ratio = float_value / denom_value
                    
                    if rule.ratio_min is not None and ratio < rule.ratio_min:
                        issues.append(ValidationIssue(
                            field=rule.field,
                            issue=f"{rule.field} ratio {ratio:.2f} is below minimum of {rule.ratio_min:.2f}",
                            level=rule.level,
                            value=value,
                            expected_range=f">= {rule.ratio_min}"
                        ))
                        
                    if rule.ratio_max is not None and ratio > rule.ratio_max:
                        issues.append(ValidationIssue(
                            field=rule.field,
                            issue=f"{rule.field} ratio {ratio:.2f} is above maximum of {rule.ratio_max:.2f}",
                            level=rule.level,
                            value=value,
                            expected_range=f"<= {rule.ratio_max}"
                        ))
            
            # Check absolute value validation if defined
            else:
                if not rule.allow_negative and float_value < 0:
                    issues.append(ValidationIssue(
                        field=rule.field,
                        issue=f"{rule.field} cannot be negative",
                        level=rule.level,
                        value=value,
                        expected_range=">= 0"
                    ))
                
                if not rule.allow_zero and float_value == 0:
                    issues.append(ValidationIssue(
                        field=rule.field,
                        issue=f"{rule.field} cannot be zero",
                        level=rule.level,
                        value=value,
                        expected_range="!= 0"
                    ))
                    
                if rule.min_value is not None and float_value < rule.min_value:
                    issues.append(ValidationIssue(
                        field=rule.field,
                        issue=f"{rule.field} value {float_value:.2f} is below minimum of {rule.min_value:.2f}",
                        level=rule.level,
                        value=value,
                        expected_range=f">= {rule.min_value}"
                    ))
                    
                if rule.max_value is not None and float_value > rule.max_value:
                    issues.append(ValidationIssue(
                        field=rule.field,
                        issue=f"{rule.field} value {float_value:.2f} is above maximum of {rule.max_value:.2f}",
                        level=rule.level,
                        value=value,
                        expected_range=f"<= {rule.max_value}"
                    ))
                continue
                
            # Check for non-negative constraint
            if not rule.allow_negative and float_value < 0:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Field {rule.field} cannot be negative",
                    level=rule.level,
                    value=value
                ))
                
            # Check for non-zero constraint
            if not rule.allow_zero and float_value == 0:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Field {rule.field} cannot be zero",
                    level=rule.level,
                    value=value
                ))
                
            # Check minimum value
            if rule.min_value is not None and float_value < rule.min_value:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Field {rule.field} is below minimum value {rule.min_value}",
                    level=rule.level,
                    value=value,
                    expected_range=f">= {rule.min_value}"
                ))
                
            # Check maximum value
            if rule.max_value is not None and float_value > rule.max_value:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Field {rule.field} is above maximum value {rule.max_value}",
                    level=rule.level,
                    value=value,
                    expected_range=f"<= {rule.max_value}"
                ))
                
            # Check ratio constraints
            if rule.ratio_denominator is not None:
                denominator = data.get(rule.ratio_denominator)
                if denominator is not None and float(denominator) != 0:
                    ratio = float_value / float(denominator)
                    
                    if rule.ratio_min is not None and ratio < rule.ratio_min:
                        issues.append(ValidationIssue(
                            field=rule.field,
                            issue=f"Ratio of {rule.field} to {rule.ratio_denominator} ({ratio:.2f}) is below minimum {rule.ratio_min}",
                            level=rule.level,
                            value=ratio,
                            expected_range=f">= {rule.ratio_min}"
                        ))
                        
                    if rule.ratio_max is not None and ratio > rule.ratio_max:
                        issues.append(ValidationIssue(
                            field=rule.field,
                            issue=f"Ratio of {rule.field} to {rule.ratio_denominator} ({ratio:.2f}) is above maximum {rule.ratio_max}",
                            level=rule.level,
                            value=ratio,
                            expected_range=f"<= {rule.ratio_max}"
                        ))
                        
        return issues
    
    def _check_required_fields(
        self, 
        data: Dict[str, Union[float, Decimal]]
    ) -> List[ValidationIssue]:
        """Check for required fields in the data."""
        issues = []
        required_fields = {rule.field for rule in self.rules if rule.required}
        
        for field in required_fields:
            if field not in data or data[field] is None:
                issues.append(ValidationIssue(
                    field=field,
                    issue=f"Required field {field} is missing",
                    level=ValidationLevel.ERROR
                ))
                
        return issues
    
    def _validate_values(
        self, 
        data: Dict[str, Union[float, Decimal]]
    ) -> List[ValidationIssue]:
        """Validate individual field values."""
        issues = []
        
        for rule in self.rules:
            value = data.get(rule.field)
            if value is None:
                continue
                
            # Convert to float for comparison
            try:
                value_float = float(value)
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Invalid value format for {rule.field}",
                    level=ValidationLevel.ERROR,
                    value=value
                ))
                continue
                
            # Check minimum value
            if rule.min_value is not None and value_float < rule.min_value:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Value below minimum threshold",
                    level=rule.level,
                    value=value,
                    expected_range=f">= {rule.min_value}"
                ))
                
            # Check maximum value
            if rule.max_value is not None and value_float > rule.max_value:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Value above maximum threshold",
                    level=rule.level,
                    value=value,
                    expected_range=f"<= {rule.max_value}"
                ))
                
            # Check zero value
            if not rule.allow_zero and value_float == 0:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Zero value not allowed",
                    level=rule.level,
                    value=value
                ))
                
            # Check negative value
            if not rule.allow_negative and value_float < 0:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Negative value not allowed",
                    level=rule.level,
                    value=value
                ))
                
        return issues
    
    def _validate_ratios(
        self, 
        data: Dict[str, Union[float, Decimal]]
    ) -> List[ValidationIssue]:
        """Validate financial ratios."""
        issues = []
        
        for rule in self.rules:
            if not rule.ratio_denominator:
                continue
                
            numerator = data.get(rule.field)
            denominator = data.get(rule.ratio_denominator)
            
            if numerator is None or denominator is None:
                continue
                
            try:
                ratio = float(numerator) / float(denominator)
            except (ZeroDivisionError, ValueError, TypeError):
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Invalid ratio calculation",
                    level=ValidationLevel.ERROR
                ))
                continue
                
            if rule.ratio_min is not None and ratio < rule.ratio_min:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Ratio below minimum threshold",
                    level=rule.level,
                    value=ratio,
                    expected_range=f">= {rule.ratio_min}"
                ))
                
            if rule.ratio_max is not None and ratio > rule.ratio_max:
                issues.append(ValidationIssue(
                    field=rule.field,
                    issue=f"Ratio above maximum threshold",
                    level=rule.level,
                    value=ratio,
                    expected_range=f"<= {rule.ratio_max}"
                ))
                
        return issues
    
    def _validate_industry_specific(
        self,
        data: Dict[str, Union[float, Decimal]],
        industry: str
    ) -> List[ValidationIssue]:
        """
        Apply industry-specific validation rules.
        
        Args:
            data: Financial data dictionary
            industry: Industry classification
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if industry.upper() in ["TECH", "SOFTWARE"]:
            # Technology company specific rules
            issues.extend(self._validate_tech_company(data))
        elif industry.upper() in ["MANUFACTURING"]:
            # Manufacturing company specific rules
            issues.extend(self._validate_manufacturing(data))
            
        return issues
    
    def _validate_tech_company(
        self, 
        data: Dict[str, Union[float, Decimal]]
    ) -> List[ValidationIssue]:
        """Validate technology company specific metrics."""
        issues = []
        
        # Check R&D spending
        rd_expense = data.get("research_and_development_expense", 0)
        revenue = data.get("revenue", 0)
        
        if rd_expense and revenue:
            try:
                rd_ratio = float(rd_expense) / float(revenue)
                if rd_ratio < 0.05:  # Less than 5% R&D spending
                    issues.append(ValidationIssue(
                        field="research_and_development_expense",
                        issue="Low R&D spending for tech company",
                        level=ValidationLevel.WARNING,
                        value=rd_ratio,
                        expected_range=">= 0.05"
                    ))
            except (ZeroDivisionError, ValueError, TypeError):
                pass
                
        return issues
    
    def _validate_manufacturing(
        self, 
        data: Dict[str, Union[float, Decimal]]
    ) -> List[ValidationIssue]:
        """Validate manufacturing company specific metrics."""
        issues = []
        
        # Check inventory levels
        inventory = data.get("inventory", 0)
        total_assets = data.get("total_assets", 0)
        
        if inventory and total_assets:
            try:
                inventory_ratio = float(inventory) / float(total_assets)
                if inventory_ratio < 0.1:  # Less than 10% inventory
                    issues.append(ValidationIssue(
                        field="inventory",
                        issue="Low inventory for manufacturing company",
                        level=ValidationLevel.WARNING,
                        value=inventory_ratio,
                        expected_range=">= 0.1"
                    ))
            except (ZeroDivisionError, ValueError, TypeError):
                pass
                
        return issues
