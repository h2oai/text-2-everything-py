---
title: Migrations
---

### 0.1.3

- Renamed parameter `h2ogpte_session_id` to `chat_session_id` across Chat and Executions.
- Refactored Chat methods to require `chat_session_id`.
- Cleaned up deprecated parameters and improved consistency.

Update your calls:

```python
# Before
client.chat.chat_to_sql(project_id=pid, h2ogpte_session_id=sid, query="...")

# After
client.chat.chat_to_sql(project_id=pid, chat_session_id=sid, query="...")
```


