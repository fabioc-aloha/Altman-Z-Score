"""
Configuration management for the Altman Z-Score package.

This module provides centralized configuration handling with:
- Environment variable management with validation
- Default configuration values and overrides
- Configuration schema validation
- Support for different environments (dev, prod, test)
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path)

from .exceptions import ConfigurationError
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class APIConfig:
    """Configuration for external APIs."""
    sec_edgar_user_agent: str = ""
    yahoo_finance_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None  # Financial Modeling Prep API key
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    
    def __post_init__(self):
        """Validate API configuration."""
        # SEC EDGAR is no longer used in the current pipeline
        pass


@dataclass
class CacheConfig:
    """Configuration for caching."""
    cache_dir: str = ".cache"
    api_cache_ttl_hours: int = 48  # 48 hours for API call caching
    financial_cache_ttl_days: int = 2  # Align with API cache TTL
    cik_cache_ttl_days: int = 30  # CIK mappings change infrequently
    enable_cache: bool = True
    
    def __post_init__(self):
        """Ensure cache directory exists."""
        if self.enable_cache:
            Path(self.cache_dir).mkdir(exist_ok=True)


@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting."""
    sec_requests_per_second: float = 10.0
    yahoo_requests_per_second: float = 2.0
    finnhub_requests_per_second: float = 1.0
    fmp_requests_per_second: float = 2.0  # FMP allows 2 requests per second for free tier
    openai_requests_per_second: float = 1.0
    max_backoff_seconds: int = 64
    
    def to_rate_limits(self) -> Dict[str, float]:
        """Convert to rate limiter format."""
        return {
            "sec.gov": 1.0 / self.sec_requests_per_second,
            "finance.yahoo.com": 1.0 / self.yahoo_requests_per_second,
            "finnhub.io": 1.0 / self.finnhub_requests_per_second,
            "financialmodelingprep.com": 1.0 / self.fmp_requests_per_second,
            "openai.azure.com": 1.0 / self.openai_requests_per_second,
            "default": 1.0
        }


