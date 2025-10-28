---
title: Feedback
---

Manage feedback on chat messages and SQL executions to improve query quality and enable execution caching.

Feedback serves two key purposes:
1. **Quality Improvement**: Help the system learn from user corrections
2. **Execution Caching**: Positive feedback marks executions as reliable for cache reuse

## Basic Operations

### Create Feedback for Chat Message

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev"
)

# Create positive feedback
feedback = client.feedback.create(
    project_id="proj-123",
    chat_message_id="msg-456",
    feedback="The SQL query worked perfectly!",
    is_positive=True
)

print(f"Feedback created: {feedback.id}")
```

### Create Feedback for Execution

```python
# Link feedback to both chat message and execution
feedback = client.feedback.create(
    project_id="proj-123",
    chat_message_id="msg-456",
    execution_id="exec-789",  # Link to execution
    feedback="Query results are accurate and fast",
    is_positive=True
)

print(f"Feedback linked to execution: {feedback.execution_id}")
```

### Helper Methods

```python
# Create positive feedback
positive = client.feedback.create_positive(
    project_id="proj-123",
    chat_message_id="msg-456",
    feedback_text="Excellent query!",
    execution_id="exec-789"
)

# Create negative feedback
negative = client.feedback.create_negative(
    project_id="proj-123",
    chat_message_id="msg-456",
    feedback="Query returned incorrect results",
    execution_id="exec-789"
)
```

### List Feedback

```python
# List all feedback
all_feedback = client.feedback.list(project_id="proj-123")
for fb in all_feedback:
    status = "👍" if fb.is_positive else "👎"
    print(f"{status} {fb.feedback}")

# Search feedback
search_results = client.feedback.list(
    project_id="proj-123",
    search="query"
)

# Pagination
page1 = client.feedback.list(
    project_id="proj-123",
    skip=0,
    limit=50
)
```

### Get Feedback

```python
feedback = client.feedback.get(
    project_id="proj-123",
    feedback_id="feedback-abc"
)

print(f"Feedback: {feedback.feedback}")
print(f"Positive: {feedback.is_positive}")
print(f"Execution: {feedback.execution_id}")
```

### Update Feedback

```python
updated = client.feedback.update(
    project_id="proj-123",
    feedback_id="feedback-abc",
    feedback="Updated: The query was excellent!",
    is_positive=True
)
```

### Delete Feedback

```python
success = client.feedback.delete(
    project_id="proj-123",
    feedback_id="feedback-abc"
)
```

## Bulk Operations

### Bulk Delete

```python
result = client.feedback.bulk_delete(
    project_id="proj-123",
    feedback_ids=["feedback-1", "feedback-2", "feedback-3"]
)

print(f"Deleted {result['deleted_count']} feedback entries")
if result['failed_ids']:
    print(f"Failed: {result['failed_ids']}")
```

## Filtering and Querying

### List by Sentiment

```python
# Get all positive feedback
positive_feedback = client.feedback.list_positive(project_id="proj-123")
print(f"Found {len(positive_feedback)} positive feedback items")

# Get all negative feedback
negative_feedback = client.feedback.list_negative(project_id="proj-123")
print(f"Found {len(negative_feedback)} negative feedback items")
```

### Get Feedback for Message

```python
# Get all feedback for a specific chat message
message_feedback = client.feedback.get_feedback_for_message(
    project_id="proj-123",
    chat_message_id="msg-456"
)

for feedback in message_feedback:
    print(f"Feedback: {feedback.feedback}")
    print(f"Execution: {feedback.execution_id}")
```

## Integration with Executions

Feedback on executions is crucial for the execution cache system. Positive feedback marks executions as reliable for reuse.

### Feedback Workflow with Execution

```python
# 1. Execute a query
result = client.executions.execute_query(
    project_id="proj-123",
    connector_id="conn-456",
    sql_query="SELECT * FROM customers WHERE status = 'active'"
)

# 2. Present results to user
print(f"Query executed: {result.sql_query}")
print(f"Results: {result.result}")

# 3. User provides feedback
# If results are good, create positive feedback
feedback = client.feedback.create_positive(
    project_id="proj-123",
    chat_message_id=result.chat_message_id,  # From chat context
    feedback_text="Perfect results!",
    execution_id=result.execution_id
)

# This execution is now marked as reliable for cache reuse
```

### Enabling Cache with Feedback

```python
# Cache lookup favors executions with positive feedback
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="Show active customers",
    connector_id="conn-456",
    only_positive_feedback=True  # Only return executions with positive feedback
)

if cache_result.cache_hit:
    for match in cache_result.matches:
        if match.has_feedback and match.feedback_is_positive:
            print(f"Using execution with positive feedback")
            print(f"SQL: {match.execution['sql_query']}")
```

### Complete Chat-Execute-Feedback Flow

```python
# Create chat session
session = client.chat_sessions.create(project_id="proj-123")

# Generate and execute SQL
answer = client.chat.chat_to_answer(
    project_id="proj-123",
    chat_session_id=session.id,
    query="Count active users",
    connector_id="conn-456"
)

