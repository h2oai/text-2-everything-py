---
title: Quickstart
---

This Quickstart gets you from zero to a generated SQL query in ~5 minutes.

Prereqs:
- Have a Text2Everything API endpoint and API key
- Python 3.9+

## Installation

```bash
pip install h2o_text_2_everything-0.1.x-py3-none-any.whl
```

## Minimal setup and first query

```python
from text2everything_sdk import Text2EverythingClient

# Simple initialization
client = Text2EverythingClient(
    access_token="your-access-token",
    workspace_name="workspaces/my-workspace",
)

# 1) Create a project
project = client.projects.create(name="Quickstart Project")

# 2) Add minimal context
client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="Active customers have status = 'active'",
    is_always_displayed=True,
)

# 3) Add a minimal table schema
schema = client.schema_metadata.create(
    project_id=project.id,
    name="Customers Table",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR(100)"},
                {"name": "status", "type": "VARCHAR(32)"},
            ]
        }
    },
)

# 4) Add a golden example for better SQL quality
client.golden_examples.create(
    project_id=project.id,
    user_query="How many active customers do we have?",
    sql_query="SELECT COUNT(*) FROM customers WHERE status = 'active';",
    description="Count of active customers",
    is_always_displayed=True,
)

# 5) Start a chat session
session = client.chat_sessions.create(project_id=project.id)

# 6) Ask a question to generate SQL
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="Count active customers",
)

print("Generated SQL:", resp.sql_query)
```

Next steps:
- Add golden examples for better quality
- Connect your database and use Chat to Answer (executes SQL)
- See Guides for resource-specific tasks
