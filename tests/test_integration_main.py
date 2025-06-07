"""
Integration test to ensure main pipeline and all top-level imports work without import errors.
"""
import subprocess
import sys
import os


def test_main_entrypoint_runs():
    """
    Run main.py with a minimal valid argument to ensure no import errors occur.
    This test will fail if any import or runtime error occurs at startup.
    """
    # Use a ticker that is always available (e.g., MSFT)
    cmd = [sys.executable, "main.py", "MSFT", "--test"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    assert result.returncode == 0, f"main.py failed to run with code {result.returncode}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    assert "Traceback" not in result.stderr, f"main.py raised an exception: {result.stderr}"
    assert "ModuleNotFoundError" not in result.stderr, f"main.py import error: {result.stderr}"
