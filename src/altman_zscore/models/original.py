"""
Original Altman Z-score model implementation for Altman Z-Score analysis.

Implements the original 1968 Z-score model, including coefficients, input validation, and Z-score calculation logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from .base import ModelMetrics, ModelType, ModelVersion, ZScoreModel

ORIGINAL_COEFFICIENTS = {
    "working_capital_to_total_assets": Decimal("1.2"),
    "retained_earnings_to_total_assets": Decimal("1.4"),
    "ebit_to_total_assets": Decimal("3.3"),
    "market_value_equity_to_total_liabilities": Decimal("0.6"),
    "sales_to_total_assets": Decimal("0.999"),  # Originally 1.0, adjusted for rounding
}


class OriginalZScoreModel(ZScoreModel):
    """Original Altman Z-score model (1968).

    Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅

    Where:
        X₁ = Working Capital / Total Assets
        X₂ = Retained Earnings / Total Assets
        X₃ = EBIT / Total Assets
        X₄ = Market Value of Equity / Total Liabilities
        X₅ = Sales / Total Assets

    Interpretation:
        Z > 2.99 - "Safe" Zone
        1.81 < Z < 2.99 - "Grey" Zone
        Z < 1.81 - "Distress" Zone
    """

    def __init__(self):
        """Initialize original Z-score model."""
        super().__init__(ModelType.ORIGINAL)

        # Add initial version
        self.add_version(
            ModelVersion(
                version="1.0.0",
                release_date=datetime(1968, 1, 1),
                changes=[
                    "Initial model implementation",
                    "Based on sample of 66 manufacturing companies",
                    "33 bankrupt and 33 non-bankrupt companies",
                    "Original coefficients from Altman (1968)",
                ],
                validation_metrics=ModelMetrics(
                    accuracy=0.95,
                    precision=0.94,
                    recall=0.97,
                    f1_score=0.95,
                    sample_size=66,
                    validation_period="1946-1965",
                ),
                min_data_requirements=list(ORIGINAL_COEFFICIENTS.keys()),
            )
        )

    def calculate_zscore(self, financial_data: Dict[str, Decimal]) -> float:
        """Calculate original Z-score.

        Args:
            financial_data (dict): Dictionary containing required financial ratios.

        Returns:
            float: Z-score value.

        Raises:
            ValueError: If input data is invalid or missing required metrics.
        """
        validation_errors = self.validate_input(financial_data)
        if validation_errors:
            raise ValueError(f"Invalid input data: {', '.join(validation_errors)}")

        zscore = Decimal("0")
        for metric, coefficient in ORIGINAL_COEFFICIENTS.items():
            zscore += coefficient * financial_data[metric]

        return float(zscore)

    def validate_input(self, financial_data: Dict[str, Decimal]) -> List[str]:
        """Validate input data against requirements.

        Args:
            financial_data (dict): Dictionary of financial metrics.

        Returns:
            list: List of validation error messages.
        """
        errors = []
        required_metrics = self.get_required_metrics()

        # Check for missing metrics
        for metric in required_metrics:
            if metric not in financial_data:
                errors.append(f"Missing required metric: {metric}")
                continue

            # Validate value is a number
            value = financial_data[metric]
            if not isinstance(value, (int, float, Decimal)):
                errors.append(f"Invalid value type for {metric}: {type(value)}")

        return errors

    def get_required_metrics(self) -> List[str]:
        """Get list of required financial metrics.

        Returns:
            list: List of required metric names.
        """
        return list(ORIGINAL_COEFFICIENTS.keys())
