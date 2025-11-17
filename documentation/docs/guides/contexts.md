---
title: Contexts
---

Contexts provide business rules, definitions, and domain knowledge that improve SQL generation quality. They contain information about data semantics, business logic, and guidelines that help the system generate more accurate queries.

## Basic Operations
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")
project = client.projects.create(name="Ctx Demo")

# Create
ctx = client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="Active customers have status = 'active'",
    is_always_displayed=True,
)

# List
contexts = client.contexts.list(project_id=project.id)

# Get
ctx = client.contexts.get(project.id, ctx.id)

# Update
ctx = client.contexts.update(project.id, ctx.id, content="Updated rules...")

# Delete
client.contexts.delete(project.id, ctx.id)
```

## Bulk Operations
```python
items = [
  {"name": "Rule 1", "content": "..."},
  {"name": "Rule 2", "content": "..."},
]
created = client.contexts.bulk_create(project.id, items)
```

## Helper Methods
```python
always = client.contexts.list_always_displayed(project.id)
by_name = client.contexts.get_by_name(project.id, "Business Rules")
```
