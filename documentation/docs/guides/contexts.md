---
title: Contexts
---

Provide business/domain knowledge to improve SQL generation.

List/create/get/update/delete:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", api_key="...")
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

Bulk create:
```python
items = [
  {"name": "Rule 1", "content": "..."},
  {"name": "Rule 2", "content": "..."},
]
created = client.contexts.bulk_create(project.id, items)
```

Helpers:
```python
always = client.contexts.list_always_displayed(project.id)
by_name = client.contexts.get_by_name(project.id, "Business Rules")
```


