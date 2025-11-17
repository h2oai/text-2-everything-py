# Configuration

This page explains how to configure the SDK using environment variables and optional client parameters.

## Environment variables

Set these variables before running your code:

```bash
export T2E_ACCESS_TOKEN="your-access-token"
export T2E_WORKSPACE_NAME="workspaces/your-workspace"
export TEXT2EVERYTHING_BASE_URL="https://your-api-endpoint.com"  # Optional; omit to use default
```

Summary:

| Variable | Required | Purpose | Default |
| -------- | -------- | ------- | ------- |
| T2E_ACCESS_TOKEN | Yes | Authenticates API requests | None (must set) |
| T2E_WORKSPACE_NAME | Yes | Selects workspace scope | None (must set) |
| TEXT2EVERYTHING_BASE_URL | No | Overrides base API endpoint | Built-in default |

If `TEXT2EVERYTHING_BASE_URL` is not set, the client uses the default endpoint.

## Basic usage

```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),  # May be None; default applied internally
    access_token=os.getenv("T2E_ACCESS_TOKEN"),
    workspace_name=os.getenv("T2E_WORKSPACE_NAME"),
)
```

You can provide values directly (discouraged for secrets):

```python
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    access_token="your-token",
    workspace_name="workspaces/dev",
)
```

## Advanced options

Optional tuning parameters:

| Parameter | Type | Purpose |
| --------- | ---- | ------- |
| timeout | int | Per-request timeout (seconds) |
| max_retries | int | Retry attempts for transient failures |
| retry_delay | float | Delay between retries (seconds) |

Example:

```python
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    access_token="your-token",
    workspace_name="workspaces/dev",
    timeout=60,
    max_retries=5,
    retry_delay=2.0,
)
```

## Context manager usage

Use a context manager to ensure resources (like HTTP sessions) are released:

```python
from text2everything_sdk import Text2EverythingClient

with Text2EverythingClient(base_url="https://your-api-endpoint.com", access_token="your-token", workspace_name="workspaces/dev") as client:
    for project in client.projects.list():
        print(project.name)
```

## Next steps

Proceed to the quick start or advanced integration guides after configuration.
