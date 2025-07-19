"""Setup configuration for Rencom CLI."""

import os
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Try to read requirements.txt, fall back to hardcoded list if not found
try:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements for CLI only (not the full API)
    requirements = [
        "click>=8.1.7",
        "rich>=13.7.0", 
        "requests>=2.25.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "PyYAML>=6.0.1"
    ]

setup(
    name="rencom-cli",
    version="1.0.3",
    author="Ren Team",
    description="Command-line interface for the Rencom Reviews API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rencom=cli.main:cli",
        ],
    },
    include_package_data=True,
)