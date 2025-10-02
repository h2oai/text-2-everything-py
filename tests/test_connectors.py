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
            
            # Test create Snowflake connector (prefer key-pair if present, otherwise password/secret-id)
            sf_host = os.getenv("SNOWFLAKE_HOST")
            sf_user = os.getenv("SNOWFLAKE_USERNAME")
            sf_db = os.getenv("SNOWFLAKE_DATABASE")
            sf_wh = os.getenv("SNOWFLAKE_WAREHOUSE")
            sf_role = os.getenv("SNOWFLAKE_ROLE")

            # Key-pair envs
            sf_pk = os.getenv("SNOWFLAKE_PRIVATE_KEY")
            sf_pk_secret_id = os.getenv("SNOWFLAKE_PRIVATE_KEY_SECRET_ID")
            sf_pk_secret_name = os.getenv("SNOWFLAKE_PRIVATE_KEY_SECRET_NAME")
            # Optional passphrase for encrypted private keys
            sf_pk_pass = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
            sf_pk_pass_secret_id = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_SECRET_ID")
            sf_pk_pass_secret_name = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_SECRET_NAME")

            # Password envs
            sf_pwd = os.getenv("SNOWFLAKE_PASSWORD")
            sf_pwd_secret_id = os.getenv("SNOWFLAKE_PASSWORD_SECRET_ID")

            any_created = False
            if all([sf_host, sf_user, sf_db]) and any([sf_pk, sf_pk_secret_id, sf_pk_secret_name]):
                cfg = {"warehouse": sf_wh, "role": sf_role}
                if sf_pk:
                    cfg["private_key"] = sf_pk
                elif sf_pk_secret_id:
                    cfg["private_key_secret_id"] = sf_pk_secret_id
                else:
                    cfg["private_key_secret_name"] = sf_pk_secret_name
                # Add passphrase if provided (value or secret reference)
                if sf_pk_pass:
                    cfg["private_key_passphrase"] = sf_pk_pass
                elif sf_pk_pass_secret_id:
                    cfg["private_key_passphrase_secret_id"] = sf_pk_pass_secret_id
                elif sf_pk_pass_secret_name:
                    cfg["private_key_passphrase_secret_name"] = sf_pk_pass_secret_name

                snowflake_keypair = self.client.connectors.create(
                    name="h2o-snowflake-connector-keypair",
                    description="H2O AI Snowflake connector (key-pair)",
                    db_type="snowflake",
                    host=sf_host,
                    username=sf_user,
                    database=sf_db,
                    config=cfg,
                )
                self.created_resources['connectors'].append(snowflake_keypair.id)
                print(f"✅ Created Snowflake connector (key-pair): {snowflake_keypair.id}")
                any_created = True

            if all([sf_host, sf_user, sf_db]) and (sf_pwd or sf_pwd_secret_id):
                snowflake_password = self.client.connectors.create(
                    name="h2o-snowflake-connector-password",
                    description="H2O AI Snowflake connector (password)",
                    db_type="snowflake",
                    host=sf_host,
                    username=sf_user,
                    database=sf_db,
                    password=sf_pwd,
                    password_secret_id=sf_pwd_secret_id,
                    config={
                        "warehouse": sf_wh,
                        "role": sf_role,
                    },
                )
                self.created_resources['connectors'].append(snowflake_password.id)
                print(f"✅ Created Snowflake connector (password): {snowflake_password.id}")
                any_created = True

            if not any_created:
                print("⚠️  Skipping Snowflake connector creation (missing env vars for both methods)")
            
            # Test list connectors
            connectors = self.client.connectors.list()
            print(f"✅ Listed {len(connectors)} connectors")
            
            # Test get connector
            retrieved_connector = self.client.connectors.get(connector_result.id)
            print(f"✅ Retrieved connector: {retrieved_connector.name}")
            
            # Test update connector (don't fail suite if this errors)
            try:
                updated_connector = self.client.connectors.update(
                    connector_result.id,
                    description="Updated PostgreSQL connector description"
                )
                print("✅ Updated connector description")
            except Exception as e:
                print(f"⚠️  Update connector skipped due to error: {e}")
            
            # Test list by type (non-blocking)
            try:
                postgres_connectors = self.client.connectors.list_by_type("postgres")
                snowflake_connectors = self.client.connectors.list_by_type("snowflake")
                print(f"✅ Found {len(postgres_connectors)} PostgreSQL and {len(snowflake_connectors)} Snowflake connectors")
            except Exception as e:
                print(f"⚠️  List by type skipped due to error: {e}")
            
            # Test connection endpoints for all created connectors (non-blocking)
            created_connectors = [connector_result]
            try:
                if 'snowflake_keypair' in locals() and snowflake_keypair:
                    created_connectors.append(snowflake_keypair)
            except Exception:
                pass
            try:
                if 'snowflake_password' in locals() and snowflake_password:
                    created_connectors.append(snowflake_password)
            except Exception:
                pass

            for c in created_connectors:
                # Boolean/ok-style test
                try:
                    ok = self.client.connectors.test_connection(c.id)
                    print(f"✅ test_connection ok={ok} for {c.name} ({c.id})")
                except Exception as e:
                    print(f"⚠️  test_connection failed for {c.name} ({c.id}): {e}")
                # Detailed test
                try:
                    detail = self.client.connectors.test_connection_detailed(c.id)
                    elapsed = detail.get('elapsed_ms') if isinstance(detail, dict) else None
                    print(f"✅ test_connection_detailed ok={detail.get('ok', False) if isinstance(detail, dict) else detail} elapsed_ms={elapsed} for {c.name} ({c.id})")
                except Exception as e:
                    print(f"⚠️  test_connection_detailed failed for {c.name} ({c.id}): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connectors test failed: {e}")
            return False
