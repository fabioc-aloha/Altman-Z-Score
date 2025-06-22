"""
Z-Score Validation - Validation and sanity checks for Z-Score calculations

This module provides comprehensive validation of Z-Score calculation results
including sanity checks, outlier detection, and result consistency validation.

Strategic Advantage:
- Ensures calculation accuracy and reliability
- Detects potential data quality issues
- Provides actionable validation feedback
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import math

from ...common.logging_config import get_logger
from ...common.exceptions import ValidationError

logger = get_logger(__name__)


@dataclass
class ZScoreValidationResult:
    """Result of Z-Score validation process."""
    is_valid: bool
    confidence_score: float
    validation_warnings: List[str]
    validation_errors: List[str]
    outlier_flags: List[str]
    sanity_check_results: Dict[str, bool]
    validation_date: datetime
    recommendations: List[str]


class ZScoreValidator:
    """
    Comprehensive Z-Score validation engine.
    
    Validation Categories:
    1. Sanity Checks - Basic mathematical and logical validation
    2. Outlier Detection - Statistical outlier identification
    3. Component Validation - Individual ratio validation
    4. Result Consistency - Cross-validation with industry norms
    """
    
    def __init__(self):
        """Initialize Z-Score validator."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Industry benchmark ranges for validation
        self.benchmark_ranges = {
            'z_score': {'min': -5.0, 'max': 15.0, 'typical_min': 0.0, 'typical_max': 5.0},
            'working_capital_ratio': {'min': -1.0, 'max': 1.0, 'typical_min': -0.2, 'typical_max': 0.6},
            'retained_earnings_ratio': {'min': -2.0, 'max': 1.0, 'typical_min': -0.5, 'typical_max': 0.8},
            'ebit_ratio': {'min': -1.0, 'max': 1.0, 'typical_min': -0.1, 'typical_max': 0.3},
            'asset_turnover': {'min': 0.0, 'max': 10.0, 'typical_min': 0.3, 'typical_max': 3.0}
        }
    
    def _validate_mathematical_sanity(self, z_score: float, components: Dict[str, float]) -> Dict[str, bool]:
        """
        Perform basic mathematical sanity checks.
        
        Args:
            z_score: Calculated Z-Score value
            components: Z-Score component values (X1, X2, X3, X4, X5)
            
        Returns:
            Dict of sanity check results
        """
        results = {}
        
        # Check for NaN or infinite values
        results['z_score_finite'] = math.isfinite(z_score)
        results['components_finite'] = all(
            math.isfinite(v) for v in components.values() if v is not None
        )
        
        # Check for reasonable Z-Score range
        results['z_score_reasonable'] = (
            self.benchmark_ranges['z_score']['min'] <= z_score <= 
            self.benchmark_ranges['z_score']['max']
        )
        
        # Check component reasonableness
        for component, value in components.items():
            if value is not None:
                component_key = {
                    'X1': 'working_capital_ratio',
                    'X2': 'retained_earnings_ratio', 
                    'X3': 'ebit_ratio',
                    'X4': 'asset_turnover'
                }.get(component)
                
                if component_key and component_key in self.benchmark_ranges:
                    range_info = self.benchmark_ranges[component_key]
                    results[f'{component}_reasonable'] = (
                        range_info['min'] <= value <= range_info['max']
                    )
        
        return results
    
    def _detect_outliers(self, z_score: float, components: Dict[str, float]) -> List[str]:
        """
        Detect statistical outliers in Z-Score and components.
        
        Args:
            z_score: Calculated Z-Score value
            components: Z-Score component values
            
        Returns:
            List of outlier flags
        """
        outliers = []
        
        # Check Z-Score outliers
        if z_score > self.benchmark_ranges['z_score']['typical_max']:
            outliers.append(f"Very high Z-Score: {z_score:.3f} (typical max: {self.benchmark_ranges['z_score']['typical_max']})")
        elif z_score < self.benchmark_ranges['z_score']['typical_min']:
            outliers.append(f"Very low Z-Score: {z_score:.3f} (typical min: {self.benchmark_ranges['z_score']['typical_min']})")
        
        # Check component outliers
        component_names = {
            'X1': ('working_capital_ratio', 'Working Capital Ratio'),
            'X2': ('retained_earnings_ratio', 'Retained Earnings Ratio'),
            'X3': ('ebit_ratio', 'EBIT Ratio'),
            'X4': ('asset_turnover', 'Asset Turnover')
        }
        
        for component, value in components.items():
            if value is not None and component in component_names:
                key, name = component_names[component]
                if key in self.benchmark_ranges:
                    range_info = self.benchmark_ranges[key]
                    
                    if value > range_info['typical_max']:
                        outliers.append(f"High {name}: {value:.3f} (typical max: {range_info['typical_max']})")
                    elif value < range_info['typical_min']:
                        outliers.append(f"Low {name}: {value:.3f} (typical min: {range_info['typical_min']})")
        
        return outliers
    
    def _validate_component_consistency(self, components: Dict[str, float]) -> List[str]:
        """
        Validate consistency between Z-Score components.
        
        Args:
            components: Z-Score component values
            
        Returns:
            List of consistency warnings
        """
        warnings = []
        
        # Get component values safely
        x1 = components.get('X1')  # Working capital ratio
        x2 = components.get('X2')  # Retained earnings ratio
        x3 = components.get('X3')  # EBIT ratio
        x4 = components.get('X4')  # Asset turnover
        
        # Check for contradictory patterns
        if x1 and x3:
            # High working capital but low profitability
            if x1 > 0.3 and x3 < 0.05:
                warnings.append("High working capital but low profitability - possible inefficient asset use")
            
            # Low working capital but high profitability
            if x1 < 0.0 and x3 > 0.15:
                warnings.append("Negative working capital but high profitability - aggressive working capital management")
        
        if x2 and x3:
            # Positive retained earnings but negative EBIT
            if x2 > 0.1 and x3 < -0.05:
                warnings.append("Positive retained earnings but negative EBIT - recent profitability decline")
        
        if x3 and x4:
            # Low profitability but high turnover (efficiency vs profitability trade-off)
            if x3 < 0.05 and x4 > 2.0:
                warnings.append("Low profitability but high asset turnover - possible low-margin business model")
        
        return warnings
    
    def _generate_recommendations(self, validation_result: Dict) -> List[str]:
        """
        Generate actionable recommendations based on validation results.
        
        Args:
            validation_result: Validation analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommendations based on validation issues
        if not validation_result.get('is_valid', False):
            recommendations.append("Review input data quality and recalculate Z-Score")
        
        if validation_result.get('confidence_score', 0) < 0.7:
            recommendations.append("Low confidence score - consider additional data validation")
        
        # Specific recommendations based on outliers
        for outlier in validation_result.get('outlier_flags', []):
            if "Very high Z-Score" in outlier:
                recommendations.append("Exceptionally strong financial health - verify calculation accuracy")
            elif "Very low Z-Score" in outlier:
                recommendations.append("High bankruptcy risk indicated - perform detailed financial analysis")
            elif "High Working Capital" in outlier:
                recommendations.append("Evaluate working capital efficiency and cash management")
            elif "Low Asset Turnover" in outlier:
                recommendations.append("Consider asset utilization efficiency improvements")
        
        return recommendations
    
    def validate_zscore_calculation(self, 
                                   z_score: float,
                                   components: Dict[str, float],
                                   model_used: str,
                                   data_quality_score: float = 1.0) -> ZScoreValidationResult:
        """
        Perform comprehensive validation of Z-Score calculation.
        
        Args:
            z_score: Calculated Z-Score value
            components: Z-Score component values
            model_used: Model used for calculation
            data_quality_score: Quality score of input data
            
        Returns:
            ZScoreValidationResult with comprehensive validation analysis
        """
        try:
            self.logger.info(f"Starting Z-Score validation (score: {z_score:.3f}, model: {model_used})")
            
            warnings = []
            errors = []
            
            # Perform sanity checks
            sanity_results = self._validate_mathematical_sanity(z_score, components)
            
            # Add errors for failed sanity checks
            if not sanity_results.get('z_score_finite', True):
                errors.append("Z-Score is not finite (NaN or infinite)")
            
            if not sanity_results.get('components_finite', True):
                errors.append("One or more components are not finite")
            
            if not sanity_results.get('z_score_reasonable', True):
                errors.append(f"Z-Score outside reasonable range: {z_score:.3f}")
            
            # Detect outliers
            outliers = self._detect_outliers(z_score, components)
            
            # Validate component consistency
            consistency_warnings = self._validate_component_consistency(components)
            warnings.extend(consistency_warnings)
            
            # Calculate overall validation confidence
            confidence_factors = [
                data_quality_score,
                1.0 if sanity_results.get('z_score_finite', False) else 0.0,
                1.0 if sanity_results.get('components_finite', False) else 0.0,
                0.8 if sanity_results.get('z_score_reasonable', False) else 0.3,
                max(0.5, 1.0 - len(outliers) * 0.1),  # Reduce confidence for outliers
                max(0.7, 1.0 - len(consistency_warnings) * 0.05)  # Reduce for inconsistencies
            ]
            
            confidence_score = sum(confidence_factors) / len(confidence_factors)
            
            # Determine overall validity
            is_valid = (
                len(errors) == 0 and
                confidence_score >= 0.6 and
                sanity_results.get('z_score_finite', False)
            )
            
            # Prepare result
            result_dict = {
                'is_valid': is_valid,
                'confidence_score': confidence_score,
                'validation_warnings': warnings,
                'validation_errors': errors,
                'outlier_flags': outliers,
                'sanity_check_results': sanity_results
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(result_dict)
            
            result = ZScoreValidationResult(
                is_valid=is_valid,
                confidence_score=confidence_score,
                validation_warnings=warnings,
                validation_errors=errors,
                outlier_flags=outliers,
                sanity_check_results=sanity_results,
                validation_date=datetime.now(),
                recommendations=recommendations
            )
            
            self.logger.info(f"Z-Score validation complete - Valid: {is_valid}, Confidence: {confidence_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Z-Score validation failed: {e}")
            raise ValidationError(f"Z-Score validation failed: {str(e)}")


# Main validation function for external use
def validate_zscore_calculation(z_score: float,
                               components: Dict[str, float],
                               model_used: str,
                               data_quality_score: float = 1.0) -> ZScoreValidationResult:
    """
    Public interface for Z-Score validation.
    
    Args:
        z_score: Calculated Z-Score value
        components: Z-Score component values
        model_used: Model used for calculation
        data_quality_score: Quality score of input data
        
    Returns:
        ZScoreValidationResult with comprehensive validation analysis
        
    Strategic Advantage:
        Comprehensive validation ensures calculation reliability and provides
        actionable feedback for data quality and result interpretation.
    """
    validator = ZScoreValidator()
    return validator.validate_zscore_calculation(z_score, components, model_used, data_quality_score)
