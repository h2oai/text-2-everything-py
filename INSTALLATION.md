# Text2Everything SDK Installation Guide

This guide covers different ways to install and use the Text2Everything SDK.

## Installation Options

### Option 1: Local Development Installation (Recommended for now)

Since the SDK is not yet published to PyPI, you can install it locally:

```bash
# Navigate to the SDK directory
cd text2everything_sdk

# Install in development mode (editable install)
pip install -e .

# Or install with optional dependencies
pip install -e ".[dev,integrations]"
```

This allows you to:
- Make changes to the SDK code and see them immediately
- Run tests and contribute to development
- Use all the latest features

### Option 2: Install from Git Repository

You can install directly from the GitHub repository:

```bash
# Install latest version from main branch
pip install git+https://github.com/h2oai/text-2-everything.git#subdirectory=text2everything_sdk

# Or install a specific branch/tag
pip install git+https://github.com/h2oai/text-2-everything.git@your-branch#subdirectory=text2everything_sdk
```

### Option 3: Install from Local Archive

Create a distribution package and install it:

```bash
# Navigate to the SDK directory
cd text2everything_sdk

# Build the package
python setup.py sdist bdist_wheel

# Install from the built package
pip install dist/text2everything_sdk-0.1.2-py3-none-any.whl
```

## Quick Start After Installation

Once installed, you can use the SDK:

```python
from text2everything_sdk import Text2EverythingClient

# Initialize client
client = Text2EverythingClient(
    base_url="https://your-api-endpoint.com",
    api_key="your-api-key"
)

# Create a project
project = client.projects.create(name="My Project")
print(f"Created project: {project.id}")
```

## Publishing to PyPI (For Maintainers)

To make the SDK available via `pip install text2everything-sdk`, you need to publish it to PyPI:

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
   pip install --index-url https://test.pypi.org/simple/ text2everything-sdk
   ```

4. **Upload to Production PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

5. **Verify Installation**:
   ```bash
   pip install text2everything-sdk
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
T2E_API_KEY=your-api-key
```

The SDK will automatically load these variables when running tests.

### Environment Variables

Alternatively, set environment variables:

```bash
export T2E_BASE_URL="https://your-api-endpoint.com"
export T2E_API_KEY="your-api-key"
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

1. **For Users**: Use Option 1 (local installation) for now
2. **For Production**: Wait for PyPI publication or use Git installation
3. **For Contributors**: Use development setup with all dependencies

Once published to PyPI, users will be able to simply run:
```bash
pip install text2everything-sdk
