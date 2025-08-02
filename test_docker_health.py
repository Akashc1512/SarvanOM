#!/usr/bin/env python3
"""
SarvanOM Docker Health Test Script
==================================

This script performs comprehensive health checks for all Docker services
in the SarvanOM platform, optimized for Windows 11 Docker Desktop.

Features:
- Health checks for all services (Backend, Frontend, Ollama, Meilisearch, ArangoDB, Qdrant, PostgreSQL, Redis)
- Environment variable validation from .env.docker
- Connectivity tests between services
- Performance metrics collection
- Detailed reporting with timestamps

Usage:
    python test_docker_health.py

Requirements:
    - requests
    - psycopg2-binary
    - redis
    - python-dotenv
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerHealthTester:
    """Comprehensive Docker health testing for SarvanOM platform."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'services': {},
            'environment': {},
            'connectivity': {},
            'performance': {}
        }
        self.env_vars = {}
        self.load_environment_variables()
    
    def load_environment_variables(self) -> None:
        """Load environment variables from .env.docker file."""
        try:
            if os.path.exists('.env.docker'):
                with open('.env.docker', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.env_vars[key] = value
                logger.info(f"Loaded {len(self.env_vars)} environment variables from .env.docker")
            else:
                logger.error(".env.docker file not found")
                self.results['environment']['error'] = ".env.docker file not found"
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            self.results['environment']['error'] = str(e)
    
    def check_docker_services(self) -> None:
        """Check if all Docker services are running."""
        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                services = json.loads(result.stdout)
                running_services = [s['Service'] for s in services if s['State'] == 'running']
                expected_services = [
                    'sarvanom_backend', 'frontend', 'ollama', 'meilisearch',
                    'arangodb', 'postgres', 'qdrant', 'redis'
                ]
                
                missing_services = set(expected_services) - set(running_services)
                if missing_services:
                    logger.warning(f"Missing services: {missing_services}")
                    self.results['services']['docker_status'] = {
                        'status': 'warning',
                        'message': f"Missing services: {missing_services}",
                        'running_services': running_services
                    }
                else:
                    logger.info("All Docker services are running")
                    self.results['services']['docker_status'] = {
                        'status': 'healthy',
                        'message': "All services running",
                        'running_services': running_services
                    }
            else:
                logger.error("Failed to check Docker services")
                self.results['services']['docker_status'] = {
                    'status': 'error',
                    'message': "Failed to check Docker services"
                }
        except Exception as e:
            logger.error(f"Error checking Docker services: {e}")
            self.results['services']['docker_status'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_backend_health(self) -> None:
        """Check backend health endpoint."""
        try:
            response = requests.get('http://localhost:8000/health/basic', timeout=10)
            if response.status_code == 200:
                logger.info("Backend health check passed")
                self.results['services']['backend'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"Backend health check failed: {response.status_code}")
                self.results['services']['backend'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Backend health check error: {e}")
            self.results['services']['backend'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_frontend_health(self) -> None:
        """Check frontend health."""
        try:
            response = requests.get('http://localhost:3000', timeout=10)
            if response.status_code == 200:
                logger.info("Frontend health check passed")
                self.results['services']['frontend'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"Frontend health check failed: {response.status_code}")
                self.results['services']['frontend'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Frontend health check error: {e}")
            self.results['services']['frontend'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_ollama_health(self) -> None:
        """Check Ollama LLM service health."""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=10)
            if response.status_code == 200:
                logger.info("Ollama health check passed")
                self.results['services']['ollama'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"Ollama health check failed: {response.status_code}")
                self.results['services']['ollama'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Ollama health check error: {e}")
            self.results['services']['ollama'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_meilisearch_health(self) -> None:
        """Check Meilisearch health."""
        try:
            response = requests.get('http://localhost:7700/version', timeout=10)
            if response.status_code == 200:
                logger.info("Meilisearch health check passed")
                self.results['services']['meilisearch'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"Meilisearch health check failed: {response.status_code}")
                self.results['services']['meilisearch'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Meilisearch health check error: {e}")
            self.results['services']['meilisearch'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_arangodb_health(self) -> None:
        """Check ArangoDB health."""
        try:
            response = requests.get('http://localhost:8529/_api/version', timeout=10)
            if response.status_code == 200:
                logger.info("ArangoDB health check passed")
                self.results['services']['arangodb'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"ArangoDB health check failed: {response.status_code}")
                self.results['services']['arangodb'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"ArangoDB health check error: {e}")
            self.results['services']['arangodb'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_qdrant_health(self) -> None:
        """Check Qdrant health."""
        try:
            response = requests.get('http://localhost:6333/health', timeout=10)
            if response.status_code == 200:
                logger.info("Qdrant health check passed")
                self.results['services']['qdrant'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"Qdrant health check failed: {response.status_code}")
                self.results['services']['qdrant'] = {
                    'status': 'unhealthy',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Qdrant health check error: {e}")
            self.results['services']['qdrant'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_postgres_health(self) -> None:
        """Check PostgreSQL health using Docker exec."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'sarvanom-postgres',
                'pg_isready', '-U', 'postgres', '-d', 'sarvanom_db'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("PostgreSQL health check passed")
                self.results['services']['postgres'] = {
                    'status': 'healthy',
                    'message': result.stdout.strip()
                }
            else:
                logger.warning(f"PostgreSQL health check failed: {result.stderr}")
                self.results['services']['postgres'] = {
                    'status': 'unhealthy',
                    'message': result.stderr.strip()
                }
        except Exception as e:
            logger.error(f"PostgreSQL health check error: {e}")
            self.results['services']['postgres'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_redis_health(self) -> None:
        """Check Redis health using Docker exec."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'sarvanom-redis',
                'redis-cli', 'ping'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip() == 'PONG':
                logger.info("Redis health check passed")
                self.results['services']['redis'] = {
                    'status': 'healthy',
                    'message': result.stdout.strip()
                }
            else:
                logger.warning(f"Redis health check failed: {result.stderr}")
                self.results['services']['redis'] = {
                    'status': 'unhealthy',
                    'message': result.stderr.strip()
                }
        except Exception as e:
            logger.error(f"Redis health check error: {e}")
            self.results['services']['redis'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def validate_environment_variables(self) -> None:
        """Validate critical environment variables."""
        required_vars = [
            'DATABASE_URL', 'REDIS_URL', 'QDRANT_URL', 'ARANGODB_URL',
            'MEILISEARCH_URL', 'OLLAMA_BASE_URL', 'SECRET_KEY', 'JWT_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in self.env_vars or not self.env_vars[var]:
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            self.results['environment']['validation'] = {
                'status': 'warning',
                'missing_variables': missing_vars,
                'total_variables': len(self.env_vars)
            }
        else:
            logger.info("All required environment variables are present")
            self.results['environment']['validation'] = {
                'status': 'healthy',
                'total_variables': len(self.env_vars)
            }
    
    def check_service_connectivity(self) -> None:
        """Check connectivity between services."""
        connectivity_tests = [
            ('Backend to PostgreSQL', 'http://localhost:8000/health/db'),
            ('Backend to Redis', 'http://localhost:8000/health/cache'),
            ('Backend to Meilisearch', 'http://localhost:8000/health/search'),
            ('Backend to ArangoDB', 'http://localhost:8000/health/kg'),
            ('Backend to Qdrant', 'http://localhost:8000/health/vector'),
            ('Backend to Ollama', 'http://localhost:8000/health/llm'),
        ]
        
        for test_name, url in connectivity_tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"{test_name} connectivity: OK")
                    self.results['connectivity'][test_name] = {
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds()
                    }
                else:
                    logger.warning(f"{test_name} connectivity: Failed ({response.status_code})")
                    self.results['connectivity'][test_name] = {
                        'status': 'unhealthy',
                        'status_code': response.status_code
                    }
            except Exception as e:
                logger.error(f"{test_name} connectivity error: {e}")
                self.results['connectivity'][test_name] = {
                    'status': 'error',
                    'message': str(e)
                }
    
    def collect_performance_metrics(self) -> None:
        """Collect basic performance metrics."""
        try:
            # Docker stats
            result = subprocess.run([
                'docker', 'stats', '--no-stream', '--format', 'json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                stats = json.loads(result.stdout)
                self.results['performance']['docker_stats'] = stats
                logger.info("Performance metrics collected")
            else:
                logger.warning("Failed to collect Docker stats")
                self.results['performance']['docker_stats'] = None
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            self.results['performance']['docker_stats'] = None
    
    def determine_overall_status(self) -> None:
        """Determine overall health status."""
        all_services = self.results['services']
        healthy_count = 0
        total_count = 0
        
        for service_name, service_data in all_services.items():
            if isinstance(service_data, dict) and 'status' in service_data:
                total_count += 1
                if service_data['status'] == 'healthy':
                    healthy_count += 1
        
        if total_count == 0:
            self.results['overall_status'] = 'unknown'
        elif healthy_count == total_count:
            self.results['overall_status'] = 'healthy'
        elif healthy_count > total_count / 2:
            self.results['overall_status'] = 'warning'
        else:
            self.results['overall_status'] = 'unhealthy'
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all health tests."""
        logger.info("Starting comprehensive Docker health tests...")
        
        # Check Docker services
        self.check_docker_services()
        
        # Check individual service health
        self.check_backend_health()
        self.check_frontend_health()
        self.check_ollama_health()
        self.check_meilisearch_health()
        self.check_arangodb_health()
        self.check_qdrant_health()
        self.check_postgres_health()
        self.check_redis_health()
        
        # Validate environment variables
        self.validate_environment_variables()
        
        # Check service connectivity
        self.check_service_connectivity()
        
        # Collect performance metrics
        self.collect_performance_metrics()
        
        # Determine overall status
        self.determine_overall_status()
        
        logger.info("All health tests completed")
        return self.results
    
    def print_results(self) -> None:
        """Print formatted results."""
        print("\n" + "="*60)
        print("SARVANOM DOCKER HEALTH TEST RESULTS")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print("\n" + "-"*60)
        
        # Service Status
        print("SERVICE STATUS:")
        print("-"*30)
        for service_name, service_data in self.results['services'].items():
            if isinstance(service_data, dict) and 'status' in service_data:
                status = service_data['status'].upper()
                print(f"{service_name:20} : {status}")
                if 'response_time' in service_data:
                    print(f"{'':20}   Response: {service_data['response_time']:.3f}s")
        
        # Environment Validation
        print("\nENVIRONMENT VALIDATION:")
        print("-"*30)
        env_data = self.results['environment'].get('validation', {})
        if 'status' in env_data:
            print(f"Status: {env_data['status'].upper()}")
            if 'missing_variables' in env_data:
                print(f"Missing Variables: {env_data['missing_variables']}")
            print(f"Total Variables: {env_data.get('total_variables', 0)}")
        
        # Connectivity
        print("\nSERVICE CONNECTIVITY:")
        print("-"*30)
        for test_name, test_data in self.results['connectivity'].items():
            if isinstance(test_data, dict) and 'status' in test_data:
                status = test_data['status'].upper()
                print(f"{test_name:30} : {status}")
                if 'response_time' in test_data:
                    print(f"{'':30}   Response: {test_data['response_time']:.3f}s")
        
        print("\n" + "="*60)
        
        # Summary
        if self.results['overall_status'] == 'healthy':
            print("✅ All services are healthy!")
        elif self.results['overall_status'] == 'warning':
            print("⚠️  Some services have issues - check logs")
        else:
            print("❌ Multiple services are unhealthy - immediate attention required")
        
        print("="*60)
    
    def save_results(self, filename: str = None) -> None:
        """Save results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"docker_health_test_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")


def main():
    """Main function to run health tests."""
    try:
        tester = DockerHealthTester()
        results = tester.run_all_tests()
        tester.print_results()
        tester.save_results()
        
        # Exit with appropriate code
        if results['overall_status'] == 'healthy':
            sys.exit(0)
        elif results['overall_status'] == 'warning':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        logger.info("Health test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 