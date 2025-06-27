"""
Unit tests for data models in altman_zscore.models.data_models

Tests all data classes and their validation logic, field calculations,
and post-init processing.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

from altman_zscore.models.data_models import (
    FilteredSecData, FilteredYahooData, MergedFinancialData,
    CanonicalQuarter, CompanyProfile, ZScoreModelConfig,
    ZScoreComponent, ZScoreResult, MarketData, AnalysisContext,
    OutputManifest, ValidationResult, QualityReport, OutlierReport,
    DataQualityReport
)


class TestFilteredSecData:
    """Test FilteredSecData data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating FilteredSecData with required fields"""
        data = FilteredSecData(
            quarters=[{"period": "Q1", "data": "test"}],
            metadata={"source": "SEC"},
            start_date="2023-01-01",
            total_quarters_available=4,
            filtered_quarters_count=4
        )
        
        assert len(data.quarters) == 1
        assert data.metadata["source"] == "SEC"
        assert data.start_date == "2023-01-01"
        assert data.total_quarters_available == 4
        assert data.filtered_quarters_count == 4
        assert data.company_profile == {}  # Default value
    
    def test_creation_with_all_fields(self):
        """Test creating FilteredSecData with all fields"""
        quarters = [{"period": f"Q{i}", "data": f"test{i}"} for i in range(1, 5)]
        metadata = {"source": "SEC", "api_version": "1.0"}
        company_profile = {"name": "Test Corp", "sector": "Technology"}
        
        data = FilteredSecData(
            quarters=quarters,
            metadata=metadata,
            start_date="2023-01-01",
            total_quarters_available=4,
            filtered_quarters_count=4,
            company_profile=company_profile
        )
        
        assert len(data.quarters) == 4
        assert data.metadata["api_version"] == "1.0"
        assert data.company_profile["name"] == "Test Corp"


class TestFilteredYahooData:
    """Test FilteredYahooData data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating FilteredYahooData with required fields"""
        market_data = {"current_price": 150.0, "volume": 1000000}
        price_history = [{"date": "2023-01-01", "close": 148.0}]
        
        data = FilteredYahooData(
            market_data=market_data,
            price_history=price_history,
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        assert data.market_data["current_price"] == 150.0
        assert len(data.price_history) == 1
        assert data.start_date == "2023-01-01"
        assert data.end_date == "2023-12-31"
        assert data.metadata == {}  # Default value


class TestMergedFinancialData:
    """Test MergedFinancialData data class"""
    
    def test_creation_with_basic_fields(self):
        """Test creating MergedFinancialData with basic fields"""
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31"
        )
        
        assert data.ticker == "AAPL"
        assert data.timestamp == "2023-12-31"
        assert data.working_capital_ratio is None
        assert data.market_cap is None
        assert data.data_quality_score is None
    
    def test_creation_with_zscore_ratios(self):
        """Test creating MergedFinancialData with Z-Score ratios"""
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            asset_turnover=0.8
        )
        
        assert data.working_capital_ratio == 1.2
        assert data.retained_earnings_ratio == 0.3
        assert data.ebit_ratio == 0.15
        assert data.asset_turnover == 0.8
    
    def test_creation_with_market_data(self):
        """Test creating MergedFinancialData with market data"""
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            market_cap=3000000000000,
            shares_outstanding=15000000000,
            current_price=200.0
        )
        
        assert data.market_cap == 3000000000000
        assert data.shares_outstanding == 15000000000
        assert data.current_price == 200.0
    
    def test_creation_with_quality_metrics(self):
        """Test creating MergedFinancialData with quality metrics"""
        raw_fmp = {"source": "FMP", "ratios": {"current_ratio": 1.5}}
        raw_yahoo = {"source": "Yahoo", "price": 200.0}
        
        data = MergedFinancialData(
            ticker="AAPL",
            timestamp="2023-12-31",
            data_quality_score=0.95,
            raw_fmp_data=raw_fmp,
            raw_yahoo_data=raw_yahoo
        )
        
        assert data.data_quality_score == 0.95
        assert data.raw_fmp_data["source"] == "FMP"
        assert data.raw_yahoo_data["source"] == "Yahoo"


class TestCanonicalQuarter:
    """Test CanonicalQuarter data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating CanonicalQuarter with required fields"""
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
        
        assert quarter.period_end == "2023-12-31"
        assert quarter.total_assets == 100000000
        assert quarter.current_assets == 60000000
        assert quarter.current_liabilities == 25000000
    
    def test_working_capital_calculation(self):
        """Test automatic working capital calculation"""
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
        
        # Working capital should be calculated as current_assets - current_liabilities
        expected_working_capital = 60000000 - 25000000
        assert quarter.working_capital == expected_working_capital
    
    def test_book_value_equity_calculation(self):
        """Test automatic book value equity calculation"""
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
        
        # Book value equity should be calculated as total_assets - total_liabilities
        expected_book_value = 100000000 - 40000000
        assert quarter.book_value_equity == expected_book_value
    
    def test_explicit_working_capital_not_overridden(self):
        """Test that explicitly provided working capital is not overridden"""
        quarter = CanonicalQuarter(
            period_end="2023-12-31",
            total_assets=100000000,
            current_assets=60000000,
            current_liabilities=25000000,
            total_liabilities=40000000,
            retained_earnings=30000000,
            ebit=20000000,
            sales=80000000,
            working_capital=50000000  # Explicit value
        )
        
        # Should keep the explicit value, not calculate
        assert quarter.working_capital == 50000000


class TestCompanyProfile:
    """Test CompanyProfile data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating CompanyProfile with required fields"""
        profile = CompanyProfile(
            ticker="AAPL",
            name="Apple Inc."
        )
        
        assert profile.ticker == "AAPL"
        assert profile.name == "Apple Inc."
        assert profile.sector is None
        assert profile.is_financial is False
        assert profile.is_us_company is True  # Default value
    
    def test_creation_with_classification_flags(self):
        """Test creating CompanyProfile with classification flags"""
        profile = CompanyProfile(
            ticker="JPM",
            name="JPMorgan Chase & Co.",
            sector="Financial Services",
            industry="Banks",
            is_financial=True,
            is_us_company=True
        )
        
        assert profile.is_financial is True
        assert profile.sector == "Financial Services"
        assert profile.industry == "Banks"
    
    def test_creation_with_metadata(self):
        """Test creating CompanyProfile with metadata"""
        metadata = {"exchange": "NASDAQ", "country": "US"}
        profile = CompanyProfile(
            ticker="AAPL",
            name="Apple Inc.",
            metadata=metadata
        )
        
        assert profile.metadata["exchange"] == "NASDAQ"
        assert profile.metadata["country"] == "US"


class TestZScoreModelConfig:
    """Test ZScoreModelConfig data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating ZScoreModelConfig with required fields"""
        coefficients = {
            "working_capital": 1.2,
            "retained_earnings": 1.4,
            "ebit": 3.3,
            "market_value": 0.6,
            "sales": 1.0
        }
        thresholds = {"safe": 3.0, "grey": 1.8}
        
        config = ZScoreModelConfig(
            model_key="original",
            model_type="Altman Z-Score (1968)",
            model_coefficients=coefficients,
            model_thresholds=thresholds,
            use_market_value=True
        )
        
        assert config.model_key == "original"
        assert config.model_type == "Altman Z-Score (1968)"
        assert config.model_coefficients["working_capital"] == 1.2
        assert config.model_thresholds["safe"] == 3.0
        assert config.use_market_value is True
        assert len(config.appropriateness_warnings) == 0  # Default


class TestZScoreComponent:
    """Test ZScoreComponent data class"""
    
    def test_creation_with_valid_component(self):
        """Test creating ZScoreComponent with valid values"""
        component = ZScoreComponent(
            name="X1",
            value=1.5,
            numerator=60000000,
            denominator=40000000,
            coefficient=1.2,
            weighted_value=1.8
        )
        
        assert component.name == "X1"
        assert component.value == 1.5
        assert component.numerator == 60000000
        assert component.denominator == 40000000
        assert component.coefficient == 1.2
        assert component.weighted_value == 1.8
        assert component.is_valid is True  # Default
        assert len(component.warnings) == 0  # Default
    
    def test_creation_with_warnings(self):
        """Test creating ZScoreComponent with warnings"""
        warnings = ["Negative working capital", "Low data quality"]
        component = ZScoreComponent(
            name="X1",
            value=-0.5,
            numerator=-20000000,
            denominator=40000000,
            coefficient=1.2,
            weighted_value=-0.6,
            is_valid=False,
            warnings=warnings
        )
        
        assert component.is_valid is False
        assert len(component.warnings) == 2
        assert "Negative working capital" in component.warnings


class TestZScoreResult:
    """Test ZScoreResult data class"""
    
    def test_creation_with_valid_result(self):
        """Test creating ZScoreResult with valid calculation"""
        components = {
            "X1": ZScoreComponent("X1", 1.5, 60000000, 40000000, 1.2, 1.8),
            "X2": ZScoreComponent("X2", 0.3, 30000000, 100000000, 1.4, 0.42)
        }
        
        result = ZScoreResult(
            quarter_end="2023-12-31",
            zscore=2.5,
            components=components,
            valid=True,
            model_key="original",
            zone="grey"
        )
        
        assert result.quarter_end == "2023-12-31"
        assert result.zscore == 2.5
        assert len(result.components) == 2
        assert result.valid is True
        assert result.model_key == "original"
        assert result.zone == "grey"
        assert result.diagnostics == ""  # Default
        assert len(result.errors) == 0  # Default
    
    def test_creation_with_errors(self):
        """Test creating ZScoreResult with errors"""
        errors = ["Missing market data", "Invalid EBIT value"]
        warnings = ["Low data quality"]
        
        result = ZScoreResult(
            quarter_end="2023-12-31",
            zscore=None,
            components={},
            valid=False,
            model_key="original",
            zone="unknown",
            errors=errors,
            warnings=warnings,
            diagnostics="Calculation failed due to missing data"
        )
        
        assert result.zscore is None
        assert result.valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert "Calculation failed" in result.diagnostics


class TestMarketData:
    """Test MarketData data class"""
    
    def test_creation_with_market_values(self):
        """Test creating MarketData with market values"""
        market_values = {
            "2023-12-31": 3000000000000,
            "2023-09-30": 2800000000000,
            "2023-06-30": 2900000000000
        }
        price_history = [
            {"date": "2023-12-31", "close": 200.0},
            {"date": "2023-09-30", "close": 186.67}
        ]
        
        data = MarketData(
            market_value_equity=market_values,
            price_history=price_history
        )
        
        assert len(data.market_value_equity) == 3
        assert data.market_value_equity["2023-12-31"] == 3000000000000
        assert len(data.price_history) == 2
        assert data.price_statistics == {}  # Default


class TestAnalysisContext:
    """Test AnalysisContext data class"""
    
    def test_creation_with_required_fields(self):
        """Test creating AnalysisContext with required fields"""
        model_config = ZScoreModelConfig(
            model_key="original",
            model_type="Altman Z-Score",
            model_coefficients={},
            model_thresholds={},
            use_market_value=True
        )
        
        company_profile = CompanyProfile(
            ticker="AAPL",
            name="Apple Inc."
        )
        
        context = AnalysisContext(
            ticker="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31",
            model_config=model_config,
            company_profile=company_profile,
            quarters_analyzed=4
        )
        
        assert context.ticker == "AAPL"
        assert context.start_date == "2023-01-01"
        assert context.end_date == "2023-12-31"
        assert context.quarters_analyzed == 4
        assert context.version == "4.0.0"  # Default
        # analysis_date should be set to current date by default


class TestValidationResult:
    """Test ValidationResult data class"""
    
    def test_creation_with_valid_result(self):
        """Test creating ValidationResult for valid data"""
        result = ValidationResult(valid=True)
        
        assert result.valid is True
        assert len(result.messages) == 0
        assert len(result.warnings) == 0
        assert len(result.errors) == 0
    
    def test_creation_with_errors(self):
        """Test creating ValidationResult with errors"""
        messages = ["Validation completed"]
        warnings = ["Low data quality"]
        errors = ["Missing required field: total_assets"]
        
        result = ValidationResult(
            valid=False,
            messages=messages,
            warnings=warnings,
            errors=errors
        )
        
        assert result.valid is False
        assert len(result.messages) == 1
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert "Missing required field" in result.errors[0]


class TestDataQualityReport:
    """Test DataQualityReport data class"""
    
    def test_creation_with_high_quality(self):
        """Test creating DataQualityReport for high-quality data"""
        report = DataQualityReport(
            ticker="AAPL",
            is_complete=True,
            missing_fields=[],
            warnings=[],
            quality_score=0.95,
            recommendation="Data quality is excellent, proceed with analysis"
        )
        
        assert report.ticker == "AAPL"
        assert report.is_complete is True
        assert len(report.missing_fields) == 0
        assert report.quality_score == 0.95
        assert "excellent" in report.recommendation
    
    def test_creation_with_quality_issues(self):
        """Test creating DataQualityReport with quality issues"""
        missing_fields = ["market_cap", "shares_outstanding"]
        warnings = ["Estimated market cap may be inaccurate"]
        
        report = DataQualityReport(
            ticker="TEST",
            is_complete=False,
            missing_fields=missing_fields,
            warnings=warnings,
            quality_score=0.65,
            recommendation="Moderate data quality, proceed with caution",
            total_checks=10,
            passed_checks=6,
            failed_checks=2,
            warning_checks=2
        )
        
        assert report.ticker == "TEST"
        assert report.is_complete is False
        assert len(report.missing_fields) == 2
        assert len(report.warnings) == 1
        assert report.quality_score == 0.65
        assert report.total_checks == 10
        assert report.passed_checks == 6


class TestOutputManifest:
    """Test OutputManifest data class"""
    
    def test_creation_with_basic_outputs(self):
        """Test creating OutputManifest with basic outputs"""
        manifest = OutputManifest(
            csv_path="/output/AAPL/analysis.csv",
            json_path="/output/AAPL/analysis.json",
            chart_path="/output/AAPL/chart.png"
        )
        
        assert manifest.csv_path.endswith("analysis.csv")
        assert manifest.json_path.endswith("analysis.json")
        assert manifest.chart_path.endswith("chart.png")
        assert manifest.report_path is None
        assert len(manifest.additional_files) == 0
    
    def test_creation_with_additional_files(self):
        """Test creating OutputManifest with additional files"""
        additional = {
            "summary": "/output/AAPL/summary.md",
            "raw_data": "/output/AAPL/raw_data.json"
        }
        
        manifest = OutputManifest(
            csv_path="/output/AAPL/analysis.csv",
            additional_files=additional
        )
        
        assert len(manifest.additional_files) == 2
        assert manifest.additional_files["summary"].endswith("summary.md")
        assert manifest.additional_files["raw_data"].endswith("raw_data.json")


# Performance tests for data model operations
class TestDataModelPerformance:
    """Test performance characteristics of data models"""
    
    def test_canonical_quarter_bulk_creation(self):
        """Test bulk creation of CanonicalQuarter objects"""
        import time
        
        start_time = time.time()
        quarters = []
        
        for i in range(1000):
            quarter = CanonicalQuarter(
                period_end=f"2023-{i%12+1:02d}-{(i%28)+1:02d}",
                total_assets=100000000 + i * 1000,
                current_assets=60000000 + i * 600,
                current_liabilities=25000000 + i * 250,
                total_liabilities=40000000 + i * 400,
                retained_earnings=30000000 + i * 300,
                ebit=20000000 + i * 200,
                sales=80000000 + i * 800
            )
            quarters.append(quarter)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        assert len(quarters) == 1000
        assert creation_time < 1.0  # Should complete in under 1 second
        
        # Verify calculations are correct
        sample_quarter = quarters[500]
        expected_working_capital = (60000000 + 500 * 600) - (25000000 + 500 * 250)
        assert sample_quarter.working_capital == expected_working_capital
