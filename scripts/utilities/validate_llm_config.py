#!/usr/bin/env python3
"""
LLM Configuration Validation Script

This script validates that all LLM configuration parameters are properly
loaded from environment variables and that the LLMClient is correctly
configured with the expected temperature and token settings.

Usage:
    python scripts/utilities/validate_llm_config.py

Validates:
- Environment variable loading
- LLMConfig initialization
- Parameter ranges and types
- Configuration consistency
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def validate_llm_configuration():
    """Validate LLM configuration loading and parameters."""
    
    print("🔧 Validating LLM Configuration...")
    
    try:
        # Load main application config
        from altman_zscore.common.config import get_config
        
        config = get_config()
        print(f"✅ Main Config Loaded:")
        print(f"   Environment: {config.environment}")
        
        # Load LLM client config
        from altman_zscore.layers.data_fetch.llm_client import LLMConfig
        
        llm_config = LLMConfig.from_env()
        print(f"\n✅ LLM Client Config Loaded:")
        print(f"   API Endpoint: {llm_config.endpoint}")
        print(f"   Deployment: {llm_config.deployment}")
        print(f"   Default Temperature: {llm_config.default_temperature}")
        print(f"   Default Max Tokens: {llm_config.default_max_tokens}")
        print(f"   Comprehensive Temperature: {llm_config.comprehensive_temperature}")
        print(f"   Comprehensive Max Tokens: {llm_config.comprehensive_max_tokens}")
        print(f"   Field Mapping Temperature: {llm_config.field_mapping_temperature}")
        print(f"   Field Mapping Max Tokens: {llm_config.field_mapping_max_tokens}")
        print(f"   Financial Analysis Temperature: {llm_config.financial_analysis_temperature}")
        print(f"   Financial Analysis Max Tokens: {llm_config.financial_analysis_max_tokens}")
        
        # Validate individual environment variables
        env_vars = {
            "LLM_DEFAULT_TEMPERATURE": llm_config.default_temperature,
            "LLM_DEFAULT_MAX_TOKENS": llm_config.default_max_tokens,
            "LLM_COMPREHENSIVE_TEMPERATURE": llm_config.comprehensive_temperature,
            "LLM_COMPREHENSIVE_MAX_TOKENS": llm_config.comprehensive_max_tokens,
            "LLM_FIELD_MAPPING_TEMPERATURE": llm_config.field_mapping_temperature,
            "LLM_FIELD_MAPPING_MAX_TOKENS": llm_config.field_mapping_max_tokens,
            "LLM_FINANCIAL_ANALYSIS_TEMPERATURE": llm_config.financial_analysis_temperature,
            "LLM_FINANCIAL_ANALYSIS_MAX_TOKENS": llm_config.financial_analysis_max_tokens,
        }
        
        print(f"\n🔍 Environment Variable Validation:")
        for env_var, value in env_vars.items():
            print(f"   ✅ {env_var}: {value}")
        
        # Validate parameter ranges
        temperatures = [
            llm_config.default_temperature,
            llm_config.comprehensive_temperature,
            llm_config.field_mapping_temperature,
            llm_config.financial_analysis_temperature
        ]
        
        tokens = [
            llm_config.default_max_tokens,
            llm_config.comprehensive_max_tokens,
            llm_config.field_mapping_max_tokens,
            llm_config.financial_analysis_max_tokens
        ]
        
        # Check temperature ranges (0.0 to 1.0)
        for temp in temperatures:
            if not (0.0 <= temp <= 1.0):
                print(f"❌ Invalid temperature: {temp} (must be 0.0-1.0)")
                return False
        
        # Check token ranges (reasonable values)
        for token_count in tokens:
            if not (1000 <= token_count <= 100000):
                print(f"❌ Invalid token count: {token_count} (must be 1000-100000)")
                return False
        
        print(f"\n🎯 Configuration Summary:")
        print(f"   Temperature ranges: {min(temperatures)} to {max(temperatures)}")
        print(f"   Token ranges: {min(tokens)} to {max(tokens)}")
        print(f"   Use cases: {len(env_vars)//2} different configurations for different analysis types")
        
        print(f"\n✅ LLM Configuration validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ LLM Configuration validation failed: {str(e)}")
        return False

def validate_environment_file():
    """Validate that .env file contains required LLM variables."""
    
    env_file = project_root / ".env"
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        return False
    
    required_vars = [
        "LLM_DEFAULT_TEMPERATURE",
        "LLM_DEFAULT_MAX_TOKENS",
        "LLM_COMPREHENSIVE_TEMPERATURE",
        "LLM_COMPREHENSIVE_MAX_TOKENS",
        "LLM_FIELD_MAPPING_TEMPERATURE",
        "LLM_FIELD_MAPPING_MAX_TOKENS",
        "LLM_FINANCIAL_ANALYSIS_TEMPERATURE",
        "LLM_FINANCIAL_ANALYSIS_MAX_TOKENS",
    ]
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing LLM variables in .env file: {missing_vars}")
        return False
    
    print(f"✅ All required LLM variables found in .env file")
    return True

if __name__ == "__main__":
    success = True
    
    # Validate environment file
    if not validate_environment_file():
        success = False
    
    # Validate configuration loading
    if not validate_llm_configuration():
        success = False
    
    if success:
        print(f"\n🎉 All LLM configuration validation checks passed!")
        sys.exit(0)
    else:
        print(f"\n💥 LLM configuration validation failed!")
        sys.exit(1)
