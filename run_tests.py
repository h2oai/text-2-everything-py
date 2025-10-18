#!/usr/bin/env python3
"""
Main entry point for running Text2Everything SDK functional tests.

This script orchestrates the execution of all modularized test suites.
It provides options to run all tests or specific test suites.

Usage:
    python run_tests.py --base-url http://localhost:8000 --access-token your-access-token --workspace-name workspaces/dev
    python run_tests.py --base-url http://localhost:8000 --access-token your-access-token --tests projects,contexts
    python run_tests.py --base-url http://localhost:8000 --access-token your-access-token --exclude chat,executions
"""

import os
import sys
import argparse
import time
from typing import List, Dict, Type

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading
    pass

# Import from local tests directory
from tests import (
    BaseTestRunner,
    ProjectsTestRunner,
    ContextsTestRunner,
    SchemaMetadataTestRunner,
    GoldenExamplesTestRunner,
    ConnectorsTestRunner,
    ExecutionsTestRunner,
    ChatTestRunner,
    ChatSessionsTestRunner,
    FeedbackTestRunner,
    CustomToolsTestRunner,
    ValidationErrorsTestRunner,
    HighConcurrencySchemaMetadataTestRunner,
    HighConcurrencyContextsTestRunner,
    HighConcurrencyGoldenExamplesTestRunner
)


class TestSuiteRunner:
    """Main test suite runner that orchestrates all individual test runners."""
    
    def __init__(self, base_url: str, access_token: str, workspace_name: str | None = None):
        self.base_url = base_url
        self.access_token = access_token
        self.workspace_name = workspace_name
        
        # Define all available test runners with proper ordering
        # Tests that create resources should run before tests that depend on them
        self.test_runners: Dict[str, Type[BaseTestRunner]] = {
            'projects': ProjectsTestRunner,
            'contexts': ContextsTestRunner,
            'schema_metadata': SchemaMetadataTestRunner,
            'golden_examples': GoldenExamplesTestRunner,
            'connectors': ConnectorsTestRunner,  # Creates connectors
            'executions': ExecutionsTestRunner,  # Depends on connectors
            'chat': ChatTestRunner,              # May use connectors
            'chat_sessions': ChatSessionsTestRunner,
            'feedback': FeedbackTestRunner,
            'custom_tools': CustomToolsTestRunner,
            'validation_errors': ValidationErrorsTestRunner,
            'high_concurrency_schema_metadata': HighConcurrencySchemaMetadataTestRunner,  # 32 schema requests only
            'high_concurrency_contexts': HighConcurrencyContextsTestRunner,  # 32 context requests only
            'high_concurrency_golden_examples': HighConcurrencyGoldenExamplesTestRunner  # 32 golden example requests only
        }
        
        # Define the recommended test execution order
        # Fixed dependency chain: connectors → chat_sessions → chat → executions
        # High concurrency tests run last as they are stress tests
        self.recommended_order = [
            'projects', 'contexts', 'schema_metadata', 'golden_examples',
            'connectors', 'chat_sessions', 'chat', 'executions', 
            'feedback', 'custom_tools', 'validation_errors',
            'high_concurrency_schema_metadata', 'high_concurrency_contexts', 
            'high_concurrency_golden_examples'
        ]
    
    def run_tests(self, include_tests: List[str] = None, exclude_tests: List[str] = None) -> bool:
        """
        Run the specified test suites.
        
        Args:
            include_tests: List of test names to include (if None, run all)
            exclude_tests: List of test names to exclude
            
        Returns:
            True if all tests passed, False otherwise
        """
        print("🧪 Text2Everything SDK Modular Functional Test Suite")
        print("=" * 70)
        
        # Determine which tests to run
        if include_tests:
            tests_to_run = [name for name in include_tests if name in self.test_runners]
            if len(tests_to_run) != len(include_tests):
                invalid_tests = set(include_tests) - set(tests_to_run)
                print(f"⚠️  Invalid test names: {', '.join(invalid_tests)}")
                print(f"Available tests: {', '.join(self.test_runners.keys())}")
                return False
        else:
            tests_to_run = self.recommended_order.copy()
        
        # Remove excluded tests
        if exclude_tests:
            tests_to_run = [name for name in tests_to_run if name not in exclude_tests]
        
        # If specific tests were requested, maintain the recommended order for those tests
        if include_tests:
            # Sort the requested tests according to the recommended order
            ordered_tests = []
            for test_name in self.recommended_order:
                if test_name in tests_to_run:
                    ordered_tests.append(test_name)
            tests_to_run = ordered_tests
        
        if not tests_to_run:
            print("❌ No tests to run after applying filters")
            return False
        
        print(f"Running {len(tests_to_run)} test suites: {', '.join(tests_to_run)}")
        print()
        
        # Track results
        passed_tests = []
        failed_tests = []
        
        # Run each test suite
        for test_name in tests_to_run:
            print(f"🔄 Starting {test_name} test suite...")
            
            try:
                # Create and run the test runner
                runner_class = self.test_runners[test_name]
                runner = runner_class(self.base_url, self.access_token, self.workspace_name)
                
                # Setup the runner
                if not runner.setup():
                    print(f"❌ {test_name} test suite setup failed")
                    failed_tests.append(test_name)
                    continue
                
                # Run the test
                try:
                    success = runner.run_test()
                    if success:
                        print(f"✅ {test_name} test suite passed")
                        passed_tests.append(test_name)
                    else:
                        print(f"❌ {test_name} test suite failed")
                        failed_tests.append(test_name)
                finally:
                    # Always cleanup
                    runner.cleanup()
                    
            except Exception as e:
                print(f"❌ {test_name} test suite crashed: {e}")
                failed_tests.append(test_name)
            
            print()  # Add spacing between test suites
        
        # Print final results
        print("=" * 70)
        print("📊 Test Results Summary")
        print("=" * 70)
        
        total_tests = len(tests_to_run)
        passed_count = len(passed_tests)
        failed_count = len(failed_tests)
        
        if passed_tests:
            print(f"✅ Passed ({passed_count}/{total_tests}):")
            for test_name in passed_tests:
                print(f"   • {test_name}")
        
        if failed_tests:
            print(f"❌ Failed ({failed_count}/{total_tests}):")
            for test_name in failed_tests:
                print(f"   • {test_name}")
        
        print()
        if failed_count == 0:
            print("🎉 All test suites passed!")
            print("The Text2Everything SDK is working correctly with the live API!")
        else:
            print(f"⚠️  {failed_count} test suite(s) failed. Please check the API and try again.")
        
        return failed_count == 0


