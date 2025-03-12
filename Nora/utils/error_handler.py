"""
Error handling utilities for Nora.
"""

import sys
import logging
import traceback

logger = logging.getLogger("nora.error_handler")

def setup_error_handling():
    """
    Set up global error handling for the application.
    """
    sys.excepthook = global_exception_handler

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to log unhandled exceptions.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt (Ctrl+C)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logger.critical("Unhandled exception", 
                   exc_info=(exc_type, exc_value, exc_traceback))
    
    # Print to stderr
    print("An unexpected error occurred:", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

class NoraError(Exception):
    """Base exception class for Nora-specific errors."""
    pass

class ConfigurationError(NoraError):
    """Error raised when there's a configuration issue."""
    pass

class APIError(NoraError):
    """Error raised when an API call fails."""
    pass

class WebBrowsingError(NoraError):
    """Error raised during web browsing operations."""
    pass

class CodeGenerationError(NoraError):
    """Error raised during code generation."""
    pass

class GitHubError(NoraError):
    """Error raised during GitHub operations."""
    pass

class CloudDeploymentError(NoraError):
    """Error raised during cloud deployment."""
    pass

class DomainError(NoraError):
    """Error raised during domain operations."""
    pass

class MonetizationError(NoraError):
    """Error raised during monetization operations."""
    pass

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts (int): Maximum number of attempts
        delay (int): Initial delay between retries in seconds
        backoff (int): Backoff multiplier
        exceptions (tuple): Exceptions to catch and retry
        
    Returns:
        function: Decorated function
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = max_attempts, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Retrying {func.__name__} after error: {str(e)}")
                    mtries -= 1
                    time.sleep(mdelay)
                    mdelay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator