"""
Quality Gates - Data validation and quality assurance

This module implements comprehensive quality gates to ensure data integrity
before Z-Score calculation. Focuses on FMP pre-calculated ratios validation
and Yahoo market data consistency checks.

Key Quality Checks:
1. Financial ratio completeness and validity
2. Market data consistency validation  
3. Data freshness and availability verification
4. Outlier detection and flagging
5. Cross-validation between data sources
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from ...common.logging_config import get_logger
from ...common.exceptions import ValidationError
from ...models.data_models import MergedFinancialData, DataQualityReport

logger = get_logger(__name__)


@dataclass
class QualityThresholds:
    """Quality thresholds for data validation."""
    min_quality_score: float = 0.8
    max_ratio_value: float = 100.0  # Extreme ratio threshold
    min_market_cap: float = 1000000  # $1M minimum
    max_data_age_days: int = 90  # Maximum data staleness


@dataclass
class QualityCheckResult:
    """Result of individual quality check."""
    check_name: str
    passed: bool
    severity: str  # 'error', 'warning', 'info'
    message: str
    value: Any = None


class QualityGates:
    """
    Comprehensive data quality validation for FMP and Yahoo data.
    
    Strategic Focus: Ensure FMP pre-calculated ratios and Yahoo market data
    meet quality standards for reliable Z-Score calculations.
    """
    
    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.quality_checks = []
    
    def validate_merged_data(self, data: MergedFinancialData) -> DataQualityReport:
        """
        Comprehensive validation of merged financial data.
        
        Args:
            data: Merged financial data from FMP and Yahoo
            
        Returns:
            DataQualityReport with detailed quality assessment
        """
        logger.info(f"Starting quality validation for {data.ticker}")
        
        self.quality_checks = []  # Reset checks
        
        # Run all quality checks
        self._check_ratio_completeness(data)
        self._check_ratio_validity(data)
        self._check_market_data_consistency(data)
        self._check_data_freshness(data)
        self._check_outliers(data)
        self._cross_validate_data_sources(data)
        
        # Generate quality report
        report = self._generate_quality_report(data)
        
        logger.info(f"Quality validation complete for {data.ticker}: "
                   f"Score {report.quality_score:.2f}")
        
        return report
    
    def _check_ratio_completeness(self, data: MergedFinancialData) -> None:
        """Check completeness of essential Z-Score ratios."""
        essential_ratios = [
            ('working_capital_ratio', data.working_capital_ratio),
            ('retained_earnings_ratio', data.retained_earnings_ratio),
            ('ebit_ratio', data.ebit_ratio),
            ('asset_turnover', data.asset_turnover)
        ]
        
        missing_ratios = []
        for ratio_name, ratio_value in essential_ratios:
            if ratio_value is None:
                missing_ratios.append(ratio_name)
        
        if missing_ratios:
            self.quality_checks.append(QualityCheckResult(
                check_name="ratio_completeness",
                passed=False,
                severity="error",
                message=f"Missing essential ratios: {', '.join(missing_ratios)}",
                value=missing_ratios
            ))
        else:
            self.quality_checks.append(QualityCheckResult(
                check_name="ratio_completeness",
                passed=True,
                severity="info",
                message="All essential Z-Score ratios present"
            ))
    
    def _check_ratio_validity(self, data: MergedFinancialData) -> None:
        """Validate financial ratio values for reasonableness."""
        ratios_to_check = [
            ('working_capital_ratio', data.working_capital_ratio),
            ('retained_earnings_ratio', data.retained_earnings_ratio),
            ('ebit_ratio', data.ebit_ratio),
            ('asset_turnover', data.asset_turnover),
            ('current_ratio', data.current_ratio),
            ('debt_to_equity', data.debt_to_equity)
        ]
        
        invalid_ratios = []
        extreme_ratios = []
        
        for ratio_name, ratio_value in ratios_to_check:
            if ratio_value is None:
                continue
                
            # Check for invalid values
            if not isinstance(ratio_value, (int, float)) or \
               not (-1000 <= ratio_value <= 1000):  # Reasonable bounds
                invalid_ratios.append(f"{ratio_name}: {ratio_value}")
                continue
            
            # Check for extreme values that might indicate data issues
            if abs(ratio_value) > self.thresholds.max_ratio_value:
                extreme_ratios.append(f"{ratio_name}: {ratio_value}")
        
        # Report invalid ratios
        if invalid_ratios:
            self.quality_checks.append(QualityCheckResult(
                check_name="ratio_validity",
                passed=False,
                severity="error",
                message=f"Invalid ratio values: {', '.join(invalid_ratios)}",
                value=invalid_ratios
            ))
        
        # Report extreme ratios as warnings
        if extreme_ratios:
            self.quality_checks.append(QualityCheckResult(
                check_name="ratio_extremes",
                passed=True,
                severity="warning",
                message=f"Extreme ratio values detected: {', '.join(extreme_ratios)}",
                value=extreme_ratios
            ))
    
    def _check_market_data_consistency(self, data: MergedFinancialData) -> None:
        """Validate Yahoo market data for consistency."""
        consistency_issues = []
        
        # Check market cap vs shares * price consistency
        if all([data.market_cap, data.shares_outstanding, data.current_price]):
            calculated_market_cap = data.shares_outstanding * data.current_price
            market_cap_diff = abs(data.market_cap - calculated_market_cap) / data.market_cap
            
            if market_cap_diff > 0.1:  # More than 10% difference
                consistency_issues.append(
                    f"Market cap inconsistency: "
                    f"Reported ${data.market_cap:,.0f} vs "
                    f"Calculated ${calculated_market_cap:,.0f} "
                    f"({market_cap_diff:.1%} difference)"
                )
        
        # Check for reasonable market cap size
        if data.market_cap and data.market_cap < self.thresholds.min_market_cap:
            consistency_issues.append(
                f"Very small market cap: ${data.market_cap:,.0f}"
            )
        
        # Check for reasonable share count
        if data.shares_outstanding:
            if data.shares_outstanding < 1000:  # Very low share count
                consistency_issues.append(
                    f"Unusually low share count: {data.shares_outstanding:,.0f}"
                )
            elif data.shares_outstanding > 100_000_000_000:  # Very high share count
                consistency_issues.append(
                    f"Unusually high share count: {data.shares_outstanding:,.0f}"
                )
        
        if consistency_issues:
            self.quality_checks.append(QualityCheckResult(
                check_name="market_data_consistency",
                passed=False,
                severity="warning",
                message=f"Market data consistency issues: {'; '.join(consistency_issues)}",
                value=consistency_issues
            ))
        else:
            self.quality_checks.append(QualityCheckResult(
                check_name="market_data_consistency",
                passed=True,
                severity="info",
                message="Market data appears consistent"
            ))
    
    def _check_data_freshness(self, data: MergedFinancialData) -> None:
        """Check if data is reasonably fresh."""
        try:
            data_timestamp = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
            age_days = (datetime.now() - data_timestamp.replace(tzinfo=None)).days
            
            if age_days > self.thresholds.max_data_age_days:
                self.quality_checks.append(QualityCheckResult(
                    check_name="data_freshness",
                    passed=False,
                    severity="warning",
                    message=f"Data is {age_days} days old (threshold: {self.thresholds.max_data_age_days})",
                    value=age_days
                ))
            else:
                self.quality_checks.append(QualityCheckResult(
                    check_name="data_freshness",
                    passed=True,
                    severity="info",
                    message=f"Data is {age_days} days old (acceptable)"
                ))
        except Exception as e:
            self.quality_checks.append(QualityCheckResult(
                check_name="data_freshness",
                passed=False,
                severity="warning",
                message=f"Could not validate data freshness: {e}"
            ))
    
    def _check_outliers(self, data: MergedFinancialData) -> None:
        """Detect potential outliers in financial ratios."""
        outlier_warnings = []
        
        # Define typical ranges for ratios (based on financial literature)
        ratio_ranges = {
            'working_capital_ratio': (-0.5, 1.0),  # Can be negative
            'retained_earnings_ratio': (-2.0, 1.0),  # Can be very negative for losses
            'ebit_ratio': (-1.0, 1.0),  # Can be negative for losses
            'asset_turnover': (0.0, 10.0),  # Should be positive
            'current_ratio': (0.0, 20.0),  # Should be positive
            'debt_to_equity': (0.0, 20.0)  # Should be positive
        }
        
        ratios_to_check = [
            ('working_capital_ratio', data.working_capital_ratio),
            ('retained_earnings_ratio', data.retained_earnings_ratio),
            ('ebit_ratio', data.ebit_ratio),
            ('asset_turnover', data.asset_turnover),
            ('current_ratio', data.current_ratio),
            ('debt_to_equity', data.debt_to_equity)
        ]
        
        for ratio_name, ratio_value in ratios_to_check:
            if ratio_value is None:
                continue
                
            min_val, max_val = ratio_ranges.get(ratio_name, (-100, 100))
            
            if not (min_val <= ratio_value <= max_val):
                outlier_warnings.append(f"{ratio_name}: {ratio_value:.3f}")
        
        if outlier_warnings:
            self.quality_checks.append(QualityCheckResult(
                check_name="outlier_detection",
                passed=True,
                severity="warning",
                message=f"Potential outliers detected: {', '.join(outlier_warnings)}",
                value=outlier_warnings
            ))
    
    def _cross_validate_data_sources(self, data: MergedFinancialData) -> None:
        """Cross-validate FMP and Yahoo data for consistency."""
        validation_issues = []
        
        # Check if we have data from both sources
        has_fmp_data = any([
            data.working_capital_ratio is not None,
            data.retained_earnings_ratio is not None,
            data.ebit_ratio is not None,
            data.asset_turnover is not None
        ])
        
        has_yahoo_data = any([
            data.market_cap is not None,
            data.shares_outstanding is not None,
            data.current_price is not None
        ])
        
        if not has_fmp_data:
            validation_issues.append("No FMP financial ratios available")
        
        if not has_yahoo_data:
            validation_issues.append("No Yahoo market data available")
        
        if validation_issues:
            self.quality_checks.append(QualityCheckResult(
                check_name="cross_validation",
                passed=False,
                severity="error",
                message=f"Data source issues: {', '.join(validation_issues)}",
                value=validation_issues
            ))
        else:
            self.quality_checks.append(QualityCheckResult(
                check_name="cross_validation",
                passed=True,
                severity="info",
                message="Both FMP and Yahoo data sources available"
            ))
    
    def _generate_quality_report(self, data: MergedFinancialData) -> DataQualityReport:
        """Generate comprehensive quality report."""
        # Categorize checks
        errors = [c for c in self.quality_checks if c.severity == "error" and not c.passed]
        warnings = [c for c in self.quality_checks if c.severity == "warning"]
        passed_checks = [c for c in self.quality_checks if c.passed]
        
        # Calculate quality score
        total_checks = len(self.quality_checks)
        error_penalty = len(errors) * 0.3
        warning_penalty = len(warnings) * 0.1
        quality_score = max(0.0, 1.0 - error_penalty - warning_penalty)
        
        # Determine overall status
        is_complete = len(errors) == 0
        
        # Generate recommendation
        if not is_complete:
            recommendation = f"Data quality issues detected: {len(errors)} errors, {len(warnings)} warnings"
        elif len(warnings) > 0:
            recommendation = f"Data usable with caution: {len(warnings)} warnings detected"
        else:
            recommendation = "Data quality excellent - ready for Z-Score calculation"
        
        # Collect all issues
        missing_fields = []
        all_warnings = []
        
        for check in errors:
            if check.check_name == "ratio_completeness" and check.value:
                missing_fields.extend(check.value)
            else:
                all_warnings.append(f"ERROR: {check.message}")
        
        for check in warnings:
            all_warnings.append(f"WARNING: {check.message}")
        
        return DataQualityReport(
            ticker=data.ticker,
            is_complete=is_complete,
            missing_fields=missing_fields,
            warnings=all_warnings,
            quality_score=quality_score,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat(),
            total_checks=total_checks,
            passed_checks=len(passed_checks),
            failed_checks=len(errors),
            warning_checks=len(warnings)
        )


# Public interface functions
def validate_financial_data_integrity(data: MergedFinancialData) -> bool:
    """
    Quick validation check for financial data integrity.
    
    Args:
        data: Merged financial data
        
    Returns:
        True if data passes basic integrity checks
    """
    gates = QualityGates()
    report = gates.validate_merged_data(data)
    return report.is_complete and report.quality_score >= 0.8


def check_market_data_consistency(data: MergedFinancialData) -> bool:
    """
    Check market data consistency (market cap vs shares * price).
    
    Args:
        data: Merged financial data
        
    Returns:
        True if market data is consistent
    """
    if not all([data.market_cap, data.shares_outstanding, data.current_price]):
        return False
    
    calculated_market_cap = data.shares_outstanding * data.current_price
    market_cap_diff = abs(data.market_cap - calculated_market_cap) / data.market_cap
    
    return market_cap_diff <= 0.1  # Less than 10% difference


def apply_data_quality_thresholds(data: MergedFinancialData, 
                                 thresholds: Optional[QualityThresholds] = None) -> DataQualityReport:
    """
    Apply comprehensive data quality thresholds and validation.
    
    Args:
        data: Merged financial data
        thresholds: Optional custom quality thresholds
        
    Returns:
        Comprehensive data quality report
    """
    gates = QualityGates(thresholds)
    return gates.validate_merged_data(data)
