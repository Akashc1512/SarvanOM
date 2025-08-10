#!/usr/bin/env python3
"""
Diagnose Environment Loading Issues
When real API keys are added but system still reads placeholders
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import importlib

def diagnose_env_issues():
    print("🔍 DIAGNOSING ENVIRONMENT LOADING ISSUES")
    print("=" * 60)
    
    # Issue 1: Multiple .env files
    print("1️⃣ CHECKING FOR MULTIPLE .env FILES:")
    current_dir = Path.cwd()
    parent_dirs = [current_dir] + list(current_dir.parents)
    
    env_files_found = []
    for dir_path in parent_dirs[:3]:  # Check current and 2 parent levels
        env_file = dir_path / ".env"
        if env_file.exists():
            env_files_found.append(env_file)
            size = env_file.stat().st_size
            print(f"   📄 Found: {env_file} ({size} bytes)")
    
    if len(env_files_found) > 1:
        print("   ⚠️ MULTIPLE .env FILES DETECTED - May cause conflicts!")
    elif len(env_files_found) == 1:
        print("   ✅ Single .env file found")
    else:
        print("   ❌ No .env files found")
    
    print()
    
    # Issue 2: File encoding problems
    print("2️⃣ CHECKING FILE ENCODING:")
    env_path = Path(".env")
    if env_path.exists():
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']
            for encoding in encodings:
                try:
                    with open(env_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    if 'OPENAI_API_KEY' in content:
                        print(f"   ✅ Successfully read with {encoding}")
                        # Check for BOM or special characters
                        if content.startswith('\ufeff'):
                            print("   ⚠️ BOM detected - may cause issues")
                        break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    print()
    
    # Issue 3: Check file permissions
    print("3️⃣ CHECKING FILE PERMISSIONS:")
    if env_path.exists():
        try:
            # Test read access
            with open(env_path, 'r') as f:
                f.read(100)
            print("   ✅ File is readable")
            
            # Test write access
            stat = env_path.stat()
            print(f"   📊 File size: {stat.st_size} bytes")
            print(f"   📊 Last modified: {stat.st_mtime}")
            
        except PermissionError:
            print("   ❌ Permission denied - file may be locked")
        except Exception as e:
            print(f"   ❌ Error accessing file: {e}")
    
    print()
    
    # Issue 4: Environment variable caching
    print("4️⃣ CHECKING ENVIRONMENT CACHING:")
    
    # Clear any existing environment
    keys_to_clear = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'HUGGINGFACE_API_KEY']
    for key in keys_to_clear:
        if key in os.environ:
            print(f"   🔄 Clearing cached {key}")
            del os.environ[key]
    
    # Force reload dotenv
    load_dotenv(override=True)
    
    print("   ✅ Environment reloaded with override=True")
    
    print()
    
    # Issue 5: Check actual content vs what's loaded
    print("5️⃣ COMPARING FILE CONTENT VS LOADED VALUES:")
    
    if env_path.exists():
        # Read file directly
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        api_lines = [line.strip() for line in lines if 'API_KEY' in line and not line.strip().startswith('#')]
        
        print("   📄 File content:")
        for line in api_lines[:3]:  # Show first 3 API key lines
            if '=' in line:
                key, value = line.split('=', 1)
                masked = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
                print(f"      {key}={masked}")
        
        print("   🔄 Loaded environment:")
        for key in keys_to_clear:
            value = os.getenv(key, 'NOT_FOUND')
            if value != 'NOT_FOUND':
                masked = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
                print(f"      {key}={masked}")
                
                # Check if they match
                file_line = next((line for line in api_lines if line.startswith(f"{key}=")), None)
                if file_line:
                    _, file_value = file_line.split('=', 1)
                    if file_value.strip() == value.strip():
                        print(f"         ✅ Matches file content")
                    else:
                        print(f"         ⚠️ MISMATCH with file content!")
            else:
                print(f"      {key}=NOT_FOUND")
    
    print()
    
    # Issue 6: Python path and working directory
    print("6️⃣ CHECKING PYTHON ENVIRONMENT:")
    print(f"   📂 Current working directory: {Path.cwd()}")
    print(f"   🐍 Python executable: {sys.executable}")
    print(f"   📦 Python-dotenv location: {importlib.util.find_spec('dotenv').origin}")
    
    # Check if running from venv
    if 'venv' in sys.executable:
        print("   ✅ Running from virtual environment")
    else:
        print("   ⚠️ Not running from expected venv")
    
    print()
    
    # Issue 7: Test direct file modification detection
    print("7️⃣ TESTING LIVE FILE MODIFICATION:")
    print("   💡 Try this test:")
    print("   1. Add a test line to .env: TEST_KEY=test_value_123")
    print("   2. Run this script again")
    print("   3. Check if TEST_KEY appears in loaded environment")
    
    test_value = os.getenv('TEST_KEY')
    if test_value:
        print(f"   ✅ TEST_KEY detected: {test_value}")
    else:
        print("   ❌ TEST_KEY not found - confirms loading issue")

if __name__ == "__main__":
    diagnose_env_issues()
