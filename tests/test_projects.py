"""
Projects resource functional tests.
"""

from .base_test import BaseTestRunner
from models.projects import ProjectCreate, ProjectUpdate


class ProjectsTestRunner(BaseTestRunner):
    """Test runner for Projects resource."""
    
    def run_test(self) -> bool:
        """Test project CRUD operations."""
        print("\n1. Testing Projects Resource...")
        
        try:
            # Test list projects
            projects = self.client.projects.list()
            print(f"✅ Listed {len(projects)} projects")
            
            # Test get project
            project = self.client.projects.get(self.test_project_id)
            print(f"✅ Retrieved project: {project.name}")
            
            # Test update project
            updated_project = self.client.projects.update(
                self.test_project_id,
                description="Updated description for functional test"
            )
            print(f"✅ Updated project description")
            
            # Test project exists
            exists = self.client.projects.exists(self.test_project_id)
            if exists:
                print("✅ Project existence check passed")
            else:
                print("❌ Project existence check failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Projects test failed: {e}")
            return False
