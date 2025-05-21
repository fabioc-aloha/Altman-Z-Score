"""Tests for CIK lookup functionality."""
import os
import pytest
import logging
from unittest.mock import patch, MagicMock

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
from src.altman_zscore.cik_lookup import (
    lookup_cik,
    validate_cik,
    validate_portfolio_ciks,
    CIKLookupError
)

# Test data
TEST_PORTFOLIO = {
    "MSFT": "0000789019",  # Microsoft
    "AAPL": "0000320193",  # Apple
}

def test_lookup_cik_valid():
    """Test looking up a valid CIK."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = '''<div>CIK=0000789019</div>'''
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        os.environ['SEC_EDGAR_USER_AGENT'] = 'test test@test.com'
        assert lookup_cik('MSFT') == '0000789019'

def test_lookup_cik_invalid():
    """Test looking up an invalid ticker."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = '''<div>No matching company</div>'''
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        os.environ['SEC_EDGAR_USER_AGENT'] = 'test test@test.com'
        assert lookup_cik('INVALID') is None

def test_lookup_cik_no_user_agent():
    """Test lookup without SEC_EDGAR_USER_AGENT set."""
    with patch('src.altman_zscore.cik_lookup.load_dotenv') as mock_load_dotenv, \
         patch.dict('os.environ', {}, clear=True):  # Clear environment variables
        mock_load_dotenv.return_value = False  # Make sure load_dotenv returns False
        with pytest.raises(CIKLookupError, match="environment variables are set"):
            lookup_cik('MSFT')

def test_validate_cik():
    """Test CIK validation."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = '''<div>CIK=0000789019</div>'''
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        os.environ['SEC_EDGAR_USER_AGENT'] = 'test test@test.com'
        assert validate_cik('MSFT', '0000789019') is True
        assert validate_cik('MSFT', '0000000000') is False

def test_validate_portfolio_ciks():
    """Test portfolio CIK validation."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = '''<div>CIK=0000789019</div>'''
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        os.environ['SEC_EDGAR_USER_AGENT'] = 'test test@test.com'
        results = validate_portfolio_ciks({'MSFT': '0000789019'})
        assert results == {'MSFT': True}
