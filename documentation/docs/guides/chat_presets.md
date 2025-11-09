---
title: Chat Presets
---

Manage reusable chat configurations and prompt templates.

Chat Presets allow you to:
- Configure and save chat session settings
- Manage prompt templates for consistent AI behavior
- Activate presets for quick session creation
- Share prompt templates across teams

## Basic Operations

### Create a Chat Preset

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev"
)

# Create with existing prompt template
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

### List Chat Presets

```python
# List all presets
presets = client.chat_presets.list(project_id="proj_123")
for preset in presets:
    status = "✓" if preset.is_active else " "
    print(f"[{status}] {preset.name}")

# Search for specific presets
support_presets = client.chat_presets.list(
    project_id="proj_123",
    search="support"
)

# Pagination
page1 = client.chat_presets.list(
    project_id="proj_123",
    skip=0,
    limit=10
)
```

### Get a Chat Preset

```python
# Get by collection ID
preset = client.chat_presets.get(
    project_id="proj_123",
    collection_id="collection_456"
)

print(f"Preset: {preset.name}")
print(f"Active: {preset.is_active}")
print(f"Collection ID: {preset.h2ogpte_collection_id}")
```

### Update a Chat Preset

```python
# Update preset settings
updated = client.chat_presets.update(
    project_id="proj_123",
    collection_id="collection_456",
    description="Updated description",
    chat_settings={
        "llm": "gpt-4-turbo",
        "include_chat_history": "true"
    }
)
```

### Delete a Chat Preset

```python
result = client.chat_presets.delete(
    project_id="proj_123",
    collection_id="collection_456"
)
print(result["status"])  # "deleted"
```

## Activating Presets

Only one preset can be active per project. Active presets are used for quick session creation.

### Activate a Preset

```python
# Get a preset and activate it
presets = client.chat_presets.list(project_id="proj_123")
if presets:
    active_preset = client.chat_presets.activate(
        project_id="proj_123",
        preset_id=presets[0].id
    )
    print(f"Activated: {active_preset.name}")
```

### Get Active Preset

```python
active = client.chat_presets.get_active(project_id="proj_123")
if active:
    print(f"Active preset: {active.name}")
else:
    print("No active preset")
```

## Prompt Template Management

Prompt templates define the system prompts and behavior for AI assistants.

### Create a Prompt Template

```python
template = client.chat_presets.create_prompt_template(
    project_id="proj_123",
    name="Customer Support Template",
    system_prompt="You are a helpful customer support agent...",
    description="Template for customer support interactions",
    lang="en"
)

template_id = template["id"]
print(f"Created template: {template['name']}")
```

### Share a Prompt Template

```python
# Share with specific users
template = client.chat_presets.create_prompt_template(
    project_id="proj_123",
    name="Shared Template",
    system_prompt="You are an expert assistant...",
    share_with_usernames=["user1@example.com", "user2@example.com"]
)

# Or share with a single user
template = client.chat_presets.create_prompt_template(
    project_id="proj_123",
    name="Shared Template",
    system_prompt="You are an expert assistant...",
    share_with_username="user@example.com"
)
```

### List Prompt Templates

```python
result = client.chat_presets.list_prompt_templates(project_id="proj_123")
for template in result["items"]:
    marker = "⭐" if template["is_builtin"] else "  "
    print(f"{marker} {template['name']}")

# Check for more results
if result["has_next"]:
    next_result = client.chat_presets.list_prompt_templates(
        project_id="proj_123",
        offset=result["next_offset"]
    )

# Search templates
search_result = client.chat_presets.list_prompt_templates(
    project_id="proj_123",
    search="customer"
)
```

### Get a Prompt Template

```python
template = client.chat_presets.get_prompt_template(
    project_id="proj_123",
    template_id="template_456"
)

print(f"Template: {template.name}")
print(f"Prompt: {template.system_prompt}")
print(f"Built-in: {template.is_builtin}")
```

### Update a Prompt Template

```python
updated = client.chat_presets.update_prompt_template(
    project_id="proj_123",
    template_id="template_456",
    name="Updated Template Name",
    system_prompt="Updated prompt content...",
    description="Updated description"
)
```

## Advanced Preset Configuration

### Create Preset with Inline Template

Note: While the API accepts inline template specifications, for functional template creation it's recommended to create the template separately using `create_prompt_template()` and pass the resulting ID to `prompt_template_id`.

