"""
Chat resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from ..models.chat import (
    ChatRequest,
    ChatResponse,
    ChatToAnswerRequest,
    ChatToAnswerResponse,
    AutoFeedbackConfig
)
from ..exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class ChatResource(BaseResource):
    """Resource for natural language to SQL chat functionality."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def chat_to_sql(
        self,
        project_id: str,
        chat_session_id: str,
        query: str,
        h2ogpte_session_id: str,
        schema_metadata_id: str = None,
        contexts_limit: int = None,
        examples_limit: int = None,
        **kwargs
    ) -> ChatResponse:
        """Convert natural language query to SQL.
        
        Args:
            project_id: The project ID
            chat_session_id: Target chat session for history/summary context
            query: Natural language query
            h2ogpte_session_id: H2OGPTE session ID
            schema_metadata_id: Optional schema metadata ID
            contexts_limit: Optional limit for contexts
            examples_limit: Optional limit for examples
            **kwargs: Additional chat request fields
        
        Returns:
            Chat response with generated SQL and explanation
            
        Example:
            ```python
            response = client.chat.chat_to_sql(
                project_id=project_id,
                chat_session_id=chat_session_id,
                query="How many active users do we have?",
                h2ogpte_session_id="session-123",
                schema_metadata_id="schema-456",
                contexts_limit=5,
                examples_limit=3
            )
            print(f"Generated SQL: {response.sql_query}")
            print(f"Explanation: {response.explanation}")
            ```
        """
        # Basic validation
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        
        if not h2ogpte_session_id or not h2ogpte_session_id.strip():
            raise ValidationError("H2OGPTE session ID cannot be empty")
        if not chat_session_id or not chat_session_id.strip():
            raise ValidationError("chat_session_id cannot be empty")
        
        # Build the ChatRequest object internally
        request = ChatRequest(
            query=query,
            chat_session_id=chat_session_id,
            h2ogpte_session_id=h2ogpte_session_id,
            schema_metadata_id=schema_metadata_id,
            contexts_limit=contexts_limit,
            examples_limit=examples_limit,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/chat-sessions/{chat_session_id}/chat-to-sql",
            data=request.model_dump()
        )
        return ChatResponse(**response)
    
    def chat_to_answer(
        self,
        project_id: str,
        chat_session_id: str,
        query: str,
        h2ogpte_session_id: str,
        connector_id: str,
        custom_tool_id: str = None,
        use_agent: bool = False,
        agent_accuracy: str = "medium",
        auto_add_feedback: dict = None,
        **kwargs
    ) -> ChatToAnswerResponse:
        """Convert natural language query to SQL and execute it.
        
        Args:
            project_id: The project ID
            chat_session_id: Target chat session for history/summary context
            query: Natural language query
            h2ogpte_session_id: H2OGPTE session ID
            connector_id: Required connector ID for SQL execution
            custom_tool_id: Optional custom tool to use
            use_agent: Whether to use agent functionality
            agent_accuracy: Agent accuracy level ("low", "medium", "high")
            auto_add_feedback: Optional auto feedback configuration
            **kwargs: Additional chat to answer request fields
        
        Returns:
            Chat response with SQL, execution results, and optional feedback
            
        Example:
            ```python
            response = client.chat.chat_to_answer(
                project_id=project_id,
                query="Show me the top 10 customers by revenue",
                h2ogpte_session_id="session-123",
                connector_id="conn-789",
                use_agent=True,
                agent_accuracy="high"
            )
            
            if response.execution_result:
                print(f"Query executed in {response.execution_result.execution_time_ms}ms")
                print(f"Results: {response.execution_result.result}")
            
            if response.agent_tool_response:
                print(f"Agent response: {response.agent_tool_response}")
            ```
        """
        # Basic validation
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        
        if not h2ogpte_session_id or not h2ogpte_session_id.strip():
            raise ValidationError("H2OGPTE session ID cannot be empty")
        
        if not connector_id or not connector_id.strip():
            raise ValidationError("Connector ID cannot be empty")
        if not chat_session_id or not chat_session_id.strip():
            raise ValidationError("chat_session_id cannot be empty")
        
        # Build the ChatToAnswerRequest object internally
        # Handle auto_add_feedback parameter - if None, let the model use its default
        request_data = {
            "query": query,
            "h2ogpte_session_id": h2ogpte_session_id,
            "chat_session_id": chat_session_id,
            "connector_id": connector_id,  # Include connector_id in request body
            "custom_tool_id": custom_tool_id,
            "use_agent": use_agent,
            "agent_accuracy": agent_accuracy,
            **kwargs
        }
        
        # Handle auto_add_feedback - convert dict to AutoFeedbackConfig if needed
        if auto_add_feedback is not None:
            if isinstance(auto_add_feedback, dict):
                auto_add_feedback = AutoFeedbackConfig(**auto_add_feedback)
            request_data["auto_add_feedback"] = auto_add_feedback
            
        request = ChatToAnswerRequest(**request_data)
        
        # Send request without query parameters
        endpoint = f"/projects/{project_id}/chat-sessions/{chat_session_id}/chat-to-answer"
        
        response = self._client.post(
            endpoint,
            data=request.model_dump()
        )
        return ChatToAnswerResponse(**response)
    
    def chat_with_context(self, project_id: str, chat_session_id: str, query: str, h2ogpte_session_id: str,
                         context_id: str = None, schema_metadata_id: str = None,
                         example_id: str = None, **kwargs) -> ChatResponse:
        """Chat with specific context, schema, or example.
        
        Args:
            project_id: The project ID
            query: Natural language query
            h2ogpte_session_id: H2OGPTE session ID
            context_id: Optional specific context to use
            schema_metadata_id: Optional specific schema metadata to use
            example_id: Optional specific example to use
            **kwargs: Additional chat parameters
        
        Returns:
            Chat response with generated SQL
            
        Example:
            ```python
            response = client.chat.chat_with_context(
                project_id="proj-123",
                chat_session_id="chat-abc",
                query="Count active users",
                h2ogpte_session_id="session-456",
                context_id="ctx-789",
                schema_metadata_id="schema-101",
                llm="gpt-4",
                use_agent=True
            )
            ```
        """
        return self.chat_to_sql(
            project_id=project_id,
            chat_session_id=chat_session_id,
            query=query,
            h2ogpte_session_id=h2ogpte_session_id,
            context_id=context_id,
            schema_metadata_id=schema_metadata_id,
            example_id=example_id,
            **kwargs
        )
    
    def chat_with_agent(self, project_id: str, chat_session_id: str, query: str, h2ogpte_session_id: str,
                       connector_id: str, custom_tool_id: str = None, 
                       agent_accuracy: str = "medium", **kwargs) -> ChatToAnswerResponse:
        """Chat using custom tools and agent functionality.
        
        Args:
            project_id: The project ID
            query: Natural language query
            h2ogpte_session_id: H2OGPTE session ID
            connector_id: Required connector ID for SQL execution
            custom_tool_id: Optional custom tool to use
            agent_accuracy: Agent accuracy level ("low", "medium", "high")
            **kwargs: Additional chat parameters
        
        Returns:
            Chat response with agent tool response
            
        Example:
            ```python
            response = client.chat.chat_with_agent(
                project_id="proj-123",
                chat_session_id="chat-abc",
                query="Analyze customer churn patterns",
                h2ogpte_session_id="session-456",
                connector_id="conn-123",
                custom_tool_id="tool-789",
                agent_accuracy="high"
            )
            print(f"Agent response: {response.agent_tool_response}")
            ```
        """
        return self.chat_to_answer(
            project_id=project_id,
            chat_session_id=chat_session_id,
            query=query,
            h2ogpte_session_id=h2ogpte_session_id,
            connector_id=connector_id,
            custom_tool_id=custom_tool_id,
            use_agent=True,
            agent_accuracy=agent_accuracy,
            **kwargs
        )
