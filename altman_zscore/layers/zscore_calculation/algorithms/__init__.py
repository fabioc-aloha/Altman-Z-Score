"""
Z-Score Calculation Algorithms Package

Contains modular calculation algorithms for different Altman Z-Score models.
"""

from .calculation_algorithms import (
    ZScoreAlgorithm,
    CalculationResult,
    OriginalAltmanAlgorithm,
    AltmanZPrimeAlgorithm, 
    AltmanZDoubleAlgorithm,
    AlgorithmFactory
)

__all__ = [
    'ZScoreAlgorithm',
    'CalculationResult',
    'OriginalAltmanAlgorithm',
    'AltmanZPrimeAlgorithm',
    'AltmanZDoubleAlgorithm',
    'AlgorithmFactory'
]
