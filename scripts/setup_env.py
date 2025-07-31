#!/usr/bin/env python3
"""
Environment Setup Script for Universal Knowledge Hub
This script helps set up the required environment variables.
"""

import os
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

def check_required_vars():
    """Check if required environment variables are set."""
    required_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SECRET_KEY",
        "API_KEY_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def setup_frontend_env():
    """Set up frontend environment variables."""
    frontend_env = Path("frontend/.env.local")
    
    frontend_env_content = """# Frontend Environment Variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8002
NEXT_PUBLIC_WS_URL=ws://localhost:8002
NEXT_PUBLIC_APP_NAME=Universal Knowledge Hub
NEXT_PUBLIC_VERSION=1.0.0
NEXT_PUBLIC_ENABLE_FEEDBACK=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_EXPERT_MODE=false
NEXT_PUBLIC_API_KEY=user-Rkfu2jcgQ1mIIIWRhmDxbZH4w8b0yJPcVOxZ7XD_Vmw
"""
    
    frontend_env.write_text(frontend_env_content)
    print("✅ Created frontend/.env.local")

def main():
    """Main setup function."""
    print("🚀 Setting up Universal Knowledge Hub environment...")
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check required variables
    if not check_required_vars():
        print("\n📝 Please set the missing environment variables in your .env file")
        return False
    
    # Setup frontend environment
    setup_frontend_env()
    
    print("\n✅ Environment setup completed!")
    print("\nNext steps:")
    print("1. Start the backend: python api/main.py")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Test the application: python test_ai_improvements.py")
    
    return True

if __name__ == "__main__":
    main() 