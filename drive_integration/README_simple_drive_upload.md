# Simple H2O Drive Upload Script

This Python script is a standalone version of the `Simple_Drive_Upload.ipynb` Jupyter notebook, converted for command-line usage and automation.

## Overview

The script demonstrates how to upload local data files to H2O Drive using a simple, direct approach. It provides:

- Direct connection to H2O Drive
- Loading of local project data from filesystem
- Upload of files to Drive with organized structure
- Verification of uploads and listing of Drive contents
- Progress tracking and detailed reporting

## Features

- **Command-line interface** - Easy to use from terminal or scripts
- **Environment configuration** - Supports `.env` files for secure credential management
- **Comprehensive error handling** - Detailed error messages and validation
- **Progress tracking** - Real-time upload progress and results
- **Verification** - Automatic verification of uploaded files
- **Organized structure** - Maintains proper folder structure in Drive

## Installation

1. Install required dependencies:
```bash
pip install h2o-cloud-discovery
pip install 'h2o-drive>=4'
pip install python-dotenv
```

Or use the requirements file:
```bash
pip install -r requirements_drive_integration.txt
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
export H2O_CLOUD_ENVIRONMENT="https://your-environment.h2o.ai/"
export H2O_CLOUD_CLIENT_PLATFORM_TOKEN="your-token-here"
```

### Environment File (Recommended)

Create a `.env.upload` file in the project directory:

```
H2O_CLOUD_ENVIRONMENT=https://your-environment.h2o.ai/
H2O_CLOUD_CLIENT_PLATFORM_TOKEN=your-token-here
```

## Usage

### Basic Usage

```bash
python simple_drive_upload.py --project-path "JSON - tests" --project-name "my_uploaded_project"
```

### With Custom Environment File

```bash
python simple_drive_upload.py --project-path "data" --project-name "my_project" --env-file ".env.upload"
```

### Command-line Options

- `--project-path` (required): Path to the local project directory containing data to upload
- `--project-name` (required): Name of the project in H2O Drive (will be prefixed with 'home/' if not already)
- `--env-file` (optional): Path to environment file (default: .env.upload)

## Expected Directory Structure

The script expects your local project data to be organized as follows:

```
project_path/
├── schema_metadata/     # JSON files containing schema metadata
├── contexts/           # JSON and TXT files containing context data
└── golden_examples/    # JSON files containing golden examples
```

## Output Structure in H2O Drive

Files will be uploaded to H2O Drive with the following structure:

```
home/your_project_name/
├── schema_metadata/
│   ├── file1.json
│   └── file2.json
├── contexts/
│   ├── context1.json
│   ├── context2.txt
│   └── context3.json
└── golden_examples/
    ├── example1.json
    └── example2.json
```

## Example Output

```
🚀 Simple H2O Drive Upload
==================================================
🔧 Setting up environment...
✅ Loaded environment from .env.upload
✅ Environment: https://your-environment.h2o.ai/
✅ Token: ****abcd
🔌 Connecting to H2O Drive...
✅ Connected to H2O Drive successfully!
📁 Found 15 objects in your Drive
📥 Loading project data from: JSON - tests
📄 Found 3 schema metadata files
📄 Found 5 context files (3 JSON, 2 TXT)
📄 Found 2 golden example files

📊 Loaded Project Data Summary:
  - schema_metadata: 3 files
    • schema1.json
    • schema2.json
    • schema3.json
  - contexts: 5 files
    • context1.json
    • context2.txt
    • context3.json
  - golden_examples: 2 files
    • example1.json
    • example2.json

✅ Total files loaded: 10
🚀 Starting upload to H2O Drive...
📁 Project name: home/my_uploaded_project

📤 Uploading 3 schema_metadata files...
  ✅ Uploaded schema1.json
  ✅ Uploaded schema2.json
  ✅ Uploaded schema3.json

📤 Uploading 5 contexts files...
  ✅ Uploaded context1.json
  ✅ Uploaded context2.txt
  ✅ Uploaded context3.json

📤 Uploading 2 golden_examples files...
  ✅ Uploaded example1.json
  ✅ Uploaded example2.json

🔍 Verifying uploads in H2O Drive...

📁 Found 10 files for project 'home/my_uploaded_project':

  📂 schema_metadata: 3 files
    • schema1.json
    • schema2.json
    • schema3.json

  📂 contexts: 5 files
    • context1.json
    • context2.txt
    • context3.json

  📂 golden_examples: 2 files
    • example1.json
    • example2.json

📋 Upload Session Summary:
========================================
📊 Files processed: 10
✅ Successfully uploaded: 10
❌ Failed uploads: 0
📈 Success rate: 100.0%
📁 Project name in Drive: home/my_uploaded_project

📊 Upload Results by Type:
------------------------------
✅ schema_metadata: 3 successful, 0 failed
✅ contexts: 5 successful, 0 failed
✅ golden_examples: 2 successful, 0 failed

🎉 Simple Drive Upload Complete!

📚 What was accomplished:
   • Connected directly to H2O Drive
   • Loaded local project data
   • Uploaded files with organized structure
   • Verified uploads in Drive
   • Provided progress tracking

🎉 All operations completed successfully!
```

## Error Handling

The script provides comprehensive error handling for common issues:

- **Missing environment variables**: Clear instructions on how to set them
- **Connection failures**: Detailed error messages for H2O Drive connection issues
- **File not found**: Validation of project path and file existence
- **Upload failures**: Individual file upload error tracking
- **Verification issues**: Checks to ensure files were uploaded correctly

## Exit Codes

- `0`: All operations completed successfully
- `1`: Upload completed with some issues or verification failed
- `1`: Upload failed completely or configuration error

## Differences from Jupyter Notebook

This script provides several improvements over the original notebook:

1. **Command-line interface** - No need for Jupyter environment
2. **Better error handling** - Comprehensive exception handling and validation
3. **Argument parsing** - Flexible command-line arguments
4. **Environment management** - Secure credential handling with .env files
5. **Exit codes** - Proper exit codes for automation and scripting
6. **Logging** - Structured output with progress indicators
7. **Validation** - Input validation and file existence checks
8. **Cleanup** - Proper resource cleanup and temporary file management

## Integration

This script can be easily integrated into:

- **CI/CD pipelines** - Automated data uploads
- **Data workflows** - Part of larger data processing pipelines
- **Batch operations** - Upload multiple projects programmatically
- **Scheduled tasks** - Regular data synchronization

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all required packages are installed
2. **Authentication failures**: Check environment variables and tokens
3. **Connection timeouts**: Verify network connectivity and H2O Cloud environment URL
4. **File permission errors**: Ensure read access to local files and write access to temp directory
5. **Empty uploads**: Verify directory structure matches expected format

### Debug Mode

For debugging, you can modify the script to add more verbose logging or run with Python's verbose flag:

```bash
python -v simple_drive_upload.py --project-path "data" --project-name "test"
```

## Related Files

- `Simple_Drive_Upload.ipynb` - Original Jupyter notebook
- `drive_to_t2e_integration.py` - Integration script for Text2Everything
- `requirements_drive_integration.txt` - Required dependencies
