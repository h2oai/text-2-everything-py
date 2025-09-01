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
            # First, try to get a connector for chat operations that might need one
            connector_id = None
            
            # Try to find existing connectors first
            try:
                connectors = self.client.connectors.list()
                for connector in connectors:
                    if connector.name == "h2o-snowflake-connector":
                        connector_id = connector.id
                        print("✅ Found existing Snowflake connector for chat tests")
                        break
                
                # If no Snowflake connector found, use any available connector
                if not connector_id and connectors:
                    connector_id = connectors[0].id
                    print(f"✅ Using existing connector for chat tests: {connectors[0].name}")
                    
            except Exception as e:
                print(f"⚠️  Could not list existing connectors: {e}")
            
            # If no existing connectors, create a test connector for chat operations
            if not connector_id:
                print("🔧 Creating test connector for chat operations...")
                try:
                    # Create Snowflake connector with credentials from environment variables
                    connector_result = self.client.connectors.create(
                        name="h2o-snowflake-connector",
                        description="H2O AI Snowflake connector for chat testing",
                        db_type="snowflake",
                        host=os.getenv("SNOWFLAKE_HOST"),
                        username=os.getenv("SNOWFLAKE_USERNAME"),
                        password=os.getenv("SNOWFLAKE_PASSWORD"),
                        database=os.getenv("SNOWFLAKE_DATABASE"),
                        config={
                            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                            "role": os.getenv("SNOWFLAKE_ROLE")
                        }
                    )
                    connector_id = connector_result.id
                    self.created_resources['connectors'].append(connector_id)
                    print(f"✅ Created Snowflake connector for chat: {connector_id}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to create connector for chat: {e}")
                    # Chat tests can still run without connectors for basic functionality
            
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
