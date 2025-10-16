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

Control retrieval quality by filtering out low-similarity documents using cutoff parameters. Each cutoff independently filters its document type based on similarity scores (0.0-1.0, where higher values are more restrictive).

### Using Cutoff Parameters with chat_to_sql

```python
resp = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="Show me customer analytics",
    contexts_cutoff=0.5,      # Filter contexts below 0.5 similarity
    schema_cutoff=0.7,        # Filter schema metadata below 0.7 similarity
    feedback_cutoff=0.6,      # Filter feedback below 0.6 similarity
    examples_cutoff=0.5,      # Filter examples below 0.5 similarity
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
    contexts_cutoff=0.6,      # Only high-quality context documents
    schema_cutoff=0.8,        # Very strict schema filtering
    feedback_cutoff=0.7,      # High-quality feedback only
    examples_cutoff=0.6,      # Relevant examples only
)
if answer.execution_result:
    print(answer.execution_result.result)
```

### Cutoff Parameter Guidelines

- **Range**: 0.0 to 1.0 (typically)
- **Higher values** = more restrictive filtering (only high-similarity chunks)
- **Lower values** = less restrictive filtering (more chunks retrieved)
- **Default** (`None` or `0`): No filtering (retrieves all chunks)
- Each cutoff parameter independently controls its document type:
  - `contexts_cutoff`: Filters context documents
  - `schema_cutoff`: Filters schema metadata
  - `feedback_cutoff`: Filters user feedback
  - `examples_cutoff`: Filters golden examples

### When to Use Cutoff Parameters

Use cutoff parameters to:
- Improve retrieval quality by excluding low-relevance documents
- Reduce noise in the RAG pipeline
- Focus on only the most relevant information for your query
- Optimize response accuracy when you have many similar but not equally relevant documents
