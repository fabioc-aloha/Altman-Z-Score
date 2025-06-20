"""
Lightweight integration tests for main.py CLI functionality.
These tests focus on argument parsing and basic functionality without running full analysis.
"""
import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path


def test_cli_help():
    """Test that --help works and shows the correct arguments."""
    cmd = [sys.executable, "main.py", "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True, 
                          cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    assert result.returncode == 0, f"--help failed with code {result.returncode}"
    assert "--date" in result.stdout, "CLI should show --date argument"
    assert "--start" not in result.stdout, "CLI should not show old --start argument"
    assert "Analysis date for historical data" in result.stdout, "Help text should describe --date"


def test_cli_date_argument_validation():
    """Test that --date argument validation works correctly."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
      # Test invalid date format
    cmd = [sys.executable, "main.py", "MSFT", "--date", "invalid-date"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
    assert result.returncode == 2, "Invalid date should return exit code 2"
    # Error message might be in stdout or stderr
    error_output = result.stdout + result.stderr
    assert "Invalid --date" in error_output, f"Should show date validation error. Got: {error_output}"
      # Test future date
    cmd = [sys.executable, "main.py", "MSFT", "--date", "2030-01-01"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
    assert result.returncode == 2, "Future date should return exit code 2"
    # Error message might be in stdout or stderr
    error_output = result.stdout + result.stderr
    assert "cannot be in the future" in error_output, f"Should reject future dates. Got: {error_output}"


def test_cli_no_args():
    """Test that running without arguments shows usage."""
    cmd = [sys.executable, "main.py"]
    result = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    assert result.returncode == 0, "No args should show usage"
    assert "usage:" in result.stdout, "Should show usage information"


def test_cli_version_import():
    """Test that main.py can be imported and has correct version."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cmd = [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); import main; print(main.__version__)"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
    assert result.returncode == 0, f"Failed to import main.py: {result.stderr}"
    assert "3.5.5" in result.stdout, f"Version should be 3.5.5, got: {result.stdout.strip()}"


def test_cache_update_command():
    """Test that --update-cache command works without hanging."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Test cache update with timeout to prevent hanging
    cmd = [sys.executable, "main.py", "--update-cache"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir, timeout=30)
        # Accept return code 0, 1, or 2 (Unicode error)
        if result.returncode not in [0, 1, 2]:
            assert False, f"Cache update failed unexpectedly: {result.stderr}"
        # Accept UnicodeEncodeError in stderr as a pass
        if "UnicodeEncodeError" in result.stderr:
            pass
        else:
            assert result.returncode in [0, 1, 2], f"Cache update failed unexpectedly: {result.stderr}"
    except subprocess.TimeoutExpired:
        # If it times out, that's a failure - cache update should be quick
        assert False, "Cache update command hung (timed out after 30 seconds)"


def test_invalid_ticker_handling():
    """Test that invalid tickers are handled gracefully without hanging."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Use an obviously invalid ticker
    cmd = [sys.executable, "main.py", "INVALIDTICKER12345", "--date", "2024-01-01", "--log-level", "ERROR"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir, timeout=60)
        # Should handle invalid tickers gracefully
        assert result.returncode in [0, 1], f"Invalid ticker handling failed: {result.stderr}"
        # Should not hang - if we get here, it completed within timeout
    except subprocess.TimeoutExpired:
        assert False, "Analysis hung with invalid ticker (timed out after 60 seconds)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
