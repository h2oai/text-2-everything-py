"""
Context models for the Text2Everything SDK.
"""

from typing import Optional
from .base import BaseModel, BaseResponse


class ContextBase(BaseModel):
    """Base context model."""
    
    name: str
    description: Optional[str] = None
    content: str
    is_always_displayed: bool = False


class ContextCreate(ContextBase):
    """Model for creating a new context."""
    pass


class ContextUpdate(BaseModel):
    """Model for updating a context."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_always_displayed: Optional[bool] = None


class Context(ContextBase, BaseResponse):
    """Complete context model with all fields."""
    
    project_id: str
    h2ogpte_doc_id: Optional[str] = None


class ContextResponse(Context):
    """Context response with collection ID."""
    
    collection_id: Optional[str] = None
