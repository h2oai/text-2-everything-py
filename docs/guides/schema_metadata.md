---
title: Schema Metadata
---

Define tables, dimensions, metrics, and relationships for better SQL.

## Basic Operations

### Create table schema
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

Create relationship:
```python
relationship = client.schema_metadata.create(
    project_id=project.id,
    name="User Orders Relationship",
    schema_data={
        "relationship": {
            "from_table": "users",
            "to_table": "orders",
            "from_column": "id",
            "to_column": "user_id",
            "type": "one_to_many"
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

### Filter by type
```python
tables = client.schema_metadata.list_by_type(project.id, "table")
```

### Validation helpers
```python
errors = client.schema_metadata.validate_schema({"table": {"name": "users", "columns": []}}, "table")
stype = client.schema_metadata.get_schema_type({"table": {"name": "users", "columns": []}})
```

## Working with Large Tables (Schema Splitting)

### What is Schema Splitting?

When you create a table schema with **more than 8 columns**, the API automatically splits it into multiple parts. This improves RAG performance by creating smaller, more focused chunks for retrieval.

### Understanding the Return Type

The `create()` method returns:
- **Single object** (`SchemaMetadataResponse`) for schemas with ≤8 columns
- **List** (`List[SchemaMetadataResponse]`) for schemas with >8 columns

### Handling Split Results

Always check the return type:

```python
result = client.schema_metadata.create(
    project_id=project.id,
    name="Large Customer Table",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "email", "type": "VARCHAR(255)"},
                {"name": "first_name", "type": "VARCHAR(100)"},
                {"name": "last_name", "type": "VARCHAR(100)"},
                {"name": "phone", "type": "VARCHAR(20)"},
                {"name": "address", "type": "VARCHAR(255)"},
                {"name": "city", "type": "VARCHAR(100)"},
                {"name": "state", "type": "VARCHAR(50)"},
                {"name": "zip", "type": "VARCHAR(10)"},
                {"name": "country", "type": "VARCHAR(50)"},
            ]
        }
    }
)

# Handle both cases
if isinstance(result, list):
    print(f"Schema split into {len(result)} parts")
    split_group_id = result[0].split_group_id
    for part in result:
        print(f"Part {part.split_index}/{part.total_splits}: {part.id}")
else:
    print(f"Single schema created: {result.id}")
```

### Retrieving Split Groups

Get all parts of a split schema:

```python
# Get complete split group information
split_group = client.schema_metadata.get_split_group(
    project_id=project.id,
    split_group_id=split_group_id
)

print(f"Total parts: {split_group['total_parts']}")
for part in split_group['parts']:
    print(f"Part {part.split_index}: {part.name}")
```

### Deletion Behavior

Deleting any part of a split schema **automatically deletes all parts** in the group:

```python
# Delete just one part - all parts are removed
client.schema_metadata.delete(
    project_id=project.id,
    schema_metadata_id=result[0].id  # Deletes entire group
)
```

### Best Practices

1. **Always use `isinstance()`** to check if result is a list
2. **Store `split_group_id`** if you need to retrieve all parts later
3. **Delete any single part** - no need to delete each part individually
4. **Consider column organization** - group related columns in first 8 for better relevance

## See Also

- **How To → Bulk Operations**: Learn about `bulk_create()` with split schemas
- **How To → Validation**: Required nested fields validation
