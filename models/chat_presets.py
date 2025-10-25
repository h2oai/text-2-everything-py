"""
Chat Presets models for the Text2Everything SDK.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatSettings(BaseModel):
    """Chat settings configuration for a preset."""
    llm: Optional[str] = None
    llm_args: Optional[Dict[str, Any]] = None
    rag_config: Optional[Dict[str, Any]] = None
    include_chat_history: Optional[str] = None
    tags: Optional[List[str]] = None


class PromptTemplateSpec(BaseModel):
    """Prompt template specification."""
    name: str
    description: Optional[str] = None
    lang: Optional[str] = Field(default="en")
    system_prompt: str


class ChatPresetCreate(BaseModel):
    """Schema for creating a new chat preset."""
    name: str
    description: Optional[str] = None
    collection_name: str
    collection_description: Optional[str] = None
    make_public: bool = True
    chat_settings: Optional[ChatSettings] = None
    prompt_template: Optional[PromptTemplateSpec] = None
    prompt_template_id: Optional[str] = None
    share_prompt_with_username: Optional[str] = None
    share_prompt_with_usernames: Optional[List[str]] = None
    connector_id: Optional[str] = None
    workspace_id: Optional[str] = None
    t2e_url: Optional[str] = None
    api_system_prompt: Optional[str] = None


class ChatPresetUpdate(BaseModel):
    """Schema for updating an existing chat preset."""
    name: Optional[str] = None
    description: Optional[str] = None
    collection_name: Optional[str] = None
    collection_description: Optional[str] = None
    make_public: Optional[bool] = None
    chat_settings: Optional[ChatSettings] = None
    prompt_template_id: Optional[str] = None
    prompt_template: Optional[PromptTemplateSpec] = None
    share_prompt_with_username: Optional[str] = None
    share_prompt_with_usernames: Optional[List[str]] = None
    connector_id: Optional[str] = None
    workspace_id: Optional[str] = None
    t2e_url: Optional[str] = None
    api_system_prompt: Optional[str] = None


class ChatPresetResponse(BaseModel):
    """Response model for chat preset operations."""
    collection_id: str
    collection_name: Optional[str] = None
    prompt_template_id: Optional[str] = None
    prompt_template_name: Optional[str] = None


class ChatPreset(BaseModel):
    """Full chat preset model."""
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    h2ogpte_collection_id: str
    prompt_template_id: Optional[str] = None
    connector_id: Optional[str] = None
    chat_settings: Optional[Dict[str, Any]] = None
    is_public: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: Optional[bool] = None
    t2e_base_url: Optional[str] = None
    api_system_prompt: Optional[str] = None


class PromptTemplateCreate(BaseModel):
    """Schema for creating a prompt template."""
    name: str
    description: Optional[str] = None
    lang: Optional[str] = Field(default="en")
    system_prompt: str
    share_with_username: Optional[str] = None
    share_with_usernames: Optional[List[str]] = None


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template."""
    id: str
    name: str
    description: Optional[str] = None
    lang: Optional[str] = Field(default="en")
    system_prompt: Optional[str] = None


class PromptTemplate(BaseModel):
    """Prompt template model."""
    id: str
    name: str
    description: Optional[str] = None
    lang: Optional[str] = None
    system_prompt: Optional[str] = None
    is_builtin: Optional[bool] = None
