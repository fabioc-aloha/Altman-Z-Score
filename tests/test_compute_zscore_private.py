import pytest
from altman_zscore.compute_zscore import altman_zscore_private

def test_private_model_example():
    # Example values for a private manufacturing firm (from literature, e.g., Altman 1983)
    # These are illustrative; replace with real case-study values for full validation.
    current_assets = 1000.0
    current_liabilities = 400.0
    working_capital = current_assets - current_liabilities  # 600.0
    retained_earnings = 200.0
    ebit = 150.0
    book_value_equity = 500.0
    total_assets = 1200.0
    total_liabilities = 700.0
    sales = 900.0

    result = altman_zscore_private(
        working_capital=working_capital,
        retained_earnings=retained_earnings,
        ebit=ebit,
        book_value_equity=book_value_equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        sales=sales
    )
    # Check component ratios (rounded)
    assert abs(result.components['X1'] - 0.5) < 0.01
    assert abs(result.components['X2'] - 0.167) < 0.01
    assert abs(result.components['X3'] - 0.125) < 0.01
    assert abs(result.components['X4'] - 0.714) < 0.01
    assert abs(result.components['X5'] - 0.75) < 0.01
    # Check Z-score (manual calculation)
    expected_z = 0.717*0.5 + 0.847*0.167 + 3.107*0.125 + 0.420*0.714 + 0.998*0.75
    assert abs(result.z_score - expected_z) < 0.01
    # Check diagnostic
    # For these values, the Z-score falls in the Grey Zone (1.23 < z < 2.9)
    assert result.diagnostic == 'Grey Zone'
