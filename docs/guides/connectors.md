---
title: Connectors
---

Manage database connectors used to execute SQL.

## Create/List/Get/Update/Delete

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

# Create
conn = client.connectors.create(
    project_id=project.id,
    name="Production DB",
    db_type="postgres",
    host="db.example.com",
    port=5432,
    username="app_user",
    password="secure_password",
    database="production",
)

# List / get
connectors = client.connectors.list(project_id=project.id)
one = client.connectors.get(project_id=project.id, connector_id=conn.id)

# Update
updated = client.connectors.update(
    project_id=project.id,
    connector_id=conn.id,
    port=5433,
    description="Updated"
)

# Delete
client.connectors.delete(
    project_id=project.id,
    connector_id=conn.id,
    delete_secrets=True  # Optional: also delete secrets from Secure Store
)
```

## Test Connection

Test connection (basic):
```python
ok = client.connectors.test_connection(
    project_id=project.id,
    connector_id=conn.id
)
```

Test connection (detailed):
```python
details = client.connectors.test_connection_detailed(
    project_id=project.id,
    connector_id=conn.id
)
# {'ok': True, 'elapsed_ms': 123}
```

## Filter by Type

```python
pg = client.connectors.list_by_type(
    project_id=project.id,
    db_type="postgres"
)
```

## Snowflake Connector Example

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(base_url="https://...", access_token="...", workspace_name="workspaces/dev")

snowflake_conn = client.connectors.create(
    project_id=project.id,
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
ok = client.connectors.test_connection(
    project_id=project.id,
    connector_id=snowflake_conn.id
)
details = client.connectors.test_connection_detailed(
    project_id=project.id,
    connector_id=snowflake_conn.id
)
```