@dataclass
class AnalysisConfig:
    """Configuration for Z-Score analysis."""
    default_start_date: str = "2018-01-01"
    minimum_quarters_required: int = 4
    default_model: str = "original"
    enable_reality_checks: bool = True
    max_outlier_threshold: float = 5.0
    # FMP API data period - use "annual" for free plan, "quarter" for paid plans
    fmp_data_period: str = "annual"  # "annual" or "quarter"
    
    def __post_init__(self):
        """Validate analysis configuration."""
        if self.minimum_quarters_required < 1:
            raise ConfigurationError("minimum_quarters_required must be at least 1")
        if self.fmp_data_period not in ["annual", "quarter"]:
            raise ConfigurationError("fmp_data_period must be 'annual' or 'quarter'")


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    output_dir: str = "output"
    generate_csv: bool = True
    generate_json: bool = True
    generate_charts: bool = True
    generate_reports: bool = True
    chart_width: int = 1200
    chart_height: int = 800
    
    def __post_init__(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(exist_ok=True)


@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str = "development"
    debug: bool = False
    api: APIConfig = field(default_factory=APIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


class ConfigManager:
    """
    Centralized configuration manager for the application.
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration manager."""
        if self._config is None:
            self._config = self._load_config()
    
    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    def _load_config(self) -> AppConfig:
        """Load configuration from environment variables and files."""
        logger.info("Loading application configuration")
        
        # Load from environment variables
        config = AppConfig()
        
        # Environment        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
          # API Configuration
        config.api = APIConfig(
            sec_edgar_user_agent=os.getenv("SEC_EDGAR_USER_AGENT", ""),
            yahoo_finance_api_key=os.getenv("YAHOO_FINANCE_API_KEY"),
            finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
            fmp_api_key=os.getenv("FINANCIAL_MODELING_PREP_API_KEY"),  # Financial Modeling Prep API key
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Cache Configuration
        config.cache = CacheConfig(
            cache_dir=os.getenv("CACHE_DIR", ".cache"),
            financial_cache_ttl_days=int(os.getenv("FINANCIAL_CACHE_TTL_DAYS", "30")),
            cik_cache_ttl_days=int(os.getenv("CIK_CACHE_TTL_DAYS", "30")),
            enable_cache=os.getenv("ENABLE_CACHE", "true").lower() == "true"
        )
          # Rate Limiting Configuration
        config.rate_limit = RateLimitConfig(
            sec_requests_per_second=float(os.getenv("SEC_REQUESTS_PER_SECOND", "10.0")),
            yahoo_requests_per_second=float(os.getenv("YAHOO_REQUESTS_PER_SECOND", "2.0")),
            finnhub_requests_per_second=float(os.getenv("FINNHUB_REQUESTS_PER_SECOND", "1.0")),
            fmp_requests_per_second=float(os.getenv("FMP_REQUESTS_PER_SECOND", "2.0")),
            openai_requests_per_second=float(os.getenv("OPENAI_REQUESTS_PER_SECOND", "1.0")),
            max_backoff_seconds=int(os.getenv("MAX_BACKOFF_SECONDS", "64"))
        )
        
        # Analysis Configuration
        config.analysis = AnalysisConfig(
            default_start_date=os.getenv("DEFAULT_START_DATE", "2018-01-01"),
            minimum_quarters_required=int(os.getenv("MINIMUM_QUARTERS_REQUIRED", "4")),
            default_model=os.getenv("DEFAULT_MODEL", "original"),
            enable_reality_checks=os.getenv("ENABLE_REALITY_CHECKS", "true").lower() == "true",
            max_outlier_threshold=float(os.getenv("MAX_OUTLIER_THRESHOLD", "5.0")),
            # FMP data period setting (annual for free, quarter for paid)
            fmp_data_period=os.getenv("FMP_DATA_PERIOD", "annual")
        )
        
        # Output Configuration
        config.output = OutputConfig(
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            generate_csv=os.getenv("GENERATE_CSV", "true").lower() == "true",
            generate_json=os.getenv("GENERATE_JSON", "true").lower() == "true",
            generate_charts=os.getenv("GENERATE_CHARTS", "true").lower() == "true",
            generate_reports=os.getenv("GENERATE_REPORTS", "true").lower() == "true",
            chart_width=int(os.getenv("CHART_WIDTH", "1200")),
            chart_height=int(os.getenv("CHART_HEIGHT", "800"))
        )
        
        # Load from config file if it exists
        config_file = os.getenv("CONFIG_FILE", "config.json")
        if os.path.exists(config_file):
            config = self._merge_config_file(config, config_file)
        
        logger.info(f"Configuration loaded for environment: {config.environment}")
        return config
    
    def _get_required_env(self, *env_vars: str) -> str:
        """Get a required environment variable from a list of alternatives."""
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value:
                return value
        
        raise ConfigurationError(
            f"One of these environment variables is required: {', '.join(env_vars)}"
        )
    
    def _merge_config_file(self, config: AppConfig, config_file: str) -> AppConfig:
        """Merge configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Simple merge - in a real implementation, you'd want recursive merge
            for section, values in file_config.items():
                if hasattr(config, section) and isinstance(values, dict):
                    section_config = getattr(config, section)
                    for key, value in values.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)
            
            logger.info(f"Merged configuration from {config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config file {config_file}: {e}")
        
        return config
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration and return any issues.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate API configuration
        # SEC EDGAR validation removed - no longer used in current pipeline
        
        # Validate cache configuration
        if self.config.cache.enable_cache:
            cache_path = Path(self.config.cache.cache_dir)
            if not cache_path.exists():
                try:
                    cache_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create cache directory: {e}")
        
        # Validate output configuration
        output_path = Path(self.config.output.output_dir)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        return errors
    
    def get_env_template(self) -> str:
        """
        Generate a template .env file with all configuration options.
        
        Returns:
            String containing environment variable template
        """
        template = """# Altman Z-Score Configuration Template

# Environment
ENVIRONMENT=development
DEBUG=false

# API Configuration (Required)
SEC_EDGAR_USER_AGENT="YourCompany/1.0 your.email@domain.com"

# Optional API Keys
YAHOO_FINANCE_API_KEY="your-yahoo-api-key"
FINNHUB_API_KEY="your-finnhub-api-key"
AZURE_OPENAI_API_KEY="your-azure-openai-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Cache Configuration
CACHE_DIR=".cache"
FINANCIAL_CACHE_TTL_DAYS=30
CIK_CACHE_TTL_DAYS=30
ENABLE_CACHE=true

# Rate Limiting
SEC_REQUESTS_PER_SECOND=10.0
YAHOO_REQUESTS_PER_SECOND=2.0
FINNHUB_REQUESTS_PER_SECOND=1.0
OPENAI_REQUESTS_PER_SECOND=1.0
MAX_BACKOFF_SECONDS=64

# Analysis Settings
DEFAULT_START_DATE="2018-01-01"
MINIMUM_QUARTERS_REQUIRED=4
DEFAULT_MODEL="original"
ENABLE_REALITY_CHECKS=true
MAX_OUTLIER_THRESHOLD=5.0
FMP_DATA_PERIOD="annual"  # "annual" or "quarter"

# Output Settings
OUTPUT_DIR="output"
GENERATE_CSV=true
GENERATE_JSON=true
GENERATE_CHARTS=true
GENERATE_REPORTS=true
CHART_WIDTH=1200
CHART_HEIGHT=800

# Logging Configuration
LOG_DIR="logs"
LOG_CONSOLE_LEVEL="INFO"
LOG_FILE_LEVEL="DEBUG"
LOG_STRUCTURED=false
"""
        return template


# Global configuration instance (loaded lazily)
_config_manager = None

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config


def validate_configuration() -> None:
    """Validate the current configuration and raise errors if invalid."""
    config_manager = _config_manager or ConfigManager()
    errors = config_manager.validate_config()
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        raise ConfigurationError(error_msg)


# Example usage and testing
if __name__ == "__main__":
    # Get configuration
    config = get_config()
    
    # Print current configuration
    print("Current Configuration:")
    print(f"Environment: {config.environment}")
    print(f"Debug: {config.debug}")
    print(f"SEC User Agent: {config.api.sec_edgar_user_agent}")
    print(f"Cache Directory: {config.cache.cache_dir}")
    print(f"Output Directory: {config.output.output_dir}")
    
    # Validate configuration
    try:
        validate_configuration()
        print("Configuration is valid!")
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
    
    # Generate environment template
    config_manager = _config_manager or ConfigManager()
    template = config_manager.get_env_template()
    with open(".env.template", "w") as f:
        f.write(template)
    print("Generated .env.template file")
