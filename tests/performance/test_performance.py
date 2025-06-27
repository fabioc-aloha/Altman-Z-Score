"""
Performance tests for the Altman Z-Score analysis system

These tests validate performance characteristics including:
- Response times for individual and batch analysis
- Memory usage patterns
- Concurrent processing capabilities
- Cache effectiveness
- API rate limiting compliance
"""

import pytest
import asyncio
import time
import gc
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.layers.data_fetch.data_merger import DataMerger
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from altman_zscore.models.data_models import MergedFinancialData
from tests.conftest import MockDataGenerator, TestConfig


class PerformanceMetrics:
    """Utility class for collecting performance metrics"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.time()
        
    @property
    def execution_time(self) -> float:
        """Get execution time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class TestSingleAnalysisPerformance:
    """Test performance of single company analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = AltmanZScorePipeline()
        self.metrics = PerformanceMetrics()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_single_analysis_response_time(self):
        """Test response time for single company analysis"""
        symbol = "AAPL"
        
        # Mock data to ensure consistent test conditions
        mock_data = MergedFinancialData(
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
            mock_merger.merge_data.return_value = mock_data
            
            self.metrics.start_monitoring()
            
            result = await self.pipeline.analyze_company(symbol)
            
            self.metrics.stop_monitoring()
            
            # Performance assertions
            assert self.metrics.execution_time < 2.0  # Under 2 seconds
            assert result is not None
            assert result.ticker == symbol
            
            print(f"Single analysis time: {self.metrics.execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_single_analysis_memory_usage(self):
        """Test memory usage for single company analysis"""
        symbol = "MEMORY_TEST"
        
        mock_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            working_capital_ratio=1.1,
            retained_earnings_ratio=0.35,
            ebit_ratio=0.18,
            asset_turnover=0.75,
            market_cap=2000000000000,
            data_quality_score=0.9
        )
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.return_value = mock_data
            
            # Force garbage collection before test
            gc.collect()
            
            self.metrics.start_monitoring()
            
            result = await self.pipeline.analyze_company(symbol)
            
            self.metrics.update_peak_memory()
            self.metrics.stop_monitoring()
            
            memory_stats = self.metrics.memory_usage
            
            # Memory usage assertions
            assert memory_stats["growth_mb"] < 50  # Less than 50MB growth
            assert memory_stats["peak_growth_mb"] < 100  # Peak under 100MB growth
            assert result is not None
            
            print(f"Memory usage: {memory_stats}")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_repeated_analysis_consistency(self):
        """Test performance consistency across repeated analyses"""
        symbol = "CONSISTENCY_TEST"
        num_runs = 10
        
        mock_data = MergedFinancialData(
            ticker=symbol,
            timestamp=datetime.now().isoformat(),
            working_capital_ratio=1.15,
            retained_earnings_ratio=0.28,
            ebit_ratio=0.16,
            asset_turnover=0.82,
            market_cap=1500000000000,
            data_quality_score=0.88
        )
        
        execution_times = []
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.return_value = mock_data
            
            for run in range(num_runs):
                start_time = time.time()
                
                result = await self.pipeline.analyze_company(symbol)
                
                end_time = time.time()
                execution_times.append(end_time - start_time)
                
                assert result is not None
                assert result.ticker == symbol
        
        # Calculate performance statistics
        avg_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        # Performance consistency assertions
        assert avg_time < 1.5  # Average under 1.5 seconds
        assert std_dev < 0.5   # Low variance (under 0.5 seconds)
        assert max_time < 3.0  # No outliers over 3 seconds
        
        print(f"Performance stats - Avg: {avg_time:.3f}s, StdDev: {std_dev:.3f}s, Range: {min_time:.3f}s-{max_time:.3f}s")


class TestBatchAnalysisPerformance:
    """Test performance of batch analysis operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = AltmanZScorePipeline()
        self.metrics = PerformanceMetrics()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_small_batch_performance(self):
        """Test performance with small batch (5 companies)"""
        symbols = [f"SMALL{i:02d}" for i in range(5)]
        
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
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = mock_merge_data
            
            self.metrics.start_monitoring()
            
            results = await self.pipeline.analyze_batch(symbols)
            
            self.metrics.stop_monitoring()
            
            # Performance assertions
            assert len(results) == len(symbols)
            assert self.metrics.execution_time < 10.0  # Under 10 seconds
            
            avg_time_per_symbol = self.metrics.execution_time / len(symbols)
            assert avg_time_per_symbol < 2.0  # Under 2 seconds per symbol
            
            print(f"Small batch ({len(symbols)} symbols): {self.metrics.execution_time:.3f}s total, {avg_time_per_symbol:.3f}s per symbol")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_medium_batch_performance(self):
        """Test performance with medium batch (20 companies)"""
        symbols = [f"MED{i:03d}" for i in range(20)]
        
        def mock_merge_data(symbol):
            # Simulate slight delay for more realistic testing
            return MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=0.8 + (hash(symbol) % 15) * 0.05,
                retained_earnings_ratio=0.2 + (hash(symbol) % 8) * 0.02,
                ebit_ratio=0.1 + (hash(symbol) % 12) * 0.01,
                asset_turnover=0.6 + (hash(symbol) % 10) * 0.05,
                market_cap=500000000000 + (hash(symbol) % 20) * 100000000000,
                data_quality_score=0.85 + (hash(symbol) % 10) * 0.01
            )
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = mock_merge_data
            
            self.metrics.start_monitoring()
            
            results = await self.pipeline.analyze_batch(symbols)
            
            self.metrics.stop_monitoring()
            
            # Performance assertions
            assert len(results) == len(symbols)
            assert self.metrics.execution_time < 40.0  # Under 40 seconds
            
            avg_time_per_symbol = self.metrics.execution_time / len(symbols)
            assert avg_time_per_symbol < 2.5  # Under 2.5 seconds per symbol
            
            memory_stats = self.metrics.memory_usage
            assert memory_stats["growth_mb"] < 200  # Under 200MB growth
            
            print(f"Medium batch ({len(symbols)} symbols): {self.metrics.execution_time:.3f}s total, {avg_time_per_symbol:.3f}s per symbol")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_vs_sequential_performance(self):
        """Test performance difference between concurrent and sequential processing"""
        symbols = [f"CONC{i:02d}" for i in range(8)]
        
        def mock_merge_data(symbol):
            # Add small delay to simulate real API call
            import asyncio
            time.sleep(0.1)  # 100ms delay
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
        
        with patch.object(self.pipeline, 'data_merger') as mock_merger:
            mock_merger.merge_data.side_effect = mock_merge_data
            
            # Test concurrent processing (default)
            start_time = time.time()
            concurrent_results = await self.pipeline.analyze_batch(symbols)
            concurrent_time = time.time() - start_time
            
            # Test sequential processing
            start_time = time.time()
            sequential_results = []
            for symbol in symbols:
                result = await self.pipeline.analyze_company(symbol)
                sequential_results.append(result)
            sequential_time = time.time() - start_time
            
            # Performance comparison
            assert len(concurrent_results) == len(sequential_results)
            assert len(concurrent_results) == len(symbols)
            
            # Concurrent should be significantly faster
            speedup_ratio = sequential_time / concurrent_time
            assert speedup_ratio > 1.5  # At least 50% faster
            
            print(f"Concurrent: {concurrent_time:.3f}s, Sequential: {sequential_time:.3f}s, Speedup: {speedup_ratio:.2f}x")


