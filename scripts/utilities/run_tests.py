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
    
    print("🧪 Running Altman Z-Score Infrastructure Test Suite...")
    
    # Run new layered architecture tests
    test_categories = [
        ("Infrastructure Tests", ["tests/test_layers/test_common/"]),
    ]
    
    all_passed = True
    
    for category, test_paths in test_categories:
        print(f"\n📋 Running {category}...")
        
        # Filter to only existing test paths
        existing_paths = [f for f in test_paths if os.path.exists(f)]
        
        if not existing_paths:
            print(f"⚠️  No test paths found for {category}")
            continue
            
        cmd = [sys.executable, "-m", "pytest"] + existing_paths + ["-v", "--timeout=30"]
        
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
    
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
