"""
Terminal color utilities for Altman Z-Score analysis.

Provides ANSI color codes for styling terminal output, including codes for warnings, errors, and success messages.
"""


class Colors:
    """ANSI color codes for terminal output.

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
