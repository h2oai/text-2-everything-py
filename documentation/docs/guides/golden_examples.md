---
title: Golden Examples
---

Provide high-quality query↔SQL pairs to guide generation.

Create/list/get/update/delete:
```python
example = client.golden_examples.create(
    project_id=project.id,
    user_query="How many users?",
    sql_query="SELECT COUNT(*) FROM users;",
    description="Count total users",
)

examples = client.golden_examples.list(project.id)
example = client.golden_examples.get(project.id, example.id)
example = client.golden_examples.update(project.id, example.id, description="Updated")
client.golden_examples.delete(project.id, example.id)
```

Bulk create:
```python
items = [
  {"user_query": "How many users?", "sql_query": "SELECT COUNT(*) FROM users;"},
  {"user_query": "How many active?", "sql_query": "SELECT COUNT(*) FROM users WHERE active=true;"},
]
created = client.golden_examples.bulk_create(project.id, items)
```

Helpers:
```python
always = client.golden_examples.list_always_displayed(project.id)
search = client.golden_examples.search_by_query(project.id, "user")
```


