import io
import sys
import pytest
from altman_zscore.plotting_terminal import Colors, print_info, print_warning, print_error

@pytest.fixture
def capture_stdout(monkeypatch):
    captured_output = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', captured_output)
    return captured_output

def test_colors_class():
    assert Colors.CYAN is not None
    assert Colors.YELLOW is not None
    assert Colors.RED is not None
    assert Colors.ENDC is not None

def test_print_info_with_color(capture_stdout, monkeypatch):
    def mock_print(*args, **kwargs):
        # This will write directly to our StringIO
        capture_stdout.write(args[0] + '\n')
    
    monkeypatch.setattr('builtins.print', mock_print)
    msg = "Test info message"
    print_info(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"{Colors.CYAN}[INFO]{Colors.ENDC} {msg}"
    assert output == expected

def test_print_warning_with_color(capture_stdout, monkeypatch):
    def mock_print(*args, **kwargs):
        # This will write directly to our StringIO
        capture_stdout.write(args[0] + '\n')
        
    monkeypatch.setattr('builtins.print', mock_print)
    msg = "Test warning message"
    print_warning(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {msg}"
    assert output == expected

def test_print_error_with_color(capture_stdout, monkeypatch):
    def mock_print(*args, **kwargs):
        # This will write directly to our StringIO
        capture_stdout.write(args[0] + '\n')
        
    monkeypatch.setattr('builtins.print', mock_print)
    msg = "Test error message"
    print_error(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"{Colors.RED}[ERROR]{Colors.ENDC} {msg}"
    assert output == expected

def test_print_info_without_color_handling(capture_stdout, monkeypatch):
    """Test that print_info works correctly when the first print raises an exception"""
    msg = "Test info message"
    counter = [0]  # Use a list to allow modification in closure
    
    def mock_print(*args, **kwargs):
        counter[0] += 1
        if counter[0] == 1:
            raise Exception("No color support")
        capture_stdout.write(args[0] + '\n')
    
    monkeypatch.setattr('builtins.print', mock_print)
    print_info(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"[INFO] {msg}"
    assert output == expected

def test_print_warning_without_color_handling(capture_stdout, monkeypatch):
    """Test that print_warning works correctly when the first print raises an exception"""
    msg = "Test warning message"
    counter = [0]  # Use a list to allow modification in closure
    
    def mock_print(*args, **kwargs):
        counter[0] += 1
        if counter[0] == 1:
            raise Exception("No color support")
        capture_stdout.write(args[0] + '\n')
    
    monkeypatch.setattr('builtins.print', mock_print)
    print_warning(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"[WARNING] {msg}"
    assert output == expected

def test_print_error_without_color_handling(capture_stdout, monkeypatch):
    """Test that print_error works correctly when the first print raises an exception"""
    msg = "Test error message"
    counter = [0]  # Use a list to allow modification in closure
    
    def mock_print(*args, **kwargs):
        counter[0] += 1
        if counter[0] == 1:
            raise Exception("No color support")
        capture_stdout.write(args[0] + '\n')
    
    monkeypatch.setattr('builtins.print', mock_print)
    print_error(msg)
    output = capture_stdout.getvalue().strip()
    expected = f"[ERROR] {msg}"
    assert output == expected
