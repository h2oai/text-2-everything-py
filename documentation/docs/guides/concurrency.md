---
title: Concurrency & Performance
---

Optimize `Text2EverythingClient` for high-throughput and long-running requests.

### Recommended settings

```python
client = Text2EverythingClient(
    base_url="https://...",
    api_key="...",
    read_timeout=300,
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=300.0,
)
```

### Tips

- Prefer session reuse; avoid recreating the client per request.
- Use `chat_to_sql` for generation-only; `chat_to_answer` when you need execution.
- For heavy result sets, add limits in your SQL to reduce transfer time.
- Monitor 429s and backoff using `retry_after`.

### Long-running tasks

- Increase `read_timeout` appropriately.
- Ensure downstream DB timeouts (e.g., warehouse) are compatible.


