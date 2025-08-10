#!/usr/bin/env python3
"""
Check .env file status and API key values
"""

import os
import pathlib
from dotenv import load_dotenv

def check_env_status():
    print("🔍 CHECKING .env FILE STATUS")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = pathlib.Path('.env')
    print(f".env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f".env file size: {env_file.stat().st_size} bytes")
        
        # Load and check values
        load_dotenv()
        
        print("\n🔑 API KEY STATUS:")
        print("-" * 30)
        
        # Check each API key
        api_keys = {
            "HuggingFace": os.getenv('HUGGINGFACE_API_KEY'),
            "OpenAI": os.getenv('OPENAI_API_KEY'), 
            "Anthropic": os.getenv('ANTHROPIC_API_KEY')
        }
        
        for name, key in api_keys.items():
            if not key:
                status = "❌ NOT SET"
                preview = ""
            elif "your_" in key.lower():
                status = "⚠️ PLACEHOLDER"
                preview = f"({key[:20]}...)"
            elif len(key.strip()) < 10:
                status = "⚠️ TOO SHORT"
                preview = f"({key})"
            else:
                status = "✅ REAL KEY"
                preview = f"({key[:10]}...{key[-5:]})"
            
            print(f"  {name:12}: {status} {preview}")
        
        print(f"\n🎯 ENVIRONMENT SETTINGS:")
        print(f"  PRIORITIZE_FREE_MODELS: {os.getenv('PRIORITIZE_FREE_MODELS')}")
        print(f"  USE_DYNAMIC_SELECTION: {os.getenv('USE_DYNAMIC_SELECTION')}")
        
        # Check if any real keys exist
        real_keys = [name for name, key in api_keys.items() 
                    if key and "your_" not in key.lower() and len(key.strip()) >= 10]
        
        if real_keys:
            print(f"\n🚀 WORKING PROVIDERS: {', '.join(real_keys)}")
            print("💡 These should give fast responses!")
        else:
            print(f"\n❌ NO WORKING API KEYS FOUND")
            print("🔧 Please add real API keys to .env file")
            
    else:
        print("❌ .env file not found in current directory")
        print("💡 Create .env file with your API keys")
        
        # Show current directory
        current_dir = pathlib.Path.cwd()
        print(f"📁 Current directory: {current_dir}")
        
        # Look for .env files
        env_files = list(current_dir.glob("*.env*"))
        if env_files:
            print(f"📄 Found env files: {[f.name for f in env_files]}")

if __name__ == "__main__":
    check_env_status()
