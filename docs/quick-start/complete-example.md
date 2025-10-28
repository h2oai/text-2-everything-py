# Complete SDK Example

Build a complete text-to-SQL application using only the Text2Everything SDK. This guide shows all major features in a realistic e-commerce scenario.

## Overview

We'll build a query system for an e-commerce database with:
- 3 related tables (customers, orders, products)
- Business context and rules
- Example queries
- SQL generation and execution
- Feedback and caching

**Time**: ~15 minutes | **Level**: Beginner to Intermediate

## Setup

```python
from text2everything_sdk import Text2EverythingClient

# Initialize client
client = Text2EverythingClient(
    base_url="https://your-api.com",
    access_token="your-token",
    workspace_name="workspaces/prod"
)

# Create project
project = client.projects.create(
    name="E-commerce Analytics",
    description="Natural language queries for e-commerce data"
)

print(f"Project created: {project.id}")
```

## Step 1: Define Data Model

Create schemas for your database tables:

```python
# Customers table
customers_schema = client.schema_metadata.create(
    project_id=project.id,
    name="customers_table",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "customer_id", "type": "INTEGER", "description": "Primary key"},
                {"name": "name", "type": "VARCHAR(100)", "description": "Customer name"},
                {"name": "email", "type": "VARCHAR(255)", "description": "Email address"},
                {"name": "signup_date", "type": "DATE", "description": "Account creation date"},
                {"name": "tier", "type": "VARCHAR(20)", "description": "Customer tier: bronze, silver, gold"}
            ]
        }
    }
)

# Orders table
orders_schema = client.schema_metadata.create(
    project_id=project.id,
    name="orders_table",
    schema_data={
        "table": {
            "name": "orders",
            "columns": [
                {"name": "order_id", "type": "INTEGER"},
                {"name": "customer_id", "type": "INTEGER", "description": "FK to customers"},
                {"name": "order_date", "type": "TIMESTAMP"},
                {"name": "total_amount", "type": "DECIMAL(10,2)"},
                {"name": "status", "type": "VARCHAR(20)", "description": "pending, shipped, delivered"}
            ]
        }
    }
)

# Products table
products_schema = client.schema_metadata.create(
    project_id=project.id,
    name="products_table",
    schema_data={
        "table": {
            "name": "products",
            "columns": [
                {"name": "product_id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR(200)"},
                {"name": "category", "type": "VARCHAR(50)"},
                {"name": "price", "type": "DECIMAL(10,2)"}
            ]
        }
    }
)

# Define relationship
relationship = client.schema_metadata.create(
    project_id=project.id,
    name="customer_orders_relationship",
    schema_data={
        "relationship": {
            "from_table": "customers",
            "to_table": "orders",
            "from_column": "customer_id",
            "to_column": "customer_id",
            "type": "one_to_many"
        }
    }
)

print("✅ Data model defined")
```

## Step 2: Add Business Context

Provide business rules and definitions:

```python
# Business rules
business_rules = client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="""
    - Active customers have placed an order in the last 90 days
    - VIP customers are those with tier='gold' or total purchases > $10,000
    - Monthly active users are counted by unique customers with orders in that month
    - Revenue is calculated from orders with status='delivered'
    """,
    is_always_displayed=True
)

# Data definitions
definitions = client.contexts.create(
    project_id=project.id,
    name="Data Definitions",
    content="""
    - Customer tiers: bronze (new), silver (regular), gold (VIP)
    - Order statuses: pending, shipped, delivered, cancelled
    - Product categories: electronics, clothing, home, sports
    """,
    is_always_displayed=True
)

print("✅ Business context added")
```

## Step 3: Add Golden Examples

Provide example queries to guide SQL generation:

```python
# Example 1: Customer count
example1 = client.golden_examples.create(
    project_id=project.id,
    name="Active customer count",
    user_query="How many active customers do we have?",
    sql_query="""
    SELECT COUNT(DISTINCT customer_id) 
    FROM orders 
    WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
    """,
    description="Count customers with recent orders"
)

# Example 2: Revenue by category
example2 = client.golden_examples.create(
    project_id=project.id,
    name="Revenue by category",
    user_query="What's our revenue by product category?",
    sql_query="""
    SELECT 
        p.category,
        SUM(o.total_amount) as revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'delivered'
    GROUP BY p.category
    ORDER BY revenue DESC
    """,
    description="Calculate delivered order revenue by category"
)

# Example 3: Top customers
example3 = client.golden_examples.create(
    project_id=project.id,
    name="Top customers",
    user_query="Show me our top 10 customers by revenue",
    sql_query="""
    SELECT 
        c.name,
        c.email,
        SUM(o.total_amount) as total_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'delivered'
    GROUP BY c.customer_id, c.name, c.email
    ORDER BY total_revenue DESC
    LIMIT 10
    """,
    description="Top customers by total delivered order value"
)

print("✅ Golden examples added")
```

## Step 4: Generate SQL

Create a chat session and generate SQL:

```python
# Create chat session
session = client.chat_sessions.create(
    project_id=project.id,
    name="Analytics Session"
)

# Generate SQL from natural language
response = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="What are the monthly sales trends for the last year?"
)

print(f"\nQuery: What are the monthly sales trends for the last year?")
print(f"Generated SQL:\n{response.sql_query}")
print(f"\nExplanation: {response.explanation}")
```

## Step 5: Execute Queries (Optional)

If you have a database connector:

