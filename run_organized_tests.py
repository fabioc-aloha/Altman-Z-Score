"""
Master Test Runner for Organized Test Structure

This script provides easy access to run tests from the organized test structure.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_category(category: str):
    """Run all tests in a specific category."""
    category_path = Path("tests") / category
    if not category_path.exists():
        print(f"❌ Category '{category}' not found")
        return False
    
    print(f"🧪 Running {category.upper()} tests...")
    print("=" * 50)
    
    # Find all test files in the category
    test_files = list(category_path.glob("test_*.py"))
    if not test_files:
        test_files = list(category_path.glob("*.py"))
    
    if not test_files:
        print(f"❌ No test files found in {category}")
        return False
    
    success_count = 0
    for test_file in test_files:
        print(f"\n📝 Running {test_file.name}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ {test_file.name} - PASSED")
                success_count += 1
            else:
                print(f"❌ {test_file.name} - FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file.name} - TIMEOUT")
        except Exception as e:
            print(f"❌ {test_file.name} - ERROR: {e}")
    
    print(f"\n📊 {category.upper()} Results: {success_count}/{len(test_files)} passed")
    return success_count == len(test_files)

def run_specific_test(test_path: str):
    """Run a specific test file."""
    test_file = Path("tests") / test_path
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🧪 Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, str(test_file)], timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def list_test_categories():
    """List all available test categories."""
    tests_dir = Path("tests")
    categories = []
    
    for item in tests_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            test_count = len(list(item.glob("*.py")))
            categories.append((item.name, test_count))
    
    # Also check for files directly in tests/
    direct_tests = len(list(tests_dir.glob("test_*.py")))
    if direct_tests > 0:
        categories.append(("root", direct_tests))
    
    return categories

def main():
    """Main test runner interface."""
    if len(sys.argv) < 2:
        print("🧪 Altman Z-Score Test Runner")
        print("=" * 40)
        print("Usage:")
        print("  python run_organized_tests.py <category>")
        print("  python run_organized_tests.py <category/test_file.py>")
        print("  python run_organized_tests.py list")
        print()
        print("Available categories:")
        categories = list_test_categories()
        for category, count in categories:
            print(f"  {category:<15} ({count} tests)")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        categories = list_test_categories()
        print("📁 Available Test Categories:")
        for category, count in categories:
            print(f"  {category:<15} ({count} tests)")
        return
    
    if "/" in command:
        # Running specific test
        success = run_specific_test(command)
    else:
        # Running category
        success = run_test_category(command)
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed or had issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
