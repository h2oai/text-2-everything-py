"""
Setup configuration for the Text2Everything SDK.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="text2everything-sdk",
    version="0.1.6-rc1",
    author="Text2Everything Team",
    author_email="support@h2o.ai",
    description="Official Python SDK for the Text2Everything API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/h2oai/text-2-everything",
    packages=['text2everything_sdk', 'text2everything_sdk.models', 'text2everything_sdk.resources', 'text2everything_sdk.tests'],
    package_dir={
        'text2everything_sdk': '.',
        'text2everything_sdk.models': 'models',
        'text2everything_sdk.resources': 'resources', 
        'text2everything_sdk.tests': 'tests'
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.22.0",
        ],
        "integrations": [
            "pandas>=1.5.0",
            "h2o-drive>=1.0.0",
            "jupyter>=1.0.0",
        ]
    },
    keywords=[
        "text2sql",
        "sql",
        "natural language",
        "database",
        "api",
        "sdk",
        "h2o",
        "ai",
        "machine learning"
    ],
    project_urls={
        "Bug Reports": "https://github.com/h2oai/text-2-everything/issues",
        "Source": "https://github.com/h2oai/text-2-everything",
        "Documentation": "https://docs.text2everything.com",
    },
    include_package_data=True,
    zip_safe=False,
)
