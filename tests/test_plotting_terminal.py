import io
import sys
import pytest
import logging
from altman_zscore.plotting.plotting_terminal import print_info, print_warning, print_error

@pytest.mark.parametrize("func,level,msg", [
    (print_info, "INFO", "Test info message"),
    (print_warning, "WARNING", "Test warning message"),
    (print_error, "ERROR", "Test error message"),
])
def test_logging_output(func, level, msg, caplog):
    with caplog.at_level(getattr(logging, level)):
        func(msg)
    # Only check the last log record for the message
    assert any(msg in record.message and record.levelname == level for record in caplog.records)
