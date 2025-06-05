"""
Enums for company stage and type.
"""
from enum import Enum, auto

class CompanyStage(Enum):
    """
    Enum for company lifecycle stages.
    """
    EARLY = auto()
    GROWTH = auto()
    MATURE = auto()

class CompanyType(Enum):
    """
    Enum for company types.
    """
    PUBLIC = auto()
    PRIVATE = auto()
