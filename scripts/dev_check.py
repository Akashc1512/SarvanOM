#!/usr/bin/env python3
"""
Development Environment Check Script
MAANG/OpenAI/Perplexity Standards Implementation
August 16, 2025

This script verifies the development environment requirements:
- Python ≥3.11
- Node ≥18
- Docker presence
- Environment file configurations
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_section(text: str):
    """Print a formatted section header"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}📋 {text}{Colors.ENDC}")
    print("-" * 50)

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is ≥3.11"""
    version = sys.version_info
    current_version = f"{version.major}.{version.minor}.{version.micro}"
    required_version = "3.11"
    
    if version >= (3, 11):
        return True, current_version
    else:
        return False, current_version

def check_node_version() -> Tuple[bool, str]:
    """Check if Node.js version is ≥18"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_str = result.stdout.strip().lstrip('v')
            version_parts = version_str.split('.')
            major_version = int(version_parts[0])
        
            if major_version >= 18:
                return True, version_str
            else:
                return False, version_str
        else:
            return False, "Not found"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False, "Not found"

def check_docker() -> Tuple[bool, str]:
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip()
            # Extract version from "Docker version 20.10.0, build 7287ab3"
            if 'version' in version_line:
                version = version_line.split('version')[1].split(',')[0].strip()
                return True, version
        else:
                return True, "Available"
    else:
            return False, "Not found"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False, "Not found"

def load_env_file(file_path: Path) -> Dict[str, str]:
    """Load environment variables from a file"""
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
            print_warning(f"Error reading {file_path}: {e}")
    return env_vars

def check_env_files() -> Dict[str, Dict[str, str]]:
    """Check all environment files for required keys"""
    env_files = {
        '.env': Path('.env'),
        '.env.docker': Path('.env.docker'),
        'frontend/.env.local': Path('frontend/.env.local')
    }
    
    env_data = {}
    for name, path in env_files.items():
        env_data[name] = load_env_file(path)
    
    return env_data

def get_required_keys() -> Dict[str, Dict[str, str]]:
    """Define required environment keys and their descriptions"""
    return {
        'NEXT_PUBLIC_API_URL': {
            'description': 'Frontend API URL',
            'required': True,
            'default': 'http://localhost:8000'
        },
        'ALLOWED_ORIGINS': {
            'description': 'CORS allowed origins',
            'required': True,
            'default': 'http://localhost:3000,http://localhost:8000'
        },
        'OPENAI_API_KEY': {
            'description': 'OpenAI API key',
            'required': False,
            'default': 'disabled'
        },
        'ANTHROPIC_API_KEY': {
            'description': 'Anthropic API key',
            'required': False,
            'default': 'disabled'
        },
        'HF_HOME': {
            'description': 'HuggingFace cache directory',
            'required': False,
            'default': './models_cache'
        },
        'OLLAMA_HOST': {
            'description': 'Ollama service host',
            'required': False,
            'default': 'http://localhost:11434'
        },
        'USE_VECTOR_DB': {
            'description': 'Enable vector database',
            'required': False,
            'default': 'false'
        },
        'PRIORITIZE_FREE_MODELS': {
            'description': 'Prioritize free models',
            'required': False,
            'default': 'true'
        }
    }

