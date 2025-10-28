---
title: Bulk Operations
---

Create many items efficiently. If bulk fails, fall back to per-item creates.

Contexts bulk:
```python
items = [{"name": "Rule 1", "content": "..."}, {"name": "Rule 2", "content": "..."}]
created = client.contexts.bulk_create(project.id, items)
```

Schema metadata bulk with validation:
```python
schemas = [
  {"name": "t1", "schema_data": {"table": {"name": "t1", "columns": []}}},
  {"name": "dim1", "schema_data": {"table": {"dimension": {"name": "d", "content": {}}}}},
]
created = client.schema_metadata.bulk_create(project.id, schemas, validate=True)
```

Golden examples bulk:
```python
examples = [
  {"user_query": "How many users?", "sql_query": "SELECT COUNT(*) FROM users;"},
  {"user_query": "Active users?", "sql_query": "SELECT COUNT(*) FROM users WHERE active=true;"},
]
created = client.golden_examples.bulk_create(project.id, examples)
```

## Bulk Operations with Split Schemas

When creating schema metadata with `bulk_create()`, tables with >8 columns are automatically split into multiple parts. The results are **flattened**, meaning you get all parts from all schemas in a single list.

### Understanding Result Flattening

```python
schemas = [
    # Small schema (4 columns) - returns 1 part
    {
        "name": "Small Table",
        "schema_data": {
            "table": {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "email", "type": "VARCHAR(255)"},
                    {"name": "name", "type": "VARCHAR(100)"},
                    {"name": "status", "type": "VARCHAR(50)"},
                ]
            }
        }
    },
    # Large schema (10 columns) - returns 2 parts
    {
        "name": "Large Table",
        "schema_data": {
            "table": {
                "name": "customers",
                "columns": [
                    {"name": f"col_{i}", "type": "VARCHAR(100)"}
                    for i in range(10)
                ]
            }
        }
    }
]

# Create both schemas
results = client.schema_metadata.bulk_create(project.id, schemas)

# Results are flattened: 1 part + 2 parts = 3 total items
print(f"Input: {len(schemas)} schemas")
print(f"Output: {len(results)} schema parts")  # Will be 3

# Identify split vs non-split schemas
for result in results:
    if result.split_group_id:
        print(f"Split part {result.split_index}/{result.total_splits}: {result.name}")
    else:
        print(f"Single schema: {result.name}")
```

### Handling Split Results

Group results by `split_group_id` to identify which parts belong together:

```python
# Organize results by split groups
split_groups = {}
single_schemas = []

for result in results:
    if result.split_group_id:
        if result.split_group_id not in split_groups:
            split_groups[result.split_group_id] = []
        split_groups[result.split_group_id].append(result)
    else:
        single_schemas.append(result)

print(f"Created {len(single_schemas)} single schemas")
print(f"Created {len(split_groups)} split groups")
```

### Parallel Bulk Operations

For large batches, use parallel processing with split-aware handling:

```python
# Enable parallel processing (default)
results = client.schema_metadata.bulk_create(
    project.id,
    schemas,
    parallel=True,
    max_workers=8  # Control concurrency
)

# Results are still flattened - handle them the same way
split_count = sum(1 for r in results if r.split_group_id)
single_count = len(results) - split_count
print(f"Created {single_count} single + {split_count} split parts")
```

### Best Practices

1. **Expect more results than inputs** - large schemas create multiple parts
2. **Group by `split_group_id`** - to identify which parts belong together
3. **Delete responsibly** - deleting one part cascades to entire split group
4. **Use parallel mode** - significantly faster for large batches

## Fallback Pattern

Fallback helper:
```python
def create_with_fallback(client, project_id, data_list, resource_name):
    try:
        if resource_name == "contexts":
            return client.contexts.bulk_create(project_id, data_list)
        elif resource_name == "schema_metadata":
            return client.schema_metadata.bulk_create(project_id, data_list)
        elif resource_name == "golden_examples":
            return client.golden_examples.bulk_create(project_id, data_list)
    except Exception:
        results = []
        for item_data in data_list:
            try:
                if resource_name == "contexts":
                    results.append(client.contexts.create(project_id=project_id, **item_data))
                elif resource_name == "schema_metadata":
                    results.append(client.schema_metadata.create(project_id=project_id, **item_data))
                elif resource_name == "golden_examples":
                    results.append(client.golden_examples.create(project_id=project_id, **item_data))
            except Exception:
                pass
        return results
```
