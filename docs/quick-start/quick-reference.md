# Text2Everything Quick Reference Guide

A condensed reference for developers who have completed the [Developer Starter Guide](developer-starter-guide.md).

## 🚀 Quick Setup Commands

### Environment Setup
```bash
# Install packages
pip install h2o-drive>=4.1.0 text2everything_sdk-0.1.x-py3-none-any.whl python-dotenv tqdm

# Create .env file
cat > .env << EOF
H2O_CLOUD_ENVIRONMENT=https://your-environment.h2o.ai/
H2O_CLOUD_CLIENT_PLATFORM_TOKEN=your-h2o-token-here
TEXT2EVERYTHING_URL=http://text2everything.text2everything.svc.cluster.local:8000
H2OGPTE_API_KEY=your-h2ogpte-api-key-here
SNOWFLAKE_ACCOUNT=your-account.snowflakecomputing.com
SNOWFLAKE_USERNAME=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
EOF
```

## 📁 Data Structure Template

```
your_project_data/
├── schema_metadata/     # Table schemas (JSON)
│   ├── customers.json
│   └── orders.json
├── contexts/           # Business rules (JSON)
│   ├── business_rules.txt
│   └── data_definitions.json
└── golden_examples/    # Query examples (JSON)
    ├── customer_queries.json
    └── sales_queries.json
```

## 🔧 Essential Code Snippets

### 1. H2O Drive Connection
```python
import h2o_drive, h2o_discovery
from dotenv import load_dotenv

load_dotenv()
discovery = h2o_discovery.discover()
drive_client = h2o_drive.connect(discovery=discovery)
bucket = drive_client.user_bucket()
```

### 2. Text2Everything SDK Setup
```python
from text2everything_sdk import Text2EverythingClient
import os

sdk_client = Text2EverythingClient(
    base_url=os.getenv("TEXT2EVERYTHING_URL"),
    access_token=os.getenv("T2E_ACCESS_TOKEN"),
    workspace_name=os.getenv("T2E_WORKSPACE_NAME"),
    timeout=200,
    max_retries=1
)
```

### 3. Create Project
```python
project = sdk_client.projects.create(
    name="Your Project Name",
    description="Project description"
)
print(f"Project ID: {project.id}")
```

### 4. Snowflake Connector
```python
snowflake_connector = sdk_client.connectors.create(
    project_id=project.id,
    name="Snowflake Warehouse",
    db_type="snowflake",
    host=os.getenv("SNOWFLAKE_ACCOUNT"),
    port=443,
    username=os.getenv("SNOWFLAKE_USERNAME"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    config={
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "role": "ANALYST_ROLE"
    }
)
print(f"Connector ID: {snowflake_connector.id}")
```

### 5. Upload Data (Bulk)
```python
# Upload contexts
contexts = sdk_client.contexts.bulk_create(
    project_id=project.id,
    contexts=contexts_data
)

# Upload schema metadata
schemas = sdk_client.schema_metadata.bulk_create(
    project_id=project.id,
    schema_metadata_list=schema_data,
    validate=True
)

# Upload golden examples
examples = sdk_client.golden_examples.bulk_create(
    project_id=project.id,
    golden_examples=examples_data
)
```

### 6. Generate SQL
```python
# Create chat session
session = sdk_client.chat_sessions.create(project_id=project.id)

# Generate SQL only
sql_response = sdk_client.chat.chat_to_sql(
    project_id=project.id,
    chat_session_id=session.id,
    query="Your natural language query"
)

# Generate and execute SQL
answer_response = sdk_client.chat.chat_to_answer(
    project_id=project.id,
    chat_session_id=session.id,
    query="Your natural language query",
    connector_id=snowflake_connector.id
)
```

## 📋 Data Format Examples

### Schema Metadata (JSON)
```json
{
  "name": "customers",
  "description": "Customer information table",
  "schema_data": {
    "table": {
      "name": "customers",
      "columns": [
        {"name": "id", "type": "INTEGER", "description": "Primary key"},
        {"name": "name", "type": "VARCHAR(100)", "description": "Customer name"},
        {"name": "email", "type": "VARCHAR(255)", "description": "Email address"},
        {"name": "status", "type": "VARCHAR(32)", "description": "active, inactive, pending"}
      ]
    }
  }
}
```

### Context (JSON)
```json
{
  "name": "Business Rules",
  "content": "Active customers have status = 'active'. High-value customers have total_orders > 1000.",
  "is_always_displayed": true
}
```

### Golden Example (JSON)
```json
{
  "name": "Active Customer Count",
  "user_query": "How many active customers do we have?",
  "sql_query": "SELECT COUNT(*) FROM customers WHERE status = 'active';",
  "description": "Count of active customers",
  "is_always_displayed": true
}
```

## 🔍 Quick Diagnostics