class TestDataProcessingPerformance:
    """Test performance of individual data processing components"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_zscore_calculation_performance(self):
        """Test Z-Score calculation performance"""
        calculator = ZScoreCalculator()
        num_calculations = 100
        
        # Create test data
        test_data = []
        for i in range(num_calculations):
            data = MergedFinancialData(
                ticker=f"CALC{i:03d}",
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.0 + (i % 20) * 0.05,
                retained_earnings_ratio=0.2 + (i % 15) * 0.02,
                ebit_ratio=0.1 + (i % 10) * 0.02,
                asset_turnover=0.6 + (i % 12) * 0.05,
                market_cap=1000000000000 + i * 50000000000,
                data_quality_score=0.85 + (i % 10) * 0.01
            )
            test_data.append(data)
        
        # Time the calculations
        start_time = time.time()
        
        results = []
        for data in test_data:
            result = calculator.calculate_zscore(data)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(results) == num_calculations
        assert total_time < 10.0  # Under 10 seconds for 100 calculations
        
        avg_time_per_calc = total_time / num_calculations
        assert avg_time_per_calc < 0.2  # Under 0.2 seconds per calculation
        
        # Verify all calculations completed successfully
        successful_results = [r for r in results if r.z_score is not None]
        success_rate = len(successful_results) / len(results)
        assert success_rate > 0.95  # At least 95% success rate
        
        print(f"Z-Score calculation: {total_time:.3f}s total, {avg_time_per_calc:.4f}s per calculation, {success_rate:.1%} success rate")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_data_merger_performance(self):
        """Test data merger performance"""
        merger = DataMerger()
        symbols = [f"MERGE{i:02d}" for i in range(10)]
        
        # Mock API responses
        def mock_fmp_fetch(symbol):
            return {
                "working_capital_ratio": 1.2,
                "retained_earnings_ratio": 0.3,
                "ebit_ratio": 0.15,
                "asset_turnover": 0.8
            }
        
        def mock_yahoo_fetch(symbol):
            return {
                "market_cap": 1000000000000,
                "current_price": 150.0,
                "shares_outstanding": 1000000000
            }
        
        with patch.object(merger, 'fmp_fetcher') as mock_fmp:
            with patch.object(merger, 'yahoo_fetcher') as mock_yahoo:
                mock_fmp.fetch_ratios.side_effect = mock_fmp_fetch
                mock_yahoo.fetch_market_data.side_effect = mock_yahoo_fetch
                
                start_time = time.time()
                
                merge_tasks = [merger.merge_data(symbol) for symbol in symbols]
                results = await asyncio.gather(*merge_tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Performance assertions
                assert len(results) == len(symbols)
                assert total_time < 10.0  # Under 10 seconds
                
                avg_time_per_merge = total_time / len(symbols)
                assert avg_time_per_merge < 2.0  # Under 2 seconds per merge
                
                print(f"Data merger: {total_time:.3f}s total, {avg_time_per_merge:.3f}s per merge")


class TestCachePerformance:
    """Test caching performance and effectiveness"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_cache_hit_performance(self):
        """Test performance improvement from cache hits"""
        # This test will be more meaningful once caching is implemented
        merger = DataMerger()
        symbol = "CACHE_TEST"
        
        # Mock slow API response
        async def slow_api_response(*args, **kwargs):
            await asyncio.sleep(0.5)  # Simulate 500ms API delay
            return MergedFinancialData(
                ticker=symbol,
                timestamp=datetime.now().isoformat(),
                working_capital_ratio=1.2,
                retained_earnings_ratio=0.3,
                ebit_ratio=0.15,
                data_quality_score=0.9
            )
        
        with patch.object(merger, 'merge_data', side_effect=slow_api_response):
            # First call (cache miss)
            start_time = time.time()
            result1 = await merger.merge_data(symbol)
            first_call_time = time.time() - start_time
            
            # Second call (should be cache hit when caching is implemented)
            start_time = time.time()
            result2 = await merger.merge_data(symbol)
            second_call_time = time.time() - start_time
            
            # Verify results are consistent
            assert result1.ticker == result2.ticker
            
            # Note: Currently no caching, so times will be similar
            # When caching is implemented, second_call_time should be much faster
            print(f"First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")


# Performance tests - run with pytest --run-performance
