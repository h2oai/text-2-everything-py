"""
Test for verifying that create() returns single object for small schemas.

This is a focused test to verify the SDK properly normalizes API responses:
- Small schemas (≤8 columns) should return a single SchemaMetadataResponse object
- Large schemas (>8 columns) should return a list of SchemaMetadataResponse objects
"""

from .base_test import BaseTestRunner


class SmallSchemaReturnTypeTestRunner(BaseTestRunner):
    """Test runner for verifying create() return type normalization."""
    
    def run_test(self) -> bool:
        """Test that small schemas return single object, not list."""
        print("\n📝 Testing create() return type for small schemas...")
        
        try:
            # Test case: Small schema (4 columns, ≤8) should return single object
            print("\n  Creating small schema (4 columns)...")
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
                print(f"    ❌ FAIL: Expected single object for ≤8 columns, got list with {len(result)} items")
                if result:
                    print(f"       First item type: {type(result[0]).__name__}")
                    print(f"       First item split_group_id: {result[0].split_group_id}")
                return False
            
            # Verify result is a single SchemaMetadataResponse
            print(f"    ✅ Got single object as expected")
            print(f"       Result type: {type(result).__name__}")
            print(f"       Schema ID: {result.id}")
            print(f"       split_group_id: {result.split_group_id}")
            
            # Track for cleanup
            self.created_resources['schema_metadata'].append(result.id)
            
            # Verify split fields are None for non-split schema
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
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
