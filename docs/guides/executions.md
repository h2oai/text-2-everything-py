---
title: Executions
---

Execute SQL directly or from chat messages using a Connector.

## Execute SQL

Execute from chat message:
```python
result = client.executions.execute_from_chat(
    project_id=project.id,
    connector_id=connector.id,
    chat_message_id="msg-123",
)
print(result.result)
```

Execute a raw SQL query:
```python
result = client.executions.execute_query(
    project_id=project.id,
    connector_id=connector.id,
    sql_query="SELECT COUNT(*) FROM users",
)
print(result.result)
```

Execute SQL with full control:
```python
result = client.executions.execute_sql(
    project_id=project.id,
    connector_id=connector.id,
    sql_query="SELECT * FROM customers WHERE active = true LIMIT 100",
    chat_session_id=session.id  # Optional context
)
print(f"Execution time: {result.execution_time_ms}ms")
print(f"Results: {result.result}")
```

## List Executions

List all executions:
```python
executions = client.executions.list(project_id=project.id)

for execution in executions:
    print(f"ID: {execution.id}")
    print(f"SQL: {execution.sql_query}")
    print(f"Time: {execution.execution_time_ms}ms")
    print(f"Success: {execution.is_successful}")
```

List with filters:
```python
# Filter by connector
executions = client.executions.list(
    project_id=project.id,
    connector_id=connector.id
)

# Search and paginate
executions = client.executions.list(
    project_id=project.id,
    q="SELECT",      # Search term
    skip=0,          # Skip first N items
    limit=50         # Max items to return
)

# Filter by chat message
executions = client.executions.list(
    project_id=project.id,
    chat_message_id="msg-123"
)
```

## Get Single Execution

Retrieve details for a specific execution:
```python
execution = client.executions.get(
    project_id=project.id,
    execution_id="exec-123"
)
print(f"Query: {execution.sql_query}")
print(f"Time: {execution.execution_time_ms}ms")
print(f"Result: {execution.result}")
```
