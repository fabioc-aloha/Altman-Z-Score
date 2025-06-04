"""
Terminal output formatting helpers for Altman Z-Score analysis.
Centralizes info, warning, error, and header print functions using Colors.
"""
from .colors import Colors
import sys

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {msg}", file=sys.stderr)

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {msg}", file=sys.stderr)

def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {msg}")

def print_header(msg: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{msg}{Colors.ENDC}\n")
