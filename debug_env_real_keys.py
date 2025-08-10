#!/usr/bin/env python3
"""
Debug Environment Variables - Real Keys Check
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def debug_environment():
    print("🔍 ENVIRONMENT DEBUGGING")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📂 Current Directory: {current_dir}")
    
    # Look for .env file
    env_file = current_dir / ".env"
    print(f"📄 .env file path: {env_file}")
    print(f"📄 .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f"📄 .env file size: {env_file.stat().st_size} bytes")
        print("📄 .env file content preview:")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')[:10]  # First 10 lines
                for i, line in enumerate(lines, 1):
                    if 'API_KEY' in line:
                        # Hide the actual key value for security
                        if '=' in line:
                            key, value = line.split('=', 1)
                            print(f"  {i:2d}: {key}=***{value[-10:] if len(value) > 10 else '***'}")
                        else:
                            print(f"  {i:2d}: {line}")
                    else:
                        print(f"  {i:2d}: {line}")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    
    print()
    print("🔄 Loading environment variables...")
    load_dotenv()
    
    # Check specific keys
    keys_to_check = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'HUGGINGFACE_API_KEY',
        'LLM_TIMEOUT_SECONDS',
        'PRIORITIZE_FREE_MODELS'
    ]
    
    print("🔑 Environment Variables Status:")
    for key in keys_to_check:
        value = os.getenv(key, 'NOT_SET')
        if value == 'NOT_SET':
            print(f"  ❌ {key}: NOT SET")
        elif 'your_' in value:
            print(f"  ⚠️ {key}: PLACEHOLDER ({value[:20]}...)")
        elif key.endswith('_API_KEY') and len(value) > 10:
            print(f"  ✅ {key}: REAL KEY DETECTED (***{value[-8:]})")
        else:
            print(f"  ✅ {key}: {value}")
    
    print()
    print("🎯 RECOMMENDATIONS:")
    if not env_file.exists():
        print("  📝 Create .env file in root directory")
        print("  📋 Copy content from CREATE_ENV_FILE_INSTRUCTIONS.md")
    else:
        # Check if we have any real keys
        openai_key = os.getenv('OPENAI_API_KEY', '')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        if 'your_' in openai_key or 'your_' in anthropic_key:
            print("  🔄 Replace placeholder values with real API keys")
            print("  📝 Edit .env file and change:")
            print("     OPENAI_API_KEY=sk-proj-your-real-key")
            print("     ANTHROPIC_API_KEY=sk-ant-your-real-key")
        else:
            print("  🚀 Environment looks ready for testing!")

if __name__ == "__main__":
    debug_environment()
