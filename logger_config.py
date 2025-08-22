# logger_config.py

import logging
import sys

def setup_logger():
    """Sets up a centralized logger for the application."""
    # Get the root logger
    logger = logging.getLogger()
    
    # Avoid adding duplicate handlers if this is called more than once
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the lowest level of messages to handle
    logger.setLevel(logging.INFO)

    # Create a formatter - this defines the structure of your log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - ERROR_ID:[%(funcName)s] - %(message)s'
    )

    # Create a handler to write logs to a file (e.g., app.log)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.ERROR) # Only write ERROR level messages and above to the file
    file_handler.setFormatter(formatter)

    # Create a handler to print logs to the console (for debugging)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO) # Print INFO level messages and above to the console
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Create a logger instance to be imported by other modules
logger = setup_logger()

def setup_analytics_logger():
    """Sets up a separate logger for usage analytics."""
    analytics_logger = logging.getLogger('AnalyticsLogger')
    analytics_logger.setLevel(logging.INFO)
    
    # Use a simple formatter for easy parsing
    formatter = logging.Formatter('%(asctime)s,%(message)s')
    
    # Prevent logs from bubbling up to the root logger
    analytics_logger.propagate = False
    
    # Clear handlers to avoid duplicates on Streamlit re-runs
    if analytics_logger.hasHandlers():
        analytics_logger.handlers.clear()
        
    # Log to a dedicated file
    handler = logging.FileHandler('analytics.log')
    handler.setFormatter(formatter)
    analytics_logger.addHandler(handler)
    
    return analytics_logger

analytics_logger = setup_analytics_logger()