"""
Centralized logging configuration for the Altman Z-Score package.

This module provides a unified logging framework that supports:
- Multiple output formats (console, file, structured JSON)
- Per-module/layer log level configuration
- Integration with API rate limiting logging
- Structured logging for better debugging and monitoring
"""

import os
import sys
import json
import logging
import logging.config
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for better parsing.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class LoggingConfig:
    """
    Centralized logging configuration manager.
    """
    
    # Default log levels for different components
    DEFAULT_LOG_LEVELS = {
        "altman_zscore": "INFO",
        "altman_zscore.layers.data_fetch": "DEBUG",
        "altman_zscore.layers.field_mapping": "INFO",
        "altman_zscore.layers.model_selection": "INFO",
        "altman_zscore.layers.zscore_calculation": "DEBUG",
        "altman_zscore.layers.market_data": "INFO",
        "altman_zscore.layers.output_generation": "INFO",
        "altman_zscore.common.api_rate_limiter": "DEBUG",
        "altman_zscore.cache": "INFO"
    }
    
    def __init__(self, 
                 log_dir: str = "logs",
                 console_level: str = "INFO",
                 file_level: str = "DEBUG",
                 structured_output: bool = False):
        """
        Initialize logging configuration.
        
        Args:
            log_dir: Directory for log files
            console_level: Console logging level
            file_level: File logging level
            structured_output: Whether to use structured JSON logging
        """
        self.log_dir = Path(log_dir)
        self.console_level = console_level
        self.file_level = file_level
        self.structured_output = structured_output
        
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
    
    def setup_logging(self) -> None:
        """
        Set up centralized logging configuration.
        """
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "structured": {
                    "()": StructuredFormatter
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.console_level,
                    "formatter": "structured" if self.structured_output else "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.file_level,
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "altman_zscore.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "errors.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {},
            "root": {
                "level": "DEBUG",
                "handlers": ["console", "file", "error_file"]
            }
        }
        
        # Set up per-module log levels
        for logger_name, level in self.DEFAULT_LOG_LEVELS.items():
            # Override with environment variable if set
            env_var = f"LOG_LEVEL_{logger_name.replace('.', '_').upper()}"
            actual_level = os.getenv(env_var, level)
            
            config["loggers"][logger_name] = {
                "level": actual_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            }
        
        # Apply configuration
        logging.config.dictConfig(config)
    
    @classmethod
    def setup_from_env(cls) -> 'LoggingConfig':
        """
        Set up logging configuration from environment variables.
        
        Environment variables:
        - LOG_DIR: Directory for log files (default: "logs")
        - LOG_CONSOLE_LEVEL: Console logging level (default: "INFO")
        - LOG_FILE_LEVEL: File logging level (default: "DEBUG")
        - LOG_STRUCTURED: Whether to use structured logging (default: False)
        """
        log_dir = os.getenv("LOG_DIR", "logs")
        console_level = os.getenv("LOG_CONSOLE_LEVEL", "INFO")
        file_level = os.getenv("LOG_FILE_LEVEL", "DEBUG")
        structured_output = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
        
        config = cls(
            log_dir=log_dir,
            console_level=console_level,
            file_level=file_level,
            structured_output=structured_output
        )
        config.setup_logging()
        return config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, 
                    level: int, 
                    message: str, 
                    **context) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (logging.INFO, logging.DEBUG, etc.)
        message: Log message
        **context: Additional context fields
    """
    # Create a custom log record with extra fields
    record = logger.makeRecord(
        logger.name, level, "", 0, message, (), None
    )
    record.extra_fields = context
    logger.handle(record)


def log_function_call(func):
    """
    Decorator to log function calls with arguments and return values.
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} with result type: {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_layer_operation(layer_name: str, operation: str, **context):
    """
    Decorator to log layer operations with context.
    
    Args:
        layer_name: Name of the layer (e.g., "data_fetch", "field_mapping")
        operation: Operation being performed
        **context: Additional context
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(f"altman_zscore.layers.{layer_name}")
            
            # Log operation start
            log_with_context(
                logger, logging.INFO,
                f"Starting {operation}",
                layer=layer_name,
                operation=operation,
                **context
            )
            
            try:
                result = func(*args, **kwargs)
                log_with_context(
                    logger, logging.INFO,
                    f"Completed {operation}",
                    layer=layer_name,
                    operation=operation,
                    success=True,
                    **context
                )
                return result
            except Exception as e:
                log_with_context(
                    logger, logging.ERROR,
                    f"Failed {operation}: {str(e)}",
                    layer=layer_name,
                    operation=operation,
                    success=False,
                    error=str(e),
                    **context
                )
                raise
        
        return wrapper
    return decorator


# Initialize logging on module import
if not os.getenv("ALTMAN_ZSCORE_SKIP_LOGGING_INIT"):
    LoggingConfig.setup_from_env()


# Example usage
if __name__ == "__main__":
    # Example of different logging patterns
    logger = get_logger(__name__)
    
    logger.info("Starting Altman Z-Score analysis")
    
    # Log with context
    log_with_context(
        logger, logging.INFO,
        "Processing company data",
        ticker="AAPL",
        quarters=8,
        model="original"
    )
    
    # Function decorator example
    @log_function_call
    def example_function(ticker: str, model: str):
        return f"Analysis for {ticker} using {model} model"
    
    result = example_function("AAPL", "original")
    
    # Layer operation example
    @log_layer_operation("data_fetch", "fetch_sec_data", ticker="AAPL")
    def fetch_data():
        return "Fetched data"
    
    fetch_data()
