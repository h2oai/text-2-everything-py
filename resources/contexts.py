"""
Contexts resource for the Text2Everything SDK.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import concurrent.futures
import httpx
from text2everything_sdk.resources.base import BaseResource
from text2everything_sdk.resources.rate_limited_executor import RateLimitedExecutor
from text2everything_sdk.models.contexts import Context, ContextCreate, ContextUpdate, ContextResponse
from text2everything_sdk.exceptions import ValidationError

if TYPE_CHECKING:
    from text2everything_sdk.client import Text2EverythingClient


class ContextsResource(BaseResource):
    """
    Client for managing contexts in the Text2Everything API.
    
    Contexts provide business rules and domain knowledge to improve SQL generation.
    They can contain text content or structured information that helps the AI
    understand the business context and generate more accurate SQL queries.
    """
    
    def list(
        self,
        project_id: str,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        is_always_displayed: Optional[bool] = None,
    ) -> List[Context]:
        """
        List contexts for a specific project.
        
        Args:
            project_id: The project ID to list contexts for
            page: Page number (default: 1)
            per_page: Items per page (default: 50)
            search: Search term to filter contexts by name
            
        Returns:
            List of Context instances
            
        Example:
            >>> contexts = client.contexts.list(project_id="proj_123")
            >>> for context in contexts:
            ...     print(f"{context.name}: {context.is_always_displayed}")
        """
        # Convert to backend params
        params = {
            'skip': (page - 1) * per_page,
            'limit': per_page,
        }
        if search:
            params['q'] = search
        if is_always_displayed is not None:
            params['is_always_displayed'] = is_always_displayed

        endpoint = self._build_endpoint("projects", project_id, "contexts")
        return self._paginate(endpoint, params=params, model_class=Context)
    
    def get(self, project_id: str, context_id: str) -> Context:
        """
        Get a specific context by ID.
        
        Args:
            project_id: The project ID
            context_id: The context ID
            
        Returns:
            Context instance
            
        Raises:
            NotFoundError: If context doesn't exist
            
        Example:
            >>> context = client.contexts.get("proj_123", "ctx_456")
            >>> print(context.content)
        """
        endpoint = self._build_endpoint("projects", project_id, "contexts", context_id)
        response = self._client.get(endpoint)
        return self._create_model_instance(response, Context)
    
    def create(
        self,
        project_id: str,
        name: str,
        content: str,
        description: Optional[str] = None,
        is_always_displayed: bool = False,
        **kwargs
    ) -> Context:
        """
        Create a new context.
        
        Args:
            project_id: The project ID
            name: Context name
            content: Context content (business rules, domain knowledge, etc.)
            description: Context description
            is_always_displayed: Whether this context should always be included
            **kwargs: Additional context fields
            
        Returns:
            Created Context instance
            
        Example:
            >>> context = client.contexts.create(
            ...     project_id="proj_123",
            ...     name="Business Rules",
            ...     content="Active customers have status = 'active'",
            ...     is_always_displayed=True
            ... )
        """
        data = ContextCreate(
            name=name,
            content=content,
            description=description,
            is_always_displayed=is_always_displayed,
            **kwargs
        ).model_dump(exclude_none=True)
        
        endpoint = self._build_endpoint("projects", project_id, "contexts")
        response = self._client.post(endpoint, data=data)
        return self._create_model_instance(response, Context)
    
    def update(
        self,
        project_id: str,
        context_id: str,
        name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        is_always_displayed: Optional[bool] = None,
        **kwargs
    ) -> Context:
        """
        Update an existing context.
        
        Args:
            project_id: The project ID
            context_id: The context ID
            name: New context name
            content: New context content
            description: New context description
            is_always_displayed: Whether this context should always be included
            **kwargs: Additional fields to update
            
        Returns:
            Updated Context instance
            
        Example:
            >>> context = client.contexts.update(
            ...     "proj_123", "ctx_456",
            ...     content="Updated business rules..."
            ... )
        """
        # Get current context data first since API expects complete data
        current_context = self.get(project_id, context_id)
        
        # Use current values as defaults, override with provided values
        update_data = ContextCreate(
            name=name if name is not None else current_context.name,
            content=content if content is not None else current_context.content,
            description=description if description is not None else current_context.description,
            is_always_displayed=is_always_displayed if is_always_displayed is not None else current_context.is_always_displayed,
            **kwargs
        ).model_dump(exclude_none=True)
        
        endpoint = self._build_endpoint("projects", project_id, "contexts", context_id)
        response = self._client.put(endpoint, data=update_data)
        return self._create_model_instance(response, Context)
    
    def delete(self, project_id: str, context_id: str) -> Dict[str, Any]:
        """
        Delete a context.
        
        Args:
            project_id: The project ID
            context_id: The context ID
            
        Returns:
            Deletion confirmation response
            
        Example:
            >>> result = client.contexts.delete("proj_123", "ctx_456")
            >>> print(result["message"])
        """
        endpoint = self._build_endpoint("projects", project_id, "contexts", context_id)
        return self._client.delete(endpoint)
    
    def bulk_delete(
        self,
        project_id: str,
        context_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete multiple contexts at once.
        
        Args:
            project_id: The project ID
            context_ids: List of context IDs to delete
            
        Returns:
            Dict with deletion results:
            - deleted_count: Number of successfully deleted items (int)
            - failed_ids: List of IDs that failed to delete (List[str])
            
        Raises:
            ValidationError: If context_ids is empty or invalid
            
        Example:
            >>> result = client.contexts.bulk_delete(
            ...     project_id="proj_123",
            ...     context_ids=["ctx_1", "ctx_2", "ctx_3"]
            ... )
            >>> print(f"Deleted {result['deleted_count']} contexts")
            >>> if result['failed_ids']:
            ...     print(f"Failed IDs: {result['failed_ids']}")
        """
        if not context_ids:
            raise ValidationError("context_ids cannot be empty")
        
        if not isinstance(context_ids, list):
            raise ValidationError("context_ids must be a list")
        
        payload = {"ids": context_ids}
        endpoint = self._build_endpoint("projects", project_id, "contexts", "bulk-delete")
        return self._client.post(endpoint, data=payload)
    
    def bulk_create(
        self,
        project_id: str,
        contexts: List[Dict[str, Any]],
        parallel: bool = True,
        max_workers: Optional[int] = None,
        max_concurrent: int = 8,
        use_connection_isolation: bool = True
    ) -> List[Context]:
        """
        Create multiple contexts with optional parallel execution and rate limiting.
        
        Args:
            project_id: The project ID
            contexts: List of context data dictionaries
            parallel: Whether to execute requests in parallel (default: True)
            max_workers: Maximum number of parallel workers (default: min(16, len(items)))
            max_concurrent: Maximum number of concurrent requests to prevent server overload (default: 8)
            use_connection_isolation: Use isolated HTTP clients for each request to prevent connection conflicts (default: True)
            
        Returns:
            List of created Context instances in the same order as input
            
        Raises:
            ValidationError: If any validation fails
            
        Example:
            >>> contexts_data = [
            ...     {"name": "Rule 1", "content": "Business rule 1"},
            ...     {"name": "Rule 2", "content": "Business rule 2"}
            ... ]
            >>> # Parallel execution with rate limiting (default)
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data)
            >>> 
            >>> # Sequential execution
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data, parallel=False)
            >>> 
            >>> # Custom rate limiting
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data, max_concurrent=4)
            >>> 
            >>> # Disable connection isolation for shared connection pool
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data, use_connection_isolation=False)
        """
        if not contexts:
            return []
        
        # Pre-validate all contexts
        all_errors = []
        for i, context_data in enumerate(contexts):
            try:
                if not context_data.get("name", "").strip():
                    all_errors.append(f"Item {i} ({context_data.get('name', 'unnamed')}): Name cannot be empty")
                if not context_data.get("content", "").strip():
                    all_errors.append(f"Item {i} ({context_data.get('name', 'unnamed')}): Content cannot be empty")
            except Exception as e:
                all_errors.append(f"Item {i}: Invalid data structure - {str(e)}")
        
        if all_errors:
            raise ValidationError(f"Bulk validation failed: {'; '.join(all_errors)}")
        
        if not parallel or len(contexts) == 1:
            # Sequential execution
            results = []
            for context_data in contexts:
                result = self.create(
                    project_id=project_id,
                    **context_data
                )
                results.append(result)
            return results
        
        # Create the first item sequentially to avoid race conditions when creating collections
        first_result = self.create(
            project_id=project_id,
            **contexts[0]
        )
        
        # Parallel execution for the remaining items
        remaining = contexts[1:]
        if max_workers is None:
            max_workers = min(16, len(remaining))
        
        def create_single_context(indexed_data):
            """Helper function to create a single context with error handling."""
            index, context_data = indexed_data
            try:
                if use_connection_isolation:
                    # Create isolated HTTP client for this request to avoid connection conflicts
                    return index, self._create_with_isolated_client(
                        project_id=project_id,
                        context_data=context_data
                    ), None
                else:
                    # Use shared connection pool
                    return index, self.create(
                        project_id=project_id,
                        **context_data
                    ), None
            except Exception as e:
                return index, None, f"Item {index} ({context_data.get('name', 'unnamed')}): {str(e)}"
        
        # Execute in parallel with RateLimitedExecutor
        results = [None] * len(contexts)
        results[0] = first_result
        errors = []
        
        with RateLimitedExecutor(max_workers=max_workers, max_concurrent=max_concurrent) as executor:
            # Submit tasks for remaining items with their original indices starting at 1
            indexed_data = list(enumerate(remaining, start=1))
            future_to_index = {
                executor.submit_rate_limited(create_single_context, item): item[0] 
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
                f"Bulk create partially failed: {successful_count}/{len(contexts)} succeeded. "
                f"Errors: {'; '.join(errors)}"
            )
        
        return results
    
    def _create_with_isolated_client(self, project_id: str, context_data: Dict[str, Any]) -> Context:
        """
        Create a context using an isolated HTTP client to avoid connection conflicts.
        
        Args:
            project_id: The project ID
            context_data: Context data dictionary
            
        Returns:
            Created Context instance
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
            # Prepare context data
            data = ContextCreate(
                name=context_data["name"],
                content=context_data["content"],
                description=context_data.get("description"),
                is_always_displayed=context_data.get("is_always_displayed", False),
                **{k: v for k, v in context_data.items() if k not in ["name", "content", "description", "is_always_displayed"]}
            ).model_dump(exclude_none=True)
            
            # Build endpoint and headers
            endpoint = self._build_endpoint("projects", project_id, "contexts")
            url = self._client._build_url(endpoint)
            headers = self._client._get_default_headers()
            
            # Make isolated request
            response = isolated_client.post(url, json=data, headers=headers)
            response_data = self._client._handle_response(response)
            
            return self._create_model_instance(response_data, Context)
    
    def get_by_name(self, project_id: str, name: str) -> Optional[Context]:
        """
        Get a context by name within a project.
        
        Args:
            project_id: The project ID
            name: Context name to search for
            
        Returns:
            Context instance if found, None otherwise
            
        Example:
            >>> context = client.contexts.get_by_name("proj_123", "Business Rules")
            >>> if context:
            ...     print(f"Found context: {context.id}")
        """
        contexts = self.list(project_id=project_id, search=name)
        for context in contexts:
            if context.name == name:
                return context
        return None
    
    def list_always_displayed(self, project_id: str) -> List[Context]:
        """
        Get all contexts that are always displayed for a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of Context instances with is_always_displayed=True
            
        Example:
            >>> always_contexts = client.contexts.list_always_displayed("proj_123")
            >>> print(f"Found {len(always_contexts)} always-displayed contexts")
        """
        all_contexts = self.list(project_id=project_id)
        return [ctx for ctx in all_contexts if ctx.is_always_displayed]
