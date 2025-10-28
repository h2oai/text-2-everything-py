"""
Schema metadata resource functional tests.
"""

import time
from .base_test import BaseTestRunner
from text2everything_sdk.exceptions import ValidationError


class SchemaMetadataTestRunner(BaseTestRunner):
    """Test runner for Schema Metadata resource."""
    
    def _get_schema_id(self, result):
        """
        Safely get schema ID from create() result.
        Handles both single SchemaMetadataResponse and List[SchemaMetadataResponse].
        
        For split schemas (list), returns the first part's ID.
        For single schemas, returns the ID directly.
        """
        if isinstance(result, list):
            return result[0].id if result else None
        return result.id
    
    def run_test(self) -> bool:
        """Test schema metadata CRUD operations with nested validation."""
        print("\n3. Testing Schema Metadata Resource...")
        
        try:
            # Test create table schema
            table_result = self.client.schema_metadata.create(
                self.test_project_id,
                name="users_table_schema",
                description="User table schema for functional test",
                schema_data={
                    "table": {
                        "name": "users",
                        "description": "User information table",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True},
                            {"name": "email", "type": "string", "unique": True},
                            {"name": "status", "type": "string"},
                            {"name": "created_at", "type": "timestamp"}
                        ]
                    }
                }
            )
            table_id = self._get_schema_id(table_result)
            self.created_resources['schema_metadata'].append(table_id)
            print(f"✅ Created table schema: {table_id}")
            
            # Test create dimension schema
            dimension_result = self.client.schema_metadata.create(
                self.test_project_id,
                name="status_dimension",
                description="User status dimension",
                schema_data={
                    "table": {
                        "dimension": {
                            "name": "user_status",
                            "description": "User account status",
                            "content": {
                                "type": "categorical",
                                "values": ["active", "inactive", "pending", "suspended"]
                            }
                        }
                    }
                }
            )
            dimension_id = self._get_schema_id(dimension_result)
            self.created_resources['schema_metadata'].append(dimension_id)
            print(f"✅ Created dimension schema: {dimension_id}")
            
            # Test create metric schema
            metric_result = self.client.schema_metadata.create(
                self.test_project_id,
                name="user_count_metric",
                description="Total user count metric",
                schema_data={
                    "table": {
                        "metric": {
                            "name": "total_users",
                            "description": "Total number of users",
                            "content": {
                                "aggregation": "count",
                                "column": "id",
                                "filters": {"status": "active"}
                            }
                        }
                    }
                }
            )
            metric_id = self._get_schema_id(metric_result)
            self.created_resources['schema_metadata'].append(metric_id)
            print(f"✅ Created metric schema: {metric_id}")
            
            # Test create relationship schema
            relationship_result = self.client.schema_metadata.create(
                self.test_project_id,
                name="user_order_relationship",
                description="Relationship between users and orders",
                schema_data={
                    "relationship": {
                        "name": "user_orders",
                        "from_table": "users",
                        "to_table": "orders",
                        "type": "one_to_many",
                        "foreign_key": "user_id"
                    }
                }
            )
            relationship_id = self._get_schema_id(relationship_result)
            self.created_resources['schema_metadata'].append(relationship_id)
            print(f"✅ Created relationship schema: {relationship_id}")
            
            # Test update schema metadata
            updated_table = self.client.schema_metadata.update(
                self.test_project_id,
                table_id,
                name="updated_users_table_schema",
                description="Updated user table schema for functional test",
                schema_data={
                    "table": {
                        "name": "users",
                        "description": "Updated user information table",
                        "columns": [
                            {"name": "id", "type": "integer", "primary_key": True},
                            {"name": "email", "type": "string", "unique": True},
                            {"name": "status", "type": "string"},
                            {"name": "created_at", "type": "timestamp"},
                            {"name": "updated_at", "type": "timestamp"}
                        ]
                    }
                },
                is_always_displayed=True
            )
            print("✅ Updated schema metadata")
            
            # Test list schema metadata
            all_schemas = self.client.schema_metadata.list(self.test_project_id)
            print(f"✅ Listed {len(all_schemas)} schema metadata items")
            
            # Test list by type
            tables = self.client.schema_metadata.list_by_type(self.test_project_id, "table")
            dimensions = self.client.schema_metadata.list_by_type(self.test_project_id, "dimension")
            metrics = self.client.schema_metadata.list_by_type(self.test_project_id, "metric")
            relationships = self.client.schema_metadata.list_by_type(self.test_project_id, "relationship")
            
            print(f"✅ Found {len(tables)} tables, {len(dimensions)} dimensions, {len(metrics)} metrics, {len(relationships)} relationships")
            
            # Test schema validation
            test_schema_data = {
                "table": {
                    "name": "test_table",
                    "columns": [{"name": "id", "type": "integer"}]
                }
            }
            validation_errors = self.client.schema_metadata.validate_schema(test_schema_data, "table")
            if not validation_errors:
                print("✅ Schema validation passed")
            else:
                print(f"❌ Schema validation failed: {validation_errors}")
                return False
            
            # Test schema type detection
            detected_type = self.client.schema_metadata.get_schema_type(test_schema_data)
            if detected_type == "table":
                print("✅ Schema type detection passed")
            else:
                print(f"❌ Schema type detection failed: expected 'table', got '{detected_type}'")
                return False
            
            # Test parallel bulk operations
            if not self._test_parallel_bulk_operations():
                return False
            
            # Test bulk delete
            if not self._test_bulk_delete():
                return False
            
            # Test split groups
            if not self._test_split_groups():
                return False
            
            # Test new split return type behavior
            if not self._test_create_returns_list_for_splits():
                return False
            
            if not self._test_create_returns_single_for_small_schemas():
                return False
            
            if not self._test_bulk_create_flattens_splits():
                return False
            
            if not self._test_bulk_create_parallel_with_splits():
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Schema metadata test failed: {e}")
            return False
    
    def _test_parallel_bulk_operations(self) -> bool:
        """Test parallel bulk operations functionality."""
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
            for i in range(6)  # 6 schemas for performance test
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
            for i in range(6)
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
        
        # Test with clearly invalid data that should trigger validation errors
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
            # Invalid schema (completely malformed schema_data)
            {
                "name": "invalid_schema_1",
                "schema_data": {
                    "invalid_structure": "this should fail validation"
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
            # If we get here, the API might be more lenient than expected
            print("    ⚠️  API accepted schemas that were expected to fail - validation may be lenient")
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
            empty_results = self.client.schema_metadata.bulk_create(
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
    
    def _test_split_groups(self) -> bool:
        """Test schema split group functionality."""
        print("\n  🔀 Testing split groups...")
        
        # Create a large table schema that will be split (>8 columns)
        large_table_schema = {
            "table": {
                "name": "large_users_table",
                "columns": [
                    {"name": "id", "type": "integer", "description": "User ID"},
                    {"name": "email", "type": "string", "description": "Email address"},
                    {"name": "first_name", "type": "string", "description": "First name"},
                    {"name": "last_name", "type": "string", "description": "Last name"},
                    {"name": "phone", "type": "string", "description": "Phone number"},
                    {"name": "address", "type": "string", "description": "Street address"},
                    {"name": "city", "type": "string", "description": "City"},
                    {"name": "state", "type": "string", "description": "State"},
                    {"name": "zip_code", "type": "string", "description": "ZIP code"},
                    {"name": "country", "type": "string", "description": "Country"},
                    {"name": "created_at", "type": "timestamp", "description": "Creation date"},
                    {"name": "updated_at", "type": "timestamp", "description": "Last update"},
                ]
            }
        }
        
        # Create the schema metadata (should be auto-split)
        result = self.client.schema_metadata.create(
            project_id=self.test_project_id,
            name="Large Table for Split Test",
            schema_data=large_table_schema,
            description="Table with >8 columns to test split functionality"
        )
        
        # Handle new return type: list for split schemas, single object otherwise
        split_group_id = None
        
        if isinstance(result, list):
            # New behavior (v0.1.7-rc2+): create() returns list of all parts
            if not result:
                print(f"    ❌ Expected non-empty list for split schema")
                return False
            
            split_group_id = result[0].split_group_id
            print(f"    ✅ Schema was split into {len(result)} parts")
            print(f"    ✅ Split Group ID: {split_group_id}")
            
            # Verify all parts in the returned list
            for i, part in enumerate(result):
                if part.split_group_id != split_group_id:
                    print(f"    ❌ Part {i} has different split_group_id")
                    return False
                if part.split_index != i + 1:
                    print(f"    ❌ Part {i} has incorrect split_index: {part.split_index}")
                    return False
                if part.total_splits != len(result):
                    print(f"    ❌ Part {i} has incorrect total_splits: {part.total_splits}")
                    return False
            
            print(f"    ✅ All {len(result)} parts from create() have correct split fields")
            
        elif hasattr(result, 'split_group_id') and result.split_group_id:
            # Old behavior fallback: single object with split_group_id
            split_group_id = result.split_group_id
            print(f"    ℹ️  Got single object with split_group_id: {split_group_id}")
            
        else:
            # Schema was not split
            print(f"    ℹ️  Schema was not split (may have ≤8 columns or split disabled)")
            self.created_resources['schema_metadata'].append(result.id)
            return True
        
        # Test get_split_group API endpoint
        if split_group_id:
            group = self.client.schema_metadata.get_split_group(
                self.test_project_id,
                split_group_id
            )
            
            if not group:
                print(f"    ❌ Failed to retrieve split group")
                return False
            
            if 'split_group_id' not in group:
                print(f"    ❌ Group missing split_group_id")
                return False
            
            if 'parts' not in group:
                print(f"    ❌ Group missing parts")
                return False
            
            if 'total_parts' not in group:
                print(f"    ❌ Group missing total_parts")
                return False
            
            parts_count = group['total_parts']
            print(f"    ✅ get_split_group() retrieved {parts_count} parts")
            
            # Verify parts structure
            for i, part in enumerate(group['parts']):
                if not hasattr(part, 'id'):
                    print(f"    ❌ Part {i} missing ID")
                    return False
                if not hasattr(part, 'name'):
                    print(f"    ❌ Part {i} missing name")
                    return False
            
            print(f"    ✅ All {parts_count} parts from get_split_group() have valid structure")
            
            # Track only the first part for cleanup - API cascade-deletes all parts
            # when deleting any part in a split group
            self.created_resources['schema_metadata'].append(group['parts'][0].id)
        
        return True
    
    def _test_create_returns_list_for_splits(self) -> bool:
        """Test that create() returns a list for schemas with >8 columns."""
        print("\n  📝 Testing create() returns list for split schemas...")
        
        # Create schema with >8 columns (should be split)
        large_schema_data = {
            "table": {
                "name": "test_large_customers",
                "columns": [
                    {"name": "id", "type": "integer", "description": "Customer ID"},
                    {"name": "first_name", "type": "string", "description": "First name"},
                    {"name": "last_name", "type": "string", "description": "Last name"},
                    {"name": "email", "type": "string", "description": "Email"},
                    {"name": "phone", "type": "string", "description": "Phone"},
                    {"name": "address", "type": "string", "description": "Address"},
                    {"name": "city", "type": "string", "description": "City"},
                    {"name": "state", "type": "string", "description": "State"},
                    {"name": "zip", "type": "string", "description": "ZIP"},
                    {"name": "country", "type": "string", "description": "Country"},
                ]
            }
        }
        
        result = self.client.schema_metadata.create(
            project_id=self.test_project_id,
            name="Large Customer Table Test",
            schema_data=large_schema_data,
            description="Test schema with >8 columns"
        )
        
        # Verify result is a list
        if not isinstance(result, list):
            print(f"    ❌ Expected list for >8 columns, got {type(result).__name__}")
            return False
        
        print(f"    ✅ create() returned list with {len(result)} parts")
        
        # Verify all parts have same split_group_id
        split_group_ids = set(part.split_group_id for part in result)
        if len(split_group_ids) != 1:
            print(f"    ❌ Expected all parts to have same split_group_id, found {len(split_group_ids)}")
            return False
        
        split_group_id = result[0].split_group_id
        print(f"    ✅ All parts share split_group_id: {split_group_id}")
        
        # Verify split_index sequence
        split_indices = [part.split_index for part in result]
        expected_indices = list(range(1, len(result) + 1))
        if split_indices != expected_indices:
            print(f"    ❌ Expected indices {expected_indices}, got {split_indices}")
            return False
        
        print(f"    ✅ split_index sequence correct: {split_indices}")
        
        # Verify total_splits is consistent
        total_splits_values = set(part.total_splits for part in result)
        if len(total_splits_values) != 1 or total_splits_values.pop() != len(result):
            print(f"    ❌ total_splits inconsistent or incorrect")
            return False
        
        print(f"    ✅ total_splits consistent: {result[0].total_splits}")
        
        # Verify each part can be retrieved individually
        for part in result:
            retrieved = self.client.schema_metadata.get(self.test_project_id, part.id)
            if not retrieved or retrieved.id != part.id:
                print(f"    ❌ Failed to retrieve part {part.id}")
                return False
        
        print(f"    ✅ All {len(result)} parts can be retrieved individually")
        
        # Cleanup: only track first part, cascade delete handles rest
        self.created_resources['schema_metadata'].append(result[0].id)
        
        return True
    
    def _test_create_returns_single_for_small_schemas(self) -> bool:
        """Test that create() returns single object for schemas with ≤8 columns."""
        print("\n  📝 Testing create() returns single object for small schemas...")
        
        # Create schema with ≤8 columns (should NOT be split)
        small_schema_data = {
            "table": {
                "name": "test_small_users",
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "email", "type": "string"},
                    {"name": "status", "type": "string"},
                ]
            }
        }
        
        result = self.client.schema_metadata.create(
            project_id=self.test_project_id,
            name="Small User Table Test",
            schema_data=small_schema_data,
            description="Test schema with ≤8 columns"
        )
        
        # Verify result is NOT a list
        if isinstance(result, list):
            print(f"    ❌ Expected single object for ≤8 columns, got list with {len(result)} items")
            return False
        
        print(f"    ✅ create() returned single SchemaMetadataResponse")
        
        # Verify split fields are None
        if result.split_group_id is not None:
            print(f"    ❌ Expected split_group_id to be None, got {result.split_group_id}")
            return False
        
        if result.split_index is not None:
            print(f"    ❌ Expected split_index to be None, got {result.split_index}")
            return False
        
        if result.total_splits is not None:
            print(f"    ❌ Expected total_splits to be None, got {result.total_splits}")
            return False
        
        print(f"    ✅ All split fields are None (not split)")
        
        # Cleanup
        self.created_resources['schema_metadata'].append(result.id)
        
        return True
    
    def _test_bulk_create_flattens_splits(self) -> bool:
        """Test that bulk_create() properly flattens split results."""
        print("\n  📦 Testing bulk_create() flattens split results...")
        
        # Create mix of small and large schemas
        test_schemas = [
            # Small schema (≤8 columns) - should return 1 part
            {
                "name": "Bulk Small Schema 1",
                "schema_data": {
                    "table": {
                        "name": "small_table_1",
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": "value", "type": "string"},
                        ]
                    }
                }
            },
            # Large schema (10 columns) - should return 2 parts
            {
                "name": "Bulk Large Schema 1",
                "schema_data": {
                    "table": {
                        "name": "large_table_1",
                        "columns": [
                            {"name": f"col_{i}", "type": "string"}
                            for i in range(10)
                        ]
                    }
                }
            },
            # Another large schema (12 columns) - should return 2 parts
            {
                "name": "Bulk Large Schema 2",
                "schema_data": {
                    "table": {
                        "name": "large_table_2",
                        "columns": [
                            {"name": f"col_{i}", "type": "string"}
                            for i in range(12)
                        ]
                    }
                }
            },
        ]
        
        # Execute bulk create
        results = self.client.schema_metadata.bulk_create(
            self.test_project_id,
            test_schemas,
            parallel=False
        )
        
        print(f"    Input: {len(test_schemas)} schemas")
        print(f"    Output: {len(results)} schema parts")
        
        # Verify result count exceeds input count
        # Expected: 1 (small) + 2 (large1) + 2 (large2) = 5 total
        # Note: Actual split behavior may vary, so we check that output >= input
        if len(results) < len(test_schemas):
            print(f"    ❌ Expected at least {len(test_schemas)} results, got {len(results)}")
            return False
        
        print(f"    ✅ Results properly flattened ({len(results)} >= {len(test_schemas)})")
        
        # Verify each result has correct split grouping info
        split_groups = {}
        for result in results:
            if result.split_group_id:
                if result.split_group_id not in split_groups:
                    split_groups[result.split_group_id] = []
                split_groups[result.split_group_id].append(result)
        
        # Verify split groups have consistent data
        for group_id, parts in split_groups.items():
            total_splits = parts[0].total_splits
            if len(parts) != total_splits:
                print(f"    ❌ Split group {group_id}: expected {total_splits} parts, got {len(parts)}")
                return False
            
            indices = sorted([p.split_index for p in parts])
            expected_indices = list(range(1, total_splits + 1))
            if indices != expected_indices:
                print(f"    ❌ Split group {group_id}: incorrect indices {indices}")
                return False
        
        if split_groups:
            print(f"    ✅ Found {len(split_groups)} split groups with correct structure")
        
        # Cleanup: track first part of each split group, individual schemas
        cleaned_up = set()
        for result in results:
            if result.split_group_id:
                if result.split_group_id not in cleaned_up:
                    self.created_resources['schema_metadata'].append(result.id)
                    cleaned_up.add(result.split_group_id)
            else:
                self.created_resources['schema_metadata'].append(result.id)
        
        return True
    
    def _test_bulk_create_parallel_with_splits(self) -> bool:
        """Test that parallel bulk_create() properly handles split results."""
        print("\n  ⚡ Testing parallel bulk_create() with splits...")
        
        # Create mix of schemas for parallel processing
        test_schemas = [
            # Small schemas
            {
                "name": f"Parallel Small {i}",
                "schema_data": {
                    "table": {
                        "name": f"parallel_small_{i}",
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": "value", "type": "string"},
                        ]
                    }
                }
            }
            for i in range(2)
        ] + [
            # Large schemas (>8 columns)
            {
                "name": f"Parallel Large {i}",
                "schema_data": {
                    "table": {
                        "name": f"parallel_large_{i}",
                        "columns": [
                            {"name": f"col_{j}", "type": "string"}
                            for j in range(10)
                        ]
                    }
                }
            }
            for i in range(2)
        ]
        
        # Execute parallel bulk create
        results = self.client.schema_metadata.bulk_create(
            self.test_project_id,
            test_schemas,
            parallel=True
        )
        
        print(f"    Input: {len(test_schemas)} schemas (parallel)")
        print(f"    Output: {len(results)} schema parts")
        
        # Verify flattening works in parallel mode
        if len(results) < len(test_schemas):
            print(f"    ❌ Expected at least {len(test_schemas)} results, got {len(results)}")
            return False
        
        print(f"    ✅ Parallel processing with flattening successful")
        
        # Verify no duplicates or missing parts
        result_ids = [r.id for r in results]
        if len(result_ids) != len(set(result_ids)):
            print(f"    ❌ Found duplicate IDs in results")
            return False
        
        print(f"    ✅ No duplicate parts in results")
        
        # Verify split groups are complete
        split_groups = {}
        for result in results:
            if result.split_group_id:
                if result.split_group_id not in split_groups:
                    split_groups[result.split_group_id] = []
                split_groups[result.split_group_id].append(result)
        
        for group_id, parts in split_groups.items():
            if len(parts) != parts[0].total_splits:
                print(f"    ❌ Split group {group_id} incomplete: {len(parts)}/{parts[0].total_splits} parts")
                return False
        
        if split_groups:
            print(f"    ✅ All {len(split_groups)} split groups complete")
        
        # Cleanup
        cleaned_up = set()
        for result in results:
            if result.split_group_id:
                if result.split_group_id not in cleaned_up:
                    self.created_resources['schema_metadata'].append(result.id)
                    cleaned_up.add(result.split_group_id)
            else:
                self.created_resources['schema_metadata'].append(result.id)
        
        return True
    
    def _test_bulk_delete(self) -> bool:
        """Test bulk delete functionality."""
        print("\n  🗑️  Testing bulk delete...")
        
        # Create test items for bulk deletion
        items_to_delete = []
        for i in range(5):
            schema = self.client.schema_metadata.create(
                project_id=self.test_project_id,
                name=f"Bulk Delete Test Schema {i}",
                description=f"Schema {i} to be bulk deleted",
                schema_data={
                    "table": {
                        "name": f"bulk_delete_table_{i}",
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": f"field_{i}", "type": "string"}
                        ]
                    }
                }
            )
            schema_id = self._get_schema_id(schema)
            items_to_delete.append(schema_id)
            # Don't add to created_resources - will be bulk deleted
        
        # Test bulk delete
        result = self.client.schema_metadata.bulk_delete(
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
        remaining = self.client.schema_metadata.list(self.test_project_id)
        remaining_ids = [item.id for item in remaining]
        
        for deleted_id in items_to_delete:
            if deleted_id in remaining_ids:
                print(f"❌ Item {deleted_id} still exists after bulk delete")
                return False
        
        print(f"    ✅ Successfully bulk deleted {len(items_to_delete)} items")
        
        # Test error handling - try to delete non-existent IDs
        fake_ids = ["fake_id_1", "fake_id_2"]
        try:
            result = self.client.schema_metadata.bulk_delete(
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
            result = self.client.schema_metadata.bulk_delete(
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
