"""
Models module with Z-Score model variants and their calibrations.

This module defines various Z-Score models, their thresholds, and coefficients.
It includes methods for retrieving diagnostic information and specialized thresholds
for different company types and stages.

Note: This code follows PEP 8 style guidelines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Dict, Optional


class CompanyStage(Enum):
    """Enum for company lifecycle stages"""

    EARLY = auto()
    GROWTH = auto()
    MATURE = auto()


class CompanyType(Enum):
    """Enum for company types"""

    PUBLIC = auto()
    PRIVATE = auto()


@dataclass
class ModelThresholds:
    """
    Thresholds for interpreting Z-Score results.

    Attributes:
        safe_zone (Decimal): Threshold for the safe zone.
        grey_zone_upper (Decimal): Upper threshold for the grey zone.
        grey_zone_lower (Decimal): Lower threshold for the grey zone.
        distress_zone (Decimal): Threshold for the distress zone.

    Methods:
        get_diagnostic(score, company_type):
            Provides diagnostic information based on the Z-Score.
        original():
            Returns thresholds for the original Z-Score model.
        private_company():
            Returns thresholds for private companies.
        non_manufacturing():
            Returns thresholds for non-manufacturing companies.
        tech_early_stage():
            Returns thresholds for early-stage tech companies.
        tech_growth_stage():
            Returns thresholds for growth-stage tech companies.
        tech_mature_stage():
            Returns thresholds for mature tech companies.
        saas_company():
            Returns thresholds for SaaS companies.
    """

    safe_zone: Decimal
    grey_zone_upper: Decimal
    grey_zone_lower: Decimal
    distress_zone: Decimal

    def get_diagnostic(self, score: Decimal, company_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed diagnostic information based on Z-Score and company type.

        Args:
            score: The calculated Z-Score
            company_type: Optional company type for specialized interpretation

        Returns:
            Dict containing diagnostic status and interpretation
        """
        if score > self.safe_zone:
            status = "Safe Zone"
            interpretation = "Strong financial health with low probability of distress."
        elif score > self.distress_zone:
            status = "Grey Zone"
            interpretation = "Some signs of financial stress. Requires monitoring."
        else:
            status = "Distress Zone"
            interpretation = "High risk of financial distress. Immediate action required."

        return {
            "status": status,
            "interpretation": interpretation,
            "score": score,
            "safe_threshold": self.safe_zone,
            "distress_threshold": self.distress_zone,
            "company_type": company_type,
        }

    @classmethod
    def original(cls) -> "ModelThresholds":
        """Original Z-Score thresholds"""
        return cls(
            safe_zone=Decimal("2.99"),
            grey_zone_upper=Decimal("2.99"),
            grey_zone_lower=Decimal("1.81"),
            distress_zone=Decimal("1.81"),
        )

    @classmethod
    def private_company(cls) -> "ModelThresholds":
        """Z'-Score thresholds for private companies"""
        return cls(
            safe_zone=Decimal("2.90"),
            grey_zone_upper=Decimal("2.90"),
            grey_zone_lower=Decimal("1.23"),
            distress_zone=Decimal("1.23"),
        )

    @classmethod
    def non_manufacturing(cls) -> "ModelThresholds":
        """Z"-Score thresholds for non-manufacturing companies"""
        return cls(
            safe_zone=Decimal("2.60"),
            grey_zone_upper=Decimal("2.60"),
            grey_zone_lower=Decimal("1.10"),
            distress_zone=Decimal("1.10"),
        )

    @classmethod
    def tech_early_stage(cls) -> "ModelThresholds":
        """Thresholds for early-stage tech companies"""
        return cls(
            safe_zone=Decimal("2.20"),
            grey_zone_upper=Decimal("2.20"),
            grey_zone_lower=Decimal("1.40"),
            distress_zone=Decimal("1.40"),
        )

    @classmethod
    def tech_growth_stage(cls) -> "ModelThresholds":
        """Thresholds for growth-stage tech companies"""
        return cls(
            safe_zone=Decimal("2.40"),
            grey_zone_upper=Decimal("2.40"),
            grey_zone_lower=Decimal("1.45"),
            distress_zone=Decimal("1.45"),
        )

    @classmethod
    def tech_mature_stage(cls) -> "ModelThresholds":
        """Thresholds for mature tech companies"""
        return cls(
            safe_zone=Decimal("2.60"),
            grey_zone_upper=Decimal("2.60"),
            grey_zone_lower=Decimal("1.50"),
            distress_zone=Decimal("1.50"),
        )

    @classmethod
    def saas_company(cls) -> "ModelThresholds":
        """Thresholds for SaaS companies"""
        return cls(
            safe_zone=Decimal("2.50"),
            grey_zone_upper=Decimal("2.50"),
            grey_zone_lower=Decimal("1.50"),
            distress_zone=Decimal("1.50"),
        )


