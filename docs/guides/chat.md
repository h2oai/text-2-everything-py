---
title: Chat
---

Turn natural language into SQL, or generate and execute (Chat to Answer).

Generate SQL:
```python
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many active users?",
    h2ogpte_session_id=session.id,
    contexts_limit=5,
    examples_limit=3,
)
print(resp.sql_query)
```

Generate and execute (requires a Connector):
```python
answer = client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="Top 10 customers by revenue",
    h2ogpte_session_id=session.id,
    connector_id=connector.id,
    use_agent=True,
    agent_accuracy="high",
)
if answer.execution_result:
    print(answer.execution_result.result)
```

Agent helper:
```python
answer = client.chat.chat_with_agent(
    project_id="proj-123",
    chat_session_id=session.id,
    query="Analyze churn",
    h2ogpte_session_id=session.id,
    connector_id=connector.id,
    custom_tool_id=tool.id,
    agent_accuracy="high",
)
```
