import pytest
from altman_zscore.one_stock_analysis import analyze_single_stock_zscore_trend

def test_pipeline_integration_real():
    ticker = "AAPL"
    df = analyze_single_stock_zscore_trend(ticker)
    # Should return a DataFrame with at least one row
    assert not df.empty
    # All rows should have the expected columns
    for col in ["quarter_end", "zscore", "valid", "error", "diagnostic", "model"]:
        assert col in df.columns
    # At least one row should be valid (should be true for real data)
    assert df["valid"].any()
    # Z-score should be a float or None
    assert df["zscore"].dropna().apply(lambda x: isinstance(x, float)).all()
