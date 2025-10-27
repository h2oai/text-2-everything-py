"""
Text2Everything SDK - Official Python SDK for the Text2Everything API.

This SDK provides a comprehensive interface for building intelligent text-to-SQL
applications with advanced RAG (Retrieval-Augmented Generation) capabilities.
"""

from text2everything_sdk.client import Text2EverythingClient
from text2everything_sdk.exceptions import (
    Text2EverythingError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ConnectionError,
    TimeoutError,
    InvalidConfigurationError
)

__version__ = "0.1.6-rc1"
__all__ = [
    "Text2EverythingClient",
    "Text2EverythingError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
    "InvalidConfigurationError"
]
