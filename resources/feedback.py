"""
Feedback resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from ..models.feedback import (
    Feedback,
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse
)
from ..exceptions import ValidationError
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import Text2EverythingClient


class FeedbackResource(BaseResource):
    """Resource for managing feedback on chat messages and SQL executions."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        chat_message_id: str,
        feedback: str,
        is_positive: bool,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> FeedbackResponse:
        """Create feedback for a chat message or execution.
        
        Args:
            project_id: The project ID
            chat_message_id: The chat message ID
            feedback: The feedback text
            is_positive: Whether the feedback is positive
            execution_id: Optional execution ID
            **kwargs: Additional feedback fields
        
        Returns:
            The created feedback with response details
            
        Example:
            ```python
            result = client.feedback.create(
                project_id=project_id,
                chat_message_id="msg-123",
                feedback="The SQL query worked perfectly!",
                is_positive=True,
                execution_id="exec-456"
            )
            ```
        """
        # Basic validation
        if not chat_message_id or not chat_message_id.strip():
            raise ValidationError("Chat message ID cannot be empty")
        
        if not feedback or not feedback.strip():
            raise ValidationError("Feedback text cannot be empty")
        
        # Build the FeedbackCreate object internally
        feedback_data = FeedbackCreate(
            chat_message_id=chat_message_id,
            feedback=feedback,
            is_positive=is_positive,
            execution_id=execution_id,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/feedback",
            data=feedback_data.model_dump()
        )
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return FeedbackResponse(**response_data)
    
    def get(self, project_id: str, feedback_id: str) -> FeedbackResponse:
        """Get feedback by ID.
        
        Args:
            project_id: The project ID
            feedback_id: The feedback ID
            
        Returns:
            The feedback details
            
        Example:
            ```python
            feedback = client.feedback.get(project_id, feedback_id)
            print(f"Feedback: {feedback.feedback}")
            print(f"Positive: {feedback.is_positive}")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/feedback/{feedback_id}")
        # Handle both list and single object responses
        if isinstance(response, list):
            if response:
                response_data = response[0]  # Take first item from list
            else:
                raise ValidationError("API returned empty list")
        else:
            response_data = response
        
        return FeedbackResponse(**response_data)
    
    def list(self, project_id: str, limit: int = 100, offset: int = 0) -> List[FeedbackResponse]:
        """List feedback for a project.
        
        Args:
            project_id: The project ID
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of feedback items
            
        Example:
            ```python
            feedback_list = client.feedback.list(project_id)
            for feedback in feedback_list:
                status = "👍" if feedback.is_positive else "👎"
                print(f"{status} {feedback.feedback}")
            ```
        """
        endpoint = f"/projects/{project_id}/feedback"
        params = {"limit": limit, "offset": offset}
        return self._paginate(endpoint, params=params, model_class=FeedbackResponse)
    
    def update(
        self,
        project_id: str,
        feedback_id: str,
        chat_message_id: Optional[str] = None,
        feedback: Optional[str] = None,
        is_positive: Optional[bool] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> FeedbackResponse:
        """Update feedback.
        
        Args:
            project_id: The project ID
            feedback_id: The feedback ID to update
            chat_message_id: New chat message ID
            feedback: New feedback text
            is_positive: New positive/negative setting
            execution_id: New execution ID
            **kwargs: Additional fields to update
            
        Returns:
            The updated feedback
            
        Example:
            ```python
            result = client.feedback.update(
                project_id=project_id,
                feedback_id=feedback_id,
                feedback="Updated: The query was excellent!",
                is_positive=True
            )
            ```
        """
        # Get current feedback first since API expects complete data
        current_feedback = self.get(project_id, feedback_id)
        
        # Use current values as defaults, override with provided values
        update_data = FeedbackCreate(
            chat_message_id=chat_message_id if chat_message_id is not None else current_feedback.chat_message_id,
            feedback=feedback if feedback is not None else current_feedback.feedback,
            is_positive=is_positive if is_positive is not None else current_feedback.is_positive,
            execution_id=execution_id if execution_id is not None else current_feedback.execution_id,
            **kwargs
        )
        
        response = self._client.put(
            f"/projects/{project_id}/feedback/{feedback_id}",
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
        
        return FeedbackResponse(**response_data)
    
    def delete(self, project_id: str, feedback_id: str) -> bool:
        """Delete feedback.
        
        Args:
            project_id: The project ID
            feedback_id: The feedback ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.feedback.delete(project_id, feedback_id)
            ```
        """
        self._client.delete(f"/projects/{project_id}/feedback/{feedback_id}")
        return True
    
    def create_positive(self, project_id: str, chat_message_id: str, 
                       feedback_text: str, execution_id: str = None) -> FeedbackResponse:
        """Create positive feedback for a chat message.
        
        Args:
            project_id: The project ID
            chat_message_id: The chat message ID
            feedback_text: The feedback text
            execution_id: Optional execution ID
            
        Returns:
            The created positive feedback
            
        Example:
            ```python
            feedback = client.feedback.create_positive(
                project_id="proj-123",
                chat_message_id="msg-456",
                feedback_text="Perfect SQL query!",
                execution_id="exec-789"
            )
            ```
        """
        return self.create(
            project_id=project_id,
            chat_message_id=chat_message_id,
            feedback=feedback_text,
            is_positive=True,
            execution_id=execution_id
        )
    
    def create_negative(self, project_id: str, chat_message_id: str, 
                       feedback: str, execution_id: str = None) -> FeedbackResponse:
        """Create negative feedback for a chat message.
        
        Args:
            project_id: The project ID
            chat_message_id: The chat message ID
            feedback_text: The feedback text
            execution_id: Optional execution ID
            
        Returns:
            The created negative feedback
            
        Example:
            ```python
            feedback = client.feedback.create_negative(
                project_id="proj-123",
                chat_message_id="msg-456",
                feedback_text="Query returned incorrect results",
                execution_id="exec-789"
            )
            ```
        """
        return self.create(
            project_id=project_id,
            chat_message_id=chat_message_id,
            feedback=feedback,
            is_positive=False,
            execution_id=execution_id
        )
    
    def list_positive(self, project_id: str) -> List[FeedbackResponse]:
        """List all positive feedback for a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of positive feedback items
            
        Example:
            ```python
            positive_feedback = client.feedback.list_positive(project_id)
            print(f"Found {len(positive_feedback)} positive feedback items")
            ```
        """
        all_feedback = self.list(project_id)
        return [fb for fb in all_feedback if fb.is_positive]
    
    def list_negative(self, project_id: str) -> List[FeedbackResponse]:
        """List all negative feedback for a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of negative feedback items
            
        Example:
            ```python
            negative_feedback = client.feedback.list_negative(project_id)
            print(f"Found {len(negative_feedback)} negative feedback items")
            ```
        """
        all_feedback = self.list(project_id)
        return [fb for fb in all_feedback if not fb.is_positive]
    
    def get_feedback_for_message(self, project_id: str, chat_message_id: str) -> List[FeedbackResponse]:
        """Get all feedback for a specific chat message.
        
        Args:
            project_id: The project ID
            chat_message_id: The chat message ID
            
        Returns:
            List of feedback for the message
            
        Example:
            ```python
            message_feedback = client.feedback.get_feedback_for_message(
                project_id, "msg-123"
            )
            for feedback in message_feedback:
                print(f"Feedback: {feedback.feedback}")
            ```
        """
        all_feedback = self.list(project_id)
        return [fb for fb in all_feedback if fb.chat_message_id == chat_message_id]
