"""
Schema metadata resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import concurrent.futures
import httpx
from ..models.schema_metadata import (
    SchemaMetadata,
    SchemaMetadataCreate,
    SchemaMetadataUpdate,
    SchemaMetadataResponse,
    validate_schema_metadata_create,
    validate_schema_metadata_update,
    validate_schema_metadata,
    detect_schema_type
)
from ..exceptions import ValidationError
from .base import BaseResource
from .rate_limited_executor import RateLimitedExecutor

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class SchemaMetadataResource(BaseResource):
    """Resource for managing schema metadata with nested field validation."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        name: str,
        schema_data: Dict[str, Any],
        description: Optional[str] = None,
        is_always_displayed: bool = False,
        validate: bool = True,
        **kwargs
    ) -> SchemaMetadataResponse:
        """Create new schema metadata with validation.
        
        Args:
            project_id: The project ID to create schema metadata in
            name: Schema metadata name
            schema_data: The schema data structure
            description: Optional description
            is_always_displayed: Whether this schema should always be displayed
            validate: Whether to perform nested field validation (default: True)
            **kwargs: Additional schema metadata fields
        
        Returns:
            The created schema metadata with response details
            
        Raises:
            ValidationError: If validation fails and validate=True
            
        Example:
            ```python
            # Create a table schema
            result = client.schema_metadata.create(
                project_id=project_id,
                name="users_table",
                description="User information table",
                schema_data={
                    "table": {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": "email", "type": "string"}
                        ]
                    }
                },
                is_always_displayed=True
            )
            ```
        """
        # Build the SchemaMetadataCreate object internally
        schema_metadata = SchemaMetadataCreate(
            name=name,
            schema_data=schema_data,
            description=description,
            is_always_displayed=is_always_displayed,
            **kwargs
        )
        
        if validate:
            validation_errors = validate_schema_metadata_create(schema_metadata)
            if validation_errors:
                raise ValidationError(f"Schema metadata validation failed: {'; '.join(validation_errors)}")
        
        response = self._client.post(
            f"/projects/{project_id}/schema-metadata",
            data=schema_metadata.model_dump()
        )
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return SchemaMetadataResponse(**response_data)
    
    def get(self, project_id: str, schema_metadata_id: str) -> SchemaMetadataResponse:
        """Get schema metadata by ID.
        
        Args:
            project_id: The project ID
            schema_metadata_id: The schema metadata ID
            
        Returns:
            The schema metadata details
            
        Example:
            ```python
            schema_metadata = client.schema_metadata.get(project_id, schema_metadata_id)
            print(f"Schema type: {detect_schema_type(schema_metadata.schema_data)}")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/schema-metadata/{schema_metadata_id}")
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return SchemaMetadataResponse(**response_data)
    
    def list(self, project_id: str, limit: int = 100, offset: int = 0) -> List[SchemaMetadataResponse]:
        """List schema metadata for a project.
        
        Args:
            project_id: The project ID
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of schema metadata
            
        Example:
            ```python
            all_schemas = client.schema_metadata.list(project_id)
            tables = [s for s in all_schemas if detect_schema_type(s.schema_data) == "table"]
            ```
        """
        endpoint = f"/projects/{project_id}/schema-metadata"
        params = {"limit": limit, "offset": offset}
        return self._paginate(endpoint, params=params, model_class=SchemaMetadataResponse)
    
    def update(
        self,
        project_id: str,
        schema_metadata_id: str,
        name: Optional[str] = None,
        schema_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        is_always_displayed: Optional[bool] = None,
        validate: bool = True,
        **kwargs
    ) -> SchemaMetadataResponse:
        """Update schema metadata with validation.
        
        Args:
            project_id: The project ID
            schema_metadata_id: The schema metadata ID to update
            name: New schema metadata name
            schema_data: New schema data structure
            description: New description
            is_always_displayed: New always displayed setting
            validate: Whether to perform nested field validation (default: True)
            **kwargs: Additional fields to update
            
        Returns:
            The updated schema metadata
            
        Raises:
            ValidationError: If validation fails and validate=True
            
        Example:
            ```python
            # Update a dimension schema
            result = client.schema_metadata.update(
                project_id=project_id,
                schema_metadata_id=schema_id,
                description="Updated dimension description",
                schema_data={
                    "table": {
                        "dimension": {
                            "name": "updated_dimension",
                            "content": {"type": "categorical", "values": ["A", "B", "C"]}
                        }
                    }
                }
            )
            ```
        """
        # Get current schema metadata first since API expects complete data
        current_schema = self.get(project_id, schema_metadata_id)
        
        # Use current values as defaults, override with provided values
        update_data = SchemaMetadataCreate(
            name=name if name is not None else current_schema.name,
            description=description if description is not None else current_schema.description,
            schema_data=schema_data if schema_data is not None else current_schema.schema_data,
            is_always_displayed=is_always_displayed if is_always_displayed is not None else current_schema.is_always_displayed,
            **kwargs
        )
        
        if validate:
            validation_errors = validate_schema_metadata_create(update_data)
            if validation_errors:
                raise ValidationError(f"Schema metadata validation failed: {'; '.join(validation_errors)}")
        
        response = self._client.put(
            f"/projects/{project_id}/schema-metadata/{schema_metadata_id}",
            data=update_data.model_dump()
        )
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return SchemaMetadataResponse(**response_data)
    
    def delete(self, project_id: str, schema_metadata_id: str) -> bool:
        """Delete schema metadata.
        
        Args:
            project_id: The project ID
            schema_metadata_id: The schema metadata ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.schema_metadata.delete(project_id, schema_metadata_id)
            ```
        """
        self._client.delete(f"/projects/{project_id}/schema-metadata/{schema_metadata_id}")
        return True
    
    def list_by_type(self, project_id: str, schema_type: str) -> List[SchemaMetadataResponse]:
        """List schema metadata filtered by type.
        
        Args:
            project_id: The project ID
            schema_type: The schema type to filter by ('table', 'dimension', 'metric', 'relationship')
            
        Returns:
            List of schema metadata of the specified type
            
        Example:
            ```python
            # Get all table schemas
            tables = client.schema_metadata.list_by_type(project_id, "table")
            
            # Get all metrics
            metrics = client.schema_metadata.list_by_type(project_id, "metric")
            ```
        """
        all_schemas = self.list(project_id)
        return [
            schema for schema in all_schemas 
            if detect_schema_type(schema.schema_data) == schema_type
        ]
    
    def validate_schema(self, schema_data: Dict[str, Any], expected_type: Optional[str] = None) -> List[str]:
        """Validate schema data structure with nested field checks.
        
        Args:
            schema_data: The schema data to validate
            expected_type: Optional expected schema type
            
        Returns:
            List of validation error messages (empty if valid)
            
        Example:
            ```python
            # Validate a table schema
            table_data = {
                "table": {
                    "name": "users",
                    "columns": [{"name": "id", "type": "integer"}]
                }
            }
            errors = client.schema_metadata.validate_schema(table_data, "table")
            if not errors:
                print("Schema is valid!")
            ```
        """
        return validate_schema_metadata({"name": "validation_test", "schema_data": schema_data}, expected_type)
    
    def get_schema_type(self, schema_data: Dict[str, Any]) -> Optional[str]:
        """Detect the schema type from schema data structure.
        
        Args:
            schema_data: The schema data to analyze
            
        Returns:
            The detected schema type or None if unable to detect
            
        Example:
            ```python
            schema_type = client.schema_metadata.get_schema_type(schema_data)
            print(f"Detected schema type: {schema_type}")
            ```
        """
        return detect_schema_type(schema_data)
    
    def bulk_create(
        self, 
        project_id: str, 
        schema_metadata_list: List[Dict[str, Any]], 
        validate: bool = True,
        parallel: bool = True,
        max_workers: Optional[int] = None,
        max_concurrent: int = 8,
        use_connection_isolation: bool = True
    ) -> List[SchemaMetadataResponse]:
        """Create multiple schema metadata items with validation and optional parallel execution.
        
        Args:
            project_id: The project ID
            schema_metadata_list: List of schema metadata dictionaries to create
            validate: Whether to perform nested field validation (default: True)
            parallel: Whether to execute requests in parallel (default: True)
            max_workers: Maximum number of parallel workers (default: min(16, len(items)))
            max_concurrent: Maximum number of concurrent requests (default: 8, rate limiting)
            use_connection_isolation: Use isolated HTTP clients for each request to prevent connection conflicts (default: True)
            
        Returns:
            List of created schema metadata in the same order as input
            
        Raises:
            ValidationError: If any validation fails and validate=True, or if any creation fails
            
        Example:
            ```python
            schemas = [
                {
                    "name": "table1", 
                    "schema_data": {"table": {"columns": []}},
                    "description": "First table"
                },
                {
                    "name": "dim1", 
                    "schema_data": {"table": {"dimension": {"content": {}}}},
                    "is_always_displayed": True
                }
            ]
            # Parallel execution (default)
            results = client.schema_metadata.bulk_create(project_id, schemas)
            
            # Sequential execution
            results = client.schema_metadata.bulk_create(project_id, schemas, parallel=False)
            
            # Disable connection isolation for shared connection pool
            results = client.schema_metadata.bulk_create(project_id, schemas, use_connection_isolation=False)
            ```
        """
        if not schema_metadata_list:
            return []
        
        # Pre-validate all items if validation is enabled
        if validate:
            all_errors = []
            for i, schema_data in enumerate(schema_metadata_list):
                try:
                    # Create temporary object for validation
                    temp_schema = SchemaMetadataCreate(**schema_data)
                    validation_errors = validate_schema_metadata_create(temp_schema)
                    if validation_errors:
                        all_errors.append(f"Item {i} ({schema_data.get('name', 'unnamed')}): {'; '.join(validation_errors)}")
                except Exception as e:
                    all_errors.append(f"Item {i} ({schema_data.get('name', 'unnamed')}): Invalid data structure - {str(e)}")
            
            if all_errors:
                raise ValidationError(f"Bulk validation failed: {'; '.join(all_errors)}")
        
        if not parallel or len(schema_metadata_list) == 1:
            # Sequential execution
            results = []
            for schema_data in schema_metadata_list:
                result = self.create(
                    project_id=project_id,
                    validate=False,  # Already validated
                    **schema_data
                )
                results.append(result)
            return results
        
        # Create the first item sequentially to avoid race conditions when creating collections
        first_result = self.create(
            project_id=project_id,
            validate=False,
            **schema_metadata_list[0]
        )
        
        # Parallel execution for remaining items with rate limiting
        remaining = schema_metadata_list[1:]
        if max_workers is None:
            max_workers = min(16, len(remaining))
        
        def create_single_schema(indexed_data):
            """Helper function to create a single schema with error handling."""
            index, schema_data = indexed_data
            try:
                if use_connection_isolation:
                    # Create isolated HTTP client for this request to avoid connection conflicts
                    return index, self._create_with_isolated_client(
                        project_id=project_id,
                        schema_data=schema_data
                    ), None
                else:
                    # Use shared connection pool
                    return index, self.create(
                        project_id=project_id,
                        validate=False,  # Already validated
                        **schema_data
                    ), None
            except Exception as e:
                return index, None, f"Item {index} ({schema_data.get('name', 'unnamed')}): {str(e)}"
        
        # Execute in parallel with rate-limited executor
        results = [None] * len(schema_metadata_list)
        results[0] = first_result
        errors = []
        
        with RateLimitedExecutor(max_workers=max_workers, max_concurrent=max_concurrent) as executor:
            # Submit tasks for remaining items with their original indices starting at 1
            indexed_data = list(enumerate(remaining, start=1))
            future_to_index = {
                executor.submit_rate_limited(create_single_schema, item): item[0] 
                for item in indexed_data
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_index):
                index, result, error = future.result()
                if error:
                    errors.append(error)
                else:
                    results[index] = result
        
        # Check for any errors
        if errors:
            successful_count = sum(1 for r in results if r is not None)
            raise ValidationError(
                f"Bulk create partially failed: {successful_count}/{len(schema_metadata_list)} succeeded. "
                f"Errors: {'; '.join(errors)}"
            )
        
        return results
    
    def _create_with_isolated_client(self, project_id: str, schema_data: Dict[str, Any]) -> SchemaMetadataResponse:
        """
        Create schema metadata using an isolated HTTP client to avoid connection conflicts.
        
        Args:
            project_id: The project ID
            schema_data: Schema metadata data dictionary
            
        Returns:
            Created SchemaMetadataResponse instance
        """
        # Create isolated HTTP client with same configuration as main client
        timeout_config = httpx.Timeout(
            connect=30,      # Connection timeout
            read=180,        # Read timeout for long requests
            write=30,        # Write timeout
            pool=300         # Pool timeout
        )
        
        limits_config = httpx.Limits(
            max_connections=1,           # Single connection for isolation
            max_keepalive_connections=0, # No keep-alive to avoid state issues
            keepalive_expiry=0           # Immediate expiry
        )
        
        with httpx.Client(
            timeout=timeout_config,
            limits=limits_config,
            http2=False  # Use HTTP/1.1 for better compatibility
        ) as isolated_client:
            # Prepare schema metadata
            schema_metadata = SchemaMetadataCreate(
                name=schema_data["name"],
                schema_data=schema_data["schema_data"],
                description=schema_data.get("description"),
                is_always_displayed=schema_data.get("is_always_displayed", False),
                **{k: v for k, v in schema_data.items() if k not in ["name", "schema_data", "description", "is_always_displayed"]}
            )
            
            # Build endpoint and headers
            url = self._client._build_url(f"/projects/{project_id}/schema-metadata")
            headers = self._client._get_default_headers()
            
            # Make isolated request
            response = isolated_client.post(url, json=schema_metadata.model_dump(), headers=headers)
            response_data = self._client._handle_response(response)
            
            # Handle both list and single object responses
            if isinstance(response_data, list):
                if response_data:
                    response_data = response_data[0]  # Take first item from list
                else:
                    raise ValidationError("API returned empty list")
            
            return SchemaMetadataResponse(**response_data)
    
    def list_always_displayed(self, project_id: str) -> List[SchemaMetadataResponse]:
        """List schema metadata that are marked as always displayed.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of schema metadata marked as always displayed
            
        Example:
            ```python
            important_schemas = client.schema_metadata.list_always_displayed(project_id)
            ```
        """
        all_schemas = self.list(project_id)
        return [schema for schema in all_schemas if schema.is_always_displayed]
