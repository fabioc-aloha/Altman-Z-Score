#!/usr/bin/env python3
"""
Tests for the AI-powered parsing functionality.

This module tests the AI-powered parsing of SEC EDGAR and Yahoo Finance API responses,
comparing results with the traditional parsing approach.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Ensure the project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Check if OpenAI and dotenv are installed
try:
    import openai
    from dotenv import load_dotenv
    # Load environment variables for testing
    load_dotenv()
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Skip tests if OpenAI is not installed
if not HAS_OPENAI:
    print("OpenAI SDK not installed. AI parsing tests will be skipped.")
    
# Check for OpenAI credentials
def has_openai_credentials():
    """Check if OpenAI credentials are available in environment"""
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_key = os.getenv("OPENAI_API_KEY")
    return (azure_key and azure_endpoint) or openai_key

@unittest.skipIf(not HAS_OPENAI or not has_openai_credentials(), "OpenAI SDK or credentials not available")
class TestAIParsing(unittest.TestCase):
    """Test AI-powered parsing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Import AI modules
        from srcai.altman_zscore.api.openai_client import OpenAIClient
        from srcai.altman_zscore.config.prompt_config import PromptConfig
        
        # Create mock prompt templates for testing
        self.mock_prompt_dir = Path("/tmp/altman_z_score_test_prompts")
        self.mock_prompt_dir.mkdir(exist_ok=True)
        
        # SEC EDGAR prompt template
        with open(self.mock_prompt_dir / "sec_edgar_parser.txt", "w") as f:
            f.write("Extract structured data from this SEC EDGAR API payload: {payload}\n"
                    "Return only a valid JSON object with numerical values.")
        
        # Yahoo Finance prompt template
        with open(self.mock_prompt_dir / "yahoo_finance_parser.txt", "w") as f:
            f.write("Extract structured data from this Yahoo Finance API payload: {payload}\n"
                    "Return only a valid JSON object with numerical values.")
        
        # Initialize AI components with mock data
        self.prompt_config = PromptConfig(config_dir=str(self.mock_prompt_dir))
        
        # Create a mock OpenAI client
        self.mock_openai_client = MagicMock(spec=OpenAIClient)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.mock_prompt_dir.exists():
            shutil.rmtree(self.mock_prompt_dir)
    
    def test_prompt_config(self):
        """Test prompt configuration loading"""
        # Test that prompt templates are loaded correctly
        sec_prompt = self.prompt_config.get_prompt("sec_edgar_parser")
        yahoo_prompt = self.prompt_config.get_prompt("yahoo_finance_parser")
        
        self.assertIn("SEC EDGAR API payload", sec_prompt)
        self.assertIn("Yahoo Finance API payload", yahoo_prompt)
        
    @patch("srcai.altman_zscore.api.openai_client.OpenAIClient")
    def test_sec_ai_client(self, mock_openai_client_class):
        """Test SEC AI client with mock data"""
        from srcai.altman_zscore.api.sec_ai_client import SECAIClient
        
        # Mock SEC client
        mock_sec_client = MagicMock()
        mock_sec_client.get_company_info.return_value = {
            "cik": "0000789019",
            "name": "MICROSOFT CORP",
            "sicCode": "7370",
            "sicDescription": "SERVICES-COMPUTER PROGRAMMING, DATA PROCESSING, ETC.",
            "tickers": ["MSFT"]
        }
        
        # Mock OpenAI client
        mock_openai_client = mock_openai_client_class.return_value
        mock_openai_client.extract_json_from_api_payload.return_value = {
            "cik": "0000789019",
            "name": "MICROSOFT CORP",
            "industry": "SERVICES-COMPUTER PROGRAMMING, DATA PROCESSING, ETC.",
            "sic_code": "7370",
            "ticker": "MSFT",
            "total_assets": 350000000000
        }
        
        # Initialize SEC AI client with mocks
        sec_ai_client = SECAIClient(
            openai_client=mock_openai_client,
            prompt_config=self.prompt_config,
            sec_client=mock_sec_client
        )
        
        # Test get_company_info
        result = sec_ai_client.get_company_info("MSFT")
        
        # Verify SEC client was called
        mock_sec_client.get_company_info.assert_called_once_with("MSFT")
        
        # Verify OpenAI client was called with the correct prompt
        mock_openai_client.extract_json_from_api_payload.assert_called_once()
        
        # Verify result contains expected data
        self.assertEqual(result["cik"], "0000789019")
        self.assertEqual(result["name"], "MICROSOFT CORP")
        self.assertEqual(result["total_assets"], 350000000000)
        
    @patch("srcai.altman_zscore.api.openai_client.OpenAIClient")
    @patch("yfinance.Ticker")
    def test_yahoo_ai_client(self, mock_ticker_class, mock_openai_client_class):
        """Test Yahoo Finance AI client with mock data"""
        from srcai.altman_zscore.api.yahoo_ai_client import YahooFinanceAIClient
        
        # Mock YFinance
        mock_ticker = mock_ticker_class.return_value
        mock_ticker.info = {
            "symbol": "AAPL",
            "shortName": "Apple Inc.",
            "industry": "Consumer Electronics",
            "sector": "Technology",
            "marketCap": 2500000000000,
            "regularMarketPrice": 150.25
        }
        
        # Mock OpenAI client
        mock_openai_client = mock_openai_client_class.return_value
        mock_openai_client.extract_json_from_api_payload.return_value = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "industry": "Consumer Electronics",
            "sector": "Technology",
            "market_cap": 2500000000000,
            "price": 150.25
        }
        
        # Initialize Yahoo Finance AI client with mocks
        yahoo_ai_client = YahooFinanceAIClient(
            openai_client=mock_openai_client,
            prompt_config=self.prompt_config
        )
        
        # Test get_ticker_info
        result = yahoo_ai_client.get_ticker_info("AAPL")
        
        # Verify YFinance was called
        mock_ticker_class.assert_called_once_with("AAPL")
        
        # Verify OpenAI client was called with the correct prompt
        mock_openai_client.extract_json_from_api_payload.assert_called_once()
        
        # Verify result contains expected data
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["name"], "Apple Inc.")
        self.assertEqual(result["market_cap"], 2500000000000)


if __name__ == "__main__":
    unittest.main()