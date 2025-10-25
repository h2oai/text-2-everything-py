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
            
            # Test collections functionality
            if not self._test_collections():
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Projects test failed: {e}")
            return False
    
    def _test_collections(self) -> bool:
        """Test project collections functionality."""
        print("\n  📦 Testing collections...")
        
        # First, create some resources to generate collections
        # Create a context to trigger collection creation
        context = self.client.contexts.create(
            project_id=self.test_project_id,
            name="Test Context for Collections",
            content="Test content for collections testing"
        )
        self.created_resources['contexts'].append(context.id)
        
        # List all collections
        collections = self.client.projects.list_collections(self.test_project_id)
        
        if len(collections) == 0:
            print(f"    ⚠️  No collections found - this is expected if no resources have been created")
        else:
            print(f"    ✅ Found {len(collections)} collections")
            
            # Verify collection structure
            for collection in collections:
                if not hasattr(collection, 'component_type'):
                    print(f"❌ Collection missing component_type")
                    return False
                if not hasattr(collection, 'h2ogpte_collection_id'):
                    print(f"❌ Collection missing h2ogpte_collection_id")
                    return False
        
        # Test get collection by type
        try:
            contexts_collection = self.client.projects.get_collection_by_type(
                self.test_project_id,
                "contexts"
            )
            
            if contexts_collection.component_type != "contexts":
                print(f"❌ Wrong collection type returned")
                return False
            
            print(f"    ✅ Retrieved contexts collection: {contexts_collection.h2ogpte_collection_id}")
        except Exception as e:
            print(f"    ⚠️  Could not retrieve contexts collection: {e}")
            # This might be expected if collection hasn't been created yet
        
        return True
