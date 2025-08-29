---
title: Schema Metadata
---

Define tables, dimensions, metrics, and relationships for better SQL.

Create table schema:
```python
schema = client.schema_metadata.create(
    project_id=project.id,
    name="Users Table",
    schema_data={
        "table": {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "email", "type": "VARCHAR(255)"}
            ]
        }
    },
)
```

Create dimension:
```python
dimension = client.schema_metadata.create(
    project_id=project.id,
    name="User Status",
    schema_data={
        "table": {
            "dimension": {
                "name": "status",
                "content": {"type": "categorical", "values": ["active","inactive"]}
            }
        }
    },
)
```

Create metric:
```python
metric = client.schema_metadata.create(
    project_id=project.id,
    name="Total Revenue",
    schema_data={
        "table": {
            "metric": {
                "name": "total_revenue",
                "content": {"aggregation": "sum", "column": "amount"}
            }
        }
    },
)
```

List/get/update/delete:
```python
schemas = client.schema_metadata.list(project_id=project.id)
one = client.schema_metadata.get(project_id=project.id, schema_metadata_id=schema.id)
updated = client.schema_metadata.update(project_id=project.id, schema_metadata_id=schema.id, description="Updated")
client.schema_metadata.delete(project_id=project.id, schema_metadata_id=schema.id)
```

Filter by type:
```python
tables = client.schema_metadata.list_by_type(project.id, "table")
```

Bulk create with validation:
```python
items = [
  {"name": "t1", "schema_data": {"table": {"name": "t1", "columns": []}}},
  {"name": "dim1", "schema_data": {"table": {"dimension": {"name": "d", "content": {}}}}},
]
created = client.schema_metadata.bulk_create(project.id, items, validate=True)
```

Validation helpers:
```python
errors = client.schema_metadata.validate_schema({"table": {"name": "users", "columns": []}}, "table")
stype = client.schema_metadata.get_schema_type({"table": {"name": "users", "columns": []}})
```

See also: How To → Validation for required nested fields.
