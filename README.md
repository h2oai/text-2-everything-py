# Text2Everything SDK

The official Python SDK for the Text2Everything API, providing easy access to text-to-SQL conversion, project management, and data operations.

## Features

- **Unified Client**: Single entry point for all API operations
- **Type Safety**: Full Pydantic model integration with IDE support
- **Error Handling**: Comprehensive exception hierarchy with detailed error information
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Pagination**: Automatic handling of paginated responses
- **Resource Management**: Organized clients for each API resource type
- **Context Manager**: Proper resource cleanup with context manager support
- **Custom Tools**: Upload and manage custom Python tools with directory-based creation
- **Multipart File Uploads**: Native support for file uploads with proper Content-Type handling
- **Nested Validation**: Comprehensive schema validation with nested field requirements
- **Environment Configuration**: Support for .env files for easy local development setup

## Installation

**Note**: The SDK is not yet published to PyPI. For now, use local installation:

```bash
# Navigate to the SDK directory
cd text2everything_sdk

# Install in development mode
pip install -e .

# Or with optional dependencies
pip install -e ".[dev,integrations]"
```

**For complete installation options**, see [INSTALLATION.md](INSTALLATION.md)

### Future PyPI Installation

Once published, you'll be able to install with:

```bash
pip install text2everything-sdk

# With optional dependencies
pip install text2everything-sdk[integrations]  # pandas, jupyter, h2o-drive
pip install text2everything-sdk[dev]          # development tools
pip install text2everything-sdk[docs]         # documentation tools
```

## Quick Start

```python
from text2everything_sdk import Text2EverythingClient

# Initialize the client
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    access_token="your-access-token",
    workspace_name="workspaces/my-workspace"
)

# Create a project
project = client.projects.create(
    name="My Project",
    description="A sample project for text-to-SQL conversion"
)

# Add context information
context = client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="Important business context and rules...",
    is_always_displayed=True
)

# Add schema metadata
schema = client.schema_metadata.create(
    project_id=project.id,
    name="Customers Table",
    description="Customer information table",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR(100)"},
                {"name": "email", "type": "VARCHAR(255)"}
            ]
        }
    }
)

# Create a chat session
session = client.chat_sessions.create(project_id=project.id)

# Generate SQL for a query
response = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="Show me all customers from California",
)
print(f"Generated SQL: {response.sql_query}")
```

## API Resources

The SDK provides clients for all Text2Everything API resources:

### Projects
```python
# List projects
projects = client.projects.list()

# Get project by ID
project = client.projects.get("project_id")

# Create project
project = client.projects.create(name="New Project")

# Update project
project = client.projects.update("project_id", name="Updated Name")

# Delete project
client.projects.delete("project_id")
```

### Contexts
```python
# Add business context
context = client.contexts.create(
    project_id="project_id",
    name="Business Rules",
    content="Context content...",
    is_always_displayed=True
)

# List contexts for a project
contexts = client.contexts.list(project_id="project_id")
```

### Schema Metadata
```python
# Add table schema
table = client.schema_metadata.create(
    project_id="project_id",
    name="Users Table",
    schema_data={
        "table": {
            "name": "users",
            "columns": [...]
        }
    }
)

# Add dimension
dimension = client.schema_metadata.create(
    project_id="project_id",
    name="User Status",
    schema_data={
        "table": {
            "dimension": {
                "name": "status",
                "content": {...}
            }
        }
    }
)
```

### Golden Examples
```python
# Add example query-SQL pairs
example = client.golden_examples.create(
    project_id="project_id",
    name="High Value Customers",
    user_query="Show me customers with orders over $1000",
    sql_query="SELECT * FROM customers WHERE total_orders > 1000",
    description="Example for high-value customer queries"
)
```

### Chat Sessions and Chat
```python
# Create chat session
session = client.chat_sessions.create(project_id="project_id")

# Convert natural language to SQL
resp = client.chat.chat_to_sql(
    project_id="project_id",
    chat_session_id=session.id,
    query="Your natural language query here",
)

# Or convert and execute
ans = client.chat.chat_to_answer(
    project_id="project_id",
    chat_session_id=session.id,
    query="Top 10 customers by revenue",
    connector_id="your-connector-id"
)
```

### Custom Tools
```python
# Create custom tool from individual files
with open("my_tool.py", "rb") as f:
    tool = client.custom_tools.create(
        name="My Custom Tool",
        description="A custom Python tool for data processing",
        files=[f]
    )

# Create custom tool from directory (uploads all Python files)
tool = client.custom_tools.create_from_directory(
    name="Data Processing Suite",
    description="Complete data processing toolkit",
    directory_path="/path/to/tool/directory"
)

# List custom tools
tools = client.custom_tools.list()

# Get custom tool details
tool = client.custom_tools.get("tool_id")

# Update custom tool
updated_tool = client.custom_tools.update(
    "tool_id",
    name="Updated Tool Name",
    description="Updated description"
)

# Delete custom tool
client.custom_tools.delete("tool_id")
```

