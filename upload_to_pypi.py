#!/usr/bin/env python3
"""
Script to upload Rencom CLI to PyPI
"""

import os
import sys
from pathlib import Path

def upload_to_pypi():
    """Upload package to PyPI using twine"""
    
    # Check if dist directory exists
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory not found. Run 'python -m build' first.")
        return False
    
    # Check if packages exist
    packages = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
    if not packages:
        print("❌ No packages found in dist/ directory.")
        return False
    
    print("📦 Found packages:")
    for pkg in packages:
        print(f"   - {pkg.name}")
    
    # Get token from environment, .env file, or prompt
    token = os.getenv("PYPI_TOKEN")
    
    # Try to load from .env file if not in environment
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("PYPI_TOKEN")
        except ImportError:
            pass
    
    if not token:
        print("\n🔑 Enter your PyPI API token (or set PYPI_TOKEN environment variable or add to .env file):")
        token = input().strip()
    
    if not token:
        print("❌ No token provided.")
        return False
    
    # Create twine command
    import subprocess
    
    # Set environment variables for twine
    env = os.environ.copy()
    env["TWINE_USERNAME"] = "__token__"
    env["TWINE_PASSWORD"] = token
    
    print("\n🚀 Uploading to PyPI...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "twine", "upload", "dist/*"
        ], env=env, capture_output=True, text=True, check=True)
        
        print("✅ Upload successful!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Upload failed!")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    success = upload_to_pypi()
    sys.exit(0 if success else 1) 