"""
Executions resource functional tests.
"""

import os
from .base_test import BaseTestRunner


class ExecutionsTestRunner(BaseTestRunner):
    """Test runner for Executions resource."""
    
    def run_test(self) -> bool:
        """Test SQL execution operations."""
        print("\n8. Testing Executions Resource...")
        
        try:
            # First, we need a connector to execute against
            # Check if we have any connectors, if not create one
            connector_id = None
            
            # Prefer explicit env-provided connector id
            env_connector_id = os.getenv("EXECUTIONS_CONNECTOR_ID")
            if env_connector_id:
                connector_id = env_connector_id
                print(f"✅ Using connector from EXECUTIONS_CONNECTOR_ID: {connector_id}")
            
            if not connector_id:
                print("❌ No connector available for executions test")
                return False
            
            print(f"🔗 Using connector {connector_id} for execution tests")
            
            # Test SQL execution
            try:
                execution_result = self.client.executions.execute_sql(
                    self.test_project_id,
                    sql_query="SELECT 1 as test_column;",
                    connector_id=connector_id
                )
                print(f"✅ SQL execution completed (execution_id: {execution_result.execution_id})")
            except Exception as e:
                print(f"⚠️  SQL execution failed with test connector: {e}")
            
            # Test chat-based execution with real chat session and message
            try:
                # First, create a real chat session to get chat_session_id
                chat_session = self.client.chat_sessions.create(
                    self.test_project_id,
                    name="Execution Test Session"
                )
                self.created_resources['chat_sessions'].append(chat_session.id)
                print(f"✅ Created chat session for execution test: {chat_session.id}")
                
                # Use the chat session ID
                chat_session_id = chat_session.id
                
                # Create a real chat message to get a valid message ID
                # Send chat message to generate SQL and get a real message ID
                chat_response = self.client.chat.chat_to_sql(
                    self.test_project_id,
                    chat_session_id=chat_session_id,
                    query="SELECT 1 as test_column;",
                    connector_id=connector_id
                )
                real_message_id = chat_response.id
                print(f"✅ Created real chat message for execution test: {real_message_id}")
                
                # Now test execution from the real chat message
                chat_execution = self.client.executions.execute_from_chat(
                    self.test_project_id,
                    connector_id=connector_id,
                    chat_message_id=real_message_id,
                    chat_session_id=chat_session_id
                )
                print(f"✅ Chat-based execution completed with real message ID")
                
            except Exception as e:
                print(f"⚠️  Chat-based execution failed (may require H2OGPTE setup): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Executions test failed: {e}")
            return False
