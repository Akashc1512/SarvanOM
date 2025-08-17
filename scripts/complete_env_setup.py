#!/usr/bin/env python3
"""
SarvanOM Environment Setup Completion Script
===========================================

This script helps complete the environment setup by adding missing variables
to the .env file with recommended defaults for free mode.

Usage: python scripts/complete_env_setup.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def load_env_file(file_path: Path) -> Dict[str, str]:
    """Load environment variables from a file."""
    env_vars = {}
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    return env_vars

def get_missing_variables() -> Dict[str, str]:
    """Get the missing environment variables with recommended defaults."""
    return {
        "NEXT_PUBLIC_API_URL": "http://localhost:8004",
        "ALLOWED_ORIGINS": "http://localhost:3000",
        "HF_HOME": "./models_cache",
        "OLLAMA_HOST": "http://localhost:11434",
        "PRIORITIZE_FREE_MODELS": "true"
    }

def backup_env_file(env_path: Path) -> Path:
    """Create a backup of the .env file."""
    backup_path = env_path.with_suffix('.env.backup')
    try:
        with open(env_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"{Colors.GREEN}✓ Backup created: {backup_path}{Colors.END}")
        return backup_path
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to create backup: {e}{Colors.END}")
        return None

def add_missing_variables(env_path: Path, missing_vars: Dict[str, str]) -> bool:
    """Add missing variables to the .env file."""
    try:
        # Read existing content
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add missing variables at the end
        additions = []
        for var, value in missing_vars.items():
            additions.append(f"\n# Added by complete_env_setup.py")
            additions.append(f"{var}={value}")
        
        # Write back with additions
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(additions))
        
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to add variables: {e}{Colors.END}")
        return False

def main() -> None:
    """Main function to complete environment setup."""
    print_header("SarvanOM Environment Setup Completion")
    
    env_path = Path(".env")
    if not env_path.exists():
        print(f"{Colors.RED}✗ .env file not found. Please create it first.{Colors.END}")
        return
    
    # Load current environment variables
    current_vars = load_env_file(env_path)
    missing_vars = get_missing_variables()
    
    # Filter out variables that already exist
    to_add = {}
    for var, value in missing_vars.items():
        if var not in current_vars:
            to_add[var] = value
    
    if not to_add:
        print(f"{Colors.GREEN}✓ All required environment variables are already set!{Colors.END}")
        return
    
    print(f"{Colors.BOLD}Missing environment variables to add:{Colors.END}")
    for var, value in to_add.items():
        print(f"  {Colors.BLUE}{var:<25}{Colors.END} = {Colors.GREEN}{value}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}This will add the missing variables to your .env file.{Colors.END}")
    response = input(f"{Colors.BOLD}Continue? (y/N): {Colors.END}").strip().lower()
    
    if response not in ['y', 'yes']:
        print(f"{Colors.YELLOW}Setup cancelled.{Colors.END}")
        return
    
    # Create backup
    backup_path = backup_env_file(env_path)
    if not backup_path:
        print(f"{Colors.RED}✗ Cannot proceed without backup.{Colors.END}")
        return
    
    # Add missing variables
    if add_missing_variables(env_path, to_add):
        print(f"{Colors.GREEN}✓ Successfully added {len(to_add)} variables to .env{Colors.END}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print(f"  1. {Colors.BLUE}Run: python scripts/dev_check.py{Colors.END}")
        print(f"  2. {Colors.BLUE}Start Docker Desktop (if not running){Colors.END}")
        print(f"  3. {Colors.BLUE}Run: make up{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Failed to add variables. Check the backup at {backup_path}{Colors.END}")

if __name__ == "__main__":
    main()
