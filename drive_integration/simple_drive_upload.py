#!/usr/bin/env python3
"""
Simple H2O Drive Upload Script

This script demonstrates how to upload local data files to H2O Drive using a simple, direct approach.

Features:
- Connect directly to H2O Drive
- Load local project data from filesystem
- Upload files to Drive using native API
- Verify uploads and list Drive contents
- Simple progress tracking

Usage:
    python simple_drive_upload.py --project-path "JSON - tests" --project-name "my_uploaded_project"
    python simple_drive_upload.py --project-path "data" --project-name "my_project" --env-file ".env.upload"
"""

import os
import sys
import json
import asyncio
import tempfile
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Third-party imports
try:
    import h2o_drive
    import h2o_discovery
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Required package not installed: {e}")
    print("Install required packages with:")
    print("  pip install h2o-cloud-discovery")
    print("  pip install 'h2o-drive>=4'")
    print("  pip install python-dotenv")
    sys.exit(1)


def setup_environment(env_file: Optional[str] = None) -> bool:
    """
    Setup environment variables and validate configuration.
    
    Args:
        env_file: Optional path to environment file
        
    Returns:
        bool: True if setup successful, False otherwise
    """
    print("🔧 Setting up environment...")
    
    # Load environment variables
    if env_file and Path(env_file).exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        # Try default .env.upload file
        default_env = ".env.upload"
        if Path(default_env).exists():
            load_dotenv(default_env)
            print(f"✅ Loaded environment from {default_env}")
        else:
            print("⚠️ No environment file found, using system environment variables")
    
    # Validate required environment variables
    environment = os.environ.get('H2O_CLOUD_ENVIRONMENT')
    token = os.environ.get('H2O_CLOUD_CLIENT_PLATFORM_TOKEN')
    
    if not environment:
        print("❌ H2O_CLOUD_ENVIRONMENT not set")
        print("Set it with: export H2O_CLOUD_ENVIRONMENT='https://your-environment.h2o.ai/'")
        return False
    
    if not token:
        print("❌ H2O_CLOUD_CLIENT_PLATFORM_TOKEN not set")
        print("Set it with: export H2O_CLOUD_CLIENT_PLATFORM_TOKEN='your-token-here'")
        return False
    
    print(f"✅ Environment: {environment}")
    print(f"✅ Token: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'}")
    
    return True


async def connect_to_drive():
    """
    Connect to H2O Drive and return bucket instance.
    
    Returns:
        Bucket instance or None if connection failed
    """
    print("🔌 Connecting to H2O Drive...")
    
    try:
        # Discover H2O services
        discovery = h2o_discovery.discover()
        
        # Connect to Drive
        drive_client = h2o_drive.connect(discovery=discovery)
        bucket = drive_client.user_bucket()
        
        print("✅ Connected to H2O Drive successfully!")
        
        # Test connection by listing some objects
        objects = await bucket.list_objects()
        print(f"📁 Found {len(objects)} objects in your Drive")
        
        return bucket
        
    except Exception as e:
        print(f"❌ Failed to connect to H2O Drive: {e}")
        print("Please check your H2O_CLOUD_ENVIRONMENT and H2O_CLOUD_CLIENT_PLATFORM_TOKEN")
        return None


