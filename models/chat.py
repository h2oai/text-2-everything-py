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
    # RAG retrieval cutoff thresholds
    contexts_cutoff: Optional[float] = None
    schema_cutoff: Optional[float] = None
    feedback_cutoff: Optional[float] = None
    examples_cutoff: Optional[float] = None
    # LLM agent parameters
    use_agent: Optional[bool] = None
    agent_accuracy: Optional[str] = None
    # System prompt override
    system_prompt: Optional[str] = None


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


class ExecutionCacheLookupRequest(BaseModel):
    """Request to find a recent similar execution."""
    
    user_query: str
    connector_id: str
    max_age_days: int = 30
    similarity_threshold: float = 0.65
    limit: int = 50
    top_n: int = 5  # Number of top matches to return
    only_positive_feedback: bool = False  # Optional filter for positive feedback only


class CacheMatch(BaseModel):
    """A single cache match with execution and similarity score."""
    
    execution: Dict[str, Any]  # Execution object
    similarity_score: float
    has_feedback: bool = False
    feedback_is_positive: Optional[bool] = None
    feedback_comment: Optional[str] = None


class ExecutionCacheLookupResponse(BaseModel):
    """Response with cache hit/miss and execution details."""
    
    cache_hit: bool
    matches: list[CacheMatch] = []
    candidates_checked: int
