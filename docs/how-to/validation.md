---
title: Validation
---

Required nested fields by type:
- Tables: `table` and `table.columns`
- Dimensions: `table.dimension` and `table.dimension.content`
- Metrics: `table.metric` and `table.metric.content`
- Relationships: `relationship`

Valid examples:
```python
# Table
{"table": {"name": "customers", "columns": [{"name": "id", "type": "INTEGER"}]}}

# Dimension
{"table": {"name": "customers", "dimension": {"name": "status", "content": {"type": "categorical", "values": ["active","inactive"]}}}}

# Metric
{"table": {"name": "orders", "metric": {"name": "total_revenue", "content": {"aggregation": "sum", "column": "amount"}}}}

# Relationship
{"relationship": {"from_table": "users", "to_table": "orders", "from_column": "id", "to_column": "user_id", "type": "one_to_many"}}
```

Programmatic validation:
```python
errors = client.schema_metadata.validate_schema({"table": {"name": "users", "columns": []}}, "table")
if errors:
    print("Invalid:", errors)
```

Invalid example (shows error):
```python
try:
    client.schema_metadata.create(
        project_id=project.id,
        name="Bad Dimension",
        schema_data={"table": {"dimension": {"name": "status"}}},  # missing content
    )
except Exception as e:
    print("Expected ValidationError:", e)
```
