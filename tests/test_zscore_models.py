import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from decimal import Decimal
from altman_zscore.enums import CompanyStage, CompanyType
from altman_zscore.model_thresholds import ModelThresholds, ModelCoefficients, TechCalibration
from altman_zscore.zscore_model_base import ZScoreModel
from altman_zscore.zscore_models import OriginalZScore, TechZScore

def test_model_thresholds_diagnostics():
    thresholds = ModelThresholds.original()
    result = thresholds.get_diagnostic(Decimal("3.0"))
    assert result["status"] == "Safe Zone"
    result = thresholds.get_diagnostic(Decimal("2.0"))
    assert result["status"] == "Grey Zone"
    result = thresholds.get_diagnostic(Decimal("1.0"))
    assert result["status"] == "Distress Zone"

def test_model_coefficients_original():
    coeffs = ModelCoefficients.original()
    assert coeffs.working_capital_to_assets == Decimal("1.2")
    assert coeffs.sales_to_assets == Decimal("1.0")

def test_tech_calibration_saas():
    cal = TechCalibration.saas()
    assert cal.coefficients.sales_to_assets == Decimal("0")
    assert cal.thresholds.safe_zone == Decimal("2.50")

def test_original_zscore():
    model = OriginalZScore()
    data = {
        "working_capital_to_assets": Decimal("1.0"),
        "retained_earnings_to_assets": Decimal("1.0"),
        "ebit_to_assets": Decimal("1.0"),
        "equity_to_liabilities": Decimal("1.0"),
        "sales_to_assets": Decimal("1.0"),
    }
    score = model.calculate_zscore(data)
    assert isinstance(score, Decimal)
    assert model.interpret_score(score) in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_tech_zscore():
    cal = TechCalibration.saas()
    model = TechZScore(cal)
    data = {
        "working_capital_to_assets": Decimal("1.0"),
        "retained_earnings_to_assets": Decimal("1.0"),
        "ebit_to_assets": Decimal("1.0"),
        "equity_to_liabilities": Decimal("1.0"),
        "sales_to_assets": Decimal("1.0"),
        "rd_to_revenue": Decimal("0.2"),
    }
    score = model.calculate_zscore(data)
    assert isinstance(score, Decimal)
    assert model.interpret_score(score) in {"Safe Zone", "Grey Zone", "Distress Zone"}
