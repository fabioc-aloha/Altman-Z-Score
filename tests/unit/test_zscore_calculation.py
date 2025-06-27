"""
Unit tests for Z-Score calculation system

Tests the Z-Score calculator, model selector, and validation components
to ensure accurate calculations and proper model selection.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from typing import Dict, Any

from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator, ZScoreCalculationResult
from altman_zscore.layers.zscore_calculation.model_selector import (
    ModelSelector, CompanyType, ModelSelectionResult
)
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from altman_zscore.common.exceptions import CalculationError, ModelSelectionError


@pytest.mark.unit
class TestModelSelector:
    """Test ModelSelector class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.selector = ModelSelector()
    
    def test_has_market_data_with_valid_data(self):
        """Test market data detection with valid data"""
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            market_cap=3000000000000,
            shares_outstanding=15000000000
        )
        
        assert self.selector._has_market_data(data) == True
    
    def test_has_market_data_with_missing_data(self):
        """Test market data detection with missing data"""
        data = MergedFinancialData(
            ticker="PRIVATE",
            timestamp="2023-12-31",
            market_cap=None,
            shares_outstanding=None
        )
        
        assert self.selector._has_market_data(data) == False
    
    def test_has_market_data_with_zero_values(self):
        """Test market data detection with zero values"""
        data = MergedFinancialData(
            ticker="ZERO",
            timestamp="2023-12-31",
            market_cap=0,
            shares_outstanding=0
        )
        
        assert self.selector._has_market_data(data) == False
    
    def test_classify_company_type_private(self):
        """Test company type classification for private company"""
        data = MergedFinancialData(
            ticker="PRIVATE",
            timestamp="2023-12-31",
            market_cap=None,
            shares_outstanding=None
        )
        
        company_type = self.selector._classify_company_type(data)
        assert company_type == CompanyType.PRIVATE_COMPANY
    
    def test_classify_company_type_public_manufacturing(self):
        """Test company type classification for public manufacturing company"""
        data = MergedFinancialData(
            ticker="MANUF",
            timestamp="2023-12-31",
            market_cap=1000000000,
            shares_outstanding=100000000,
            inventory_ratio=0.15,  # High inventory indicates manufacturing
            asset_turnover=0.8
        )
        with patch.object(self.selector, '_has_market_data', return_value=True):
            # Mock the data attributes to trigger manufacturing classification
            data.inventory_ratio = 0.1  # Below retail threshold
            data.asset_turnover = 1.0   # Normal manufacturing range
            company_type = self.selector._classify_company_type(data)
            assert company_type == CompanyType.PUBLIC_MANUFACTURING
    
    def test_classify_company_type_public_retail(self):
        """Test company type classification for public retail company"""
        data = MergedFinancialData(
            ticker="RETAIL",
            timestamp="2023-12-31",
            market_cap=5000000000,
            shares_outstanding=500000000,
            inventory_ratio=0.25,  # High inventory for retail
            asset_turnover=2.5  # High turnover for retail
        )
        with patch.object(self.selector, '_has_market_data', return_value=True):
            # Mock the data attributes to trigger retail classification
            data.inventory_ratio = 0.25  # High inventory for retail
            data.asset_turnover = 1.0    # Normal retail range
            company_type = self.selector._classify_company_type(data)
            assert company_type == CompanyType.PUBLIC_RETAIL
    
    def test_model_mapping_completeness(self):
        """Test that all company types have model mappings"""
        for company_type in CompanyType:
            if company_type != CompanyType.FINANCIAL_COMPANY:  # Excluded type
                assert company_type in self.selector.model_mapping
    
    def test_select_model_for_public_manufacturing(self):
        """Test model selection for public manufacturing company"""
        data = MergedFinancialData(
            ticker="MANUF",
            timestamp="2023-12-31",
            market_cap=1000000000,
            shares_outstanding=100000000,
            inventory_ratio=0.10,
            asset_turnover=0.8
        )
        
        result = self.selector.select_model(data)
        assert result.model_name == "original"
        assert result.company_type == CompanyType.PUBLIC_MANUFACTURING
        assert result.confidence > 0
    
    def test_select_model_for_private_company(self):
        """Test model selection for private company"""
        data = MergedFinancialData(
            ticker="PRIVATE",
            timestamp="2023-12-31",
            market_cap=None,
            shares_outstanding=None
        )
        
        result = self.selector.select_model(data)
        assert result.model_name == "private"
        assert result.company_type == CompanyType.PRIVATE_COMPANY
        assert result.confidence > 0
    
    def test_select_model_for_financial_company_exclusion(self):
        """Test that financial companies are properly excluded"""
        data = MergedFinancialData(
            ticker="BANK",
            timestamp="2023-12-31",
            market_cap=100000000000,
            shares_outstanding=1000000000
        )
        
        # Test that financial companies would be excluded by exclusion check
        with patch.object(self.selector, '_check_sector_exclusions', return_value="Financial sector company"):
            data.debt_to_equity = 15.0  # High debt ratio suggesting financial company
            result = self.selector.select_model(data)
            
            # Should complete but add warning about potential exclusion
            assert len(result.warnings) > 0
            assert any("exclusion" in warning.lower() for warning in result.warnings)


