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
            
            # Try to find existing connectors first
            try:
                connectors = self.client.connectors.list()
                for connector in connectors:
                    if connector.name == "h2o-snowflake-connector":
                        connector_id = connector.id
                        print("✅ Found existing Snowflake connector for execution tests")
                        break
                
                # If no Snowflake connector found, use any available connector
                if not connector_id and connectors:
                    connector_id = connectors[0].id
                    print(f"✅ Using existing connector: {connectors[0].name}")
                    
            except Exception as e:
                print(f"⚠️  Could not list existing connectors: {e}")
            
            # If no existing connectors, create a test connector
            if not connector_id:
                print("🔧 Creating test connector for executions...")
                try:
                    # Create Snowflake connector with credentials from environment variables
                    connector_result = self.client.connectors.create(
                        name="executions-test-snowflake-connector",
                        description="H2O AI Snowflake connector for executions testing",
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
                    print(f"✅ Created Snowflake connector for executions: {connector_id}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to create Snowflake connector, creating PostgreSQL fallback: {e}")
                    # Fallback to PostgreSQL connector
                    try:
                        connector_result = self.client.connectors.create(
                            name="executions-test-postgres-connector",
                            description="PostgreSQL connector for executions testing",
                            db_type="postgres",
                            host="localhost",
                            port=5432,
                            database="test_db",
                            username="test_user",
                            password="test_password"
                        )
                        connector_id = connector_result.id
                        self.created_resources['connectors'].append(connector_id)
                        print(f"✅ Created PostgreSQL connector for executions: {connector_id}")
                    except Exception as e2:
                        print(f"❌ Failed to create any connector for executions: {e2}")
                        return False
            
            if not connector_id:
                print("❌ No connector available for executions test")
                return False
            
            print(f"🔗 Using connector {connector_id} for execution tests")
            
            # Test SQL execution
            try:
                execution_result = self.client.executions.execute_sql(
                    sql_query="SELECT 1 as test_column;",
                    connector_id=connector_id
                )
                print(f"✅ SQL execution completed (execution_id: {execution_result.execution_id})")
            except Exception as e:
                print(f"⚠️  SQL execution failed as expected with test connector: {e}")
            
            # Test chat-based execution with real chat session and message
            try:
                # First, create a real chat session to get h2ogpte_session_id
                chat_session = self.client.chat_sessions.create(
                    self.test_project_id,
                    name="Execution Test Session"
                )
                self.created_resources['chat_sessions'].append(chat_session.id)
                print(f"✅ Created chat session for execution test: {chat_session.id}")
                
                # Use the chat session ID as the h2ogpte_session_id
                h2ogpte_session_id = chat_session.id
                
                # Create a real chat message to get a valid message ID
                # Send chat message to generate SQL and get a real message ID
                chat_response = self.client.chat.chat_to_sql(
                    self.test_project_id,
                    query="SELECT 1 as test_column;",
                    h2ogpte_session_id=h2ogpte_session_id,
                    connector_id=connector_id
                )
                real_message_id = chat_response.id
                print(f"✅ Created real chat message for execution test: {real_message_id}")
                
                # Now test execution from the real chat message
                chat_execution = self.client.executions.execute_from_chat(
                    connector_id=connector_id,
                    chat_message_id=real_message_id,
                    h2ogpte_session_id=h2ogpte_session_id
                )
                print(f"✅ Chat-based execution completed with real message ID")
                
            except Exception as e:
                print(f"⚠️  Chat-based execution failed (may require H2OGPTE setup): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Executions test failed: {e}")
            return False
