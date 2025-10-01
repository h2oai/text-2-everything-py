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
import argparse
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

def check_and_import_dependencies():
    """Check and import required dependencies"""
    try:
        import h2o_drive
        from h2o_drive import core
    except ImportError:
        print("❌ h2o_drive not installed. Install with: pip install h2o_drive")
        sys.exit(1)

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
    
    return h2o_drive, core, Text2EverythingClient, AuthenticationError, ValidationError, NotFoundError, RateLimitError, ServerError


class DriveManager:
    """Drive manager for essential operations"""
    
    def __init__(self, bucket):
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
    
    async def list_subdirectories(self, parent_path: str) -> List[str]:
        """List subdirectories within a given path"""
        try:
            all_objects = await self.bucket.list_objects(f"{parent_path}/")
            subdirs = set()
            
            for obj in all_objects:
                # Remove the parent path prefix and get the next level
                relative_path = obj.key[len(parent_path)+1:]  # +1 for the trailing slash
                parts = relative_path.split('/')
                if len(parts) > 1:  # Has subdirectories
                    subdirs.add(parts[0])
            
            return sorted(list(subdirs))
        except Exception as e:
            print(f"❌ Error listing subdirectories in {parent_path}: {e}")
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


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Transfer data from H2O Drive to Text2Everything",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python drive_to_t2e_integration.py

  # Non-interactive mode
  python drive_to_t2e_integration.py --drive-project-name "home/my_data" --t2e-project-name "MyProject" --non-interactive

  # Create a new T2E project
  python drive_to_t2e_integration.py --create-t2e-project --t2e-project-name "My New Project"

  # Create project with description
  python drive_to_t2e_integration.py --create-t2e-project --t2e-project-name "My Project" --t2e-project-description "Data migration project"

  # Non-interactive mode with project creation
  python drive_to_t2e_integration.py --create-t2e-project --t2e-project-name "AutoProject" --drive-project-name "home/my_data" --non-interactive

  # List available projects
  python drive_to_t2e_integration.py --list-drive-projects
  python drive_to_t2e_integration.py --list-t2e-projects

  # Custom configuration
  python drive_to_t2e_integration.py --t2e-base-url "https://custom.api.com" --timeout 120

