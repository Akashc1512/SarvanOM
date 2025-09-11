#!/usr/bin/env python3
"""
Simple backend startup script for SarvanOM
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the backend service"""
    print("🚀 Starting SarvanOM Backend Service...")
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check if virtual environment exists
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run: python -m venv venv")
        return 1
    
    # Check if gateway directory exists
    gateway_path = project_root / "services" / "gateway"
    if not gateway_path.exists():
        print("❌ Gateway service not found!")
        return 1
    
    try:
        # Start the backend service
        print("📍 Starting gateway service...")
        subprocess.run([
            sys.executable, "main.py"
        ], cwd=gateway_path, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend service: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Backend service stopped by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())
