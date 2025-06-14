"""
data_validation.py
-----------------
Financial data validation utilities for Altman Z-Score pipeline.

This module provides Pydantic-based validation and diagnostics for financial data
used in Z-Score computation. Handles missing fields, outliers, and edge-case reporting.

Classes:
    ValidationLevel (Enum): Severity level for validation issues.
    ValidationIssue: Represents a validation issue for a field.
    FinancialDataValidator: Validates financial data for Altman Z-Score computation.
"""

from enum import Enum
from altman_zscore.computation.constants import (
    ERROR_MSG_ALL_FIELDS_MISSING,
    ERROR_MSG_MISSING_FIELD,
    ERROR_MSG_NEGATIVE_ASSETS,
    ERROR_MSG_NEGATIVE_SALES,
    ERROR_MSG_LIABILITIES_RATIO,
)


class ValidationLevel(Enum):
    """
    Enum for severity level of validation issues.
    """
    ERROR = "ERROR"
    WARNING = "WARNING"


class ValidationIssue:
    """
    Represents a validation issue for a field in financial data.

    Attributes:
        field (str): Field name with the issue.
        issue (str): Description of the issue.
        level (ValidationLevel): Severity level (ERROR or WARNING).
        value (Any, optional): Value that triggered the issue.
        expected_range (Any, optional): Expected value range (if applicable).
    """

    def __init__(self, field, issue, level, value=None, expected_range=None):
        self.field = field
        self.issue = issue
        self.level = level
        self.value = value
        self.expected_range = expected_range


class FinancialDataValidator:
    """
    Validates financial data for Altman Z-Score computation.

    Methods:
        validate(q, industry=None): Validate a single quarter's data.
        validate_data(q, industry=None): Alias for validate.
        summarize_issues(issues): Summarize validation issues for diagnostics/reporting.
        check_consistency(q): Run consistency checks for financial data.
    """

    REQUIRED_FIELDS = [
        "total_assets",
        "current_assets",
        "current_liabilities",
        "retained_earnings",
        "ebit",
        "sales",
    ]

    def validate(self, q, industry=None):
        """
        Validate a single quarter's financial data for required fields, missing values, and suspicious values.

        Args:
            q (dict): Financial data for a quarter.
            industry (str, optional): Industry string for context.
        Returns:
            list: List of ValidationIssue (warnings/errors).
        """
        issues = []
        # 1. Required field check
        for field in self.REQUIRED_FIELDS:
            if field not in q or q[field] is None:
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue=ERROR_MSG_MISSING_FIELD.format(field=field),
                        level=ValidationLevel.ERROR,
                    )
                )
        # 2. All-zero or all-missing check (edge case: empty quarter)
        nonzero_fields = [f for f in self.REQUIRED_FIELDS if q.get(f) not in (None, "", 0.0)]
        if len(nonzero_fields) == 0:
            issues.append(
                ValidationIssue(
                    field=None,
                    issue=ERROR_MSG_ALL_FIELDS_MISSING,
                    level=ValidationLevel.ERROR,
                )
            )
        # 3. Suspicious value checks (edge cases)
        if q.get("total_assets") is not None and q["total_assets"] < 0:
            issues.append(
                ValidationIssue(
                    field="total_assets",
                    issue=ERROR_MSG_NEGATIVE_ASSETS,
                    level=ValidationLevel.WARNING,
                    value=q["total_assets"],
                )
            )
        if q.get("sales") is not None and q["sales"] < 0:
            issues.append(
                ValidationIssue(
                    field="sales",
                    issue=ERROR_MSG_NEGATIVE_SALES,
                    level=ValidationLevel.WARNING,
                    value=q["sales"],
                )
            )
        # 4. Extreme ratio checks (e.g., liabilities > 10x assets)
        if q.get("total_liabilities") is not None and q.get("total_assets") not in (None, 0.0):
            ratio = q["total_liabilities"] / q["total_assets"]
            if ratio > 10:
                issues.append(
                    ValidationIssue(
                        field="total_liabilities",
                        issue=ERROR_MSG_LIABILITIES_RATIO,
                        level=ValidationLevel.WARNING,
                        value=ratio,
                    )
                )
        return issues

    def validate_data(self, q, industry=None):
        """
        Alias for validate().

        Args:
            q (dict): Financial data for a quarter.
            industry (str, optional): Industry string for context.
        Returns:
            list: List of ValidationIssue (warnings/errors).
        """
        return self.validate(q, industry)

    def summarize_issues(self, issues):
        """
        Return a summary string for edge-case diagnostics.

        Args:
            issues (list): List of ValidationIssue.
        Returns:
            str: Summary string for reporting.
        """
        if not issues:
            return "No validation issues."
        lines = []
        for i in issues:
            prefix = "[ERROR]" if i.level == ValidationLevel.ERROR else "[WARN]"
            field = f"{i.field}: " if i.field else ""
            val = f" (value: {i.value})" if hasattr(i, "value") and i.value is not None else ""
            lines.append(f"{prefix} {field}{i.issue}{val}")
        return " | ".join(lines)

    def check_consistency(self, q):
        """
        Run consistency checks for financial data as described in ModelSelection.md pseudocode:
            - TA >= CA (Total Assets >= Current Assets)
            - TL >= CL (Total Liabilities >= Current Liabilities)
            - BVE ≈ TA - TL (Shareholders’ Equity ≈ Total Assets - Total Liabilities)
            - Rounding discrepancies (not implemented; raw values not always available)

        Args:
            q (dict): Financial data for a quarter.
        Returns:
            list: List of ValidationIssue (level=WARNING) for any detected inconsistencies.
        """
        issues = []
        # TA >= CA
        ta = q.get("total_assets")
        ca = q.get("current_assets")
        if ta is not None and ca is not None and ta < ca:
            issues.append(ValidationIssue(
                field="total_assets/current_assets",
                issue="Total Assets < Current Assets — check tags for TA or CA",
                level=ValidationLevel.WARNING,
                value=f"TA={ta}, CA={ca}"
            ))
        # TL >= CL
        tl = q.get("total_liabilities")
        cl = q.get("current_liabilities")
        if tl is not None and cl is not None and tl < cl:
            issues.append(ValidationIssue(
                field="total_liabilities/current_liabilities",
                issue="Total Liabilities < Current Liabilities — check tags for TL or CL",
                level=ValidationLevel.WARNING,
                value=f"TL={tl}, CL={cl}"
            ))
        # BVE ≈ TA - TL
        bve = q.get("book_value_equity")
        if ta is not None and tl is not None and bve is not None:
            equity_diff = abs(bve - (ta - tl))
            if equity_diff > 1_000_000:
                issues.append(ValidationIssue(
                    field="book_value_equity",
                    issue="Shareholders’ Equity mismatch: BVE vs. TA - TL",
                    level=ValidationLevel.WARNING,
                    value=f"BVE={bve}, TA-TL={ta-tl}, Diff={equity_diff}"
                ))
        # Rounding discrepancies (if raw and rounded available)
        # Not implemented here, as raw values are not always available in q
        return issues
