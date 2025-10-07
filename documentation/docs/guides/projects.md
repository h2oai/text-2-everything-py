---
title: Projects
---

Manage top-level containers for your resources.

Common tasks:

List/get/create/update/delete:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

# List
projects = client.projects.list()

# Create
project = client.projects.create(name="My Project", description="Demo")

# Get
project = client.projects.get(project.id)

# Update
project = client.projects.update(project.id, name="Updated Name")

# Delete
client.projects.delete(project.id)
```

Pagination:
```python
page1 = client.projects.list(page=1, per_page=10)
page2 = client.projects.list(page=2, per_page=10)
```

Helpers:
```python
# By name
maybe = client.projects.get_by_name("My Project")
exists = client.projects.exists(project.id)
```


