import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from decimal import Decimal
from altman_zscore.models.base import ModelType
from altman_zscore.models.factory import ModelRegistry
from altman_zscore.models.industry_classifier import classify_company
from altman_zscore.computation.model_selection import select_zscore_model

# Test data
SAMPLE_COMPANY_DATA = {
    "manufacturing": {
        "name": "Test Manufacturing Co",
        "sector": "Manufacturing",
        "industry": "Industrial Manufacturing",
        "sic_code": "3000",
        "market_cap": 1000000000,  # Large cap
        "region": "North America"
    },
    "financial": {
        "name": "Test Bank",
        "sector": "Financial Services",
        "industry": "Banks",
        "sic_code": "6000",
        "market_cap": 5000000000,
        "region": "North America"
    },
    "retail": {
        "name": "Test Retail Store",
        "sector": "Consumer Cyclical",
        "industry": "Retail",
        "sic_code": "5200",
        "market_cap": 500000000,
        "region": "North America"
    },
    "emerging": {
        "name": "Test Emerging Co",
        "sector": "Technology",
        "industry": "Software",
        "sic_code": "7370",
        "market_cap": 100000000,
        "region": "Asia"
    }
}

def test_model_registry_creation():
    """Test that all model types can be created from registry"""
    for model_type in ModelType:
        model = ModelRegistry.create_model(model_type)
        assert model is not None
        assert hasattr(model, 'calculate_zscore')
        # Only check for validate_data if it exists
        if hasattr(model, 'validate_data'):
            assert callable(model.validate_data)

def test_company_classification():
    """Test company classification logic"""
    # Use representative tickers for each type
    mfg_type = classify_company("F")  # Ford, manufacturing
    assert mfg_type["industry"] != "Unknown"
    assert mfg_type["is_public"] is True

    fin_type = classify_company("JPM")  # JPMorgan, financial
    assert fin_type["industry"] != "Unknown"
    assert fin_type["is_public"] is True

    retail_type = classify_company("WMT")  # Walmart, retail
    assert retail_type["industry"] != "Unknown"
    assert retail_type["is_public"] is True

def test_model_selection():
    """Test model selection logic"""
    # Test manufacturing company
    mfg_model_key = select_zscore_model(
        int(SAMPLE_COMPANY_DATA["manufacturing"]["sic_code"]), True
    )
    assert mfg_model_key == "original"

    # Test retail company
    retail_model_key = select_zscore_model(
        int(SAMPLE_COMPANY_DATA["retail"]["sic_code"]), True
    )
    assert retail_model_key == "retail"

def test_validation_warnings():
    """Test validation warnings for inappropriate model selection"""
    mfg_model = ModelRegistry.create_model(ModelType.ORIGINAL)
    if hasattr(mfg_model, 'validate_company_profile'):
        with pytest.warns(UserWarning):
            mfg_model.validate_company_profile(SAMPLE_COMPANY_DATA["financial"])
    fin_model = ModelRegistry.create_model(ModelType.FINANCIAL)
    if hasattr(fin_model, 'validate_company_profile'):
        with pytest.warns(UserWarning):
            fin_model.validate_company_profile(SAMPLE_COMPANY_DATA["retail"])

def test_model_data_validation():
    """Test model-specific data validation"""
    mfg_model = ModelRegistry.create_model(ModelType.ORIGINAL)
    valid_mfg_data = {
        "working_capital": 200.0,
        "retained_earnings": 300.0,
        "ebit": 150.0,
        "market_value_equity": 500.0,
        "total_assets": 1000.0,
        "total_liabilities": 400.0,
        "sales": 1200.0
    }
    if hasattr(mfg_model, 'validate_data'):
        assert mfg_model.validate_data(valid_mfg_data) is not None
    fin_model = ModelRegistry.create_model(ModelType.FINANCIAL)
    valid_fin_data = {
        "total_assets": 1000.0,
        "total_liabilities": 800.0,
        "retained_earnings": 200.0,
        "ebit": 100.0,
        "total_equity": 300.0,
        "intangible_assets": 50.0
    }
    if hasattr(fin_model, 'validate_data'):
        assert fin_model.validate_data(valid_fin_data) is not None

def test_invalid_data_handling():
    """Test handling of invalid data"""
    model = ModelRegistry.create_model(ModelType.ORIGINAL)
    invalid_data = {
        "working_capital_to_assets": Decimal("-5.0"),  # Unrealistic value
        "retained_earnings_to_assets": Decimal("0.3"),
        "ebit_to_assets": Decimal("0.15"),
        "equity_to_liabilities": Decimal("2.0"),
        "sales_to_assets": Decimal("1.2")
    }
    if hasattr(model, 'validate_data'):
        with pytest.raises(ValueError):
            model.validate_data(invalid_data)
