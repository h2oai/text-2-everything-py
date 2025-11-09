---
title: Chat Sessions
---

Create and manage chat sessions for organizing conversations.

## Basic Operations

### Create Session

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev"
)

# Create a chat session
session = client.chat_sessions.create(
    project_id="proj-123",
    name="Customer Analysis"
)

print(f"Session ID: {session.id}")
```

### Get Session

```python
# Retrieve a specific session
session = client.chat_sessions.get(
    project_id="proj-123",
    session_id="session-456"
)

print(f"Session: {session.name}")
```

### List Sessions

```python
# List all sessions
sessions = client.chat_sessions.list(project_id="proj-123")

for session in sessions:
    print(f"Session: {session.name} (ID: {session.id})")

# List with pagination
sessions = client.chat_sessions.list(
    project_id="proj-123",
    skip=0,
    limit=20
)
```

### Update Session

```python
# Update session name
updated = client.chat_sessions.update(
    project_id="proj-123",
    session_id="session-456",
    name="Updated Analysis Session"
)
```

### Delete Session

```python
# Delete a session
success = client.chat_sessions.delete(
    project_id="proj-123",
    session_id="session-456"
)
```

## Common Patterns

### Session-Based Workflow

```python
# 1. Create session
session = client.chat_sessions.create(
    project_id="proj-123",
    name="Sales Analysis"
)

# 2. Use session for queries
response = client.chat.chat_to_sql(
    project_id="proj-123",
    chat_session_id=session.id,
    query="Show me top customers"
)

# 3. Continue conversation in same session
response2 = client.chat.chat_to_sql(
    project_id="proj-123",
    chat_session_id=session.id,
    query="What about their revenue?"
)

# 4. Clean up when done
client.chat_sessions.delete("proj-123", session.id)
```
