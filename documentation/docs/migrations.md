---
title: Migrations
---

### 0.1.3

- Version 0.1.3 renames the parameter `h2ogpte_session_id` to `chat_session_id` across Chat and Executions.
- Chat methods now require `chat_session_id`.
- This version removes deprecated parameters and improves consistency.

Update your calls:

```python
# Before
client.chat.chat_to_sql(project_id=pid, h2ogpte_session_id=sid, query="...")

# After
client.chat.chat_to_sql(project_id=pid, chat_session_id=sid, query="...")
```


