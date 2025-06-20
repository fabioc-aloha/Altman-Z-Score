#!/usr/bin/env python3
"""
Test runner for AI-Powered Altman Z-Score Analysis
Runs tests with appropriate timeouts to prevent hanging
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the test suite with proper configuration"""
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Running Altman Z-Score Test Suite...")
    print("=" * 50)
      # Run different test categories
    test_categories = [
        ("Basic Functionality Tests", ["tests/test_basic_functionality.py"]),
        ("Data Processing Tests", ["tests/test_data_processing.py"]),
        ("CLI Integration Tests", ["tests/test_cli_integration.py", "tests/test_integration_main.py"]),
    ]
    
    all_passed = True
    
    for category, test_files in test_categories:
        print(f"\n📋 Running {category}...")
        
        # Filter to only existing test files
        existing_files = [f for f in test_files if os.path.exists(f)]
        
        if not existing_files:
            print(f"⚠️  No test files found for {category}")
            continue
            
        cmd = [sys.executable, "-m", "pytest"] + existing_files + ["-v", "--timeout=30"]
        
        try:
            result = subprocess.run(cmd, timeout=120)  # Overall timeout of 2 minutes
            if result.returncode == 0:
                print(f"✅ {category} passed")
            else:
                print(f"❌ {category} failed")
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"⏰ {category} timed out (hung)")
            all_passed = False
        except Exception as e:
            print(f"💥 {category} error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
