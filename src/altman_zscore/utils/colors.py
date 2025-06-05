"""
Terminal color utilities for Altman Z-Score analysis.

This module provides ANSI color codes for styling terminal output.
It includes predefined color codes for common use cases like warnings,
errors, and success messages.

Note: This code follows PEP 8 style guidelines.
"""


class Colors:
    """
    ANSI color codes for terminal output.

    Attributes:
        BLUE (str): Blue color code.
        GREEN (str): Green color code.
        YELLOW (str): Yellow color code.
        RED (str): Red color code.
        BOLD (str): Bold text style code.
        UNDERLINE (str): Underline text style code.
        ENDC (str): Reset color/style code.
    """

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"
