"""
Unit tests for data integration and fetching components
"""

import pytest
from unittest.mock import Mock, patch
from altman_zscore.layers.data_fetch.data_merger import FMPRatiosData, YahooMarketData
from altman_zscore.layers.data_fetch.fmp_fetcher import FMPDataFetcher
from altman_zscore.common.exceptions import DataFetchError


class TestFMPRatiosData:
    """Test FMPRatiosData dataclass"""
    
    def test_creation_with_default_values(self):
        """Test creating FMPRatiosData with default values"""
        data = FMPRatiosData()
        
        assert data.working_capital_ratio is None
        assert data.retained_earnings_ratio is None
        assert data.ebit_ratio is None
        assert data.asset_turnover is None


class TestFMPDataFetcher:
    """Test FMPDataFetcher class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.fetcher = FMPDataFetcher()
        self.test_symbol = "AAPL"
    
    def test_get_financial_ratios_success(self):
        """Test successful ratio fetching from FMP"""
        mock_response = [
            {
                "symbol": "AAPL",
                "date": "2023-12-31",
                "currentRatio": 1.5,
                "debtToEquityRatio": 0.3,
                "returnOnAssets": 0.22,
                "returnOnEquity": 0.36,
                "assetTurnover": 0.85
            }
        ]
        
        with patch.object(self.fetcher, '_make_request', return_value=mock_response):
            ratios = self.fetcher.get_financial_ratios(self.test_symbol)
            
            assert len(ratios) == 1
            assert ratios[0]["symbol"] == "AAPL"
            assert ratios[0]["currentRatio"] == 1.5
            assert ratios[0]["assetTurnover"] == 0.85
    
    def test_get_financial_ratios_api_error(self):
        """Test ratio fetching with API error"""
        # Clear any cached data first
        cache_key = f"fmp_ratios:{self.test_symbol}:annual:None"
        if hasattr(self.fetcher.cache, 'delete'):
            self.fetcher.cache.delete(cache_key)
        elif hasattr(self.fetcher.cache, 'clear'):
            self.fetcher.cache.clear()
        
        with patch.object(self.fetcher, '_make_request', 
                         side_effect=DataFetchError("API Error")):
            with pytest.raises(DataFetchError) as exc_info:
                self.fetcher.get_financial_ratios(self.test_symbol)
            
            assert "API Error" in str(exc_info.value)
