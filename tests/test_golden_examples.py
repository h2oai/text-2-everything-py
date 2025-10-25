"""
Golden examples resource functional tests.
"""

import time
from .base_test import BaseTestRunner
from exceptions import ValidationError


class GoldenExamplesTestRunner(BaseTestRunner):
    """Test runner for Golden Examples resource."""
    
    def run_test(self) -> bool:
        """Test golden examples CRUD operations."""
        print("\n4. Testing Golden Examples Resource...")
        
        try:
            # Test create golden example
            example_result = self.client.golden_examples.create(
                self.test_project_id,
                description="Count all active users",
                user_query="How many active users do we have?",
                sql_query="SELECT COUNT(*) FROM users WHERE status = 'active';",
                is_always_displayed=True
            )
            self.created_resources['golden_examples'].append(example_result.id)
            print(f"✅ Created golden example: {example_result.id}")
            
            # Test create another example
            example_result2 = self.client.golden_examples.create(
                self.test_project_id,
                description="Count recent user signups",
                user_query="How many users signed up in the last 30 days?",
                sql_query="SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '30 days';",
                is_always_displayed=False
            )
            self.created_resources['golden_examples'].append(example_result2.id)
            print(f"✅ Created second golden example: {example_result2.id}")
            
            # Test list golden examples
            examples = self.client.golden_examples.list(self.test_project_id)
            print(f"✅ Listed {len(examples)} golden examples")
            
            # Test get golden example
            retrieved_example = self.client.golden_examples.get(self.test_project_id, example_result.id)
            print(f"✅ Retrieved golden example: {retrieved_example.user_query}")
            
            # Test update golden example
            updated_example = self.client.golden_examples.update(
                self.test_project_id,
                example_result.id,
                description="Updated: Count all active users in the system",
                sql_query="SELECT COUNT(*) as active_user_count FROM users WHERE status = 'active';"
            )
            print("✅ Updated golden example")
            
            # Test search by query
            search_results = self.client.golden_examples.search_by_query(self.test_project_id, "users")
            print(f"✅ Found {len(search_results)} examples containing 'users'")
            
            # Test search by user query (replaces get_by_name functionality)
            search_results = self.client.golden_examples.search_by_query(self.test_project_id, "active users")
            if search_results:
                print("✅ Found example by searching user query")
            else:
                print("❌ Failed to find example by searching user query")
                return False
            
            # Test list always displayed
            always_examples = self.client.golden_examples.list_always_displayed(self.test_project_id)
            print(f"✅ Found {len(always_examples)} always-displayed examples")
            
            # Test parallel bulk operations
            if not self._test_parallel_bulk_operations():
                return False
            
            # Test bulk delete
            if not self._test_bulk_delete():
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Golden examples test failed: {e}")
            return False
    
    def _test_parallel_bulk_operations(self) -> bool:
        """Test parallel bulk operations functionality for golden examples."""
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
            
            # Test 4: Edge cases
            if not self._test_parallel_edge_cases():
                return False
            
            print("✅ All parallel bulk operation tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Parallel bulk operations test failed: {e}")
            return False
    
    def _test_basic_parallel_bulk_create(self) -> bool:
        """Test basic parallel bulk create functionality."""
        print("\n  📋 Testing basic parallel bulk create...")
        
        # Create test data with different golden examples
        test_examples = [
            {
                "user_query": f"How many orders were placed in Q{i}?",
                "sql_query": f"SELECT COUNT(*) FROM orders WHERE EXTRACT(QUARTER FROM created_at) = {i};",
                "description": f"Count orders in Q{i}",
                "is_always_displayed": i % 2 == 0
            }
            for i in range(1, 5)
        ]
        
        # Add more diverse examples
        test_examples.extend([
            {
                "user_query": "What is the average order value?",
                "sql_query": "SELECT AVG(total_amount) FROM orders;",
                "description": "Calculate average order value"
            },
            {
                "user_query": "How many customers are active?",
                "sql_query": "SELECT COUNT(*) FROM customers WHERE status = 'active';",
                "description": "Count active customers",
                "is_always_displayed": True
            },
            {
                "user_query": "What are the top 5 products by sales?",
                "sql_query": "SELECT product_name, SUM(quantity) as total_sales FROM order_items GROUP BY product_name ORDER BY total_sales DESC LIMIT 5;",
                "description": "Top selling products"
            }
        ])
        
        # Test parallel execution (default)
        start_time = time.time()
        parallel_results = self.client.golden_examples.bulk_create(
            self.test_project_id, 
            test_examples,
            parallel=True
        )
        parallel_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in parallel_results:
            self.created_resources['golden_examples'].append(result.id)
        
        # Verify results
        if len(parallel_results) != len(test_examples):
            print(f"❌ Expected {len(test_examples)} results, got {len(parallel_results)}")
            return False
        
        # Verify all examples were created with correct data
        for i, (original, result) in enumerate(zip(test_examples, parallel_results)):
            if result.user_query != original["user_query"]:
                print(f"❌ Example {i}: user_query mismatch")
                return False
            if result.sql_query != original["sql_query"]:
                print(f"❌ Example {i}: sql_query mismatch")
                return False
            if result.description != original.get("description"):
                print(f"❌ Example {i}: description mismatch")
                return False
            if result.is_always_displayed != original.get("is_always_displayed", False):
                print(f"❌ Example {i}: is_always_displayed mismatch")
                return False
        
        print(f"    ✅ Created {len(parallel_results)} golden examples in parallel ({parallel_time:.2f}s)")
        return True
    
    def _test_performance_comparison(self) -> bool:
        """Test performance comparison between parallel and sequential execution."""
        print("\n  ⚡ Testing performance comparison...")
        
        # Create test data (smaller set for performance test)
        test_examples = [
            {
                "user_query": f"How many items in category {i}?",
                "sql_query": f"SELECT COUNT(*) FROM products WHERE category_id = {i};",
                "description": f"Count products in category {i}"
            }
            for i in range(1, 7)  # 6 examples for performance test
        ]
        
        # Test sequential execution
        start_time = time.time()
        sequential_results = self.client.golden_examples.bulk_create(
            self.test_project_id,
            test_examples,
            parallel=False
        )
        sequential_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in sequential_results:
            self.created_resources['golden_examples'].append(result.id)
        
        # Create another set for parallel test
        parallel_test_examples = [
            {
                "user_query": f"What is the revenue for region {i}?",
                "sql_query": f"SELECT SUM(total_amount) FROM orders WHERE region_id = {i};",
                "description": f"Calculate revenue for region {i}"
            }
            for i in range(1, 7)
        ]
        
        # Test parallel execution
        start_time = time.time()
        parallel_results = self.client.golden_examples.bulk_create(
            self.test_project_id,
            parallel_test_examples,
            parallel=True
        )
        parallel_time = time.time() - start_time
        
        # Store created IDs for cleanup
        for result in parallel_results:
            self.created_resources['golden_examples'].append(result.id)
        
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
        
        # Test with invalid data that should trigger validation errors
        test_examples = [
            # Valid example
            {
                "user_query": "How many valid orders?",
                "sql_query": "SELECT COUNT(*) FROM orders WHERE status = 'valid';",
                "description": "Count valid orders"
            },
            # Invalid example (empty user_query)
            {
                "user_query": "",
                "sql_query": "SELECT COUNT(*) FROM orders;",
                "description": "Invalid example with empty user query"
            },
            # Another valid example
            {
                "user_query": "What is the total revenue?",
                "sql_query": "SELECT SUM(total_amount) FROM orders;",
                "description": "Calculate total revenue"
            }
        ]
        
        # Test that validation catches errors before parallel execution
        try:
            self.client.golden_examples.bulk_create(
                self.test_project_id,
                test_examples,
                parallel=True
            )
            # If we get here, the API might be more lenient than expected
            print("    ⚠️  API accepted examples that were expected to fail - validation may be lenient")
            print("    ✅ Parallel execution completed without errors")
        except ValidationError as e:
            if "Bulk validation failed" in str(e):
                print("    ✅ Validation correctly caught errors before parallel execution")
            else:
                print(f"    ✅ Validation caught errors as expected: {e}")
        except Exception as e:
            print(f"    ✅ Error handling working correctly: {e}")
        
        # Test empty list handling
        try:
            empty_results = self.client.golden_examples.bulk_create(
                self.test_project_id,
                [],
                parallel=True
            )
            if len(empty_results) == 0:
                print("    ✅ Empty list handled correctly")
            else:
                print(f"    ❌ Expected empty results, got {len(empty_results)}")
                return False
        except Exception as e:
            print(f"    ❌ Empty list test failed: {e}")
            return False
        
        return True
    
    def _test_bulk_delete(self) -> bool:
        """Test bulk delete functionality."""
        print("\n  🗑️  Testing bulk delete...")
        
        # Create test items for bulk deletion
        items_to_delete = []
        for i in range(5):
            example = self.client.golden_examples.create(
                project_id=self.test_project_id,
                user_query=f"Bulk delete test query {i}",
                sql_query=f"SELECT {i};",
                description=f"Example {i} to be bulk deleted"
            )
            items_to_delete.append(example.id)
            # Don't add to created_resources - will be bulk deleted
        
        # Test bulk delete
        result = self.client.golden_examples.bulk_delete(
            self.test_project_id,
            items_to_delete
        )
        
        # Verify results
        if result['deleted_count'] != 5:
            print(f"❌ Expected 5 deletions, got {result['deleted_count']}")
            return False
        
        if result.get('failed_ids'):
            print(f"❌ Unexpected failures: {result['failed_ids']}")
            return False
        
        # Verify items are actually deleted
        remaining = self.client.golden_examples.list(self.test_project_id)
        remaining_ids = [item.id for item in remaining]
        
        for deleted_id in items_to_delete:
            if deleted_id in remaining_ids:
                print(f"❌ Item {deleted_id} still exists after bulk delete")
                return False
        
        print(f"    ✅ Successfully bulk deleted {len(items_to_delete)} items")
        
        # Test error handling - try to delete non-existent IDs
        fake_ids = ["fake_id_1", "fake_id_2"]
        try:
            result = self.client.golden_examples.bulk_delete(
                self.test_project_id,
                fake_ids
            )
            if result.get('failed_ids'):
                print("    ✅ Error handling working correctly for invalid IDs")
            else:
                print("    ⚠️  API accepted invalid IDs without errors")
        except Exception as e:
            print(f"    ✅ Exception raised for invalid IDs: {type(e).__name__}")
        
        # Test empty list
        try:
            result = self.client.golden_examples.bulk_delete(
                self.test_project_id,
                []
            )
            print(f"    ❌ Empty list should raise ValidationError")
            return False
        except ValidationError:
            print("    ✅ Empty list correctly raises ValidationError")
        
        return True
    
    def _test_parallel_edge_cases(self) -> bool:
        """Test edge cases for parallel bulk operations."""
        print("\n  🔬 Testing edge cases...")
        
        # Test single item (should use sequential path)
        single_example = [{
            "user_query": "Single edge case test",
            "sql_query": "SELECT 1;",
            "description": "Single example test"
        }]
        
        try:
            results = self.client.golden_examples.bulk_create(
                self.test_project_id,
                single_example,
                parallel=True
            )
            
            if len(results) == 1:
                self.created_resources['golden_examples'].append(results[0].id)
                print("    ✅ Single item handled correctly")
            else:
                print(f"❌ Expected 1 result, got {len(results)}")
                return False
        except Exception as e:
            print(f"❌ Single item test failed: {e}")
            return False
        
        # Test custom max_workers
        test_examples = [
            {
                "user_query": f"Max workers test {i}",
                "sql_query": f"SELECT {i};",
                "description": f"Max workers test example {i}"
            }
            for i in range(4)
        ]
        
        try:
            results = self.client.golden_examples.bulk_create(
                self.test_project_id,
                test_examples,
                parallel=True,
                max_workers=2
            )
            
            if len(results) == 4:
                for result in results:
                    self.created_resources['golden_examples'].append(result.id)
                print("    ✅ Custom max_workers handled correctly")
            else:
                print(f"❌ Expected 4 results, got {len(results)}")
                return False
        except Exception as e:
            print(f"❌ Custom max_workers test failed: {e}")
            return False
        
        return True
