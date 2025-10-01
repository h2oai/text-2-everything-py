---
title: Connectors
---

Manage database connectors used to execute SQL.

Create/list/get/update/delete:
```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

# Create
conn = client.connectors.create(
    name="Production DB",
    db_type="postgres",
    host="db.example.com",
    port=5432,
    username="app_user",
    password="secure_password",
    database="production",
)

# List / get
connectors = client.connectors.list()
one = client.connectors.get(conn.id)

# Update
updated = client.connectors.update(conn.id, port=5433, description="Updated")

# Delete
client.connectors.delete(conn.id)
```

Test connection (basic):
```python
ok = client.connectors.test_connection(conn.id)
```

Filter by type:
```python
pg = client.connectors.list_by_type("postgres")
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
```
