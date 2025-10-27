---
title: Projects
---

Manage top-level containers for your resources.

Projects are the top-level containers for organizing contexts, schema metadata, golden examples, and other resources in the Text2Everything SDK.

## Basic Operations

### List Projects

```python
from text2everything_sdk import Text2EverythingClient

client = Text2EverythingClient(
    base_url="https://...",
    access_token="...",
    workspace_name="workspaces/dev"
)

# List all projects
projects = client.projects.list()
for project in projects:
    print(f"{project.name}: {project.description}")

# Pagination
page1 = client.projects.list(page=1, per_page=10)
page2 = client.projects.list(page=2, per_page=10)

# Search by name
matching_projects = client.projects.list(search="customer")
```

### Get a Project

```python
# Get by ID
project = client.projects.get("proj_123")
print(f"Project: {project.name}")
print(f"Description: {project.description}")
```

### Create a Project

```python
# Basic creation
project = client.projects.create(
    name="My Project",
    description="Demo project for customer analytics"
)

print(f"Created project: {project.id}")
```

### Update a Project

```python
# Update project details
updated = client.projects.update(
    project_id="proj_123",
    name="Updated Project Name",
    description="Updated description"
)
```

### Delete a Project

```python
result = client.projects.delete("proj_123")
print(result["message"])
```

## Helper Methods

### Get Project by Name

```python
# Find a project by name
project = client.projects.get_by_name("My Project")
if project:
    print(f"Found project: {project.id}")
else:
    print("Project not found")
```

### Check if Project Exists

```python
if client.projects.exists("proj_123"):
    print("Project exists")
else:
    print("Project not found")
```

## Collection Management

Collections are created automatically when resources (contexts, schema metadata, etc.) are added to a project. Each collection type corresponds to a resource type.

### List All Collections

```python
collections = client.projects.list_collections("proj_123")
for collection in collections:
    print(f"{collection.component_type}: {collection.h2ogpte_collection_id}")
```

### Get Collection by Type

```python
# Get specific collection types
contexts_collection = client.projects.get_collection_by_type(
    project_id="proj_123",
    component_type="contexts"
)
print(f"Contexts collection ID: {contexts_collection.h2ogpte_collection_id}")

# Available component types:
# - "contexts"
# - "schema_metadata"
# - "examples" (golden examples)
# - "feedback"
# - "custom_tools"
```

## Common Patterns

### Project Setup Workflow

```python
# 1. Create project
project = client.projects.create(
    name="Sales Analytics",
    description="Project for sales data analysis"
)

# 2. Add contexts
client.contexts.create(
    project_id=project.id,
    name="Business Rules",
    content="Active customers have status = 'active'",
    is_always_displayed=True
)

# 3. Add schema metadata
client.schema_metadata.create(
    project_id=project.id,
    name="customers",
    schema_data={
        "table": {
            "name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR(100)"},
                {"name": "status", "type": "VARCHAR(32)"}
            ]
        }
    }
)

# 4. Add golden examples
client.golden_examples.create(
    project_id=project.id,
    user_query="How many active customers?",
    sql_query="SELECT COUNT(*) FROM customers WHERE status = 'active';"
)

# 5. Create connector
connector = client.connectors.create(
    project_id=project.id,
    name="Production DB",
    db_type="postgres",
    host="db.example.com",
    port=5432,
    username="app_user",
    password="secure_password",
    database="production"
)

print(f"Project {project.name} is ready!")
```

### Multi-Environment Projects

```python
# Create separate projects for different environments
environments = ["development", "staging", "production"]

for env in environments:
    project = client.projects.create(
        name=f"Sales Analytics - {env.title()}",
        description=f"{env.title()} environment for sales analytics"
    )
    print(f"Created {env} project: {project.id}")
```

### Project Cleanup

```python
# Find and delete old test projects
all_projects = client.projects.list(search="test")
for project in all_projects:
    if "deprecated" in project.description.lower():
        client.projects.delete(project.id)
        print(f"Deleted: {project.name}")
```

## Best Practices

1. **Naming Conventions**
   - Use descriptive, meaningful project names
   - Include environment or team information when relevant
   - Keep names consistent across related projects

2. **Project Organization**
   - One project per application or data source
   - Separate projects for different environments (dev, staging, prod)
   - Group related resources within a project

3. **Resource Management**
   - Use collections to understand what resources exist
   - Clean up unused projects regularly
   - Document project purposes in descriptions

4. **Search and Discovery**
   - Use descriptive names that work well with search
   - Leverage the `get_by_name()` helper for known project names
   - Use pagination for large project lists
