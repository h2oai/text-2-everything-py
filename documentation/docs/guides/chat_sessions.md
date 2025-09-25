---
title: Chat Sessions
---

Create and manage chat sessions.

Create/list/delete:
```python
session = client.chat_sessions.create(project_id=project.id, name="Analysis")
sessions = client.chat_sessions.list(project.id, limit=20)
client.chat_sessions.delete(project.id, session.id)
```

Attach/detach a custom tool:
```python
# Attach
session = client.chat_sessions.update_custom_tool(project.id, session.id, custom_tool_id="tool-123")
# Detach
session = client.chat_sessions.update_custom_tool(project.id, session.id, custom_tool_id=None)
```

Get suggested questions:
```python
qs = client.chat_sessions.get_questions(project.id, session.id)
```


