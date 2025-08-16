"""
Logging setup and utilities for SAGE++ Trading Bot

Provides structured logging with multiple outputs including:
- Console output with color coding
- File rotation
- Structured JSON logging for analysis
- Integration with monitoring systems
"""

import logging
import logging.handlers
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': ''.join(traceback.format_tb(record.exc_info[2]))
            }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_obj.update(record.extra_data)
        
        return json.dumps(log_obj)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors for console output"""
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class TradingLogger:
    """Enhanced logger for trading operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._extra_data = {}
    
    def with_context(self, **kwargs) -> 'TradingLogger':
        """Add context to all log messages"""
        new_logger = TradingLogger(self.logger.name)
        new_logger.logger = self.logger
        new_logger._extra_data = {**self._extra_data, **kwargs}
        return new_logger
    
    def _log_with_extra(self, level: int, message: str, *args, **kwargs):
        """Log with extra context data"""
        extra_data = {**self._extra_data, **kwargs.pop('extra', {})}
        self.logger._log(level, message, args, extra={'extra_data': extra_data}, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self._log_with_extra(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log_with_extra(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log_with_extra(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log_with_extra(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log_with_extra(logging.CRITICAL, message, *args, **kwargs)
    
    def trade(self, action: str, symbol: str, quantity: float, price: float, **kwargs):
        """Log trading operations"""
        self.info(
            f"Trade executed: {action} {quantity} {symbol} @ {price}",
            extra={
                'event_type': 'trade',
                'action': action,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                **kwargs
            }
        )
    
    def order(self, action: str, order_id: str, status: str, **kwargs):
        """Log order operations"""
        self.info(
            f"Order {action}: {order_id} - {status}",
            extra={
                'event_type': 'order',
                'action': action,
                'order_id': order_id,
                'status': status,
                **kwargs
            }
        )
    
    def performance(self, metric: str, value: float, **kwargs):
        """Log performance metrics"""
        self.info(
            f"Performance metric: {metric} = {value}",
            extra={
                'event_type': 'performance',
                'metric': metric,
                'value': value,
                **kwargs
            }
        )
    
    def alert(self, alert_type: str, message: str, severity: str = 'WARNING', **kwargs):
        """Log alerts"""
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        self._log_with_extra(
            log_level,
            f"ALERT [{alert_type}]: {message}",
            extra={
                'event_type': 'alert',
                'alert_type': alert_type,
                'severity': severity,
                **kwargs
            }
        )


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
    enable_json: bool = True,
    enable_console: bool = True
) -> None:
    """
    Setup comprehensive logging for SAGE++ Trading Bot
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path (optional)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        enable_json: Enable JSON structured logging to file
        enable_console: Enable console output
    """
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    handlers = []
    
    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(numeric_level)
        handlers.append(console_handler)
    
    # File handlers
    if log_file:
        # Create log directory
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Regular text log with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)
        
        # JSON structured log
        if enable_json:
            json_log_file = str(log_path.with_suffix('.json'))
            json_handler = logging.handlers.RotatingFileHandler(
                json_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            json_handler.setFormatter(JSONFormatter())
            json_handler.setLevel(numeric_level)
            handlers.append(json_handler)
    
    # Add all handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific logger levels
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('websocket').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Create main application logger
    logger = logging.getLogger('sagepp')
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    
    return logger


def get_trading_logger(name: str) -> TradingLogger:
    """Get a trading logger instance"""
    return TradingLogger(name)
