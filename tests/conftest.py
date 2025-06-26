"""
Test Configuration and Utilities

Provides common test utilities, fixtures, and configuration for the test suite.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import project modules
from altman_zscore.models.data_models import (
    CompanyProfile, CanonicalQuarter, ZScoreResult,
    MergedFinancialData, MarketData, AnalysisContext,
    DataQualityReport
)
from altman_zscore.common.constants import ZSCORE_MODELS


class TestConfig:
    """Test configuration constants"""
    
    # Test symbols
    TEST_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    MOCK_SYMBOL = "TEST"
    
    # API configuration
    API_TIMEOUT = 30
    RATE_LIMIT_DELAY = 0.1
    
    # Test data paths
    FIXTURES_PATH = Path(__file__).parent / "fixtures"
    MOCK_DATA_PATH = FIXTURES_PATH / "mock_data.json"
    
    # Z-Score test thresholds
    SAFE_ZONE_MIN = 3.0
    GREY_ZONE_MIN = 1.8
    DISTRESS_ZONE_MAX = 1.8


class MockDataGenerator:
    """Generate mock data for testing"""
    
    @staticmethod
    def create_mock_company_profile(symbol: str = "TEST") -> CompanyProfile:
        """Create a mock company profile"""
        return CompanyProfile(
            ticker=symbol,
            name=f"Test Company {symbol}",
            sector="Technology",
            industry="Software",
            sic="7372",
            sic_description="Prepackaged Software",
            cik="1234567890",
            is_financial=False,
            is_retail=False,
            is_manufacturing=False,
            is_service=True,
            is_us_company=True,
            is_adr=False
        )
    
    @staticmethod
    def create_mock_canonical_quarter(period: str = "2023-12-31") -> CanonicalQuarter:
        """Create mock canonical quarter data"""
        return CanonicalQuarter(
            period_end=period,
            total_assets=100000000,
            current_assets=60000000,
            current_liabilities=25000000,
            total_liabilities=40000000,
            retained_earnings=30000000,
            ebit=28000000,
            sales=80000000,
            market_value_equity=120000000,
            inventory=8000000,
            intangible_assets=5000000
        )
    
    @staticmethod
    def create_mock_market_data(symbol: str = "TEST") -> MarketData:
        """Create mock market data"""
        return MarketData(
            market_value_equity={
                "2023-12-31": 120000000000,
                "2023-09-30": 115000000000,
                "2023-06-30": 118000000000
            },
            price_history=[
                {"date": "2023-12-31", "close": 150.50, "volume": 1500000},
                {"date": "2023-12-30", "close": 149.75, "volume": 1200000}
            ]
        )
    
    @staticmethod
    def create_mock_merged_financial_data(symbol: str = "TEST") -> MergedFinancialData:
        """Create comprehensive mock merged financial data"""
        return MergedFinancialData(
            ticker=symbol,
            timestamp="2023-12-31T00:00:00Z",
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            asset_turnover=0.8,
            market_cap=120000000000,
            shares_outstanding=800000000,
            current_price=150.0,
            current_ratio=2.4,
            debt_to_equity=0.33,
            data_quality_score=0.95
        )
    
    @staticmethod
    def create_mock_zscore_result(
        symbol: str = "TEST",
        z_score: float = 2.5
    ) -> ZScoreResult:
        """Create mock Z-Score result"""
        from altman_zscore.models.data_models import ZScoreComponent
        
        components = {
            "X1": ZScoreComponent(
                name="X1",
                value=1.4,
                numerator=35000000,
                denominator=25000000,
                coefficient=1.2,
                weighted_value=1.68
            ),
            "X2": ZScoreComponent(
                name="X2",
                value=0.3,
                numerator=30000000,
                denominator=100000000,
                coefficient=1.4,
                weighted_value=0.42
            )
        }
        
        return ZScoreResult(
            quarter_end="2023-12-31",
            zscore=z_score,
            components=components,
            valid=True,
            model_key="original",
            zone="GREY_ZONE" if 1.8 <= z_score < 3.0 else "SAFE_ZONE" if z_score >= 3.0 else "DISTRESS_ZONE"
        )


class MockAPIClient:
    """Mock API client for testing"""
    
    def __init__(self, simulate_errors: bool = False):
        self.simulate_errors = simulate_errors
        self.call_count = 0
        self.rate_limit_hit = False
    
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Mock company profile fetch"""
        self.call_count += 1
        
        if self.simulate_errors and self.call_count % 3 == 0:
            raise Exception("Simulated API error")
        
        return {
            "symbol": symbol,
            "companyName": f"Test Company {symbol}",
            "sector": "Technology",
            "industry": "Software",
            "mktCap": 1000000000,
            "description": f"Mock company for testing: {symbol}",
            "ceo": "Test CEO",
            "website": f"https://www.{symbol.lower()}.com",
            "fullTimeEmployees": 10000
        }
    
    async def get_balance_sheet(self, symbol: str) -> List[Dict[str, Any]]:
        """Mock balance sheet fetch"""
        self.call_count += 1
        
        if self.simulate_errors and self.call_count % 4 == 0:
            raise Exception("Simulated API error")
        
        return [{
            "date": "2023-12-31",
            "totalAssets": 100000000,
            "totalCurrentAssets": 60000000,
            "totalLiabilities": 40000000,
            "totalCurrentLiabilities": 25000000,
            "totalStockholdersEquity": 60000000,
            "retainedEarnings": 30000000,
            "totalDebt": 20000000,
            "cashAndCashEquivalents": 15000000,
            "inventory": 8000000,
            "netReceivables": 12000000,
            "accountsPayable": 10000000
        }]


@pytest.fixture
def mock_merged_financial_data():
    """Fixture providing mock merged financial data"""
    return MockDataGenerator.create_mock_merged_financial_data()


@pytest.fixture
def mock_company_profile():
    """Fixture providing mock company profile"""
    return MockDataGenerator.create_mock_company_profile()


@pytest.fixture
def mock_api_client():
    """Fixture providing mock API client"""
    return MockAPIClient()


@pytest.fixture
def mock_api_client_with_errors():
    """Fixture providing mock API client that simulates errors"""
    return MockAPIClient(simulate_errors=True)


@pytest.fixture
def test_symbols():
    """Fixture providing test symbols"""
    return TestConfig.TEST_SYMBOLS


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestUtilities:
    """Utility functions for testing"""
    
    @staticmethod
    def compare_decimals(a: Decimal, b: Decimal, precision: int = 2) -> bool:
        """Compare two decimal values with specified precision"""
        return abs(a - b) < Decimal(10) ** (-precision)
    
    @staticmethod
    def validate_zscore_range(z_score: float) -> bool:
        """Validate that Z-Score is in reasonable range"""
        return -10.0 <= z_score <= 20.0
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = ".json") -> Path:
        """Create a temporary file for testing"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=suffix, 
            delete=False
        )
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)
    
    @staticmethod
    def load_test_data(filename: str) -> Dict[str, Any]:
        """Load test data from fixtures"""
        fixtures_path = TestConfig.FIXTURES_PATH / filename
        if fixtures_path.exists():
            with open(fixtures_path, 'r') as f:
                return json.load(f)
        return {}
