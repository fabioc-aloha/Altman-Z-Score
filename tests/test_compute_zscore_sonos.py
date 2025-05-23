import pytest
from altman_zscore.compute_zscore import altman_zscore_original

def test_sonos_q1_fy2025():
    # Sonos Q1 FY2025 values from OneStockAnalysis.md
    current_assets = 453.0
    current_liabilities = 286.9
    working_capital = current_assets - current_liabilities  # 166.1
    retained_earnings = -12.8
    ebit = -69.7
    market_value_equity = 1031.5
    total_assets = 453.0
    total_liabilities = 344.5
    sales = 259.8

    result = altman_zscore_original(
        working_capital=working_capital,
        retained_earnings=retained_earnings,
        ebit=ebit,
        market_value_equity=market_value_equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        sales=sales
    )
    # Check component ratios
    assert abs(result.components['X1'] - 0.366) < 0.001
    assert abs(result.components['X2'] - -0.028) < 0.001
    assert abs(result.components['X3'] - -0.154) < 0.001
    assert abs(result.components['X4'] - 2.994) < 0.001
    assert abs(result.components['X5'] - 0.574) < 0.001
    # Check Z-score
    assert abs(result.z_score - 2.262) < 0.01
    # Check diagnostic
    assert result.diagnostic == 'Grey Zone'