@dataclass
class ModelCoefficients:
    """
    Coefficients for Z-Score calculation.

    Attributes:
        working_capital_to_assets (Decimal): Coefficient for working capital to assets.
        retained_earnings_to_assets (Decimal): Coefficient for retained earnings to assets.
        ebit_to_assets (Decimal): Coefficient for EBIT to assets.
        equity_to_liabilities (Decimal): Coefficient for equity to liabilities.
        sales_to_assets (Decimal): Coefficient for sales to assets.

    Methods:
        original():
            Returns coefficients for the original Z-Score model.
        private_company():
            Returns coefficients for private companies.
        non_manufacturing():
            Returns coefficients for non-manufacturing companies.
    """

    working_capital_to_assets: Decimal
    retained_earnings_to_assets: Decimal
    ebit_to_assets: Decimal
    equity_to_liabilities: Decimal
    sales_to_assets: Decimal

    @classmethod
    def original(cls) -> "ModelCoefficients":
        """Original Z-Score coefficients"""
        return cls(
            working_capital_to_assets=Decimal("1.2"),
            retained_earnings_to_assets=Decimal("1.4"),
            ebit_to_assets=Decimal("3.3"),
            equity_to_liabilities=Decimal("0.6"),
            sales_to_assets=Decimal("1.0"),
        )

    @classmethod
    def private_company(cls) -> "ModelCoefficients":
        """Z'-Score coefficients for private companies"""
        return cls(
            working_capital_to_assets=Decimal("0.717"),
            retained_earnings_to_assets=Decimal("0.847"),
            ebit_to_assets=Decimal("3.107"),
            equity_to_liabilities=Decimal("0.420"),
            sales_to_assets=Decimal("0.998"),
        )

    @classmethod
    def non_manufacturing(cls) -> "ModelCoefficients":
        """Z"-Score coefficients for non-manufacturing companies"""
        return cls(
            working_capital_to_assets=Decimal("6.56"),
            retained_earnings_to_assets=Decimal("3.26"),
            ebit_to_assets=Decimal("6.72"),
            equity_to_liabilities=Decimal("1.05"),
            sales_to_assets=Decimal("0"),  # Not used in this model
        )


@dataclass
class TechCalibration:
    """Tech-specific calibration parameters"""

    rd_intensity_threshold: Decimal
    data_asset_factor: Decimal
    computing_efficiency_factor: Decimal
    customer_acquisition_factor: Decimal
    coefficients: ModelCoefficients
    thresholds: ModelThresholds

    @classmethod
    def saas(cls) -> "TechCalibration":
        """Calibration for SaaS companies"""
        return cls(
            rd_intensity_threshold=Decimal("0.15"),
            data_asset_factor=Decimal("1.2"),
            computing_efficiency_factor=Decimal("1.1"),
            customer_acquisition_factor=Decimal("0.9"),
            coefficients=ModelCoefficients.non_manufacturing(),
            thresholds=ModelThresholds(
                safe_zone=Decimal("2.50"),
                grey_zone_upper=Decimal("2.50"),
                grey_zone_lower=Decimal("1.50"),
                distress_zone=Decimal("1.50"),
            ),
        )

    @classmethod
    def ai_ml(cls, stage: CompanyStage) -> "TechCalibration":
        """Calibration for AI/ML companies based on company stage"""
        base = cls(
            rd_intensity_threshold=Decimal("0.20"),
            data_asset_factor=Decimal("1.5"),
            computing_efficiency_factor=Decimal("1.3"),
            customer_acquisition_factor=Decimal("0.8"),
            coefficients=ModelCoefficients.non_manufacturing(),
            thresholds=ModelThresholds(
                safe_zone=Decimal("2.20"),
                grey_zone_upper=Decimal("2.20"),
                grey_zone_lower=Decimal("1.40"),
                distress_zone=Decimal("1.40"),
            ),
        )

        if stage == CompanyStage.GROWTH:
            base.thresholds = ModelThresholds(
                safe_zone=Decimal("2.40"),
                grey_zone_upper=Decimal("2.40"),
                grey_zone_lower=Decimal("1.45"),
                distress_zone=Decimal("1.45"),
            )
        elif stage == CompanyStage.MATURE:
            base.thresholds = ModelThresholds(
                safe_zone=Decimal("2.60"),
                grey_zone_upper=Decimal("2.60"),
                grey_zone_lower=Decimal("1.50"),
                distress_zone=Decimal("1.50"),
            )

        return base

    @classmethod
    def hardware(cls) -> "TechCalibration":
        """Calibration for hardware tech companies"""
        return cls(
            rd_intensity_threshold=Decimal("0.10"),
            data_asset_factor=Decimal("1.0"),
            computing_efficiency_factor=Decimal("1.0"),
            customer_acquisition_factor=Decimal("1.0"),
            coefficients=ModelCoefficients.original(),
            thresholds=ModelThresholds.original(),
        )


class ZScoreModel(ABC):
    """Abstract base class for Z-Score models"""

    @abstractmethod
    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the Z-Score for given financial data"""

    @abstractmethod
    def interpret_score(self, score: Decimal) -> str:
        """Interpret the calculated Z-Score"""


class OriginalZScore(ZScoreModel):
    """Original Z-Score model for public manufacturing companies"""

    def __init__(self):
        self.coefficients = ModelCoefficients.original()
        self.thresholds = ModelThresholds.original()

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the original Z-Score"""
        return (
            self.coefficients.working_capital_to_assets * financial_data["working_capital_to_assets"]
            + self.coefficients.retained_earnings_to_assets * financial_data["retained_earnings_to_assets"]
            + self.coefficients.ebit_to_assets * financial_data["ebit_to_assets"]
            + self.coefficients.equity_to_liabilities * financial_data["equity_to_liabilities"]
            + self.coefficients.sales_to_assets * financial_data["sales_to_assets"]
        )

    def interpret_score(self, score: Decimal) -> str:
        """Interpret the Z-Score using original thresholds"""
        if score > self.thresholds.safe_zone:
            return "Safe Zone"
        elif score > self.thresholds.distress_zone:
            return "Grey Zone"
        return "Distress Zone"


class TechZScore(ZScoreModel):
    """Specialized Z-Score model for technology companies"""

    def __init__(self, calibration: TechCalibration):
        self.calibration = calibration

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the tech-adjusted Z-Score"""
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
        """Interpret the Z-Score using tech-calibrated thresholds"""
        if score > self.calibration.thresholds.safe_zone:
            return "Safe Zone"
        elif score > self.calibration.thresholds.distress_zone:
            return "Grey Zone"
        return "Distress Zone"