### Connectors
```python
# Add database connector
connector = client.connectors.create(
    name="Production DB",
    db_type="postgres",
    host="localhost",
    port=5432,
    username="user",
    password="password",
    database="mydb"
)

# Test connection
result = client.connectors.test_connection(connector.id)
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from text2everything_sdk import (
    Text2EverythingClient,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError
)

try:
    project = client.projects.get("invalid_id")
except NotFoundError as e:
    print(f"Project not found: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.response_data}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after} seconds")
```

## Configuration

### Environment Variables

You can configure the SDK using environment variables:

```bash
export TEXT2EVERYTHING_BASE_URL="https://your-api-endpoint.com"
export T2E_ACCESS_TOKEN="your-oidc-access-token"
export T2E_WORKSPACE_NAME="workspaces/my-workspace"
```

```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),
    access_token=os.getenv("T2E_ACCESS_TOKEN"),
    workspace_name=os.getenv("T2E_WORKSPACE_NAME")
)
```

### .env File Support

For local development, create a `.env` file in your project root:

```bash
# .env file
T2E_BASE_URL=https://your-api-endpoint.com
T2E_ACCESS_TOKEN=your-oidc-access-token
T2E_WORKSPACE_NAME=workspaces/my-workspace
```

The SDK will automatically load these variables when running tests:

```python
# The SDK automatically loads .env files for testing
from text2everything_sdk import Text2EverythingClient

# These will be loaded from .env file automatically
client = Text2EverythingClient()
```

### Advanced Configuration

```python
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    access_token="your-oidc-access-token",
    workspace_name="workspaces/my-workspace",
    timeout=60,  # Request timeout in seconds
    max_retries=5,  # Maximum retry attempts
    retry_delay=2.0  # Initial retry delay in seconds
)
```

## Context Manager

Use the client as a context manager for proper resource cleanup:

```python
with Text2EverythingClient(base_url="...", access_token="...", workspace_name="workspaces/dev") as client:
    projects = client.projects.list()
    # Client will be automatically closed when exiting the context
```

## Pagination

The SDK automatically handles pagination for list operations:

```python
# Get all projects (automatically handles pagination)
all_projects = client.projects.list()

# Manual pagination control
page1_projects = client.projects.list(page=1, per_page=10)
page2_projects = client.projects.list(page=2, per_page=10)
```

## Schema Validation

The SDK includes comprehensive nested field validation for schema metadata:

### Required Nested Fields

Different schema types require specific nested fields:

- **Tables**: `schema_metadata.table` and `schema_metadata.table.columns`
- **Dimensions**: `schema_metadata.table`, `schema_metadata.table.dimension`, and `schema_metadata.table.dimension.content`
- **Metrics**: `schema_metadata.table`, `schema_metadata.table.metric`, and `schema_metadata.table.metric.content`
- **Relationships**: `schema_metadata.relationship`

### Validation Examples

```python
# Valid table schema
table_schema = {
    "table": {
        "name": "customers",
        "columns": [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR(100)"}
        ]
    }
}

# Valid dimension schema
dimension_schema = {
    "table": {
        "name": "customers",
        "dimension": {
            "name": "customer_status",
            "content": {
                "type": "categorical",
                "values": ["active", "inactive", "pending"]
            }
        }
    }
}

# Valid metric schema
metric_schema = {
    "table": {
        "name": "orders",
        "metric": {
            "name": "total_revenue",
            "content": {
                "aggregation": "sum",
                "column": "amount"
            }
        }
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: [https://h2oai.github.io/text-2-everything-py/](https://h2oai.github.io/text-2-everything-py/)
- **Issues**: [GitHub Issues](https://github.com/h2oai/text-2-everything/issues)
- **Email**: support@h2o.ai

## Changelog

### v1.1.0
- **Custom Tools Support**: Added full CRUD operations for custom Python tools
- **Directory-based Tool Creation**: Upload entire directories as custom tools
- **Multipart File Upload**: Native support for file uploads with proper Content-Type handling
- **Enhanced Validation**: Comprehensive nested field validation for schema metadata
- **Environment Configuration**: Added .env file support for local development
- **Improved Testing**: Enhanced test suite with automatic environment loading
- **Bug Fixes**: Resolved Content-Type header conflicts in multipart requests

### v1.0.0
- Initial release
- Complete API coverage for all Text2Everything endpoints
- Type-safe Pydantic models
- Comprehensive error handling
- Automatic pagination and retry logic
- Context manager support
- Integration with existing H2O Drive SDK