Environment Variables:
  T2E_ACCESS_TOKEN             OIDC access token for Text2Everything (required)
  T2E_WORKSPACE_NAME           Optional workspace scope, e.g., workspaces/dev
  T2E_BASE_URL                 Text2Everything base URL (optional)
  H2O_CLOUD_ENVIRONMENT       H2O Cloud environment URL (required for H2O Drive)
  H2O_CLOUD_CLIENT_PLATFORM_TOKEN  H2O Cloud platform token (required for H2O Drive)
        """
    )
    
    parser.add_argument(
        "--t2e-base-url",
        help="Text2Everything base URL (default: from T2E_BASE_URL env var)"
    )
    
    parser.add_argument(
        "--t2e-project-name",
        help="Target Text2Everything project name (interactive selection if not provided, required with --create-t2e-project)"
    )
    
    parser.add_argument(
        "--drive-project-name",
        help="Source H2O Drive project name (interactive selection if not provided)"
    )
    
    parser.add_argument(
        "--create-t2e-project",
        action="store_true",
        help="Create a new Text2Everything project if none exist (requires --t2e-project-name)"
    )
    
    parser.add_argument(
        "--t2e-project-description",
        help="Description for the new Text2Everything project (used with --create-t2e-project)"
    )
    
    parser.add_argument(
        "--access-token",
        help="OIDC access token (default: from T2E_ACCESS_TOKEN env var)"
    )
    parser.add_argument(
        "--workspace-name",
        help="Optional workspace name (default: from T2E_WORKSPACE_NAME env var)"
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (requires --drive-project-name and --t2e-project-name)"
    )
    
    parser.add_argument(
        "--list-drive-projects",
        action="store_true",
        help="List available H2O Drive projects and exit"
    )
    
    parser.add_argument(
        "--list-t2e-projects",
        action="store_true",
        help="List available Text2Everything projects and exit"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="SDK timeout in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts (default: 3)"
    )
    
    return parser.parse_args()


async def list_drive_projects_only(drive_manager: DriveManager):
    """List H2O Drive projects and exit"""
    print("📋 Available H2O Drive projects:")
    print("=" * 40)
    
    try:
        projects = await drive_manager.list_projects_in_drive()
        if projects:
            for i, project in enumerate(projects, 1):
                print(f"  {i}. {project}")
            print(f"\nTotal: {len(projects)} projects found")
        else:
            print("  No projects found in H2O Drive")
    except Exception as e:
        print(f"❌ Error listing Drive projects: {e}")
        sys.exit(1)


async def list_t2e_projects_only(sdk_client):
    """List Text2Everything projects and exit"""
    print("📋 Available Text2Everything projects:")
    print("=" * 40)
    
    try:
        projects = sdk_client.projects.list()
        if projects:
            for i, project in enumerate(projects, 1):
                print(f"  {i}. {project.name} (ID: {project.id})")
            print(f"\nTotal: {len(projects)} projects found")
        else:
            print("  No projects found in Text2Everything")
    except Exception as e:
        print(f"❌ Error listing T2E projects: {e}")
        sys.exit(1)


async def main():
    """Main execution function"""
    args = parse_arguments()
    
    print("🚀 H2O Drive to Text2Everything Integration")
    print("=" * 50)
    
    # Check and import dependencies
    h2o_drive, core, Text2EverythingClient, AuthenticationError, ValidationError, NotFoundError, RateLimitError, ServerError = check_and_import_dependencies()
    
    # Configuration
    BASE_URL = args.t2e_base_url or os.getenv("T2E_BASE_URL", "http://text2everything.text2everything.svc.cluster.local:8000")
    ACCESS_TOKEN = args.access_token or os.getenv("T2E_ACCESS_TOKEN")
    WORKSPACE_NAME = args.workspace_name or os.getenv("T2E_WORKSPACE_NAME")
    
    if not ACCESS_TOKEN:
        print("❌ Access token not found. Provide via --access-token or set T2E_ACCESS_TOKEN environment variable")
        sys.exit(1)
    
    # Validate project creation requirements
    if args.create_t2e_project:
        if not args.t2e_project_name:
            print("❌ --create-t2e-project requires --t2e-project-name to be specified")
            sys.exit(1)
        print("🆕 Project creation mode enabled")
    
    # Validate non-interactive mode requirements
    if args.non_interactive:
        if not args.drive_project_name or not args.t2e_project_name:
            print("❌ Non-interactive mode requires both --drive-project-name and --t2e-project-name")
            sys.exit(1)
        print("🤖 Running in non-interactive mode")
    
    print(f"🔗 Text2Everything URL: {BASE_URL}")
    print(f"⏱️  Timeout: {args.timeout}s, Max retries: {args.max_retries}")
    
    # Step 1: Connect to H2O Drive
    print("\n1️⃣ Connecting to H2O Drive...")
    try:
        drive = h2o_drive.connect()
        bucket = drive.user_bucket()
        drive_manager = DriveManager(bucket)
        print("✅ H2O Drive connected successfully")
    except Exception as e:
        print(f"❌ H2O Drive connection failed: {e}")
        sys.exit(1)
    
    # Handle list-only modes
    if args.list_drive_projects:
        await list_drive_projects_only(drive_manager)
        return
    
    # Step 2: Initialize Text2Everything SDK
    print("\n2️⃣ Initializing Text2Everything SDK...")
    try:
        sdk_client = Text2EverythingClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN,
            workspace_name=WORKSPACE_NAME,
            timeout=args.timeout,
            max_retries=args.max_retries
        )
        print("✅ Text2Everything SDK initialized")
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")
        sys.exit(1)
    
    # Handle T2E list-only mode
    if args.list_t2e_projects:
        await list_t2e_projects_only(sdk_client)
        sdk_client.close()
        return
    
    # Step 3: List and select T2E project
    print("\n3️⃣ Selecting Text2Everything project...")
    try:
        t2e_projects = sdk_client.projects.list()
        
        # Handle case when no projects exist
        if not t2e_projects:
            if args.create_t2e_project:
                print("🆕 No Text2Everything projects found. Creating new project...")
                try:
                    new_project = sdk_client.projects.create(
                        name=args.t2e_project_name,
                        description=args.t2e_project_description
                    )
                    print(f"✅ Created new T2E project: {new_project.name} (ID: {new_project.id})")
                    selected_t2e_project_name = new_project.name
                    project_id = new_project.id
                except Exception as e:
                    print(f"❌ Failed to create T2E project: {e}")
                    sdk_client.close()
                    sys.exit(1)
            else:
                print("❌ No Text2Everything projects found.")
                print("Use --create-t2e-project --t2e-project-name 'YourProjectName' to create one")
                sdk_client.close()
                sys.exit(1)
        else:
            # Projects exist, proceed with selection logic
            if args.t2e_project_name:
                # Use specified project name
                t2e_project_names = [p.name for p in t2e_projects]
                if args.t2e_project_name not in t2e_project_names:
                    if args.create_t2e_project:
                        print(f"🆕 Text2Everything project '{args.t2e_project_name}' not found. Creating new project...")
                        try:
                            new_project = sdk_client.projects.create(
                                name=args.t2e_project_name,
                                description=args.t2e_project_description
                            )
                            print(f"✅ Created new T2E project: {new_project.name} (ID: {new_project.id})")
                            selected_t2e_project_name = new_project.name
                            project_id = new_project.id
                        except Exception as e:
                            print(f"❌ Failed to create T2E project: {e}")
                            sdk_client.close()
                            sys.exit(1)
                    else:
                        print(f"❌ Text2Everything project '{args.t2e_project_name}' not found")
                        print(f"Available projects: {', '.join(t2e_project_names)}")
                        print("Use --create-t2e-project to create a new project")
                        sdk_client.close()
                        sys.exit(1)
                else:
                    selected_t2e_project_name = args.t2e_project_name
                    # Get project ID
                    selected_t2e_project = next(p for p in t2e_projects if p.name == selected_t2e_project_name)
                    project_id = selected_t2e_project.id
                    print(f"✅ Selected T2E project: {selected_t2e_project_name} (ID: {project_id})")
            else:
                # Interactive selection
                if args.non_interactive:
                    print("❌ Non-interactive mode requires --t2e-project-name")
                    sdk_client.close()
                    sys.exit(1)
                t2e_project_names = [p.name for p in t2e_projects]
                selected_t2e_project_name = select_project_interactive(t2e_project_names, "Text2Everything")
                
                if not selected_t2e_project_name:
                    print("❌ No Text2Everything project selected")
                    sdk_client.close()
                    sys.exit(1)
                
                # Get project ID
                selected_t2e_project = next(p for p in t2e_projects if p.name == selected_t2e_project_name)
                project_id = selected_t2e_project.id
                print(f"✅ Selected T2E project: {selected_t2e_project_name} (ID: {project_id})")
        
    except Exception as e:
        print(f"❌ Error with T2E projects: {e}")
        sdk_client.close()
        sys.exit(1)
    
    # Step 4: List and select Drive project
    print("\n4️⃣ Selecting H2O Drive project...")
    try:
        drive_projects = await drive_manager.list_projects_in_drive()
        if not drive_projects:
            print("❌ No H2O Drive projects found")
            sdk_client.close()
            sys.exit(1)
        
        # Check if the only available project is "home" and look deeper
        if len(drive_projects) == 1 and drive_projects[0] == "home":
            print("🔍 Found 'home' as the only project. Looking for subdirectories within home/...")
            home_subdirs = await drive_manager.list_subdirectories("home")
            
            if home_subdirs:
                print(f"📁 Found {len(home_subdirs)} subdirectories in home/")
                # Use subdirectories as the project options
                actual_projects = home_subdirs
                project_prefix = "home/"
                project_display_type = "H2O Drive (within home/)"
            else:
                print("⚠️  No subdirectories found in home/. Using 'home' as the project.")
                actual_projects = drive_projects
                project_prefix = ""
                project_display_type = "H2O Drive"
        else:
            # Normal case - use top-level projects
            actual_projects = drive_projects
            project_prefix = ""
            project_display_type = "H2O Drive"
        
        if args.drive_project_name:
            # Use specified project name
            # Handle both cases: direct project name or home/project_name format
            if project_prefix and args.drive_project_name.startswith("home/"):
                # Remove home/ prefix for comparison with actual_projects
                project_name_without_prefix = args.drive_project_name[5:]  # Remove "home/"
                if project_name_without_prefix not in actual_projects:
                    print(f"❌ H2O Drive project '{args.drive_project_name}' not found")
                    print(f"Available projects: {', '.join([project_prefix + p for p in actual_projects])}")
                    sdk_client.close()
                    sys.exit(1)
                selected_drive_project = args.drive_project_name
            elif not project_prefix and args.drive_project_name in actual_projects:
                # Normal case - direct project name
                selected_drive_project = args.drive_project_name
            else:
                print(f"❌ H2O Drive project '{args.drive_project_name}' not found")
                if project_prefix:
                    print(f"Available projects: {', '.join([project_prefix + p for p in actual_projects])}")
                else:
                    print(f"Available projects: {', '.join(actual_projects)}")
                sdk_client.close()
                sys.exit(1)
        else:
            # Interactive selection
            if args.non_interactive:
                print("❌ Non-interactive mode requires --drive-project-name")
                sdk_client.close()
                sys.exit(1)
            
            selected_project_name = select_project_interactive(actual_projects, project_display_type)
            
            if not selected_project_name:
                print("❌ No H2O Drive project selected")
                sdk_client.close()
                sys.exit(1)
            
            # Construct the full project path
            selected_drive_project = project_prefix + selected_project_name
        
        print(f"✅ Selected Drive project: {selected_drive_project}")
        
    except Exception as e:
        print(f"❌ Error with Drive projects: {e}")
        sdk_client.close()
        sys.exit(1)
    
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
        print("❌ Authentication failed. Check your access token and workspace configuration.")
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