if answer.execution_result:
    # Store execution details
    execution_id = answer.execution_result.execution_id
    chat_message_id = answer.chat_message_id
    
    # Present results to user
    print(f"SQL: {answer.sql_query}")
    print(f"Results: {answer.execution_result.result}")
    
    # User validates results and provides feedback
    user_satisfied = True  # User input
    
    if user_satisfied:
        # Add positive feedback
        feedback = client.feedback.create_positive(
            project_id="proj-123",
            chat_message_id=chat_message_id,
            feedback_text="Results are accurate",
            execution_id=execution_id
        )
        print("✅ Marked execution for cache reuse")
    else:
        # Add negative feedback with correction
        feedback = client.feedback.create_negative(
            project_id="proj-123",
            chat_message_id=chat_message_id,
            feedback="Results missing recent data - needs updated schema",
            execution_id=execution_id
        )
        print("❌ Execution marked for review")
```

## Feedback Impact on System

### Cache Quality

Positive feedback directly improves execution cache quality:

```python
# Without feedback filter - may include unreliable executions
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="sales data",
    connector_id="conn-456"
)

# With feedback filter - only proven good executions
cache_result = client.chat.execution_cache_lookup(
    project_id="proj-123",
    user_query="sales data",
    connector_id="conn-456",
    only_positive_feedback=True  # Higher quality results
)
```

### RAG Improvement

Feedback helps improve context retrieval in chat queries:

```python
# Generate SQL with feedback-enhanced RAG
response = client.chat.chat_to_sql(
    project_id="proj-123",
    chat_session_id=session.id,
    query="Show customer metrics",
    feedback_cutoff=0.5  # Use feedback in retrieval
)
```

## Best Practices

1. **Execution Feedback**
   - Always link feedback to execution_id when available
   - Add positive feedback for verified correct results
   - Add negative feedback with specific issues for debugging
   - Use feedback to build reliable execution cache

2. **Feedback Quality**
   - Provide specific, actionable feedback text
   - Include what was wrong or right
   - Reference specific data issues when applicable

3. **Cache Optimization**
   - Filter cache by positive feedback in production
   - Review negative feedback to improve queries
   - Monitor feedback rates to assess system quality

4. **Bulk Operations**
   - Use bulk_delete for cleanup operations
   - Handle failed deletions appropriately
   - Check deleted_count vs expected count

## Common Patterns

### User Validation Workflow

```python
def execute_with_validation(client, project_id, session_id, query, connector_id):
    """
    Execute query and collect user feedback.
    """
    # Execute
    answer = client.chat.chat_to_answer(
        project_id=project_id,
        chat_session_id=session_id,
        query=query,
        connector_id=connector_id
    )
    
    if not answer.execution_result:
        return None
    
    # Present to user
    print(f"SQL: {answer.sql_query}")
    print(f"Results: {answer.execution_result.result}")
    
    # Collect feedback
    user_rating = input("Rate this result (good/bad): ").lower()
    user_comment = input("Comments (optional): ")
    
    # Record feedback
    if user_rating == "good":
        client.feedback.create_positive(
            project_id=project_id,
            chat_message_id=answer.chat_message_id,
            feedback_text=user_comment or "Results validated",
            execution_id=answer.execution_result.execution_id
        )
    elif user_rating == "bad":
        client.feedback.create_negative(
            project_id=project_id,
            chat_message_id=answer.chat_message_id,
            feedback=user_comment or "Results incorrect",
            execution_id=answer.execution_result.execution_id
        )
    
    return answer.execution_result
```

### Feedback-Driven Cache

```python
def smart_query(client, project_id, connector_id, user_query):
    """
    Use cache with feedback, fall back to execution.
    """
    # Try cache with positive feedback only
    cache_result = client.chat.execution_cache_lookup(
        project_id=project_id,
        user_query=user_query,
        connector_id=connector_id,
        only_positive_feedback=True,
        similarity_threshold=0.8
    )
    
    if cache_result.cache_hit and cache_result.matches:
        best_match = cache_result.matches[0]
        print(f"Using cached result (feedback score: ✅)")
        return best_match.execution['result']
    
    # Execute new query
    session = client.chat_sessions.create(project_id=project_id)
    answer = client.chat.chat_to_answer(
        project_id=project_id,
        chat_session_id=session.id,
        query=user_query,
        connector_id=connector_id
    )
    
    if answer.execution_result:
        # Prompt for feedback to improve future cache
        print("Please provide feedback to improve future results...")
        return answer.execution_result.result
    
    return None
```

### Feedback Analytics

```python
# Analyze feedback patterns
all_feedback = client.feedback.list(project_id="proj-123")

positive_count = sum(1 for f in all_feedback if f.is_positive)
negative_count = len(all_feedback) - positive_count

print(f"Positive: {positive_count} ({positive_count/len(all_feedback)*100:.1f}%)")
print(f"Negative: {negative_count} ({negative_count/len(all_feedback)*100:.1f}%)")

# Review negative feedback for improvements
negative = [f for f in all_feedback if not f.is_positive]
for fb in negative:
    print(f"Issue: {fb.feedback}")
    print(f"Execution: {fb.execution_id}")
```
