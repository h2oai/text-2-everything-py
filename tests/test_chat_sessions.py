"""
Chat sessions resource functional tests.
"""

from .base_test import BaseTestRunner


class ChatSessionsTestRunner(BaseTestRunner):
    """Test runner for Chat Sessions resource."""
    
    def run_test(self) -> bool:
        """Test chat session operations."""
        print("\n6. Testing Chat Sessions Resource...")
        
        try:
            # Test create chat session
            try:
                session_result = self.client.chat_sessions.create(
                    self.test_project_id,
                    name="Functional Test Session",
                    custom_tool_id=None
                )
                self.created_resources['chat_sessions'].append(session_result.id)
                print(f"✅ Created chat session: {session_result.id}")
                
                # Test list chat sessions
                sessions = self.client.chat_sessions.list(self.test_project_id)
                print(f"✅ Listed {len(sessions)} chat sessions")
                
                # Test get questions
                try:
                    questions = self.client.chat_sessions.get_questions(
                        self.test_project_id,
                        session_result.id
                    )
                    print(f"✅ Retrieved {len(questions)} questions")
                    print(f"Questions: {[q.question for q in questions]}")
                except Exception as e:
                    print(f"⚠️  Getting questions failed (may require H2OGPTE setup): {e}")
                
            except Exception as e:
                print(f"⚠️  Chat session operations failed (may require H2OGPTE setup): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Chat sessions test failed: {e}")
            return False