def analyze_env_keys(env_data: Dict[str, Dict[str, str]], required_keys: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """Analyze which keys are present/missing in each env file"""
    analysis = {}
    
    for env_file, env_vars in env_data.items():
        analysis[env_file] = {}
        for key, config in required_keys.items():
            if key in env_vars:
                analysis[env_file][key] = {
                    'status': 'present',
                    'value': '***' if 'KEY' in key or 'SECRET' in key else env_vars[key]
                }
                else:
                analysis[env_file][key] = {
                    'status': 'missing',
                    'value': config['default']
                }
    
    return analysis

def print_analysis_table(analysis: Dict[str, Dict[str, str]], required_keys: Dict[str, Dict[str, str]]):
    """Print a formatted table of environment key analysis"""
    print(f"\n{Colors.BOLD}Environment Configuration Analysis:{Colors.ENDC}")
    print("=" * 100)
    
    # Header
    header = f"{'Key':<25} {'Status':<10} {'Value':<20} {'File':<15}"
    print(f"{Colors.UNDERLINE}{header}{Colors.ENDC}")
    
    for key, config in required_keys.items():
        for env_file, file_analysis in analysis.items():
            if key in file_analysis:
                status = file_analysis[key]['status']
                value = file_analysis[key]['value']
                
                # Color coding
                if status == 'present':
                    status_color = Colors.OKGREEN
                    status_icon = "✅"
                else:
                    status_color = Colors.WARNING
                    status_icon = "⚠️"
                
                # Truncate long values
                display_value = value[:17] + "..." if len(value) > 20 else value
                
                print(f"{key:<25} {status_color}{status_icon} {status:<8}{Colors.ENDC} {display_value:<20} {env_file:<15}")

def print_recommendations(analysis: Dict[str, Dict[str, str]], required_keys: Dict[str, Dict[str, str]]):
    """Print recommendations based on analysis"""
    print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
    print("=" * 50)
    
    # Check for critical missing keys
    critical_missing = []
    for key, config in required_keys.items():
        if config['required']:
            found = False
            for env_file, file_analysis in analysis.items():
                if key in file_analysis and file_analysis[key]['status'] == 'present':
                    found = True
                    break
            if not found:
                critical_missing.append(key)
    
    if critical_missing:
        print_error(f"Critical missing keys: {', '.join(critical_missing)}")
        print_info("These keys are required for basic functionality")
    else:
        print_success("All critical keys are present")
    
    # Check for free mode configuration
    free_mode_enabled = False
    for env_file, file_analysis in analysis.items():
        if 'PRIORITIZE_FREE_MODELS' in file_analysis:
            if file_analysis['PRIORITIZE_FREE_MODELS']['status'] == 'present':
                value = file_analysis['PRIORITIZE_FREE_MODELS']['value']
                if value.lower() in ['true', '1', 'yes']:
                    free_mode_enabled = True
                    break
    
    if free_mode_enabled:
        print_success("Free mode is enabled (recommended for development)")
        else:
        print_warning("Free mode is not enabled - consider setting PRIORITIZE_FREE_MODELS=true")
    
    # Check for vector DB configuration
    vector_db_enabled = False
    for env_file, file_analysis in analysis.items():
        if 'USE_VECTOR_DB' in file_analysis:
            if file_analysis['USE_VECTOR_DB']['status'] == 'present':
                value = file_analysis['USE_VECTOR_DB']['value']
                if value.lower() in ['true', '1', 'yes']:
                    vector_db_enabled = True
                    break
    
    if vector_db_enabled:
        print_info("Vector database is enabled")
    else:
        print_info("Vector database is disabled (recommended for development)")

def main():
    """Main function to run all checks"""
    print_header("SarvanOM Development Environment Check")
    
    # Check system requirements
    print_section("System Requirements")
    
    # Python version check
    python_ok, python_version = check_python_version()
    if python_ok:
        print_success(f"Python {python_version} (≥3.11 required)")
    else:
        print_error(f"Python {python_version} (≥3.11 required)")
    
    # Node.js version check
    node_ok, node_version = check_node_version()
    if node_ok:
        print_success(f"Node.js {node_version} (≥18 required)")
    else:
        print_error(f"Node.js {node_version} (≥18 required)")
    
    # Docker check
    docker_ok, docker_version = check_docker()
    if docker_ok:
        print_success(f"Docker {docker_version}")
    else:
        print_error("Docker not found")
    
    # Environment files check
    print_section("Environment Files")
    
    env_data = check_env_files()
    required_keys = get_required_keys()
    
    # Check which env files exist
    for env_file, path in [('.env', Path('.env')), 
                          ('.env.docker', Path('.env.docker')), 
                          ('frontend/.env.local', Path('frontend/.env.local'))]:
        if path.exists():
            print_success(f"{env_file} exists")
        else:
            print_warning(f"{env_file} not found")
    
    # Analyze environment keys
    analysis = analyze_env_keys(env_data, required_keys)
    
    # Print analysis table
    print_analysis_table(analysis, required_keys)
    
    # Print recommendations
    print_recommendations(analysis, required_keys)
    
    # Summary
    print_section("Summary")
    
    all_ok = python_ok and node_ok and docker_ok
    
    if all_ok:
        print_success("All system requirements met!")
    else:
        print_error("Some system requirements are missing")
    
    # Check if critical env keys are present
    critical_keys_present = True
    for key, config in required_keys.items():
        if config['required']:
            found = False
            for env_file, file_analysis in analysis.items():
                if key in file_analysis and file_analysis[key]['status'] == 'present':
                    found = True
                    break
            if not found:
                critical_keys_present = False
                break
    
    if critical_keys_present:
        print_success("All critical environment keys are present!")
    else:
        print_warning("Some critical environment keys are missing")
    
    # Exit code
    if all_ok and critical_keys_present:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Development environment is ready!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Development environment needs attention{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
