#!/usr/bin/env python3
"""
Super simple project creation test using just requests.
Replace the API_KEY and BASE_URL with your actual values.
"""

import requests
import json
from datetime import datetime

# Replace these with your actual values
API_KEY = "your-api-key-here"
BASE_URL = "https://your-api-endpoint.com"  # e.g., "https://api.text2everything.com"

def create_project():
    """Create a project with raw HTTP requests."""
    
    url = f"{BASE_URL.rstrip('/')}/api/projects"
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    project_data = {
        "name": f"Test Project {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    print(f"Creating project: {project_data['name']}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=project_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✓ SUCCESS!")
        else:
            print("❌ FAILED")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    create_project()
