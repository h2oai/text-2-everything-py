"""
Chat sessions models for the Text2Everything SDK.
"""

from typing import Optional, List
from datetime import datetime
from .base import BaseModel


class ChatSessionCreate(BaseModel):
    """Model for creating a new chat session."""
    
    name: Optional[str] = None
    custom_tool_id: Optional[str] = None


class ChatSessionResponse(BaseModel):
    """Model for chat session response."""
    
    id: str
    name: Optional[str] = None
    created_at: datetime
    custom_tool_id: Optional[str] = None


class ChatSessionUpdateRequest(BaseModel):
    """Model for updating a chat session."""
    
    custom_tool_id: Optional[str] = None


class ChatSessionQuestion(BaseModel):
    """Model for chat session question."""
    
    question: str


class ChatSessionQuestionsResponse(BaseModel):
    """Model for chat session questions response."""
    
    session_id: str
    questions: List[ChatSessionQuestion]
