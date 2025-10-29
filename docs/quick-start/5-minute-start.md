# 5-Minute Quick Start

Get started with Text2Everything SDK in minutes. This guide shows you the absolute basics to generate SQL from natural language.

## Prerequisites

- Python 3.9 or higher
- Text2Everything API access

## Installation

```bash
pip install h2o-text-2-everything
```

## Configuration

Set up your environment variables:

```bash
export TEXT2EVERYTHING_URL="https://your-api.com"
export T2E_ACCESS_TOKEN="your-access-token"
export T2E_WORKSPACE_NAME="workspaces/your-workspace"
```

## Quick Start Code

```python
from text2everything_sdk import Text2EverythingClient

# 1. Initialize client
client = Text2EverythingClient(
    base_url="https://your-api.com",
    access_token="your-token",
    workspace_name="workspaces/prod"
)

# 2. Create a project
project = client.projects.create(
    name="My First Project",
    description="Learning Text2Everything"
)

# 3. Add a simple table schema
schema = client.schema_metadata.create(
    project_id=project.id,
    name="customers_table",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR(100)"},
                {"name": "email", "type": "VARCHAR(255)"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        }
    }
)

# 4. Add business context
context = client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="Customers are users who have registered for an account."
)

# 5. Create a chat session
session = client.chat_sessions.create(
    project_id=project.id,
    name="First Session"
)

# 6. Generate SQL from natural language!
response = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many customers do we have?"
)

print(f"Generated SQL: {response.sql_query}")
print(f"Explanation: {response.explanation}")
```

## What Just Happened?

1. **Created a project** - Organizes all your data
2. **Defined a schema** - Told the AI about your database structure
3. **Added context** - Gave the AI business knowledge
4. **Generated SQL** - Converted natural language to SQL!

## Sample Output

```
Generated SQL: SELECT COUNT(*) FROM customers;
Explanation: This query counts the total number of customer records in the customers table.
```

## Next Steps

### Execute SQL (Optional)
If you have a database connector:

```python
# Execute the generated SQL
answer = client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many customers do we have?",
    connector_id="your-connector-id"
)

print(f"Answer: {answer.execution_result.result}")
```

### Learn More

- **[Complete Example](complete-example.md)** - See a full realistic example
- **[Core Guides](../guides/projects.md)** - Deep dive into specific features
- **[Quick Reference](quick-reference.md)** - Common commands cheat sheet

### Try Different Queries

```python
# Ask more complex questions
queries = [
    "Show me customers created this month",
    "What's the average age of our customers?",
    "Find customers with email addresses ending in .com"
]

for query in queries:
    response = client.chat.chat_to_sql(
        project_id=project.id,
        chat_session_id=session.id,
        query=query
    )
    print(f"\nQuery: {query}")
    print(f"SQL: {response.sql_query}")
```

## Troubleshooting

### Authentication Error
Check your environment variables are set correctly:
```python
import os
print(os.getenv('TEXT2EVERYTHING_URL'))
print(os.getenv('T2E_ACCESS_TOKEN'))
```

### Schema Validation Error
Ensure your schema follows the required format:
```python
# Table schemas must have 'table' and 'columns'
schema_data = {
    "table": {
        "name": "table_name",
        "columns": [
            {"name": "col1", "type": "TYPE"}
        ]
    }
}
```

## What's Next?

You've learned the basics! Now explore:

1. **[Complete Example](complete-example.md)** - Build a real application
2. **[Schema Metadata Guide](../guides/schema_metadata.md)** - Advanced schema definition
3. **[Chat Guide](../guides/chat.md)** - Fine-tune SQL generation
4. **[Executions Guide](../guides/executions.md)** - Execute and cache queries

**Ready for more?** Check out the [Complete Example](complete-example.md) for a full workflow! 🚀
