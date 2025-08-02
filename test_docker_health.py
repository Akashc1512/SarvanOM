#!/usr/bin/env python3
"""
SarvanOM Docker Health Check Script

This script tests the health of all services in the SarvanOM Docker stack:
- Backend API (FastAPI)
- Ollama (Local LLM)
- Meilisearch (Search Engine)
- ArangoDB (Knowledge Graph)
- PostgreSQL (Primary Database)
- Qdrant (Vector Database)
- Redis (Caching)

Usage:
    python test_docker_health.py

Environment Variables:
    Loads from .env.docker file if available
"""

import asyncio
import aiohttp
import asyncpg
import redis
import json
import sys
import os
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.docker')
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealth:
    """Health status for a service"""
    name: str
    status: str
    response_time: float
    details: Optional[str] = None
    error: Optional[str] = None

class DockerHealthChecker:
    """Comprehensive health checker for SarvanOM Docker stack"""
    
    def __init__(self):
        self.results: List[ServiceHealth] = []
        self.start_time = time.time()
        
        # Service configurations
        self.services = {
            'backend': {
                'url': 'http://localhost:8000/health/basic',
                'name': 'SarvanOM Backend',
                'timeout': 10
            },
            'ollama': {
                'url': 'http://localhost:11434/api/tags',
                'name': 'Ollama LLM',
                'timeout': 15
            },
            'meilisearch': {
                'url': 'http://localhost:7700/version',
                'name': 'Meilisearch',
                'timeout': 10
            },
            'arangodb': {
                'url': 'http://localhost:8529/_api/version',
                'name': 'ArangoDB',
                'timeout': 10
            },
            'qdrant': {
                'url': 'http://localhost:6333/health',
                'name': 'Qdrant Vector DB',
                'timeout': 10
            }
        }
        
        # Database configurations
        self.databases = {
            'postgres': {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': 'password',
                'database': 'sarvanom_db',
                'name': 'PostgreSQL'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'name': 'Redis'
            }
        }

    async def check_http_service(self, service_key: str, config: Dict) -> ServiceHealth:
        """Check HTTP service health"""
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=config['timeout'])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(config['url']) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return ServiceHealth(
                            name=config['name'],
                            status='healthy',
                            response_time=response_time,
                            details=f"Status: {response.status}"
                        )
                    else:
                        return ServiceHealth(
                            name=config['name'],
                            status='unhealthy',
                            response_time=response_time,
                            error=f"HTTP {response.status}"
                        )
                        
        except asyncio.TimeoutError:
            return ServiceHealth(
                name=config['name'],
                status='timeout',
                response_time=config['timeout'],
                error="Request timed out"
            )
        except Exception as e:
            return ServiceHealth(
                name=config['name'],
                status='error',
                response_time=time.time() - start_time,
                error=str(e)
            )

    async def check_postgres(self) -> ServiceHealth:
        """Check PostgreSQL database health"""
        start_time = time.time()
        config = self.databases['postgres']
        
        try:
            conn = await asyncpg.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            
            # Test basic query
            result = await conn.fetchval('SELECT 1')
            await conn.close()
            
            response_time = time.time() - start_time
            
            if result == 1:
                return ServiceHealth(
                    name=config['name'],
                    status='healthy',
                    response_time=response_time,
                    details="Connection successful"
                )
            else:
                return ServiceHealth(
                    name=config['name'],
                    status='unhealthy',
                    response_time=response_time,
                    error="Query test failed"
                )
                
        except Exception as e:
            return ServiceHealth(
                name=config['name'],
                status='error',
                response_time=time.time() - start_time,
                error=str(e)
            )

    async def check_redis(self) -> ServiceHealth:
        """Check Redis database health"""
        start_time = time.time()
        config = self.databases['redis']
        
        try:
            r = redis.Redis(
                host=config['host'],
                port=config['port'],
                db=config['db'],
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test ping
            result = r.ping()
            response_time = time.time() - start_time
            
            if result:
                return ServiceHealth(
                    name=config['name'],
                    status='healthy',
                    response_time=response_time,
                    details="Ping successful"
                )
            else:
                return ServiceHealth(
                    name=config['name'],
                    status='unhealthy',
                    response_time=response_time,
                    error="Ping failed"
                )
                
        except Exception as e:
            return ServiceHealth(
                name=config['name'],
                status='error',
                response_time=time.time() - start_time,
                error=str(e)
            )

    async def run_all_checks(self) -> List[ServiceHealth]:
        """Run all health checks concurrently"""
        tasks = []
        
        # HTTP service checks
        for service_key, config in self.services.items():
            tasks.append(self.check_http_service(service_key, config))
        
        # Database checks
        tasks.append(self.check_postgres())
        tasks.append(self.check_redis())
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, ServiceHealth):
                self.results.append(result)
            else:
                logger.error(f"Check failed with exception: {result}")
        
        return self.results

    def print_results(self):
        """Print formatted health check results"""
        print("\n" + "="*80)
        print("🚀 SARVANOM DOCKER HEALTH CHECK REPORT")
        print("="*80)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total Duration: {time.time() - self.start_time:.2f}s")
        print()
        
        # Group results by status
        healthy_services = []
        unhealthy_services = []
        error_services = []
        
        for result in self.results:
            if result.status == 'healthy':
                healthy_services.append(result)
            elif result.status == 'unhealthy':
                unhealthy_services.append(result)
            else:
                error_services.append(result)
        
        # Print healthy services
        if healthy_services:
            print("✅ HEALTHY SERVICES:")
            print("-" * 40)
            for service in healthy_services:
                print(f"  • {service.name:<20} ({service.response_time:.2f}s)")
                if service.details:
                    print(f"    └─ {service.details}")
            print()
        
        # Print unhealthy services
        if unhealthy_services:
            print("⚠️  UNHEALTHY SERVICES:")
            print("-" * 40)
            for service in unhealthy_services:
                print(f"  • {service.name:<20} ({service.response_time:.2f}s)")
                if service.error:
                    print(f"    └─ Error: {service.error}")
            print()
        
        # Print error services
        if error_services:
            print("❌ ERROR SERVICES:")
            print("-" * 40)
            for service in error_services:
                print(f"  • {service.name:<20} ({service.response_time:.2f}s)")
                if service.error:
                    print(f"    └─ Error: {service.error}")
            print()
        
        # Summary
        total_services = len(self.results)
        healthy_count = len(healthy_services)
        unhealthy_count = len(unhealthy_services)
        error_count = len(error_services)
        
        print("📊 SUMMARY:")
        print("-" * 40)
        print(f"  Total Services: {total_services}")
        print(f"  Healthy:        {healthy_count}")
        print(f"  Unhealthy:      {unhealthy_count}")
        print(f"  Errors:         {error_count}")
        print(f"  Success Rate:   {(healthy_count/total_services)*100:.1f}%")
        print()
        
        # Overall status
        if error_count == 0 and unhealthy_count == 0:
            print("🎉 ALL SERVICES ARE HEALTHY!")
            print("   SarvanOM Docker stack is ready for use.")
            return True
        elif error_count == 0:
            print("⚠️  SOME SERVICES ARE UNHEALTHY")
            print("   Check the details above and restart if needed.")
            return False
        else:
            print("❌ CRITICAL ERRORS DETECTED")
            print("   Some services failed to start. Check Docker logs.")
            return False

    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"docker_health_check_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': time.time() - self.start_time,
            'services': [
                {
                    'name': result.name,
                    'status': result.status,
                    'response_time': result.response_time,
                    'details': result.details,
                    'error': result.error
                }
                for result in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")

async def main():
    """Main function"""
    print("🔍 Starting SarvanOM Docker Health Check...")
    print("   This will test all services in the Docker stack.")
    print()
    
    # Check if Docker is running
    try:
        import subprocess
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running or not accessible")
            print("   Please start Docker Desktop and try again.")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ Docker command not found")
        print("   Please install Docker and try again.")
        sys.exit(1)
    
    # Check if containers are running
    try:
        result = subprocess.run(
            ['docker-compose', 'ps', '--services'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("❌ Docker Compose not found or no services running")
            print("   Please run 'make up' to start the services.")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ Docker Compose not found")
        print("   Please install Docker Compose and try again.")
        sys.exit(1)
    
    # Run health checks
    checker = DockerHealthChecker()
    await checker.run_all_checks()
    
    # Print and save results
    success = checker.print_results()
    checker.save_results()
    
    # Exit with appropriate code
    if success:
        print("✅ Health check completed successfully!")
        sys.exit(0)
    else:
        print("❌ Health check found issues!")
        print("   Run 'make logs' to see detailed logs.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1) 