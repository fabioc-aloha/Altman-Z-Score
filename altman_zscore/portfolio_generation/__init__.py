"""
Portfolio Generation Module

Provides modular portfolio generation functionality to replace the duplicated
generate_*.py scripts with a clean, reusable architecture.

Key Features:
- Single source of truth for portfolio generation logic
- Strategy-based filtering and ranking
- Template-based HTML generation
- Configurable portfolio types and criteria
"""

from .base import PortfolioGenerator, PortfolioStrategy, PortfolioConfig
from .strategies import (
    StrongBuyStrategy, BuyStrategy, 
    SellStrategy, StrongSellStrategy,
    ValueStrategy, GrowthStrategy,
    DividendStrategy, ConservativeStrategy,
    AggressiveStrategy, ModelPortfolioStrategy
)
from .html_generator import HTMLPortfolioGenerator
from .data_extractor import CompanyDataExtractor

__all__ = [
    'PortfolioGenerator',
    'PortfolioStrategy',
    'PortfolioConfig',
    'StrongBuyStrategy',
    'BuyStrategy',
    'SellStrategy', 
    'StrongSellStrategy',
    'ValueStrategy',
    'GrowthStrategy',
    'DividendStrategy',
    'ConservativeStrategy',
    'AggressiveStrategy',
    'ModelPortfolioStrategy',
    'HTMLPortfolioGenerator',
    'CompanyDataExtractor'
]
