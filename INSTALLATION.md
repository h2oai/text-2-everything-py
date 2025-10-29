# Text2Everything SDK Installation Guide

This guide covers different ways to install and use the Text2Everything SDK.

## Installation from PyPI (Recommended)

The SDK is published to PyPI and can be installed with pip:

```bash
# Install the latest version
pip install h2o-text-2-everything

# Install with optional dependencies
pip install h2o-text-2-everything[integrations]  # pandas, jupyter, h2o-drive
pip install h2o-text-2-everything[dev]          # development tools
pip install h2o-text-2-everything[docs]         # documentation tools

# Install a specific version
pip install h2o-text-2-everything==0.1.7rc3
```

This is the recommended installation method for most users.

## Quick Start After Installation

Once installed, you can use the SDK:

```python
from text2everything_sdk import Text2EverythingClient

# Initialize client
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    access_token="your-access-token",
    workspace_name="workspaces/my-workspace"
)

# Create a project
project = client.projects.create(name="My Project")
print(f"Created project: {project.id}")
```

## Development Installation

For contributing to the SDK or local development:

```bash
# Clone the repository
git clone https://github.com/h2oai/text-2-everything.git
cd text-2-everything/text2everything_sdk

# Install in development mode with all dependencies
pip install -e ".[dev,integrations,docs]"
```

Or install from a local wheel file:

```bash
pip install dist/h2o_text_2_everything-0.1.2-py3-none-any.whl
```

## Publishing to PyPI (For Maintainers)

The SDK is published to PyPI using GitHub Actions. To publish manually:

### Prerequisites

1. **Create PyPI Account**: Register at [pypi.org](https://pypi.org/account/register/)
2. **Install Publishing Tools**:
   ```bash
   pip install build twine
   ```

### Publishing Steps

1. **Prepare for Publishing**:
   ```bash
   cd text2everything_sdk
   
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info/
   
   # Update version in setup.py if needed
   # Ensure README.md and requirements.txt are up to date
   ```

2. **Build the Package**:
   ```bash
   python -m build
   ```

3. **Test Upload to TestPyPI** (recommended first):
   ```bash
   # Upload to TestPyPI first
   python -m twine upload --repository testpypi dist/*
   
   # Test installation from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ h2o-text-2-everything
   ```

4. **Upload to Production PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

5. **Verify Installation**:
   ```bash
   pip install h2o-text-2-everything
   ```

### PyPI Configuration

Create a `.pypirc` file in your home directory for authentication:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Environment Setup

### Using .env Files

Create a `.env` file in your project root:

```bash
# .env file
T2E_BASE_URL=https://your-api-endpoint.com
T2E_ACCESS_TOKEN=your-access-token
T2E_WORKSPACE_NAME=workspaces/my-workspace
```

The SDK will automatically load these variables when running tests.

### Environment Variables

Alternatively, set environment variables:

```bash
export T2E_BASE_URL="https://your-api-endpoint.com"
export T2E_ACCESS_TOKEN="your-access-token"
export T2E_WORKSPACE_NAME="workspaces/my-workspace"
```

## Development Setup

For contributing to the SDK:

```bash
# Clone the repository
git clone https://github.com/h2oai/text-2-everything.git
cd text-2-everything/text2everything_sdk

# Install in development mode with all dependencies
pip install -e ".[dev,integrations,docs]"

# Run tests
python run_tests.py

# Or use pytest directly
pytest

# Format code
black .
isort .

# Type checking
mypy text2everything_sdk/
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the right directory and the package is installed
2. **Authentication Errors**: Verify your API key and base URL are correct
3. **Connection Errors**: Check your network connection and API endpoint

### Getting Help

- **Documentation**: Check the README.md for API reference
- **Examples**: See the `examples/` directory for usage examples
- **Issues**: Report bugs at [GitHub Issues](https://github.com/h2oai/text-2-everything/issues)

## Version History

- **v0.1.2**: Current version with custom tools, nested validation, and .env support
- **v0.1.1**: Enhanced multipart file upload support
- **v0.1.0**: Initial release with core functionality

## Next Steps

1. **For Users**: Install from PyPI with `pip install h2o-text-2-everything`
2. **For Contributors**: Use development installation with all dependencies
3. **For Maintainers**: Follow the publishing guide above
