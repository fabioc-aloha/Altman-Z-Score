"""
Standardized error handling framework for the Altman Z-Score package.

This module provides:
- Standardized error handling patterns across all layers
- Error classification and severity levels
- Automatic error reporting and logging
- Recovery strategies for common failure modes
"""

import sys
import traceback
from typing import Dict, List, Optional, Any, Callable, Type
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field

from .exceptions import (
    ZScoreError, DataFetchError, APIRateLimitError, FieldMappingError,
    InsufficientDataError, ModelSelectionError, SectorExclusionError,
    ValidationError, ComponentValidationError, NonUSCompanyError,
    CacheError, OutputGenerationError, ConfigurationError
)
from .logging_config import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"          # Minor issues, can continue
    MEDIUM = "medium"    # Significant issues, may affect quality
    HIGH = "high"        # Major issues, likely to fail
    CRITICAL = "critical"  # Fatal errors, cannot continue


class ErrorCategory(Enum):
    """Error category classification."""
    DATA = "data"              # Data quality or availability issues
    API = "api"                # External API errors
    VALIDATION = "validation"  # Data validation errors
    CONFIGURATION = "config"   # Configuration or setup errors
    COMPUTATION = "computation"  # Calculation or processing errors
    IO = "io"                  # File I/O or network errors
    SYSTEM = "system"          # System-level errors


