"""
Connectors resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from models.connectors import (
    Connector,
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorType
)
from exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from client import Text2EverythingClient


class ConnectorsResource(BaseResource):
    """Resource for managing database connectors."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        name: str,
        db_type: str,
        host: str,
        username: str,
        database: str,
        password: str | None = None,
        password_secret_id: str | None = None,
        port: Optional[int] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs
    ) -> Connector:
        """Create a new database connector.
        
        Args:
            project_id: The project ID
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
                project_id="proj-123",
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
        
        # Snowflake supports key-pair auth via config.private_key/secret; otherwise need password or secret id
        if db_type.lower() == "snowflake":
            cfg = config or {}
            has_private_key = bool(cfg.get("private_key") or cfg.get("private_key_secret_id") or cfg.get("private_key_secret_name"))
            has_password = bool((password and password.strip()) or (password_secret_id and password_secret_id.strip()))
            if not has_private_key and not has_password:
                raise ValidationError("Snowflake requires password or private_key (or secret reference)")
            if has_private_key and has_password:
                raise ValidationError("Provide either password or private_key, not both, for Snowflake")
        else:
            if not (password and password.strip()) and not (password_secret_id and password_secret_id.strip()):
                raise ValidationError("Either password or password_secret_id must be provided")
        
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
            password_secret_id=password_secret_id,
            database=database,
            description=description,
            config=config,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/connectors",
            data=connector.model_dump()
        )
        return Connector(**response)
    
    def get(self, project_id: str, connector_id: str) -> Connector:
        """Get a connector by ID.
        
        Args:
            project_id: The project ID
            connector_id: The connector ID
            
        Returns:
            The connector details
            
        Example:
            ```python
            connector = client.connectors.get(
                project_id="proj-123",
                connector_id="conn-456"
            )
            print(f"Database: {connector.db_type} at {connector.host}")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/connectors/{connector_id}")
        return Connector(**response)
    
    def list(self, project_id: str, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Connector]:
        """List all connectors.
        
        Args:
            project_id: The project ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search query
            
        Returns:
            List of connectors
            
        Example:
            ```python
            connectors = client.connectors.list(project_id="proj-123")
            for connector in connectors:
                print(f"{connector.name}: {connector.db_type}")
            ```
        """
        endpoint = f"/projects/{project_id}/connectors"
        params = {"limit": limit, "skip": skip}
        if search:
            params["q"] = search
        return self._paginate(endpoint, params=params, model_class=Connector)
    
    def update(
        self,
        project_id: str,
        connector_id: str,
        name: Optional[str] = None,
        db_type: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        password_secret_id: Optional[str] = None,
        database: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        **kwargs
    ) -> Connector:
        """Update a connector.
        
        Args:
            project_id: The project ID
            connector_id: The connector ID to update
            name: New connector name
            db_type: New database type
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
                project_id="proj-123",
                connector_id="conn-456",
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
        current_connector = self.get(project_id, connector_id)
        
        # Resolve password_secret_id for non-Snowflake to satisfy API validation without rotating secrets
        effective_db_type = (db_type or current_connector.db_type or "").lower()
        resolved_password_secret_id = password_secret_id
        if not resolved_password_secret_id and not password and effective_db_type != "snowflake":
            # Try to preserve existing secret by converting name to id (suffix after '/secrets/')
            existing_secret_name = getattr(current_connector, "password_secret_name", None)
            if isinstance(existing_secret_name, str) and "/secrets/" in existing_secret_name:
                resolved_password_secret_id = existing_secret_name.split("/secrets/")[-1] or None

        # Use current values as defaults, override with provided values
        update_data = ConnectorCreate(
            name=name if name is not None else current_connector.name,
            description=description if description is not None else current_connector.description,
            db_type=db_type if db_type is not None else current_connector.db_type,
            host=host if host is not None else current_connector.host,
            port=port if port is not None else current_connector.port,
            username=username if username is not None else current_connector.username,
            password=password if password is not None else current_connector.password,
            password_secret_id=resolved_password_secret_id,
            database=database if database is not None else current_connector.database,
            config=config if config is not None else current_connector.config,
            **kwargs
        )
        
        response = self._client.put(
            f"/projects/{project_id}/connectors/{connector_id}",
            data=update_data.model_dump()
        )
        return Connector(**response)
    
    def delete(self, project_id: str, connector_id: str, delete_secrets: bool = False) -> bool:
        """Delete a connector.
        
        Args:
            project_id: The project ID
            connector_id: The connector ID to delete
            delete_secrets: Whether to also delete secrets from Secure Store
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.connectors.delete(
                project_id="proj-123",
                connector_id="conn-456",
                delete_secrets=True
            )
            ```
        """
        params = {"delete_secrets": delete_secrets} if delete_secrets else {}
        self._client.delete(f"/projects/{project_id}/connectors/{connector_id}", params=params)
        return True
    
    def test_connection(self, project_id: str, connector_id: str) -> bool:
        """Test a connector's database connection.
        
        Args:
            project_id: The project ID
            connector_id: The connector ID to test
            
        Returns:
            True if connection is successful
            
        Raises:
            ValidationError: If connection fails
            
        Example:
            ```python
            try:
                success = client.connectors.test_connection(
                    project_id="proj-123",
                    connector_id="conn-456"
                )
                print("Connection successful!")
            except ValidationError as e:
                print(f"Connection failed: {e}")
            ```
        """
        try:
            resp = self._client.post(f"/projects/{project_id}/connectors/{connector_id}/test")
            return bool(resp.get("ok", False))
        except Exception as e:
            raise ValidationError(f"Connection test failed: {str(e)}")

    def test_connection_detailed(self, project_id: str, connector_id: str) -> dict:
        """Test a connector and return detailed response (e.g., elapsed_ms).
        
        Args:
            project_id: The project ID
            connector_id: The connector ID to test
            
        Returns:
            Dict with fields like { ok: bool, elapsed_ms: int }
        """
        return self._client.post(f"/projects/{project_id}/connectors/{connector_id}/test")
    
    def list_by_type(self, project_id: str, db_type: str) -> List[Connector]:
        """List connectors by database type.
        
        Args:
            project_id: The project ID
            db_type: The database type to filter by
            
        Returns:
            List of connectors of the specified type
            
        Example:
            ```python
            postgres_connectors = client.connectors.list_by_type(
                project_id="proj-123",
                db_type="postgres"
            )
            ```
        """
        # Validate db_type
        if db_type.lower() not in [e.value for e in ConnectorType]:
            valid_types = ", ".join([e.value for e in ConnectorType])
            raise ValidationError(f"Invalid database type. Supported types are: {valid_types}")
        
        all_connectors = self.list(project_id)
        return [conn for conn in all_connectors if conn.db_type.lower() == db_type.lower()]
