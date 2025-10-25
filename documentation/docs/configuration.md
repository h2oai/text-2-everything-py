---
title: Configuration
---

This guide helps you configure the Text2Everything SDK using environment variables or direct parameters.

## Environment variables
Define your API endpoint and credentials as environment variables so they can be reused safely across shells and scripts.
```bash
export TEXT2EVERYTHING_BASE_URL="https://your-api-endpoint.com"
export TEXT2EVERYTHING_API_KEY="your-api-key"
```

## Basic client initialization (env vars)
Create a client by reading values from the environment variables defined above.
```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),
    access_token=os.getenv("T2E_ACCESS_TOKEN"),
    workspace_name=os.getenv("T2E_WORKSPACE_NAME"),
)
```

## Advanced options
Tune timeouts and retries to match your network conditions and request profiles.
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

## Context manager usage
Use the client as a context manager to ensure connections are closed and resources cleaned up automatically.
```python
from text2everything_sdk import Text2EverythingClient

with Text2EverythingClient(base_url="...", access_token="...", workspace_name="workspaces/dev") as client:
    projects = client.projects.list()
```