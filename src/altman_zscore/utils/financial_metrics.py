"""
Financial metrics and ratio calculations for Altman Z-Score analysis.

Provides utilities for calculating financial ratios and metrics, including safe division and edge case handling for financial data.
"""

import logging
from decimal import Decimal
from typing import Dict, Optional

logger = logging.getLogger(__name__)


# Updated docstring for FinancialMetricsCalculator
class FinancialMetricsCalculator:
    """Calculator for financial metrics and ratios used in Z-Score analysis.

    Methods:
        safe_divide(numerator, denominator):
            Safely perform division, handling zero denominator.
        calculate_working_capital_ratio(current_assets, current_liabilities):
            Calculate working capital to total assets ratio.
        calculate_retained_earnings_ratio(retained_earnings, total_assets):
            Calculate retained earnings to total assets ratio.
        calculate_ebit_ratio(ebit, total_assets):
            Calculate EBIT to total assets ratio.
        calculate_equity_ratio(market_value_equity, total_liabilities):
            Calculate market value of equity to total liabilities ratio.
        calculate_sales_ratio(sales, total_assets):
            Calculate sales to total assets ratio.
        calculate_all_ratios(financial_data):
            Calculate all Z-score ratios from a dictionary of financial data.
    """

    @staticmethod
    def safe_divide(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
        """Safely perform division handling zero denominator.

        Args:
            numerator (Decimal): Division numerator.
            denominator (Decimal): Division denominator.

        Returns:
            Optional[Decimal]: Division result or None if denominator is zero or invalid input.

        Raises:
            ValueError: If inputs are not valid Decimal objects.
        """
        try:
            if denominator == 0:
                return None
            return numerator / denominator
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"Division error: {str(e)}")
            return None

    def calculate_working_capital_ratio(
        self, current_assets: Decimal, current_liabilities: Decimal
    ) -> Optional[Decimal]:
        """Calculate working capital to total assets ratio.

        Args:
            current_assets (Decimal): Current assets value.
            current_liabilities (Decimal): Current liabilities value.

        Returns:
            Optional[Decimal]: Ratio value or None if invalid.
        """
        working_capital = current_assets - current_liabilities
        total_assets = current_assets  # Assuming total_assets provided
        return self.safe_divide(working_capital, total_assets)

    def calculate_retained_earnings_ratio(self, retained_earnings: Decimal, total_assets: Decimal) -> Optional[Decimal]:
        """Calculate retained earnings to total assets ratio.

        Args:
            retained_earnings (Decimal): Retained earnings value.
            total_assets (Decimal): Total assets value.

        Returns:
            Optional[Decimal]: Ratio value or None if invalid.
        """
        return self.safe_divide(retained_earnings, total_assets)

    def calculate_ebit_ratio(self, ebit: Decimal, total_assets: Decimal) -> Optional[Decimal]:
        """Calculate EBIT to total assets ratio.

        Args:
            ebit (Decimal): EBIT (Earnings Before Interest and Taxes) value.
            total_assets (Decimal): Total assets value.

        Returns:
            Optional[Decimal]: Ratio value or None if invalid.
        """
        return self.safe_divide(ebit, total_assets)

    def calculate_equity_ratio(self, market_value_equity: Decimal, total_liabilities: Decimal) -> Optional[Decimal]:
        """Calculate market value of equity to total liabilities ratio.

        Args:
            market_value_equity (Decimal): Market value of equity.
            total_liabilities (Decimal): Total liabilities value.

        Returns:
            Optional[Decimal]: Ratio value or None if invalid.
        """
        return self.safe_divide(market_value_equity, total_liabilities)

    def calculate_sales_ratio(self, sales: Decimal, total_assets: Decimal) -> Optional[Decimal]:
        """Calculate sales to total assets ratio.

        Args:
            sales (Decimal): Sales value.
            total_assets (Decimal): Total assets value.

        Returns:
            Optional[Decimal]: Ratio value or None if invalid.
        """
        return self.safe_divide(sales, total_assets)

    def calculate_all_ratios(self, financial_data: Dict[str, Decimal]) -> Dict[str, Optional[Decimal]]:
        """Calculate all Z-score ratios from financial data.

        Args:
            financial_data (dict): Dictionary of financial values.

        Returns:
            dict: Dictionary of calculated ratios.

        Raises:
            ValueError: If required fields are missing from financial_data.
        """
        required_fields = {
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "total_assets",
            "ebit",
            "market_value_equity",
            "total_liabilities",
            "sales",
        }

        # Validate required fields
        missing_fields = required_fields - set(financial_data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        return {
            "working_capital_to_total_assets": self.calculate_working_capital_ratio(
                financial_data["current_assets"], financial_data["current_liabilities"]
            ),
            "retained_earnings_to_total_assets": self.calculate_retained_earnings_ratio(
                financial_data["retained_earnings"], financial_data["total_assets"]
            ),
            "ebit_to_total_assets": self.calculate_ebit_ratio(financial_data["ebit"], financial_data["total_assets"]),
            "market_value_equity_to_total_liabilities": self.calculate_equity_ratio(
                financial_data["market_value_equity"], financial_data["total_liabilities"]
            ),
            "sales_to_total_assets": self.calculate_sales_ratio(
                financial_data["sales"], financial_data["total_assets"]
            ),
        }
