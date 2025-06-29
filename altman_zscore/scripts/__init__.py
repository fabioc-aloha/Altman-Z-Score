"""
Scripts Module

Contains command-line scripts and utilities for the Altman Z-Score system.

This module provides:
- Unified portfolio generation script
- Replacement for individual generate_*_picks.py scripts
- Command-line interface for portfolio operations
"""

from .generate_portfolio import PortfolioGeneratorScript

__all__ = [
    'PortfolioGeneratorScript'
]
