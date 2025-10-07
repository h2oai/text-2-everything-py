---
title: Troubleshooting & Error Handling
---

### Common Exceptions

- AuthenticationError (401): Ensure `Authorization: Bearer <access_token>` is set and, if required, `X-Workspace-Name` matches your workspace scope.
- ValidationError (400): Inspect `response_data` for field errors.
- NotFoundError (404): Verify IDs (`project_id`, `connector_id`, etc.).
- RateLimitError (429): Respect `retry_after`; reduce concurrency.
- TimeoutError: Increase `read_timeout` or simplify the request.
- ServerError (5xx): Retry later; capture context for support.

### Remedies

```python
from text2everything_sdk import AuthenticationError, ValidationError, RateLimitError

try:
    ...
except RateLimitError as e:
    delay = e.retry_after or 2
    time.sleep(delay)
except ValidationError as e:
    print(e.response_data)
```

### Chat/Executions gotchas

- `chat_session_id` is required for chat methods.
- Executions: provide exactly one of `chat_message_id` or `sql_query`.
- Connectors: ensure credentials and network access to target DB.


