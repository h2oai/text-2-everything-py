"""
Base models for the Text2Everything SDK.
"""

from pydantic import BaseModel as PydanticBaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""
    
    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    
    items: List[Dict[str, Any]]
    total: int
    page: int = 1
    per_page: int = 50
    pages: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str
    detail: Optional[str] = None
    status_code: Optional[int] = None


class AutoFeedbackConfig(BaseModel):
    """Auto feedback configuration."""
    
    positive: bool = False
    negative: bool = False
