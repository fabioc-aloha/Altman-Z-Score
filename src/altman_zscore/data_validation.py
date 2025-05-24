"""
Data validation for Altman Z-Score pipeline (MVP scaffold).
"""

from enum import Enum


class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


class ValidationIssue:
    def __init__(self, field, issue, level, value=None, expected_range=None):
        self.field = field
        self.issue = issue
        self.level = level
        self.value = value
        self.expected_range = expected_range


class FinancialDataValidator:
    REQUIRED_FIELDS = [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "ebit",
        "sales",
    ]

    def validate(self, q, industry=None):
        issues = []
        for field in self.REQUIRED_FIELDS:
            if field not in q or q[field] is None:
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue=f"Missing required field: {field}",
                        level=ValidationLevel.ERROR,
                    )
                )
        return issues

    def validate_data(self, q, industry=None):
        return self.validate(q, industry)
