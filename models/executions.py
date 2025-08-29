"""
Executions models for the Text2Everything SDK.
"""

from typing import Optional, Dict, Any
from .base import BaseModel, BaseResponse


class SQLExecuteRequest(BaseModel):
    """Model for SQL execution request."""
    
    connector_id: str
    chat_message_id: Optional[str] = None
    sql_query: Optional[str] = None
    h2ogpte_session_id: Optional[str] = None


class SQLExecuteResponse(BaseModel):
    """Model for SQL execution response."""
    
    execution_id: str
    connector_id: str
    sql_query: str
    result: Dict[str, Any]
    execution_time_ms: int
    chat_message_id: Optional[str] = None


class ExecutionBase(BaseModel):
    """Base execution model."""
    
    result: Dict[str, Any]
    execution_time_ms: int
    chat_message_id: Optional[str] = None
    sql_query: Optional[str] = None
    connector_id: str


class Execution(ExecutionBase, BaseResponse):
    """Complete execution model with all fields."""
    pass
