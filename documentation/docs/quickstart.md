---
title: Quickstart
---

This quickstart guide helps you generate your first SQL query using the **Text2Everything** Python SDK.

This page is for developers who want a fast, working example. You will install the SDK, create minimal project data, and ask a question that the SDK converts to SQL.

Estimated time: 5 minutes.

## Prerequisites
- **Python 3.9+:** The SDK targets CPython 3.9 or newer; earlier versions are unsupported.
- **Text2Everything API endpoint and API key:** You need network access to your API deployment and a valid key to authenticate requests.

## Step 1: Install the SDK
Use the prebuilt wheel or see [Installation](./installation.md) for detailed steps.

```bash
pip install text2everything_sdk-0.1.x-py3-none-any.whl
```

## Step 2: Minimal setup and first query
In this step you will create a project, add the smallest useful context and schema, provide one golden example, start a chat session, and ask a question that the SDK converts into SQL.
> **Info:** Replace placeholder values such as `your-api-key` with your actual credentials.

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

The output is a SQL string produced by the service. 

## Next steps
- Improve quality with more [Golden examples](./guides/golden_examples.md)
- Connect a database and use [Chat → Answer](./guides/chat.md)
- Explore resource workflows in [Guides](./guides/projects.md)
- Review client options in [Configuration](./configuration.md) and API details in [Reference](./reference)


