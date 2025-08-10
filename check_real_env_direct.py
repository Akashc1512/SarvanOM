#!/usr/bin/env python3
"""
Direct .env File Content Check
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_direct():
    print("🔍 DIRECT .env FILE CHECK")
    print("=" * 50)
    
    env_path = Path(".env")
    print(f"📂 Looking for: {env_path.absolute()}")
    print(f"📄 File exists: {env_path.exists()}")
    
    if env_path.exists():
        print(f"📄 File size: {env_path.stat().st_size} bytes")
        
        print("\n📝 READING FILE CONTENT:")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            api_key_lines = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and 'API_KEY' in line and not line.startswith('#'):
                    api_key_lines.append((i, line))
            
            print(f"📊 Found {len(api_key_lines)} API key lines:")
            for line_num, line in api_key_lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Security: Show only first/last few chars
                    if value and len(value) > 10:
                        masked_value = f"{value[:3]}...{value[-4:]}"
                        print(f"  Line {line_num:2d}: {key}={masked_value}")
                        
                        # Check if it's a real key
                        if 'your_' in value:
                            print(f"            ⚠️ PLACEHOLDER detected")
                        elif key == 'OPENAI_API_KEY' and value.startswith('sk-'):
                            print(f"            ✅ REAL OpenAI key detected")
                        elif key == 'ANTHROPIC_API_KEY' and value.startswith('sk-ant-'):
                            print(f"            ✅ REAL Anthropic key detected")  
                        elif key == 'HUGGINGFACE_API_KEY' and value.startswith('hf_'):
                            print(f"            ✅ REAL HuggingFace key detected")
                        else:
                            print(f"            ❓ Key format unclear")
                    else:
                        print(f"  Line {line_num:2d}: {line}")
                        print(f"            ⚠️ Empty or too short")
                        
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    print("\n🔄 LOADING WITH PYTHON-DOTENV:")
    load_dotenv()
    
    # Check environment variables
    keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'HUGGINGFACE_API_KEY']
    working_keys = 0
    
    for key in keys:
        value = os.getenv(key, '')
        if value and 'your_' not in value and len(value) > 10:
            print(f"✅ {key}: LOADED (**{value[-6:]})")
            working_keys += 1
        elif value:
            print(f"⚠️ {key}: PLACEHOLDER ({value[:20]}...)")
        else:
            print(f"❌ {key}: NOT FOUND")
    
    print(f"\n🎯 SUMMARY: {working_keys}/3 real API keys detected")
    
    if working_keys > 0:
        print("🚀 READY FOR FAST RESPONSES!")
        return True
    else:
        print("⏳ Still need real API keys for fast responses")
        return False

if __name__ == "__main__":
    check_env_direct()
