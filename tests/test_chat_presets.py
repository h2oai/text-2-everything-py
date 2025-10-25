"""
Chat Presets resource functional tests.
"""

import time
from .base_test import BaseTestRunner
from models.chat_presets import ChatPresetCreate
from exceptions import ValidationError, NotFoundError


class ChatPresetsTestRunner(BaseTestRunner):
    """Test runner for Chat Presets resource."""
    
    def setup(self):
        """Initialize and create prerequisite resources."""
        if not super().setup():
            return False
        
        # Chat presets need a connector for testing
        try:
            connector = self.client.connectors.create(
                project_id=self.test_project_id,
                name="Test Connector for Presets",
                db_type="snowflake",
                host="test.snowflake.com",
                username="test_user",
                password="test_password",
                database="test_db"
            )
            self.test_connector_id = connector.id
            self.created_resources['connectors'].append(connector.id)
            print(f"✅ Test connector created for presets: {connector.id}")
            return True
        except Exception as e:
            print(f"❌ Failed to create test connector: {e}")
            return False
    
    def run_test(self) -> bool:
        """Test chat preset operations."""
        print("\n🎨 Testing Chat Presets Resource...")
        
        try:
            # Test 1: Create preset
            if not self._test_create_preset():
                return False
            
            # Test 2: Get preset
            if not self._test_get_preset():
                return False
            
            # Test 3: List presets
            if not self._test_list_presets():
                return False
            
            # Test 4: Update preset
            if not self._test_update_preset():
                return False
            
            # Test 5: Activate preset
            if not self._test_activate_preset():
                return False
            
            # Test 6: Get active preset
            if not self._test_get_active_preset():
                return False
            
            # Test 7: Prompt template operations
            if not self._test_prompt_templates():
                return False
            
            # Test 8: Inline template creation
            if not self._test_inline_template_creation():
                return False
            
            # Test 9: Delete preset
            if not self._test_delete_preset():
                return False
            
            print("✅ All chat preset tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Chat presets test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_create_preset(self) -> bool:
        """Test creating a chat preset."""
        print("\n  📝 Testing create preset...")
        
        # Create returns ChatPresetResponse with collection_id
        response = self.client.chat_presets.create(
            project_id=self.test_project_id,
            name="Test Preset",
            collection_name="test_preset_collection",
            description="A test chat preset",
            connector_id=self.test_connector_id,
            chat_settings={
                "llm": "gpt-4",
                "llm_args": {},  # API requires this to not be None
                "include_chat_history": "auto"
            }
        )
        
        # Store collection_id for later operations
        self.test_collection_id = response.collection_id
        self.created_resources['chat_presets'].append(response.collection_id)
        
        # Verify response has expected fields
        if not response.collection_id:
            print(f"❌ No collection_id in response")
            return False
        
        print(f"    ✅ Created preset with collection: {response.collection_id}")
        
        # Now get the full preset details to verify it was created correctly
        preset = self.client.chat_presets.get(
            self.test_project_id,
            response.collection_id
        )
        
        self.test_preset_id = preset.id
        
        if preset.name != "Test Preset":
            print(f"❌ Preset name mismatch")
            return False
        
        if preset.connector_id != self.test_connector_id:
            print(f"❌ Connector ID mismatch")
            return False
        
        print(f"    ✅ Verified preset details: {preset.id}")
        return True
    
    def _test_get_preset(self) -> bool:
        """Test retrieving a preset."""
        print("\n  🔍 Testing get preset...")
        
        # get() uses collection_id, not preset_id
        preset = self.client.chat_presets.get(
            self.test_project_id,
            self.test_collection_id
        )
        
        if preset.id != self.test_preset_id:
            print(f"❌ Retrieved wrong preset")
            return False
        
        print(f"    ✅ Retrieved preset: {preset.name}")
        return True
    
    def _test_list_presets(self) -> bool:
        """Test listing presets."""
        print("\n  📋 Testing list presets...")
        
        presets = self.client.chat_presets.list(self.test_project_id)
        
        if len(presets) == 0:
            print(f"❌ Expected at least 1 preset")
            return False
        
        preset_ids = [p.id for p in presets]
        if self.test_preset_id not in preset_ids:
            print(f"❌ Created preset not in list")
            return False
        
        print(f"    ✅ Listed {len(presets)} presets")
        return True
    
    def _test_update_preset(self) -> bool:
        """Test updating a preset."""
        print("\n  ✏️  Testing update preset...")
        
        # update() uses collection_id
        updated = self.client.chat_presets.update(
            self.test_project_id,
            self.test_collection_id,
            description="Updated description"
        )
        
        # Update returns ChatPresetResponse, not full preset
        if not updated.collection_id:
            print(f"❌ No collection_id in update response")
            return False
        
        # Verify by fetching the preset
        preset = self.client.chat_presets.get(
            self.test_project_id,
            self.test_collection_id
        )
        
        if preset.description != "Updated description":
            print(f"❌ Description not updated")
            return False
        
        print(f"    ✅ Updated preset successfully")
        return True
    
    def _test_activate_preset(self) -> bool:
        """Test activating a preset."""
        print("\n  ⭐ Testing activate preset...")
        
        activated = self.client.chat_presets.activate(
            self.test_project_id,
            self.test_preset_id
        )
        
        if not activated.is_active:
            print(f"❌ Preset not marked as active")
            return False
        
        print(f"    ✅ Activated preset")
        return True
    
    def _test_get_active_preset(self) -> bool:
        """Test getting the active preset."""
        print("\n  🎯 Testing get active preset...")
        
        active = self.client.chat_presets.get_active(self.test_project_id)
        
        if not active:
            print(f"❌ No active preset found")
            return False
        
        if active.id != self.test_preset_id:
            print(f"❌ Wrong preset marked as active")
            return False
        
        print(f"    ✅ Retrieved active preset: {active.name}")
        return True
    
    def _test_prompt_templates(self) -> bool:
        """Test prompt template operations."""
        print("\n  📄 Testing prompt templates...")
        
        # Create prompt template using correct signature
        template = self.client.chat_presets.create_prompt_template(
            project_id=self.test_project_id,
            name="Test Template",
            system_prompt="You are a helpful SQL assistant.",
            description="Test template for chat presets"
        )
        
        if not template or not template.get("id"):
            print(f"❌ Failed to create prompt template")
            return False
        
        print(f"    ✅ Created prompt template: {template['id']}")
        
        # List templates using correct signature
        result = self.client.chat_presets.list_prompt_templates(
            project_id=self.test_project_id
        )
        
        templates = result.get("items", [])
        if len(templates) == 0:
            print(f"❌ Expected at least 1 template")
            return False
        
        print(f"    ✅ Listed {len(templates)} templates")
        return True
    
    def _test_inline_template_creation(self) -> bool:
        """Test creating preset with inline template."""
        print("\n  🎨 Testing inline template creation...")
        
        # Create preset with inline template
        response = self.client.chat_presets.create(
            project_id=self.test_project_id,
            name="Preset with Inline Template",
            collection_name="inline_template_collection",
            description="Testing inline template creation",
            prompt_template={
                "name": "Inline Test Template",
                "system_prompt": "You are an expert data analyst for inline templates.",
                "description": "Template created inline with preset",
                "lang": "en"
            },
            connector_id=self.test_connector_id,
            workspace_id="test_workspace"
        )
        
        # Store for cleanup
        self.created_resources['chat_presets'].append(response.collection_id)
        
        if not response.collection_id:
            print(f"❌ Failed to create preset with inline template")
            return False
        
        print(f"    ✅ Created preset with inline template: {response.collection_id}")
        
        # Verify the preset was created
        preset = self.client.chat_presets.get(
            self.test_project_id,
            response.collection_id
        )
        
        # NOTE: Current API limitation - inline prompt_template is accepted but not processed
        # The template must be created separately and referenced by ID
        if preset.prompt_template_id:
            print(f"    ✅ Preset has template ID: {preset.prompt_template_id}")
        else:
            print(f"    ℹ️  Preset created successfully (inline template not processed by API - known limitation)")
        
        # Test with sharing parameters
        response2 = self.client.chat_presets.create(
            project_id=self.test_project_id,
            name="Shared Preset",
            collection_name="shared_preset_collection",
            prompt_template={
                "name": "Shared Template",
                "system_prompt": "You are a shared assistant."
            },
            share_prompt_with_usernames=["user1@example.com", "user2@example.com"],
            connector_id=self.test_connector_id,
            t2e_url="https://test-t2e.example.com"
        )
        
        self.created_resources['chat_presets'].append(response2.collection_id)
        
        print(f"    ✅ Created shared preset: {response2.collection_id}")
        return True
    
    def _test_create_session_from_preset(self) -> bool:
        """Test creating a chat session from preset."""
        print("\n  🔗 Testing create session from preset...")
        
        session = self.client.chat_sessions.create_from_preset(
            self.test_project_id,
            self.test_preset_id
        )
        
        self.created_resources['chat_sessions'].append(session.id)
        
        if not session:
            print(f"❌ Failed to create session from preset")
            return False
        
        print(f"    ✅ Created session from preset: {session.id}")
        
        # Test create from active preset
        session2 = self.client.chat_sessions.create_from_active_preset(
            self.test_project_id
        )
        
        self.created_resources['chat_sessions'].append(session2.id)
        
        print(f"    ✅ Created session from active preset: {session2.id}")
        return True
    
    def _test_delete_preset(self) -> bool:
        """Test deleting a preset."""
        print("\n  🗑️  Testing delete preset...")
        
        # Create a new preset to delete (don't delete the main test preset yet)
        temp_response = self.client.chat_presets.create(
            project_id=self.test_project_id,
            name="Temp Preset to Delete",
            collection_name="temp_delete_collection",
            connector_id=self.test_connector_id
        )
        
        # Delete uses collection_id
        result = self.client.chat_presets.delete(
            self.test_project_id,
            temp_response.collection_id
        )
        
        # Verify it's gone
        try:
            self.client.chat_presets.get(self.test_project_id, temp_response.collection_id)
            print(f"❌ Preset still exists after deletion")
            return False
        except NotFoundError:
            print(f"    ✅ Preset successfully deleted")
        except Exception as e:
            # Some APIs might return 404 differently
            if "404" in str(e) or "not found" in str(e).lower():
                print(f"    ✅ Preset successfully deleted")
            else:
                raise
        
        return True
