"""
High concurrency test for Golden Examples resource.
Tests 32 concurrent requests to stress test golden example operations.
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


class HighConcurrencyGoldenExamplesTestRunner(BaseTestRunner):
    """Test runner for high concurrency golden examples operations with 32 requests."""
    
    def run_test(self) -> bool:
        """Test high concurrency golden examples operations."""
        print("\n🚀 Testing High Concurrency Golden Examples Operations (32 requests)...")
        
        try:
            if not self._test_golden_examples_high_concurrency():
                return False
            
            print("✅ Golden examples high concurrency test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Golden examples high concurrency test failed: {e}")
            return False
    
    def _test_golden_examples_high_concurrency(self) -> bool:
        """Test golden examples with 32 concurrent requests."""
        print("\n  💎 Testing Golden Examples - 32 concurrent requests...")
        
        # Create 32 identical golden example requests (with variations)
        test_examples = [
            {
                "user_query": f"How many concurrent operations {i:03d} completed successfully?",
                "sql_query": f"SELECT COUNT(*) FROM operations WHERE status = 'completed' AND batch_id = {i};",
                "description": f"High concurrency test example {i:03d}",
                "is_always_displayed": i % 6 == 0  # Every 6th item
            }
            for i in range(32)
        ]
        
        # Test parallel execution with 32 requests and rate limiting
        start_time = time.time()
        try:
            parallel_results = self.client.golden_examples.bulk_create(
                self.test_project_id, 
                test_examples,
                parallel=True,
                max_concurrent=8  # Rate limit to 8 concurrent requests
            )
            parallel_time = time.time() - start_time
            
            # Store created IDs for cleanup
            for result in parallel_results:
                self.created_resources['golden_examples'].append(result.id)
            
            # Verify results
            if len(parallel_results) != 32:
                print(f"❌ Expected 32 results, got {len(parallel_results)}")
                return False
            
            # Verify data integrity
            for i, result in enumerate(parallel_results):
                expected_query = f"How many concurrent operations {i:03d} completed successfully?"
                if result.user_query != expected_query:
                    print(f"❌ Example {i}: user_query mismatch")
                    return False
                if f"batch_id = {i}" not in result.sql_query:
                    print(f"❌ Example {i}: sql_query missing batch_id")
                    return False
            
            print(f"    ✅ Created 32 golden examples concurrently in {parallel_time:.2f}s")
            print(f"    📈 Average time per request: {parallel_time/32:.3f}s")
            print(f"    🚀 Throughput: {32/parallel_time:.1f} requests/second")
            print(f"    🛡️  Rate limited to max 8 concurrent requests")
            
            return True
            
        except Exception as e:
            print(f"❌ Golden examples high concurrency test failed: {e}")
            return False


def run_high_concurrency_golden_examples_test():
    """Standalone function to run golden examples high concurrency test."""
    test_runner = HighConcurrencyGoldenExamplesTestRunner()
    return test_runner.run_test()


if __name__ == "__main__":
    # Allow running this test standalone
    success = run_high_concurrency_golden_examples_test()
    exit(0 if success else 1)
