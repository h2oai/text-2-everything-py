"""
Connectors models for the Text2Everything SDK.
"""

from typing import Optional, Dict, Any
from enum import Enum
from .base import BaseModel, BaseResponse


class ConnectorType(str, Enum):
    """Supported database connector types."""
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class ConnectorBase(BaseModel):
    """Base connector model."""
    
    name: str
    description: Optional[str] = None
    db_type: str
    host: str
    port: Optional[int] = None
    username: str
    password: str
    database: str
    config: Optional[Dict[str, Any]] = None


class ConnectorCreate(ConnectorBase):
    """Model for creating a new connector."""
    pass


class ConnectorUpdate(BaseModel):
    """Model for updating a connector."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Connector(ConnectorBase, BaseResponse):
    """Complete connector model with all fields."""
    pass
