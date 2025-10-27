# Text2Everything Developer & Data Scientist Starter Guide

A practical, step-by-step guide to get you from zero to a fully functional Text2Everything setup with H2O Drive integration, Snowflake connectivity, and CustomGPT configuration.

## Table of Contents

1. [Prerequisites & Setup](#prerequisites-setup)
2. [Step 1: Upload Data to H2O Drive](#step-1-upload-data-to-h2o-drive)
3. [Step 2: Configure Text2Everything API](#step-2-configure-text2everything-api)
4. [Step 3: Configure Snowflake Connector](#step-3-configure-snowflake-connector)
5. [Step 4: Configure CustomGPT](#step-4-configure-customgpt)
6. [Step 5: Setup Agent Environment](#step-5-setup-agent-environment)
7. [End-to-End Workflow Example](#end-to-end-workflow-example)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Setup

### Requirements
- Python 3.9+
- H2O Drive access with valid credentials
- Text2Everything API access
- Snowflake account (optional, for database connectivity)
- H2OGPTE UI access

### Installation

```bash
# Install required packages
pip install h2o-drive>=4.1.0
pip install text2everything_sdk-0.1.x-py3-none-any.whl
pip install python-dotenv
pip install tqdm
```

### Environment Setup

Create a `.env` file in your project root:

```bash
# H2O Drive Configuration
H2O_CLOUD_ENVIRONMENT=https://your-environment.h2o.ai/
H2O_CLOUD_CLIENT_PLATFORM_TOKEN=your-h2o-token-here

# Text2Everything Configuration
TEXT2EVERYTHING_URL=http://text2everything.text2everything.svc.cluster.local:8000
T2E_ACCESS_TOKEN=your-access-token-here
T2E_WORKSPACE_NAME=workspaces/your-workspace

# Snowflake Configuration (optional)
SNOWFLAKE_ACCOUNT=your-account.snowflakecomputing.com
SNOWFLAKE_USERNAME=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=PUBLIC
```

---

## Step 1: Upload Data to H2O Drive

### 1.1 Connect to H2O Drive

```python
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple

# H2O Drive imports
import h2o_drive
import h2o_discovery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to H2O Drive
print("🔌 Connecting to H2O Drive...")

try:
    # Discover H2O services
    discovery = h2o_discovery.discover()
    
    # Connect to Drive
    drive_client = h2o_drive.connect(discovery=discovery)
    bucket = drive_client.user_bucket()
    
    print("✅ Connected to H2O Drive successfully!")
    
    # Test connection
    objects = await bucket.list_objects()
    print(f"📁 Found {len(objects)} objects in your Drive")
    
except Exception as e:
    print(f"❌ Failed to connect to H2O Drive: {e}")
    print("Please check your H2O_CLOUD_ENVIRONMENT and H2O_CLOUD_CLIENT_PLATFORM_TOKEN")
    raise
```

### 1.2 Prepare Your Data Structure

Organize your local data in the following structure:

```
your_project_data/
├── schema_metadata/     # JSON files with table schemas
├── contexts/           # JSON and TXT files with business context
└── golden_examples/    # JSON files with query-SQL examples
```

### 1.3 Load and Upload Data

```python
def load_local_project_data(project_path: Path) -> Dict[str, List[Tuple[str, Any]]]:
    """Load project data from local filesystem."""
    project_data = {
        "schema_metadata": [],
        "contexts": [],
        "golden_examples": []
    }
    
    # Load schema metadata
    schema_path = project_path / "schema_metadata"
    if schema_path.exists():
        for json_file in schema_path.glob("**/*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["schema_metadata"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
    
    # Load contexts (JSON and TXT files)
    contexts_path = project_path / "contexts"
    if contexts_path.exists():
        # JSON files
        for json_file in contexts_path.glob("**/*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["contexts"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
        
        # Text files
        for txt_file in contexts_path.glob("**/*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    data = f.read()
                    project_data["contexts"].append((str(txt_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {txt_file}: {e}")
    
    # Load golden examples
    examples_path = project_path / "golden_examples"
    if examples_path.exists():
        for json_file in examples_path.glob("**/*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["golden_examples"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
    
    return project_data

# Load your data
local_data_path = Path("path/to/your/data")  # Update this path
project_data = load_local_project_data(local_data_path)

print(f"📊 Loaded {sum(len(files) for files in project_data.values())} total files")
```

### 1.4 Upload to H2O Drive

```python
import tempfile

async def upload_data_to_drive(bucket, project_data: Dict[str, List[Tuple[str, Any]]], project_name: str = "my_project"):
    """Upload project data to H2O Drive with organized structure."""
    upload_results = {
        "schema_metadata": {"success": 0, "failed": 0, "errors": []},
        "contexts": {"success": 0, "failed": 0, "errors": []},
        "golden_examples": {"success": 0, "failed": 0, "errors": []}
    }
    
    for data_type, files in project_data.items():
        if not files:
            continue
            
        print(f"📤 Uploading {len(files)} {data_type} files...")
        
        for file_path, data in files:
            filename = Path(file_path).name
            drive_key = f"{project_name}/{data_type}/{filename}"
            
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as tmp_file:
                    if isinstance(data, str):
                        tmp_file.write(data)
                    else:
                        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
                    temp_path = tmp_file.name
                
                # Upload to Drive
                await bucket.upload_file(temp_path, drive_key)
                
                # Clean up temp file
                os.remove(temp_path)
                
                upload_results[data_type]["success"] += 1
                print(f"  ✅ Uploaded {filename}")
                
            except Exception as e:
                upload_results[data_type]["failed"] += 1
                upload_results[data_type]["errors"].append(f"{filename}: {str(e)}")
                print(f"  ❌ Failed to upload {filename}: {e}")
                
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
    
    return upload_results

# Upload the data
project_name = "home/my_uploaded_project"  # Keep the 'home/' prefix
upload_results = await upload_data_to_drive(bucket, project_data, project_name)

# Display results
total_success = sum(r["success"] for r in upload_results.values())
total_failed = sum(r["failed"] for r in upload_results.values())
print(f"📈 Upload complete: {total_success} successful, {total_failed} failed")
```

---

## Step 2: Configure Text2Everything API

### 2.1 Initialize the SDK Client

```python
from text2everything_sdk import Text2EverythingClient
from text2everything_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError
)

# Initialize Text2Everything SDK
print("🔌 Initializing Text2Everything SDK...")

try:
    sdk_client = Text2EverythingClient(
        access_token=os.getenv("T2E_ACCESS_TOKEN"),
        workspace_name=os.getenv("T2E_WORKSPACE_NAME"),
        base_url=os.getenv("TEXT2EVERYTHING_URL"),
        timeout=200,
        max_retries=1
    )
    print("✅ Text2Everything SDK initialized successfully")
except Exception as e:
    print(f"❌ SDK initialization failed: {e}")
    raise
```

### 2.2 Create or Select a Project

```python
# List existing projects
t2e_projects = sdk_client.projects.list()
print(f"📋 Found {len(t2e_projects)} existing projects")

# Option 1: Create a new project
project = sdk_client.projects.create(
    name="H2O Drive Integration Project",
    description="Project created for H2O Drive to Text2Everything integration"
)
print(f"✅ Created project: {project.name} (ID: {project.id})")

# Option 2: Use existing project
# project = t2e_projects[0]  # Select first existing project
```

### 2.3 Load Data from H2O Drive

```python
# Import the integration helper (assuming you have the drive_to_t2e_integration.py file)
from drive_integration.drive_to_t2e_integration import DriveManager, prepare_data_for_sdk

# Create Drive manager
drive_manager = DriveManager(bucket)

# Load project data from H2O Drive
selected_drive_project = "home/my_uploaded_project"  # Your uploaded project name
project_data = await drive_manager.load_project_data(selected_drive_project)

print(f"📥 Loaded data from H2O Drive:")
for data_type, files in project_data.items():
    print(f"   - {data_type}: {len(files)} files")
```

### 2.4 Prepare and Upload Data to Text2Everything

```python
# Prepare data for SDK
sdk_ready_data = prepare_data_for_sdk(project_data)

print("🔧 Data prepared for Text2Everything:")
for data_type, items in sdk_ready_data.items():
    print(f"   - {data_type}: {len(items)} items")

# Upload data using bulk operations
upload_results = {}

try:
    # Upload contexts
    if sdk_ready_data.get('contexts'):
        print(f"📤 Uploading {len(sdk_ready_data['contexts'])} contexts...")
        contexts = sdk_client.contexts.bulk_create(
            project_id=project.id,
            contexts=sdk_ready_data['contexts']
        )
        upload_results['contexts'] = len(contexts)
        print(f"   ✅ {len(contexts)} contexts uploaded")

    # Upload schema metadata
    if sdk_ready_data.get('schema_metadata'):
        print(f"📤 Uploading {len(sdk_ready_data['schema_metadata'])} schema metadata items...")
        schemas = sdk_client.schema_metadata.bulk_create(
            project_id=project.id,
            schema_metadata_list=sdk_ready_data['schema_metadata'],
            validate=True
        )
        upload_results['schema_metadata'] = len(schemas)
        print(f"   ✅ {len(schemas)} schema metadata items uploaded")

    # Upload golden examples
    if sdk_ready_data.get('golden_examples'):
        print(f"📤 Uploading {len(sdk_ready_data['golden_examples'])} golden examples...")
        examples = sdk_client.golden_examples.bulk_create(
            project_id=project.id,
            golden_examples=sdk_ready_data['golden_examples']
        )
        upload_results['golden_examples'] = len(examples)
        print(f"   ✅ {len(examples)} golden examples uploaded")

    print("🎉 All data uploaded successfully to Text2Everything!")

except Exception as e:
    print(f"❌ Upload failed: {e}")
    raise
```

---

## Step 3: Configure Snowflake Connector

### 3.1 Snowflake Configuration

```python
# Snowflake connection configuration
SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    "username": os.getenv("SNOWFLAKE_USERNAME"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "role": "ANALYST_ROLE"  # Optional: adjust as needed
}

print("📋 Snowflake Configuration:")
print(f"   Account: {SNOWFLAKE_CONFIG['account']}")
print(f"   Database: {SNOWFLAKE_CONFIG['database']}")
print(f"   Warehouse: {SNOWFLAKE_CONFIG['warehouse']}")
```

### 3.2 Create Snowflake Connector

```python
# Create Snowflake connector
print("🔌 Creating Snowflake connector...")

try:
    snowflake_connector = sdk_client.connectors.create(
        name="H2O Drive Analytics Warehouse",
        description="Snowflake data warehouse for H2O Drive analytics and processed data",
        db_type="snowflake",
        host=SNOWFLAKE_CONFIG["account"],
        port=443,  # Snowflake standard HTTPS port
        username=SNOWFLAKE_CONFIG["username"],
        password=SNOWFLAKE_CONFIG["password"],
        database=SNOWFLAKE_CONFIG["database"],
        config={
            "warehouse": SNOWFLAKE_CONFIG["warehouse"],
            "role": SNOWFLAKE_CONFIG.get("role")
        }
    )
    
    print("✅ Snowflake connector created successfully!")
    print(f"   Connector ID: {snowflake_connector.id}")
    print(f"   Name: {snowflake_connector.name}")
    
    # Test the connection
    connection_ok = sdk_client.connectors.test_connection(snowflake_connector.id)
    if connection_ok:
        print("✅ Snowflake connection test successful!")
    else:
        print("⚠️ Snowflake connection test failed")
    
except Exception as e:
    print(f"❌ Failed to create Snowflake connector: {e}")
    snowflake_connector = None
```

### 3.3 List and Manage Connectors

```python
# List all connectors
all_connectors = sdk_client.connectors.list()
snowflake_connectors = [c for c in all_connectors if c.db_type.lower() == "snowflake"]

print(f"📋 Found {len(snowflake_connectors)} Snowflake connector(s):")
for connector in snowflake_connectors:
    print(f"   • {connector.name} (ID: {connector.id})")
    print(f"     Database: {connector.database}")
    print(f"     Host: {connector.host}")

# Store connector ID for future use
if snowflake_connector:
    SNOWFLAKE_CONNECTOR_ID = snowflake_connector.id
    print(f"💾 Snowflake Connector ID: {SNOWFLAKE_CONNECTOR_ID}")
```

---

## Step 4: Configure CustomGPT

### 4.1 Access H2OGPTE UI

1. Navigate to: `https://h2ogpte.you_domain_id.dedicated.h2o.ai/`
2. Log in with your credentials

### 4.2 Create a Collection

1. **Go to Collections**:
   - Click on "Collections" in the main navigation
   - Click "Create Collection" or "+" button

2. **Configure Collection Settings**:
   ```
   Collection Name: H2O Analytics Collection
   Description: Collection for H2O data analysis and SQL generation
   ```

### 4.3 Create Custom Prompt

1. **Navigate to Prompts**:
   - Go to "Prompts" section
   - Click "Create Prompt" or "+" button

2. **Configure Custom Prompt**:
   ```
    You will use:
    base_url = os.getenv("TEXT2EVERYTHING_URL") 
    project_id = os.getenv("TEXT2EVERYTHING_PROJECT_ID")  
    connector_id = os.getenv("TEXT2EVERYTHING_CONNECTOR_ID")  
    access_token = os.getenv("T2E_ACCESS_TOKEN")  

   Prompt Name: H2O Drive SQL Assistant
   
   System Prompt:
   As h2oGPTe, you are an AI system expert in answering questions created by H2O.ai. Your primary function is to answer questions using the Text2Everything API always first in order to gather the data.

   ### Communication Guidelines

    - **Audience**: You are speaking to C-level executives and business users
    - **Style**: Clear, concise, business language, to the point
    - **Length**: Be brief
    - **Recommendations**: Only provide recommendations if specifically asked
    - **Technical details**: Omit technical information or terms
    - **File references**: Do not mention generated files in your response
    - **Visualizations**: Include graphs when they provide greater clarity
    - **Content**: Never create synthetic data, only provide analysis from the resulting query of the Text2Everything API
   

    ## API Configuration

    ### Environment Variables
    ```python
    base_url = os.getenv("TEXT2EVERYTHING_URL") # Already set up
    project_id = os.getenv("TEXT2EVERYTHING_PROJECT_ID")  # Already set up
    connector_id = os.getenv("TEXT2EVERYTHING_CONNECTOR_ID")  # Already set up
    access_token = os.getenv("T2E_ACCESS_TOKEN")  # Already set up
    ```

    ### Headers
    ```python
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Workspace-Name": os.getenv("T2E_WORKSPACE_NAME", "")
    }
    ```

   ...
   ...
   ...

   ### Formulate Business-Oriented Response

    When formulating your response:

    1. **Start with the key insight**: Begin with the most important finding
    2. **Use business terminology**: Translate technical database terms to business language
    3. **Be concise**: Keep explanations brief and to the point
    4. **Include visuals**: Reference any generated visualizations if they add clarity
    5. **Avoid technical details**: Don't mention API calls, SQL queries, or data processing steps
   ```

### 4.4 Configure Tools and Settings

1. **Enable Tools**:
   - Enable "Python" for enabling programming
   - Enable "Shell scripting" if needed for internal reasoning

2. **Model Settings and agentic settings**:
   ```
   Model: claude-3.7 (recommended for higher agentic accuracy)
   Agent accuracy: 'basic' (around 10 reasoning iterations)
   Max Agent Turn Time: 180 (to enable enough time for the API to respond)
   ```

3. **Collection Integration**:
   - Attach your created collection to the prompt
   - Apply current settings as collections defaults

---

## Step 5: Setup Agent Environment

### 5.1 Access Agent Configuration

1. **Navigate to Agents Section**:
   - Go to the H2OGPTE UI
   - Click on "Agents" in the main navigation
   - Select your agent or create a new one

### 5.2 Configure Authentication

1. **Go to Authentication Tab**:
   - Click on the "Authentication" tab in the agent settings

2. **Add Keys (Environment Variables)**:
   ```bash
   # Text2Everything Configuration
   TEXT2EVERYTHING_URL = "http://text2everything.text2everything.svc.cluster.local:8000"
   TEXT2EVERYTHING_PROJECT_ID = "<your_project_id>"
   TEXT2EVERYTHING_CONNECTOR_ID = "<your_connector_id>"
   
   # H2OGPTE API Configuration
   T2E_ACCESS_TOKEN = "<your_access_token>"
   ```

3. **Replace Placeholder Values**:
   The values here correspond to the ids generated when interacting with the T2E SDK.

### 5.3 Test the CustomGPT

Now that the agent environment is configured, you can test the CustomGPT:

1. **Create a Test Chat**:
   - Go to collections, and find the `H2O Analytics Collection` collection
   - Click on `+ New Chat`
   - Test with sample queries like:
     ```
     "Show me the top 10 customers by revenue"
     "What are the monthly sales trends?"
     "Find customers who haven't placed orders in the last 90 days"
     ```

2. **Validate Results**:
   - Check that the CustomGPT can access the Text2Everything API
   - Verify that response is correct.
   - Ensure business rules are applied correctly
   - Confirm that results are presented in business-friendly language

---

## End-to-End Workflow Example

### Complete Integration Test

```python
async def end_to_end_workflow_test():
    """Complete end-to-end workflow test."""
    
    print("🚀 Starting end-to-end workflow test...")
    
    # 1. Verify H2O Drive connection
    print("\n1️⃣ Testing H2O Drive connection...")
    objects = await bucket.list_objects()
    print(f"   ✅ H2O Drive: {len(objects)} objects accessible")
    
    # 2. Verify Text2Everything connection
    print("\n2️⃣ Testing Text2Everything connection...")
    projects = sdk_client.projects.list()
    print(f"   ✅ Text2Everything: {len(projects)} projects accessible")
    
    # 3. Test Snowflake connector (if available)
    if snowflake_connector:
        print("\n3️⃣ Testing Snowflake connector...")
        connection_ok = sdk_client.connectors.test_connection(snowflake_connector.id)
        print(f"   ✅ Snowflake: Connection {'successful' if connection_ok else 'failed'}")
    
    # 4. Test SQL generation
    print("\n4️⃣ Testing SQL generation...")
    try:
        # Create a chat session
        session = sdk_client.chat_sessions.create(project_id=project.id)
        
        # Generate SQL
        response = sdk_client.chat.chat_to_sql(
            project_id=project.id,
            chat_session_id=session.id,
            query="Show me a count of all records in the main table"
        )
        
        print(f"   ✅ Generated SQL: {response.sql_query[:100]}...")
        
    except Exception as e:
        print(f"   ❌ SQL generation failed: {e}")
    
    # 5. Test with Snowflake execution (if connector available)
    if snowflake_connector:
        print("\n5️⃣ Testing SQL execution with Snowflake...")
        try:
            answer_response = sdk_client.chat.chat_to_answer(
                project_id=project.id,
                chat_session_id=session.id,
                query="Count the total number of records",
                connector_id=snowflake_connector.id
            )
            print(f"   ✅ Query executed successfully")
            print(f"   📊 Result: {answer_response.answer[:200]}...")
            
        except Exception as e:
            print(f"   ⚠️ SQL execution test skipped: {e}")
    
    print("\n🎉 End-to-end workflow test complete!")

# Run the test
await end_to_end_workflow_test()
```

### Production Usage Example

```python
def production_query_example():
    """Example of production usage."""
    
    # Create a new chat session for production use
    session = sdk_client.chat_sessions.create(project_id=project.id)
    
    # Example business queries
    business_queries = [
        "What are our top 10 customers by total revenue?",
        "Show me monthly sales trends for the last 12 months",
        "Find customers who haven't placed orders in the last 90 days",
        "What's the average order value by customer segment?"
    ]
    
    print("📊 Production Query Examples:")
    
    for i, query in enumerate(business_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        try:
            # Generate SQL
            sql_response = sdk_client.chat.chat_to_sql(
                project_id=project.id,
                chat_session_id=session.id,
                query=query
            )
            
            print(f"   Generated SQL: {sql_response.sql_query}")
            
            # Execute if Snowflake connector is available
            if snowflake_connector:
                answer_response = sdk_client.chat.chat_to_answer(
                    project_id=project.id,
                    chat_session_id=session.id,
                    query=query,
                    connector_id=snowflake_connector.id
                )
                print(f"   Result: {answer_response.answer[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

# Run production examples
production_query_example()
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. H2O Drive Connection Issues

**Problem**: `Failed to connect to H2O Drive`
```python
# Solution: Verify environment variables
print("H2O Environment:", os.getenv('H2O_CLOUD_ENVIRONMENT'))
print("H2O Token:", os.getenv('H2O_CLOUD_CLIENT_PLATFORM_TOKEN')[:10] + "..." if os.getenv('H2O_CLOUD_CLIENT_PLATFORM_TOKEN') else "Not set")

# Check token validity
try:
    discovery = h2o_discovery.discover()
    print("✅ H2O Discovery successful")
except Exception as e:
    print(f"❌ H2O Discovery failed: {e}")
```

#### 2. Text2Everything API Issues

**Problem**: `Authentication failed`
```python
# Solution: Verify access token and URL
print("T2E URL:", os.getenv('TEXT2EVERYTHING_URL'))
print("Access Token:", os.getenv('T2E_ACCESS_TOKEN')[:10] + "..." if os.getenv('T2E_ACCESS_TOKEN') else "Not set")
print("Workspace:", os.getenv('T2E_WORKSPACE_NAME'))

# Test basic connection
try:
    test_client = Text2EverythingClient(
        access_token=os.getenv('T2E_ACCESS_TOKEN'),
        workspace_name=os.getenv('T2E_WORKSPACE_NAME'),
        base_url=os.getenv('TEXT2EVERYTHING_URL')
    )
    projects = test_client.projects.list()
    print(f"✅ API connection successful, {len(projects)} projects found")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

#### 3. Snowflake Connector Issues

**Problem**: `Snowflake connection test failed`
```python
# Solution: Verify Snowflake credentials
def debug_snowflake_connection():
    print("Snowflake Debug Info:")
    print(f"   Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print(f"   Username: {os.getenv('SNOWFLAKE_USERNAME')}")
    print(f"   Database: {os.getenv('SNOWFLAKE_DATABASE')}")
    print(f"   Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE')}")
    
    # Test with minimal connection
    try:
        import snowflake.connector
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USERNAME'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE')
        )
        print("✅ Direct Snowflake connection successful")
        conn.close()
    except Exception as e:
        print(f"❌ Direct Snowflake connection failed: {e}")

debug_snowflake_connection()
```

#### 4. Data Upload Issues

**Problem**: `Validation error during bulk upload`

**Solution**: Use the SDK's built-in `validate_schema` method to check schema metadata before upload.

```python
# Validate table schema
table_schema = {
    "table": {
        "name": "customers",
        "columns": [{"name": "id", "type": "INTEGER"}]
    }
}

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
            "content": {
                "type": "categorical",
                "values": ["active", "inactive"]
            }
        }
    }
}

errors = sdk_client.schema_metadata.validate_schema(dimension_schema, "dimension")
if errors:
    print(f"❌ Dimension validation errors: {errors}")
else:
    print("✅ Dimension schema is valid")

# Validate metric schema
metric_schema = {
    "table": {
        "name": "orders",
        "metric": {
            "name": "total_revenue",
            "content": {
                "aggregation": "sum",
                "column": "amount"
            }
        }
    }
}

errors = sdk_client.schema_metadata.validate_schema(metric_schema, "metric")
if errors:
    print(f"❌ Metric validation errors: {errors}")
else:
    print("✅ Metric schema is valid")
```

#### 5. Performance Optimization

**Problem**: Slow upload or query performance
```python
# Solution: Implement batch processing and connection pooling
async def optimized_upload(sdk_client, project_id, data, batch_size=10):
    """Upload data in optimized batches."""
    
    for data_type, items in data.items():
        if not items:
            continue
            
        print(f"📤 Uploading {len(items)} {data_type} in batches of {batch_size}")
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            
            try:
                if data_type == 'contexts':
                    result = sdk_client.contexts.bulk_create(
                        project_id=project_id,
                        contexts=batch
                    )
                elif data_type == 'schema_metadata':
                    result = sdk_client.schema_metadata.bulk_create(
                        project_id=project_id,
                        schema_metadata_list=batch
                    )
                elif data_type == 'golden_examples':
                    result = sdk_client.golden_examples.bulk_create(
                        project_id=project_id,
                        golden_examples=batch
                    )
                
                print(f"   ✅ Batch {i//batch_size + 1}: {len(result)} items uploaded")
                
            except Exception as e:
                print(f"   ❌ Batch {i//batch_size + 1} failed: {e}")

# Use optimized upload
# await optimized_upload(sdk_client, project.id, sdk_ready_data)
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Enable verbose logging in your environment
2. **Verify credentials**: Ensure all API keys and tokens are valid
3. **Test connections**: Use the diagnostic functions provided above
4. **Check documentation**: Refer to the [Text2Everything SDK documentation](https://h2oai.github.io/text-2-everything-py/)
5. **Contact support**: Email support@h2o.ai with detailed error messages

## Next Steps

After completing this guide, you should have:

1. ✅ **Data in H2O Drive**: Your project data organized and uploaded
2. ✅ **Text2Everything Project**: Configured with contexts, schemas, and examples
3. ✅ **Snowflake Connector**: Database connectivity for SQL execution
4. ✅ **CustomGPT Setup**: AI assistant configured for your data
5. ✅ **Agent Environment**: Production-ready environment variables

### Recommended Next Actions

1. **Expand Your Data**: Add more contexts, schemas, and golden examples
2. **Optimize Performance**: Change context, schemas, golden examples and feedback limits
3. **Train Your Team**: Share this guide with your development team
4. **Iterate and Improve**: Continuously refine your prompts and examples. Add feedback whenever possible.

### Additional Resources

- [Text2Everything SDK Documentation](https://h2oai.github.io/text-2-everything-py/)
- [H2O Drive Documentation](https://docs.h2o.ai/h2o-drive/)
- [Snowflake Connector Guide](../guides/connectors.md)
- [Bulk Operations Guide](../how-to/bulk_operations.md)
- [Jupyter Integration Guide](../how-to/jupyter.md)

---

**Happy coding! 🚀**

*This guide was created to help developers and data scientists quickly get started with the Text2Everything ecosystem. For questions or improvements, please reach out to the H2O.ai team.*
