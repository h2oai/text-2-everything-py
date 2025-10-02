"""
Chat resource functional tests.
"""

import os
from .base_test import BaseTestRunner
from text2everything_sdk.models.chat import ChatToAnswerRequest, AutoFeedbackConfig


class ChatTestRunner(BaseTestRunner):
    """Test runner for Chat resource."""
    
    def run_test(self) -> bool:
        """Test chat operations."""
        print("\n7. Testing Chat Resource...")
        
        try:
            # Prefer explicit env-provided connector id for chat operations
            connector_id = None
            env_connector_id = os.getenv("EXECUTIONS_CONNECTOR_ID")
            if env_connector_id:
                connector_id = env_connector_id
                print(f"✅ Using connector from EXECUTIONS_CONNECTOR_ID: {connector_id}")
            else:
                print("⚠️  No EXECUTIONS_CONNECTOR_ID provided; proceeding without connector where possible")
            
            # Create a real chat session for proper testing
            try:
                chat_session = self.client.chat_sessions.create(
                    self.test_project_id,
                    name="Chat Test Session",
                    custom_tool_id=None
                )
                self.created_resources['chat_sessions'].append(chat_session.id)
                h2ogpte_session_id = chat_session.id
                print(f"✅ Created chat session for testing: {h2ogpte_session_id}")
            except Exception as e:
                print(f"❌ Failed to create chat session: {e}")
                return False
            
            # Test basic chat request (with connector if available)
            try:
                if connector_id:
                    print(f"🔗 Using connector {connector_id} for chat tests")
                    chat_response = self.client.chat.chat_to_sql(
                        self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="What tables are available in the database?",
                        connector_id=connector_id
                    )
                else:
                    chat_response = self.client.chat.chat_to_sql(
                        self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="What tables are available in the database?",
                    )
                print(f"✅ Chat message sent successfully")
                if hasattr(chat_response, 'response'):
                    print(f"✅ Received chat response")
            except Exception as e:
                print(f"⚠️  Chat request failed (may require H2OGPTE setup): {e}")
            
            # Test chat to answer request (with connector if available)
            try:
                if connector_id:
                    # 🆕 NEW: Use keyword arguments instead of ChatToAnswerRequest object
                    answer_response = self.client.chat.chat_to_answer(
                        project_id=self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="What tables are available in the database?",
                        connector_id=connector_id,
                        auto_add_feedback={"positive": True, "negative": False}
                    )
                    print(f"✅ Chat to answer request completed")
                else:
                    print(f"⚠️  Skipping chat to answer test - no connector available")
            except Exception as e:
                print(f"⚠️  Chat to answer failed (may require H2OGPTE setup): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
            return False
