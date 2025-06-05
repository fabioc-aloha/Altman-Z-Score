import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from decimal import Decimal
from altman_zscore.computation import formulas

class DummyZScoreResult:
    def __init__(self, z_score, model, components, diagnostic, thresholds):
        self.z_score = z_score
        self.model = model
        self.components = components
        self.diagnostic = diagnostic
        self.thresholds = thresholds

def test_altman_zscore_original():
    result = formulas.altman_zscore_original(
        working_capital=100,
        retained_earnings=200,
        ebit=300,
        market_value_equity=400,
        total_assets=1000,
        total_liabilities=500,
        sales=600,
    )
    assert result.model == "original"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_altman_zscore_private():
    result = formulas.altman_zscore_private(
        working_capital=100,
        retained_earnings=200,
        ebit=300,
        book_value_equity=400,
        total_assets=1000,
        total_liabilities=500,
        sales=600,
    )
    assert result.model == "private"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_altman_zscore_service():
    result = formulas.altman_zscore_service(
        working_capital=100,
        retained_earnings=200,
        ebit=300,
        equity=400,
        total_assets=1000,
        total_liabilities=500,
        model_key="service",
    )
    assert result.model == "service"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_altman_zscore_em():
    result = formulas.altman_zscore_em(
        working_capital=100,
        retained_earnings=200,
        ebit=300,
        book_value_equity=400,
        total_assets=1000,
        total_liabilities=500,
    )
    assert result.model == "em"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}
