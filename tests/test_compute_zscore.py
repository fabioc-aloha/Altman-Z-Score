"""Tests for the compute_zscore module."""
import pytest
from datetime import datetime
from altman_zscore import FinancialMetrics, ZScoreCalculator


@pytest.fixture
def sample_metrics():
    """Create sample financial metrics for testing."""
    return FinancialMetrics(
        current_assets=1000.0,
        current_liabilities=500.0,
        total_assets=2000.0,
        retained_earnings=800.0,
        ebit=300.0,
        total_liabilities=1000.0,
        sales=1500.0,
        market_value_equity=1500.0,
        date=datetime(2025, 5, 21)
    )


def test_financial_metrics_from_dict():
    """Test creating FinancialMetrics from a dictionary."""
    fin_dict = {
        "CA": 1000.0,
        "CL": 500.0,
        "TA": 2000.0,
        "RE": 800.0,
        "EBIT": 300.0,
        "TL": 1000.0,
        "Sales": 1500.0
    }
    mve = 1500.0
    date = datetime(2025, 5, 21)
    
    metrics = FinancialMetrics.from_dict(fin_dict, mve, date)
    
    assert metrics.current_assets == 1000.0
    assert metrics.current_liabilities == 500.0
    assert metrics.total_assets == 2000.0
    assert metrics.market_value_equity == 1500.0


def test_zscore_calculation(sample_metrics):
    """Test Z-score calculation."""
    calculator = ZScoreCalculator()
    components = calculator.compute_components(sample_metrics)
    
    # Working Capital Ratio (X1)
    assert components.working_capital_ratio == pytest.approx(0.25)  # (1000-500)/2000
    
    # Retained Earnings Ratio (X2)
    assert components.retained_earnings_ratio == pytest.approx(0.4)  # 800/2000
    
    # EBIT Ratio (X3)
    assert components.ebit_ratio == pytest.approx(0.15)  # 300/2000
    
    # Market Value Ratio (X4)
    assert components.market_value_ratio == pytest.approx(1.5)  # 1500/1000
    
    # Asset Turnover (X5)
    assert components.asset_turnover == pytest.approx(0.75)  # 1500/2000
    
    # Final Z-Score
    expected_z = (
        1.2 * 0.25 +  # X1
        1.4 * 0.4 +   # X2
        3.3 * 0.15 +  # X3
        0.6 * 1.5 +   # X4 
        1.0 * 0.75    # X5
    )
    assert components.z_score == pytest.approx(expected_z)
