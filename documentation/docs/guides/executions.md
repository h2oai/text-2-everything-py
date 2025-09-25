---
title: Executions
---

Execute SQL directly or from chat messages using a Connector.

Execute from chat message:
```python
result = client.executions.execute_from_chat(
    connector_id=connector.id,
    chat_message_id="msg-123",
)
print(result.result)
```

Execute a raw SQL query:
```python
result = client.executions.execute_query(
    connector_id=connector.id,
    sql_query="SELECT COUNT(*) FROM users",
)
print(result.result)
```