def load_local_project_data(project_path: Path) -> Dict[str, List[Tuple[str, Any]]]:
    """
    Load project data from local filesystem.
    
    Expected structure:
    project_path/
    ├── schema_metadata/
    ├── contexts/
    └── golden_examples/
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary containing loaded project data
    """
    print(f"📥 Loading project data from: {project_path}")
    
    project_data = {
        "schema_metadata": [],
        "contexts": [],
        "golden_examples": []
    }
    
    # Load schema metadata
    schema_path = project_path / "schema_metadata"
    if schema_path.exists():
        json_files = list(schema_path.glob("**/*.json"))
        print(f"📄 Found {len(json_files)} schema metadata files")
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["schema_metadata"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
    else:
        print("⚠️ No schema_metadata directory found")
    
    # Load contexts (JSON and TXT files)
    contexts_path = project_path / "contexts"
    if contexts_path.exists():
        # JSON files
        json_files = list(contexts_path.glob("**/*.json"))
        txt_files = list(contexts_path.glob("**/*.txt"))
        total_context_files = len(json_files) + len(txt_files)
        print(f"📄 Found {total_context_files} context files ({len(json_files)} JSON, {len(txt_files)} TXT)")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["contexts"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
        
        # Text files
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    data = f.read()
                    project_data["contexts"].append((str(txt_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {txt_file}: {e}")
    else:
        print("⚠️ No contexts directory found")
    
    # Load golden examples
    examples_path = project_path / "golden_examples"
    if examples_path.exists():
        json_files = list(examples_path.glob("**/*.json"))
        print(f"📄 Found {len(json_files)} golden example files")
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project_data["golden_examples"].append((str(json_file), data))
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
    else:
        print("⚠️ No golden_examples directory found")
    
    # Print summary
    total_files = sum(len(files) for files in project_data.values())
    print(f"\n📊 Loaded Project Data Summary:")
    for data_type, files in project_data.items():
        count = len(files)
        print(f"  - {data_type}: {count} files")
        
        # Show first few files
        for file_path, _ in files[:3]:
            filename = Path(file_path).name
            print(f"    • {filename}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
    
    print(f"\n✅ Total files loaded: {total_files}")
    return project_data


async def upload_data_to_drive(bucket, project_data: Dict[str, List[Tuple[str, Any]]], project_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Upload project data to H2O Drive with organized structure.
    
    Args:
        bucket: H2O Drive bucket instance
        project_data: Dictionary containing project data
        project_name: Name of the project in Drive
        
    Returns:
        Dictionary containing upload results
    """
    print(f"🚀 Starting upload to H2O Drive...")
    print(f"📁 Project name: {project_name}")
    
    upload_results = {
        "schema_metadata": {"success": 0, "failed": 0, "errors": []},
        "contexts": {"success": 0, "failed": 0, "errors": []},
        "golden_examples": {"success": 0, "failed": 0, "errors": []}
    }
    
    for data_type, files in project_data.items():
        if not files:
            print(f"⚠️ No {data_type} files to upload")
            continue
            
        print(f"\n📤 Uploading {len(files)} {data_type} files...")
        
        for file_path, data in files:
            filename = Path(file_path).name
            drive_key = f"{project_name}/{data_type}/{filename}"
            
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as tmp_file:
                    if isinstance(data, str):
                        # Text content
                        tmp_file.write(data)
                    else:
                        # JSON content
                        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
                    temp_path = tmp_file.name
                
                # Upload to Drive
                await bucket.upload_file(temp_path, drive_key)
                
                # Clean up temp file
                os.remove(temp_path)
                
                upload_results[data_type]["success"] += 1
                print(f"  ✅ Uploaded {filename}")
                
            except Exception as e:
                upload_results[data_type]["failed"] += 1
                upload_results[data_type]["errors"].append(f"{filename}: {str(e)}")
                print(f"  ❌ Failed to upload {filename}: {e}")
                
                # Clean up temp file if it exists
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
    
    return upload_results


async def verify_uploads(bucket, project_name: str) -> bool:
    """
    Verify uploads by listing files in H2O Drive.
    
    Args:
        bucket: H2O Drive bucket instance
        project_name: Name of the project in Drive
        
    Returns:
        bool: True if verification successful, False otherwise
    """
    print("🔍 Verifying uploads in H2O Drive...")
    
    try:
        all_objects = await bucket.list_objects()
        
        # Filter objects that belong to our project
        project_objects = [obj for obj in all_objects if obj.key.startswith(f"{project_name}/")]
        
        if project_objects:
            print(f"\n📁 Found {len(project_objects)} files for project '{project_name}':")
            
            # Group by data type
            by_type = {"schema_metadata": [], "contexts": [], "golden_examples": []}
            
            for obj in project_objects:
                key_parts = obj.key.split('/')
                if len(key_parts) >= 3:
                    data_type = key_parts[1]
                    if data_type in by_type:
                        by_type[data_type].append(obj.key)
            
            # Display organized results
            for data_type, files in by_type.items():
                if files:
                    print(f"\n  📂 {data_type}: {len(files)} files")
                    for file_key in files[:5]:  # Show first 5 files
                        filename = Path(file_key).name
                        print(f"    • {filename}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more files")
            
            return True
        else:
            print(f"❌ No files found for project '{project_name}'")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying uploads: {e}")
        return False


def print_summary(upload_results: Dict[str, Dict[str, Any]], project_name: str):
    """
    Print final summary of the upload session.
    
    Args:
        upload_results: Dictionary containing upload results
        project_name: Name of the project in Drive
    """
    print("\n📋 Upload Session Summary:")
    print("=" * 40)
    
    total_attempted = sum(r["success"] + r["failed"] for r in upload_results.values())
    total_successful = sum(r["success"] for r in upload_results.values())
    
    print(f"📊 Files processed: {total_attempted}")
    print(f"✅ Successfully uploaded: {total_successful}")
    print(f"❌ Failed uploads: {total_attempted - total_successful}")
    
    if total_successful > 0:
        success_rate = (total_successful / total_attempted) * 100 if total_attempted > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        print(f"📁 Project name in Drive: {project_name}")
    
    # Show detailed results
    print("\n📊 Upload Results by Type:")
    print("-" * 30)
    
    for data_type, results in upload_results.items():
        success = results["success"]
        failed = results["failed"]
        
        status_icon = "✅" if failed == 0 else "⚠️" if success > 0 else "❌"
        print(f"{status_icon} {data_type}: {success} successful, {failed} failed")
        
        # Show errors if any
        if results["errors"]:
            for error in results["errors"][:3]:  # Show first 3 errors
                print(f"    • {error}")
            if len(results["errors"]) > 3:
                print(f"    ... and {len(results['errors']) - 3} more errors")
    
    print("\n🎉 Simple Drive Upload Complete!")
    print("\n📚 What was accomplished:")
    print("   • Connected directly to H2O Drive")
    print("   • Loaded local project data")
    print("   • Uploaded files with organized structure")
    print("   • Verified uploads in Drive")
    print("   • Provided progress tracking")


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Upload local project data to H2O Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simple_drive_upload.py --project-path "JSON - tests" --project-name "my_uploaded_project"
  python simple_drive_upload.py --project-path "data" --project-name "my_project" --env-file ".env.upload"
        """
    )
    
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to the local project directory containing data to upload"
    )
    
    parser.add_argument(
        "--project-name",
        required=True,
        help="Name of the project in H2O Drive (will be prefixed with 'home/' if not already)"
    )
    
    parser.add_argument(
        "--env-file",
        help="Path to environment file (default: .env.upload)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Simple H2O Drive Upload")
    print("=" * 50)
    
    # Setup environment
    if not setup_environment(args.env_file):
        sys.exit(1)
    
    # Validate project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        print("Please check the path and try again.")
        print(f"Current working directory: {Path.cwd()}")
        sys.exit(1)
    
    # Prepare project name
    project_name = args.project_name
    if not project_name.startswith("home/"):
        project_name = f"home/{project_name}"
    
    # Connect to H2O Drive
    bucket = await connect_to_drive()
    if not bucket:
        sys.exit(1)
    
    # Load local project data
    project_data = load_local_project_data(project_path)
    
    if not any(len(files) > 0 for files in project_data.values()):
        print("❌ No data found in the specified project path")
        print("Expected directory structure:")
        print("  project_path/")
        print("  ├── schema_metadata/")
        print("  ├── contexts/")
        print("  └── golden_examples/")
        sys.exit(1)
    
    # Upload data to Drive
    upload_results = await upload_data_to_drive(bucket, project_data, project_name)
    
    # Verify uploads
    verification_success = await verify_uploads(bucket, project_name)
    
    # Print summary
    print_summary(upload_results, project_name)
    
    # Exit with appropriate code
    total_attempted = sum(r["success"] + r["failed"] for r in upload_results.values())
    total_successful = sum(r["success"] for r in upload_results.values())
    
    if total_successful == total_attempted and verification_success:
        print("\n🎉 All operations completed successfully!")
        sys.exit(0)
    elif total_successful > 0:
        print("\n⚠️ Upload completed with some issues.")
        sys.exit(1)
    else:
        print("\n❌ Upload failed completely.")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
