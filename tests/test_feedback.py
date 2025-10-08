"""
Feedback resource functional tests.
"""

import os
from .base_test import BaseTestRunner


class FeedbackTestRunner(BaseTestRunner):
    """Test runner for Feedback resource."""
    
    def run_test(self) -> bool:
        """Test feedback operations."""
        print("\n9. Testing Feedback Resource...")
        
        try:
            # First, get or create h2o-snowflake-connector
            connector_id = None
            
            # Try to find existing h2o-snowflake-connector
            try:
                connectors = self.client.connectors.list(self.test_project_id)
                for connector in connectors:
                    if connector.name == "h2o-snowflake-connector":
                        connector_id = connector.id
                        print("✅ Found existing h2o-snowflake-connector for feedback tests")
                        break
            except Exception as e:
                print(f"⚠️  Could not list existing connectors: {e}")
            
            # If no h2o-snowflake-connector found, create it
            if not connector_id:
                print("🔧 Creating h2o-snowflake-connector for feedback operations...")
                try:
                    # Only attempt Snowflake if env present
                    if all([
                        os.getenv("SNOWFLAKE_HOST"),
                        os.getenv("SNOWFLAKE_USERNAME"),
                        os.getenv("SNOWFLAKE_PASSWORD") or os.getenv("SNOWFLAKE_PASSWORD_SECRET_ID"),
                        os.getenv("SNOWFLAKE_DATABASE")
                    ]):
                        connector_result = self.client.connectors.create(
                            project_id=self.test_project_id,
                            name="h2o-snowflake-connector",
                            description="H2O AI Snowflake connector for feedback testing",
                            db_type="snowflake",
                            host=os.getenv("SNOWFLAKE_HOST"),
                            username=os.getenv("SNOWFLAKE_USERNAME"),
                            password=os.getenv("SNOWFLAKE_PASSWORD"),
                            password_secret_id=os.getenv("SNOWFLAKE_PASSWORD_SECRET_ID"),
                            database=os.getenv("SNOWFLAKE_DATABASE"),
                            config={
                                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                                "role": os.getenv("SNOWFLAKE_ROLE")
                            }
                        )
                        connector_id = connector_result.id
                        self.created_resources['connectors'].append(connector_id)
                        print(f"✅ Created h2o-snowflake-connector: {connector_id}")
                    else:
                        # Fallback postgres connector for local testing
                        connector_result = self.client.connectors.create(
                            project_id=self.test_project_id,
                            name="feedback-test-postgres-connector",
                            description="PostgreSQL connector for feedback testing",
                            db_type="postgres",
                            host="localhost",
                            port=5432,
                            database="test_db",
                            username="test_user",
                            password="test_password"
                        )
                        connector_id = connector_result.id
                        self.created_resources['connectors'].append(connector_id)
                        print(f"✅ Created fallback PostgreSQL connector: {connector_id}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to create connector for feedback: {e}")
                    return False
            
            # Create a chat session for testing
            chat_session = self.client.chat_sessions.create(
                self.test_project_id,
                name="Feedback Test Session",
                custom_tool_id=None
            )
            self.created_resources['chat_sessions'].append(chat_session.id)
            h2ogpte_session_id = chat_session.id
            print(f"✅ Created chat session for feedback testing: {h2ogpte_session_id}")
            
            # Create a chat message to get a real chat_message_id
            chat_response = self.client.chat.chat_to_sql(
                self.test_project_id,
                chat_session_id=h2ogpte_session_id,
                query="What tables are available?",
                connector_id=connector_id
            )
            chat_message_id = chat_response.id
            print(f"✅ Created chat message for feedback: {chat_message_id}")
            
            # Test create positive feedback for chat message
            feedback_result = self.client.feedback.create(
                self.test_project_id,
                chat_message_id=chat_message_id,
                feedback="This response was very helpful and accurate",
                is_positive=True
            )
            self.created_resources['feedback'].append(feedback_result.id)
            print(f"✅ Created positive feedback for chat message: {feedback_result.id}")
            
            # Create an execution to get a real execution_id
            execution_id = None
            try:
                execution_response = self.client.executions.execute_sql(
                    self.test_project_id,
                    connector_id=connector_id,
                    chat_message_id=chat_message_id
                )
                execution_id = execution_response.execution_id
                print(f"✅ Created execution for feedback: {execution_id}")
            except Exception as e:
                print(f"⚠️  Could not create execution: {e}")
            
            # Test create negative feedback with execution_id
            if execution_id:
                negative_result = self.client.feedback.create(
                    self.test_project_id,
                    chat_message_id=chat_message_id,
                    feedback="This execution result was not accurate",
                    is_positive=False,
                    execution_id=execution_id
                )
                self.created_resources['feedback'].append(negative_result.id)
                print(f"✅ Created negative feedback with execution_id: {negative_result.id}")
            else:
                # Fallback: create negative feedback without execution_id
                negative_result = self.client.feedback.create(
                    self.test_project_id,
                    chat_message_id=chat_message_id,
                    feedback="This response was not accurate",
                    is_positive=False
                )
                self.created_resources['feedback'].append(negative_result.id)
                print(f"✅ Created negative feedback for chat message: {negative_result.id}")
            
            # Test list all feedback
            all_feedback = self.client.feedback.list(self.test_project_id)
            print(f"✅ Listed {len(all_feedback)} feedback items")
            
            # Test get feedback
            retrieved_feedback = self.client.feedback.get(self.test_project_id, feedback_result.id)
            feedback_type = "positive" if retrieved_feedback.is_positive else "negative"
            print(f"✅ Retrieved feedback: {feedback_type}")
            
            # Test update feedback
            updated_feedback = self.client.feedback.update(
                self.test_project_id,
                feedback_result.id,
                feedback="Updated: This response was excellent"
            )
            print("✅ Updated feedback comment")
            
            # Test list by type
            positive_feedback_list = self.client.feedback.list_positive(self.test_project_id)
            negative_feedback_list = self.client.feedback.list_negative(self.test_project_id)
            print(f"✅ Found {len(positive_feedback_list)} positive and {len(negative_feedback_list)} negative feedback items")
            
            # Test get feedback for message
            message_feedback = self.client.feedback.get_feedback_for_message(self.test_project_id, chat_message_id)
            if message_feedback:
                print(f"✅ Found {len(message_feedback)} feedback items for message {chat_message_id}")
            else:
                print("⚠️  No feedback found for test message")
            
            return True
            
        except Exception as e:
            print(f"❌ Feedback test failed: {e}")
            return False
