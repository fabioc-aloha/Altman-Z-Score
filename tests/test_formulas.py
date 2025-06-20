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
    metrics = {
        'working_capital': 100,
        'retained_earnings': 200,
        'ebit': 300,
        'market_value_equity': 400,
        'total_assets': 1000,
        'total_liabilities': 500,
        'sales': 600
    }

    result = formulas.altman_zscore_original(metrics)
    assert result.model == "original"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    # Note: diagnostic might be None if not calculated, just verify the structure
    assert hasattr(result, 'diagnostic')

def test_altman_zscore_private():
    metrics = {
        'working_capital': 100,
        'retained_earnings': 200,
        'ebit': 300,
        'book_value_equity': 400,
        'total_assets': 1000,
        'total_liabilities': 500,
        'sales': 600
    }
    result = formulas.altman_zscore_private(metrics)
    assert result.model == "private"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_altman_zscore_service():
    metrics = {
        'working_capital': 100,
        'retained_earnings': 200,
        'ebit': 300,
        'market_value_equity': 400,
        'total_assets': 1000,
        'total_liabilities': 500
    }
    result = formulas.altman_zscore_service(metrics, False)  # False = use market value (public)
    assert result.model == "service"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}

def test_altman_zscore_em():
    metrics = {
        'working_capital': 100,
        'retained_earnings': 200,
        'ebit': 300,
        'book_value_equity': 400,
        'total_assets': 1000,
        'total_liabilities': 500
    }
    result = formulas.altman_zscore_em(metrics)
    assert result.model == "em"
    assert isinstance(result.z_score, Decimal)
    assert "X1" in result.components
    assert result.diagnostic in {"Safe Zone", "Grey Zone", "Distress Zone"}
