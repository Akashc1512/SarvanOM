#!/usr/bin/env python3
"""
Docker Test Execution Script for SarvanOM
Orchestrates comprehensive testing of all LLM/DB/KG combinations
"""

import subprocess
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import requests
import docker
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerTestOrchestrator:
    """Orchestrates comprehensive Docker testing for SarvanOM"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.test_results_dir = Path("test_results")
        self.test_results_dir.mkdir(exist_ok=True)
        
    def check_docker_health(self) -> bool:
        """Check if Docker is running and accessible"""
        try:
            self.docker_client.ping()
            logger.info("✅ Docker is running and accessible")
            return True
        except Exception as e:
            logger.error(f"❌ Docker is not accessible: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env.docker file with test configuration"""
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
        try:
            with open('.env.docker', 'w') as f:
                f.write(env_content)
            logger.info("✅ Created .env.docker file")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create .env.docker: {e}")
            return False
    
    def start_infrastructure_services(self) -> bool:
        """Start infrastructure services (databases, etc.)"""
        logger.info("🚀 Starting infrastructure services...")
        
        try:
            # Start infrastructure services only
            cmd = [
                "docker", "compose", "-f", "docker-compose.test.yml", 
                "--env-file", ".env.docker", "up", "-d",
                "postgres", "redis", "arangodb", "qdrant", "meilisearch", "ollama", "minio"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Infrastructure services started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start infrastructure services: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout starting infrastructure services")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting infrastructure services: {e}")
            return False
    
    def wait_for_services_health(self, timeout: int = 300) -> bool:
        """Wait for all services to be healthy"""
        logger.info("⏳ Waiting for services to be healthy...")
        
        services = [
            ("postgres", "http://localhost:5432"),
            ("redis", "http://localhost:6379"),
            ("arangodb", "http://localhost:8529/_api/version"),
            ("qdrant", "http://localhost:6333/"),
            ("meilisearch", "http://localhost:7700/health"),
            ("ollama", "http://localhost:11434/api/tags"),
            ("minio", "http://localhost:9000/minio/health/live")
        ]
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service_name, health_url in services:
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code not in [200, 201]:
                        all_healthy = False
                        logger.info(f"⏳ {service_name} not ready yet...")
                        break
                except:
                    all_healthy = False
                    logger.info(f"⏳ {service_name} not ready yet...")
                    break
            
            if all_healthy:
                logger.info("✅ All infrastructure services are healthy")
                return True
            
            time.sleep(10)
        
        logger.error("❌ Timeout waiting for services to be healthy")
        return False
    
    def start_backend_service(self) -> bool:
        """Start the backend service"""
        logger.info("🚀 Starting backend service...")
        
        try:
            cmd = [
                "docker", "compose", "-f", "docker-compose.test.yml",
                "--env-file", ".env.docker", "up", "-d", "backend-test"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info("✅ Backend service started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start backend service: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout starting backend service")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting backend service: {e}")
            return False
    
    def wait_for_backend_health(self, timeout: int = 120) -> bool:
        """Wait for backend to be healthy"""
        logger.info("⏳ Waiting for backend to be healthy...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:8000/health", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Backend is healthy and ready")
                    return True
            except:
                pass
            
            logger.info("⏳ Backend not ready yet...")
            time.sleep(5)
        
        logger.error("❌ Timeout waiting for backend to be healthy")
        return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive tests using the test runner"""
        logger.info("🧪 Running comprehensive tests...")
        
        try:
            cmd = [
                "docker", "compose", "-f", "docker-compose.test.yml",
                "--env-file", ".env.docker", "run", "--rm", "test-runner"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 minutes timeout
            
            if result.returncode == 0:
                logger.info("✅ Comprehensive tests completed successfully")
                logger.info("Test output:")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ Comprehensive tests failed: {result.stderr}")
                logger.error("Test output:")
                print(result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout running comprehensive tests")
            return False
        except Exception as e:
            logger.error(f"❌ Error running comprehensive tests: {e}")
            return False
    
    def collect_test_results(self) -> Dict[str, Any]:
        """Collect and analyze test results"""
        logger.info("📊 Collecting test results...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_files": [],
            "summary": {}
        }
        
        # Find all test result files
        for result_file in self.test_results_dir.glob("test_*.json"):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    results["test_files"].append({
                        "file": str(result_file),
                        "type": "summary" if "summary" in str(result_file) else "detailed",
                        "data": data
                    })
            except Exception as e:
                logger.warning(f"⚠️ Could not read {result_file}: {e}")
        
        # Generate overall summary
        if results["test_files"]:
            summary_file = next((f for f in results["test_files"] if f["type"] == "summary"), None)
            if summary_file:
                results["summary"] = summary_file["data"]
        
        return results
    
    def cleanup_services(self):
        """Clean up all test services"""
        logger.info("🧹 Cleaning up test services...")
        
        try:
            cmd = ["docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            logger.info("✅ Test services cleaned up")
        except Exception as e:
            logger.warning(f"⚠️ Error during cleanup: {e}")
    
    def run_full_test_suite(self) -> bool:
        """Run the complete test suite"""
        logger.info("🚀 Starting SarvanOM Comprehensive Docker Test Suite")
        logger.info("=" * 80)
        
        try:
            # Step 1: Check Docker health
            if not self.check_docker_health():
                return False
            
            # Step 2: Create environment file
            if not self.create_env_file():
                return False
            
            # Step 3: Start infrastructure services
            if not self.start_infrastructure_services():
                return False
            
            # Step 4: Wait for services to be healthy
            if not self.wait_for_services_health():
                return False
            
            # Step 5: Start backend service
            if not self.start_backend_service():
                return False
            
            # Step 6: Wait for backend to be healthy
            if not self.wait_for_backend_health():
                return False
            
            # Step 7: Run comprehensive tests
            if not self.run_comprehensive_tests():
                return False
            
            # Step 8: Collect results
            results = self.collect_test_results()
            
            # Print final summary
            self.print_final_summary(results)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False
        finally:
            # Always cleanup
            self.cleanup_services()
    
    def print_final_summary(self, results: Dict[str, Any]):
        """Print final test summary"""
        print("\n" + "=" * 80)
        print("SARVANOM COMPREHENSIVE TEST SUITE - FINAL SUMMARY")
        print("=" * 80)
        
        if results["summary"]:
            summary = results["summary"]
            test_summary = summary.get("test_summary", {})
            
            print(f"📊 Total Tests: {test_summary.get('total_tests', 0)}")
            print(f"✅ Successful: {test_summary.get('successful_tests', 0)}")
            print(f"❌ Failed: {test_summary.get('failed_tests', 0)}")
            print(f"📈 Success Rate: {test_summary.get('success_rate', 0):.2f}%")
            print(f"⏱️ Total Time: {test_summary.get('total_execution_time_seconds', 0):.2f}s")
            print(f"⚡ Avg Response Time: {test_summary.get('average_response_time_ms', 0):.2f}ms")
            
            # Component breakdown
            print("\n📋 BY COMPONENT:")
            for component, stats in summary.get("by_component", {}).items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"  {component}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
            
            # Complexity breakdown
            print("\n🎯 BY COMPLEXITY:")
            for complexity, stats in summary.get("by_complexity", {}).items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"  {complexity}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n📁 Test results saved in: {self.test_results_dir}")
        print("=" * 80)

def main():
    """Main function"""
    orchestrator = DockerTestOrchestrator()
    
    success = orchestrator.run_full_test_suite()
    
    if success:
        print("\n🎉 COMPREHENSIVE TEST SUITE COMPLETED SUCCESSFULLY!")
        print("All LLM/DB/KG combinations have been tested and validated.")
        return 0
    else:
        print("\n⚠️ COMPREHENSIVE TEST SUITE FAILED!")
        print("Some components or combinations need attention.")
        return 1

if __name__ == "__main__":
    exit(main())
