# Text2Everything SDK Modular Test Suite

This directory contains the modularized functional test suite for the Text2Everything SDK. Each test module focuses on a specific resource type or functionality, making it easier to run targeted tests and maintain the test code.

## Structure

```
tests/
├── __init__.py                    # Package initialization and exports
├── README.md                      # This file
├── base_test.py                   # Base test class with common functionality
├── test_projects.py               # Projects resource tests
├── test_contexts.py               # Contexts resource tests
├── test_schema_metadata.py        # Schema metadata resource tests
├── test_golden_examples.py        # Golden examples resource tests
├── test_connectors.py             # Connectors resource tests
├── test_executions.py             # SQL executions resource tests
├── test_chat.py                   # Chat resource tests
├── test_chat_sessions.py          # Chat sessions resource tests
├── test_feedback.py               # Feedback resource tests
├── test_custom_tools.py           # Custom tools resource tests
└── test_validation_errors.py      # Validation error handling tests
```

## Running Tests

### Main Test Runner

Use the main test runner to execute all or specific test suites:

```bash
# Run all tests
python run_tests.py --base-url http://localhost:8000 --api-key your-api-key

# Run specific test suites
python run_tests.py --base-url http://localhost:8000 --api-key your-api-key --tests projects,contexts,schema_metadata

# Run all tests except specific ones
python run_tests.py --base-url http://localhost:8000 --api-key your-api-key --exclude chat,executions

# List available test suites
python run_tests.py --list-tests
```

### Environment Variables

You can also set environment variables instead of using command-line arguments:

```bash
export T2E_BASE_URL=http://localhost:8000
export T2E_API_KEY=your-api-key
python run_tests.py
```

### Individual Test Modules

Each test module can also be run independently if needed:

```python
from tests.test_projects import ProjectsTestRunner

runner = ProjectsTestRunner("http://localhost:8000", "your-api-key")
if runner.setup():
    success = runner.run_test()
    runner.cleanup()
```

## Available Test Suites

- **projects**: Tests project CRUD operations
- **contexts**: Tests context management and business rules
- **schema_metadata**: Tests schema metadata with nested validation (tables, dimensions, metrics, relationships)
- **golden_examples**: Tests golden example management and search functionality
- **connectors**: Tests database connector creation and management (PostgreSQL, Snowflake)
- **executions**: Tests SQL execution operations
- **chat**: Tests chat functionality and H2OGPTE integration
- **chat_sessions**: Tests chat session management
- **feedback**: Tests feedback collection and management
- **custom_tools**: Tests custom tool upload and management
- **validation_errors**: Tests proper validation error handling

## Features

### Modular Design
- Each resource type has its own test module
- Common functionality is shared through the base test class
- Easy to add new test modules or modify existing ones

### Flexible Execution
- Run all tests or specific subsets
- Exclude problematic tests during development
- Individual test modules can be run independently

### Comprehensive Coverage
- Tests all major SDK functionality
- Includes real H2O Snowflake connector credentials for execution tests
- Validates error handling and edge cases

### Clean Resource Management
- Automatic setup and cleanup for each test suite
- Proper resource dependency handling
- No test pollution between runs

## Migration from Original Test

The original `test_functional.py` file has been split into these modular components. The functionality remains the same, but now you can:

1. Run specific test suites instead of all tests
2. Easily add new test modules
3. Maintain and debug individual components
4. Exclude problematic tests during development

## Adding New Tests

To add a new test module:

1. Create a new file `test_your_resource.py` in the `tests/` directory
2. Import and extend `BaseTestRunner`
3. Implement the `run_test()` method
4. Add your test class to `tests/__init__.py`
5. Add your test to the `test_runners` dictionary in `run_tests.py`

Example:

```python
# tests/test_your_resource.py
from .base_test import BaseTestRunner

class YourResourceTestRunner(BaseTestRunner):
    def run_test(self) -> bool:
        print("Testing your resource...")
        # Your test logic here
        return True
