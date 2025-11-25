"""
Logging Configuration Module

Provides centralized logging configuration for Calcifer.
All modules should use this for consistent log output.

This is CORE functionality - required for Calcifer to work.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, format_json: bool = False) -> logging.Logger:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (default: INFO)
        format_json: If True, output JSON format for log aggregation
        
    Returns:
        Root logger for the application
    """
    # Determine format based on environment
    if format_json:
        # JSON format for production/container environments
        log_format = '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}'
    else:
        # Human-readable format for development
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        stream=sys.stdout,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Return the calcifer root logger
    return logging.getLogger('calcifer')


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (e.g., 'calcifer.core.work_module')
        
    Returns:
        Logger instance for the module
    
    Example:
        logger = get_logger('calcifer.core.work_module')
        logger.info("Work item created")
    """
    return logging.getLogger(name)


# Module-level convenience function
def log_startup():
    """Log application startup information."""
    logger = logging.getLogger('calcifer')
    logger.info("=" * 60)
    logger.info("🔥 Calcifer Infrastructure Platform Starting")
    logger.info("=" * 60)


def log_shutdown():
    """Log application shutdown information."""
    logger = logging.getLogger('calcifer')
    logger.info("=" * 60)
    logger.info("🔥 Calcifer Shutting Down")
    logger.info("=" * 60)