```python
# Create connector (Snowflake example)
connector = client.connectors.create(
    name="E-commerce Database",
    db_type="snowflake",
    host="your-account.snowflakecomputing.com",
    port=443,
    database="ecommerce",
    username="your-username",
    password="your-password",
    config={"warehouse": "COMPUTE_WH"}
)

# Generate and execute SQL
answer = client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="How many orders were placed last month?",
    connector_id=connector.id
)

if answer.execution_result:
    print(f"\nSQL: {answer.sql_query}")
    print(f"Result: {answer.execution_result.result}")
    print(f"Execution time: {answer.execution_result.execution_time_ms}ms")
```

## Step 6: Add Feedback

Improve the system with user feedback:

```python
# Positive feedback for good results
feedback = client.feedback.create_positive(
    project_id=project.id,
    chat_message_id=answer.chat_message_id,
    feedback_text="Perfect! Exactly what I needed.",
    execution_id=answer.execution_result.execution_id
)

print("✅ Feedback added - this execution is now cached for reuse")
```

## Step 7: Use Execution Cache

Leverage cached results for similar queries:

```python
# Look for cached executions
cache_result = client.chat.execution_cache_lookup(
    project_id=project.id,
    user_query="How many orders last month",
    connector_id=connector.id,
    only_positive_feedback=True,  # Only use verified good queries
    similarity_threshold=0.8
)

if cache_result.cache_hit:
    print(f"\n✅ Found {len(cache_result.matches)} similar cached queries!")
    
    best_match = cache_result.matches[0]
    print(f"Similarity: {best_match.similarity_score:.2f}")
    print(f"Cached SQL: {best_match.execution['sql_query']}")
    print(f"Cached Result: {best_match.execution['result']}")
else:
    print("No cache hits - executing new query")
```

## Complete Workflow

Here's a complete function that ties it all together:

```python
def query_with_cache(client, project_id, session_id, connector_id, user_query):
    """
    Query with cache-first strategy and feedback collection.
    """
    # 1. Try cache first
    cache_result = client.chat.execution_cache_lookup(
        project_id=project_id,
        user_query=user_query,
        connector_id=connector_id,
        similarity_threshold=0.85,
        only_positive_feedback=True
    )
    
    if cache_result.cache_hit and cache_result.matches:
        print("📦 Using cached result")
        return cache_result.matches[0].execution['result']
    
    # 2. Generate and execute new query
    print("🔄 Generating new query...")
    answer = client.chat.chat_to_answer(
        project_id=project_id,
        chat_session_id=session_id,
        query=user_query,
        connector_id=connector_id
    )
    
    if answer.execution_result:
        print(f"✅ Query executed in {answer.execution_result.execution_time_ms}ms")
        
        # 3. Collect feedback (in production, ask user)
        # For now, we'll add positive feedback automatically
        client.feedback.create_positive(
            project_id=project_id,
            chat_message_id=answer.chat_message_id,
            feedback_text="Query executed successfully",
            execution_id=answer.execution_result.execution_id
        )
        
        return answer.execution_result.result
    
    return None

# Usage
result = query_with_cache(
    client,
    project.id,
    session.id,
    connector.id,
    "What were our total sales last quarter?"
)
print(f"Result: {result}")
```

## Common Queries to Try

```python
queries = [
    "How many new customers signed up last month?",
    "What's the average order value by customer tier?",
    "Which products are selling best this quarter?",
    "Show me customers who haven't ordered in 6 months",
    "What's our revenue growth month over month?"
]

for query in queries:
    response = client.chat.chat_to_sql(
        project_id=project.id,
        chat_session_id=session.id,
        query=query
    )
    print(f"\n📊 Query: {query}")
    print(f"SQL: {response.sql_query[:100]}...")
```

## Best Practices

### 1. Schema Design
- Include descriptive column descriptions
- Define relationships between tables
- Add dimensions and metrics for common aggregations

### 2. Context Management
- Keep contexts concise and focused
- Mark important contexts as `is_always_displayed=True`
- Update contexts as business rules change

### 3. Golden Examples
- Cover common query patterns
- Include edge cases
- Keep examples up-to-date with schema changes

### 4. Feedback Loop
- Always add feedback for executed queries
- Use positive feedback to build cache
- Review negative feedback to improve examples

### 5. Performance
- Use cache lookup before executing queries
- Set appropriate similarity thresholds
- Monitor cache hit rates

## Next Steps

### Learn Advanced Features
- [RAG Filtering](../guides/chat.md#rag-retrieval-filtering) - Fine-tune context retrieval
- [Bulk Operations](../how-to/bulk_operations.md) - Efficiently manage large datasets
- [Chat Presets](../guides/chat_presets.md) - Reusable configurations

### Production Deployment
- [Connectors Guide](../guides/connectors.md) - Connect to your databases
- [Feedback Guide](../guides/feedback.md) - Build feedback loops
- [Executions Guide](../guides/executions.md) - Optimize query execution

### Enterprise Integration
For H2O ecosystem integration including H2O Drive, CustomGPT, and agent orchestration, see:
- [Advanced Integration Guide](advanced-integration.md)

## Troubleshooting

### SQL Quality Issues
```python
# Fine-tune RAG retrieval for better context
response = client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="your query",
    contexts_cutoff=0.3,      # Stricter context matching
    examples_cutoff=0.2,      # Very strict example matching
    schema_cutoff=0.2         # Precise schema matching
)
```

### Performance Issues
```python
# Use bulk operations for large datasets
schemas = client.schema_metadata.bulk_create(
    project_id=project.id,
    schema_metadata_list=schema_list,
    validate=True
)
```

## Summary

You've built a complete text-to-SQL application! You now know how to:

✅ Define data models with schemas and relationships  
✅ Add business context and rules  
✅ Provide golden examples for guidance  
✅ Generate SQL from natural language  
✅ Execute queries (optional)  
✅ Add feedback to improve results  
✅ Leverage caching for performance  

**Ready for production?** Check out the [Guides](../guides/projects.md) for advanced features and best practices.
