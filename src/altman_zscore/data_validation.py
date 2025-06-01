"""
Financial data validation utilities for Altman Z-Score pipeline.

This module provides Pydantic-based validation and diagnostics for financial data
used in Z-Score computation. Handles missing fields, outliers, and edge-case reporting.

Note: This code follows PEP 8 style guidelines.
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
    """
    Validates financial data for Altman Z-Score computation.

    Methods:
        validate(q, industry=None): Validate a single quarter's data.
        validate_data(q, industry=None): Alias for validate.
        summarize_issues(issues): Summarize validation issues for diagnostics/reporting.
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
        Validate a single quarter's financial data.

        Args:
            q (dict): Financial data for a quarter
            industry (str, optional): Industry string for context
        Returns:
            list: List of validation issues (warnings/errors)
        """
        issues = []
        # 1. Required field check
        for field in self.REQUIRED_FIELDS:
            if field not in q or q[field] is None:
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue=f"Missing required field: {field}",
                        level=ValidationLevel.ERROR,
                    )
                )
        # 2. All-zero or all-missing check (edge case: empty quarter)
        nonzero_fields = [f for f in self.REQUIRED_FIELDS if q.get(f) not in (None, "", 0.0)]
        if len(nonzero_fields) == 0:
            issues.append(
                ValidationIssue(
                    field=None,
                    issue="All required fields are missing or zero (possible empty or placeholder quarter)",
                    level=ValidationLevel.ERROR,
                )
            )
        # 3. Suspicious value checks (edge cases)
        if q.get("total_assets") is not None and q["total_assets"] < 0:
            issues.append(
                ValidationIssue(
                    field="total_assets",
                    issue="Total assets is negative (suspicious)",
                    level=ValidationLevel.WARNING,
                    value=q["total_assets"],
                )
            )
        if q.get("sales") is not None and q["sales"] < 0:
            issues.append(
                ValidationIssue(
                    field="sales",
                    issue="Sales is negative (suspicious)",
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
                        issue="Total liabilities > 10x total assets (possible data error)",
                        level=ValidationLevel.WARNING,
                        value=ratio,
                    )
                )
        return issues

    def validate_data(self, q, industry=None):
        """
        Alias for validate().
        """
        return self.validate(q, industry)

    def summarize_issues(self, issues):
        """
        Return a summary string for edge-case diagnostics.

        Args:
            issues (list): List of validation issues
        Returns:
            str: Summary string for reporting
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
        Run consistency checks as described in ModelSelection.md pseudocode:
        - TA >= CA
        - TL >= CL
        - BVE ≈ TA - TL
        - Rounding discrepancies
        Returns:
            list: List of ValidationIssue (level=WARNING)
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
