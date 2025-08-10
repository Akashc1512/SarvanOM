#!/usr/bin/env python3
"""
Simple test to check why real API keys aren't loading
"""

import os
from pathlib import Path

def simple_test():
    print("🔍 SIMPLE ENVIRONMENT TEST")
    print("=" * 40)
    
    # Test 1: Check if .env file exists and size
    env_file = Path(".env")
    print(f"📄 .env exists: {env_file.exists()}")
    if env_file.exists():
        print(f"📄 Size: {env_file.stat().st_size} bytes")
    
    # Test 2: Read first few lines directly
    print("\n📝 First 20 lines of .env:")
    try:
        with open(".env", "r") as f:
            for i, line in enumerate(f, 1):
                if i <= 20:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        print(f"  {i:2d}: {line}")
                if i >= 20:
                    break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Check specific API key lines
    print("\n🔑 Looking for API key lines:")
    try:
        with open(".env", "r") as f:
            content = f.read()
            
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'API_KEY' in line and not line.strip().startswith('#'):
                print(f"  Line {i}: {line.strip()}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Check environment variables WITHOUT dotenv
    print("\n🌍 Environment variables (before dotenv):")
    api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'HUGGINGFACE_API_KEY']
    for key in api_keys:
        value = os.environ.get(key, 'NOT_SET')
        if value != 'NOT_SET':
            print(f"  {key}: {value[:10]}...{value[-5:]}")
        else:
            print(f"  {key}: NOT_SET")
    
    # Test 5: Load with dotenv and check again
    print("\n🔄 Loading with dotenv:")
    try:
        from dotenv import load_dotenv
        result = load_dotenv(override=True)
        print(f"  load_dotenv() returned: {result}")
        
        print("\n🌍 Environment variables (after dotenv):")
        for key in api_keys:
            value = os.getenv(key, 'NOT_SET')
            if value != 'NOT_SET' and len(value) > 10:
                print(f"  {key}: {value[:10]}...{value[-5:]}")
                
                # Check if it looks like a real key
                if 'your_' in value:
                    print(f"    ⚠️ Still placeholder!")
                elif key == 'OPENAI_API_KEY' and value.startswith('sk-'):
                    print(f"    ✅ Real OpenAI key!")
                elif key == 'ANTHROPIC_API_KEY' and value.startswith('sk-ant-'):
                    print(f"    ✅ Real Anthropic key!")
                elif key == 'HUGGINGFACE_API_KEY' and value.startswith('hf_'):
                    print(f"    ✅ Real HuggingFace key!")
                else:
                    print(f"    ❓ Unknown format")
            else:
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"❌ Dotenv error: {e}")

if __name__ == "__main__":
    simple_test()
