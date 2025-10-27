"""
Main client class for the Text2Everything SDK.
"""

import httpx
import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from text2everything_sdk.exceptions import (
    Text2EverythingError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ConnectionError,
    TimeoutError,
    InvalidConfigurationError
)
from text2everything_sdk.resources.projects import ProjectsResource
from text2everything_sdk.resources.contexts import ContextsResource
from text2everything_sdk.resources.golden_examples import GoldenExamplesResource
from text2everything_sdk.resources.schema_metadata import SchemaMetadataResource
from text2everything_sdk.resources.connectors import ConnectorsResource
from text2everything_sdk.resources.executions import ExecutionsResource
from text2everything_sdk.resources.chat import ChatResource
from text2everything_sdk.resources.chat_sessions import ChatSessionsResource
from text2everything_sdk.resources.chat_presets import ChatPresetsResource
from text2everything_sdk.resources.feedback import FeedbackResource
from text2everything_sdk.resources.custom_tools import CustomToolsResource


class Text2EverythingClient:
    """
    Main client for the Text2Everything API.
    
    This client provides access to all Text2Everything API resources through
    a unified interface with automatic authentication, error handling, and retry logic.
    Optimized for high-concurrency scenarios and long-running requests.
    
    Args:
        base_url: The base URL of the Text2Everything API
        access_token: OIDC access token to send as Authorization Bearer
        workspace_name: Required workspace scope header to include via X-Workspace-Name
            (must start with "workspaces/")
        timeout: Connection timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1)
        read_timeout: Read timeout for long-running requests in seconds (default: 180)
        pool_timeout: Connection pool timeout in seconds (default: 300)
        max_connections: Maximum total connections in pool (default: 50)
        max_keepalive_connections: Maximum keep-alive connections (default: 10)
        keepalive_expiry: Keep-alive connection expiry in seconds (default: 300)
        http2: Enable HTTP/2 support (default: False)
        
    Example:
        >>> # Standard usage (Bearer + required workspace)
        >>> client = Text2EverythingClient(
        ...     base_url="https://api.text2everything.com",
        ...     access_token="your-oidc-access-token",
        ...     workspace_name="workspaces/my-workspace"
        ... )
        >>> 
        >>> # High-concurrency configuration
        >>> client = Text2EverythingClient(
        ...     base_url="https://api.text2everything.com",
        ...     access_token="your-oidc-access-token",
        ...     workspace_name="workspaces/my-workspace",
        ...     read_timeout=300,  # 5 minutes for long requests
        ...     max_connections=100,
        ...     max_keepalive_connections=20
        ... )
        >>> projects = client.projects.list()
        >>> project = client.projects.create(name="My Project")
    """
    
    def __init__(
        self,
        *,
        access_token: str,
        workspace_name: str,
        base_url: str = "http://text2everything.text2everything.svc.cluster.local:8000",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        read_timeout: int = 180,
        pool_timeout: int = 300,
        max_connections: int = 50,
        max_keepalive_connections: int = 10,
        keepalive_expiry: float = 300.0,
        http2: bool = False,
        **kwargs
    ):
        if not base_url:
            raise InvalidConfigurationError("base_url is required and cannot be empty")
        if not access_token:
            raise InvalidConfigurationError("access_token is required and cannot be empty")
        if not workspace_name:
            raise InvalidConfigurationError("workspace_name is required")
        if not str(workspace_name).startswith("workspaces/"):
            raise InvalidConfigurationError("workspace_name must start with 'workspaces/' (e.g., 'workspaces/my-workspace')")
        
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.workspace_name = workspace_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Configure timeouts for long-running requests
        timeout_config = httpx.Timeout(
            connect=timeout,           # Connection establishment timeout
            read=read_timeout,         # Read timeout for long-running requests
            write=timeout,             # Write timeout
            pool=pool_timeout          # Pool timeout
        )
        
        # Configure connection limits for high concurrency
        limits_config = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )
        
        # Initialize HTTP client with optimized settings for high concurrency and long requests
        self._client = httpx.Client(
            timeout=timeout_config,
            limits=limits_config,
            http2=http2,
            **kwargs
        )
        
        # Initialize resource clients
        self.projects = ProjectsResource(self)
        self.contexts = ContextsResource(self)
        self.golden_examples = GoldenExamplesResource(self)
        self.schema_metadata = SchemaMetadataResource(self)
        self.connectors = ConnectorsResource(self)
        self.executions = ExecutionsResource(self)
        self.chat = ChatResource(self)
        self.chat_sessions = ChatSessionsResource(self)
        self.chat_presets = ChatPresetsResource(self)
        self.feedback = FeedbackResource(self)
        self.custom_tools = CustomToolsResource(self)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "text2everything-sdk/1.0.0",
            "Authorization": f"Bearer {self.access_token}",
        }
        if self.workspace_name:
            headers["X-Workspace-Name"] = self.workspace_name
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + "/api/", endpoint.lstrip("/"))
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {"error": "Invalid JSON response"}
        
        if response.status_code == 200 or response.status_code == 201:
            return data
        elif response.status_code == 400:
            raise ValidationError(
                data.get("error", "Validation error"),
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                data.get("error", "Authentication failed"),
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 404:
            raise NotFoundError(
                data.get("error", "Resource not found"),
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                data.get("error", "Rate limit exceeded"),
                retry_after=int(retry_after) if retry_after else None,
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code >= 500:
            raise ServerError(
                data.get("error", "Server error"),
                status_code=response.status_code,
                response_data=data
            )
        else:
            raise Text2EverythingError(
                data.get("error", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                response_data=data
            )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
            
        Raises:
            Text2EverythingError: For API errors
            ConnectionError: For connection issues
            TimeoutError: For request timeouts
        """
        url = self._build_url(endpoint)
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    **kwargs
                )
                return self._handle_response(response)
                
            except httpx.ConnectError as e:
                if attempt == self.max_retries:
                    raise ConnectionError(f"Failed to connect to API: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except httpx.TimeoutException as e:
                if attempt == self.max_retries:
                    raise TimeoutError(f"Request timed out: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except httpx.RemoteProtocolError as e:
                # Handle HTTP protocol errors (like connection drops during high concurrency)
                if attempt == self.max_retries:
                    raise ConnectionError(f"HTTP protocol error: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except httpx.ReadError as e:
                # Handle connection read errors
                if attempt == self.max_retries:
                    raise ConnectionError(f"Connection read error: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except RateLimitError as e:
                if attempt == self.max_retries:
                    raise
                # Use retry_after if provided, otherwise exponential backoff
                delay = e.retry_after or (self.retry_delay * (2 ** attempt))
                time.sleep(delay)
                
            except (ServerError, Text2EverythingError) as e:
                if attempt == self.max_retries or e.status_code < 500:
                    raise
                time.sleep(self.retry_delay * (2 ** attempt))
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def post_multipart(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                      files: Optional[list] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request with multipart form data."""
        return self._make_multipart_request("POST", endpoint, data=data, files=files, **kwargs)
    
    def put_multipart(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     files: Optional[list] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request with multipart form data."""
        return self._make_multipart_request("PUT", endpoint, data=data, files=files, **kwargs)
    
    def _make_multipart_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with multipart form data.
        
        Args:
            method: HTTP method (POST, PUT)
            endpoint: API endpoint
            data: Form data
            files: List of file tuples (field_name, (filename, file_obj, content_type))
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)
        # Start with default headers but remove Content-Type for multipart
        request_headers = self._get_default_headers().copy()
        # Don't set Content-Type for multipart, let httpx set boundary
        if "Content-Type" in request_headers:
            request_headers.pop("Content-Type", None)
        
        # Use list of tuples format which works with FastAPI
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    data=data,
                    files=files,
                    headers=request_headers,
                    **kwargs
                )
                return self._handle_response(response)
                
            except httpx.ConnectError as e:
                if attempt == self.max_retries:
                    raise ConnectionError(f"Failed to connect to API: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except httpx.TimeoutException as e:
                if attempt == self.max_retries:
                    raise TimeoutError(f"Request timed out: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except RateLimitError as e:
                if attempt == self.max_retries:
                    raise
                delay = e.retry_after or (self.retry_delay * (2 ** attempt))
                time.sleep(delay)
                
            except (ServerError, Text2EverythingError) as e:
                if attempt == self.max_retries or e.status_code < 500:
                    raise
                time.sleep(self.retry_delay * (2 ** attempt))
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
