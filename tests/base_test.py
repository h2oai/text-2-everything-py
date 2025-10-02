"""
Base test class for Text2Everything SDK functional tests.

This module provides the common functionality needed by all test modules,
including client setup, resource cleanup, and shared utilities.
"""

import os
import sys
import time
from typing import Optional, List

# Add the parent directory to the path so we can import the SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from text2everything_sdk import Text2EverythingClient
from text2everything_sdk.models.projects import ProjectCreate
from text2everything_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    Text2EverythingError
)


class BaseTestRunner:
    """Base class for functional test runners."""
    
    def __init__(self, base_url: str, access_token: str, workspace_name: Optional[str] = None):
        self.base_url = base_url
        self.access_token = access_token
        self.workspace_name = workspace_name
        self.client: Optional[Text2EverythingClient] = None
        self.test_project_id = None
        self.created_resources = {
            'projects': [],
            'contexts': [],
            'schema_metadata': [],
            'golden_examples': [],
            'connectors': [],
            'chat_sessions': [],
            'feedback': [],
            'custom_tools': []
        }
    
    def setup(self):
        """Initialize the client and create test project."""
        print("🔧 Setting up test environment...")
        
        try:
            self.client = Text2EverythingClient(
                base_url=self.base_url,
                access_token=self.access_token,
                workspace_name=self.workspace_name,
            )
            print(f"✅ Client initialized for {self.base_url}")
            
            # Create a test project
            test_project = ProjectCreate(
                name=f"SDK_Test_{int(time.time())}",
                description="Temporary project for SDK testing"
            )
            
            project = self.client.projects.create(
                name=test_project.name,
                description=test_project.description
            )
            self.test_project_id = project.id
            self.created_resources['projects'].append(project.id)
            print(f"✅ Test project created: {project.id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up all created test resources."""
        print("\n🧹 Cleaning up test resources...")
        
        if not self.client:
            return
        
        # Clean up in reverse order of dependencies
        cleanup_order = ['feedback', 'custom_tools', 'chat_sessions', 'connectors', 'golden_examples', 'schema_metadata', 'contexts', 'projects']
        
        for resource_type in cleanup_order:
            for resource_id in self.created_resources[resource_type]:
                try:
                    if resource_type == 'projects':
                        self.client.projects.delete(resource_id)
                    elif resource_type == 'contexts':
                        self.client.contexts.delete(self.test_project_id, resource_id)
                    elif resource_type == 'schema_metadata':
                        self.client.schema_metadata.delete(self.test_project_id, resource_id)
                    elif resource_type == 'golden_examples':
                        self.client.golden_examples.delete(self.test_project_id, resource_id)
                    elif resource_type == 'connectors':
                        self.client.connectors.delete(resource_id)
                    elif resource_type == 'chat_sessions':
                        self.client.chat_sessions.delete(self.test_project_id, resource_id)
                    elif resource_type == 'feedback':
                        self.client.feedback.delete(self.test_project_id, resource_id)
                    elif resource_type == 'custom_tools':
                        self.client.custom_tools.delete(self.test_project_id, resource_id)
                    
                    print(f"✅ Deleted {resource_type}: {resource_id}")
                except Exception as e:
                    print(f"⚠️  Failed to delete {resource_type} {resource_id}: {e}")
    
    def run_test(self) -> bool:
        """Override this method in subclasses to implement specific tests."""
        raise NotImplementedError("Subclasses must implement run_test method")
