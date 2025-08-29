"""
Contexts resource for the Text2Everything SDK.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import concurrent.futures
from .base import BaseResource
from ..models.contexts import Context, ContextCreate, ContextUpdate, ContextResponse
from ..exceptions import ValidationError

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


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
        search: Optional[str] = None
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
        params = {
            'page': page,
            'per_page': per_page
        }
        if search:
            params['search'] = search
            
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
    
    def bulk_create(
        self,
        project_id: str,
        contexts: List[Dict[str, Any]],
        parallel: bool = True,
        max_workers: Optional[int] = None
    ) -> List[Context]:
        """
        Create multiple contexts with optional parallel execution.
        
        Args:
            project_id: The project ID
            contexts: List of context data dictionaries
            parallel: Whether to execute requests in parallel (default: True)
            max_workers: Maximum number of parallel workers (default: min(32, len(items)))
            
        Returns:
            List of created Context instances in the same order as input
            
        Raises:
            ValidationError: If any validation fails
            
        Example:
            >>> contexts_data = [
            ...     {"name": "Rule 1", "content": "Business rule 1"},
            ...     {"name": "Rule 2", "content": "Business rule 2"}
            ... ]
            >>> # Parallel execution (default)
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data)
            >>> 
            >>> # Sequential execution
            >>> contexts = client.contexts.bulk_create("proj_123", contexts_data, parallel=False)
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
        
        # Parallel execution
        if max_workers is None:
            max_workers = min(32, len(contexts))
        
        def create_single_context(indexed_data):
            """Helper function to create a single context with error handling."""
            index, context_data = indexed_data
            try:
                return index, self.create(
                    project_id=project_id,
                    **context_data
                ), None
            except Exception as e:
                return index, None, f"Item {index} ({context_data.get('name', 'unnamed')}): {str(e)}"
        
        # Execute in parallel with ThreadPoolExecutor
        results = [None] * len(contexts)
        errors = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks with their original indices
            indexed_data = list(enumerate(contexts))
            future_to_index = {
                executor.submit(create_single_context, item): item[0] 
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
