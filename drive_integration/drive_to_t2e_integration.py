#!/usr/bin/env python3
"""
H2O Drive to Text2Everything Integration Script

This script provides a way to:
1. List projects in H2O Drive
2. Download and prepare data from Drive (contexts, schema metadata, golden examples)
3. Upload data to Text2Everything API using the SDK

Features an efficient, SDK-focused workflow for data transfer.
"""

import os
import sys
import json
import tempfile
import asyncio
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# H2O Drive imports
try:
    import h2o_drive
    from h2o_drive import core
except ImportError:
    print("❌ h2o_drive not installed. Install with: pip install h2o_drive")
    sys.exit(1)

# Text2Everything SDK imports
try:
    from text2everything_sdk import Text2EverythingClient
    from text2everything_sdk.exceptions import (
        AuthenticationError,
        ValidationError,
        NotFoundError,
        RateLimitError,
        ServerError
    )
except ImportError:
    print("❌ text2everything_sdk not installed. Install the SDK first.")
    sys.exit(1)


class DriveManager:
    """Drive manager for essential operations"""
    
    def __init__(self, bucket: core.Bucket):
        self.bucket = bucket
    
    async def list_projects_in_drive(self, prefix: str = "") -> List[str]:
        """List all project folders in H2O Drive"""
        try:
            all_objects = await self.bucket.list_objects(prefix)
            projects = set()
            
            for obj in all_objects:
                parts = obj.key.split('/')
                if len(parts) > 1:
                    projects.add(parts[0])
            
            return sorted(list(projects))
        except Exception as e:
            print(f"❌ Error listing projects in Drive: {e}")
            return []
    
    async def load_file_from_drive(self, file_key: str) -> Any:
        """Download and load a file from H2O Drive"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tmp') as tmp_file:
            temp_path = tmp_file.name
        
        try:
            await self.bucket.download_file(file_key, temp_path)
            
            if file_key.endswith('.json'):
                with open(temp_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_key.endswith(('.txt', '.md')):
                with open(temp_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_key}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def load_project_data(self, project_name: str) -> Dict[str, List[Tuple[str, Any]]]:
        """Load all project data from H2O Drive"""
        print(f"📁 Loading project data for: {project_name}")
        
        # Discover files
        all_objects = await self.bucket.list_objects(f"{project_name}/")
        
        project_data = {
            "schema_metadata": [],
            "contexts": [],
            "golden_examples": []
        }
        
        # Categorize files
        files_by_type = {
            "schema_metadata": [],
            "contexts": [],
            "golden_examples": []
        }
        
        for obj in all_objects:
            if "/schema_metadata/" in obj.key and obj.key.endswith('.json'):
                files_by_type["schema_metadata"].append(obj.key)
            elif "/contexts/" in obj.key and obj.key.endswith(('.json', '.txt')):
                files_by_type["contexts"].append(obj.key)
            elif "/golden_examples/" in obj.key and obj.key.endswith('.json'):
                files_by_type["golden_examples"].append(obj.key)
        
        # Load files
        for data_type, file_keys in files_by_type.items():
            if not file_keys:
                print(f"⚠️  No {data_type} files found")
                continue
            
            print(f"📥 Loading {len(file_keys)} {data_type} files...")
            for file_key in file_keys:
                try:
                    data = await self.load_file_from_drive(file_key)
                    project_data[data_type].append((file_key, data))
                except Exception as e:
                    print(f"❌ Error loading {file_key}: {e}")
        
        total_files = sum(len(files) for files in project_data.values())
        print(f"✅ Loaded {total_files} files from H2O Drive")
        
        return project_data


def prepare_data_for_sdk(project_data: Dict[str, List[Tuple[str, Any]]]) -> Dict[str, List[Dict]]:
    """Convert loaded data to SDK-compatible format"""
    sdk_data = {}
    
    # Prepare contexts
    if project_data.get('contexts'):
        contexts_data = []
        for file_key, ctx_data in project_data['contexts']:
            if isinstance(ctx_data, str):
                # Text file - create context object
                filename = Path(file_key).stem
                contexts_data.append({
                    "name": filename,
                    "content": ctx_data,
                    "description": f"Context from {filename}",
                    "is_always_displayed": False
                })
            elif isinstance(ctx_data, dict):
                # JSON file - use as-is but ensure required fields
                contexts_data.append({
                    "name": ctx_data.get("name", Path(file_key).stem),
                    "content": ctx_data.get("content", ""),
                    "description": ctx_data.get("description", ""),
                    "is_always_displayed": ctx_data.get("is_always_displayed", False)
                })
        sdk_data['contexts'] = contexts_data
    
    # Prepare schema metadata
    if project_data.get('schema_metadata'):
        schema_data = []
        for file_key, schema in project_data['schema_metadata']:
            schema_data.append({
                "name": schema.get("name", Path(file_key).stem),
                "schema_data": schema.get("schema_data", schema),
                "description": schema.get("description", ""),
                "is_always_displayed": schema.get("is_always_displayed", False)
            })
        sdk_data['schema_metadata'] = schema_data
    
    # Prepare golden examples
    if project_data.get('golden_examples'):
        examples_data = []
        for file_key, example in project_data['golden_examples']:
            examples_data.append({
                "name": example.get("name", Path(file_key).stem),
                "user_query": example.get("user_query", ""),
                "sql_query": example.get("sql_query", ""),
                "description": example.get("description", ""),
                "is_always_displayed": example.get("is_always_displayed", False)
            })
        sdk_data['golden_examples'] = examples_data
    
    return sdk_data


def select_project_interactive(projects: List[str], project_type: str) -> Optional[str]:
    """Interactive project selection"""
    if not projects:
        print(f"❌ No {project_type} projects found")
        return None
    
    print(f"\n📋 Available {project_type} projects:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project}")
    
    while True:
        try:
            choice = input(f"\nSelect {project_type} project (1-{len(projects)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                return projects[idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")


async def main():
    """Main execution function"""
    print("🚀 H2O Drive to Text2Everything Integration")
    print("=" * 50)
    
    # Configuration
    BASE_URL = os.getenv("T2E_BASE_URL", "http://text2everything.text2everything.svc.cluster.local:8000")
    API_KEY = os.getenv("H2OGPTE_API_KEY")
    
    if not API_KEY:
        print("❌ API key not found. Set H2OGPTE_API_KEY environment variable")
        return
    
    # Step 1: Connect to H2O Drive
    print("\n1️⃣ Connecting to H2O Drive...")
    try:
        drive = h2o_drive.connect()
        bucket = drive.user_bucket()
        drive_manager = DriveManager(bucket)
        print("✅ H2O Drive connected successfully")
    except Exception as e:
        print(f"❌ H2O Drive connection failed: {e}")
        return
    
    # Step 2: Initialize Text2Everything SDK
    print("\n2️⃣ Initializing Text2Everything SDK...")
    try:
        sdk_client = Text2EverythingClient(
            base_url=BASE_URL,
            api_key=API_KEY,
            timeout=60,
            max_retries=3
        )
        print("✅ Text2Everything SDK initialized")
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")
        return
    
    # Step 3: List and select T2E project
    print("\n3️⃣ Listing Text2Everything projects...")
    try:
        t2e_projects = sdk_client.projects.list()
        if not t2e_projects:
            print("❌ No Text2Everything projects found. Create a project first.")
            return
        
        t2e_project_names = [p.name for p in t2e_projects]
        selected_t2e_project_name = select_project_interactive(t2e_project_names, "Text2Everything")
        
        if not selected_t2e_project_name:
            print("❌ No Text2Everything project selected")
            return
        
        # Get project ID
        selected_t2e_project = next(p for p in t2e_projects if p.name == selected_t2e_project_name)
        project_id = selected_t2e_project.id
        print(f"✅ Selected T2E project: {selected_t2e_project_name} (ID: {project_id})")
        
    except Exception as e:
        print(f"❌ Error listing T2E projects: {e}")
        return
    
    # Step 4: List and select Drive project
    print("\n4️⃣ Listing H2O Drive projects...")
    try:
        drive_projects = await drive_manager.list_projects_in_drive()
        selected_drive_project = select_project_interactive(drive_projects, "H2O Drive")
        
        if not selected_drive_project:
            print("❌ No H2O Drive project selected")
            return
        
        print(f"✅ Selected Drive project: {selected_drive_project}")
        
    except Exception as e:
        print(f"❌ Error listing Drive projects: {e}")
        return
    
    # Step 5: Load data from Drive
    print("\n5️⃣ Loading data from H2O Drive...")
    try:
        project_data = await drive_manager.load_project_data(selected_drive_project)
        
        if not any(len(files) > 0 for files in project_data.values()):
            print("❌ No data found in selected Drive project")
            return
        
        # Show summary
        for data_type, files in project_data.items():
            print(f"   - {data_type}: {len(files)} files")
        
    except Exception as e:
        print(f"❌ Error loading data from Drive: {e}")
        return
    
    # Step 6: Prepare data for SDK
    print("\n6️⃣ Preparing data for Text2Everything SDK...")
    try:
        sdk_ready_data = prepare_data_for_sdk(project_data)
        
        print("✅ Data prepared for SDK:")
        for data_type, items in sdk_ready_data.items():
            print(f"   - {data_type}: {len(items)} items")
        
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return
    
    # Step 7: Upload data using SDK
    print("\n7️⃣ Uploading data to Text2Everything...")
    upload_results = {}
    
    try:
        # Upload contexts
        if sdk_ready_data.get('contexts'):
            print(f"📤 Uploading {len(sdk_ready_data['contexts'])} contexts...")
            try:
                contexts = sdk_client.contexts.bulk_create(
                    project_id=project_id,
                    contexts=sdk_ready_data['contexts']
                )
                upload_results['contexts'] = {'success': len(contexts), 'total': len(sdk_ready_data['contexts'])}
                print(f"   ✅ {len(contexts)} contexts uploaded successfully")
            except ValidationError as e:
                print(f"   ⚠️  Contexts upload had validation issues: {e}")
                upload_results['contexts'] = {'success': 0, 'total': len(sdk_ready_data['contexts'])}
        
        # Upload schema metadata
        if sdk_ready_data.get('schema_metadata'):
            print(f"📤 Uploading {len(sdk_ready_data['schema_metadata'])} schema metadata items...")
            try:
                schemas = sdk_client.schema_metadata.bulk_create(
                    project_id=project_id,
                    schema_metadata_list=sdk_ready_data['schema_metadata'],
                    validate=True
                )
                upload_results['schema_metadata'] = {'success': len(schemas), 'total': len(sdk_ready_data['schema_metadata'])}
                print(f"   ✅ {len(schemas)} schema metadata items uploaded successfully")
            except ValidationError as e:
                print(f"   ⚠️  Schema metadata upload had validation issues: {e}")
                upload_results['schema_metadata'] = {'success': 0, 'total': len(sdk_ready_data['schema_metadata'])}
        
        # Upload golden examples
        if sdk_ready_data.get('golden_examples'):
            print(f"📤 Uploading {len(sdk_ready_data['golden_examples'])} golden examples...")
            try:
                examples = sdk_client.golden_examples.bulk_create(
                    project_id=project_id,
                    golden_examples=sdk_ready_data['golden_examples']
                )
                upload_results['golden_examples'] = {'success': len(examples), 'total': len(sdk_ready_data['golden_examples'])}
                print(f"   ✅ {len(examples)} golden examples uploaded successfully")
            except ValidationError as e:
                print(f"   ⚠️  Golden examples upload had validation issues: {e}")
                upload_results['golden_examples'] = {'success': 0, 'total': len(sdk_ready_data['golden_examples'])}
        
    except AuthenticationError:
        print("❌ Authentication failed. Check your API key.")
        return
    except RateLimitError as e:
        print(f"❌ Rate limit exceeded. Retry after: {e.retry_after} seconds")
        return
    except Exception as e:
        print(f"❌ Unexpected error during upload: {e}")
        return
    
    # Step 8: Summary
    print("\n8️⃣ Upload Summary")
    print("=" * 30)
    
    total_success = sum(r.get('success', 0) for r in upload_results.values())
    total_attempted = sum(r.get('total', 0) for r in upload_results.values())
    
    print(f"✅ Successfully uploaded: {total_success}/{total_attempted} items")
    
    for data_type, result in upload_results.items():
        success = result.get('success', 0)
        total = result.get('total', 0)
        print(f"   - {data_type}: {success}/{total}")
    
    # Cleanup
    sdk_client.close()
    print("\n🎉 Integration complete!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
