---
title: Quickstart
---

This Quickstart gets you from zero to a generated SQL query in ~5 minutes.

Prereqs:
- Have a Text2Everything API endpoint and API key
- Python 3.9+

Install (local dev):
```bash
pip install -e .
```

Minimal setup and first query:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    api_key="your-api-key",
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

# 4) Start a chat session
session = client.chat_sessions.create(project_id=project.id)

# 5) Ask a question to generate SQL
resp = client.chat.chat_to_sql(
    project_id=project.id,
    query="Count active customers",
    h2ogpte_session_id=session.id,
)

print("Generated SQL:", resp.sql_query)
```

Next steps:
- Add golden examples for better quality
- Connect your database and use Chat to Answer (executes SQL)
- See Guides for resource-specific tasks
