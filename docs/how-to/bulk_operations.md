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
