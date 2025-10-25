"""
Projects resource for the Text2Everything SDK.
"""

from typing import List, Optional, Dict, Any, Union
from .base import BaseResource
from models.projects import Project, ProjectCreate, ProjectUpdate, Collection


class ProjectsResource(BaseResource):
    """
    Client for managing projects in the Text2Everything API.
    
    Projects are the top-level containers for organizing contexts, schema metadata,
    golden examples, and other resources.
    """
    
    def list(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None
    ) -> List[Project]:
        """
        List all projects.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50)
            search: Search term to filter projects by name
            
        Returns:
            List of Project instances
            
        Example:
            >>> projects = client.projects.list()
            >>> for project in projects:
            ...     print(f"{project.name}: {project.description}")
        """
        # Backend expects skip/limit. Convert page/per_page to skip/limit.
        params = {
            'skip': (page - 1) * per_page,
            'limit': per_page,
        }
        if search:
            # Backend uses 'q' as free-text filter
            params['q'] = search
        return self._paginate("projects", params=params, model_class=Project)
    
    def get(self, project_id: str) -> Project:
        """
        Get a specific project by ID.
        
        Args:
            project_id: The project ID
            
        Returns:
            Project instance
            
        Raises:
            NotFoundError: If project doesn't exist
            
        Example:
            >>> project = client.projects.get("proj_123")
            >>> print(project.name)
        """
        endpoint = self._build_endpoint("projects", project_id)
        response = self._client.get(endpoint)
        return self._create_model_instance(response, Project)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Project:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            **kwargs: Additional project fields
            
        Returns:
            Created Project instance
            
        Example:
            >>> project = client.projects.create(
            ...     name="My Project",
            ...     description="A sample project"
            ... )
        """
        data = ProjectCreate(
            name=name,
            description=description,
            **kwargs
        ).model_dump(exclude_none=True)
        
        response = self._client.post("projects", data=data)
        return self._create_model_instance(response, Project)
    
    def update(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Project:
        """
        Update an existing project.
        
        Args:
            project_id: The project ID
            name: New project name
            description: New project description
            **kwargs: Additional fields to update
            
        Returns:
            Updated Project instance
            
        Example:
            >>> project = client.projects.update(
            ...     "proj_123",
            ...     name="Updated Name"
            ... )
        """
        # Get current project data first since API expects complete data
        current_project = self.get(project_id)
        
        # Use current values as defaults, override with provided values
        update_data = ProjectCreate(
            name=name if name is not None else current_project.name,
            description=description if description is not None else current_project.description,
            **kwargs
        ).model_dump(exclude_none=True)
        
        endpoint = self._build_endpoint("projects", project_id)
        response = self._client.put(endpoint, data=update_data)
        return self._create_model_instance(response, Project)
    
    def delete(self, project_id: str) -> Dict[str, Any]:
        """
        Delete a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            Deletion confirmation response
            
        Example:
            >>> result = client.projects.delete("proj_123")
            >>> print(result["message"])
        """
        endpoint = self._build_endpoint("projects", project_id)
        return self._client.delete(endpoint)
    
    def get_by_name(self, name: str) -> Optional[Project]:
        """
        Get a project by name.
        
        Args:
            name: Project name to search for
            
        Returns:
            Project instance if found, None otherwise
            
        Example:
            >>> project = client.projects.get_by_name("My Project")
            >>> if project:
            ...     print(f"Found project: {project.id}")
        """
        projects = self.list(search=name)
        for project in projects:
            if project.name == name:
                return project
        return None
    
    def exists(self, project_id: str) -> bool:
        """
        Check if a project exists.
        
        Args:
            project_id: The project ID
            
        Returns:
            True if project exists, False otherwise
            
        Example:
            >>> if client.projects.exists("proj_123"):
            ...     print("Project exists")
        """
        try:
            self.get(project_id)
            return True
        except Exception:
            return False
    
    def list_collections(self, project_id: str) -> List[Collection]:
        """
        List all collections for a project.
        
        Collections are created automatically when resources (contexts, schema metadata,
        etc.) are added to a project. Each collection type corresponds to a resource type.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of Collection instances
            
        Example:
            >>> collections = client.projects.list_collections("proj_123")
            >>> for collection in collections:
            ...     print(f"{collection.component_type}: {collection.h2ogpte_collection_id}")
        """
        endpoint = self._build_endpoint("projects", project_id, "collections")
        response = self._client.get(endpoint)
        return [Collection(**item) for item in response]
    
    def get_collection_by_type(self, project_id: str, component_type: str) -> Collection:
        """
        Get a specific collection by component type.
        
        Args:
            project_id: The project ID
            component_type: The component type (e.g., 'contexts', 'schema_metadata', 
                          'examples', 'feedback', 'custom_tools')
            
        Returns:
            Collection instance
            
        Raises:
            NotFoundError: If collection doesn't exist for the specified type
            
        Example:
            >>> collection = client.projects.get_collection_by_type(
            ...     "proj_123",
            ...     "contexts"
            ... )
            >>> print(f"Contexts collection ID: {collection.h2ogpte_collection_id}")
        """
        endpoint = self._build_endpoint("projects", project_id, "collections", component_type)
        response = self._client.get(endpoint)
        return Collection(**response)
