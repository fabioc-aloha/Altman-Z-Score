import pytest
from altman_zscore.compute_zscore import altman_zscore_private

test_cases = [
    # (current_assets, current_liabilities, retained_earnings, ebit, book_value_equity, total_assets, total_liabilities, sales, expected_diagnostic)
    # Case 1: Safe Zone (high profitability, strong equity)
    (2000.0, 500.0, 800.0, 600.0, 1500.0, 2500.0, 1000.0, 2000.0, 'Safe Zone'),
    # Case 2: Grey Zone (moderate profitability, moderate equity)
    (1200.0, 600.0, 200.0, 100.0, 400.0, 1600.0, 900.0, 1000.0, 'Grey Zone'),
    # Case 3: Distress Zone (low profitability, low equity)
    (800.0, 700.0, -100.0, -50.0, 50.0, 1000.0, 950.0, 400.0, 'Distress Zone'),
    # Case 4: Borderline Safe/Grey (just above safe threshold)
    (1500.0, 700.0, 300.0, 200.0, 800.0, 1800.0, 1000.0, 1200.0, 'Safe Zone'),
    # Case 5: Borderline Grey/Distress (just above distress threshold)
    (1000.0, 800.0, 50.0, 20.0, 100.0, 1200.0, 1100.0, 300.0, 'Grey Zone'),
]

@pytest.mark.parametrize(
    "current_assets,current_liabilities,retained_earnings,ebit,book_value_equity,total_assets,total_liabilities,sales,expected_diagnostic",
    test_cases
)
def test_private_model_multi(current_assets, current_liabilities, retained_earnings, ebit, book_value_equity, total_assets, total_liabilities, sales, expected_diagnostic):
    working_capital = current_assets - current_liabilities
    result = altman_zscore_private(
        working_capital=working_capital,
        retained_earnings=retained_earnings,
        ebit=ebit,
        book_value_equity=book_value_equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        sales=sales
    )
    assert result.diagnostic == expected_diagnostic
