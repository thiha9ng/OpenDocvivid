"""
Logging module for AI DocVivid Service
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from src.configs.config import settings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging() -> None:
    """Setup logging configuration"""
    
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use colored formatter for console in development
    if settings.debug:
        console_formatter = ColoredFormatter(settings.log_format)
    else:
        console_formatter = logging.Formatter(settings.log_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file is specified)
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=settings.log_max_size * 1024 * 1024,
            backupCount=settings.log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        file_formatter = logging.Formatter(settings.log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance"""
    if name is None:
        name = __name__
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()

# Create a default logger for this module
logger = get_logger(__name__) 