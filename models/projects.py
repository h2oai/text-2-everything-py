"""
Project models for the Text2Everything SDK.
"""

from typing import Optional
from .base import BaseModel, BaseResponse


class ProjectBase(BaseModel):
    """Base project model."""
    
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating a project."""
    
    name: Optional[str] = None
    description: Optional[str] = None


class Project(ProjectBase, BaseResponse):
    """Complete project model with all fields."""
    pass
