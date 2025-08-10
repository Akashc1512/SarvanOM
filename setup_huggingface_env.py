#!/usr/bin/env python3
"""
Setup script for HuggingFace environment variables
Helps configure HuggingFace tokens for SarvanOM
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_huggingface_env():
    """Setup HuggingFace environment variables"""
    
    print("🚀 HUGGINGFACE ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Read existing .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check for HuggingFace tokens
        has_read_token = "HUGGINGFACE_READ_TOKEN" in content
        has_write_token = "HUGGINGFACE_WRITE_TOKEN" in content
        has_api_token = "HUGGINGFACE_API_TOKEN" in content
        
        print(f"📋 Current HuggingFace tokens:")
        print(f"   Read Token: {'✅' if has_read_token else '❌'}")
        print(f"   Write Token: {'✅' if has_write_token else '❌'}")
        print(f"   API Token: {'✅' if has_api_token else '❌'}")
        
        if not any([has_read_token, has_write_token, has_api_token]):
            print("\n⚠️  No HuggingFace tokens found in .env file")
            print("Please add the following to your .env file:")
            print("HUGGINGFACE_READ_TOKEN=your_read_token_here")
            print("HUGGINGFACE_WRITE_TOKEN=your_write_token_here")
            print("HUGGINGFACE_API_TOKEN=your_api_token_here")
    else:
        print("❌ .env file not found")
        print("Please create a .env file in the root directory with:")
        print("HUGGINGFACE_READ_TOKEN=your_read_token_here")
        print("HUGGINGFACE_WRITE_TOKEN=your_write_token_here")
        print("HUGGINGFACE_API_TOKEN=your_api_token_here")
    
    # Set environment variables for current session
    print("\n🔧 Setting environment variables for current session...")
    
    # You can set these manually or they will be loaded from .env file
    # For testing purposes, we'll set some default values
    if not os.getenv("HUGGINGFACE_READ_TOKEN"):
        os.environ["HUGGINGFACE_READ_TOKEN"] = "hf_demo_read_token"
        print("   Set HUGGINGFACE_READ_TOKEN (demo)")
    
    if not os.getenv("HUGGINGFACE_WRITE_TOKEN"):
        os.environ["HUGGINGFACE_WRITE_TOKEN"] = "hf_demo_write_token"
        print("   Set HUGGINGFACE_WRITE_TOKEN (demo)")
    
    if not os.getenv("HUGGINGFACE_API_TOKEN"):
        os.environ["HUGGINGFACE_API_TOKEN"] = "hf_demo_api_token"
        print("   Set HUGGINGFACE_API_TOKEN (demo)")
    
    print("\n✅ Environment setup complete!")
    print("\n📝 Next steps:")
    print("1. Replace the demo tokens with your actual HuggingFace tokens")
    print("2. Restart the server to load the new environment variables")
    print("3. Test the HuggingFace integration")

def test_huggingface_config():
    """Test HuggingFace configuration"""
    
    print("\n🧪 TESTING HUGGINGFACE CONFIGURATION")
    print("=" * 50)
    
    try:
        # Import and test configuration
        sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
        from config.huggingface_config import huggingface_config
        
        print(f"📋 Configuration loaded:")
        print(f"   Cache Directory: {huggingface_config.cache_dir}")
        print(f"   Device: {huggingface_config.device}")
        print(f"   Authenticated: {huggingface_config.is_authenticated()}")
        
        # Check for configuration issues
        issues = huggingface_config.validate_config()
        if issues:
            print(f"⚠️  Configuration issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Configuration is valid")
        
        # Test token access
        read_token = huggingface_config.get_token_for_operation("read")
        write_token = huggingface_config.get_token_for_operation("write")
        api_token = huggingface_config.get_token_for_operation("api")
        
        print(f"🔑 Token access:")
        print(f"   Read Token: {'✅' if read_token else '❌'}")
        print(f"   Write Token: {'✅' if write_token else '❌'}")
        print(f"   API Token: {'✅' if api_token else '❌'}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

if __name__ == "__main__":
    setup_huggingface_env()
    test_huggingface_config()
    
    print("\n🎯 SETUP COMPLETE!")
    print("You can now run the HuggingFace integration tests.")
