#!/usr/bin/env python3
"""
Pre-Release Validation Script for Altman Z-Score v4.3.0
Comprehensive system checks before running large portfolios (166+ companies)
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any

def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")

def print_check(check_name: str, status: bool, details: str = ""):
    """Print check result with status."""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {check_name}")
    if details:
        print(f"   {details}")

def check_version():
    """Verify version information."""
    print_header("VERSION VALIDATION")
    
    try:
        # Check main version file
        sys.path.insert(0, str(Path.cwd()))
        from altman_zscore._version import __version__, RELEASE_NAME, RELEASE_DATE
        
        expected_version = "4.5.0"
        expected_date = "2025-06-30"
        expected_name = "DIAMOND Release - Novel Retail Z-Score Model & Academic Excellence"
        
        version_ok = __version__ == expected_version
        date_ok = RELEASE_DATE == expected_date
        name_ok = RELEASE_NAME == expected_name
        
        print_check("Version Number", version_ok, f"Expected: {expected_version}, Got: {__version__}")
        print_check("Release Date", date_ok, f"Expected: {expected_date}, Got: {RELEASE_DATE}")
        print_check("Release Name", name_ok, f"Expected: {expected_name}, Got: {RELEASE_NAME}")
        
        return version_ok and date_ok and name_ok
        
    except Exception as e:
        print_check("Version Import", False, f"Error: {e}")
        return False

def check_configuration():
    """Test configuration system."""
    print_header("CONFIGURATION SYSTEM")
    
    try:
        from altman_zscore.common.config import ConfigManager
        
        # Test configuration loading
        config_manager = ConfigManager()
        config_loaded = config_manager.config is not None
        print_check("Configuration Loading", config_loaded)
        
        # Check critical configuration values
        if config_loaded:
            config = config_manager.config
            
            # Check if LLM config exists
            llm_config_ok = hasattr(config, 'llm')
            print_check("LLM Configuration", llm_config_ok)
            
            # Check analysis config
            analysis_config_ok = hasattr(config, 'analysis')
            print_check("Analysis Configuration", analysis_config_ok)
            
            # Check output config
            output_config_ok = hasattr(config, 'output')
            print_check("Output Configuration", output_config_ok)
            
            return llm_config_ok and analysis_config_ok and output_config_ok
        
        return False
        
    except Exception as e:
        print_check("Configuration System", False, f"Error: {e}")
        return False

def check_dependencies():
    """Check required dependencies."""
    print_header("DEPENDENCY VALIDATION")
    
    required_modules = [
        "pandas", "numpy", "requests", "matplotlib", "plotly", 
        "yfinance", "openai", "dotenv", "asyncio", "scipy",
        "pydantic", "pytest", "tabulate", "aiohttp", "jinja2", "tqdm"
    ]
    
    all_ok = True
    for module in required_modules:
        try:
            if module == "dotenv":
                import dotenv
            else:
                __import__(module)
            print_check(f"Module: {module}", True)
        except ImportError:
            print_check(f"Module: {module}", False, "Missing or incompatible version")
            all_ok = False
    
    return all_ok

def check_environment():
    """Check environment setup."""
    print_header("ENVIRONMENT VALIDATION")
    
    # Check for .env file
    env_file_exists = Path(".env").exists()
    print_check(".env File", env_file_exists, "Required for API keys and configuration")
    
    # Check critical directories
    required_dirs = ["logs", "output", "portfolios", "altman_zscore"]
    dirs_ok = True
    for dir_name in required_dirs:
        dir_exists = Path(dir_name).exists()
        dirs_ok = dirs_ok and dir_exists
        print_check(f"Directory: {dir_name}", dir_exists)
    
    return env_file_exists and dirs_ok

def calculate_processing_estimates(portfolio_size: int = 166):
    """Calculate processing time and resource estimates."""
    print_header("LARGE PORTFOLIO PROCESSING ESTIMATES")
    
    # Default v4.3.0 settings
    default_processes = 8
    default_quarters = 12
    enhanced_analysis = True
    
    print(f"📊 Portfolio Size: {portfolio_size} companies")
    print(f"⚡ Parallel Processes: {default_processes} (default v4.3.0)")
    print(f"📈 Historical Quarters: {default_quarters} (default v4.3.0)")
    print(f"🎯 Enhanced Analysis: {'Enabled' if enhanced_analysis else 'Disabled'}")
    print()
    
    # Estimate processing time per company
    base_time_per_company = 30  # seconds for basic analysis
    enhanced_multiplier = 2.0 if enhanced_analysis else 1.0
    quarters_multiplier = 1 + (default_quarters - 4) * 0.1  # Additional time for more quarters
    
    time_per_company = base_time_per_company * enhanced_multiplier * quarters_multiplier
    
    # Calculate batch processing
    companies_per_batch = portfolio_size // default_processes
    remainder = portfolio_size % default_processes
    
    # Time estimates
    sequential_time = portfolio_size * time_per_company
    parallel_time = companies_per_batch * time_per_company
    if remainder > 0:
        parallel_time += time_per_company  # Last batch
    
    print(f"📋 Batch Configuration:")
    print(f"   Companies per batch: {companies_per_batch}")
    print(f"   Batches with extra company: {remainder}")
    print()
    
    print(f"⏱️  Time Estimates:")
    print(f"   Per company: {time_per_company:.1f} seconds")
    print(f"   Sequential processing: {sequential_time/60:.1f} minutes ({sequential_time/3600:.1f} hours)")
    print(f"   Parallel processing: {parallel_time/60:.1f} minutes ({parallel_time/3600:.1f} hours)")
    print(f"   Speedup: {sequential_time/parallel_time:.1f}x faster")
    print()
    
    # API call estimates
    base_api_calls_per_company = 5
    enhanced_api_calls = 12 if enhanced_analysis else 5
    quarterly_api_calls = default_quarters * 2  # Financial + market data
    
    total_api_calls = portfolio_size * (enhanced_api_calls + quarterly_api_calls)
    
    print(f"🔗 API Usage Estimates:")
    print(f"   API calls per company: {enhanced_api_calls + quarterly_api_calls}")
    print(f"   Total API calls: {total_api_calls:,}")
    print(f"   Estimated data transfer: {total_api_calls * 50 / 1024:.1f} MB")
    print()
    
    # Resource recommendations
    print(f"💻 System Recommendations:")
    print(f"   RAM: {default_processes * 512} MB minimum")
    print(f"   Disk space: {portfolio_size * 5} MB for outputs")
    print(f"   Network: Stable connection for {total_api_calls:,} API calls")
    
    return {
        "parallel_time_minutes": parallel_time / 60,
        "total_api_calls": total_api_calls,
        "companies_per_batch": companies_per_batch
    }

def check_scripts():
    """Validate PowerShell scripts."""
    print_header("SCRIPT VALIDATION")
    
    scripts = [
        "run_parallel_portfolio.ps1",
        "analyze_portfolio.ps1", 
        "analyze_portfolio.bat"
    ]
    
    all_ok = True
    for script in scripts:
        script_exists = Path(script).exists()
        all_ok = all_ok and script_exists
        print_check(f"Script: {script}", script_exists)
    
    return all_ok

def main():
    """Run comprehensive pre-release validation."""
    print_header("ALTMAN Z-SCORE v4.3.0 PRE-RELEASE VALIDATION")
    print("Comprehensive system checks for large portfolio processing")
    
    # Track overall status
    checks = []
    
    # Run all validation checks
    checks.append(("Version", check_version()))
    checks.append(("Configuration", check_configuration()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Environment", check_environment()))
    checks.append(("Scripts", check_scripts()))
    
    # Calculate processing estimates
    estimates = calculate_processing_estimates(166)
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed_checks = sum(1 for _, status in checks if status)
    total_checks = len(checks)
    
    for check_name, status in checks:
        print_check(check_name, status)
    
    print(f"\n📊 Overall Status: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 SYSTEM READY FOR v4.3.0 RELEASE!")
        print("✅ All validation checks passed")
        print(f"✅ Ready for large portfolio processing ({estimates['companies_per_batch']} companies per batch)")
        print(f"✅ Estimated processing time: {estimates['parallel_time_minutes']:.1f} minutes")
        print(f"✅ API efficiency: {estimates['total_api_calls']:,} total calls")
        
        print("\n🚀 Recommended command for 166-company portfolio:")
        print("   .\\run_parallel_portfolio.ps1 -PortfolioFile 'your_166_companies.txt'")
        print("   (Uses v4.3.0 defaults: 8 processes, 12 quarters, enhanced analysis)")
        
        return 0
    else:
        print("\n⚠️  VALIDATION ISSUES DETECTED")
        print("❌ Some checks failed - review issues before release")
        print(f"❌ {total_checks - passed_checks} issues need attention")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
