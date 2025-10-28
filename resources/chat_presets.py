"""
Chat Presets resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from text2everything_sdk.models.chat_presets import (
    ChatPreset,
    ChatPresetCreate,
    ChatPresetUpdate,
    ChatPresetResponse,
    PromptTemplate,
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateSpec,
    ChatSettings
)
from text2everything_sdk.exceptions import ValidationError
from text2everything_sdk.resources.base import BaseResource

if TYPE_CHECKING:
    from text2everything_sdk.client import Text2EverythingClient


class ChatPresetsResource(BaseResource):
    """Resource for managing chat presets and reusable chat configurations."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(
        self,
        project_id: str,
        name: str,
        collection_name: str,
        description: Optional[str] = None,
        collection_description: Optional[str] = None,
        make_public: bool = True,
        chat_settings: Optional[Dict[str, Any]] = None,
        prompt_template_id: Optional[str] = None,
        prompt_template: Optional[Dict[str, Any]] = None,
        share_prompt_with_username: Optional[str] = None,
        share_prompt_with_usernames: Optional[List[str]] = None,
        connector_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        t2e_url: Optional[str] = None,
        api_system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatPresetResponse:
        """Create a new chat preset.
        
        Args:
            project_id: The project ID
            name: Name of the chat preset
            collection_name: Name for the H2OGPTE collection
            description: Optional description of the preset
            collection_description: Optional description for the collection
            make_public: Whether the preset is public (default: True)
            chat_settings: Optional chat configuration settings
            prompt_template_id: Optional existing prompt template ID
            prompt_template: Optional inline prompt template specification with keys:
                - name: Template name
                - system_prompt: The system prompt content
                - description: Optional description
                - lang: Optional language code (default: "en")
                NOTE: Currently accepted for API parity but not processed by the API.
                For functional template creation, create the template separately using
                create_prompt_template() and pass the resulting ID to prompt_template_id.
            share_prompt_with_username: Optional single username to share prompt with
            share_prompt_with_usernames: Optional list of usernames to share prompt with
            connector_id: Optional connector ID for data access
            workspace_id: Optional workspace ID
            t2e_url: Optional Text2Everything base URL
            api_system_prompt: Optional system prompt for API interactions
            **kwargs: Additional preset fields
        
        Returns:
            The created chat preset response
            
        Examples:
            Basic preset with existing template:
            ```python
            preset = client.chat_presets.create(
                project_id="proj_123",
                name="Customer Support Preset",
                collection_name="support_collection",
                description="Preset for customer support chats",
                make_public=True,
                prompt_template_id="template_456",
                chat_settings={
                    "llm": "gpt-4",
                    "include_chat_history": "auto"
                }
            )
            print(f"Created preset with collection: {preset.collection_id}")
            ```
            
            Preset with inline template creation and sharing:
            ```python
            preset = client.chat_presets.create(
                project_id="proj_123",
                name="Advanced Preset",
                collection_name="advanced_collection",
                prompt_template={
                    "name": "Custom Template",
                    "system_prompt": "You are an expert assistant...",
                    "description": "Custom template for advanced queries",
                    "lang": "en"
                },
                share_prompt_with_usernames=["user1@example.com", "user2@example.com"],
                workspace_id="workspace_123"
            )
            ```
        """
        # Basic validation
        if not name or not name.strip():
            raise ValidationError("Preset name cannot be empty")
        
        if not collection_name or not collection_name.strip():
            raise ValidationError("Collection name cannot be empty")
        
        # Build ChatPresetCreate object
        preset_data = ChatPresetCreate(
            name=name,
            description=description,
            collection_name=collection_name,
            collection_description=collection_description,
            make_public=make_public,
            chat_settings=ChatSettings(**chat_settings) if chat_settings and isinstance(chat_settings, dict) else chat_settings,
            prompt_template_id=prompt_template_id,
            prompt_template=PromptTemplateSpec(**prompt_template) if prompt_template and isinstance(prompt_template, dict) else None,
            share_prompt_with_username=share_prompt_with_username,
            share_prompt_with_usernames=share_prompt_with_usernames,
            connector_id=connector_id,
            workspace_id=workspace_id,
            t2e_url=t2e_url,
            api_system_prompt=api_system_prompt,
            **kwargs
        )
        
        response = self._client.post(
            f"/projects/{project_id}/chat-presets",
            data=preset_data.model_dump(exclude_none=True)
        )
        return ChatPresetResponse(**response)
    
    def get(self, project_id: str, collection_id: str) -> ChatPreset:
        """Get a chat preset by its collection ID.
        
        Note: The API uses collection_id as the identifier for presets.
        
        Args:
            project_id: The project ID
            collection_id: The H2OGPTE collection ID
            
        Returns:
            The chat preset details
            
        Example:
            ```python
            preset = client.chat_presets.get(project_id, collection_id)
            print(f"Preset: {preset.name}")
            print(f"Active: {preset.is_active}")
            ```
        """
        # List all presets and find the one with matching collection_id
        all_presets = self.list(project_id)
        for preset in all_presets:
            if preset.h2ogpte_collection_id == collection_id:
                return preset
        
        raise ValidationError(f"Chat preset with collection_id '{collection_id}' not found")
    
    def list(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[ChatPreset]:
        """List all chat presets for a project.
        
        Args:
            project_id: The project ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search query to filter by name
            
        Returns:
            List of chat presets
            
        Example:
            ```python
            presets = client.chat_presets.list(project_id)
            for preset in presets:
                status = "✓" if preset.is_active else " "
                print(f"[{status}] {preset.name}")
            
            # Search for specific presets
            support_presets = client.chat_presets.list(
                project_id,
                search="support"
            )
            ```
        """
        params = {"skip": skip, "limit": limit}
        if search:
            params["q"] = search
        
        endpoint = f"/projects/{project_id}/chat-presets"
        response = self._client.get(endpoint, params=params)
        
        # API returns list directly
        if isinstance(response, list):
            return [ChatPreset(**item) for item in response]
        return []
    
    def update(
        self,
        project_id: str,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        collection_name: Optional[str] = None,
        collection_description: Optional[str] = None,
        make_public: Optional[bool] = None,
        chat_settings: Optional[Dict[str, Any]] = None,
        prompt_template_id: Optional[str] = None,
        prompt_template: Optional[Dict[str, Any]] = None,
        share_prompt_with_username: Optional[str] = None,
        share_prompt_with_usernames: Optional[List[str]] = None,
        connector_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        t2e_url: Optional[str] = None,
        api_system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatPresetResponse:
        """Update an existing chat preset.
        
        Args:
            project_id: The project ID
            collection_id: The H2OGPTE collection ID
            name: New preset name
            description: New description
            collection_name: New collection name
            collection_description: New collection description
            make_public: New public setting
            chat_settings: New chat settings
            prompt_template_id: New prompt template ID
            prompt_template: Optional inline prompt template specification with keys:
                - name: Template name
                - system_prompt: The system prompt content
                - description: Optional description
                - lang: Optional language code (default: "en")
            share_prompt_with_username: Optional single username to share prompt with
            share_prompt_with_usernames: Optional list of usernames to share prompt with
            connector_id: New connector ID
            workspace_id: New workspace ID
            t2e_url: New Text2Everything base URL
            api_system_prompt: New API system prompt
            **kwargs: Additional fields to update
            
        Returns:
            The updated chat preset response
            
        Example:
            ```python
            preset = client.chat_presets.update(
                project_id,
                collection_id,
                description="Updated description",
                chat_settings={
                    "llm": "gpt-4-turbo",
                    "include_chat_history": "true"
                }
            )
            ```
        """
        # Build update data
        update_data = ChatPresetUpdate(
            name=name,
            description=description,
            collection_name=collection_name,
            collection_description=collection_description,
            make_public=make_public,
            chat_settings=ChatSettings(**chat_settings) if chat_settings and isinstance(chat_settings, dict) else chat_settings,
            prompt_template_id=prompt_template_id,
            prompt_template=PromptTemplateSpec(**prompt_template) if prompt_template and isinstance(prompt_template, dict) else None,
            share_prompt_with_username=share_prompt_with_username,
            share_prompt_with_usernames=share_prompt_with_usernames,
            connector_id=connector_id,
            workspace_id=workspace_id,
            t2e_url=t2e_url,
            api_system_prompt=api_system_prompt,
            **kwargs
        )
        
        response = self._client.put(
            f"/projects/{project_id}/chat-presets/{collection_id}",
            data=update_data.model_dump(exclude_none=True)
        )
        return ChatPresetResponse(**response)
    
    def delete(self, project_id: str, collection_id: str) -> Dict[str, str]:
        """Delete a chat preset.
        
        Args:
            project_id: The project ID
            collection_id: The H2OGPTE collection ID to delete
            
        Returns:
            Deletion confirmation with status
            
        Example:
            ```python
            result = client.chat_presets.delete(project_id, collection_id)
            print(result["status"])  # "deleted"
            ```
        """
        response = self._client.delete(
            f"/projects/{project_id}/chat-presets/{collection_id}"
        )
        return response if isinstance(response, dict) else {"status": "deleted"}
    
    def activate(self, project_id: str, preset_id: str) -> ChatPreset:
        """Activate a chat preset for the project.
        
        Only one preset can be active per project.
        
        Args:
            project_id: The project ID
            preset_id: The preset ID (not collection_id) to activate
            
        Returns:
            The activated chat preset
            
        Example:
            ```python
            # Get a preset and activate it
            presets = client.chat_presets.list(project_id)
            if presets:
                active_preset = client.chat_presets.activate(
                    project_id,
                    presets[0].id
                )
                print(f"Activated: {active_preset.name}")
            ```
        """
        response = self._client.post(
            f"/projects/{project_id}/chat-presets/{preset_id}/activate"
        )
        return ChatPreset(**response)
    
    def get_active(self, project_id: str) -> Optional[ChatPreset]:
        """Get the currently active chat preset for a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            The active preset, or None if no preset is active
            
        Example:
            ```python
            active = client.chat_presets.get_active(project_id)
            if active:
                print(f"Active preset: {active.name}")
            else:
                print("No active preset")
            ```
        """
        all_presets = self.list(project_id)
        for preset in all_presets:
            if preset.is_active:
                return preset
        return None
    
    def create_prompt_template(
        self,
        project_id: str,
        name: str,
        system_prompt: str,
        description: Optional[str] = None,
        lang: str = "en",
        share_with_username: Optional[str] = None,
        share_with_usernames: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Create a new prompt template.
        
        Args:
            project_id: The project ID
            name: Template name
            system_prompt: The system prompt content
            description: Optional description
            lang: Language code (default: "en")
            share_with_username: Optional username to share with
            share_with_usernames: Optional list of usernames to share with
            
        Returns:
            Dict with template id and name
            
        Example:
            ```python
            template = client.chat_presets.create_prompt_template(
                project_id,
                name="Customer Support Template",
                system_prompt="You are a helpful customer support agent...",
                description="Template for customer support interactions"
            )
            template_id = template["id"]
            ```
        """
        if not system_prompt or not system_prompt.strip():
            raise ValidationError("System prompt cannot be empty")
        
        template_data = PromptTemplateCreate(
            name=name,
            system_prompt=system_prompt,
            description=description,
            lang=lang,
            share_with_username=share_with_username,
            share_with_usernames=share_with_usernames
        )
        
        response = self._client.post(
            f"/projects/{project_id}/chat-presets/prompt-templates",
            data=template_data.model_dump(exclude_none=True)
        )
        return response
    
    def get_prompt_template(
        self,
        project_id: str,
        template_id: str
    ) -> PromptTemplate:
        """Get a prompt template by ID.
        
        Args:
            project_id: The project ID
            template_id: The template ID
            
        Returns:
            The prompt template
            
        Example:
            ```python
            template = client.chat_presets.get_prompt_template(
                project_id,
                template_id
            )
            print(f"Template: {template.name}")
            print(f"Prompt: {template.system_prompt}")
            ```
        """
        response = self._client.get(
            f"/projects/{project_id}/chat-presets/prompt-templates/{template_id}"
        )
        return PromptTemplate(**response)
    
    def list_prompt_templates(
        self,
        project_id: str,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List available prompt templates.
        
        Args:
            project_id: The project ID
            offset: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search query
            
        Returns:
            Dict with items, has_next, and next_offset
            
        Example:
            ```python
            result = client.chat_presets.list_prompt_templates(project_id)
            for template in result["items"]:
                marker = "⭐" if template["is_builtin"] else "  "
                print(f"{marker} {template['name']}")
            ```
        """
        params = {"offset": offset, "limit": limit}
        if search:
            params["q"] = search
        
        response = self._client.get(
            f"/projects/{project_id}/chat-presets/prompt-templates",
            params=params
        )
        return response
    
    def update_prompt_template(
        self,
        project_id: str,
        template_id: str,
        name: str,
        description: Optional[str] = None,
        lang: str = "en",
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """Update a prompt template.
        
        Args:
            project_id: The project ID
            template_id: The template ID
            name: New template name
            description: New description
            lang: Language code
            system_prompt: New system prompt content
            
        Returns:
            Dict with template id and name
            
        Example:
            ```python
            updated = client.chat_presets.update_prompt_template(
                project_id,
                template_id,
                name="Updated Template Name",
                system_prompt="Updated prompt content..."
            )
            ```
        """
        update_data = PromptTemplateUpdate(
            id=template_id,
            name=name,
            description=description,
            lang=lang,
            system_prompt=system_prompt
        )
        
        response = self._client.put(
            f"/projects/{project_id}/chat-presets/prompt-templates/{template_id}",
            data=update_data.model_dump(exclude_none=True)
        )
        return response
    
    def get_preset_options(self, project_id: str) -> Dict[str, Any]:
        """Get available options for configuring chat presets.
        
        Returns configuration options including:
        - Available agent tools
        - Prompt templates  
        - LLM models
        - Vision-capable models
        - Chat history options
        - RAG types
        - And more
        
        Args:
            project_id: The project ID
            
        Returns:
            Dict with all available configuration options
            
        Example:
            ```python
            options = client.chat_presets.get_preset_options(project_id)
            print(f"Available LLMs: {options['llm_names']}")
            print(f"Available tools: {len(options['agent_tools'])}")
            print(f"Templates: {len(options['prompt_templates'])}")
            ```
        """
        response = self._client.get(
            f"/projects/{project_id}/chat-presets/options"
        )
        return response
