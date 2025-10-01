"""
Base resource class for the Text2Everything SDK.
"""

from typing import TYPE_CHECKING, Dict, Any, List, Optional, Type, TypeVar
from ..models.base import BaseModel, PaginatedResponse

if TYPE_CHECKING:
    from ..client import Text2EverythingClient

T = TypeVar('T', bound=BaseModel)


class BaseResource:
    """
    Base class for all API resource clients.
    
    Provides common functionality for CRUD operations and pagination.
    """
    
    def __init__(self, client: "Text2EverythingClient"):
        self._client = client
    
    def _build_endpoint(self, *parts: str) -> str:
        """Build endpoint URL from parts."""
        return "/".join(str(part) for part in parts if part)
    
    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        model_class: Optional[Type[T]] = None
    ) -> List[T]:
        """
        Handle paginated responses.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            model_class: Pydantic model class for response items
            
        Returns:
            List of model instances
        """
        all_items = []
        page = 1
        per_page = params.get('per_page', 50) if params else 50
        
        while True:
            page_params = (params or {}).copy()
            page_params.update({'page': page, 'per_page': per_page})
            
            response = self._client.get(endpoint, params=page_params)

            # Handle both paginated and non-paginated responses
            if isinstance(response, list):
                # Direct list response
                items = response
                has_more = len(items) == per_page
            elif isinstance(response, dict) and 'items' in response:
                # Backend returns { items, total, page, page_size, has_next }
                items = response.get('items', [])
                # Derive has_more from explicit has_next if present; otherwise compute
                if 'has_next' in response:
                    has_more = bool(response.get('has_next'))
                else:
                    total = response.get('total')
                    page_value = response.get('page') or page
                    page_size_value = response.get('page_size') or per_page
                    has_more = (page_value * page_size_value) < (total or 0)
            else:
                # Single item response
                items = [response] if response else []
                has_more = False
            
            # Convert to model instances if model_class provided
            if model_class:
                items = [model_class(**item) for item in items]
            
            all_items.extend(items)
            
            if not has_more:
                break
                
            page += 1
        
        return all_items
    
    def _create_model_instance(self, data: Dict[str, Any], model_class: Type[T]) -> T:
        """Create model instance from response data."""
        return model_class(**data)
    
    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for API request (remove None values, etc.)."""
        return {k: v for k, v in data.items() if v is not None}
