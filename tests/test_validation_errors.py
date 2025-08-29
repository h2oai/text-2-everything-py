"""
Validation error handling functional tests.
"""

from .base_test import BaseTestRunner
from text2everything_sdk.exceptions import ValidationError


class ValidationErrorsTestRunner(BaseTestRunner):
    """Test runner for validation error handling."""
    
    def run_test(self) -> bool:
        """Test that validation errors are properly raised."""
        print("\n11. Testing Validation Error Handling...")
        
        try:
            # Test invalid table schema (missing columns)
            try:
                self.client.schema_metadata.create(
                    self.test_project_id,
                    name="invalid_table",
                    description="Table missing required columns",
                    schema_data={
                        "table": {
                            "name": "invalid_table"
                            # Missing required 'columns' field
                        }
                    }
                )
                print("❌ Should have failed validation for missing columns")
                return False
                
            except ValidationError as e:
                print("✅ Correctly caught validation error for missing columns")
            
            # Test invalid dimension schema (missing content)
            try:
                self.client.schema_metadata.create(
                    self.test_project_id,
                    name="invalid_dimension",
                    description="Dimension missing required content",
                    schema_data={
                        "table": {
                            "dimension": {
                                "name": "invalid_dimension"
                                # Missing required 'content' field
                            }
                        }
                    }
                )
                print("❌ Should have failed validation for missing dimension content")
                return False
                
            except ValidationError as e:
                print("✅ Correctly caught validation error for missing dimension content")
            
            # Test invalid golden example (empty query)
            try:
                self.client.golden_examples.create(
                    self.test_project_id,
                    description="Example with empty query",
                    user_query="",  # Empty query should fail
                    sql_query="SELECT 1;"
                )
                print("❌ Should have failed validation for empty user query")
                return False
                
            except ValidationError as e:
                print("✅ Correctly caught validation error for empty user query")
            
            return True
            
        except Exception as e:
            print(f"❌ Validation error testing failed: {e}")
            return False