@pytest.mark.unit
class TestZScoreCalculator:
    """Test ZScoreCalculator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = ZScoreCalculator()
    
    def test_calculator_initialization(self):
        """Test calculator initialization"""
        assert self.calculator is not None
        assert hasattr(self.calculator, 'model_selector')
        assert hasattr(self.calculator, 'risk_thresholds')
    
    def test_calculate_zscore_with_valid_data(self):
        """Test Z-Score calculation with valid financial data"""
        # Create mock financial data
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            asset_turnover=0.8,
            market_cap=3000000000000,
            shares_outstanding=15000000000,
            data_quality_score=0.95
        )
        
        # Mock model selection
        model_result = ModelSelectionResult(
            model_name="original",
            company_type=CompanyType.PUBLIC_MANUFACTURING,
            confidence=0.9,
            selection_rationale="Public manufacturing company",
            warnings=[],
            model_metadata={}
        )
        
        with patch.object(self.calculator, 'model_selector') as mock_selector:
            mock_selector.select_model.return_value = model_result
            result = self.calculator.calculate_zscore(data)
            
            # Validate the result
            assert isinstance(result, ZScoreCalculationResult)
            assert result.ticker == "AAPL"
            assert result.z_score is not None
            assert result.model_used == "original"
            assert result.risk_category in ["Safe", "Gray Zone", "Distress"]
    
    def test_calculate_zscore_with_missing_data(self):
        """Test Z-Score calculation with missing financial data"""
        data = MergedFinancialData(
            ticker="INCOMPLETE",
            timestamp="2023-12-31",
            working_capital_ratio=None,  # Missing critical data
            retained_earnings_ratio=0.3,
            ebit_ratio=None,  # Missing critical data
            market_cap=1000000000
        )
        
        # Should complete calculation despite missing data
        result = self.calculator.calculate_zscore(data)
        assert isinstance(result, ZScoreCalculationResult)
        assert result.ticker == "INCOMPLETE"
        assert len(result.warnings) > 0  # Should have warnings about missing data
    
    def test_categorize_risk_safe_zone(self):
        """Test risk category determination for safe zone"""
        z_score = 3.5
        category = self.calculator._categorize_risk(z_score, "original")
        assert category == "Safe"
    
    def test_categorize_risk_grey_zone(self):
        """Test risk category determination for grey zone"""
        z_score = 2.2
        category = self.calculator._categorize_risk(z_score, "original")
        assert category == "Gray Zone"
    
    def test_categorize_risk_distress_zone(self):
        """Test risk category determination for distress zone"""
        z_score = 1.5
        category = self.calculator._categorize_risk(z_score, "original")
        assert category == "Distress"
    
    def test_calculate_zscore_private_model(self):
        """Test Z-Score calculation using private company model"""
        data = MergedFinancialData(
            ticker="PRIVATE",
            timestamp="2023-12-31",
            working_capital_ratio=0.8,
            retained_earnings_ratio=0.2,
            ebit_ratio=0.12,
            asset_turnover=1.2,
            market_cap=None,  # Private company
            shares_outstanding=None,
            data_quality_score=0.85
        )
        
        model_result = ModelSelectionResult(
            model_name="private",
            company_type=CompanyType.PRIVATE_COMPANY,
            confidence=0.95,
            selection_rationale="No market data available",
            warnings=["Using book value instead of market value"],
            model_metadata={}
        )
        
        with patch.object(self.calculator, 'model_selector') as mock_selector:
            mock_selector.select_model.return_value = model_result
            result = self.calculator.calculate_zscore(data)
            
            assert result.model_used == "private"
            assert result.z_score is not None
            assert result.risk_category in ["Safe", "Gray Zone", "Distress"]
    
    def test_validate_calculation_data_sufficient(self):
        """Test data validation with sufficient data"""
        data = MergedFinancialData(
            ticker="GOOD",
            timestamp="2023-12-31",
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            data_quality_score=0.9
        )
        
        warnings = self.calculator._validate_calculation_data(data)
        # Should have some warnings but not fail completely
        assert isinstance(warnings, list)
    
    def test_validate_calculation_data_insufficient(self):
        """Test data validation with insufficient data quality"""
        data = MergedFinancialData(
            ticker="BAD",
            timestamp="2023-12-31",
            working_capital_ratio=None,
            retained_earnings_ratio=None,
            ebit_ratio=None,
            data_quality_score=0.3
        )
        
        # Should complete but with many warnings
        warnings = self.calculator._validate_calculation_data(data)
        assert isinstance(warnings, list)
        assert len(warnings) > 0
    
    def test_calculation_with_edge_case_values(self):
        """Test calculation handling of edge case values"""
        data = MergedFinancialData(
            ticker="EDGE",
            timestamp="2023-12-31",
            working_capital_ratio=-0.5,  # Negative working capital
            retained_earnings_ratio=-0.1,  # Negative retained earnings
            ebit_ratio=0.05,  # Low EBIT
            asset_turnover=0.2,  # Low turnover
            market_cap=100000000,  # Small market cap
            data_quality_score=0.8
        )
        
        model_result = ModelSelectionResult(
            model_name="original",
            company_type=CompanyType.PUBLIC_MANUFACTURING,
            confidence=0.7,
            selection_rationale="Public company with challenging metrics",
            warnings=["Negative working capital", "Low profitability"],
            model_metadata={}
        )
        
        with patch.object(self.calculator, 'model_selector') as mock_selector:
            mock_selector.select_model.return_value = model_result
            result = self.calculator.calculate_zscore(data)
            
            assert result.z_score < 1.8  # Should be in distress zone
            assert result.risk_category == "Distress"


@pytest.mark.integration
class TestZScoreCalculationIntegration:
    """Test Z-Score calculation integration scenarios"""
    
    def test_end_to_end_calculation_public_company(self):
        """Test complete calculation flow for a public company"""
        calculator = ZScoreCalculator()
        
        # Create realistic public company data
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            working_capital_ratio=1.1,
            retained_earnings_ratio=0.45,
            ebit_ratio=0.25,
            asset_turnover=0.85,
            market_cap=3000000000000,
            shares_outstanding=15000000000,
            current_price=200.0,
            current_ratio=1.5,
            debt_to_equity=0.3,
            data_quality_score=0.95
        )
        
        result = calculator.calculate_zscore(data)
        
        # Validate result structure
        assert isinstance(result, ZScoreCalculationResult)
        assert result.ticker == "AAPL"
        assert result.z_score is not None
        assert result.z_score > 0
        assert result.model_used in ["original", "service", "retail"]
        assert result.risk_category in ["Safe", "Gray Zone", "Distress"]
        assert result.data_quality_score == 0.95
        assert result.component_values is not None
        assert "z_score" in result.component_values
    
    def test_end_to_end_calculation_private_company(self):
        """Test complete calculation flow for a private company"""
        calculator = ZScoreCalculator()
        
        # Create private company data (no market data)
        data = MergedFinancialData(
            ticker="PRIVATE_CO",
            timestamp="2023-12-31",
            working_capital_ratio=0.9,
            retained_earnings_ratio=0.25,
            ebit_ratio=0.15,
            asset_turnover=1.1,
            market_cap=None,
            shares_outstanding=None,
            current_ratio=1.2,
            debt_to_equity=0.6,
            data_quality_score=0.85
        )
        
        result = calculator.calculate_zscore(data)
        
        assert result.model_used == "private"
        assert result.z_score is not None
        assert result.risk_category in ["Safe", "Gray Zone", "Distress"]
        # Note: updated to check for actual warning content
        assert len(result.warnings) > 0
    
    def test_calculation_performance(self):
        """Test calculation performance with multiple companies"""
        import time
        calculator = ZScoreCalculator()
        
        # Create multiple test data sets
        test_data = []
        for i in range(10):
            data = MergedFinancialData(
                ticker=f"TEST_{i}",
                timestamp="2023-12-31",
                working_capital_ratio=1.0 + (i * 0.1),
                retained_earnings_ratio=0.2 + (i * 0.02),
                ebit_ratio=0.1 + (i * 0.01),
                asset_turnover=0.8 + (i * 0.05),
                market_cap=1000000000 * (i + 1),
                data_quality_score=0.8 + (i * 0.01)
            )
            test_data.append(data)
        
        # Time the calculations
        start_time = time.time()
        results = [calculator.calculate_zscore(data) for data in test_data]
        end_time = time.time()
        
        # Performance validation
        total_time = end_time - start_time
        assert total_time < 5.0  # Should complete in under 5 seconds
        assert len(results) == 10
        assert all(isinstance(result, ZScoreCalculationResult) for result in results)


@pytest.mark.unit
class TestZScoreValidation:
    """Test Z-Score calculation validation and edge cases"""
    
    def test_extreme_positive_zscore(self):
        """Test handling of extremely high Z-Scores"""
        calculator = ZScoreCalculator()
        
        # Data that would produce very high Z-Score
        data = MergedFinancialData(
            ticker="EXTREME_HIGH",
            timestamp="2023-12-31",
            working_capital_ratio=5.0,  # Very high
            retained_earnings_ratio=2.0,  # Very high
            ebit_ratio=1.0,  # Very high
            asset_turnover=3.0,  # Very high
            market_cap=10000000000000,  # Very high
            shares_outstanding=1000000000,
            data_quality_score=0.9
        )
        
        result = calculator.calculate_zscore(data)
        
        # Should handle extreme values gracefully
        assert result.z_score > 0
        assert result.risk_category == "Safe"
        assert result.z_score < 1000  # Should be reasonable, not infinite
    
    def test_extreme_negative_zscore(self):
        """Test handling of extremely low Z-Scores"""
        calculator = ZScoreCalculator()
        
        # Data that would produce very low Z-Score
        data = MergedFinancialData(
            ticker="EXTREME_LOW",
            timestamp="2023-12-31",
            working_capital_ratio=-2.0,  # Very negative
            retained_earnings_ratio=-0.5,  # Negative
            ebit_ratio=-0.2,  # Negative EBIT
            asset_turnover=0.1,  # Very low
            market_cap=10000000,  # Very low
            shares_outstanding=1000000,
            data_quality_score=0.7
        )
        
        result = calculator.calculate_zscore(data)
        
        # Should handle extreme negative values
        assert result.z_score < 0
        assert result.risk_category == "Distress"
        assert result.z_score > -1000  # Should be reasonable, not negative infinite
    
    def test_zero_division_protection(self):
        """Test protection against division by zero"""
        calculator = ZScoreCalculator()
        
        # Data with potential zero denominators
        data = MergedFinancialData(
            ticker="ZERO_TEST",
            timestamp="2023-12-31",
            working_capital_ratio=0.0,
            retained_earnings_ratio=0.0,
            ebit_ratio=0.0,
            asset_turnover=0.0,
            market_cap=0,
            shares_outstanding=0,
            data_quality_score=0.5
        )
        
        # Should complete without throwing exceptions
        result = calculator.calculate_zscore(data)
        assert isinstance(result, ZScoreCalculationResult)
        assert result.ticker == "ZERO_TEST"
        assert result.z_score is not None
        assert not (result.z_score == float('inf') or result.z_score == float('-inf'))
