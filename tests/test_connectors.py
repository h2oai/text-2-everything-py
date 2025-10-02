"""
Connectors resource functional tests.
"""

import os
from .base_test import BaseTestRunner


class ConnectorsTestRunner(BaseTestRunner):
    """Test runner for Connectors resource."""
    
    def run_test(self) -> bool:
        """Test connector CRUD operations."""
        print("\n5. Testing Connectors Resource...")
        
        try:
            # Test create PostgreSQL connector
            connector_result = self.client.connectors.create(
                name="test_postgres_connector",
                description="PostgreSQL connector for functional testing",
                db_type="postgres",
                host="localhost",
                port=5432,
                database="test_db",
                username="test_user",
                password="test_password"
            )
            self.created_resources['connectors'].append(connector_result.id)
            print(f"✅ Created PostgreSQL connector: {connector_result.id}")
            
            # Test create Snowflake connector with credentials from environment variables
            # Only attempt Snowflake creation if minimal env vars present
            if all([
                os.getenv("SNOWFLAKE_HOST"),
                os.getenv("SNOWFLAKE_USERNAME"),
                os.getenv("SNOWFLAKE_PASSWORD") or os.getenv("SNOWFLAKE_PASSWORD_SECRET_NAME"),
                os.getenv("SNOWFLAKE_DATABASE")
            ]):
                snowflake_result = self.client.connectors.create(
                    name="h2o-snowflake-connector",
                    description="H2O AI Snowflake connector for Text2Everything demo data",
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
                self.created_resources['connectors'].append(snowflake_result.id)
                print(f"✅ Created Snowflake connector: {snowflake_result.id}")
            else:
                print("⚠️  Skipping Snowflake connector creation (missing env vars)")
            
            # Test list connectors
            connectors = self.client.connectors.list()
            print(f"✅ Listed {len(connectors)} connectors")
            
            # Test get connector
            retrieved_connector = self.client.connectors.get(connector_result.id)
            print(f"✅ Retrieved connector: {retrieved_connector.name}")
            
            # Test update connector
            updated_connector = self.client.connectors.update(
                connector_result.id,
                description="Updated PostgreSQL connector description"
            )
            print("✅ Updated connector description")
            
            # Test list by type
            postgres_connectors = self.client.connectors.list_by_type("postgres")
            snowflake_connectors = self.client.connectors.list_by_type("snowflake")
            print(f"✅ Found {len(postgres_connectors)} PostgreSQL and {len(snowflake_connectors)} Snowflake connectors")
            
            # Test connection (this might fail with test credentials, but should not raise unexpected errors)
            try:
                test_result = self.client.connectors.test_connection(connector_result.id)
                if isinstance(test_result, dict):
                    print(f"✅ Connection test completed (success: {test_result.get('success', False)})")
                else:
                    print(f"✅ Connection test completed (result: {test_result})")
            except Exception as e:
                print(f"⚠️  Connection test failed as expected with test credentials: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connectors test failed: {e}")
            return False
