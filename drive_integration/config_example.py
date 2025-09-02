"""
Configuration example for the simplified Drive to T2E integration script.

Copy this file to config.py and update the values for your environment.
"""

# Text2Everything API Configuration
T2E_CONFIG = {
    "base_url": "http://text2everything.text2everything.svc.cluster.local:8000",
    "api_key": "",  # Set this or use T2E_API_KEY environment variable
    "timeout": 60,
    "max_retries": 3
}

# H2O Drive Configuration
DRIVE_CONFIG = {
    "auto_connect": True,  # Automatically connect to H2O Drive
    "default_bucket": "user",  # Use user bucket by default
}

# Data Processing Configuration
DATA_CONFIG = {
    "validate_before_upload": True,  # Enable validation before upload
    "skip_empty_files": True,  # Skip files with no content
    "auto_generate_names": True,  # Auto-generate names from filenames if missing
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "show_progress": True,  # Show progress bars
    "verbose_errors": True,  # Show detailed error messages
}
