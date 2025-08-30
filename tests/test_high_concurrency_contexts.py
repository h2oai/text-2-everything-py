"""
High concurrency test for Contexts resource.
Tests 32 concurrent requests to stress test context operations.
"""

import time
from .base_test import BaseTestRunner


class HighConcurrencyContextsTestRunner(BaseTestRunner):
    """Test runner for high concurrency contexts operations with 32 requests."""
    
    def run_test(self) -> bool:
        """Test high concurrency contexts operations."""
        print("\n🚀 Testing High Concurrency Contexts Operations (32 requests)...")
        
        try:
            if not self._test_contexts_high_concurrency():
                return False
            
            print("✅ Contexts high concurrency test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Contexts high concurrency test failed: {e}")
            return False
    
    def _test_contexts_high_concurrency(self) -> bool:
        """Test contexts with 32 concurrent requests."""
        print("\n  📝 Testing Contexts - 32 concurrent requests...")
        
        # Create 32 identical context requests (with name variations)
        test_contexts = [
            {
                "name": f"High Concurrency Rule {i:03d}",
                "content": f"Concurrency test rule {i:03d}: All high-load operations must complete within acceptable time limits. Request ID: {i}",
                "description": "High concurrency test context",
                "is_always_displayed": i % 8 == 0  # Every 8th item
            }
            for i in range(32)
        ]
        
        # Test parallel execution with 32 requests and rate limiting
        start_time = time.time()
        try:
            parallel_results = self.client.contexts.bulk_create(
                self.test_project_id, 
                test_contexts,
                parallel=True,
                max_concurrent=8  # Rate limit to 8 concurrent requests
            )
            parallel_time = time.time() - start_time
            
            # Store created IDs for cleanup
            for result in parallel_results:
                self.created_resources['contexts'].append(result.id)
            
            # Verify results
            if len(parallel_results) != 32:
                print(f"❌ Expected 32 results, got {len(parallel_results)}")
                return False
            
            # Verify data integrity
            for i, result in enumerate(parallel_results):
                expected_name = f"High Concurrency Rule {i:03d}"
                if result.name != expected_name:
                    print(f"❌ Context {i}: name mismatch - expected {expected_name}, got {result.name}")
                    return False
                if f"Request ID: {i}" not in result.content:
                    print(f"❌ Context {i}: content missing request ID")
                    return False
            
            print(f"    ✅ Created 32 contexts concurrently in {parallel_time:.2f}s")
            print(f"    📈 Average time per request: {parallel_time/32:.3f}s")
            print(f"    🚀 Throughput: {32/parallel_time:.1f} requests/second")
            print(f"    🛡️  Rate limited to max 8 concurrent requests")
            
            return True
            
        except Exception as e:
            print(f"❌ Contexts high concurrency test failed: {e}")
            return False


def run_high_concurrency_contexts_test():
    """Standalone function to run contexts high concurrency test."""
    test_runner = HighConcurrencyContextsTestRunner()
    return test_runner.run_test()


if __name__ == "__main__":
    # Allow running this test standalone
    success = run_high_concurrency_contexts_test()
    exit(0 if success else 1)
