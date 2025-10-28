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

## Bulk Operations

The SDK provides efficient bulk delete operations for managing multiple resources at once:

### Bulk Delete Contexts
```python
# Delete multiple contexts in one operation
context_ids = ["id1", "id2", "id3"]
result = client.contexts.bulk_delete(project_id="project_id", context_ids=context_ids)

print(f"Deleted: {result['deleted_count']}")
print(f"Failed: {result.get('failed_ids', [])}")
```

### Bulk Delete Schema Metadata
```python
# Bulk delete schemas (automatically handles split groups)
schema_ids = ["schema1", "schema2", "schema3"]
result = client.schema_metadata.bulk_delete(project_id="project_id", schema_ids=schema_ids)

# Returns structured response with success/failure details
print(f"Successfully deleted {result['deleted_count']} schemas")
```

### Bulk Delete Golden Examples
```python
# Delete multiple examples at once
example_ids = ["ex1", "ex2", "ex3"]
result = client.golden_examples.bulk_delete(project_id="project_id", example_ids=example_ids)
```

### Bulk Delete Feedback
```python
# Clean up multiple feedback items
feedback_ids = ["fb1", "fb2", "fb3"]
result = client.feedback.bulk_delete(project_id="project_id", feedback_ids=feedback_ids)
```

## Chat Presets

Chat presets allow you to create reusable chat configurations with predefined settings, connectors, and prompt templates:

### Creating and Managing Presets
```python
# Create a basic chat preset with existing template
preset = client.chat_presets.create(
    project_id="project_id",
    name="Production Analytics",
    collection_name="analytics_collection",
    description="Preset for production data analysis",
    prompt_template_id="template_id",
    connector_id="connector_id",
    chat_settings={
        "llm": "gpt-4",
        "include_chat_history": "auto"
    }
)

# NOTE: Inline template creation - API limitation
# The prompt_template parameter is accepted for API parity but not currently processed.
# To use a custom template, create it first then reference by ID:
template = client.chat_presets.create_prompt_template(
    project_id="project_id",
    name="Custom Analytics Template",
    system_prompt="You are an expert data analyst specializing in...",
    description="Template for advanced analytics queries"
)

preset = client.chat_presets.create(
    project_id="project_id",
    name="Advanced Analytics",
    collection_name="advanced_collection",
    prompt_template_id=template["id"],  # Use the created template ID
    connector_id="connector_id",
    workspace_id="workspace_123"
)

# Create preset with sharing and workspace settings
preset = client.chat_presets.create(
    project_id="project_id",
    name="Shared Team Preset",
    collection_name="team_collection",
    prompt_template={
        "name": "Team Template",
        "system_prompt": "You are a helpful assistant for the team..."
    },
    share_prompt_with_usernames=["user1@example.com", "user2@example.com"],
    workspace_id="workspace_123",
    t2e_url="https://custom-t2e.example.com"
)

# List all presets
presets = client.chat_presets.list(project_id="project_id")

# Search for specific presets
support_presets = client.chat_presets.list(
    project_id="project_id",
    search="support"
)

# Get specific preset by collection ID
preset = client.chat_presets.get(
    project_id="project_id",
    collection_id="collection_id"
)

# Update preset
updated = client.chat_presets.update(
    project_id="project_id",
    collection_id="collection_id",
    name="Updated Analytics Preset",
    description="Updated description",
    chat_settings={
        "llm": "gpt-4-turbo",
        "include_chat_history": "true"
    }
)

# Delete preset
client.chat_presets.delete(
    project_id="project_id",
    collection_id="collection_id"
)
```

### Managing Prompt Templates
```python
# Add prompt template to preset
template = client.chat_presets.add_prompt_template(
    project_id="project_id",
    preset_id="preset_id",
    template_name="Analysis Template",
    template_content="Analyze the following data: {query}"
)

# List templates for a preset
templates = client.chat_presets.list_prompt_templates(
    project_id="project_id",
    preset_id="preset_id"
)

# Delete template
client.chat_presets.delete_prompt_template(
    project_id="project_id",
    preset_id="preset_id",
    template_id="template_id"
)
```

