---
title: Jupyter Usage
---

Use the SDK from notebooks. Start from the quick start guides or adapt the cells below.

Minimal cell:
```python
from text2everything_sdk import Text2EverythingClient
client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")
project = client.projects.create(name="Notebook Demo")
session = client.chat_sessions.create(project_id=project.id)
resp = client.chat.chat_to_sql(project_id=project.id, chat_session_id=session.id, query="Count users")
resp.sql_query
```

See also:
- Quickstart
- Guides → Chat Sessions, Chat
- How To → Bulk Operations, Validation
