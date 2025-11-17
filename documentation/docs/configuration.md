---
title: Configuration
---

Env vars:

```bash
export TEXT2EVERYTHING_BASE_URL="https://your-api-endpoint.com" 
export T2E_ACCESS_TOKEN="your-access-token"
export T2E_WORKSPACE_NAME="workspaces/your-workspace"
```
Note: On a regular install you shouldn't need to provide a BASE URL

Using env vars:
```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),
    access_token=os.getenv("T2E_ACCESS_TOKEN"),
    workspace_name=os.getenv("T2E_WORKSPACE_NAME")
)
```

Advanced:
```python
client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev",
    timeout=60,
    max_retries=5,
    retry_delay=2.0,
)
```

Context manager:
```python
from text2everything_sdk import Text2EverythingClient

with Text2EverythingClient(base_url="...", access_token="...", workspace_name="workspaces/dev") as client:
    projects = client.projects.list()
```
