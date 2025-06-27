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


class SafeStreamHandler(logging.StreamHandler):
    """
    A stream handler that safely handles encoding errors on Windows.
    """
    
    def emit(self, record):
        """Emit a record, handling encoding errors gracefully."""
        try:
            # Format the message and replace problematic Unicode characters
            msg = self.format(record)
            
            # If on Windows with cp1252 encoding, replace emojis and special chars
            if hasattr(self.stream, 'encoding') and self.stream.encoding and 'cp' in self.stream.encoding.lower():
                # Replace common emojis and Unicode chars that cause issues
                emoji_replacements = {
                    '📊': '[CHART]',
                    '📈': '[TRENDING_UP]', 
                    '📉': '[TRENDING_DOWN]',
                    '💰': '[MONEY]',
                    '⚠️': '[WARNING]',
                    '✅': '[CHECK]',
                    '❌': '[X]',
                    '🚀': '[ROCKET]',
                    '🔍': '[SEARCH]',
                    '💡': '[BULB]',
                    '⭐': '[STAR]',
                    '🎯': '[TARGET]',
                    '📋': '[CLIPBOARD]'
                }
                
                for emoji, replacement in emoji_replacements.items():
                    msg = msg.replace(emoji, replacement)
                
                # Also handle any remaining non-ASCII characters
                msg = msg.encode(self.stream.encoding, errors='replace').decode(self.stream.encoding)
            
            self.stream.write(msg + self.terminator)
            self.flush()
            
        except (OSError, UnicodeEncodeError) as e:
            # If console output fails, try to write a safe fallback message
            try:
                safe_msg = f"[LOGGING ERROR] Failed to output log message for {record.name}: {str(e)}\n"
                self.stream.write(safe_msg.encode('ascii', errors='replace').decode('ascii'))
                self.stream.flush()
            except Exception:
                # If even the fallback fails, just ignore it
                pass


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
    
    This class manages all logging configuration including:
    - Console and file logging levels
    - Structured vs standard output formats
    - Log directory management
    - Per-module log level overrides
    - Progress bar display logic for quiet logging modes
    """
    
    # Default log levels for different modules
    DEFAULT_LOG_LEVELS = {
        "altman_zscore.layers.data_fetch": "INFO",
        "altman_zscore.layers.zscore_calculation": "INFO", 
        "altman_zscore.layers.market_analysis": "INFO",
        "altman_zscore.layers.output_generation": "INFO",
        "altman_zscore.layers.ai_insights": "INFO",
        "altman_zscore.common.api_rate_limiter": "WARNING",
        "altman_zscore.common.cache": "WARNING",
        "altman_zscore.common.progress": "INFO"
    }
    
    # Quiet logging levels that should show progress bars
    QUIET_LEVELS = {"WARNING", "ERROR", "CRITICAL"}
    
    def __init__(self, 
                 log_level: str = "INFO",
                 console_level: Optional[str] = None,
                 file_level: str = "DEBUG",
                 log_dir: str = "logs",
                 structured_output: bool = False,
                 enhanced_logging: bool = True):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Default log level
            console_level: Console-specific log level (defaults to log_level)
            file_level: File-specific log level  
            log_dir: Directory for log files
            structured_output: Whether to use structured JSON logging
            enhanced_logging: Whether to enable enhanced logging features
        """
        self.log_level = log_level.upper()
        self.console_level = (console_level or log_level).upper()
        self.file_level = file_level.upper()
        self.log_dir = Path(log_dir)
        self.structured_output = structured_output
        self.enhanced_logging = enhanced_logging
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Track if logging has been configured
        self._configured = False
    
    def should_show_progress_bar(self) -> bool:
        """
        Determine if progress bars should be displayed.
        
        Progress bars are shown when console logging is set to quiet levels
        (WARNING, ERROR, CRITICAL) to provide visual feedback when detailed
        logging output is suppressed.
        
        Returns:
            bool: True if progress bars should be displayed
        """
        return self.console_level in self.QUIET_LEVELS
    
    def is_quiet_mode(self) -> bool:
        """
        Check if logging is in quiet mode.
        
        Returns:
            bool: True if console logging level suppresses info/debug output
        """
        return self.console_level in self.QUIET_LEVELS
    
    def setup_logging(self) -> None:
        """
        Set up centralized logging configuration.
        """
        # Set up console encoding for Windows compatibility
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass
        if hasattr(sys.stderr, 'reconfigure'):
            try:
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass
        
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
                    "()": SafeStreamHandler,
                    "level": self.console_level,
                    "formatter": "structured" if self.structured_output else "standard",
                    "stream": sys.stdout
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.file_level,
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "altman_zscore.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8"
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "errors.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8"
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
        
        # Store as global configuration
        global _global_logging_config
        _global_logging_config = self
        
        # Mark as configured
        self._configured = True
    
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


# Global logging configuration instance
_global_logging_config: Optional[LoggingConfig] = None


def get_logging_config() -> Optional[LoggingConfig]:
    """
    Get the current global logging configuration.
    
    Returns:
        LoggingConfig: Current logging configuration, or None if not initialized
    """
    return _global_logging_config


def should_show_progress_bars() -> bool:
    """
    Determine if progress bars should be displayed based on current logging configuration.
    
    Progress bars are shown based on the SHOW_PROGRESS_BARS environment variable:
    - 'auto' (default): Show when console logging is WARNING/ERROR/CRITICAL
    - 'always': Always show progress bars
    - 'never': Never show progress bars
    
    Returns:
        bool: True if progress bars should be displayed
    """
    progress_setting = os.getenv("SHOW_PROGRESS_BARS", "auto").lower()
    
    if progress_setting == "always":
        return True
    elif progress_setting == "never":
        return False
    else:  # auto mode
        config = get_logging_config()
        if config:
            return config.should_show_progress_bar()
        
        # Fallback: check log level from environment
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        console_level = os.getenv("LOG_CONSOLE_LEVEL", log_level).upper()
        return console_level in LoggingConfig.QUIET_LEVELS


def is_quiet_logging_mode() -> bool:
    """
    Check if logging is in quiet mode (WARNING/ERROR/CRITICAL).
    
    Returns:
        bool: True if console logging level suppresses info/debug output
    """
    config = get_logging_config()
    if config:
        return config.is_quiet_mode()
    
    # Fallback: check log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    console_level = os.getenv("LOG_CONSOLE_LEVEL", log_level).upper()
    return console_level in LoggingConfig.QUIET_LEVELS


# Initialize logging on module import only if not disabled
# This allows main.py to control when logging is initialized
if not os.getenv("ALTMAN_ZSCORE_SKIP_LOGGING_INIT") and __name__ != "__main__":
    # Only auto-initialize if we're not being imported by main.py
    # Check if we're in a CLI context where main.py should control logging
    try:
        if len(sys.argv) > 0 and "main.py" not in sys.argv[0]:
            LoggingConfig.setup_from_env()
    except (AttributeError, IndexError):
        # If sys.argv is not available or empty, just set up default logging
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
