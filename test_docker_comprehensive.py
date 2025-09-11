#!/usr/bin/env python3
"""
Simple Docker Test Execution Script
Quick way to run comprehensive SarvanOM testing
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 SarvanOM Comprehensive Docker Testing")
    print("=" * 50)
    
    # Check if Docker is running
    if not run_command("docker --version", "Checking Docker"):
        print("❌ Docker is not available. Please install and start Docker.")
        return 1
    
    # Create .env.docker if it doesn't exist
    env_file = Path(".env.docker")
    if not env_file.exists():
        print("📝 Creating .env.docker file...")
        env_content = """# SarvanOM Docker Test Environment
POSTGRES_DB=sarvanom_test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sarvanom_test_password_2025
REDIS_PASSWORD=sarvanom_redis_test_2025
ARANGODB_PASSWORD=sarvanom_arangodb_test_2025
MEILI_MASTER_KEY=sarvanom_meili_test_master_key_2025_very_secure
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
ENVIRONMENT=testing
LOG_LEVEL=DEBUG
"""
        with open('.env.docker', 'w') as f:
            f.write(env_content)
        print("✅ Created .env.docker file")
    
    # Create test directories
    Path("test_results").mkdir(exist_ok=True)
    Path("test_data").mkdir(exist_ok=True)
    
    # Run the comprehensive test suite
    print("\n🧪 Starting comprehensive test suite...")
    
    # Use the Python script for comprehensive testing
    test_script = Path("scripts/run_docker_tests.py")
    if test_script.exists():
        cmd = f"python {test_script}"
    else:
        # Fallback to direct docker compose commands
        print("📋 Running tests with docker compose...")
        
        # Start infrastructure
        if not run_command(
            "docker compose -f docker-compose.test.yml --env-file .env.docker up -d postgres redis arangodb qdrant meilisearch ollama minio",
            "Starting infrastructure services"
        ):
            return 1
        
        # Wait for services
        print("⏳ Waiting for services to be ready...")
        time.sleep(30)
        
        # Start backend
        if not run_command(
            "docker compose -f docker-compose.test.yml --env-file .env.docker up -d backend-test",
            "Starting backend service"
        ):
            return 1
        
        # Wait for backend
        print("⏳ Waiting for backend to be ready...")
        time.sleep(30)
        
        # Run tests
        if not run_command(
            "docker compose -f docker-compose.test.yml --env-file .env.docker run --rm test-runner",
            "Running comprehensive tests"
        ):
            return 1
        
        # Cleanup
        run_command(
            "docker compose -f docker-compose.test.yml down -v",
            "Cleaning up services"
        )
    
    print("\n🎉 Comprehensive testing completed!")
    print("📁 Check test_results/ directory for detailed results")
    
    return 0

if __name__ == "__main__":
    exit(main())
