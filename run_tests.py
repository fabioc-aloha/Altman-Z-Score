#!/usr/bin/env python3
"""
Test Runner for Altman Z-Score Test Suite v4.2.0

This script provides convenient commands to run different categories of tests
with appropriate configurations and reporting.

Usage:
    python run_tests.py [OPTIONS] [TEST_CATEGORY]

Test Categories:
    unit         - Run unit tests only
    integration  - Run integration tests only  
    performance  - Run performance tests only
    all          - Run all tests (default)
    fast         - Run fast tests only (exclude slow/performance)
    
Options:
    --verbose    - Verbose output
    --coverage   - Generate coverage report
    --html       - Generate HTML coverage report
    --parallel   - Run tests in parallel
    --markers    - Show available test markers
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for the Altman Z-Score test suite"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        
    def run_command(self, cmd: List[str], description: str) -> int:
        """Run a command and return exit code"""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=False)
            return result.returncode
        except Exception as e:
            print(f"Error running command: {e}")
            return 1
    
    def build_pytest_command(
        self, 
        test_path: Optional[str] = None,
        markers: Optional[str] = None,
        verbose: bool = False,
        coverage: bool = False,
        html_cov: bool = False,
        parallel: bool = False,
        extra_args: Optional[List[str]] = None
    ) -> List[str]:
        """Build pytest command with specified options"""
        
        cmd = ["python", "-m", "pytest"]
        
        # Test path
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("tests")
        
        # Markers
        if markers:
            cmd.extend(["-m", markers])
        
        # Verbosity
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Coverage
        if coverage:
            cmd.extend([
                "--cov=altman_zscore",
                "--cov-report=term-missing"
            ])
            
            if html_cov:
                cmd.append("--cov-report=html")
        
        # Parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Extra arguments
        if extra_args:
            cmd.extend(extra_args)
        
        return cmd
    
    def run_unit_tests(self, **kwargs) -> int:
        """Run unit tests"""
        cmd = self.build_pytest_command(
            test_path="tests/unit",
            markers="unit",
            **kwargs
        )
        return self.run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self, **kwargs) -> int:
        """Run integration tests"""
        cmd = self.build_pytest_command(
            test_path="tests/integration", 
            markers="integration",
            **kwargs
        )
        return self.run_command(cmd, "Integration Tests")
    
    def run_performance_tests(self, **kwargs) -> int:
        """Run performance tests"""
        cmd = self.build_pytest_command(
            test_path="tests/performance",
            markers="performance",
            extra_args=["--run-performance"],
            **kwargs
        )
        return self.run_command(cmd, "Performance Tests")
    
    def run_fast_tests(self, **kwargs) -> int:
        """Run fast tests (exclude slow and performance)"""
        cmd = self.build_pytest_command(
            markers="not slow and not performance",
            **kwargs
        )
        return self.run_command(cmd, "Fast Tests")
    
    def run_all_tests(self, **kwargs) -> int:
        """Run all tests"""
        cmd = self.build_pytest_command(**kwargs)
        return self.run_command(cmd, "All Tests")
    
    def show_markers(self) -> int:
        """Show available test markers"""
        cmd = ["python", "-m", "pytest", "--markers"]
        return self.run_command(cmd, "Available Test Markers")
    
    def check_environment(self) -> bool:
        """Check if test environment is properly set up"""
        print("Checking test environment...")
        
        # Check if pytest is available
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode != 0:
                print("❌ pytest not available")
                return False
            print(f"✅ {result.stdout.strip()}")
        except Exception:
            print("❌ pytest not available")
            return False
        
        # Check if test directory exists
        if not self.test_dir.exists():
            print("❌ Tests directory not found")
            return False
        print("✅ Tests directory found")
        
        # Check if altman_zscore package is available
        try:
            result = subprocess.run(
                ["python", "-c", "import altman_zscore; print('altman_zscore package available')"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode != 0:
                print("❌ altman_zscore package not available")
                print(f"Error: {result.stderr}")
                return False
            print("✅ altman_zscore package available")
        except Exception:
            print("❌ altman_zscore package not available")
            return False
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Altman Z-Score Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        default="all",
        choices=["unit", "integration", "performance", "all", "fast"],
        help="Test category to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--markers",
        action="store_true",
        help="Show available test markers"
    )
    
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check test environment setup"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check environment if requested
    if args.check_env:
        if runner.check_environment():
            print("\n✅ Test environment is properly set up")
            return 0
        else:
            print("\n❌ Test environment has issues")
            return 1
    
    # Show markers if requested
    if args.markers:
        return runner.show_markers()
    
    # Check environment before running tests
    if not runner.check_environment():
        print("\n❌ Test environment check failed. Use --check-env for details.")
        return 1
    
    # Build test options
    test_options = {
        "verbose": args.verbose,
        "coverage": args.coverage,
        "html_cov": args.html,
        "parallel": args.parallel
    }
    
    # Run tests based on category
    if args.category == "unit":
        return runner.run_unit_tests(**test_options)
    elif args.category == "integration":
        return runner.run_integration_tests(**test_options)
    elif args.category == "performance":
        return runner.run_performance_tests(**test_options)
    elif args.category == "fast":
        return runner.run_fast_tests(**test_options)
    elif args.category == "all":
        return runner.run_all_tests(**test_options)
    else:
        print(f"Unknown test category: {args.category}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
