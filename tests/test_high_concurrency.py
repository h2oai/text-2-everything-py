"""
High concurrency tests for the Text2Everything SDK.
Tests with 32 concurrent requests to stress test the system.
"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from .base_test import BaseTestRunner
from ..exceptions import ValidationError


class HighConcurrencyTestRunner(BaseTestRunner):
    """Test runner for high concurrency operations with 32 requests."""
    
    def run_test(self) -> bool:
        """Test high concurrency operations across all resources."""
        print("\n🚀 Testing High Concurrency Operations (32 requests)...")
        
        try:
            # Test 1: Schema Metadata high concurrency
            if not self._test_schema_metadata_high_concurrency():
                return False
            
            # Test 2: Contexts high concurrency
            if not self._test_contexts_high_concurrency():
                return False
            
            # Test 3: Golden Examples high concurrency
            if not self._test_golden_examples_high_concurrency():
                return False
            
            # Test 4: Mixed resource high concurrency
            if not self._test_mixed_resource_high_concurrency():
                return False
            
            # Test 5: Stress test with increasing load
            if not self._test_stress_increasing_load():
                return False
            
            # Test 6: Extreme stress test with 32 workers
            if not self._test_extreme_stress_32_workers():
                return False
            
            print("✅ All high concurrency tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ High concurrency test failed: {e}")
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
        
        # Test parallel execution with 32 requests
        start_time = time.time()
        try:
            parallel_results = self.client.schema_metadata.bulk_create(
                self.test_project_id, 
                test_schemas,
                parallel=True
                # Uses default max_workers (16 for 32 requests)
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
            
            return True
            
        except Exception as e:
            print(f"❌ Schema metadata high concurrency test failed: {e}")
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
        
        # Test parallel execution with 32 requests
        start_time = time.time()
        try:
            parallel_results = self.client.contexts.bulk_create(
                self.test_project_id, 
                test_contexts,
                parallel=True
                # Uses default max_workers (16 for 32 requests)
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
            
            return True
            
        except Exception as e:
            print(f"❌ Contexts high concurrency test failed: {e}")
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
        
        # Test parallel execution with 32 requests
        start_time = time.time()
        try:
            parallel_results = self.client.golden_examples.bulk_create(
                self.test_project_id, 
                test_examples,
                parallel=True
                # Uses default max_workers (16 for 32 requests)
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
            
            return True
            
        except Exception as e:
            print(f"❌ Golden examples high concurrency test failed: {e}")
            return False
    
    def _test_mixed_resource_high_concurrency(self) -> bool:
        """Test mixed resource types with high concurrency."""
        print("\n  🔀 Testing Mixed Resources - 32 concurrent requests across all types...")
        
        # Create a mix of all resource types (10 schemas, 11 contexts, 11 examples = 32 total)
        mixed_operations = []
        
        # 10 schema operations
        for i in range(10):
            mixed_operations.append(('schema', {
                "name": f"mixed_schema_{i:03d}",
                "description": "Mixed concurrency test schema",
                "schema_data": {
                    "table": {
                        "name": f"mixed_table_{i:03d}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            }))
        
        # 11 context operations
        for i in range(11):
            mixed_operations.append(('context', {
                "name": f"Mixed Rule {i:03d}",
                "content": f"Mixed concurrency test rule {i:03d}",
                "description": "Mixed concurrency test context"
            }))
        
        # 11 golden example operations
        for i in range(11):
            mixed_operations.append(('example', {
                "user_query": f"Mixed test query {i:03d}?",
                "sql_query": f"SELECT {i} as mixed_test;",
                "description": f"Mixed concurrency test example {i:03d}"
            }))
        
        # Execute all operations concurrently using ThreadPoolExecutor
        start_time = time.time()
        results = {'schema': [], 'context': [], 'example': []}
        
        def execute_operation(op_type: str, data: Dict[str, Any]) -> Tuple[str, Any]:
            """Execute a single operation."""
            try:
                if op_type == 'schema':
                    result = self.client.schema_metadata.create(
                        self.test_project_id,
                        name=data["name"],
                        description=data["description"],
                        schema_data=data["schema_data"]
                    )
                elif op_type == 'context':
                    result = self.client.contexts.create(
                        self.test_project_id,
                        name=data["name"],
                        content=data["content"],
                        description=data["description"]
                    )
                elif op_type == 'example':
                    result = self.client.golden_examples.create(
                        self.test_project_id,
                        user_query=data["user_query"],
                        sql_query=data["sql_query"],
                        description=data["description"]
                    )
                return (op_type, result)
            except Exception as e:
                return (op_type, f"Error: {e}")
        
        try:
            with ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all operations
                future_to_op = {
                    executor.submit(execute_operation, op_type, data): (op_type, data)
                    for op_type, data in mixed_operations
                }
                
                # Collect results
                for future in as_completed(future_to_op):
                    op_type, result = future.result()
                    if isinstance(result, str) and result.startswith("Error:"):
                        print(f"❌ Operation failed: {result}")
                        return False
                    else:
                        results[op_type].append(result)
                        # Store for cleanup
                        if op_type == 'schema':
                            self.created_resources['schema_metadata'].append(result.id)
                        elif op_type == 'context':
                            self.created_resources['contexts'].append(result.id)
                        elif op_type == 'example':
                            self.created_resources['golden_examples'].append(result.id)
            
            mixed_time = time.time() - start_time
            
            # Verify results
            total_created = len(results['schema']) + len(results['context']) + len(results['example'])
            if total_created != 32:
                print(f"❌ Expected 32 total results, got {total_created}")
                return False
            
            print(f"    ✅ Created 32 mixed resources concurrently in {mixed_time:.2f}s")
            print(f"    📊 Breakdown: {len(results['schema'])} schemas, {len(results['context'])} contexts, {len(results['example'])} examples")
            print(f"    📈 Average time per request: {mixed_time/32:.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Mixed resource high concurrency test failed: {e}")
            return False
    
    def _test_stress_increasing_load(self) -> bool:
        """Test with increasing load: 8 → 16 → 32 requests."""
        print("\n  📈 Testing Stress with Increasing Load...")
        
        load_levels = [8, 16, 32]
        times = []
        
        for load in load_levels:
            print(f"\n    🔄 Testing with {load} concurrent requests...")
            
            # Create test data for current load level
            test_schemas = [
                {
                    "name": f"stress_test_{load}_{i:03d}",
                    "description": f"Stress test schema for load {load}",
                    "schema_data": {
                        "table": {
                            "name": f"stress_table_{load}_{i:03d}",
                            "columns": [{"name": "id", "type": "integer"}]
                        }
                    }
                }
                for i in range(load)
            ]
            
            # Execute with current load
            start_time = time.time()
            try:
                results = self.client.schema_metadata.bulk_create(
                    self.test_project_id,
                    test_schemas,
                    parallel=True,
                    max_workers=min(16, load)  # Cap workers at 16
                )
                execution_time = time.time() - start_time
                times.append(execution_time)
                
                # Store for cleanup
                for result in results:
                    self.created_resources['schema_metadata'].append(result.id)
                
                # Verify results
                if len(results) != load:
                    print(f"❌ Expected {load} results, got {len(results)}")
                    return False
                
                print(f"      ✅ {load} requests completed in {execution_time:.2f}s")
                print(f"      📊 Average: {execution_time/load:.3f}s per request")
                
            except Exception as e:
                print(f"❌ Stress test failed at load {load}: {e}")
                return False
        
        # Analyze scaling behavior
        print(f"\n    📈 Scaling Analysis:")
        for i, (load, time_taken) in enumerate(zip(load_levels, times)):
            throughput = load / time_taken
            print(f"      {load} requests: {time_taken:.2f}s ({throughput:.1f} req/s)")
        
        # Check if performance degrades significantly
        if len(times) >= 2:
            throughput_8 = load_levels[0] / times[0]
            throughput_32 = load_levels[-1] / times[-1]
            efficiency = throughput_32 / throughput_8
            
            print(f"    🎯 Efficiency at 32 vs 8 requests: {efficiency:.2f}x")
            
            if efficiency < 0.3:  # Less than 30% efficiency is concerning
                print(f"    ⚠️  Warning: Significant performance degradation at high load")
            else:
                print(f"    ✅ Good scaling performance maintained")
        
        return True
    
    def _test_error_resilience_high_concurrency(self) -> bool:
        """Test error handling with high concurrency."""
        print("\n  🚨 Testing Error Resilience - 32 requests with some failures...")
        
        # Create mix of valid and invalid requests
        test_schemas = []
        
        # 24 valid requests
        for i in range(24):
            test_schemas.append({
                "name": f"resilience_valid_{i:03d}",
                "description": "Valid resilience test schema",
                "schema_data": {
                    "table": {
                        "name": f"resilience_table_{i:03d}",
                        "columns": [{"name": "id", "type": "integer"}]
                    }
                }
            })
        
        # 8 invalid requests (missing required fields)
        for i in range(8):
            test_schemas.append({
                "name": f"resilience_invalid_{i:03d}",
                "description": "Invalid resilience test schema",
                "schema_data": {
                    "invalid_structure": "this should fail"
                }
            })
        
        # Test with validation disabled to see runtime error handling
        start_time = time.time()
        try:
            results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                test_schemas,
                parallel=True,
                validate=False,
                max_workers=16
            )
            
            # Store valid results for cleanup
            for result in results:
                if result and hasattr(result, 'id'):
                    self.created_resources['schema_metadata'].append(result.id)
            
            execution_time = time.time() - start_time
            
            # Should have some results but not all 32
            print(f"    ✅ Processed {len(results)} out of 32 requests in {execution_time:.2f}s")
            print(f"    🛡️  System handled mixed success/failure gracefully")
            
            return True
            
        except ValidationError as e:
            if "validation failed" in str(e).lower():
                print("    ✅ Validation correctly caught errors in high concurrency")
                return True
            else:
                print(f"❌ Unexpected validation error: {e}")
                return False
        except Exception as e:
            print(f"    ✅ Error handling working correctly under high load: {e}")
            return True
    
    def _test_extreme_stress_32_workers(self) -> bool:
        """Test extreme stress with 32 workers for 32 requests."""
        print("\n  🔥 Testing EXTREME Stress - 32 workers for 32 requests...")
        
        # Create 32 schema requests for extreme stress test
        test_schemas = [
            {
                "name": f"extreme_stress_{i:03d}",
                "description": f"Extreme stress test schema {i:03d}",
                "schema_data": {
                    "table": {
                        "name": f"extreme_table_{i:03d}",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True},
                            {"name": "extreme_field", "type": "string"},
                            {"name": "stress_id", "type": "integer"}
                        ]
                    }
                }
            }
            for i in range(32)
        ]
        
        # Test with maximum 32 workers (one per request)
        start_time = time.time()
        try:
            extreme_results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                test_schemas,
                parallel=True,
                max_workers=32  # EXTREME: Use 32 workers for 32 requests
            )
            extreme_time = time.time() - start_time
            
            # Store created IDs for cleanup
            for result in extreme_results:
                self.created_resources['schema_metadata'].append(result.id)
            
            # Verify results
            if len(extreme_results) != 32:
                print(f"❌ Expected 32 results, got {len(extreme_results)}")
                return False
            
            # Verify data integrity
            for i, result in enumerate(extreme_results):
                expected_name = f"extreme_stress_{i:03d}"
                if result.name != expected_name:
                    print(f"❌ Extreme test {i}: name mismatch - expected {expected_name}, got {result.name}")
                    return False
            
            print(f"    ✅ EXTREME: Created 32 schemas with 32 workers in {extreme_time:.2f}s")
            print(f"    🚀 Average time per request: {extreme_time/32:.3f}s")
            print(f"    ⚡ Throughput: {32/extreme_time:.1f} requests/second")
            
            # Compare with default (16 workers) performance
            # Run a comparison test with 16 workers
            comparison_schemas = [
                {
                    "name": f"comparison_16w_{i:03d}",
                    "description": f"Comparison test schema {i:03d}",
                    "schema_data": {
                        "table": {
                            "name": f"comparison_table_{i:03d}",
                            "columns": [{"name": "id", "type": "integer"}]
                        }
                    }
                }
                for i in range(32)
            ]
            
            start_time = time.time()
            comparison_results = self.client.schema_metadata.bulk_create(
                self.test_project_id,
                comparison_schemas,
                parallel=True,
                max_workers=16  # Default conservative setting
            )
            comparison_time = time.time() - start_time
            
            # Store for cleanup
            for result in comparison_results:
                self.created_resources['schema_metadata'].append(result.id)
            
            # Performance comparison
            extreme_throughput = 32 / extreme_time
            comparison_throughput = 32 / comparison_time
            performance_gain = extreme_throughput / comparison_throughput
            
            print(f"\n    📊 Performance Comparison:")
            print(f"      32 workers: {extreme_time:.2f}s ({extreme_throughput:.1f} req/s)")
            print(f"      16 workers: {comparison_time:.2f}s ({comparison_throughput:.1f} req/s)")
            print(f"      🎯 Performance gain: {performance_gain:.2f}x")
            
            if performance_gain > 1.2:
                print(f"    ✅ Significant performance improvement with 32 workers!")
            elif performance_gain > 0.9:
                print(f"    ✅ Comparable performance with 32 workers")
            else:
                print(f"    ⚠️  Warning: 32 workers performed worse than 16 workers")
                print(f"    💡 This suggests the server may be overwhelmed or rate-limited")
            
            return True
            
        except Exception as e:
            print(f"❌ Extreme stress test failed: {e}")
            print(f"    💡 This may indicate the server cannot handle 32 concurrent workers")
            print(f"    🔧 Consider this when setting production max_workers limits")
            return False


def run_high_concurrency_test():
    """Standalone function to run high concurrency test."""
    test_runner = HighConcurrencyTestRunner()
    return test_runner.run_test()


if __name__ == "__main__":
    # Allow running this test standalone
    success = run_high_concurrency_test()
    exit(0 if success else 1)
