"""
Models module with Z-Score model variants and their calibrations.

This module defines various Z-Score models, their thresholds, and coefficients.
It includes methods for retrieving diagnostic information and specialized thresholds
for different company types and stages.

Note: This code follows PEP 8 style guidelines.
"""

from typing import Any, Dict, Optional
from decimal import Decimal
from .enums import CompanyStage, CompanyType
from .model_thresholds import ModelThresholds, ModelCoefficients, TechCalibration
from .zscore_model_base import ZScoreModel


class OriginalZScore(ZScoreModel):
    """Original Z-Score model for public manufacturing companies.

    Uses the original Altman Z-Score formula and thresholds for public manufacturing firms.
    """

    def __init__(self):
        """Initialize the original Z-Score model with default coefficients and thresholds."""
        self.coefficients = ModelCoefficients.original()
        self.thresholds = ModelThresholds.original()

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """
        Calculate the original Z-Score.

        Args:
            financial_data (Dict): Dictionary of required financial ratios.

        Returns:
            Decimal: The computed Z-Score.
        """
        return (
            self.coefficients.working_capital_to_assets * financial_data["working_capital_to_assets"]
            + self.coefficients.retained_earnings_to_assets * financial_data["retained_earnings_to_assets"]
            + self.coefficients.ebit_to_assets * financial_data["ebit_to_assets"]
            + self.coefficients.equity_to_liabilities * financial_data["equity_to_liabilities"]
            + self.coefficients.sales_to_assets * financial_data["sales_to_assets"]
        )

    def interpret_score(self, score: Decimal) -> str:
        """
        Interpret the Z-Score using original thresholds.

        Args:
            score (Decimal): The Z-Score to interpret.

        Returns:
            str: The risk zone label (Safe Zone, Grey Zone, Distress Zone).
        """
        if score > self.thresholds.safe_zone:
            return "Safe Zone"
        elif score > self.thresholds.distress_zone:
            return "Grey Zone"
        return "Distress Zone"


class TechZScore(ZScoreModel):
    """Specialized Z-Score model for technology companies.

    Applies tech-specific calibration and R&D intensity adjustments.
    """

    def __init__(self, calibration: TechCalibration):
        """
        Initialize the TechZScore model with a given calibration.

        Args:
            calibration (TechCalibration): Calibration object with coefficients and thresholds.
        """
        self.calibration = calibration

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """
        Calculate the tech-adjusted Z-Score.

        Args:
            financial_data (Dict): Dictionary of required financial ratios.

        Returns:
            Decimal: The computed Z-Score, with R&D intensity bonus if applicable.
        """
        base_score = (
            self.calibration.coefficients.working_capital_to_assets * financial_data["working_capital_to_assets"]
            + self.calibration.coefficients.retained_earnings_to_assets * financial_data["retained_earnings_to_assets"]
            + self.calibration.coefficients.ebit_to_assets * financial_data["ebit_to_assets"]
            + self.calibration.coefficients.equity_to_liabilities * financial_data["equity_to_liabilities"]
            + self.calibration.coefficients.sales_to_assets * financial_data["sales_to_assets"]
        )

        # Apply tech-specific adjustments
        rd_intensity = financial_data.get("rd_to_revenue", Decimal("0"))
        if rd_intensity > self.calibration.rd_intensity_threshold:
            base_score *= Decimal("1.1")  # Bonus for high R&D intensity

        return base_score

    def interpret_score(self, score: Decimal) -> str:
        """
        Interpret the Z-Score using tech-calibrated thresholds.

        Args:
            score (Decimal): The Z-Score to interpret.

        Returns:
            str: The risk zone label (Safe Zone, Grey Zone, Distress Zone).
        """
        if score > self.calibration.thresholds.safe_zone:
            return "Safe Zone"
        elif score > self.calibration.thresholds.distress_zone:
            return "Grey Zone"
        return "Distress Zone"
