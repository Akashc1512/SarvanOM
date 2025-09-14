"""
Production Deployment Pipeline

This module provides automated deployment, monitoring, and operations
capabilities for the SarvanOM platform in production environments.
"""

import asyncio
import aiohttp
import json
import subprocess
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import yaml

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    environment: str
    services: List[str]
    docker_compose_file: str
    health_check_timeout: int = 300
    rollback_enabled: bool = True
    monitoring_enabled: bool = True

@dataclass
class ServiceStatus:
    """Service deployment status"""
    service_name: str
    status: str  # deploying, healthy, unhealthy, failed
    port: int
    health_endpoint: str
    last_check: datetime
    error_message: Optional[str] = None

class DeploymentPipeline:
    """Production deployment pipeline"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.service_statuses: Dict[str, ServiceStatus] = {}
        self.deployment_log: List[Dict[str, Any]] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Service configurations
        self.service_configs = {
            "model_registry": {"port": 8000, "health_endpoint": "/health"},
            "gateway": {"port": 8007, "health_endpoint": "/health"},
            "synthesis": {"port": 8008, "health_endpoint": "/health"},
            "feeds": {"port": 8005, "health_endpoint": "/health"},
            "retrieval": {"port": 8004, "health_endpoint": "/health"},
            "auth": {"port": 8012, "health_endpoint": "/auth/health"},
            "knowledge_graph": {"port": 8013, "health_endpoint": "/health"},
            "search": {"port": 8015, "health_endpoint": "/search/health"},
            "model_router": {"port": 8001, "health_endpoint": "/health"},
            "auto_upgrade": {"port": 8002, "health_endpoint": "/health"},
            "guided_prompt": {"port": 8003, "health_endpoint": "/health"},
            "observability": {"port": 8009, "health_endpoint": "/health"},
            "security": {"port": 8014, "health_endpoint": "/health"},
            "fact_check": {"port": 8011, "health_endpoint": "/health"},
            "cicd": {"port": 8010, "health_endpoint": "/health"},
            "crud": {"port": 8011, "health_endpoint": "/health"}
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def log_deployment_event(self, event: str, details: Dict[str, Any]):
        """Log deployment events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "environment": self.config.environment,
            "details": details
        }
        self.deployment_log.append(log_entry)
        logger.info(f"Deployment Event: {event} - {details}")
    
    async def deploy_services(self) -> bool:
        """Deploy all configured services"""
        self.log_deployment_event("deployment_started", {
            "services": self.config.services,
            "environment": self.config.environment
        })
        
        try:
            # Step 1: Start infrastructure services
            await self._start_infrastructure()
            
            # Step 2: Deploy services in dependency order
            deployment_order = self._get_deployment_order()
            
            for service_group in deployment_order:
                await self._deploy_service_group(service_group)
            
            # Step 3: Verify deployment
            deployment_success = await self._verify_deployment()
            
            if deployment_success:
                self.log_deployment_event("deployment_completed", {
                    "status": "success",
                    "services_deployed": len(self.config.services)
                })
            else:
                self.log_deployment_event("deployment_failed", {
                    "status": "failed",
                    "reason": "health_check_failed"
                })
                
                if self.config.rollback_enabled:
                    await self._rollback_deployment()
            
            return deployment_success
            
        except Exception as e:
            self.log_deployment_event("deployment_error", {
                "error": str(e),
                "status": "failed"
            })
            
            if self.config.rollback_enabled:
                await self._rollback_deployment()
            
            return False
    
    async def _start_infrastructure(self):
        """Start infrastructure services (Redis, Qdrant, etc.)"""
        self.log_deployment_event("infrastructure_start", {"step": "starting_infrastructure"})
        
        try:
            # Start Docker infrastructure services
            result = subprocess.run([
                "docker-compose", "-f", "docker-compose.yml", "up", "-d",
                "redis", "qdrant", "meilisearch", "arangodb"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_deployment_event("infrastructure_started", {"status": "success"})
                # Wait for infrastructure to be ready
                await asyncio.sleep(30)
            else:
                raise Exception(f"Infrastructure start failed: {result.stderr}")
                
        except Exception as e:
            self.log_deployment_event("infrastructure_error", {"error": str(e)})
            raise
    
    def _get_deployment_order(self) -> List[List[str]]:
        """Get deployment order based on service dependencies"""
        # Group services by deployment order (dependencies first)
        return [
            # Core services first
            ["model_registry", "gateway"],
            # Processing services
            ["synthesis", "retrieval", "feeds"],
            # Specialized services
            ["auth", "knowledge_graph", "search"],
            # Supporting services
            ["model_router", "auto_upgrade", "guided_prompt"],
            # Monitoring and operations
            ["observability", "security", "fact_check", "cicd", "crud"]
        ]
    
    async def _deploy_service_group(self, service_group: List[str]):
        """Deploy a group of services"""
        self.log_deployment_event("service_group_deploy", {"services": service_group})
        
        # Start services in parallel
        tasks = []
        for service in service_group:
            if service in self.config.services:
                task = asyncio.create_task(self._deploy_single_service(service))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        # Wait for services to be ready
        await asyncio.sleep(10)
    
    async def _deploy_single_service(self, service_name: str):
        """Deploy a single service"""
        self.log_deployment_event("service_deploy_start", {"service": service_name})
        
        try:
            # Update service status
            self.service_statuses[service_name] = ServiceStatus(
                service_name=service_name,
                status="deploying",
                port=self.service_configs[service_name]["port"],
                health_endpoint=self.service_configs[service_name]["health_endpoint"],
                last_check=datetime.now()
            )
            
            # Start the service (in production, this would be Docker/Kubernetes)
            # For now, we'll simulate by checking if the service is already running
            await self._start_service(service_name)
            
            # Wait for service to be healthy
            health_check_passed = await self._wait_for_health(service_name)
            
            if health_check_passed:
                self.service_statuses[service_name].status = "healthy"
                self.log_deployment_event("service_deploy_success", {"service": service_name})
            else:
                self.service_statuses[service_name].status = "unhealthy"
                self.log_deployment_event("service_deploy_failed", {
                    "service": service_name,
                    "reason": "health_check_failed"
                })
                
        except Exception as e:
            self.service_statuses[service_name].status = "failed"
            self.service_statuses[service_name].error_message = str(e)
            self.log_deployment_event("service_deploy_error", {
                "service": service_name,
                "error": str(e)
            })
    
    async def _start_service(self, service_name: str):
        """Start a service (placeholder for actual deployment logic)"""
        # In production, this would start the service using Docker, Kubernetes, etc.
        # For now, we'll just check if the service is already running
        port = self.service_configs[service_name]["port"]
        
        # Check if service is already running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"Service {service_name} is already running")
                        return
        except:
            pass
        
        # If not running, start it (this would be actual deployment logic)
        logger.info(f"Starting service {service_name} on port {port}")
        # In production: subprocess.run(["docker", "run", "-d", f"sarvanom/{service_name}"])
    
    async def _wait_for_health(self, service_name: str, timeout: int = 60) -> bool:
        """Wait for service to become healthy"""
        start_time = time.time()
        port = self.service_configs[service_name]["port"]
        health_endpoint = self.service_configs[service_name]["health_endpoint"]
        
        while time.time() - start_time < timeout:
            try:
                async with self.session.get(f"http://localhost:{port}{health_endpoint}") as response:
                    if response.status == 200:
                        self.service_statuses[service_name].last_check = datetime.now()
                        return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        return False
    
    async def _verify_deployment(self) -> bool:
        """Verify that all services are healthy"""
        self.log_deployment_event("deployment_verification", {"step": "verifying_services"})
        
        all_healthy = True
        
        for service_name in self.config.services:
            if service_name in self.service_statuses:
                status = self.service_statuses[service_name]
                if status.status != "healthy":
                    all_healthy = False
                    self.log_deployment_event("service_unhealthy", {
                        "service": service_name,
                        "status": status.status,
                        "error": status.error_message
                    })
        
        return all_healthy
    
    async def _rollback_deployment(self):
        """Rollback deployment in case of failure"""
        self.log_deployment_event("rollback_started", {"reason": "deployment_failure"})
        
        try:
            # Stop all services
            for service_name in self.config.services:
                await self._stop_service(service_name)
            
            self.log_deployment_event("rollback_completed", {"status": "success"})
            
        except Exception as e:
            self.log_deployment_event("rollback_failed", {"error": str(e)})
    
    async def _stop_service(self, service_name: str):
        """Stop a service"""
        logger.info(f"Stopping service {service_name}")
        # In production: subprocess.run(["docker", "stop", f"sarvanom_{service_name}"])
    
    async def monitor_deployment(self, duration_minutes: int = 60):
        """Monitor deployment health"""
        self.log_deployment_event("monitoring_started", {"duration_minutes": duration_minutes})
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            for service_name in self.config.services:
                if service_name in self.service_statuses:
                    await self._check_service_health(service_name)
            
            await asyncio.sleep(30)  # Check every 30 seconds
        
        self.log_deployment_event("monitoring_completed", {"status": "success"})
    
    async def _check_service_health(self, service_name: str):
        """Check health of a single service"""
        if service_name not in self.service_statuses:
            return
        
        status = self.service_statuses[service_name]
        port = status.port
        health_endpoint = status.health_endpoint
        
        try:
            async with self.session.get(f"http://localhost:{port}{health_endpoint}") as response:
                if response.status == 200:
                    if status.status != "healthy":
                        self.log_deployment_event("service_recovered", {"service": service_name})
                    status.status = "healthy"
                else:
                    if status.status == "healthy":
                        self.log_deployment_event("service_degraded", {
                            "service": service_name,
                            "status_code": response.status
                        })
                    status.status = "unhealthy"
                
                status.last_check = datetime.now()
                
        except Exception as e:
            if status.status == "healthy":
                self.log_deployment_event("service_failed", {
                    "service": service_name,
                    "error": str(e)
                })
            status.status = "failed"
            status.error_message = str(e)
            status.last_check = datetime.now()
    
    def generate_deployment_report(self) -> str:
        """Generate deployment report"""
        report = []
        report.append("=" * 80)
        report.append("SARVANOM DEPLOYMENT REPORT")
        report.append("=" * 80)
        report.append(f"Environment: {self.config.environment}")
        report.append(f"Deployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Service status summary
        report.append("SERVICE STATUS SUMMARY")
        report.append("-" * 40)
        
        healthy_count = sum(1 for s in self.service_statuses.values() if s.status == "healthy")
        total_count = len(self.service_statuses)
        
        report.append(f"Total Services: {total_count}")
        report.append(f"Healthy Services: {healthy_count}")
        report.append(f"Unhealthy Services: {total_count - healthy_count}")
        report.append("")
        
        # Individual service status
        report.append("INDIVIDUAL SERVICE STATUS")
        report.append("-" * 40)
        
        for service_name, status in self.service_statuses.items():
            status_icon = "✅" if status.status == "healthy" else "❌"
            report.append(f"{status_icon} {service_name}")
            report.append(f"  Status: {status.status}")
            report.append(f"  Port: {status.port}")
            report.append(f"  Last Check: {status.last_check.strftime('%H:%M:%S')}")
            if status.error_message:
                report.append(f"  Error: {status.error_message}")
            report.append("")
        
        # Deployment events
        report.append("DEPLOYMENT EVENTS")
        report.append("-" * 40)
        
        for event in self.deployment_log[-10:]:  # Show last 10 events
            report.append(f"{event['timestamp']}: {event['event']}")
            if 'details' in event:
                report.append(f"  Details: {event['details']}")
            report.append("")
        
        return "\n".join(report)
    
    def save_deployment_log(self, filename: str = None):
        """Save deployment log to file"""
        if not filename:
            filename = f"deployment_log_{self.config.environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.deployment_log, f, indent=2)
        
        logger.info(f"Deployment log saved to {filename}")

async def run_production_deployment():
    """Run production deployment"""
    config = DeploymentConfig(
        environment="production",
        services=[
            "model_registry", "gateway", "synthesis", "feeds", "retrieval",
            "auth", "knowledge_graph", "search", "model_router", "auto_upgrade",
            "guided_prompt", "observability", "security", "fact_check", "cicd", "crud"
        ],
        docker_compose_file="docker-compose.yml",
        health_check_timeout=300,
        rollback_enabled=True,
        monitoring_enabled=True
    )
    
    async with DeploymentPipeline(config) as pipeline:
        logger.info("Starting production deployment...")
        
        # Deploy services
        deployment_success = await pipeline.deploy_services()
        
        if deployment_success:
            logger.info("Deployment successful! Starting monitoring...")
            
            # Monitor deployment for 10 minutes
            await pipeline.monitor_deployment(duration_minutes=10)
        else:
            logger.error("Deployment failed!")
        
        # Generate report
        report = pipeline.generate_deployment_report()
        print(report)
        
        # Save deployment log
        pipeline.save_deployment_log()
        
        return deployment_success

if __name__ == "__main__":
    asyncio.run(run_production_deployment())
