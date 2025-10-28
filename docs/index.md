---
title: Text2Everything SDK
---

Welcome to the Text2Everything Python SDK documentation. This SDK provides a comprehensive Python interface for building intelligent text-to-SQL applications with advanced RAG (Retrieval-Augmented Generation) capabilities.

## What is Text2Everything?

Text2Everything transforms natural language into executable SQL queries by combining:

- **Semantic understanding** of your database schema and business context
- **Intelligent retrieval** of relevant examples and documentation  
- **LLM-powered generation** of accurate, optimized SQL
- **Execution caching** to improve performance and reduce costs
- **Feedback loops** that continuously improve query quality

## Core Capabilities

### Data Management
- **Projects**: Organize your applications and isolate data
- **Schema Metadata**: Define tables, dimensions, metrics, and relationships for better SQL generation
- **Contexts**: Provide business rules, definitions, and domain knowledge
- **Golden Examples**: Curate query-SQL pairs to guide the AI
- **Feedback**: Capture user validation to improve results over time

### Query Generation & Execution
- **Chat Sessions**: Maintain conversation context across multiple queries
- **Chat to SQL**: Generate SQL from natural language with RAG-enhanced context
- **Chat to Answer**: Generate and execute SQL in one step
- **SQL Execution**: Execute queries against database connectors
- **Execution Cache**: Reuse results from semantically similar queries

### Operations
- **Database Connectors**: Connect to Snowflake and other databases
- **Chat Presets**: Configure reusable settings and prompt templates
- **Bulk Operations**: Efficiently manage large datasets
- **Validation**: Ensure data quality with schema validation

## Quick Example

```python
from text2everything_sdk import Text2EverythingClient

# Initialize client
client = Text2EverythingClient(
    base_url="https://your-api.com",
    access_token="your-token",
    workspace_name="workspaces/prod"
)

# Generate and execute SQL
answer = client.chat.chat_to_answer(
    project_id="proj-123",
    chat_session_id="session-456",
    query="What are our top 10 customers by revenue?",
    connector_id="snowflake-789"
)

print(f"SQL: {answer.sql_query}")
print(f"Results: {answer.execution_result.result}")
```

## Getting Started

1. **[Installation](installation.md)** - Install the SDK and dependencies
2. **[Quickstart](quickstart.md)** - Build your first text-to-SQL application
3. **[Configuration](configuration.md)** - Set up authentication and environments
4. **[Guides](quick-start/README.md)** - Explore tutorials and quick start guides

## Key Features

- **High Accuracy**: Leverage schema metadata, business context, and examples for precise SQL
- **Performance**: Built-in caching and intelligent retrieval for fast responses
- **Continuous Learning**: Feedback system that improves quality over time
- **Easy Integration**: Simple Python API with comprehensive error handling
- **Production Ready**: Bulk operations, validation, and enterprise features
