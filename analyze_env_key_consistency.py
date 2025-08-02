#!/usr/bin/env python3
"""
Analyze consistency between environment variables used in code and those defined in .env file.
"""

import os
import re
from typing import Dict, List, Set, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_env_keys_from_code() -> Set[str]:
    """Extract all environment variable keys used in the codebase."""
    env_keys = set()
    
    # Common patterns for os.getenv calls
    patterns = [
        r'os\.getenv\(["\']([^"\']+)["\']',
        r'os\.getenv\(["\']([^"\']+)["\'],\s*[^)]+\)',
        r'os\.environ\[["\']([^"\']+)["\']\]',
        r'os\.environ\.get\(["\']([^"\']+)["\']',
    ]
    
    # Search in Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', 'venv', 'env']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                env_keys.add(match)
                                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return env_keys

def extract_env_keys_from_env_file() -> Set[str]:
    """Extract all environment variable keys from .env file."""
    env_keys = set()
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#') and '=' in line:
                    key = line.split('=')[0].strip()
                    env_keys.add(key)
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    return env_keys

def analyze_consistency():
    """Analyze consistency between code and .env file."""
    print("🔍 Analyzing Environment Variable Consistency")
    print("=" * 60)
    
    # Extract keys from code
    print("📦 Extracting environment variables from code...")
    code_keys = extract_env_keys_from_code()
    print(f"Found {len(code_keys)} unique environment variables in code")
    
    # Extract keys from .env file
    print("📄 Extracting environment variables from .env file...")
    env_keys = extract_env_keys_from_env_file()
    print(f"Found {len(env_keys)} unique environment variables in .env file")
    
    # Analyze consistency
    print("\n📊 Consistency Analysis")
    print("=" * 40)
    
    # Keys in code but not in .env
    missing_in_env = code_keys - env_keys
    print(f"\n❌ Missing in .env file ({len(missing_in_env)}):")
    for key in sorted(missing_in_env):
        print(f"   - {key}")
    
    # Keys in .env but not in code
    unused_in_env = env_keys - code_keys
    print(f"\n⚠️ Unused in code ({len(unused_in_env)}):")
    for key in sorted(unused_in_env):
        print(f"   - {key}")
    
    # Keys in both
    common_keys = code_keys & env_keys
    print(f"\n✅ Common keys ({len(common_keys)}):")
    for key in sorted(common_keys):
        print(f"   - {key}")
    
    # Calculate statistics
    total_keys = len(code_keys | env_keys)
    consistency_rate = len(common_keys) / total_keys * 100 if total_keys > 0 else 0
    
    print(f"\n📈 Statistics:")
    print(f"   Total unique keys: {total_keys}")
    print(f"   Common keys: {len(common_keys)}")
    print(f"   Missing in .env: {len(missing_in_env)}")
    print(f"   Unused in .env: {len(unused_in_env)}")
    print(f"   Consistency rate: {consistency_rate:.1f}%")
    
    return {
        'code_keys': code_keys,
        'env_keys': env_keys,
        'missing_in_env': missing_in_env,
        'unused_in_env': unused_in_env,
        'common_keys': common_keys,
        'consistency_rate': consistency_rate
    }

def check_key_values():
    """Check if keys in .env file have proper values."""
    print("\n🔧 Checking .env Key Values")
    print("=" * 40)
    
    issues = []
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Check for empty values
                    if not value:
                        issues.append(f"Line {line_num}: {key} has empty value")
                    elif value == "your_*_here":
                        issues.append(f"Line {line_num}: {key} has placeholder value")
                    elif value.startswith("your_") and value.endswith("_here"):
                        issues.append(f"Line {line_num}: {key} has placeholder value")
    
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return
    
    if issues:
        print("⚠️ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ All keys have proper values")

def generate_recommendations(analysis):
    """Generate recommendations based on analysis."""
    print("\n💡 Recommendations")
    print("=" * 30)
    
    if analysis['missing_in_env']:
        print("\n🔧 Add these keys to .env file:")
        for key in sorted(analysis['missing_in_env']):
            print(f"   {key}=your_value_here")
    
    if analysis['unused_in_env']:
        print("\n🧹 Consider removing unused keys from .env:")
        for key in sorted(analysis['unused_in_env']):
            print(f"   # {key} (unused)")
    
    if analysis['consistency_rate'] < 90:
        print(f"\n⚠️ Low consistency rate ({analysis['consistency_rate']:.1f}%). Consider:")
        print("   - Adding missing keys to .env file")
        print("   - Removing unused keys from .env file")
        print("   - Updating code to use consistent key names")
    else:
        print(f"\n✅ Good consistency rate ({analysis['consistency_rate']:.1f}%)")

def main():
    """Run the complete analysis."""
    print("🚀 Environment Variable Consistency Analysis")
    print("=" * 60)
    
    # Run analysis
    analysis = analyze_consistency()
    
    # Check key values
    check_key_values()
    
    # Generate recommendations
    generate_recommendations(analysis)
    
    print("\n🎉 Analysis completed!")

if __name__ == "__main__":
    main() 