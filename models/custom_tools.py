"""
Custom tools models for the Text2Everything SDK.
"""

from typing import Optional, List
from .base import BaseModel, BaseResponse


class CustomToolDocumentBase(BaseModel):
    """Base custom tool document model."""
    
    filename: str
    h2ogpte_doc_id: str


class CustomToolDocument(CustomToolDocumentBase, BaseResponse):
    """Complete custom tool document model."""
    
    custom_tool_id: str


class CustomToolBase(BaseModel):
    """Base custom tool model."""
    
    name: str
    description: str
    h2ogpte_collection_id: Optional[str] = None


class CustomToolCreate(BaseModel):
    """Model for creating a new custom tool."""
    
    name: str
    description: str


class CustomToolUpdate(BaseModel):
    """Model for updating a custom tool."""
    
    name: Optional[str] = None
    description: Optional[str] = None


class CustomTool(CustomToolBase, BaseResponse):
    """Complete custom tool model with all fields."""
    
    project_id: str
    documents: List[CustomToolDocument] = []