```python
# Create template first
template = client.chat_presets.create_prompt_template(
    project_id="proj_123",
    name="Custom Template",
    system_prompt="You are an expert assistant...",
    description="Custom template for advanced queries"
)

# Then create preset with template ID
preset = client.chat_presets.create(
    project_id="proj_123",
    name="Advanced Preset",
    collection_name="advanced_collection",
    prompt_template_id=template["id"],
    chat_settings={
        "llm": "gpt-4-turbo",
        "include_chat_history": "auto"
    }
)
```

### Preset with Connector

```python
# Create preset linked to a database connector
preset = client.chat_presets.create(
    project_id="proj_123",
    name="Data Analysis Preset",
    collection_name="analysis_collection",
    connector_id="connector_789",
    prompt_template_id="template_456",
    chat_settings={
        "llm": "gpt-4",
        "include_chat_history": "true"
    }
)
```

### Preset with Custom API System Prompt

```python
preset = client.chat_presets.create(
    project_id="proj_123",
    name="API-Optimized Preset",
    collection_name="api_collection",
    api_system_prompt="Custom system prompt for API interactions...",
    chat_settings={
        "llm": "gpt-4",
        "include_chat_history": "auto"
    }
)
```

## Preset Configuration Options

Get available options for configuring presets:

```python
options = client.chat_presets.get_preset_options(project_id="proj_123")

print(f"Available LLMs: {options['llm_names']}")
print(f"Available tools: {len(options['agent_tools'])}")
print(f"Templates: {len(options['prompt_templates'])}")

# Options include:
# - llm_names: Available language models
# - vision_llm_names: Vision-capable models
# - agent_tools: Available agent tools
# - prompt_templates: Available templates
# - include_chat_history_options: Chat history settings
# - rag_type_options: RAG configuration options
# - agent_accuracy_options: Agent accuracy levels
```

## Integration with Chat Sessions

Use presets when creating chat sessions:

```python
# Create session from specific preset
session = client.chat_sessions.create_from_preset(
    project_id="proj_123",
    preset_id="preset_456",
    name="Customer Support Session"
)

# Create session from active preset
session = client.chat_sessions.create_from_active_preset(
    project_id="proj_123"
)

print(f"Session created: {session.id}")
```

## Best Practices

1. **Template Organization**
   - Create templates for different use cases (support, analysis, general)
   - Use descriptive names and descriptions
   - Share templates with team members when appropriate

2. **Preset Management**
   - Keep one preset active for quick access
   - Use meaningful collection names
   - Document preset purposes in descriptions

3. **Chat Settings**
   - Choose appropriate LLM for your use case
   - Configure chat history based on context needs
   - Test settings before wide deployment

4. **Connector Integration**
   - Link presets to appropriate database connectors
   - Ensure connector permissions are properly configured
   - Test connections before activating presets

## Common Patterns

### Multi-Environment Setup

```python
# Development preset
dev_preset = client.chat_presets.create(
    project_id="proj_123",
    name="Development Preset",
    collection_name="dev_collection",
    prompt_template_id="template_dev",
    connector_id="dev_connector",
    chat_settings={"llm": "gpt-3.5-turbo"}
)

# Production preset
prod_preset = client.chat_presets.create(
    project_id="proj_123",
    name="Production Preset",
    collection_name="prod_collection",
    prompt_template_id="template_prod",
    connector_id="prod_connector",
    chat_settings={"llm": "gpt-4"}
)

# Activate production
client.chat_presets.activate(project_id="proj_123", preset_id=prod_preset.id)
```

### Template Library

```python
# Create a library of templates for different scenarios
templates = {
    "support": {
        "name": "Customer Support",
        "prompt": "You are a friendly customer support agent..."
    },
    "technical": {
        "name": "Technical Expert",
        "prompt": "You are a technical expert specializing in..."
    },
    "sales": {
        "name": "Sales Assistant",
        "prompt": "You are a knowledgeable sales assistant..."
    }
}

template_ids = {}
for key, config in templates.items():
    template = client.chat_presets.create_prompt_template(
        project_id="proj_123",
        name=config["name"],
        system_prompt=config["prompt"],
        description=f"Template for {key} scenarios"
    )
    template_ids[key] = template["id"]

# Create presets for each template
for key, template_id in template_ids.items():
    client.chat_presets.create(
        project_id="proj_123",
        name=f"{key.title()} Preset",
        collection_name=f"{key}_collection",
        prompt_template_id=template_id
    )
```
