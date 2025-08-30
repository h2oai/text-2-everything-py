"""
High concurrency test for Schema Metadata resource.
Tests 32 concurrent requests to stress test schema metadata operations.
"""

import time
import sys
import os

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .base_test import BaseTestRunner
except ImportError:
    from tests.base_test import BaseTestRunner


class HighConcurrencySchemaMetadataTestRunner(BaseTestRunner):
    """Test runner for high concurrency schema metadata operations with 32 requests."""
    
    def run_test(self) -> bool:
        """Test high concurrency schema metadata operations."""
        print("\n🚀 Testing High Concurrency Schema Metadata Operations (32 requests)...")
        
        try:
            if not self._test_schema_metadata_high_concurrency():
                return False
            
            print("✅ Schema metadata high concurrency test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Schema metadata high concurrency test failed: {e}")
            return False
    
    def _test_schema_metadata_high_concurrency(self) -> bool:
        """Test schema metadata with 32 concurrent requests."""
        print("\n  📊 Testing Schema Metadata - 32 concurrent requests...")
        
        # Create 32 identical schema requests (with name variations)
        test_schemas = [
            {
                "name": f"high_concurrency_table_{i:03d}",
                "description": "High concurrency test table schema",
                "schema_data": {
                    "table": {
                        "name": f"concurrency_test_table_{i:03d}",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True},
                            {"name": "test_field", "type": "string"},
                            {"name": "concurrency_id", "type": "integer"},
                            {"name": "created_at", "type": "timestamp"},
                            {"name": "updated_at", "type": "timestamp"},
                            {"name": "is_active", "type": "boolean"},
                            {"name": "owner_id", "type": "integer"},
                            {"name": "tags", "type": "array"},
                            {"name": "metadata", "type": "json"},
                            {"name": "version", "type": "integer"},
                            {"name": "description", "type": "string"}
                        ]
                    }
                },
                "is_always_displayed": i % 4 == 0  # Every 4th item
            }
            for i in range(32)
        ]
        
        # Test parallel execution with 32 requests and rate limiting
        start_time = time.time()
        try:
            parallel_results = self.client.schema_metadata.bulk_create(
                self.test_project_id, 
                test_schemas,
                parallel=True,
                max_concurrent=8  # Rate limit to 8 concurrent requests
            )
            parallel_time = time.time() - start_time
            
            # Store created IDs for cleanup
            for result in parallel_results:
                self.created_resources['schema_metadata'].append(result.id)
            
            # Verify results
            if len(parallel_results) != 32:
                print(f"❌ Expected 32 results, got {len(parallel_results)}")
                return False
            
            # Verify data integrity
            for i, result in enumerate(parallel_results):
                expected_name = f"high_concurrency_table_{i:03d}"
                if result.name != expected_name:
                    print(f"❌ Schema {i}: name mismatch - expected {expected_name}, got {result.name}")
                    return False
            
            print(f"    ✅ Created 32 schemas concurrently in {parallel_time:.2f}s")
            print(f"    📈 Average time per request: {parallel_time/32:.3f}s")
            print(f"    🚀 Throughput: {32/parallel_time:.1f} requests/second")
            print(f"    🛡️  Rate limited to max 8 concurrent requests")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema metadata high concurrency test failed: {e}")
            return False


def run_high_concurrency_schema_metadata_test():
    """Standalone function to run schema metadata high concurrency test."""
    test_runner = HighConcurrencySchemaMetadataTestRunner()
    return test_runner.run_test()


if __name__ == "__main__":
    # Allow running this test standalone
    success = run_high_concurrency_schema_metadata_test()
    exit(0 if success else 1)