### Using Presets in Chat Sessions
```python
# Activate a preset for use
client.chat_presets.activate(project_id="project_id", preset_id="preset_id")

# Get currently active preset
active = client.chat_presets.get_active(project_id="project_id")

# Create chat session from preset
session = client.chat_sessions.create_from_preset(
    project_id="project_id",
    preset_id="preset_id"
)

# Or use the active preset
session = client.chat_sessions.create_from_active_preset(project_id="project_id")
```

## Advanced Features

### Project Collections

Access and manage H2OGPTE collections for your project resources:

```python
# List all collections for a project
collections = client.projects.list_collections(project_id="project_id")

for collection in collections:
    print(f"{collection.component_type}: {collection.h2ogpte_collection_id}")

# Get collection by type
contexts_collection = client.projects.get_collection_by_type(
    project_id="project_id",
    component_type="contexts"
)
```

### Execution Cache Lookup

Query the execution cache to find similar past queries for performance optimization:

```python
# Look up cached executions for a query
cache_result = client.chat.execution_cache_lookup(
    project_id="project_id",
    user_query="Show me top 10 customers",
    connector_id="connector_id",
    similarity_threshold=0.8,  # 0.0 to 1.0
    top_n=5,  # Return top 5 matches
    only_positive_feedback=True  # Only include positively rated executions
)

# Check if we got a cache hit
if cache_result.cache_hit:
    print(f"Found {len(cache_result.matches)} similar executions")
    for match in cache_result.matches:
        print(f"Similarity: {match.similarity_score}")
        print(f"SQL: {match.execution.sql_query}")
        print(f"Results: {match.execution.results}")
```

### Schema Splitting for Large Tables

Tables with more than 8 columns are automatically split into multiple parts. The `create()` method returns:
- Single `SchemaMetadataResponse` for small schemas (≤8 columns)
- `List[SchemaMetadataResponse]` for large schemas (>8 columns)

```python
result = client.schema_metadata.create(
    project_id="project_id",
    name="My Table",
    schema_data=my_schema_data
)

# Always check the return type
if isinstance(result, list):
    print(f"Schema split into {len(result)} parts")
    # All parts share the same split_group_id
else:
    print(f"Created single schema: {result.id}")
```

**📖 For complete documentation on working with split schemas**, see:
- [`docs/guides/schema_metadata.md`](docs/guides/schema_metadata.md) - Basic split handling
- [`docs/how-to/bulk_operations.md`](docs/how-to/bulk_operations.md) - Bulk operations with splits

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

### v0.1.7 (Current)
- **100% API Parity Achieved**: Complete coverage of all Text2Everything API endpoints
- **Bulk Delete Operations**: Added bulk delete support for contexts, schema metadata, golden examples, and feedback
- **Chat Presets**: Full CRUD operations for chat presets with prompt templates and active preset management
- **Project Collections**: List and retrieve project collections by type
- **Execution Cache Lookup**: Query execution cache for performance optimization
- **Schema Split Groups**: Automatic handling of large table schemas (>8 columns)
- **Custom Tools Support**: Full CRUD operations for custom Python tools
- **Directory-based Tool Creation**: Upload entire directories as custom tools
- **Multipart File Upload**: Native support for file uploads with proper Content-Type handling
- **Enhanced Validation**: Comprehensive nested field validation for schema metadata
- **Environment Configuration**: Added .env file support for local development
- **Improved Testing**: Enhanced test suite with automatic environment loading
- **Bug Fixes**: Resolved Content-Type header conflicts in multipart requests

### v0.1.0
- Initial release
- Complete API coverage for all Text2Everything endpoints
- Type-safe Pydantic models
- Comprehensive error handling
- Automatic pagination and retry logic
- Context manager support
- Integration with existing H2O Drive SDK
