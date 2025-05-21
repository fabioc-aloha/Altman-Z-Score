"""Tests for integrated financials fetching with CIK lookup."""
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.altman_zscore.fetch_financials import fetch_batch_financials
from src.altman_zscore.config import PORTFOLIO

# Test data
MOCK_FINANCIAL_DATA = {
    "CA": 100000000.0,
    "TA": 500000000.0,
    "RE": 200000000.0,
    "EBIT": 50000000.0,
    "TL": 150000000.0,
    "Sales": 300000000.0
}

@pytest.fixture
def mock_environment():
    """Set up test environment variables."""
    with patch.dict('os.environ', {'SEC_EDGAR_USER_AGENT': 'test test@test.com'}):
        yield

def test_fetch_batch_financials_success(mock_environment):
    """Test successful batch financial data fetching."""
    test_tickers = ["MSFT", "GOOGL"]
    
    # Mock the CIK lookup
    mock_cik_map = {
        "MSFT": "0000789019",
        "GOOGL": "0001652044"
    }
    
    with patch('src.altman_zscore.cik_mapping.get_cik_mapping') as mock_get_cik_map, \
         patch('src.altman_zscore.fetch_financials.fetch_filing_url') as mock_fetch_url, \
         patch('src.altman_zscore.fetch_financials.parse_financials') as mock_parse:
        
        mock_get_cik_map.return_value = mock_cik_map
        mock_fetch_url.return_value = "http://example.com/filing.htm"
        mock_parse.return_value = MOCK_FINANCIAL_DATA
        
        period_end = "2025-03-31"
        results = fetch_batch_financials(test_tickers, period_end)
        
        # Verify the results
        assert len(results) == 2
        for ticker in test_tickers:
            assert results[ticker]["success"]
            assert results[ticker]["data"] == MOCK_FINANCIAL_DATA
            assert results[ticker]["error"] is None

def test_fetch_batch_financials_missing_cik(mock_environment):
    """Test batch fetching when some CIKs are not found."""
    test_tickers = ["MSFT", "INVALID"]
    
    # Mock the CIK lookup to return only one valid CIK
    mock_cik_map = {
        "MSFT": "0000789019"
    }
    
    with patch('src.altman_zscore.cik_mapping.get_cik_mapping') as mock_get_cik_map, \
         patch('src.altman_zscore.fetch_financials.fetch_filing_url') as mock_fetch_url, \
         patch('src.altman_zscore.fetch_financials.parse_financials') as mock_parse:
        
        mock_get_cik_map.return_value = mock_cik_map
        mock_fetch_url.return_value = "http://example.com/filing.htm"
        mock_parse.return_value = MOCK_FINANCIAL_DATA
        
        period_end = "2025-03-31"
        results = fetch_batch_financials(test_tickers, period_end)
        
        # Verify the results
        assert len(results) == 1  # Only MSFT should have results
        assert results["MSFT"]["success"]
        assert "INVALID" not in results

def test_fetch_batch_financials_all_ciks_missing(mock_environment):
    """Test batch fetching when no CIKs are found."""
    test_tickers = ["INVALID1", "INVALID2"]
    
    with patch('src.altman_zscore.cik_mapping.get_cik_mapping') as mock_get_cik_map:
        mock_get_cik_map.return_value = {}
        
        with pytest.raises(ValueError, match="No valid CIK numbers found"):
            fetch_batch_financials(test_tickers, "2025-03-31")

def test_fetch_batch_financials_parsing_error(mock_environment):
    """Test handling of parsing errors during batch fetching."""
    test_tickers = ["MSFT", "GOOGL"]
    
    # Mock the CIK lookup
    mock_cik_map = {
        "MSFT": "0000789019",
        "GOOGL": "0001652044"
    }
    
    with patch('src.altman_zscore.cik_mapping.get_cik_mapping') as mock_get_cik_map, \
         patch('src.altman_zscore.fetch_financials.fetch_filing_url') as mock_fetch_url, \
         patch('src.altman_zscore.fetch_financials.parse_financials') as mock_parse:
        
        mock_get_cik_map.return_value = mock_cik_map
        mock_fetch_url.return_value = "http://example.com/filing.htm"
        
        # Make parsing fail for GOOGL
        def mock_parse_with_error(url):
            if "0001652044" in url:  # GOOGL's CIK
                raise ValueError("Failed to parse financials")
            return MOCK_FINANCIAL_DATA
            
        mock_parse.side_effect = mock_parse_with_error
        
        period_end = "2025-03-31"
        results = fetch_batch_financials(test_tickers, period_end)
        
        # Verify the results
        assert len(results) == 2
        assert results["MSFT"]["success"]
        assert not results["GOOGL"]["success"]
        assert results["GOOGL"]["error"] is not None

def test_fetch_batch_financials_with_portfolio():
    """Test batch fetching with actual portfolio from config."""
    with patch('src.altman_zscore.cik_mapping.get_cik_mapping') as mock_get_cik_map, \
         patch('src.altman_zscore.fetch_financials.fetch_filing_url') as mock_fetch_url, \
         patch('src.altman_zscore.fetch_financials.parse_financials') as mock_parse:
        
        # Create mock CIK map for all portfolio tickers
        mock_cik_map = {ticker: f"{i:010d}" for i, ticker in enumerate(PORTFOLIO)}
        mock_get_cik_map.return_value = mock_cik_map
        mock_fetch_url.return_value = "http://example.com/filing.htm"
        mock_parse.return_value = MOCK_FINANCIAL_DATA
        
        period_end = "2025-03-31"
        results = fetch_batch_financials(PORTFOLIO, period_end)
        
        # Verify all portfolio stocks were processed
        assert len(results) == len([t for t in PORTFOLIO if t and not t.startswith("#")])
        for ticker in PORTFOLIO:
            if ticker and not ticker.startswith("#"):
                assert results[ticker]["success"]
                assert results[ticker]["data"] == MOCK_FINANCIAL_DATA
