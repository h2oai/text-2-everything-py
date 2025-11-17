# 5-minute quick start

Generate SQL from natural language using the Text2Everything SDK. This guide walks through the minimal steps: install, configure, define a small schema, add context, create a chat session, and produce a query.

## Before you begin

* Python 3.9 or later
* Text2Everything API endpoint and access token

## Install

```bash
pip install h2o-text-2-everything
```

## Configure

Set environment variables (use your real endpoint, token, and workspace):

```bash
export TEXT2EVERYTHING_URL="https://your-api.com"
export T2E_ACCESS_TOKEN="your-access-token"
export T2E_WORKSPACE_NAME="workspaces/your-workspace"
```

## Example

```python
from text2everything_sdk import Text2EverythingClient

# Initialize client
client = Text2EverythingClient(
    base_url="https://your-api.com",
    access_token="your-token",
    workspace_name="workspaces/prod"
)

# Create a project
project = client.projects.create(
    name="quick_start_project",
    description="Quick start demo"
)

# Add a table schema
client.schema_metadata.create(
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

# Add business context
client.contexts.create(
    project_id=project.id,
    name="business_rules",
    content="Customers are registered users."
)

# Create a chat session
session = client.chat_sessions.create(
    project_id=project.id,
    name="initial_session"
)

# Generate SQL from a natural language question
response = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many customers do we have?"
)

print("SQL:", response.sql_query)
print("Explanation:", response.explanation)
```

## Summary

1. Created a project to group related assets.
2. Added a schema so the system understands table structure.
3. Added context to supply business meaning.
4. Generated SQL from a natural language question.

## Sample output

```text
SQL: SELECT COUNT(*) FROM customers;
Explanation: Counts total customer records.
```

## Optional: execute SQL

If you have a database connector configured:

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

## Explore more

* [Complete example](complete-example.md): Full workflow
* [Core guides](../guides/projects.md): Feature details
* [Quick reference](quick-reference.md): Common operations

## Try more queries

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

### Authentication errors
Confirm environment variables:
```python
import os
print(os.getenv('TEXT2EVERYTHING_URL'))
print(os.getenv('T2E_ACCESS_TOKEN'))
```

### Schema validation errors
Ensure schema contains table and columns:
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

## Next steps

* [Complete example](complete-example.md): Build a production-style flow
* [Schema metadata guide](../guides/schema_metadata.md): Advanced schema definition
* [Chat guide](../guides/chat.md): Improve SQL generation
* [Executions guide](../guides/executions.md): Execute and cache queries

For a full walkthrough, see the complete example.
