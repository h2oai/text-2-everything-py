---
title: Chat
---

Turn natural language into SQL, or generate and execute (Chat to Answer).

## Basic Usage

Generate SQL:
```python
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many active users?",
    contexts_limit=5,
    examples_limit=3,
)
print(resp.sql_query)
```

Generate and execute (requires a Connector):
```python
answer = client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="Top 10 customers by revenue",
    connector_id=connector.id,
)
if answer.execution_result:
    print(answer.execution_result.result)
```

Agent helper:
```python
answer = client.chat.chat_with_agent(
    project_id="proj-123",
    chat_session_id=session.id,
    query="Analyze churn",
    connector_id=connector.id,
    custom_tool_id=tool.id,
    agent_accuracy="basic", # quick | basic | standard | maximum
)
```

## RAG Retrieval Filtering

Control retrieval quality by filtering documents based on KNN distance. The cutoff parameters use L2 distance in embedding space to filter retrieved documents.

### Understanding Cutoff Values

The cutoff parameters filter by KNN distance (L2 space):

- **`0` (default)**: No filtering - retrieves all documents regardless of similarity
- **Low values** (e.g., `0.00001` - `0.1`): **MORE restrictive** - only retrieves very similar documents (near-exact matches)
- **High values** (e.g., `100+`): **LESS restrictive** - retrieves most documents with minimal filtering
- **Range**: Unbounded (no upper limit), but practical values typically between 0 and 10

**Important**: Lower values mean stricter filtering, higher values mean looser filtering. This is distance-based, not similarity-based.

### Using Cutoff Parameters with chat_to_sql

```python
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="Show me customer analytics",
    contexts_cutoff=0.5,      # Fairly strict context filtering
    schema_cutoff=0.3,        # Very strict schema filtering (closer matches only)
    feedback_cutoff=0.7,      # Moderate feedback filtering
    examples_cutoff=0.4,      # Strict example filtering
)
print(resp.sql_query)
```

### Using Cutoff Parameters with chat_to_answer

```python
answer = client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="Calculate monthly revenue",
    connector_id=connector.id,
    contexts_cutoff=0.3,      # Very strict - only highly relevant contexts
    schema_cutoff=0.2,        # Extremely strict - near-exact schema matches
    feedback_cutoff=0.5,      # Moderate feedback filtering
    examples_cutoff=0.3,      # Very strict example matching
)
if answer.execution_result:
    print(answer.execution_result.result)
```

### Cutoff Parameter Guidelines

Each cutoff independently controls its document type using KNN distance:
- `contexts_cutoff`: Filters context documents by distance
- `schema_cutoff`: Filters schema metadata by distance  
- `feedback_cutoff`: Filters user feedback by distance
- `examples_cutoff`: Filters golden examples by distance

**Recommended Starting Values:**
- **Strict filtering** (high precision): `0.1 - 0.3`
- **Moderate filtering** (balanced): `0.4 - 0.7`
- **Loose filtering** (high recall): `0.8 - 2.0`
- **No filtering**: `0` or omit the parameter

### When to Use Cutoff Parameters

Use cutoff parameters to:
- **Reduce noise**: Set low cutoff values (0.1-0.3) to retrieve only highly relevant documents
- **Improve precision**: Stricter filtering ensures retrieved documents are closely related to the query
- **Handle large datasets**: Filter out less relevant documents when you have many embeddings
- **Balance precision vs recall**: Adjust values based on whether you need exact matches or broader context

### Examples by Use Case

```python
# High precision - only very relevant documents
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="exact column names in users table",
    schema_cutoff=0.1,  # Very strict - only near-exact matches
)

# Balanced approach - moderate filtering
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="show customer information",
    contexts_cutoff=0.5,
    schema_cutoff=0.5,
    examples_cutoff=0.5,
)

# High recall - retrieve more context
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="general analytics query",
    contexts_cutoff=1.5,  # Loose filtering - more context
    examples_cutoff=1.0,
)
```