def main():
    """Main function to run the test suite."""
    parser = argparse.ArgumentParser(
        description="Run Text2Everything SDK modular functional tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py --base-url http://localhost:8000 --access-token your-token
  
  # Run specific tests
  python run_tests.py --base-url http://localhost:8000 --access-token your-token --tests projects,contexts
  
  # Run all tests except specific ones
  python run_tests.py --base-url http://localhost:8000 --access-token your-token --exclude chat,executions
        """
    )
    
    parser.add_argument(
        "--base-url",
        default=os.getenv("T2E_BASE_URL", "http://localhost:8000"),
        help="Base URL of the Text2Everything API"
    )
    parser.add_argument(
        "--access-token",
        default=os.getenv("T2E_ACCESS_TOKEN"),
        help="OIDC access token for authentication"
    )
    parser.add_argument(
        "--workspace-name",
        default=os.getenv("T2E_WORKSPACE_NAME"),
        help="Optional workspace name, e.g., workspaces/dev"
    )
    parser.add_argument(
        "--tests",
        help="Comma-separated list of specific tests to run"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of tests to exclude"
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List available test suites and exit"
    )
    
    args = parser.parse_args()
    
    # Create the test suite runner
    runner = TestSuiteRunner("", "")  # Temporary for listing tests
    
    if args.list_tests:
        print("Available test suites:")
        for test_name in runner.test_runners.keys():
            print(f"  • {test_name}")
        sys.exit(0)
    
    if not args.access_token:
        print("❌ Access token is required. Provide it via --access-token or T2E_ACCESS_TOKEN environment variable.")
        sys.exit(1)
    
    # Parse test filters
    include_tests = None
    if args.tests:
        include_tests = [test.strip() for test in args.tests.split(',')]
    
    exclude_tests = None
    if args.exclude:
        exclude_tests = [test.strip() for test in args.exclude.split(',')]
    
    print("Text2Everything SDK Modular Functional Test Suite")
    print("This script runs individual test suites against a live API endpoint.")
    print(f"API Endpoint: {args.base_url}")
    if args.workspace_name:
        print(f"Workspace: {args.workspace_name}")
    print()
    
    # Create and run the test suite
    suite_runner = TestSuiteRunner(args.base_url, args.access_token, args.workspace_name)
    success = suite_runner.run_tests(include_tests, exclude_tests)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
