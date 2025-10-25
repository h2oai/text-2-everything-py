"""
Chat resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from models.chat import (
    ChatRequest,
    ChatResponse,
    ChatToAnswerRequest,
    ChatToAnswerResponse,
    AutoFeedbackConfig,
    ExecutionCacheLookupRequest,
    ExecutionCacheLookupResponse
)
from exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from client import Text2EverythingClient


class ChatResource(BaseResource):
    """Resource for natural language to SQL chat functionality."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def chat_to_sql(
        self,
        project_id: str,
        chat_session_id: str,
        query: str,
        schema_metadata_id: str = None,
        contexts_limit: int = None,
        examples_limit: int = None,
        contexts_cutoff: float = None,
        schema_cutoff: float = None,
        feedback_cutoff: float = None,
        examples_cutoff: float = None,
        system_prompt: str = None,
        **kwargs
    ) -> ChatResponse:
        """Convert natural language query to SQL.
        
        Args:
            project_id: The project ID
            chat_session_id: Target chat session for history/summary context
            query: Natural language query
            schema_metadata_id: Optional schema metadata ID
            contexts_limit: Optional limit for contexts
            examples_limit: Optional limit for examples
            contexts_cutoff: Optional similarity cutoff for contexts (0.0-1.0, higher = more restrictive)
            schema_cutoff: Optional similarity cutoff for schema metadata (0.0-1.0, higher = more restrictive)
            feedback_cutoff: Optional similarity cutoff for feedback (0.0-1.0, higher = more restrictive)
            examples_cutoff: Optional similarity cutoff for examples (0.0-1.0, higher = more restrictive)
            **kwargs: Additional chat request fields
        
        Returns:
            Chat response with generated SQL and explanation
            
        Example:
            ```python
            response = client.chat.chat_to_sql(
                project_id=project_id,
                chat_session_id=chat_session_id,
                query="How many active users do we have?",
                schema_metadata_id="schema-456",
                contexts_limit=5,
                examples_limit=3,
                contexts_cutoff=0.5,
                schema_cutoff=0.7
            )
            print(f"Generated SQL: {response.sql_query}")
            print(f"Explanation: {response.explanation}")
            ```
        """
        # Basic validation
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        
        if not chat_session_id or not chat_session_id.strip():
            raise ValidationError("chat_session_id cannot be empty")
        
        # Build the ChatRequest object internally
        request = ChatRequest(
            query=query,
            schema_metadata_id=schema_metadata_id,
            contexts_limit=contexts_limit,
            examples_limit=examples_limit,
            contexts_cutoff=contexts_cutoff,
            schema_cutoff=schema_cutoff,
            feedback_cutoff=feedback_cutoff,
            examples_cutoff=examples_cutoff,
            system_prompt=system_prompt,
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
        connector_id: str,
        custom_tool_id: str = None,
        use_agent: bool = False,
        agent_accuracy: str = "medium",
        auto_add_feedback: dict = None,
        contexts_cutoff: float = None,
        schema_cutoff: float = None,
        feedback_cutoff: float = None,
        examples_cutoff: float = None,
        system_prompt: str = None,
        **kwargs
    ) -> ChatToAnswerResponse:
        """Convert natural language query to SQL and execute it.
        
        Args:
            project_id: The project ID
            chat_session_id: Target chat session for history/summary context
            query: Natural language query
            connector_id: Required connector ID for SQL execution
            custom_tool_id: Optional custom tool to use
            use_agent: Whether to use agent functionality
            agent_accuracy: Agent accuracy level ("low", "medium", "high")
            auto_add_feedback: Optional auto feedback configuration
            contexts_cutoff: Optional similarity cutoff for contexts (0.0-1.0, higher = more restrictive)
            schema_cutoff: Optional similarity cutoff for schema metadata (0.0-1.0, higher = more restrictive)
            feedback_cutoff: Optional similarity cutoff for feedback (0.0-1.0, higher = more restrictive)
            examples_cutoff: Optional similarity cutoff for examples (0.0-1.0, higher = more restrictive)
            **kwargs: Additional chat to answer request fields
        
        Returns:
            Chat response with SQL, execution results, and optional feedback
            
        Example:
            ```python
            response = client.chat.chat_to_answer(
                project_id=project_id,
                query="Show me the top 10 customers by revenue",
                connector_id="conn-789",
                use_agent=True,
                agent_accuracy="high",
                contexts_cutoff=0.5,
                schema_cutoff=0.7
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
        
        
        if not connector_id or not connector_id.strip():
            raise ValidationError("Connector ID cannot be empty")
        if not chat_session_id or not chat_session_id.strip():
            raise ValidationError("chat_session_id cannot be empty")
        
        # Build the ChatToAnswerRequest object internally
        # Handle auto_add_feedback parameter - if None, let the model use its default
        request_data = {
            "query": query,
            "connector_id": connector_id,  # Include connector_id in request body
            "custom_tool_id": custom_tool_id,
            "use_agent": use_agent,
            "agent_accuracy": agent_accuracy,
            "contexts_cutoff": contexts_cutoff,
            "schema_cutoff": schema_cutoff,
            "feedback_cutoff": feedback_cutoff,
            "examples_cutoff": examples_cutoff,
            "system_prompt": system_prompt,
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
    
    def chat_with_context(self, project_id: str, chat_session_id: str, query: str,
                         context_id: str = None, schema_metadata_id: str = None,
                         example_id: str = None, **kwargs) -> ChatResponse:
        """Chat with specific context, schema, or example.
        
        Args:
            project_id: The project ID
            query: Natural language query
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
            context_id=context_id,
            schema_metadata_id=schema_metadata_id,
            example_id=example_id,
            **kwargs
        )
    
    def chat_with_agent(self, project_id: str, chat_session_id: str, query: str,
                       connector_id: str, custom_tool_id: str = None, 
                       agent_accuracy: str = "medium", **kwargs) -> ChatToAnswerResponse:
        """Chat using custom tools and agent functionality.
        
        Args:
            project_id: The project ID
            query: Natural language query
            connector_id: Required connector ID for SQL execution
            custom_tool_id: Optional custom tool to use
            agent_accuracy: Agent accuracy level ("quick", "basic", "standard", "maximum")
            **kwargs: Additional chat parameters
        
        Returns:
            Chat response with agent tool response
            
        Example:
            ```python
            response = client.chat.chat_with_agent(
                project_id="proj-123",
                chat_session_id="chat-abc",
                query="Analyze customer churn patterns",
                connector_id="conn-123",
                custom_tool_id="tool-789",
                agent_accuracy="quick|basic|standard|maximum"
            )
            print(f"Agent response: {response.agent_tool_response}")
            ```
        """
        return self.chat_to_answer(
            project_id=project_id,
            chat_session_id=chat_session_id,
            query=query,
            connector_id=connector_id,
            custom_tool_id=custom_tool_id,
            use_agent=True,
            agent_accuracy=agent_accuracy,
            **kwargs
        )
    
    def execution_cache_lookup(
        self,
        project_id: str,
        user_query: str,
        connector_id: str,
        max_age_days: int = 30,
        similarity_threshold: float = 0.65,
        limit: int = 50,
        top_n: int = 5,
        only_positive_feedback: bool = False
    ) -> ExecutionCacheLookupResponse:
        """Find recent similar SQL executions to potentially reuse results.
        
        This method searches for previously executed SQL queries that are semantically
        similar to the user's query, allowing you to potentially reuse cached results
        instead of re-executing the same or similar queries.
        
        Args:
            project_id: The project ID
            user_query: The natural language query to find similar executions for
            connector_id: The connector ID to filter executions by
            max_age_days: Maximum age of executions to consider (default: 30 days)
            similarity_threshold: Minimum similarity score (0.0-1.0, default: 0.65)
            limit: Maximum number of candidates to check (default: 50)
            top_n: Number of top matches to return (default: 5)
            only_positive_feedback: If True, only return executions with positive feedback
        
        Returns:
            ExecutionCacheLookupResponse with cache hit status and matching executions
            
        Example:
            ```python
            # Look for similar executions
            result = client.chat.execution_cache_lookup(
                project_id="proj-123",
                user_query="How many active users do we have?",
                connector_id="conn-456",
                similarity_threshold=0.7,
                top_n=3,
                only_positive_feedback=True
            )
            
            if result.cache_hit:
                print(f"Found {len(result.matches)} similar executions!")
                for match in result.matches:
                    print(f"Similarity: {match.similarity_score:.2f}")
                    print(f"SQL: {match.execution.get('sql_query')}")
                    print(f"Results: {match.execution.get('result')}")
                    if match.has_feedback:
                        print(f"Feedback: {'👍' if match.feedback_is_positive else '👎'}")
            else:
                print("No similar executions found in cache")
            ```
        """
        # Basic validation
        if not user_query or not user_query.strip():
            raise ValidationError("User query cannot be empty")
        
        if not connector_id or not connector_id.strip():
            raise ValidationError("Connector ID cannot be empty")
        
        # Build the request
        request = ExecutionCacheLookupRequest(
            user_query=user_query,
            connector_id=connector_id,
            max_age_days=max_age_days,
            similarity_threshold=similarity_threshold,
            limit=limit,
            top_n=top_n,
            only_positive_feedback=only_positive_feedback
        )
        
        response = self._client.post(
            f"/projects/{project_id}/execution-cache-lookup",
            data=request.model_dump()
        )
        return ExecutionCacheLookupResponse(**response)
