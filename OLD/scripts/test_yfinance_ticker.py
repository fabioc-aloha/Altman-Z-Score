import pytest
import yfinance as yf

@pytest.mark.parametrize("symbol", ["MSFT", "CA"])
def test_yfinance_ticker(symbol):
    """
    Basic integration test for yfinance Ticker.
    Checks that ticker.info and history can be retrieved without exception.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    # info should be a dict
    assert isinstance(info, dict)
    # history should return a non-empty DataFrame
    history = ticker.history(period="1mo")
    assert not history.empty
    # fast_info attribute should exist
    fast_info = getattr(ticker, 'fast_info', None)
    assert fast_info is not None
    # shares attribute should exist (if available)
    shares = getattr(ticker, 'shares', None)
    # shares may be None or a series, but attribute must exist
    assert hasattr(ticker, 'shares')
