"""
Text2Everything SDK

A comprehensive Python SDK for the Text2Everything API, providing easy access to
text-to-SQL conversion, project management, and data operations.
"""

from .client import Text2EverythingClient
from .exceptions import (
    Text2EverythingError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError
)

__version__ = "0.1.2"
__author__ = "Text2Everything Team"

__all__ = [
    "Text2EverythingClient",
    "Text2EverythingError",
    "AuthenticationError", 
    "ValidationError",
    "NotFoundError",
    "RateLimitError"
]
