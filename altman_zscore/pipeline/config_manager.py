"""
Pipeline Configuration - Centralized configuration management

This module provides centralized configuration handling for the pipeline,
separating configuration logic from the main orchestration.

Key Features:
- Environment-based configuration
- Parameter validation
- Feature flag management
- Resource allocation settings
- Output path management
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..common.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EnhancedAnalysisConfig:
    """Configuration for enhanced analysis features."""
    enabled: bool = False
    quarters: int = 4
    batch_size: int = 10
    min_quarters: int = 4
    max_quarters: int = 20
    default_batch_size: int = 10
    max_batch_size: int = 50


@dataclass
class FeatureFlags:
    """Feature flags for optional pipeline components."""
    include_market_analysis: bool = True
    include_comprehensive_ai_analysis: bool = True
    include_ai_insights: bool = True
    generate_charts: bool = True
    generate_reports: bool = True
    enable_progress_bars: bool = True
    enable_timing_display: bool = True
    enable_detailed_logging: bool = False


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    base_path: str = "output"
    generate_csv: bool = True
    generate_json: bool = True
    generate_html_reports: bool = True
    generate_summary_reports: bool = True
    generate_charts: bool = True
    chart_format: str = "html"  # html, png, pdf
    backup_existing: bool = False


@dataclass
class ResourceConfig:
    """Configuration for resource allocation."""
    max_concurrent_requests: int = 5
    request_timeout_seconds: int = 30
    max_memory_usage_mb: int = 2048
    temp_dir: Optional[str] = None
    cache_enabled: bool = True
    cache_ttl_hours: int = 24


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    # Core settings
    ticker: str
    forced_model: Optional[str] = None
    
    # Feature configuration
    features: FeatureFlags = field(default_factory=FeatureFlags)
    enhanced_analysis: EnhancedAnalysisConfig = field(default_factory=EnhancedAnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    
    # Runtime settings
    debug_mode: bool = False
    validate_inputs: bool = True
    fail_fast: bool = False
    retry_failed_steps: bool = True
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        errors = []
        
        # Validate ticker
        if not self.ticker or not isinstance(self.ticker, str):
            errors.append("Ticker must be a non-empty string")
        
        # Validate enhanced analysis settings
        if self.enhanced_analysis.enabled:
            if self.enhanced_analysis.quarters < self.enhanced_analysis.min_quarters:
                errors.append(f"Quarters must be at least {self.enhanced_analysis.min_quarters}")
            if self.enhanced_analysis.quarters > self.enhanced_analysis.max_quarters:
                errors.append(f"Quarters cannot exceed {self.enhanced_analysis.max_quarters}")
            if self.enhanced_analysis.batch_size > self.enhanced_analysis.max_batch_size:
                errors.append(f"Batch size cannot exceed {self.enhanced_analysis.max_batch_size}")
        
        # Validate output paths
        try:
            Path(self.output.base_path).resolve()
        except Exception as e:
            errors.append(f"Invalid output base path: {e}")
        
        # Validate forced model
        if self.forced_model:
            from ..common.constants import ZSCORE_MODELS
            valid_models = list(ZSCORE_MODELS.keys())
            if self.forced_model.lower().replace(" ", "_").replace("-", "_") not in valid_models:
                errors.append(f"Invalid forced model. Valid options: {valid_models}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ticker': self.ticker,
            'forced_model': self.forced_model,
            'features': {
                'include_market_analysis': self.features.include_market_analysis,
                'include_comprehensive_ai_analysis': self.features.include_comprehensive_ai_analysis,
                'include_ai_insights': self.features.include_ai_insights,
                'generate_charts': self.features.generate_charts,
                'generate_reports': self.features.generate_reports,
                'enable_progress_bars': self.features.enable_progress_bars,
                'enable_timing_display': self.features.enable_timing_display,
                'enable_detailed_logging': self.features.enable_detailed_logging
            },
            'enhanced_analysis': {
                'enabled': self.enhanced_analysis.enabled,
                'quarters': self.enhanced_analysis.quarters,
                'batch_size': self.enhanced_analysis.batch_size
            },
            'output': {
                'base_path': self.output.base_path,
                'generate_csv': self.output.generate_csv,
                'generate_json': self.output.generate_json,
                'generate_html_reports': self.output.generate_html_reports,
                'generate_summary_reports': self.output.generate_summary_reports,
                'generate_charts': self.output.generate_charts,
                'chart_format': self.output.chart_format,
                'backup_existing': self.output.backup_existing
            },
            'resources': {
                'max_concurrent_requests': self.resources.max_concurrent_requests,
                'request_timeout_seconds': self.resources.request_timeout_seconds,
                'max_memory_usage_mb': self.resources.max_memory_usage_mb,
                'cache_enabled': self.resources.cache_enabled,
                'cache_ttl_hours': self.resources.cache_ttl_hours
            },
            'runtime': {
                'debug_mode': self.debug_mode,
                'validate_inputs': self.validate_inputs,
                'fail_fast': self.fail_fast,
                'retry_failed_steps': self.retry_failed_steps,
                'max_retries': self.max_retries
            }
        }


class ConfigurationManager:
    """Manages pipeline configuration from various sources."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.logger = get_logger(self.__class__.__name__)
    
    def create_config_from_args(
        self,
        ticker: str,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_ai_insights: bool = True,
        include_comprehensive_ai_analysis: bool = True,
        include_market_analysis: bool = True,
        forced_model: Optional[str] = None,
        quarters: int = 4,
        enhanced_analysis: bool = False,
        batch_size: int = 10,
        output_base_path: str = "output",
        **kwargs
    ) -> PipelineConfig:
        """
        Create pipeline configuration from function arguments.
        
        Args:
            ticker: Stock ticker to analyze
            generate_charts: Whether to generate charts
            generate_reports: Whether to generate reports
            include_ai_insights: Whether to include AI insights
            include_comprehensive_ai_analysis: Whether to include comprehensive AI analysis
            include_market_analysis: Whether to include market analysis
            forced_model: Optional forced Z-Score model
            quarters: Number of quarters for analysis
            enhanced_analysis: Whether to enable enhanced features
            batch_size: Batch size for processing
            output_base_path: Base path for output files
            **kwargs: Additional configuration options
            
        Returns:
            Complete pipeline configuration
        """
        # Create feature flags
        features = FeatureFlags(
            include_market_analysis=include_market_analysis,
            include_comprehensive_ai_analysis=include_comprehensive_ai_analysis,
            include_ai_insights=include_ai_insights,
            generate_charts=generate_charts,
            generate_reports=generate_reports
        )
        
        # Create enhanced analysis config
        enhanced_config = EnhancedAnalysisConfig(
            enabled=enhanced_analysis,
            quarters=quarters,
            batch_size=batch_size
        )
        
        # Create output config
        output_config = OutputConfig(
            base_path=output_base_path,
            generate_charts=generate_charts,
            generate_html_reports=generate_reports,
            generate_summary_reports=generate_reports
        )
        
        # Create main config
        config = PipelineConfig(
            ticker=ticker,
            forced_model=forced_model,
            features=features,
            enhanced_analysis=enhanced_config,
            output=output_config
        )
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self.logger.warning(f"Unknown configuration option: {key}")
        
        self.logger.info(f"Created configuration for {ticker} with enhanced_analysis={enhanced_analysis}")
        return config
    
    def create_config_from_env(self, ticker: str) -> PipelineConfig:
        """
        Create pipeline configuration from environment variables.
        
        Args:
            ticker: Stock ticker to analyze
            
        Returns:
            Configuration based on environment variables
        """
        # Read environment variables with defaults
        enhanced_analysis = os.getenv('FMP_ENHANCED_MODE', '0') == '1'
        quarters = int(os.getenv('ANALYSIS_QUARTERS', '4'))
        batch_size = int(os.getenv('BATCH_SIZE', '10'))
        
        features = FeatureFlags(
            include_market_analysis=os.getenv('INCLUDE_MARKET_ANALYSIS', 'true').lower() == 'true',
            include_comprehensive_ai_analysis=os.getenv('INCLUDE_AI_ANALYSIS', 'true').lower() == 'true',
            include_ai_insights=os.getenv('INCLUDE_AI_INSIGHTS', 'true').lower() == 'true',
            generate_charts=os.getenv('GENERATE_CHARTS', 'true').lower() == 'true',
            generate_reports=os.getenv('GENERATE_REPORTS', 'true').lower() == 'true'
        )
        
        enhanced_config = EnhancedAnalysisConfig(
            enabled=enhanced_analysis,
            quarters=quarters,
            batch_size=batch_size
        )
        
        output_config = OutputConfig(
            base_path=os.getenv('OUTPUT_BASE_PATH', 'output')
        )
        
        config = PipelineConfig(
            ticker=ticker,
            forced_model=os.getenv('FORCED_MODEL'),
            features=features,
            enhanced_analysis=enhanced_config,
            output=output_config,
            debug_mode=os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        )
        
        self.logger.info(f"Created configuration from environment for {ticker}")
        return config
    
    def apply_environment_overrides(self, config: PipelineConfig) -> PipelineConfig:
        """
        Apply environment variable overrides to existing configuration.
        
        Args:
            config: Base configuration to modify
            
        Returns:
            Modified configuration with environment overrides
        """
        # Enhanced analysis settings
        if os.getenv('FMP_ENHANCED_MODE') == '1':
            config.enhanced_analysis.enabled = True
            
        if os.getenv('ANALYSIS_QUARTERS'):
            config.enhanced_analysis.quarters = int(os.getenv('ANALYSIS_QUARTERS'))
            
        if os.getenv('BATCH_SIZE'):
            config.enhanced_analysis.batch_size = int(os.getenv('BATCH_SIZE'))
        
        # Feature flags
        if os.getenv('INCLUDE_MARKET_ANALYSIS'):
            config.features.include_market_analysis = os.getenv('INCLUDE_MARKET_ANALYSIS').lower() == 'true'
            
        if os.getenv('GENERATE_CHARTS'):
            config.features.generate_charts = os.getenv('GENERATE_CHARTS').lower() == 'true'
        
        # Output settings
        if os.getenv('OUTPUT_BASE_PATH'):
            config.output.base_path = os.getenv('OUTPUT_BASE_PATH')
        
        # Runtime settings
        if os.getenv('DEBUG_MODE'):
            config.debug_mode = os.getenv('DEBUG_MODE').lower() == 'true'
            
        if os.getenv('FAIL_FAST'):
            config.fail_fast = os.getenv('FAIL_FAST').lower() == 'true'
        
        # Re-validate after applying overrides
        config.validate()
        
        self.logger.info(f"Applied environment overrides to configuration for {config.ticker}")
        return config
    
    def get_legacy_args(self, config: PipelineConfig) -> Dict[str, Any]:
        """
        Convert modern configuration back to legacy argument format.
        Useful for compatibility with existing code.
        
        Args:
            config: Modern pipeline configuration
            
        Returns:
            Dictionary of legacy-style arguments
        """
        return {
            'ticker': config.ticker,
            'generate_charts': config.features.generate_charts,
            'generate_reports': config.features.generate_reports,
            'include_ai_insights': config.features.include_ai_insights,
            'include_comprehensive_ai_analysis': config.features.include_comprehensive_ai_analysis,
            'include_market_analysis': config.features.include_market_analysis,
            'forced_model': config.forced_model,
            'quarters': config.enhanced_analysis.quarters,
            'enhanced_analysis': config.enhanced_analysis.enabled,
            'batch_size': config.enhanced_analysis.batch_size
        }
