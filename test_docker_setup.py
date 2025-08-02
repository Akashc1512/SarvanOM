#!/usr/bin/env python3
"""
SarvanOM Docker Setup Test Script

This script validates the Docker setup configuration files
without requiring Docker to be running.
"""

import os
import sys
import yaml
import json
from pathlib import Path

def test_docker_compose():
    """Test docker-compose.yml configuration"""
    print("🔍 Testing docker-compose.yml...")
    
    try:
        with open('docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required services
        required_services = [
            'sarvanom_backend', 'ollama', 'meilisearch', 
            'arangodb', 'postgres', 'qdrant', 'redis'
        ]
        
        found_services = list(config.get('services', {}).keys())
        missing_services = [s for s in required_services if s not in found_services]
        
        if missing_services:
            print(f"❌ Missing services: {missing_services}")
            return False
        
        print(f"✅ Found {len(found_services)} services: {found_services}")
        
        # Check resource limits
        for service_name, service_config in config['services'].items():
            if 'deploy' in service_config and 'resources' in service_config['deploy']:
                resources = service_config['deploy']['resources']
                if 'limits' in resources:
                    limits = resources['limits']
                    print(f"  📊 {service_name}: {limits.get('memory', 'N/A')} RAM, {limits.get('cpus', 'N/A')} CPU")
        
        # Check health checks
        health_check_count = 0
        for service_config in config['services'].values():
            if 'healthcheck' in service_config:
                health_check_count += 1
        
        print(f"✅ {health_check_count} services have health checks configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False

def test_env_template():
    """Test environment template file"""
    print("\n🔍 Testing env.docker.template...")
    
    try:
        with open('env.docker.template', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required environment variables
        required_vars = [
            'DATABASE_URL', 'REDIS_URL', 'MEILISEARCH_URL',
            'ARANGODB_URL', 'QDRANT_URL', 'OLLAMA_BASE_URL',
            'SECRET_KEY', 'JWT_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        print(f"✅ Found all required environment variables")
        
        # Count total variables
        var_count = content.count('=')
        print(f"📊 Total environment variables: {var_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading env.docker.template: {e}")
        return False

def test_requirements():
    """Test requirements.txt file"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential dependencies
        essential_deps = [
            'fastapi', 'uvicorn', 'aiohttp', 'redis', 
            'asyncpg', 'pydantic', 'python-dotenv'
        ]
        
        missing_deps = []
        for dep in essential_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing dependencies: {missing_deps}")
            return False
        
        print(f"✅ Found all essential dependencies")
        
        # Count total dependencies
        dep_count = len([line for line in content.split('\n') 
                        if line.strip() and not line.startswith('#')])
        print(f"📊 Total dependencies: {dep_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_health_script():
    """Test health check script"""
    print("\n🔍 Testing test_docker_health.py...")
    
    try:
        with open('test_docker_health.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            'aiohttp', 'asyncpg', 'redis', 'asyncio'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if f'import {imp}' not in content and f'from {imp}' not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        
        print(f"✅ Health check script has all required imports")
        
        # Check for service configurations
        if 'self.services = {' in content:
            print("✅ Service configurations found")
        else:
            print("❌ Service configurations missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading test_docker_health.py: {e}")
        return False

def test_makefile():
    """Test Makefile commands"""
    print("\n🔍 Testing Makefile...")
    
    try:
        with open('Makefile', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required commands
        required_commands = [
            'up:', 'down:', 'docker-health:', 'restart:'
        ]
        
        missing_commands = []
        for cmd in required_commands:
            if cmd not in content:
                missing_commands.append(cmd)
        
        if missing_commands:
            print(f"❌ Missing Makefile commands: {missing_commands}")
            return False
        
        print(f"✅ Found all required Makefile commands")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Makefile: {e}")
        return False

def test_file_structure():
    """Test overall file structure"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'docker-compose.yml',
        'env.docker.template',
        'requirements.txt',
        'test_docker_health.py',
        'Makefile',
        'Dockerfile.enterprise'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print(f"✅ All required files present")
    
    # Check file sizes
    for file in required_files:
        size = os.path.getsize(file)
        print(f"  📄 {file}: {size:,} bytes")
    
    return True

def main():
    """Run all tests"""
    print("🚀 SarvanOM Docker Setup Validation")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_docker_compose,
        test_env_template,
        test_requirements,
        test_health_script,
        test_makefile
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Docker setup is ready.")
        print("\n📋 Next steps:")
        print("1. Copy env.docker.template to .env.docker")
        print("2. Run 'make up' to start the stack")
        print("3. Run 'make docker-health' to check services")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 