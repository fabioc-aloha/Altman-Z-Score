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
        assert hasattr(model, 'validate_data')

def test_company_classification():
    """Test company classification logic"""
    # Test manufacturing company
    mfg_type = classify_company(
        SAMPLE_COMPANY_DATA["manufacturing"]["sector"],
        SAMPLE_COMPANY_DATA["manufacturing"]["industry"],
        SAMPLE_COMPANY_DATA["manufacturing"]["sic_code"]
    )
    assert mfg_type == ModelType.ORIGINAL

    # Test financial institution
    fin_type = classify_company(
        SAMPLE_COMPANY_DATA["financial"]["sector"],
        SAMPLE_COMPANY_DATA["financial"]["industry"],
        SAMPLE_COMPANY_DATA["financial"]["sic_code"]
    )
    assert fin_type == ModelType.FINANCIAL

    # Test retail company
    retail_type = classify_company(
        SAMPLE_COMPANY_DATA["retail"]["sector"],
        SAMPLE_COMPANY_DATA["retail"]["industry"],
        SAMPLE_COMPANY_DATA["retail"]["sic_code"]
    )
    assert retail_type == ModelType.RETAIL

def test_model_selection():
    """Test model selection logic"""
    # Test manufacturing company
    mfg_model = select_zscore_model(
        SAMPLE_COMPANY_DATA["manufacturing"],
        forced_model=None
    )
    assert mfg_model.get_model_type() == ModelType.ORIGINAL

    # Test financial institution with forced model override
    fin_model = select_zscore_model(
        SAMPLE_COMPANY_DATA["financial"],
        forced_model=ModelType.ORIGINAL
    )
    assert fin_model.get_model_type() == ModelType.ORIGINAL  # Should respect override

    # Test retail company
    retail_model = select_zscore_model(
        SAMPLE_COMPANY_DATA["retail"],
        forced_model=None
    )
    assert retail_model.get_model_type() == ModelType.RETAIL

def test_validation_warnings():
    """Test validation warnings for inappropriate model selection"""
    # Test using manufacturing model for financial institution
    mfg_model = ModelRegistry.create_model(ModelType.ORIGINAL)
    with pytest.warns(UserWarning):
        mfg_model.validate_company_profile(SAMPLE_COMPANY_DATA["financial"])

    # Test using financial model for retail company
    fin_model = ModelRegistry.create_model(ModelType.FINANCIAL)
    with pytest.warns(UserWarning):
        fin_model.validate_company_profile(SAMPLE_COMPANY_DATA["retail"])

def test_model_data_validation():
    """Test model-specific data validation"""
    # Test manufacturing model validation
    mfg_model = ModelRegistry.create_model(ModelType.ORIGINAL)
    valid_mfg_data = {
        "working_capital_to_assets": Decimal("0.2"),
        "retained_earnings_to_assets": Decimal("0.3"),
        "ebit_to_assets": Decimal("0.15"),
        "equity_to_liabilities": Decimal("2.0"),
        "sales_to_assets": Decimal("1.2")
    }
    assert mfg_model.validate_data(valid_mfg_data) is True

    # Test financial model validation
    fin_model = ModelRegistry.create_model(ModelType.FINANCIAL)
    valid_fin_data = {
        "liquid_assets_to_total_assets": Decimal("0.3"),
        "loan_loss_reserves_to_loans": Decimal("0.02"),
        "operating_expenses_to_income": Decimal("0.6"),
        "equity_to_total_debt": Decimal("0.15"),
        "core_revenue_to_assets": Decimal("0.08")
    }
    assert fin_model.validate_data(valid_fin_data) is True

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
    with pytest.raises(ValueError):
        model.validate_data(invalid_data)
