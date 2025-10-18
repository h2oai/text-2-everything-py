"""
Golden examples resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import concurrent.futures
import httpx
from ..models.golden_examples import (
    GoldenExample,
    GoldenExampleCreate,
    GoldenExampleUpdate,
    GoldenExampleResponse
)
from ..exceptions import ValidationError
from .base import BaseResource
from .rate_limited_executor import RateLimitedExecutor

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class GoldenExamplesResource(BaseResource):
    """Resource for managing golden examples (query-SQL pairs)."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        user_query: str,
        sql_query: str,
        description: Optional[str] = None,
        is_always_displayed: bool = False,
        **kwargs
    ) -> GoldenExampleResponse:
        """Create a new golden example.
        
        Args:
            project_id: The project ID to create the golden example in
            user_query: The natural language query
            sql_query: The corresponding SQL query
            description: Optional description of the golden example
            is_always_displayed: Whether this example should always be displayed
            **kwargs: Additional golden example fields
        
        Returns:
            The created golden example with response details
            
        Example:
            ```python
            result = client.golden_examples.create(
                project_id=project_id,
                user_query="How many users do we have?",
                sql_query="SELECT COUNT(*) FROM users;",
                description="Count total users",
                is_always_displayed=True
            )
            ```
        """
        # Basic validation
        if not user_query or not user_query.strip():
            raise ValidationError("User query cannot be empty")
        
        if not sql_query or not sql_query.strip():
            raise ValidationError("SQL query cannot be empty")
        
        # Build the GoldenExampleCreate object internally
        golden_example = GoldenExampleCreate(
            user_query=user_query,
            sql_query=sql_query,
            description=description,
            is_always_displayed=is_always_displayed,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/golden-examples",
            data=golden_example.model_dump()
        )
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return GoldenExampleResponse(**response_data)
    
    def get(self, project_id: str, golden_example_id: str) -> GoldenExampleResponse:
        """Get a golden example by ID.
        
        Args:
            project_id: The project ID
            golden_example_id: The golden example ID
            
        Returns:
            The golden example details
            
        Example:
            ```python
            golden_example = client.golden_examples.get(project_id, golden_example_id)
            print(f"Query: {golden_example.user_query}")
            print(f"SQL: {golden_example.sql_query}")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/golden-examples/{golden_example_id}")
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return GoldenExampleResponse(**response_data)
    
    def list(self, project_id: str, skip: int = 0, limit: int = 100, search: Optional[str] = None, is_always_displayed: Optional[bool] = None) -> List[GoldenExampleResponse]:
        """List golden examples for a project.
        
        Args:
            project_id: The project ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search query
            is_always_displayed: Optional filter for always displayed items
            
        Returns:
            List of golden examples
            
        Example:
            ```python
            examples = client.golden_examples.list(project_id)
            for example in examples:
                print(f"{example.user_message} -> {example.expected_sql}")
            ```
        """
        endpoint = f"/projects/{project_id}/golden-examples"
        params = {"limit": limit, "skip": skip}
        if search:
            params["q"] = search
        if is_always_displayed is not None:
            params["is_always_displayed"] = is_always_displayed
        return self._paginate(endpoint, params=params, model_class=GoldenExampleResponse)
    
    def update(
        self,
        project_id: str,
        golden_example_id: str,
        user_query: Optional[str] = None,
        sql_query: Optional[str] = None,
        description: Optional[str] = None,
        is_always_displayed: Optional[bool] = None,
        **kwargs
    ) -> GoldenExampleResponse:
        """Update a golden example.
        
        Args:
            project_id: The project ID
            golden_example_id: The golden example ID to update
            user_query: New user query
            sql_query: New SQL query
            description: New description
            is_always_displayed: New always displayed setting
            **kwargs: Additional fields to update
            
        Returns:
            The updated golden example
            
        Example:
            ```python
            result = client.golden_examples.update(
                project_id=project_id,
                golden_example_id=example_id,
                description="Updated description",
                sql_query="SELECT COUNT(*) as total_users FROM users WHERE active = true;"
            )
            ```
        """
        # Get current golden example first since API expects complete data
        current_example = self.get(project_id, golden_example_id)
        
        # Use current values as defaults, override with provided values
        update_data = GoldenExampleCreate(
            user_query=user_query if user_query is not None else current_example.user_query,
            sql_query=sql_query if sql_query is not None else current_example.sql_query,
            description=description if description is not None else current_example.description,
            is_always_displayed=is_always_displayed if is_always_displayed is not None else current_example.is_always_displayed,
            **kwargs
        )
        
        # Validate non-empty queries
        if not update_data.user_query or not update_data.user_query.strip():
            raise ValidationError("User query cannot be empty")
        
        if not update_data.sql_query or not update_data.sql_query.strip():
            raise ValidationError("SQL query cannot be empty")
        
        response = self._client.put(
            f"/projects/{project_id}/golden-examples/{golden_example_id}",
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
        
        return GoldenExampleResponse(**response_data)
    
    def delete(self, project_id: str, golden_example_id: str) -> bool:
        """Delete a golden example.
        
        Args:
            project_id: The project ID
            golden_example_id: The golden example ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.golden_examples.delete(project_id, golden_example_id)
            ```
        """
        self._client.delete(f"/projects/{project_id}/golden-examples/{golden_example_id}")
        return True
    
    def search_by_query(self, project_id: str, search_term: str) -> List[GoldenExampleResponse]:
        """Search golden examples by user query text.
        
        Args:
            project_id: The project ID
            search_term: Term to search for in user queries
            
        Returns:
            List of golden examples matching the search term
            
        Example:
            ```python
            # Find examples related to users
            user_examples = client.golden_examples.search_by_query(project_id, "user")
            ```
        """
        all_examples = self.list(project_id)
        search_term_lower = search_term.lower()
        
        return [
            example for example in all_examples
            if search_term_lower in example.user_query.lower()
        ]
    
    
    def bulk_create(
        self, 
        project_id: str, 
        golden_examples: List[Dict[str, Any]], 
        parallel: bool = True,
        max_workers: Optional[int] = None,
        max_concurrent: int = 8,
        use_connection_isolation: bool = True
    ) -> List[GoldenExampleResponse]:
        """Create multiple golden examples with optional parallel execution and rate limiting.
        
        Args:
            project_id: The project ID
            golden_examples: List of golden example dictionaries to create
            parallel: Whether to execute requests in parallel (default: True)
            max_workers: Maximum number of parallel workers (default: min(16, len(items)))
            max_concurrent: Maximum number of concurrent requests to prevent server overload (default: 8)
            use_connection_isolation: Use isolated HTTP clients for each request to prevent connection conflicts (default: True)
            
        Returns:
            List of created golden examples in the same order as input
            
        Raises:
            ValidationError: If any validation fails
            
        Example:
            ```python
            examples = [
                {
                    "user_query": "How many users?",
                    "sql_query": "SELECT COUNT(*) FROM users;",
                    "description": "Count total users"
                },
                {
                    "user_query": "How many active users?",
                    "sql_query": "SELECT COUNT(*) FROM users WHERE active = true;",
                    "is_always_displayed": True
                }
            ]
            # Parallel execution with rate limiting (default)
            results = client.golden_examples.bulk_create(project_id, examples)
            
            # Sequential execution
            results = client.golden_examples.bulk_create(project_id, examples, parallel=False)
            
            # Custom rate limiting
            results = client.golden_examples.bulk_create(project_id, examples, max_concurrent=4)
            
            # Disable connection isolation for shared connection pool
            results = client.golden_examples.bulk_create(project_id, examples, use_connection_isolation=False)
            ```
        """
        if not golden_examples:
            return []
        
        # Pre-validate all examples
        all_errors = []
        for i, example_data in enumerate(golden_examples):
            try:
                if not example_data.get("user_query", "").strip():
                    all_errors.append(f"Item {i} ({example_data.get('user_query', 'unnamed')}): User query cannot be empty")
                if not example_data.get("sql_query", "").strip():
                    all_errors.append(f"Item {i} ({example_data.get('user_query', 'unnamed')}): SQL query cannot be empty")
            except Exception as e:
                all_errors.append(f"Item {i}: Invalid data structure - {str(e)}")
        
        if all_errors:
            raise ValidationError(f"Bulk validation failed: {'; '.join(all_errors)}")
        
        if not parallel or len(golden_examples) == 1:
            # Sequential execution
            results = []
            for example_data in golden_examples:
                result = self.create(
                    project_id=project_id,
                    **example_data
                )
                results.append(result)
            return results
        
        # Create the first item sequentially to avoid race conditions when creating collections
        first_result = self.create(
            project_id=project_id,
            **golden_examples[0]
        )
        
        # Parallel execution for remaining items
        remaining = golden_examples[1:]
        if max_workers is None:
            max_workers = min(16, len(remaining))
        
        def create_single_example(indexed_data):
            """Helper function to create a single golden example with error handling."""
            index, example_data = indexed_data
            try:
                if use_connection_isolation:
                    # Create isolated HTTP client for this request to avoid connection conflicts
                    return index, self._create_with_isolated_client(
                        project_id=project_id,
                        example_data=example_data
                    ), None
                else:
                    # Use shared connection pool
                    return index, self.create(
                        project_id=project_id,
                        **example_data
                    ), None
            except Exception as e:
                return index, None, f"Item {index} ({example_data.get('user_query', 'unnamed')}): {str(e)}"
        
        # Execute in parallel with RateLimitedExecutor
        results = [None] * len(golden_examples)
        results[0] = first_result
        errors = []
        
        with RateLimitedExecutor(max_workers=max_workers, max_concurrent=max_concurrent) as executor:
            # Submit tasks for remaining items with their original indices starting at 1
            indexed_data = list(enumerate(remaining, start=1))
            future_to_index = {
                executor.submit_rate_limited(create_single_example, item): item[0] 
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
                f"Bulk create partially failed: {successful_count}/{len(golden_examples)} succeeded. "
                f"Errors: {'; '.join(errors)}"
            )
        
        return results
    
    def _create_with_isolated_client(self, project_id: str, example_data: Dict[str, Any]) -> GoldenExampleResponse:
        """
        Create a golden example using an isolated HTTP client to avoid connection conflicts.
        
        Args:
            project_id: The project ID
            example_data: Golden example data dictionary
            
        Returns:
            Created GoldenExampleResponse instance
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
            # Prepare golden example
            golden_example = GoldenExampleCreate(
                user_query=example_data["user_query"],
                sql_query=example_data["sql_query"],
                description=example_data.get("description"),
                is_always_displayed=example_data.get("is_always_displayed", False),
                **{k: v for k, v in example_data.items() if k not in ["user_query", "sql_query", "description", "is_always_displayed"]}
            )
            
            # Build endpoint and headers
            url = self._client._build_url(f"/projects/{project_id}/golden-examples")
            headers = self._client._get_default_headers()
            
            # Make isolated request
            response = isolated_client.post(url, json=golden_example.model_dump(), headers=headers)
            response_data = self._client._handle_response(response)
            
            # Handle both list and single object responses
            if isinstance(response_data, list):
                if response_data:
                    response_data = response_data[0]  # Take first item from list
                else:
                    raise ValidationError("API returned empty list")
            
            return GoldenExampleResponse(**response_data)
    
    def list_always_displayed(self, project_id: str) -> List[GoldenExampleResponse]:
        """List golden examples that are marked as always displayed.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of golden examples marked as always displayed
            
        Example:
            ```python
            important_examples = client.golden_examples.list_always_displayed(project_id)
            ```
        """
        all_examples = self.list(project_id)
        return [example for example in all_examples if example.is_always_displayed]
