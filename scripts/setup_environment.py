#!/usr/bin/env python3
"""
Environment Setup Script for Universal Knowledge Hub
This script helps set up the required environment variables and dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_template = Path("env.template")
    env_file = Path(".env")
    
    if not env_file.exists():
        if env_template.exists():
            shutil.copy(env_template, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please update the API keys in .env file:")
            print("   - OPENAI_API_KEY")
            print("   - ANTHROPIC_API_KEY")
            print("   - PINECONE_API_KEY (if using Pinecone)")
        else:
            print("❌ env.template not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def check_python_dependencies():
    """Check and install Python dependencies."""
    print("\n🔍 Checking Python dependencies...")
    
    try:
        # Check if virtual environment exists
        venv_path = Path(".venv")
        if not venv_path.exists():
            print("📦 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
        # Activate virtual environment and install requirements
        if os.name == "nt":  # Windows
            python_path = ".venv/Scripts/python.exe"
            pip_path = ".venv/Scripts/pip.exe"
        else:  # Unix/Linux
            python_path = ".venv/bin/python"
            pip_path = ".venv/bin/pip"
        
        if Path(python_path).exists():
            print("📦 Installing Python dependencies...")
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
            print("✅ Python dependencies installed")
            return True
        else:
            print("❌ Virtual environment not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False

def check_node_dependencies():
    """Check and install Node.js dependencies."""
    print("\n🔍 Checking Node.js dependencies...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Check if node_modules exists
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("📦 Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            print("✅ Node.js dependencies installed")
        else:
            print("✅ Node.js dependencies already installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Node.js dependencies: {e}")
        return False

def check_required_services():
    """Check if required services are available."""
    print("\n🔍 Checking required services...")
    
    # Check if Redis is running (optional for development)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
        r.ping()
        print("✅ Redis is running")
    except:
        print("⚠️  Redis not running (optional for development)")
    
    # Check if PostgreSQL is running (optional for development)
    try:
        import psycopg2
        psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres"
        )
        print("✅ PostgreSQL is running")
    except:
        print("⚠️  PostgreSQL not running (optional for development)")

def create_startup_scripts():
    """Create startup scripts for easy development."""
    print("\n📝 Creating startup scripts...")
    
    # Create backend startup script
    backend_script = """#!/bin/bash
# Start the backend server
cd "$(dirname "$0")"
source .venv/bin/activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    
    # Create frontend startup script
    frontend_script = """#!/bin/bash
# Start the frontend development server
cd "$(dirname "$0")/frontend"
npm run dev
"""
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script)
    
    # Make scripts executable (Unix/Linux)
    if os.name != "nt":
        os.chmod("start_backend.sh", 0o755)
        os.chmod("start_frontend.sh", 0o755)
    
    print("✅ Created startup scripts:")
    print("   - start_backend.sh")
    print("   - start_frontend.sh")

def main():
    """Main setup function."""
    print("🚀 Universal Knowledge Hub Setup")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Check Python dependencies
    if not check_python_dependencies():
        return
    
    # Check Node.js dependencies
    if not check_node_dependencies():
        return
    
    # Check required services
    check_required_services()
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update API keys in .env file")
    print("2. Start backend: ./start_backend.sh")
    print("3. Start frontend: ./start_frontend.sh")
    print("4. Open http://localhost:3000 in your browser")

if __name__ == "__main__":
    main() 