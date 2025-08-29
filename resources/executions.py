"""
SQL Executions resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from ..models.executions import (
    SQLExecuteRequest,
    SQLExecuteResponse,
    Execution
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
        connector_id: str,
        chat_message_id: str = None,
        sql_query: str = None,
        h2ogpte_session_id: str = None,
        **kwargs
    ) -> SQLExecuteResponse:
        """Execute a SQL query using the specified connector.
        
        Args:
            connector_id: The database connector ID
            chat_message_id: Optional chat message ID containing SQL query
            sql_query: Optional SQL query to execute directly
            h2ogpte_session_id: Optional H2OGPTE session ID for context
            **kwargs: Additional execution request fields
        
        Returns:
            SQL execution response with results and performance metrics
            
        Example:
            ```python
            # Execute SQL from a chat message
            result = client.executions.execute_sql(
                connector_id="conn-123",
                chat_message_id="msg-456"
            )
            print(f"Execution time: {result.execution_time_ms}ms")
            print(f"Result: {result.result}")
            
            # Execute SQL directly
            result = client.executions.execute_sql(
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
            h2ogpte_session_id=h2ogpte_session_id,
            **kwargs
        )
        
        response = self._client.post(
            "/sql/execute",
            data=request.model_dump()
        )
        return SQLExecuteResponse(**response)
    
    def execute_from_chat(self, connector_id: str, chat_message_id: str, 
                         h2ogpte_session_id: str = None) -> SQLExecuteResponse:
        """Execute SQL from a chat message.
        
        Args:
            connector_id: The database connector ID
            chat_message_id: The chat message containing the SQL query
            h2ogpte_session_id: Optional H2OGPTE session ID for context
        
        Returns:
            SQL execution response
            
        Example:
            ```python
            result = client.executions.execute_from_chat(
                connector_id="conn-123",
                chat_message_id="msg-456"
            )
            ```
        """
        return self.execute_sql(
            connector_id=connector_id,
            chat_message_id=chat_message_id,
            h2ogpte_session_id=h2ogpte_session_id
        )
    
    def execute_query(self, connector_id: str, sql_query: str,
                     h2ogpte_session_id: str = None) -> SQLExecuteResponse:
        """Execute a SQL query directly.
        
        Args:
            connector_id: The database connector ID
            sql_query: The SQL query to execute
            h2ogpte_session_id: Optional H2OGPTE session ID for context
        
        Returns:
            SQL execution response
            
        Example:
            ```python
            result = client.executions.execute_query(
                connector_id="conn-123",
                sql_query="SELECT * FROM users WHERE active = true LIMIT 10"
            )
            print(f"Found {len(result.result.get('data', []))} rows")
            ```
        """
        if not sql_query or not sql_query.strip():
            raise ValidationError("SQL query cannot be empty")
        
        return self.execute_sql(
            connector_id=connector_id,
            sql_query=sql_query,
            h2ogpte_session_id=h2ogpte_session_id
        )
    
    def get_execution(self, execution_id: str) -> Execution:
        """Get execution details by ID.
        
        Args:
            execution_id: The execution ID
            
        Returns:
            Execution details
            
        Example:
            ```python
            execution = client.executions.get_execution("exec-123")
            print(f"Query: {execution.sql_query}")
            print(f"Time: {execution.execution_time_ms}ms")
            ```
        """
        # Note: This endpoint might not exist in the current API
        # This is a placeholder for future implementation
        response = self._client.get(f"/executions/{execution_id}")
        return Execution(**response)
