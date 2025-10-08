"""
SQL Executions resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from ..models.executions import (
    SQLExecuteRequest,
    SQLExecuteResponse,
    Execution,
    ExecutionListItem
)
from ..exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class ExecutionsResource(BaseResource):
    """Resource for executing SQL queries against database connectors."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def execute_sql(
        self,
        project_id: str,
        connector_id: str,
        chat_message_id: str = None,
        sql_query: str = None,
        chat_session_id: str = None,
        **kwargs
    ) -> SQLExecuteResponse:
        """Execute a SQL query using the specified connector.
        
        Args:
            connector_id: The database connector ID
            chat_message_id: Optional chat message ID containing SQL query
            sql_query: Optional SQL query to execute directly
            chat_session_id: Optional chat session ID for context
            **kwargs: Additional execution request fields
        
        Returns:
            SQL execution response with results and performance metrics
            
        Example:
            ```python
            # Execute SQL from a chat message
            result = client.executions.execute_sql(
                project_id="proj-123",
                connector_id="conn-123",
                chat_message_id="msg-456"
            )
            print(f"Execution time: {result.execution_time_ms}ms")
            print(f"Result: {result.result}")
            
            # Execute SQL directly
            result = client.executions.execute_sql(
                project_id="proj-123",
                connector_id="conn-123",
                sql_query="SELECT COUNT(*) FROM users"
            )
            ```
        """
        # Validate that exactly one of chat_message_id or sql_query is provided
        if bool(chat_message_id) == bool(sql_query):
            raise ValidationError("Exactly one of chat_message_id or sql_query must be provided")
        
        if not connector_id or not connector_id.strip():
            raise ValidationError("Connector ID cannot be empty")
        
        # Build the SQLExecuteRequest object internally
        request = SQLExecuteRequest(
            connector_id=connector_id,
            chat_message_id=chat_message_id,
            sql_query=sql_query,
            chat_session_id=chat_session_id,
            **kwargs
        )
        
        # Project-scoped execution endpoint
        response = self._client.post(
            f"/projects/{project_id}/sql/execute",
            data=request.model_dump(by_alias=True)
        )
        return SQLExecuteResponse(**response)
    
    def execute_from_chat(self, project_id: str, connector_id: str, chat_message_id: str, 
                         chat_session_id: str = None) -> SQLExecuteResponse:
        """Execute SQL from a chat message.
        
        Args:
            connector_id: The database connector ID
            chat_message_id: The chat message containing the SQL query
            chat_session_id: Optional chat session ID for context
        
        Returns:
            SQL execution response
            
        Example:
            ```python
            result = client.executions.execute_from_chat(
                project_id="proj-123",
                connector_id="conn-123",
                chat_message_id="msg-456"
            )
            ```
        """
        return self.execute_sql(
            project_id=project_id,
            connector_id=connector_id,
            chat_message_id=chat_message_id,
            chat_session_id=chat_session_id
        )
    
    def execute_query(self, project_id: str, connector_id: str, sql_query: str,
                     chat_session_id: str = None) -> SQLExecuteResponse:
        """Execute a SQL query directly.
        
        Args:
            connector_id: The database connector ID
            sql_query: The SQL query to execute
            chat_session_id: Optional chat session ID for context
        
        Returns:
            SQL execution response
            
        Example:
            ```python
            result = client.executions.execute_query(
                project_id="proj-123",
                connector_id="conn-123",
                sql_query="SELECT * FROM users WHERE active = true LIMIT 10"
            )
            print(f"Found {len(result.result.get('data', []))} rows")
            ```
        """
        if not sql_query or not sql_query.strip():
            raise ValidationError("SQL query cannot be empty")
        
        return self.execute_sql(
            project_id=project_id,
            connector_id=connector_id,
            sql_query=sql_query,
            chat_session_id=chat_session_id
        )
    
    def get_execution(self, project_id: str, execution_id: str) -> Execution:
        """Get execution details by ID.
        
        Args:
            execution_id: The execution ID
            
        Returns:
            Execution details
            
        Example:
            ```python
            execution = client.executions.get_execution("proj-123", "exec-123")
            print(f"Query: {execution.sql_query}")
            print(f"Time: {execution.execution_time_ms}ms")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/sql/executions/{execution_id}")
        return Execution(**response)

    def list_executions(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        q: str | None = None,
        connector_id: str | None = None,
        chat_message_id: str | None = None,
    ) -> list[ExecutionListItem]:
        """List SQL executions with optional filters.

        Args:
            skip: Number of items to skip
            limit: Max items to return
            q: Search term
            connector_id: Filter by connector
            chat_message_id: Filter by source chat message

        Returns:
            List of execution summary items
        """
        params = {"skip": skip, "limit": limit}
        if q is not None:
            params["q"] = q
        if connector_id is not None:
            params["connector_id"] = connector_id
        if chat_message_id is not None:
            params["chat_message_id"] = chat_message_id

        endpoint = f"/projects/{project_id}/sql/executions"
        # Use pagination helper to unify response handling
        return self._paginate(endpoint, params=params, model_class=ExecutionListItem)
