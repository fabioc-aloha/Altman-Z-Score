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
    assert isinstance(info, dict)
    history = ticker.history(period="1mo")
    assert not history.empty
    fast_info = getattr(ticker, 'fast_info', None)
    assert fast_info is not None
    shares = getattr(ticker, 'shares', None)
    assert hasattr(ticker, 'shares')
