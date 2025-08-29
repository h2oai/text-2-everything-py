---
title: Configuration
---

Env vars:
```bash
export TEXT2EVERYTHING_BASE_URL="https://your-api-endpoint.com"
export TEXT2EVERYTHING_API_KEY="your-api-key"
```

Using env vars:
```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),
    api_key=os.getenv("TEXT2EVERYTHING_API_KEY"),
)
```

Advanced:
```python
client = Text2EverythingClient(
    base_url="https://...",
    api_key="...",
    timeout=60,
    max_retries=5,
    retry_delay=2.0,
)
```

Context manager:
```python
from text2everything_sdk import Text2EverythingClient

with Text2EverythingClient(base_url="...", api_key="...") as client:
    projects = client.projects.list()
```
