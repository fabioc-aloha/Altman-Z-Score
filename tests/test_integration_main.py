"""
Integration test to ensure main pipeline and all top-level imports work without import errors.
"""
import subprocess
import sys
import os


def test_main_import_no_errors():
    """
    Test that main.py can be imported without any import errors.
    This is a lightweight test that doesn't run the full analysis.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cmd = [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); import main; print('Import successful')"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir, timeout=10)
    assert result.returncode == 0, f"main.py import failed with code {result.returncode}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    assert "Traceback" not in result.stderr, f"main.py raised an exception: {result.stderr}"
    assert "ModuleNotFoundError" not in result.stderr, f"main.py import error: {result.stderr}"
    assert "Import successful" in result.stdout, "Import should complete successfully"


def test_main_help_runs_quickly():
    """
    Test that main.py --help runs quickly without hanging.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cmd = [sys.executable, "main.py", "--help"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir, timeout=10)
        assert result.returncode == 0, f"main.py --help failed with code {result.returncode}"
        assert "usage:" in result.stdout, "Help should show usage information"
    except subprocess.TimeoutExpired:
        assert False, "main.py --help hung (timed out after 10 seconds)"
