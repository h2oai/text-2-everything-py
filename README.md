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
    api_key="your-api-key"
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
export TEXT2EVERYTHING_API_KEY="your-api-key"
```

```python
import os
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_BASE_URL"),
    api_key=os.getenv("TEXT2EVERYTHING_API_KEY")
)
```

### .env File Support

For local development, create a `.env` file in your project root:

```bash
# .env file
T2E_BASE_URL=https://your-api-endpoint.com
T2E_API_KEY=your-api-key
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
    api_key="your-api-key",
    timeout=60,  # Request timeout in seconds
    max_retries=5,  # Maximum retry attempts
    retry_delay=2.0  # Initial retry delay in seconds
)
```

## Context Manager

Use the client as a context manager for proper resource cleanup:

```python
with Text2EverythingClient(base_url="...", api_key="...") as client:
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

## Integration with Existing H2O Drive SDK

The new SDK is designed to work alongside the existing H2O Drive integration with efficient bulk operations:

```python
# Use existing H2O Drive functionality
from sdk.src import H2ODriveManager, H2ODataValidator

# Use new unified SDK
from text2everything_sdk import Text2EverythingClient

# Combine both for complete workflow
drive_manager = H2ODriveManager(bucket)
validator = H2ODataValidator()
client = Text2EverythingClient(base_url="...", api_key="...")

# Load data from H2O Drive
project_data = await drive_manager.load_project_data_from_drive("project_name")

# Validate data
validation_results = validator.validate_all_data(project_data)

# Create project
project = client.projects.create(name="My Project")

# Use bulk operations for efficient data upload
try:
    # Bulk create contexts
    contexts_data = [
        {
            "name": ctx["name"],
            "content": ctx["content"],
            "description": ctx.get("description"),
            "is_always_displayed": ctx.get("is_always_displayed", False)
        }
        for ctx in validation_results['valid_data']['contexts']
    ]
    if contexts_data:
        contexts = client.contexts.bulk_create(project.id, contexts_data)
        print(f"Created {len(contexts)} contexts")

    # Bulk create schema metadata with validation
    schema_data = [
        {
            "name": schema["name"],
            "schema_data": schema["data"],
            "description": schema.get("description"),
            "is_always_displayed": schema.get("is_always_displayed", False)
        }
        for schema in validation_results['valid_data']['schemas']
    ]
    if schema_data:
        schemas = client.schema_metadata.bulk_create(
            project.id, 
            schema_data, 
            validate=True  # Enable nested field validation
        )
        print(f"Created {len(schemas)} schema metadata items")

    # Bulk create golden examples
    examples_data = [
        {
            "user_query": example["user_query"],
            "sql_query": example["sql_query"],
            "description": example.get("description"),
            "is_always_displayed": example.get("is_always_displayed", False)
        }
        for example in validation_results['valid_data']['golden_examples']
    ]
    if examples_data:
        examples = client.golden_examples.bulk_create(project.id, examples_data)
        print(f"Created {len(examples)} golden examples")

except ValidationError as e:
    print(f"Validation error during bulk upload: {e}")
    # Handle validation errors - could retry with individual creates
except Exception as e:
    print(f"Error during bulk upload: {e}")

print(f"Project '{project.name}' setup complete with bulk operations!")
```

### Benefits of Bulk Operations

- **Performance**: Significantly faster than individual API calls
- **Efficiency**: Reduces network overhead and API rate limiting
- **Validation**: Built-in validation for schema metadata with detailed error reporting
- **Error Handling**: Graceful handling of bulk operation failures
- **Scalability**: Better suited for large datasets from H2O Drive

### Alternative: Mixed Approach for Error Recovery

```python
# If bulk operations fail, fall back to individual creates with error handling
def create_with_fallback(client, project_id, data_list, resource_name):
    """Create items with bulk operation and individual fallback."""
    try:
        # Try bulk operation first
        if resource_name == "contexts":
            return client.contexts.bulk_create(project_id, data_list)
        elif resource_name == "schema_metadata":
            return client.schema_metadata.bulk_create(project_id, data_list)
        elif resource_name == "golden_examples":
            return client.golden_examples.bulk_create(project_id, data_list)
    except Exception as bulk_error:
        print(f"Bulk {resource_name} creation failed: {bulk_error}")
        print("Falling back to individual creation...")
        
        # Fall back to individual creates
        created_items = []
        for i, item_data in enumerate(data_list):
            try:
                if resource_name == "contexts":
                    item = client.contexts.create(project_id=project_id, **item_data)
                elif resource_name == "schema_metadata":
                    item = client.schema_metadata.create(project_id=project_id, **item_data)
                elif resource_name == "golden_examples":
                    item = client.golden_examples.create(project_id=project_id, **item_data)
                created_items.append(item)
            except Exception as item_error:
                print(f"Failed to create {resource_name} item {i}: {item_error}")
        
        return created_items

# Usage with fallback
contexts = create_with_fallback(client, project.id, contexts_data, "contexts")
schemas = create_with_fallback(client, project.id, schema_data, "schema_metadata")
examples = create_with_fallback(client, project.id, examples_data, "golden_examples")
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

## Development

### Running Tests

```bash
pip install text2everything-sdk[dev]

# Run all tests
python run_tests.py

# Or use pytest directly
pytest
```

### Environment Setup for Testing

1. Create a `.env` file in the SDK directory:
```bash
T2E_BASE_URL=https://your-test-api-endpoint.com
T2E_API_KEY=your-test-api-key
```

2. Run the test suite:
```bash
cd text2everything_sdk
python run_tests.py
```

### Code Formatting

```bash
black text2everything_sdk/
isort text2everything_sdk/
```

### Type Checking

```bash
mypy text2everything_sdk/
```

## Documentation

### Serve docs locally

```bash
make docs
```

Then open http://127.0.0.1:8000

### Build static site

```bash
make docs-build
```

Notes:
- The Makefile uses `.venv` and installs from `requirements-dev.txt` automatically.
- If needed, activate manually: `source .venv/bin/activate`.

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

- **Documentation**: [https://docs.text2everything.com](https://docs.text2everything.com)
- **Issues**: [GitHub Issues](https://github.com/h2oai/text-2-everything/issues)
- **Email**: support@text2everything.com

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