@dataclass
class ErrorContext:
    """Context information for an error."""
    layer: Optional[str] = None
    operation: Optional[str] = None
    ticker: Optional[str] = None
    quarter: Optional[str] = None
    model: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class ErrorHandler:
    """
    Centralized error handling with classification and recovery strategies.
    """
    
    # Map exception types to categories and severities
    ERROR_CLASSIFICATION = {
        DataFetchError: (ErrorCategory.API, ErrorSeverity.HIGH),
        APIRateLimitError: (ErrorCategory.API, ErrorSeverity.MEDIUM),
        FieldMappingError: (ErrorCategory.DATA, ErrorSeverity.MEDIUM),
        InsufficientDataError: (ErrorCategory.DATA, ErrorSeverity.HIGH),
        ModelSelectionError: (ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM),
        SectorExclusionError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
        ValidationError: (ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM),
        ComponentValidationError: (ErrorCategory.COMPUTATION, ErrorSeverity.HIGH),
        NonUSCompanyError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
        CacheError: (ErrorCategory.IO, ErrorSeverity.LOW),
        OutputGenerationError: (ErrorCategory.IO, ErrorSeverity.MEDIUM),
        ConfigurationError: (ErrorCategory.CONFIGURATION, ErrorSeverity.CRITICAL)
    }
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[Type[Exception], Callable] = {}
        self.error_callbacks: List[Callable] = []
    
    def classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """
        Classify an error by category and severity.
        
        Args:
            error: Exception to classify
            
        Returns:
            Tuple of (category, severity)
        """
        error_type = type(error)
        
        # Direct mapping
        if error_type in self.ERROR_CLASSIFICATION:
            return self.ERROR_CLASSIFICATION[error_type]
        
        # Check inheritance hierarchy
        for exc_type, (category, severity) in self.ERROR_CLASSIFICATION.items():
            if isinstance(error, exc_type):
                return category, severity
        
        # Default classification
        return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
    
    def handle_error(self, 
                    error: Exception, 
                    context: Optional[ErrorContext] = None,
                    reraise: bool = True) -> Optional[Any]:
        """
        Handle an error with logging, classification, and recovery.
        
        Args:
            error: Exception to handle
            context: Optional error context
            reraise: Whether to re-raise the exception
            
        Returns:
            Recovery result if available, None otherwise
        """
        category, severity = self.classify_error(error)
        error_key = f"{category.value}_{type(error).__name__}"
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log the error
        self._log_error(error, category, severity, context)
        
        # Call error callbacks
        for callback in self.error_callbacks:
            try:
                callback(error, category, severity, context)
            except Exception as callback_error:
                logger.error(f"Error in error callback: {callback_error}")
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(error, context)
        
        if reraise and recovery_result is None:
            raise error
        
        return recovery_result
    
    def _log_error(self, 
                  error: Exception, 
                  category: ErrorCategory, 
                  severity: ErrorSeverity,
                  context: Optional[ErrorContext] = None) -> None:
        """Log an error with appropriate detail level."""
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "category": category.value,
            "severity": severity.value,
            "traceback": traceback.format_exc()
        }
        
        if context:
            log_data.update({
                "layer": context.layer,
                "operation": context.operation,
                "ticker": context.ticker,
                "quarter": context.quarter,
                "model": context.model,
                **context.additional_data
            })
        
        # Choose log level based on severity
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {error}", extra={"error_data": log_data})
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {error}", extra={"error_data": log_data})
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {error}", extra={"error_data": log_data})
        else:
            logger.info(f"Low severity error: {error}", extra={"error_data": log_data})
    
    def _attempt_recovery(self, 
                         error: Exception, 
                         context: Optional[ErrorContext] = None) -> Optional[Any]:
        """Attempt to recover from an error using registered strategies."""
        error_type = type(error)
        
        # Check for exact type match
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed: {recovery_error}")
        
        # Check for inheritance-based match
        for strategy_type, strategy_func in self.recovery_strategies.items():
            if isinstance(error, strategy_type):
                try:
                    return strategy_func(error, context)
                except Exception as recovery_error:
                    logger.error(f"Recovery strategy failed: {recovery_error}")
        
        return None
    
    def register_recovery_strategy(self, 
                                 error_type: Type[Exception], 
                                 strategy: Callable) -> None:
        """
        Register a recovery strategy for a specific error type.
        
        Args:
            error_type: Exception type to handle
            strategy: Function that takes (error, context) and returns recovery result
        """
        self.recovery_strategies[error_type] = strategy
        logger.debug(f"Registered recovery strategy for {error_type.__name__}")
    
    def add_error_callback(self, callback: Callable) -> None:
        """
        Add a callback function to be called on every error.
        
        Args:
            callback: Function that takes (error, category, severity, context)
        """
        self.error_callbacks.append(callback)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = sum(self.error_counts.values())
        return {
            "total_errors": total_errors,
            "error_counts": self.error_counts.copy(),
            "most_common": max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(context: Optional[ErrorContext] = None, 
                 reraise: bool = True):
    """
    Decorator for automatic error handling.
    
    Args:
        context: Optional error context
        reraise: Whether to re-raise exceptions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create context if not provided
                if context is None:
                    func_context = ErrorContext(
                        operation=func.__name__,
                        additional_data={"args": str(args), "kwargs": str(kwargs)}
                    )
                else:
                    func_context = context
                
                return error_handler.handle_error(e, func_context, reraise)
        
        return wrapper
    return decorator


def handle_layer_errors(layer_name: str, operation: str = None):
    """
    Decorator for layer-specific error handling.
    
    Args:
        layer_name: Name of the layer
        operation: Optional operation name
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = ErrorContext(
                layer=layer_name,
                operation=operation or func.__name__
            )
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_error(e, context, reraise=True)
        
        return wrapper
    return decorator


def safe_execute(func: Callable, 
                default_value: Any = None,
                context: Optional[ErrorContext] = None) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        default_value: Value to return on error
        context: Optional error context
        
    Returns:
        Function result or default value on error
    """
    try:
        return func()
    except Exception as e:
        error_handler.handle_error(e, context, reraise=False)
        return default_value


# Register default recovery strategies
def _api_rate_limit_recovery(error: APIRateLimitError, context: Optional[ErrorContext] = None):
    """Recovery strategy for API rate limit errors."""
    logger.info("Applying rate limit recovery strategy")
    import time
    if hasattr(error, 'retry_after') and error.retry_after:
        time.sleep(error.retry_after)
    else:
        time.sleep(60)  # Default 1 minute wait
    return "retry"


def _cache_error_recovery(error: CacheError, context: Optional[ErrorContext] = None):
    """Recovery strategy for cache errors."""
    logger.info("Applying cache error recovery strategy - continuing without cache")
    return "continue_without_cache"


# Register default recovery strategies
error_handler.register_recovery_strategy(APIRateLimitError, _api_rate_limit_recovery)
error_handler.register_recovery_strategy(CacheError, _cache_error_recovery)


# Example usage
if __name__ == "__main__":
    # Example of using the error handler
    
    @handle_errors()
    def example_function():
        raise DataFetchError("Failed to fetch data", source="SEC")
    
    @handle_layer_errors("data_fetch", "fetch_sec_data")
    def layer_function():
        raise ValidationError("Invalid data format")
    
    # Test safe execution
    def risky_function():
        raise ValueError("Something went wrong")
    
    result = safe_execute(risky_function, default_value="fallback")
    print(f"Safe execution result: {result}")
    
    # Get error statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")
