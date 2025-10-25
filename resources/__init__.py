"""
Resource modules for the Text2Everything SDK.

Each resource module provides a client for interacting with a specific
set of API endpoints.
"""

from .base import BaseResource
from .projects import ProjectsResource
from .contexts import ContextsResource
from .golden_examples import GoldenExamplesResource
from .schema_metadata import SchemaMetadataResource
from .connectors import ConnectorsResource
from .executions import ExecutionsResource
from .chat import ChatResource
from .chat_sessions import ChatSessionsResource
from .chat_presets import ChatPresetsResource
from .feedback import FeedbackResource
from .custom_tools import CustomToolsResource

__all__ = [
    "BaseResource",
    "ProjectsResource",
    "ContextsResource",
    "GoldenExamplesResource",
    "SchemaMetadataResource",
    "ConnectorsResource",
    "ExecutionsResource",
    "ChatResource",
    "ChatSessionsResource",
    "ChatPresetsResource",
    "FeedbackResource",
    "CustomToolsResource"
]
