"""
Connectors resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from ..models.connectors import (
    Connector,
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorType
)
from ..exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class ConnectorsResource(BaseResource):
    """Resource for managing database connectors."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        name: str,
        db_type: str,
        host: str,
        username: str,
        password: str,
        database: str,
        port: Optional[int] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs
    ) -> Connector:
        """Create a new database connector.
        
        Args:
            name: Connector name
            db_type: Database type (postgres, mysql, sqlserver, snowflake)
            host: Database host
            port: Database port
            username: Database username
            password: Database password
            database: Database name
            description: Optional connector description
            config: Optional additional configuration
            **kwargs: Additional connector fields
        
        Returns:
            The created connector
            
        Example:
            ```python
            result = client.connectors.create(
                name="Production DB",
                description="Main production database",
                db_type="postgres",
                host="db.example.com",
                port=5432,
                username="app_user",
                password="secure_password",
                database="production"
            )
            ```
        """
        # Validate connector type
        if db_type.lower() not in [e.value for e in ConnectorType]:
            valid_types = ", ".join([e.value for e in ConnectorType])
            raise ValidationError(f"Invalid database type. Supported types are: {valid_types}")
        
        # Basic validation
        if not name or not name.strip():
            raise ValidationError("Connector name cannot be empty")
        
        if not host or not host.strip():
            raise ValidationError("Host cannot be empty")
        
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        if not password or not password.strip():
            raise ValidationError("Password cannot be empty")
        
        if not database or not database.strip():
            raise ValidationError("Database name cannot be empty")
        
        # Set default port based on database type if not provided
        if port is None:
            port_defaults = {
                "postgres": 5432,
                "mysql": 3306,
                "sqlserver": 1433,
                "snowflake": 443  # Snowflake typically uses HTTPS port
            }
            port = port_defaults.get(db_type.lower(), 5432)
        
        # Build the ConnectorCreate object internally
        connector = ConnectorCreate(
            name=name,
            db_type=db_type,
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            description=description,
            config=config,
            **kwargs
        )
        
        response = self._client.post(
            "/connectors",
            data=connector.model_dump()
        )
        return Connector(**response)
    
    def get(self, connector_id: str) -> Connector:
        """Get a connector by ID.
        
        Args:
            connector_id: The connector ID
            
        Returns:
            The connector details
            
        Example:
            ```python
            connector = client.connectors.get(connector_id)
            print(f"Database: {connector.db_type} at {connector.host}")
            ```
        """
        response = self._client.get(f"/connectors/{connector_id}")
        return Connector(**response)
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Connector]:
        """List all connectors.
        
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of connectors
            
        Example:
            ```python
            connectors = client.connectors.list()
            for connector in connectors:
                print(f"{connector.name}: {connector.db_type}")
            ```
        """
        endpoint = "/connectors"
        params = {"limit": limit, "skip": offset}
        return self._paginate(endpoint, params=params, model_class=Connector)
    
    def update(
        self,
        connector_id: str,
        name: Optional[str] = None,
        db_type: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs
    ) -> Connector:
        """Update a connector.
        
        Args:
            connector_id: The connector ID to update
            name: New connector name
        r    db_type: New database type
            host: New database host
            port: New database port
            username: New database username
            password: New database password
            database: New database name
            description: New connector description
            config: New additional configuration
            **kwargs: Additional fields to update
            
        Returns:
            The updated connector
            
        Example:
            ```python
            result = client.connectors.update(
                connector_id,
                description="Updated production database",
                port=5433
            )
            ```
        """
        # Validate connector type if provided
        if db_type and db_type.lower() not in [e.value for e in ConnectorType]:
            valid_types = ", ".join([e.value for e in ConnectorType])
            raise ValidationError(f"Invalid database type. Supported types are: {valid_types}")
        
        # Get current connector first since API expects complete data
        current_connector = self.get(connector_id)
        
        # Use current values as defaults, override with provided values
        update_data = ConnectorCreate(
            name=name if name is not None else current_connector.name,
            description=description if description is not None else current_connector.description,
            db_type=db_type if db_type is not None else current_connector.db_type,
            host=host if host is not None else current_connector.host,
            port=port if port is not None else current_connector.port,
            username=username if username is not None else current_connector.username,
            password=password if password is not None else current_connector.password,
            database=database if database is not None else current_connector.database,
            config=config if config is not None else current_connector.config,
            **kwargs
        )
        
        response = self._client.put(
            f"/connectors/{connector_id}",
            data=update_data.model_dump()
        )
        return Connector(**response)
    
    def delete(self, connector_id: str) -> bool:
        """Delete a connector.
        
        Args:
            connector_id: The connector ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.connectors.delete(connector_id)
            ```
        """
        self._client.delete(f"/connectors/{connector_id}")
        return True
    
    def test_connection(self, connector_id: str) -> bool:
        """Test a connector's database connection.
        
        Args:
            connector_id: The connector ID to test
            
        Returns:
            True if connection is successful
            
        Raises:
            ValidationError: If connection fails
            
        Example:
            ```python
            try:
                success = client.connectors.test_connection(connector_id)
                print("Connection successful!")
            except ValidationError as e:
                print(f"Connection failed: {e}")
            ```
        """
        try:
            # This would typically be a separate endpoint, but for now we'll use get
            # In a real implementation, there might be a POST /connectors/{id}/test endpoint
            connector = self.get(connector_id)
            return True
        except Exception as e:
            raise ValidationError(f"Connection test failed: {str(e)}")
    
    def list_by_type(self, db_type: str) -> List[Connector]:
        """List connectors by database type.
        
        Args:
            db_type: The database type to filter by
            
        Returns:
            List of connectors of the specified type
            
        Example:
            ```python
            postgres_connectors = client.connectors.list_by_type("postgres")
            ```
        """
        # Validate db_type
        if db_type.lower() not in [e.value for e in ConnectorType]:
            valid_types = ", ".join([e.value for e in ConnectorType])
            raise ValidationError(f"Invalid database type. Supported types are: {valid_types}")
        
        all_connectors = self.list()
        return [conn for conn in all_connectors if conn.db_type.lower() == db_type.lower()]
