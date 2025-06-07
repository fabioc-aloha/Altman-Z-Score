"""
Color schemes for plotting and terminal output in Altman Z-Score analysis.

This module defines the ColorScheme class, which centralizes all color and style constants for both matplotlib plots and terminal output.
"""

class ColorScheme:
    # ANSI Terminal Colors
    ANSI_HEADER = "\033[95m"       # Magenta
    ANSI_BLUE = "\033[94m"        # Blue
    ANSI_CYAN = "\033[96m"        # Cyan
    ANSI_GREEN = "\033[92m"       # Green
    ANSI_YELLOW = "\033[93m"      # Yellow
    ANSI_RED = "\033[91m"         # Red
    ANSI_END = "\033[0m"          # Reset to default color
    ANSI_BOLD = "\033[1m"         # Bold text
    ANSI_UNDERLINE = "\033[4m"    # Underlined text

    # Plotting Colors
    DISTRESS_ZONE = "#ff6666"     # Light red for distress zone
    GREY_ZONE = "#cccccc"         # Light grey for grey zone
    SAFE_ZONE = "#66ff66"         # Light green for safe zone
    ZSCORE_LINE = "blue"          # Blue line for Z-Score
    DARK_GREY = "#444444"         # Dark grey for plot elements
    
    # Zone Label Colors
    DISTRESS_LABEL = "#a60000"    # Dark red for distress labels
    GREY_LABEL = "#444444"        # Dark grey for grey labels
    SAFE_LABEL = "#007a00"        # Dark green for safe labels

    # Alpha Values
    DISTRESS_ALPHA = 0.8           # Transparency for distress zone
    GREY_ALPHA = 0.6               # Transparency for grey zone
    SAFE_ALPHA = 0.5               # Transparency for safe zone
