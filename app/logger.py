"""Simple logging system for CloudDash."""

import os
import logging
from datetime import datetime
from typing import Optional

LOG_DIR: str = "logs"
LOG_FILE: str = os.path.join(LOG_DIR, f"clouddash_{datetime.now().strftime('%Y%m%d')}.log")

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logger: logging.Logger = logging.getLogger("CloudDash")
logger.setLevel(logging.DEBUG)

# File handler
file_handler: logging.FileHandler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

# Console handler (only for errors and warnings)
console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Formatter
formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_info(msg: str) -> None:
    """Log info message."""
    logger.info(msg)

def log_warning(msg: str) -> None:
    """Log warning message."""
    logger.warning(msg)

def log_error(msg: str, exc_info: bool = False) -> None:
    """Log error message."""
    logger.error(msg, exc_info=exc_info)

def log_debug(msg: str) -> None:
    """Log debug message."""
    logger.debug(msg)
