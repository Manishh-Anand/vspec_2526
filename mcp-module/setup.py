#!/usr/bin/env python3
"""
Setup script for MCP Module
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements" / "base.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="mcp-module",
    version="1.0.0",
    author="MCP Module Team",
    author_email="team@mcp-module.com",
    description="Production-ready Model Context Protocol implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/mcp-module",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "prod": [
            "sentry-sdk>=1.35.0",
            "gunicorn>=21.2.0",
            "uvicorn>=0.23.0",
            "cryptography>=41.0.0",
            "uvloop>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-module=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    zip_safe=False,
)