### Test All Connections
```python
async def quick_test():
    # H2O Drive
    objects = await bucket.list_objects()
    print(f"H2O Drive: {len(objects)} objects")
    
    # Text2Everything
    projects = sdk_client.projects.list()
    print(f"T2E: {len(projects)} projects")
    
    # Snowflake (if configured)
    if snowflake_connector:
        ok = sdk_client.connectors.test_connection(snowflake_connector.id)
        print(f"Snowflake: {'✅' if ok else '❌'}")

await quick_test()
```

### Validate Environment
```python
required_vars = [
    "H2O_CLOUD_ENVIRONMENT", "H2O_CLOUD_CLIENT_PLATFORM_TOKEN",
    "TEXT2EVERYTHING_URL", "H2OGPTE_API_KEY"
]

missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f"❌ Missing: {missing}")
else:
    print("✅ All required variables set")
```

## 🎯 H2OGPTE UI Configuration

### CustomGPT Setup Checklist
- [ ] Navigate to `https://h2ogpte.your_domain_id.dedicated.h2o.ai/`
- [ ] Create Collection: "H2O Drive Analytics Collection"
- [ ] Create Custom Prompt: "H2O Drive SQL Assistant"
- [ ] Configure system prompt with business rules
- [ ] Set model to claude-3-7
- [ ] Attach prompt to collection
- [ ] Select tools: Python and Shell Scripting
- [ ] Test with sample queries

### Agent Environment Variables
```bash
# In H2OGPTE UI > Agents > Authentication tab
TEXT2EVERYTHING_URL = "http://text2everything.text2everything.svc.cluster.local:8000"
TEXT2EVERYTHING_PROJECT_ID = "<your_project_id>"
TEXT2EVERYTHING_CONNECTOR_ID = "<your_connector_id>"
T2E_ACCESS_TOKEN = "<your_access_token>"
```

## 🚨 Common Error Solutions

### H2O Drive Connection Failed
```python
# Check environment variables
print("Environment:", os.getenv('H2O_CLOUD_ENVIRONMENT'))
print("Token set:", bool(os.getenv('H2O_CLOUD_CLIENT_PLATFORM_TOKEN')))

# Test discovery
try:
    discovery = h2o_discovery.discover()
    print("✅ Discovery successful")
except Exception as e:
    print(f"❌ Discovery failed: {e}")
```

### Text2Everything Authentication Failed
```python
# Verify API key and URL
print("URL:", os.getenv('TEXT2EVERYTHING_URL'))
print("API Key set:", bool(os.getenv('H2OGPTE_API_KEY')))

# Test connection
try:
    test_client = Text2EverythingClient(
        base_url=os.getenv('TEXT2EVERYTHING_URL'),
        access_token=os.getenv('T2E_ACCESS_TOKEN'),
        workspace_name=os.getenv('T2E_WORKSPACE_NAME')
    )
    projects = test_client.projects.list()
    print(f"✅ Connected, {len(projects)} projects")
except Exception as e:
    print(f"❌ Failed: {e}")
```

### Data Upload Validation Errors
```python
# Use SDK's built-in validation method
table_schema = {
    "table": {
        "name": "customers",
        "columns": [{"name": "id", "type": "INTEGER"}]
    }
}

# Validate schema before upload
errors = sdk_client.schema_metadata.validate_schema(table_schema, "table")
if errors:
    print(f"❌ Validation errors: {errors}")
else:
    print("✅ Schema is valid")

# Validate dimension schema
dimension_schema = {
    "table": {
        "name": "customers",
        "dimension": {
            "name": "status",
            "content": {"type": "categorical", "values": ["active", "inactive"]}
        }
    }
}

errors = sdk_client.schema_metadata.validate_schema(dimension_schema, "dimension")
if errors:
    print(f"❌ Dimension errors: {errors}")
else:
    print("✅ Dimension valid")
```

## 📚 Useful Commands

### List Resources
```python
# List projects
projects = sdk_client.projects.list()
for p in projects:
    print(f"{p.name} (ID: {p.id})")

# List connectors
connectors = sdk_client.connectors.list(project.id)
for c in connectors:
    print(f"{c.name} ({c.db_type}) - ID: {c.id}")

# List contexts for project
contexts = sdk_client.contexts.list(project_id=project.id)
print(f"Found {len(contexts)} contexts")
```

### Batch Operations
```python
# Process in batches for large datasets
def batch_upload(items, batch_size=10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        # Upload batch
        result = sdk_client.contexts.bulk_create(
            project_id=project.id,
            contexts=batch
        )
        print(f"Batch {i//batch_size + 1}: {len(result)} uploaded")
```

## 🔗 Quick Links

- [Full Developer Guide](developer-starter-guide.md)
- [SDK Documentation](https://h2oai.github.io/text-2-everything-py/)
- [H2O Drive Docs](https://docs.h2o.ai/h2o-drive/)
- [Snowflake Connector Guide](guides/connectors.md)
- [Bulk Operations Guide](how-to/bulk_operations.md)

---

*Keep this reference handy for quick lookups during development! 📖*
