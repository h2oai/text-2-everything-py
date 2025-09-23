---
title: Custom Tools
---

Upload Python scripts as tools and use them with chats.

Create from files or directory:
```python
# From file paths
tool = client.custom_tools.create(
    project_id=project.id,
    name="Analysis Suite",
    description="Custom analysis tools",
    files=["analysis.py", "utils.py"],
)

# From a directory (all .py files)
tool = client.custom_tools.create_from_directory(
    project_id=project.id,
    name="Analysis Suite",
    description="Toolkit",
    directory_path="./scripts",
)
```

List/get/update/delete:
```python
tools = client.custom_tools.list(project.id)
one = client.custom_tools.get(project.id, tool.id)

# Update metadata or replace files
updated = client.custom_tools.update(project.id, tool.id, name="Updated")
updated = client.custom_tools.replace_files(project.id, tool.id, ["new_main.py"]) 

client.custom_tools.delete(project.id, tool.id)
```


