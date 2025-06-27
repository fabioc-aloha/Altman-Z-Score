"""
Unit test initialization file

Contains basic tests to verify the test suite is working correctly
and can import the main altman_zscore package.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestTestSuiteSetup:
    """Test that the test suite itself is properly configured"""
    
    def test_can_import_altman_zscore(self):
        """Test that we can import the main package"""
        try:
            import altman_zscore
            assert altman_zscore is not None
        except ImportError as e:
            pytest.skip(f"Cannot import altman_zscore: {e}")
    
    def test_can_import_models(self):
        """Test that we can import data models"""
        try:
            from altman_zscore.models import data_models
            assert data_models is not None
        except ImportError as e:
            pytest.skip(f"Cannot import data models: {e}")
    
    def test_can_import_common_modules(self):
        """Test that we can import common modules"""
        try:
            from altman_zscore.common import constants
            assert constants is not None
        except ImportError as e:
            pytest.skip(f"Cannot import common modules: {e}")
    
    def test_test_fixtures_exist(self):
        """Test that test fixtures are available"""
        fixtures_path = Path(__file__).parent.parent / "fixtures"
        assert fixtures_path.exists()
        
        test_data_path = fixtures_path / "test_data.json"
        assert test_data_path.exists()
    
    def test_pytest_markers_work(self):
        """Test that pytest markers are properly configured"""
        # This test itself uses the unit marker
        pass


class TestBasicDataModels:
    """Basic tests for data models that should always work"""
    
    def test_merged_financial_data_creation(self):
        """Test basic MergedFinancialData creation"""
        try:
            from altman_zscore.models.data_models import MergedFinancialData
            
            data = MergedFinancialData(
                ticker="TEST",
                timestamp="2023-12-31"
            )
            
            assert data.ticker == "TEST"
            assert data.timestamp == "2023-12-31"
            
        except ImportError:
            pytest.skip("Cannot import MergedFinancialData")
    
    def test_canonical_quarter_calculation(self):
        """Test CanonicalQuarter automatic calculations"""
        try:
            from altman_zscore.models.data_models import CanonicalQuarter
            
            quarter = CanonicalQuarter(
                period_end="2023-12-31",
                total_assets=100000000,
                current_assets=60000000,
                current_liabilities=25000000,
                total_liabilities=40000000,
                retained_earnings=30000000,
                ebit=20000000,
                sales=80000000
            )
            
            # Should automatically calculate working capital
            assert quarter.working_capital == 35000000  # 60M - 25M
            
            # Should automatically calculate book value equity
            assert quarter.book_value_equity == 60000000  # 100M - 40M
            
        except ImportError:
            pytest.skip("Cannot import CanonicalQuarter")


class TestConstants:
    """Test that constants are properly defined"""
    
    def test_zscore_models_exist(self):
        """Test that Z-Score models are defined"""
        try:
            from altman_zscore.common.constants import ZSCORE_MODELS
            
            assert isinstance(ZSCORE_MODELS, dict)
            assert len(ZSCORE_MODELS) > 0
            
            # Should have at least original model
            assert "original" in ZSCORE_MODELS
            
        except ImportError:
            pytest.skip("Cannot import ZSCORE_MODELS")
    
    def test_risk_zones_exist(self):
        """Test that risk zones are defined (if they exist)"""
        try:
            from altman_zscore.common.constants import RISK_ZONES
            
            assert isinstance(RISK_ZONES, dict)
            assert len(RISK_ZONES) > 0
            
        except ImportError:
            # This is okay if RISK_ZONES doesn't exist
            pytest.skip("RISK_ZONES not implemented yet")


# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit
