---
title: Executions
---

Execute SQL queries against database connectors and leverage execution caching.

## Basic Operations

### Execute SQL from Chat Message

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev"
)

# Execute SQL from a chat message
result = client.executions.execute_from_chat(
    project_id="proj-123",
    connector_id="conn-456",
    chat_message_id="msg-789"
)

print(f"Execution time: {result.execution_time_ms}ms")
print(f"Rows returned: {len(result.result.get('data', []))}")
print(f"Result: {result.result}")
```

### Execute SQL Query Directly

```python
# Execute a SQL query directly
result = client.executions.execute_query(
    project_id="proj-123",
    connector_id="conn-456",
    sql_query="SELECT * FROM users WHERE active = true LIMIT 10"
)

print(f"Query executed in {result.execution_time_ms}ms")
print(f"Found {len(result.result.get('data', []))} rows")
```

### Execute with Session Context

```python
# Include chat session for context
result = client.executions.execute_query(
    project_id="proj-123",
    connector_id="conn-456",
    sql_query="SELECT COUNT(*) FROM orders WHERE status = 'pending'",
    chat_session_id="session-abc"
)
```

### Get Execution Details

```python
# Retrieve execution by ID
execution = client.executions.get(
    project_id="proj-123",
    execution_id="exec-456"
)

print(f"Query: {execution.sql_query}")
print(f"Time: {execution.execution_time_ms}ms")
print(f"Success: {execution.successful}")
```

### List Executions

```python
# List all executions
executions = client.executions.list(project_id="proj-123")

for execution in executions:
    status = "✓" if execution.successful else "✗"
    print(f"{status} ID: {execution.id}, Time: {execution.execution_time_ms}ms")

# List with filters
executions = client.executions.list(
    project_id="proj-123",
    connector_id="conn-456",
    limit=50,
    skip=0
)

# Filter by chat message
executions = client.executions.list(
    project_id="proj-123",
    chat_message_id="msg-789"
)

# Search executions
executions = client.executions.list(
    project_id="proj-123",
    q="customers"
)
```

## Execution Cache Lookup

The execution cache allows you to find and reuse results from previously executed SQL queries that are semantically similar to your current query. This can significantly improve performance and reduce database load.

### Basic Cache Lookup

```python
# Look for similar executions
result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="How many active users do we have?",
    connector_id="conn-456"
)

if result.cache_hit:
    print(f"Found {len(result.matches)} similar executions!")
    for match in result.matches:
        print(f"Similarity: {match.similarity_score:.2f}")
        print(f"SQL: {match.execution.get('sql_query')}")
        print(f"Results: {match.execution.get('result')}")
else:
    print("No similar executions found in cache")
```

### Advanced Cache Lookup

```python
# Fine-tune cache lookup with parameters
result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="Show me top customers by revenue",
    connector_id="conn-456",
    max_age_days=7,              # Only consider executions from last 7 days
    similarity_threshold=0.8,     # Higher threshold for more similar matches
    limit=100,                    # Check up to 100 candidates
    top_n=3,                      # Return top 3 matches
    only_positive_feedback=True   # Only return executions with positive feedback
)

if result.cache_hit:
    print(f"Found {len(result.matches)} highly similar executions")
    
    for i, match in enumerate(result.matches, 1):
        print(f"\nMatch {i}:")
        print(f"  Similarity: {match.similarity_score:.2f}")
        print(f"  SQL: {match.execution.get('sql_query')}")
        print(f"  Executed: {match.execution.get('created_at')}")
        print(f"  Time: {match.execution.get('execution_time_ms')}ms")
        
        if match.has_feedback:
            feedback_icon = "👍" if match.feedback_is_positive else "👎"
            print(f"  Feedback: {feedback_icon}")
```

### Cache Lookup Parameters

- **max_age_days**: Filter executions by age (default: 30 days)
  - Use shorter periods for fast-changing data
  - Use longer periods for stable datasets
  
- **similarity_threshold**: Minimum similarity score 0.0-1.0 (default: 0.65)
  - Higher values (0.8+): Only very similar queries
  - Medium values (0.6-0.8): Balanced similarity
  - Lower values (0.4-0.6): Broader matches
  
- **limit**: Number of candidates to check (default: 50)
  - Higher values: More thorough search, slower
  - Lower values: Faster search, might miss matches
  
- **top_n**: Number of matches to return (default: 5)
  
- **only_positive_feedback**: Filter by feedback (default: False)
  - True: Only executions users marked as helpful
  - False: All executions regardless of feedback

### Using Cache Results

```python
# Lookup cache before executing new query
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="Count active customers",
    connector_id="conn-456",
    similarity_threshold=0.9,  # Very strict matching
    only_positive_feedback=True
)

if cache_result.cache_hit and cache_result.matches:
    # Use cached result
    best_match = cache_result.matches[0]
    print("Using cached result:")
    print(f"SQL: {best_match.execution['sql_query']}")
    print(f"Result: {best_match.execution['result']}")
    print(f"Age: {best_match.execution['created_at']}")
else:
    # Execute new query
    result = client.executions.execute_query(
        project_id="proj-123",
        connector_id="conn-456",
        sql_query="SELECT COUNT(*) FROM customers WHERE status = 'active'"
    )
    print("Executed new query:")
    print(f"Result: {result.result}")
```

## Integrating Cache with Chat

```python
# Complete workflow: Cache lookup + Chat + Execution
user_query = "Show me monthly sales trends"

# 1. Check cache first
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query=user_query,
    connector_id="conn-456",
    max_age_days=1,  # Today's queries only
    similarity_threshold=0.85
)

if cache_result.cache_hit:
    # Use cached result
    print("Using cached execution")
    cached_data = cache_result.matches[0].execution['result']
else:
    # No cache hit - generate and execute SQL
    print("Generating new SQL...")
    
    # Create session
    session = client.chat_sessions.create(project_id="proj-123")
    
    # Generate and execute
    answer = client.chat.chat_to_answer(
        project_id="proj-123",
        chat_session_id=session.id,
        query=user_query,
        connector_id="conn-456"
    )
    
    if answer.execution_result:
        print(f"Executed in {answer.execution_result.execution_time_ms}ms")
        result_data = answer.execution_result.result
```

## Performance Optimization

### Cache-First Pattern

```python
def get_query_result(client, project_id, connector_id, user_query):
    """
    Attempt to use cache first, fall back to execution.
    """
    # Try cache with strict matching
    cache_result = client.chat.execution_cache_lookup(
        project_id=project_id,
        user_query=user_query,
        connector_id=connector_id,
        similarity_threshold=0.85,
        max_age_days=1,
        only_positive_feedback=True
    )
    
    if cache_result.cache_hit and cache_result.matches:
        return {
            "source": "cache",
            "data": cache_result.matches[0].execution['result'],
            "cached_sql": cache_result.matches[0].execution['sql_query']
        }
    
    # No cache hit - execute query
    session = client.chat_sessions.create(project_id=project_id)
    answer = client.chat.chat_to_answer(
        project_id=project_id,
        chat_session_id=session.id,
        query=user_query,
        connector_id=connector_id
    )
    
    return {
        "source": "execution",
        "data": answer.execution_result.result if answer.execution_result else None,
        "sql": answer.sql_query
    }

# Usage
result = get_query_result(
    client, 
    "proj-123", 
    "conn-456", 
    "What are our top 10 products?"
)

print(f"Result from: {result['source']}")
print(f"Data: {result['data']}")
```

## Best Practices

1. **Cache Strategy**
   - Use cache lookup for frequently asked questions
   - Set appropriate `max_age_days` based on data volatility
   - Use `only_positive_feedback=True` for production queries
   - Monitor cache hit rates to optimize thresholds

2. **Performance**
   - Cache lookups are fast - always try cache first
   - Adjust `similarity_threshold` based on query precision needs
   - Use shorter `max_age_days` for fast-changing data
   - Set `limit` appropriately (50-100 is usually sufficient)

3. **Feedback Integration**
   - Add positive feedback to good executions to improve cache quality
   - Filter cache results by positive feedback for reliable answers
   - Review negative feedback to identify problematic queries

4. **Error Handling**
   - Always check `result.cache_hit` before using matches
   - Handle empty matches list gracefully
   - Fall back to execution if cache misses

## Common Patterns

### Daily Report Caching

```python
# Check for today's report first
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="Generate daily sales report",
    connector_id="conn-456",
    max_age_days=1,  # Today only
    similarity_threshold=0.95  # Exact match
)

if cache_result.cache_hit:
    print("Using today's cached report")
    report_data = cache_result.matches[0].execution['result']
else:
    print("Generating fresh report")
    # Execute new query...
```

### Query Suggestion from Cache

```python
# Find similar queries users have run
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="customer analytics",
    connector_id="conn-456",
    similarity_threshold=0.5,  # Broader match for suggestions
    top_n=10,
    only_positive_feedback=True
)

if cache_result.matches:
    print("Similar queries:")
    for match in cache_result.matches:
        print(f"  • {match.execution.get('user_query', 'N/A')}")
        print(f"    SQL: {match.execution['sql_query']}")
```
