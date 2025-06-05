"""
Dataclasses for Z-Score model thresholds, coefficients, and tech calibration.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

@dataclass
class ModelThresholds:
    safe_zone: Decimal
    grey_zone_upper: Decimal
    grey_zone_lower: Decimal
    distress_zone: Decimal

    def get_diagnostic(self, score: Decimal, company_type: Optional[str] = None) -> Dict[str, Any]:
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
        return cls(
            safe_zone=Decimal("2.99"),
            grey_zone_upper=Decimal("2.99"),
            grey_zone_lower=Decimal("1.81"),
            distress_zone=Decimal("1.81"),
        )

    @classmethod
    def private_company(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.90"),
            grey_zone_upper=Decimal("2.90"),
            grey_zone_lower=Decimal("1.23"),
            distress_zone=Decimal("1.23"),
        )

    @classmethod
    def non_manufacturing(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.60"),
            grey_zone_upper=Decimal("2.60"),
            grey_zone_lower=Decimal("1.10"),
            distress_zone=Decimal("1.10"),
        )

    @classmethod
    def tech_early_stage(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.20"),
            grey_zone_upper=Decimal("2.20"),
            grey_zone_lower=Decimal("1.40"),
            distress_zone=Decimal("1.40"),
        )

    @classmethod
    def tech_growth_stage(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.40"),
            grey_zone_upper=Decimal("2.40"),
            grey_zone_lower=Decimal("1.45"),
            distress_zone=Decimal("1.45"),
        )

    @classmethod
    def tech_mature_stage(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.60"),
            grey_zone_upper=Decimal("2.60"),
            grey_zone_lower=Decimal("1.50"),
            distress_zone=Decimal("1.50"),
        )

    @classmethod
    def saas_company(cls) -> "ModelThresholds":
        return cls(
            safe_zone=Decimal("2.50"),
            grey_zone_upper=Decimal("2.50"),
            grey_zone_lower=Decimal("1.50"),
            distress_zone=Decimal("1.50"),
        )

@dataclass
class ModelCoefficients:
    working_capital_to_assets: Decimal
    retained_earnings_to_assets: Decimal
    ebit_to_assets: Decimal
    equity_to_liabilities: Decimal
    sales_to_assets: Decimal

    @classmethod
    def original(cls) -> "ModelCoefficients":
        return cls(
            working_capital_to_assets=Decimal("1.2"),
            retained_earnings_to_assets=Decimal("1.4"),
            ebit_to_assets=Decimal("3.3"),
            equity_to_liabilities=Decimal("0.6"),
            sales_to_assets=Decimal("1.0"),
        )

    @classmethod
    def private_company(cls) -> "ModelCoefficients":
        return cls(
            working_capital_to_assets=Decimal("0.717"),
            retained_earnings_to_assets=Decimal("0.847"),
            ebit_to_assets=Decimal("3.107"),
            equity_to_liabilities=Decimal("0.420"),
            sales_to_assets=Decimal("0.998"),
        )

    @classmethod
    def non_manufacturing(cls) -> "ModelCoefficients":
        return cls(
            working_capital_to_assets=Decimal("6.56"),
            retained_earnings_to_assets=Decimal("3.26"),
            ebit_to_assets=Decimal("6.72"),
            equity_to_liabilities=Decimal("1.05"),
            sales_to_assets=Decimal("0"),
        )

@dataclass
class TechCalibration:
    rd_intensity_threshold: Decimal
    data_asset_factor: Decimal
    computing_efficiency_factor: Decimal
    customer_acquisition_factor: Decimal
    coefficients: ModelCoefficients
    thresholds: ModelThresholds

    @classmethod
    def saas(cls) -> "TechCalibration":
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
    def ai_ml(cls, stage) -> "TechCalibration":
        from .enums import CompanyStage
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
        return cls(
            rd_intensity_threshold=Decimal("0.10"),
            data_asset_factor=Decimal("1.0"),
            computing_efficiency_factor=Decimal("1.0"),
            customer_acquisition_factor=Decimal("1.0"),
            coefficients=ModelCoefficients.original(),
            thresholds=ModelThresholds.original(),
        )
