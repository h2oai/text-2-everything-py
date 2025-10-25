"""
Text2Everything SDK Models

Pydantic models for API request/response objects.
"""

from .base import BaseModel, BaseResponse
from .projects import Project, ProjectCreate, ProjectUpdate, Collection
from .contexts import Context, ContextCreate, ContextUpdate, ContextResponse
from .golden_examples import GoldenExample, GoldenExampleCreate, GoldenExampleUpdate, GoldenExampleResponse
from .schema_metadata import SchemaMetadata, SchemaMetadataCreate, SchemaMetadataUpdate, SchemaMetadataResponse
from .connectors import Connector, ConnectorCreate, ConnectorUpdate, ConnectorType
from .executions import Execution, SQLExecuteRequest, SQLExecuteResponse
from .chat import ChatRequest, ChatResponse, ChatToAnswerRequest, ChatToAnswerResponse, AutoFeedbackConfig, ExecutionCacheLookupRequest, CacheMatch, ExecutionCacheLookupResponse
from .chat_sessions import ChatSessionCreate, ChatSessionResponse, ChatSessionUpdateRequest, ChatSessionQuestion, ChatSessionQuestionsResponse
from .chat_presets import ChatPreset, ChatPresetCreate, ChatPresetUpdate, ChatPresetResponse, PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate, ChatSettings
from .feedback import Feedback, FeedbackCreate, FeedbackUpdate, FeedbackResponse
from .custom_tools import CustomTool, CustomToolCreate, CustomToolUpdate, CustomToolDocument

__all__ = [
    # Base
    "BaseModel",
    "BaseResponse",
    
    # Projects
    "Project",
    "ProjectCreate", 
    "ProjectUpdate",
    "Collection",
    
    # Contexts
    "Context",
    "ContextCreate",
    "ContextUpdate", 
    "ContextResponse",
    
    # Golden Examples
    "GoldenExample",
    "GoldenExampleCreate",
    "GoldenExampleUpdate",
    "GoldenExampleResponse",
    
    # Schema Metadata
    "SchemaMetadata",
    "SchemaMetadataCreate",
    "SchemaMetadataUpdate",
    "SchemaMetadataResponse",
    
    # Connectors
    "Connector",
    "ConnectorCreate",
    "ConnectorUpdate",
    "ConnectorType",
    
    # Executions
    "Execution",
    "SQLExecuteRequest",
    "SQLExecuteResponse",
    
    # Chat
    "ChatRequest",
    "ChatResponse",
    "ChatToAnswerRequest",
    "ChatToAnswerResponse",
    "AutoFeedbackConfig",
    "ExecutionCacheLookupRequest",
    "CacheMatch",
    "ExecutionCacheLookupResponse",
    
    # Chat Sessions
    "ChatSessionCreate",
    "ChatSessionResponse",
    "ChatSessionUpdateRequest",
    "ChatSessionQuestion",
    "ChatSessionQuestionsResponse",
    
    # Chat Presets
    "ChatPreset",
    "ChatPresetCreate",
    "ChatPresetUpdate",
    "ChatPresetResponse",
    "PromptTemplate",
    "PromptTemplateCreate",
    "PromptTemplateUpdate",
    "ChatSettings",
    
    # Feedback
    "Feedback",
    "FeedbackCreate",
    "FeedbackUpdate",
    "FeedbackResponse",
    
    # Custom Tools
    "CustomTool",
    "CustomToolCreate",
    "CustomToolUpdate",
    "CustomToolDocument"
]
