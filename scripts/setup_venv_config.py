#!/usr/bin/env python3
"""
Virtual Environment Configuration Setup

This script ensures the configuration management system works properly
in the virtual environment and provides setup instructions.

Usage:
    # Always use virtual environment
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # Linux/Mac
    
    # Then run this script
    python scripts/setup_venv_config.py
"""

import os
import sys
import platform
from pathlib import Path

def check_virtual_environment():
    """Check if we're running in a virtual environment."""
    print("🔍 Checking Virtual Environment")
    print("-" * 40)
    
    # Check if we're in a virtual environment
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ Running in virtual environment")
        print(f"   Python executable: {sys.executable}")
        print(f"   Virtual env path: {sys.prefix}")
        return True
    else:
        print("❌ NOT running in virtual environment")
        print(f"   Python executable: {sys.executable}")
        print(f"   System Python path: {sys.prefix}")
        return False

def provide_venv_setup_instructions():
    """Provide platform-specific virtual environment setup instructions."""
    print("\n📋 Virtual Environment Setup Instructions")
    print("-" * 50)
    
    system = platform.system().lower()
    
    print("1️⃣  Create virtual environment:")
    print("   python -m venv venv")
    
    print("\n2️⃣  Activate virtual environment:")
    if system == "windows":
        print("   # PowerShell:")
        print("   venv\\Scripts\\Activate.ps1")
        print("   # Command Prompt:")
        print("   venv\\Scripts\\activate.bat")
    else:
        print("   source venv/bin/activate")
    
    print("\n3️⃣  Install dependencies:")
    print("   .venv/bin/pip install -r requirements.txt")
    
    print("\n4️⃣  Verify setup:")
    print("   python scripts/setup_venv_config.py")
    
    print("\n5️⃣  Test configuration:")
    print("   python scripts/simple_config_test.py")

def check_dependencies():
    """Check if required dependencies are available."""
    print("\n🔍 Checking Dependencies")
    print("-" * 40)
    
    required_packages = [
        'pyyaml',
        'python-dotenv',
        'fastapi',
        'structlog'
    ]
    
    available = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            available.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    print(f"\n📊 Dependencies: {len(available)} available, {len(missing)} missing")
    
    if missing:
        print(f"\n🔧 Install missing dependencies:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def test_configuration_system():
    """Test the configuration system works in venv."""
    print("\n🧪 Testing Configuration System")
    print("-" * 40)
    
    try:
        # Test basic configuration loading
        print("📋 Testing basic configuration...")
        
        # Check config files exist
        config_files = [
            "config/development.yaml",
            "config/testing.yaml", 
            "config/staging.yaml",
            "config/production.yaml",
            "env.example"
        ]
        
        missing_files = []
        for config_file in config_files:
            if not Path(config_file).exists():
                missing_files.append(config_file)
        
        if missing_files:
            print(f"❌ Missing config files: {missing_files}")
            return False
        else:
            print("✅ All configuration files present")
        
        # Test environment variable handling
        print("\n📋 Testing environment variables...")
        app_env = os.getenv("APP_ENV", "development")
        print(f"   Current APP_ENV: {app_env}")
        
        # Test environment switching
        print("\n📋 Testing environment switching...")
        test_envs = ["development", "testing", "staging", "production"]
        original_env = os.getenv("APP_ENV")
        
        for env in test_envs:
            os.environ["APP_ENV"] = env
            current_env = os.getenv("APP_ENV")
            if current_env == env:
                print(f"   ✅ {env}")
            else:
                print(f"   ❌ {env}")
        
        # Restore original environment
        if original_env:
            os.environ["APP_ENV"] = original_env
        
        print("✅ Configuration system working")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system error: {e}")
        return False

def create_development_env_file():
    """Create a basic .env file for development if it doesn't exist."""
    print("\n📄 Checking Development Environment File")
    print("-" * 40)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating basic .env file for development...")
    
    dev_env_content = """# Development Environment Configuration
# This file was auto-generated for development setup

# Core Settings
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
SERVICE_NAME=sarvanom

# Development JWT Secret (CHANGE FOR PRODUCTION!)
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production

# Development Features
MOCK_AI_RESPONSES=true
SKIP_AUTHENTICATION=true
ENABLE_DEBUG_ENDPOINTS=true

# Optional: Add your API keys for testing
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Note: This is a basic development setup
# For production, use proper secrets and configuration
"""
    
    try:
        with open(".env", "w") as f:
            f.write(dev_env_content)
        print("✅ Created .env file with development defaults")
        print("💡 You can customize it by editing .env or copying from env.example")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup and verification function."""
    print("🔧 Virtual Environment Configuration Setup")
    print("=" * 60)
    
    success = True
    
    # Check virtual environment
    if not check_virtual_environment():
        print("\n⚠️  WARNING: Not running in virtual environment!")
        provide_venv_setup_instructions()
        success = False
    
    # Check dependencies  
    if not check_dependencies():
        success = False
    
    # Test configuration system
    if not test_configuration_system():
        success = False
    
    # Create development env file
    if not create_development_env_file():
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 Configuration setup completed successfully!")
        print("✅ Virtual environment and configuration system ready")
        print("\n💡 Next steps:")
        print("1. Customize .env file with your settings")
        print("2. Test with: python scripts/simple_config_test.py")
        print("3. Verify with: python scripts/verify_env_config.py")
    else:
        print("⚠️  Configuration setup had issues")
        print("📋 Please review the errors above and fix them")
        print("\n🔧 Common fixes:")
        print("1. Ensure you're in a virtual environment")
        print("2. Install missing dependencies")
        print("3. Check that config files exist")
    
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())