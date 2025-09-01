"""
Chat models for the Text2Everything SDK.
"""

from typing import Optional, Dict, Any
from .base import BaseModel, BaseResponse
from .executions import SQLExecuteResponse


class AutoFeedbackConfig(BaseModel):
    """Configuration for automatic feedback submission."""
    
    positive: bool = False
    negative: bool = False


class ChatRequest(BaseModel):
    """Model for chat request."""
    
    query: str
    llm: Optional[str] = None
    context_id: Optional[str] = None
    schema_metadata_id: Optional[str] = None
    connector_id: Optional[str] = None
    example_id: Optional[str] = None
    # RAG retrieval limits
    contexts_limit: Optional[int] = None
    schema_limit: Optional[int] = None
    feedback_limit: Optional[int] = None
    examples_limit: Optional[int] = None
    # LLM agent parameters
    use_agent: Optional[bool] = None
    agent_accuracy: Optional[str] = None


class ChatResponseBase(BaseModel):
    """Base chat response model."""
    
    id: str
    project_id: str
    chat_session_id: Optional[str] = None
    user_query: str
    sql_query: Optional[str] = None
    explanation: Optional[str] = None
    agent_tool_response: Optional[str] = None
    context_id: Optional[str] = None
    schema_metadata_id: Optional[str] = None
    connector_id: Optional[str] = None
    example_id: Optional[str] = None


class ChatResponse(ChatResponseBase):
    """Complete chat response model."""
    pass


class ChatToAnswerRequest(ChatRequest):
    """Model for chat-to-answer request."""
    
    auto_add_feedback: AutoFeedbackConfig = AutoFeedbackConfig()
    custom_tool_id: Optional[str] = None


class ChatToAnswerResponse(ChatResponseBase):
    """Model for chat-to-answer response."""
    
    execution_result: Optional[SQLExecuteResponse] = None
    feedback: Optional[Dict[str, Any]] = None
