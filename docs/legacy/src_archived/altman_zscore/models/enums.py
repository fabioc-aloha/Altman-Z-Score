"""
enums.py
--------
Enums for company stage and type used in Altman Z-Score analysis.

This module defines enums for company lifecycle stages and company types (public/private).
"""
from enum import Enum, auto

class CompanyStage(Enum):
    """
    Enum for company lifecycle stages (early, growth, mature).
    """
    EARLY = auto()
    GROWTH = auto()
    MATURE = auto()

class CompanyType(Enum):
    """
    Enum for company types (public or private).
    """
    PUBLIC = auto()
    PRIVATE = auto()
