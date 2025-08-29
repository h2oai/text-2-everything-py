"""
Feedback models for the Text2Everything SDK.
"""

from typing import Optional
from .base import BaseModel, BaseResponse


class FeedbackBase(BaseModel):
    """Base feedback model."""
    
    chat_message_id: str
    feedback: str
    is_positive: bool = True
    execution_id: Optional[str] = None
    h2ogpte_doc_id: Optional[str] = None


class FeedbackCreate(BaseModel):
    """Model for creating feedback."""
    
    chat_message_id: str
    feedback: str
    is_positive: bool = True
    execution_id: Optional[str] = None


class FeedbackUpdate(BaseModel):
    """Model for updating feedback."""
    
    feedback: Optional[str] = None
    is_positive: Optional[bool] = None


class Feedback(FeedbackBase, BaseResponse):
    """Complete feedback model with all fields."""
    
    project_id: str


class FeedbackResponse(Feedback):
    """Feedback response with collection ID."""
    
    collection_id: Optional[str] = None
