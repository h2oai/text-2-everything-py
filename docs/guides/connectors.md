---
title: Connectors
---

Manage database connectors used to execute SQL.

Create/list/get/update/delete:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

# Create in a project
project_id = client.projects.create(name="Demo").id
conn = client.connectors.create(
    project_id=project_id,
    name="Production DB",
    db_type="postgres",
    host="db.example.com",
    port=5432,
    username="app_user",
    password="secure_password",
    database="production",
)

# List / get in project
connectors = client.connectors.list(project_id)
one = client.connectors.get(project_id, conn.id)

# Update
updated = client.connectors.update(project_id, conn.id, port=5433, description="Updated")

# Delete
client.connectors.delete(project_id, conn.id)
```

Test connection (basic):
```python
ok = client.connectors.test_connection(project_id, conn.id)
```

Test connection (detailed):
```python
details = client.connectors.test_connection_detailed(conn.id)
# {'ok': True, 'elapsed_ms': 123}
```

Filter by type:
```python
pg = client.connectors.list_by_type(project_id, "postgres")
```

Snowflake connector example:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

snowflake_conn = client.connectors.create(
    name="Snowflake - Analytics",
    db_type="snowflake",
    host="<account>.<region>.snowflakecomputing.com",
    username="USER",
    password="PASSWORD",
    database="DB",
    config={
        "warehouse": "COMPUTE_WH",
        "role": "ANALYST",
        "schema": "PUBLIC",
    },
)

# Optional: test the connection
ok = client.connectors.test_connection(snowflake_conn.id)
details = client.connectors.test_connection_detailed(snowflake_conn.id)
```
