"""
Logging configuration for NZ Property Analyser
"""
import logging
import sys
import os
from config import LOG_FILE

# Logs folder path
LOGS_FOLDER = "logs"

# Global variable to store the current log file path
_current_log_file = None


def setup_logger(name="property_analyser", log_file=None):
    """
    Set up logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file path. If None, uses stored log file or default from config.
                 If relative path, saves to logs folder.
        
    Returns:
        Configured logger instance
    """
    global _current_log_file
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler - INFO level and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Determine log file path
    if log_file is not None:
        # Store the log file for future use
        _current_log_file = log_file
    elif _current_log_file is not None:
        # Use stored log file
        log_file = _current_log_file
    else:
        # Use default
        log_file = LOG_FILE
    
    # If log_file is not absolute, save to logs folder
    if not os.path.isabs(log_file):
        # Ensure logs folder exists
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        log_file = os.path.join(LOGS_FOLDER, log_file)
    
    # File handler - DEBUG level and above
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

