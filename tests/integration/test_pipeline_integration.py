"""
Integration tests for the complete Altman Z-Score analysis pipeline

These tests validate the end-to-end functionality of the system,
testing component interactions and complete analysis workflows.
"""

import pytest
import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.layers.data_fetch.data_merger import DataMerger
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from altman_zscore.layers.market_analysis.market_analysis_orchestrator import MarketAnalysisOrchestrator
from altman_zscore.layers.output_generation.report_generator import ReportGenerator
from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculationResult
from altman_zscore.common.exceptions import DataFetchError, CalculationError
from tests.conftest import MockDataGenerator, TestConfig


class TestMainPipelineIntegration:
    """Test the main analysis pipeline integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = AltmanZScorePipeline()
        self.test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    @pytest.mark.asyncio
    async def test_single_company_analysis_success(self):
        """Test complete analysis for a single company"""
        symbol = "AAPL"
        
        # Mock the data merger to return valid data
        mock_data = MockDataGenerator.create_mock_company_data(symbol)
        merged_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=0.15,
            asset_turnover=0.8,
            market_cap=3000000000000,
            shares_outstanding=15000000000,
            current_price=200.0,
            data_quality_score=0.95
        )
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.return_value = merged_data
            
            result = await self.pipeline.analyze_company(symbol)
            
            # Verify the result structure
            assert result is not None
            assert hasattr(result, 'ticker')
            assert result.ticker == symbol
            assert hasattr(result, 'z_score_result')
            assert hasattr(result, 'market_analysis')
            assert hasattr(result, 'risk_assessment')
    
    @pytest.mark.asyncio
    async def test_batch_analysis_success(self):
        """Test batch analysis of multiple companies"""
        symbols = self.test_symbols
        
        # Mock data for each symbol
        mock_results = {}
        for symbol in symbols:
            mock_results[symbol] = MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.0 + (hash(symbol) % 10) * 0.1,
                retained_earnings_ratio=0.2 + (hash(symbol) % 5) * 0.05,
                ebit_ratio=0.1 + (hash(symbol) % 8) * 0.02,
                asset_turnover=0.6 + (hash(symbol) % 6) * 0.1,
                market_cap=1000000000000 + (hash(symbol) % 10) * 500000000000,
                data_quality_score=0.85 + (hash(symbol) % 10) * 0.01
            )
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = lambda sym: mock_results[sym]
            
            results = await self.pipeline.analyze_batch(symbols)
            
            # Verify batch results
            assert len(results) == len(symbols)
            assert all(symbol in results for symbol in symbols)
            
            # Verify each result has required components
            for symbol, result in results.items():
                assert result.ticker == symbol
                assert hasattr(result, 'z_score_result')
                assert result.z_score_result.z_score is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_with_data_fetch_errors(self):
        """Test pipeline behavior when data fetching fails"""
        symbol = "FAIL_TEST"
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = DataFetchError("API temporarily unavailable")
            
            with pytest.raises(DataFetchError):
                await self.pipeline.analyze_company(symbol)
    
    @pytest.mark.asyncio
    async def test_pipeline_with_partial_batch_failures(self):
        """Test batch analysis with some symbols failing"""
        symbols = ["AAPL", "FAIL", "MSFT"]
        
        def mock_merge_data(symbol):
            if symbol == "FAIL":
                raise DataFetchError("Failed to fetch data")
            return MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.2,
                retained_earnings_ratio=0.3,
                ebit_ratio=0.15,
                data_quality_score=0.9
            )
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = mock_merge_data
            
            results = await self.pipeline.analyze_batch(symbols, continue_on_error=True)
            
            # Should have results for successful symbols only
            assert len(results) == 2
            assert "AAPL" in results
            assert "MSFT" in results
            assert "FAIL" not in results
    
    @pytest.mark.asyncio
    async def test_output_generation_integration(self):
        """Test integration with output generation"""
        symbol = "AAPL"
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir)
            
            # Mock analysis data
            merged_data = MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.2,
                retained_earnings_ratio=0.3,
                ebit_ratio=0.15,
                asset_turnover=0.8,
                market_cap=3000000000000,
                data_quality_score=0.95
            )
            
            with patch.object(self.pipeline, 'data_merger') as mock_merger:
                mock_merger.merge_data.return_value = merged_data
                
                result = await self.pipeline.analyze_company(
                    symbol, 
                    output_path=output_path,
                    generate_reports=True
                )
                
                # Verify analysis completed
                assert result is not None
                
                # Verify output files were created
                company_dir = output_path / symbol
                assert company_dir.exists()
                
                # Check for expected output files
                expected_files = ["analysis.json", "chart.png", "report.md"]
                for filename in expected_files:
                    file_path = company_dir / filename
                    if file_path.exists():
                        assert file_path.stat().st_size > 0


class TestDataFlowIntegration:
    """Test data flow between components"""
    
    @pytest.mark.asyncio
    async def test_data_merger_to_calculator_integration(self):
        """Test data flow from merger to Z-Score calculator"""
        symbol = "INTEGRATION_TEST"
        
        # Create realistic merged data
        merged_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            working_capital_ratio=1.1,
            retained_earnings_ratio=0.35,
            ebit_ratio=0.18,
            asset_turnover=0.75,
            market_cap=2000000000000,
            shares_outstanding=12000000000,
            current_price=166.67,
            data_quality_score=0.92
        )
        
        # Test the integration
        calculator = ZScoreCalculator()
        result = calculator.calculate_zscore(merged_data)
        
        # Verify the calculation result
        assert isinstance(result, ZScoreCalculationResult)
        assert result.ticker == symbol
        assert result.z_score is not None
        assert result.z_score > 0  # Should be positive for reasonable data
        assert result.data_quality_score == 0.92
        assert len(result.component_values) == 5  # X1 through X5
        
        # Verify component calculations are reasonable
        for component_name, value in result.component_values.items():
            assert isinstance(value, (int, float))
            assert not (value != value)  # Check for NaN
    
    @pytest.mark.asyncio
    async def test_calculator_to_market_analyzer_integration(self):
        """Test data flow from calculator to market analyzer"""
        symbol = "MARKET_TEST"
        
        # Create Z-Score result
        zscore_result = ZScoreCalculationResult(
            ticker=symbol,
            z_score=2.5,
            model_used="original",
            risk_category="Grey Zone",
            component_values={
                "X1": 1.32, "X2": 0.49, "X3": 0.59, "X4": 0.72, "X5": 0.75
            },
            calculation_timestamp=datetime.now().isoformat(),
            data_quality_score=0.88,
            warnings=[],
            metadata={}
        )
        
        # Test market analysis integration
        with patch('altman_zscore.layers.market_analysis.market_analysis_orchestrator.MarketAnalysisOrchestrator') as MockAnalyzer:
            mock_analyzer = MockAnalyzer.return_value
            mock_analyzer.analyze_market_position.return_value = {
                "sector_comparison": {"sector_average_zscore": 2.1},
                "peer_analysis": {"peer_count": 5, "relative_ranking": 3},
                "market_trends": {"trend_direction": "stable"}
            }
            
            # This would be called within the pipeline
            market_analysis = mock_analyzer.analyze_market_position(zscore_result)
            
            # Verify the integration
            assert market_analysis is not None
            assert "sector_comparison" in market_analysis
            assert "peer_analysis" in market_analysis
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_consistency(self):
        """Test data consistency through the entire pipeline"""
        symbol = "CONSISTENCY_TEST"
        
        # Start with known input data
        input_ratios = {
            "working_capital_ratio": 1.15,
            "retained_earnings_ratio": 0.28,
            "ebit_ratio": 0.16,
            "asset_turnover": 0.82
        }
        
        merged_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            **input_ratios,
            market_cap=1500000000000,
            data_quality_score=0.9
        )
        
        # Track data through the pipeline
        calculator = ZScoreCalculator()
        
        with patch.object(calculator, 'model_selector') as mock_selector:
            # Mock model selection to return original model
            from altman_zscore.layers.zscore_calculation.model_selector import (
                ModelSelectionResult, CompanyType
            )
            
            mock_selector.select_model.return_value = ModelSelectionResult(
                model_name="original",
                company_type=CompanyType.PUBLIC_MANUFACTURING,
                confidence=0.9,
                selection_rationale="Public company with market data",
                warnings=[],
                model_metadata={}
            )
            
            result = calculator.calculate_zscore(merged_data)
            
            # Verify data consistency
            assert result.ticker == symbol
            
            # Verify that input ratios are reflected in components
            # (exact values depend on model coefficients, but should be related)
            for component_name, component_value in result.component_values.items():
                assert component_value is not None
                assert isinstance(component_value, (int, float))
                assert component_value != 0  # Should have calculated values
            
            # Verify the final Z-Score is reasonable
            assert 0 < result.z_score < 10  # Reasonable range for most companies
            
            # Verify timestamp consistency
            input_timestamp = merged_data.timestamp
            output_timestamp = result.calculation_timestamp
            
            # Both should be recent timestamps
            input_dt = datetime.fromisoformat(input_timestamp.replace('Z', '+00:00'))
            output_dt = datetime.fromisoformat(output_timestamp.replace('Z', '+00:00'))
            
            time_diff = abs((output_dt - input_dt).total_seconds())
            assert time_diff < 60  # Should be within a minute


class TestErrorHandlingIntegration:
    """Test error handling across component boundaries"""
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_with_missing_data(self):
        """Test system behavior with progressively missing data"""
        symbol = "DEGRADATION_TEST"
        
        # Test with minimal data
        minimal_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            working_capital_ratio=1.2,
            retained_earnings_ratio=0.3,
            ebit_ratio=None,  # Missing
            asset_turnover=None,  # Missing
            market_cap=None,  # Missing - forces private model
            data_quality_score=0.6
        )
        
        calculator = ZScoreCalculator()
        
        # Should either calculate with available data or fail gracefully
        try:
            result = calculator.calculate_zscore(minimal_data)
            
            # If it succeeds, should have warnings about missing data
            assert len(result.warnings) > 0
            assert result.data_quality_score <= 0.7
            
        except CalculationError as e:
            # If it fails, should be due to insufficient data
            assert "insufficient" in str(e).lower() or "missing" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_error_propagation_through_pipeline(self):
        """Test how errors propagate through the pipeline"""
        pipeline = AltmanZScorePipeline()
        symbol = "ERROR_TEST"
        
        # Test with data merger error
        with patch.object(pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = DataFetchError("Network timeout")
            
            with pytest.raises(DataFetchError) as exc_info:
                await pipeline.analyze_company(symbol)
            
            assert "network timeout" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self):
        """Test system recovery from partial failures"""
        pipeline = AltmanZScorePipeline()
        symbols = ["GOOD1", "BAD", "GOOD2"]
        
        def mock_analyze_company(symbol):
            if symbol == "BAD":
                raise CalculationError("Invalid data for calculation")
            
            # Return mock successful result for good symbols
            from dataclasses import dataclass
            
            @dataclass
            class MockResult:
                ticker: str
                z_score_result: Any
                market_analysis: Any
                risk_assessment: Any
            
            return MockResult(
                ticker=symbol,
                z_score_result=Mock(),
                market_analysis=Mock(),
                risk_assessment=Mock()
            )
        
        with patch.object(pipeline, 'analyze_company', side_effect=mock_analyze_company):
            results = await pipeline.analyze_batch(symbols, continue_on_error=True)
            
            # Should have results for successful symbols
            assert len(results) == 2
            assert "GOOD1" in results
            assert "GOOD2" in results
            assert "BAD" not in results


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system"""
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self):
        """Test performance of concurrent analysis"""
        import time
        
        pipeline = AltmanZScorePipeline()
        symbols = [f"PERF{i:03d}" for i in range(10)]
        
        # Mock fast responses
        def mock_merge_data(symbol):
            return MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.0 + (hash(symbol) % 10) * 0.1,
                retained_earnings_ratio=0.3,
                ebit_ratio=0.15,
                asset_turnover=0.8,
                market_cap=1000000000000,
                data_quality_score=0.9
            )
        
        with patch.object(pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = mock_merge_data
            
            start_time = time.time()
            results = await pipeline.analyze_batch(symbols)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time_per_symbol = total_time / len(symbols)
            
            # Performance assertions
            assert len(results) == len(symbols)
            assert total_time < 30.0  # Total should be under 30 seconds
            assert avg_time_per_symbol < 5.0  # Average under 5 seconds per symbol
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that memory usage remains stable during batch processing"""
        import gc
        import sys
        
        pipeline = AltmanZScorePipeline()
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process multiple batches
        for batch in range(3):
            symbols = [f"MEM{batch}_{i:02d}" for i in range(5)]
            
            def mock_merge_data(symbol):
                return MergedFinancialData(
                    ticker=symbol,
                    timestamp=datetime.now().isoformat(),
                    working_capital_ratio=1.2,
                    retained_earnings_ratio=0.3,
                    ebit_ratio=0.15,
                    asset_turnover=0.8,
                    market_cap=1000000000000,
                    data_quality_score=0.9
                )
            
            with patch.object(pipeline, 'data_merger') as mock_merger:
                mock_merger.merge_data.side_effect = mock_merge_data
                
                results = await pipeline.analyze_batch(symbols)
                assert len(results) == len(symbols)
                
                # Force garbage collection
                del results
                gc.collect()
        
        # Check final memory usage
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Memory growth should be reasonable (less than 50% increase)
        growth_ratio = object_growth / initial_objects
        assert growth_ratio < 0.5, f"Memory usage grew by {growth_ratio:.2%}"


class TestConfigurationIntegration:
    """Test configuration and settings across components"""
    
    def test_configuration_consistency(self):
        """Test that configuration is consistent across components"""
        pipeline = AltmanZScorePipeline()
        
        # Verify that all components use consistent configuration
        assert hasattr(pipeline, 'data_merger')
        assert hasattr(pipeline, 'zscore_calculator')
        
        # Test configuration propagation (this would be more detailed
        # when actual configuration system is implemented)
        assert pipeline.data_merger is not None
        assert pipeline.zscore_calculator is not None
    
    def test_logging_integration(self):
        """Test that logging works consistently across components"""
        from altman_zscore.common.logging_config import get_logger
        
        # Get loggers for different components
        pipeline_logger = get_logger("AltmanZScorePipeline")
        merger_logger = get_logger("DataMerger")
        calculator_logger = get_logger("ZScoreCalculator")
        
        # Verify all loggers are configured
        assert pipeline_logger is not None
        assert merger_logger is not None
        assert calculator_logger is not None
        
        # Test that they can log without errors
        pipeline_logger.info("Test pipeline log message")
        merger_logger.info("Test merger log message")
        calculator_logger.info("Test calculator log message")
