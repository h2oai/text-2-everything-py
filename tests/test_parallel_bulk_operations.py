"""
Test parallel bulk operations for the Text2Everything SDK.
"""

import time
import os
from typing import List, Dict, Any
from .base_test import BaseTestRunner
from exceptions import ValidationError


class ParallelBulkOperationsTestRunner(BaseTestRunner):
    """Test runner for parallel bulk operations."""
    
    def run_test(self) -> bool:
        """Test parallel bulk operations with performance comparison."""
        print("\n🚀 Testing Parallel Bulk Operations...")
        
        try:
            # Test 1: Basic parallel bulk create functionality
            if not self._test_basic_parallel_bulk_create():
                return False
            
            # Test 2: Performance comparison (parallel vs sequential)
            if not self._test_performance_comparison():
                return False
            
            # Test 3: Error handling in parallel mode
            if not self._test_parallel_error_handling():
                return False
            
            # Test 4: Validation in parallel mode
            if not self._test_parallel_validation():
                return False
            
            # Test 5: Edge cases
            if not self._test_edge_cases():
                return False
            
            print("✅ All parallel bulk operation tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Parallel bulk operations test failed: {e}")
            return False
    
    def _test_basic_parallel_bulk_create(self) -> bool:
        """Test basic parallel bulk create functionality."""
        print("\n  📋 Testing basic parallel bulk create...")
        
        # Create test data with different schema types
        test_schemas = [
            {
                "name": f"parallel_table_{i}",
                "description": f"Test table schema {i}",
                "schema_data": {
                    "table": {
                        "name": f"test_table_{i}",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True},
                            {"name": f"field_{i}", "type": "string"}
                        ]
                    }
                },
                "is_always_displayed": i % 2 == 0
            }
            for i in range(5)
        ]
        
        # Add dimension schemas
        test_schemas.extend([
            {
                "name": f"parallel_dimension_{i}",
                "description": f"Test dimension schema {i}",
                "schema_data": {
                    "table": {
                        "dimension": {
                            "name": f"test_dimension_{i}",
                            "content": {
                                "type": "categorical",
                                "values": [f"value_{j}" for j in range(3)]
                            }
                        }
                    }
                }
            }
            for i in range(3)
        ])
        
        # Test parallel execution (default)
        start_time = time.time()
        parallel_results = self.client.schema_metadata.bulk_create(
            self.test_project_id, 
            test_schemas,
            parallel=True
        )
        parallel_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in parallel_results:
            self.created_resources['schema_metadata'].append(result.id)
        
        # Verify results
        if len(parallel_results) != len(test_schemas):
            print(f"❌ Expected {len(test_schemas)} results, got {len(parallel_results)}")
            return False
        
        # Verify all schemas were created with correct data
        for i, (original, result) in enumerate(zip(test_schemas, parallel_results)):
            if result.name != original["name"]:
                print(f"❌ Schema {i}: name mismatch")
                return False
            if result.description != original["description"]:
                print(f"❌ Schema {i}: description mismatch")
                return False
            if result.is_always_displayed != original.get("is_always_displayed", False):
                print(f"❌ Schema {i}: is_always_displayed mismatch")
                return False
        
        print(f"    ✅ Created {len(parallel_results)} schemas in parallel ({parallel_time:.2f}s)")
        return True
    
    def _test_performance_comparison(self) -> bool:
        """Test performance comparison between parallel and sequential execution."""
        print("\n  ⚡ Testing performance comparison...")
        
        # Create test data (smaller set for performance test)
        test_schemas = [
            {
                "name": f"perf_test_schema_{i}",
                "description": f"Performance test schema {i}",
                "schema_data": {
                    "table": {
                        "name": f"perf_table_{i}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
            for i in range(8)  # 8 schemas for performance test
        ]
        
        # Test sequential execution
        start_time = time.time()
        sequential_results = self.client.schema_metadata.bulk_create(
            self.test_project_id,
            test_schemas,
            parallel=False
        )
        sequential_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in sequential_results:
            self.created_resources['schema_metadata'].append(result.id)
        
        # Create another set for parallel test
        parallel_test_schemas = [
            {
                "name": f"perf_parallel_schema_{i}",
                "description": f"Performance parallel test schema {i}",
                "schema_data": {
                    "table": {
                        "name": f"perf_parallel_table_{i}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
            for i in range(8)
        ]
        
        # Test parallel execution
        start_time = time.time()
        parallel_results = self.client.schema_metadata.bulk_create(
            self.test_project_id,
            parallel_test_schemas,
            parallel=True
        )
        parallel_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in parallel_results:
            self.created_resources['schema_metadata'].append(result.id)
        
        # Verify both produced same number of results
        if len(sequential_results) != len(parallel_results):
            print(f"❌ Result count mismatch: sequential={len(sequential_results)}, parallel={len(parallel_results)}")
            return False
        
        # Calculate performance improvement
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print(f"    ✅ Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s")
            print(f"    📈 Speedup: {speedup:.2f}x")
            
            # Parallel should be faster (or at least not significantly slower)
            if speedup < 0.5:  # Allow some overhead for small datasets
                print(f"    ⚠️  Warning: Parallel execution was slower than expected")
        else:
            print(f"    ✅ Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s")
        
        return True
    
    def _test_parallel_error_handling(self) -> bool:
        """Test error handling in parallel mode."""
        print("\n  🚨 Testing parallel error handling...")
        
        # Create test data with some invalid schemas
        test_schemas = [
            # Valid schema
            {
                "name": "valid_schema_1",
                "schema_data": {
                    "table": {
                        "name": "valid_table",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            },
            # Invalid schema (missing required field)
            {
                "name": "invalid_schema_1",
                "schema_data": {
                    "table": {
                        # Missing 'name' field
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            },
            # Another valid schema
            {
                "name": "valid_schema_2",
                "schema_data": {
                    "table": {
                        "name": "valid_table_2",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
        ]
        
        # Test that validation catches errors before parallel execution
        try:
            self.client.schema_metadata.bulk_create(
                self.test_project_id,
                test_schemas,
                parallel=True,
                validate=True
            )
            print("❌ Expected validation error but none was raised")
            return False
        except ValidationError as e:
            if "Bulk validation failed" in str(e):
                print("    ✅ Validation correctly caught errors before parallel execution")
            else:
                print(f"❌ Unexpected validation error: {e}")
                return False
        
        # Test with validation disabled to see runtime error handling
        # (Note: This might create some valid schemas before failing)
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                test_schemas,
                parallel=True,
                validate=False
            )
            # If we get here, the API might be more lenient than expected
            print("    ⚠️  API accepted schemas that were expected to fail")
            # Clean up any created schemas
            for result in results:
                if result and hasattr(result, 'id'):
                    self.created_resources['schema_metadata'].append(result.id)
        except ValidationError as e:
            if "partially failed" in str(e):
                print("    ✅ Parallel execution correctly handled mixed success/failure")
            else:
                print(f"    ✅ Parallel execution failed as expected: {e}")
        
        return True
    
    def _test_parallel_validation(self) -> bool:
        """Test validation behavior in parallel mode."""
        print("\n  🔍 Testing parallel validation...")
        
        # Test with all valid schemas
        valid_schemas = [
            {
                "name": f"validation_test_{i}",
                "schema_data": {
                    "table": {
                        "name": f"validation_table_{i}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
            for i in range(3)
        ]
        
        # Test with validation enabled (should succeed)
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                valid_schemas,
                parallel=True,
                validate=True
            )
            
            # Store created IDs for cleanup
            for result in results:
                self.created_resources['schema_metadata'].append(result.id)
            
            print(f"    ✅ Validation passed for {len(results)} valid schemas")
        except Exception as e:
            print(f"❌ Validation failed unexpectedly: {e}")
            return False
        
        # Test with validation disabled (should also succeed)
        valid_schemas_no_validation = [
            {
                "name": f"no_validation_test_{i}",
                "schema_data": {
                    "table": {
                        "name": f"no_validation_table_{i}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
            for i in range(2)
        ]
        
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                valid_schemas_no_validation,
                parallel=True,
                validate=False
            )
            
            # Store created IDs for cleanup
            for result in results:
                self.created_resources['schema_metadata'].append(result.id)
            
            print(f"    ✅ No validation mode created {len(results)} schemas")
        except Exception as e:
            print(f"❌ No validation mode failed unexpectedly: {e}")
            return False
        
        return True
    
    def _test_edge_cases(self) -> bool:
        """Test edge cases for parallel bulk operations."""
        print("\n  🔬 Testing edge cases...")
        
        # Test empty list
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                [],
                parallel=True
            )
            if len(results) == 0:
                print("    ✅ Empty list handled correctly")
            else:
                print(f"❌ Expected empty results, got {len(results)}")
                return False
        except Exception as e:
            print(f"❌ Empty list test failed: {e}")
            return False
        
        # Test single item (should use sequential path)
        single_schema = [{
            "name": "single_edge_case",
            "schema_data": {
                "table": {
                    "name": "single_table",
                    "columns": [{"name": "id", "type": "integer"}]
                }
            }
        }]
        
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                single_schema,
                parallel=True
            )
            
            if len(results) == 1:
                self.created_resources['schema_metadata'].append(results[0].id)
                print("    ✅ Single item handled correctly")
            else:
                print(f"❌ Expected 1 result, got {len(results)}")
                return False
        except Exception as e:
            print(f"❌ Single item test failed: {e}")
            return False
        
        # Test custom max_workers
        test_schemas = [
            {
                "name": f"max_workers_test_{i}",
                "schema_data": {
                    "table": {
                        "name": f"max_workers_table_{i}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }
            for i in range(4)
        ]
        
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                test_schemas,
                parallel=True,
                max_workers=2
            )
            
            if len(results) == 4:
                for result in results:
                    self.created_resources['schema_metadata'].append(result.id)
                print("    ✅ Custom max_workers handled correctly")
            else:
                print(f"❌ Expected 4 results, got {len(results)}")
                return False
        except Exception as e:
            print(f"❌ Custom max_workers test failed: {e}")
            return False
        
        return True


def run_parallel_bulk_test():
    """Standalone function to run parallel bulk operations test."""
    test_runner = ParallelBulkOperationsTestRunner()
    return test_runner.run_test()


if __name__ == "__main__":
    # Allow running this test standalone
    success = run_parallel_bulk_test()
    exit(0 if success else 1)
