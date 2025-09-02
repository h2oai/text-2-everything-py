# H2O Drive to Text2Everything Integration

This script provides a streamlined way to transfer data from H2O Drive to the Text2Everything API using the official SDK.

## Features

- **Direct SDK integration**: Leverages built-in bulk operations and validation
- **Interactive project selection**: Choose source and destination projects easily
- **Comprehensive error handling**: Robust handling of connection, authentication, and validation issues
- **Multiple file format support**: JSON, text, and markdown files
- **Step-by-step workflow**: Clear progress tracking through each stage

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install h2o_drive text2everything_sdk
   ```

2. **Set environment variables**:
   ```bash
   export H2OGPTE_API_KEY="your-api-key"
   
   # Optional: Custom base URL
   export T2E_BASE_URL="https://your-t2e-instance.com"
   ```

3. **Prepare data in H2O Drive** with this structure:
   ```
   project_name/
   ├── schema_metadata/
   │   ├── schema1.json
   │   └── schema2.json
   ├── contexts/
   │   ├── context1.json
   │   ├── context2.txt
   │   └── context3.md
   └── golden_examples/
       ├── example1.json
       └── example2.json
   ```

## Usage

### Basic Usage

```bash
python drive_to_t2e_integration.py
```

The script will guide you through:
1. Connecting to H2O Drive
2. Initializing the Text2Everything SDK
3. Selecting a Text2Everything project (destination)
4. Selecting an H2O Drive project (source)
5. Loading data from Drive
6. Preparing data for the SDK
7. Uploading data using bulk operations
8. Displaying upload summary

### Interactive Selection

The script provides interactive menus for:
- **Text2Everything projects**: Choose the destination project for your data
- **H2O Drive projects**: Choose the source project containing your data

### Data Format Support

#### Contexts
- **JSON files**: Must contain `name` and `content` fields
- **Text files**: Content used directly, filename becomes the context name
- **Markdown files**: Content used directly, filename becomes the context name

#### Schema Metadata
- **JSON files**: Must contain `name` and `schema_data` fields

#### Golden Examples
- **JSON files**: Must contain `name`, `user_query`, and `sql_query` fields

## Workflow Example

```python
# The script handles this workflow automatically:

# 1. Connect to services
drive_manager = DriveManager(bucket)
sdk_client = Text2EverythingClient(base_url=BASE_URL, api_key=API_KEY)

# 2. Load and prepare data
project_data = await drive_manager.load_project_data(project_name)
sdk_ready_data = prepare_data_for_sdk(project_data)

# 3. Upload using SDK bulk operations
contexts = sdk_client.contexts.bulk_create(project_id, sdk_ready_data['contexts'])
schemas = sdk_client.schema_metadata.bulk_create(project_id, sdk_ready_data['schema_metadata'])
examples = sdk_client.golden_examples.bulk_create(project_id, sdk_ready_data['golden_examples'])
```

## Error Handling

The script includes comprehensive error handling for:
- **Connection issues**: H2O Drive and Text2Everything API connectivity
- **Authentication failures**: Invalid or missing API keys
- **Validation errors**: Malformed data or missing required fields
- **Rate limiting**: Automatic retry with backoff
- **File format issues**: Unsupported file types or encoding problems

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `H2OGPTE_API_KEY` | H2O GPT Enterprise API key | Required |
| `T2E_BASE_URL` | Text2Everything base URL | `http://text2everything.text2everything.svc.cluster.local:8000` |

### Optional Configuration

Copy `config_example.py` to `config.py` and customize:
- API timeouts and retry settings
- Data processing options
- Logging preferences

## Troubleshooting

### Common Issues

1. **"h2o_drive not installed"**
   ```bash
   pip install h2o_drive
   ```

2. **"text2everything_sdk not installed"**
   ```bash
   pip install ./text2everything_sdk-0.1.2-py3-none-any.whl
   ```

3. **"API key not found"**
   ```bash
   export H2OGPTE_API_KEY="your-api-key"
   ```

4. **"No projects found in Drive"**
   - Ensure your data follows the expected folder structure
   - Verify access to the H2O Drive bucket
   - Check that files are in the correct subdirectories

5. **"Validation errors during upload"**
   - Verify JSON files contain all required fields
   - Ensure text files use UTF-8 encoding
   - Check that file names are valid

### Data Structure Requirements

Your H2O Drive project must follow this structure:

```
your_project/
├── contexts/
│   ├── context1.json          # {"name": "...", "content": "..."}
│   ├── context2.txt           # Plain text content
│   └── context3.md            # Markdown content
├── schema_metadata/
│   ├── schema1.json           # {"name": "...", "schema_data": {...}}
│   └── schema2.json
└── golden_examples/
    ├── example1.json          # {"name": "...", "user_query": "...", "sql_query": "..."}
    └── example2.json
```

## Performance

The script is optimized for performance through:
- **Bulk operations**: Upload multiple items in single API calls
- **Efficient data loading**: Minimal memory usage with temporary files
- **Built-in retry logic**: Automatic handling of transient failures
- **Connection pooling**: Reuse connections for multiple requests

## Customization

You can extend the script by:
1. **Custom data preparation**: Modify `prepare_data_for_sdk()` for different formats
2. **Additional validation**: Add custom validation logic before upload
3. **Progress tracking**: Implement detailed progress bars or logging
4. **Batch processing**: Process multiple projects in sequence

## Support

For issues or questions:
- Check the troubleshooting section above
- Verify your data structure matches the requirements
- Ensure all dependencies are properly installed
- Confirm environment variables are set correctly
