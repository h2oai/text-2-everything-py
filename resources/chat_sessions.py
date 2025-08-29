"""
Chat sessions resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from ..models.chat_sessions import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionUpdateRequest,
    ChatSessionQuestion
)
from ..models.custom_tools import CustomTool
from ..exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class ChatSessionsResource(BaseResource):
    """Resource for managing H2OGPTE chat sessions."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        name: Optional[str] = None,
        custom_tool_id: Optional[str] = None,
        **kwargs
    ) -> ChatSessionResponse:
        """Create a new H2OGPTE chat session.
        
        Args:
            project_id: The project ID
            name: Optional name for the session
            custom_tool_id: Optional custom tool to associate
            **kwargs: Additional session fields
        
        Returns:
            The created chat session
            
        Example:
            ```python
            result = client.chat_sessions.create(
                project_id=project_id,
                name="Data Analysis Session",
                custom_tool_id="tool-123"
            )
            print(f"Session created: {result.id}")
            ```
        """
        # Build the ChatSessionCreate object internally
        session = ChatSessionCreate(
            name=name,
            custom_tool_id=custom_tool_id,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/chat-sessions",
            data=session.model_dump()
        )
        return ChatSessionResponse(**response)
    
    # TODO: The get chat session API endpoint is not working properly
    # def get(self, project_id: str, session_id: str) -> ChatSessionResponse:
    #     """Get a specific H2OGPTE chat session.
    #     
    #     Args:
    #         project_id: The project ID
    #         session_id: The chat session ID
    #         
    #     Returns:
    #         The chat session details
    #         
    #     Example:
    #         ```python
    #         session = client.chat_sessions.get(project_id, session_id)
    #         print(f"Session: {session.name}")
    #         print(f"Created: {session.created_at}")
    #         ```
    #     """
    #     response = self._client.get(f"/projects/{project_id}/chat-sessions/{session_id}")
    #     return ChatSessionResponse(**response)
    
    def list(self, project_id: str, offset: int = 0, limit: int = 10) -> List[ChatSessionResponse]:
        """List recent H2OGPTE chat sessions for a project.
        
        Args:
            project_id: The project ID
            offset: Number of sessions to skip
            limit: Maximum number of sessions to return
            
        Returns:
            List of chat sessions
            
        Example:
            ```python
            sessions = client.chat_sessions.list(project_id, limit=20)
            for session in sessions:
                print(f"{session.name}: {session.id}")
            ```
        """
        endpoint = f"/projects/{project_id}/chat-sessions"
        params = {"offset": offset, "limit": limit}
        response = self._client.get(endpoint, params=params)
        return [ChatSessionResponse(**item) for item in response]
    
    def update_custom_tool(self, project_id: str, session_id: str, 
                          custom_tool_id: str = None) -> ChatSessionResponse:
        """Update the custom tool associated with a chat session.
        
        Args:
            project_id: The project ID
            session_id: The chat session ID
            custom_tool_id: The custom tool ID to associate (None to detach)
            
        Returns:
            The updated chat session
            
        Example:
            ```python
            # Attach a custom tool
            session = client.chat_sessions.update_custom_tool(
                project_id, session_id, "tool-456"
            )
            
            # Detach custom tool
            session = client.chat_sessions.update_custom_tool(
                project_id, session_id, None
            )
            ```
        """
        update_request = ChatSessionUpdateRequest(custom_tool_id=custom_tool_id)
        response = self._client.put(
            f"/projects/{project_id}/chat-sessions/{session_id}/custom-tool",
            data=update_request.model_dump()
        )
        return ChatSessionResponse(**response)
    
    def get_custom_tool(self, project_id: str, session_id: str) -> Optional[CustomTool]:
        """Get the custom tool associated with a chat session.
        
        Args:
            project_id: The project ID
            session_id: The chat session ID
            
        Returns:
            The associated custom tool, or None if no tool is associated
            
        Example:
            ```python
            tool = client.chat_sessions.get_custom_tool(project_id, session_id)
            if tool:
                print(f"Associated tool: {tool.name}")
            else:
                print("No custom tool associated")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/chat-sessions/{session_id}/custom-tool")
        return CustomTool(**response) if response else None
    
    def get_questions(self, project_id: str, session_id: str, 
                     limit: int = 10) -> List[ChatSessionQuestion]:
        """Get suggested questions for a chat session.
        
        Args:
            project_id: The project ID
            session_id: The chat session ID
            limit: Maximum number of questions to return
            
        Returns:
            List of suggested questions
            
        Example:
            ```python
            questions = client.chat_sessions.get_questions(project_id, session_id)
            for question in questions:
                print(f"Suggested: {question.question}")
            ```
        """
        endpoint = f"/projects/{project_id}/chat-sessions/{session_id}/questions"
        params = {"limit": limit}
        response = self._client.get(endpoint, params=params)
        return [ChatSessionQuestion(**item) for item in response]
    
    def delete(self, project_id: str, session_id: str) -> bool:
        """Delete a H2OGPTE chat session.
        
        Args:
            project_id: The project ID
            session_id: The chat session ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.chat_sessions.delete(project_id, session_id)
            ```
        """
        self._client.delete(f"/projects/{project_id}/chat-sessions/{session_id}")
        return True
    
    def create_with_tool(self, project_id: str, name: str = None, 
                        custom_tool_id: str = None) -> ChatSessionResponse:
        """Create a new chat session with an optional custom tool.
        
        Args:
            project_id: The project ID
            name: Optional name for the session
            custom_tool_id: Optional custom tool to associate
            
        Returns:
            The created chat session
            
        Example:
            ```python
            session = client.chat_sessions.create_with_tool(
                project_id="proj-123",
                name="Analysis Session",
                custom_tool_id="tool-456"
            )
            ```
        """
        return self.create(
            project_id=project_id,
            name=name,
            custom_tool_id=custom_tool_id
        )
