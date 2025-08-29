"""
Custom tools resource functional tests.
"""

import tempfile
import os
from .base_test import BaseTestRunner
from text2everything_sdk.models.custom_tools import CustomToolCreate, CustomToolUpdate


class CustomToolsTestRunner(BaseTestRunner):
    """Test runner for Custom Tools resource."""
    
    def run_test(self) -> bool:
        """Test custom tools operations."""
        print("\n10. Testing Custom Tools Resource...")
        
        try:
            # Create a simple test Python script content
            test_script_content = '''
def hello_world():
    """A simple test function."""
    return "Hello from custom tool!"

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    print(hello_world())
    print(f"2 + 3 = {add_numbers(2, 3)}")
'''
            
            # Create a temporary file with the script content
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                    temp_file.write(test_script_content)
                    temp_file_path = temp_file.name
                
                # Test create custom tool with correct method signature
                tool_result = self.client.custom_tools.create(
                    self.test_project_id,
                    name="test_python_tool",
                    description="A simple Python tool for functional testing",
                    files=[temp_file_path]
                )
                self.created_resources['custom_tools'].append(tool_result.id)
                print(f"✅ Created custom tool: {tool_result.id}")
                
            finally:
                # Clean up temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
            # Test list custom tools
            tools = self.client.custom_tools.list(self.test_project_id)
            print(f"✅ Listed {len(tools)} custom tools")
            
            # Test get custom tool
            retrieved_tool = self.client.custom_tools.get(self.test_project_id, tool_result.id)
            print(f"✅ Retrieved custom tool: {retrieved_tool.name}")
            
            # Test update custom tool
            updated_tool = self.client.custom_tools.update(
                self.test_project_id,
                tool_result.id,
                description="Updated: Enhanced Python tool for testing"
            )
            print("✅ Updated custom tool description")
            
            # Test create from directory
            temp_dir = None
            try:
                # Create a temporary directory with multiple Python files
                temp_dir = tempfile.mkdtemp()
                
                # Create multiple test files
                file1_content = '''
def utility_function():
    """A utility function."""
    return "Utility result"
'''
                file2_content = '''
def main_function():
    """Main function."""
    return "Main result"
'''
                
                with open(os.path.join(temp_dir, "utils.py"), "w") as f:
                    f.write(file1_content)
                with open(os.path.join(temp_dir, "main.py"), "w") as f:
                    f.write(file2_content)
                
                # Test create from directory
                dir_tool = self.client.custom_tools.create_from_directory(
                    self.test_project_id,
                    name="directory_tool",
                    description="Tool created from directory",
                    directory_path=temp_dir
                )
                self.created_resources['custom_tools'].append(dir_tool.id)
                print(f"✅ Created custom tool from directory: {dir_tool.id}")
                
            finally:
                # Clean up temporary directory
                if temp_dir and os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
            
            print("⚠️  Skipping download test (no download endpoint available in API)")
            
            return True
            
        except Exception as e:
            print(f"❌ Custom tools test failed: {e}")
            # Print more details if it's a validation error
            if hasattr(e, 'response_data'):
                print(f"Response data: {e.response_data}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
            return False
