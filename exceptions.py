"""
Text2Everything SDK Exceptions

Custom exception classes for the Text2Everything SDK.
"""

from typing import Optional, Dict, Any


class Text2EverythingError(Exception):
    """Base exception class for all Text2Everything SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(Text2EverythingError):
    """Raised when authentication fails."""
    pass


class ValidationError(Text2EverythingError):
    """Raised when request validation fails."""
    pass


class NotFoundError(Text2EverythingError):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(Text2EverythingError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(Text2EverythingError):
    """Raised when the server returns a 5xx error."""
    pass


class ConnectionError(Text2EverythingError):
    """Raised when connection to the API fails."""
    pass


class TimeoutError(Text2EverythingError):
    """Raised when a request times out."""
    pass


class InvalidConfigurationError(Text2EverythingError):
    """Raised when SDK configuration is invalid."""
    pass
