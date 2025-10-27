"""
Custom tools resource for the Text2Everything SDK.
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING, BinaryIO, Union
from pathlib import Path
from text2everything_sdk.models.custom_tools import (
    CustomTool,
    CustomToolCreate,
    CustomToolUpdate
)
from text2everything_sdk.exceptions import ValidationError
from text2everything_sdk.resources.base import BaseResource

if TYPE_CHECKING:
    from text2everything_sdk.client import Text2EverythingClient


class CustomToolsResource(BaseResource):
    """Resource for managing custom tools with Python script uploads."""
    
    def __init__(self, client: Text2EverythingClient):
        super().__init__(client)
    
    def create(self, project_id: str, name: str, description: str, 
              files: List[Union[str, Path, BinaryIO]]) -> CustomTool:
        """Create a new custom tool with uploaded Python script files.
        
        Args:
            project_id: The project ID
            name: Name of the custom tool
            description: Description of the custom tool
            files: List of file paths or file objects to upload
        
        Returns:
            The created custom tool
            
        Example:
            ```python
            # Upload files by path
            tool = client.custom_tools.create(
                project_id="proj-123",
                name="Data Analysis Tool",
                description="Custom tool for advanced data analysis",
                files=["analysis.py", "utils.py"]
            )
            
            # Upload file objects
            with open("script.py", "rb") as f:
                tool = client.custom_tools.create(
                    project_id="proj-123",
                    name="Script Tool",
                    description="Custom script tool",
                    files=[f]
                )
            ```
        """
        # Basic validation
        if not name or not name.strip():
            raise ValidationError("Tool name cannot be empty")
        
        if not description or not description.strip():
            raise ValidationError("Tool description cannot be empty")
        
        if not files:
            raise ValidationError("At least one file must be provided")
        
        # Prepare multipart form data
        form_data = {
            "name": name,
            "description": description
        }
        
        # Prepare files for upload
        file_data = []
        opened_files = []  # Track files we opened so we can close them
        
        for file_item in files:
            if isinstance(file_item, (str, Path)):
                # File path - we need to open it
                file_path = Path(file_item)
                if not file_path.exists():
                    raise ValidationError(f"File not found: {file_path}")
                file_obj = open(file_path, "rb")
                opened_files.append(file_obj)  # Track for cleanup
                file_data.append(("files", (file_path.name, file_obj, "text/plain")))
            else:
                # File object - use as-is, don't close it
                filename = getattr(file_item, 'name', 'script.py')
                file_data.append(("files", (filename, file_item, "text/plain")))
        
        try:
            response = self._client.post_multipart(
                f"/projects/{project_id}/custom-tools",
                data=form_data,
                files=file_data
            )
            return CustomTool(**response)
        finally:
            # Close only the files we opened
            for file_obj in opened_files:
                try:
                    file_obj.close()
                except:
                    pass
    
    def get(self, project_id: str, tool_id: str) -> CustomTool:
        """Get a specific custom tool.
        
        Args:
            project_id: The project ID
            tool_id: The custom tool ID
            
        Returns:
            The custom tool details
            
        Example:
            ```python
            tool = client.custom_tools.get(project_id, tool_id)
            print(f"Tool: {tool.name}")
            print(f"Documents: {len(tool.documents)}")
            ```
        """
        response = self._client.get(f"/projects/{project_id}/custom-tools/{tool_id}")
        return CustomTool(**response)
    
    def list(self, project_id: str, skip: int = 0, limit: int = 100) -> List[CustomTool]:
        """List all custom tools for a project.
        
        Args:
            project_id: The project ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of custom tools
            
        Example:
            ```python
            tools = client.custom_tools.list(project_id)
            for tool in tools:
                print(f"{tool.name}: {tool.description}")
            ```
        """
        endpoint = f"/projects/{project_id}/custom-tools"
        params = {"limit": limit, "skip": skip}
        return self._paginate(endpoint, params=params, model_class=CustomTool)
    
    def update(self, project_id: str, tool_id: str, name: str = None, 
              description: str = None, files: List[Union[str, Path, BinaryIO]] = None) -> CustomTool:
        """Update a custom tool.
        
        Args:
            project_id: The project ID
            tool_id: The custom tool ID to update
            name: Optional new name
            description: Optional new description
            files: Optional new files to replace existing ones
            
        Returns:
            The updated custom tool
            
        Example:
            ```python
            # Update metadata only
            tool = client.custom_tools.update(
                project_id, tool_id,
                name="Updated Tool Name",
                description="Updated description"
            )
            
            # Update files
            tool = client.custom_tools.update(
                project_id, tool_id,
                files=["new_script.py", "updated_utils.py"]
            )
            ```
        """
        # Prepare multipart form data
        form_data = {}
        if name is not None:
            form_data["name"] = name
        if description is not None:
            form_data["description"] = description
        
        file_data = []
        opened_files = []  # Track files we opened so we can close them
        
        if files:
            # Prepare files for upload
            for file_item in files:
                if isinstance(file_item, (str, Path)):
                    # File path - we need to open it
                    file_path = Path(file_item)
                    if not file_path.exists():
                        raise ValidationError(f"File not found: {file_path}")
                    file_obj = open(file_path, "rb")
                    opened_files.append(file_obj)  # Track for cleanup
                    file_data.append(("files", (file_path.name, file_obj, "text/plain")))
                else:
                    # File object - use as-is, don't close it
                    filename = getattr(file_item, 'name', 'script.py')
                    file_data.append(("files", (filename, file_item, "text/plain")))
        
        try:
            response = self._client.put_multipart(
                f"/projects/{project_id}/custom-tools/{tool_id}",
                data=form_data,
                files=file_data if file_data else None
            )
            return CustomTool(**response)
        finally:
            # Close only the files we opened
            for file_obj in opened_files:
                try:
                    file_obj.close()
                except:
                    pass
    
    def delete(self, project_id: str, tool_id: str) -> bool:
        """Delete a custom tool and its associated collection.
        
        Args:
            project_id: The project ID
            tool_id: The custom tool ID to delete
            
        Returns:
            True if deletion was successful
            
        Example:
            ```python
            success = client.custom_tools.delete(project_id, tool_id)
            ```
        """
        self._client.delete(f"/projects/{project_id}/custom-tools/{tool_id}")
        return True
    
    def create_from_directory(self, project_id: str, name: str, description: str, 
                             directory_path: Union[str, Path]) -> CustomTool:
        """Create a custom tool by uploading all Python files from a directory.
        
        Args:
            project_id: The project ID
            name: Name of the custom tool
            description: Description of the custom tool
            directory_path: Path to directory containing Python files
            
        Returns:
            The created custom tool
            
        Example:
            ```python
            tool = client.custom_tools.create_from_directory(
                project_id="proj-123",
                name="Analysis Suite",
                description="Complete data analysis toolkit",
                directory_path="./analysis_scripts"
            )
            ```
        """
        dir_path = Path(directory_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValidationError(f"Directory not found: {dir_path}")
        
        # Find all Python files in the directory
        python_files = list(dir_path.glob("*.py"))
        if not python_files:
            raise ValidationError(f"No Python files found in directory: {dir_path}")
        
        return self.create(project_id, name, description, python_files)
    
    def update_metadata(self, project_id: str, tool_id: str, 
                       update_data: CustomToolUpdate) -> CustomTool:
        """Update only the metadata (name/description) of a custom tool.
        
        Args:
            project_id: The project ID
            tool_id: The custom tool ID
            update_data: The metadata updates
            
        Returns:
            The updated custom tool
            
        Example:
            ```python
            update_data = CustomToolUpdate(
                name="New Tool Name",
                description="Updated description"
            )
            tool = client.custom_tools.update_metadata(project_id, tool_id, update_data)
            ```
        """
        return self.update(
            project_id, 
            tool_id, 
            name=update_data.name, 
            description=update_data.description
        )
    
    def replace_files(self, project_id: str, tool_id: str, 
                     files: List[Union[str, Path, BinaryIO]]) -> CustomTool:
        """Replace all files in a custom tool.
        
        Args:
            project_id: The project ID
            tool_id: The custom tool ID
            files: New files to replace existing ones
            
        Returns:
            The updated custom tool
            
        Example:
            ```python
            tool = client.custom_tools.replace_files(
                project_id, tool_id, 
                ["new_main.py", "new_utils.py"]
            )
            ```
        """
        return self.update(project_id, tool_id, files=files)
