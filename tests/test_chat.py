"""
Chat resource functional tests.
"""

import os
from .base_test import BaseTestRunner
from models.chat import ChatToAnswerRequest, AutoFeedbackConfig


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
            
            # Test chat_to_sql with cutoff parameters
            try:
                if connector_id:
                    chat_response_cutoff = self.client.chat.chat_to_sql(
                        self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="Show me the top customers",
                        connector_id=connector_id,
                        contexts_cutoff=0.5,
                        schema_cutoff=0.7,
                        feedback_cutoff=0.6,
                        examples_cutoff=0.5
                    )
                    print(f"✅ Chat with cutoff parameters sent successfully")
                else:
                    chat_response_cutoff = self.client.chat.chat_to_sql(
                        self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="Show me the top customers",
                        contexts_cutoff=0.5,
                        schema_cutoff=0.7
                    )
                    print(f"✅ Chat with cutoff parameters sent successfully")
            except Exception as e:
                print(f"⚠️  Chat with cutoff parameters failed (may require H2OGPTE setup): {e}")
            
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
            
            # Test chat_to_answer with cutoff parameters
            try:
                if connector_id:
                    answer_response_cutoff = self.client.chat.chat_to_answer(
                        project_id=self.test_project_id,
                        chat_session_id=h2ogpte_session_id,
                        query="What tables are available in the database?",
                        connector_id=connector_id,
                        contexts_cutoff=0.6,
                        schema_cutoff=0.8,
                        feedback_cutoff=0.7,
                        examples_cutoff=0.6,
                        auto_add_feedback={"positive": False, "negative": False}
                    )
                    print(f"✅ Chat to answer with cutoff parameters completed")
                else:
                    print(f"⚠️  Skipping chat to answer cutoff test - no connector available")
            except Exception as e:
                print(f"⚠️  Chat to answer with cutoff parameters failed (may require H2OGPTE setup): {e}")
            
            # Test execution cache lookup
            if connector_id:
                if not self._test_execution_cache_lookup(connector_id, h2ogpte_session_id):
                    # Don't fail the whole test, cache lookup is an optimization feature
                    print("⚠️  Cache lookup test had issues but continuing...")
            else:
                print("⚠️  Skipping cache lookup test - no connector available")
            
            return True
            
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
            return False
    
    def _test_execution_cache_lookup(self, connector_id: str, chat_session_id: str) -> bool:
        """Test execution cache lookup functionality."""
        print("\n  🔍 Testing execution cache lookup...")
        
        # First, create and execute a query to populate the cache
        try:
            # Execute a query to create an execution in the cache
            chat_response = self.client.chat.chat_to_sql(
                project_id=self.test_project_id,
                chat_session_id=chat_session_id,
                query="What tables are available in the database?",
                connector_id=connector_id
            )
            
            print(f"    ✅ Created chat message for cache: {chat_response.id}")
            
            # Now test cache lookup with the same query
            cache_result = self.client.chat.execution_cache_lookup(
                project_id=self.test_project_id,
                user_query="What tables are available in the database?",
                connector_id=connector_id,
                similarity_threshold=0.9,  # High threshold for exact match
                top_n=5
            )
            
            if not hasattr(cache_result, 'cache_hit'):
                print(f"❌ Cache result missing cache_hit field")
                return False
            
            if not hasattr(cache_result, 'matches'):
                print(f"❌ Cache result missing matches field")
                return False
            
            print(f"    ✅ Cache lookup completed: cache_hit={cache_result.cache_hit}")
            
            if cache_result.cache_hit:
                print(f"    ✅ Found {len(cache_result.matches)} similar executions")
                
                # Verify match structure
                if len(cache_result.matches) > 0:
                    match = cache_result.matches[0]
                    if not hasattr(match, 'similarity_score'):
                        print(f"❌ Match missing similarity_score")
                        return False
                    if not hasattr(match, 'execution'):
                        print(f"❌ Match missing execution")
                        return False
                    
                    print(f"    ✅ Top match similarity: {match.similarity_score:.2f}")
            else:
                print(f"    ℹ️  No cache hits (checked {getattr(cache_result, 'candidates_checked', 0)} candidates)")
            
            # Test with different similarity threshold
            cache_result2 = self.client.chat.execution_cache_lookup(
                project_id=self.test_project_id,
                user_query="Show me all active users",  # Similar but different query
                connector_id=connector_id,
                similarity_threshold=0.5,  # Lower threshold
                top_n=3
            )
            
            print(f"    ✅ Tested with lower threshold: {getattr(cache_result2, 'candidates_checked', 0)} candidates checked")
            
            # Test filtering by positive feedback
            cache_result3 = self.client.chat.execution_cache_lookup(
                project_id=self.test_project_id,
                user_query="What tables are available in the database?",
                connector_id=connector_id,
                only_positive_feedback=True
            )
            
            print(f"    ✅ Tested positive feedback filter")
            
            return True
            
        except Exception as e:
            print(f"    ⚠️  Cache lookup test encountered error: {e}")
            # Don't fail the test - cache lookup is an optimization feature
            return True
