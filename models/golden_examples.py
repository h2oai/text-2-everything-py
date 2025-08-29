"""
Golden examples models for the Text2Everything SDK.
"""

from typing import Optional
from .base import BaseModel, BaseResponse


class GoldenExampleBase(BaseModel):
    """Base golden example model."""
    
    user_query: str
    sql_query: str
    description: Optional[str] = None
    is_always_displayed: bool = False


class GoldenExampleCreate(GoldenExampleBase):
    """Model for creating a new golden example."""
    pass


class GoldenExampleUpdate(BaseModel):
    """Model for updating a golden example."""
    
    user_query: Optional[str] = None
    sql_query: Optional[str] = None
    description: Optional[str] = None
    is_always_displayed: Optional[bool] = None


class GoldenExample(GoldenExampleBase, BaseResponse):
    """Complete golden example model with all fields."""
    
    project_id: str
    h2ogpte_doc_id: Optional[str] = None


class GoldenExampleResponse(GoldenExample):
    """Golden example response with collection ID."""
    
    collection_id: Optional[str] = None
