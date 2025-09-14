"""
CI/CD Gates & Quality Bars Service - SarvanOM v2

Apply docs/ci/* gates:
Block merges if contracts fail (naming, env, lint), if ttfr_refine_p95 > 800ms or accept_rate < 30% on staging 48h, or if a11y tests for Guided Prompt fail.
Release flow with canary + rollback.
"""

import asyncio
import json
import logging
import time
import subprocess
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

# Import central configuration
from shared.core.config.central_config import get_central_config

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Get configuration
config = get_central_config()

# Prometheus metrics
cicd_checks_total = Counter('sarvanom_cicd_checks_total', 'Total CI/CD checks', ['check_type', 'status'])
cicd_gates_total = Counter('sarvanom_cicd_gates_total', 'Total gate evaluations', ['gate_type', 'result'])
cicd_deployments_total = Counter('sarvanom_cicd_deployments_total', 'Total deployments', ['environment', 'status'])
cicd_rollbacks_total = Counter('sarvanom_cicd_rollbacks_total', 'Total rollbacks', ['environment', 'reason'])
cicd_performance_checks = Histogram('sarvanom_cicd_performance_checks_seconds', 'Performance check duration', ['check_type'])
cicd_quality_score = Gauge('sarvanom_cicd_quality_score', 'Overall quality score', ['metric_type'])

class GateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

class CheckType(str, Enum):
    LINT = "lint"
    TYPE_CHECK = "type_check"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    INTEGRATION = "integration"
    E2E = "e2e"

class Environment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

@dataclass
class QualityGate:
    name: str
    check_type: CheckType
    threshold: float
    current_value: float
    status: GateStatus
    message: str
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    ttfr_refine_p95: float
    accept_rate: float
    error_rate: float
    response_time_p95: float
    throughput: float

@dataclass
class DeploymentStatus:
    environment: Environment
    version: str
    status: str
    canary_percentage: float
    start_time: datetime
    metrics: PerformanceMetrics

class QualityGateManager:
    """Manages quality gates and checks"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.gate_thresholds = {
            "ttfr_refine_p95": 800.0,  # ms
            "accept_rate": 30.0,  # %
            "error_rate": 5.0,  # %
            "response_time_p95": 5000.0,  # ms
            "test_coverage": 80.0,  # %
            "lighthouse_score": 90.0,  # score
            "bundle_size": 1024.0,  # KB
        }
    
    async def run_lint_checks(self) -> QualityGate:
        """Run linting checks"""
        start_time = time.time()
        
        try:
            # Python linting
            result = subprocess.run(
                ["ruff", "check", "."],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            python_lint_passed = result.returncode == 0
            
            # TypeScript linting
            result = subprocess.run(
                ["npm", "run", "lint"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            ts_lint_passed = result.returncode == 0
            
            status = GateStatus.PASS if python_lint_passed and ts_lint_passed else GateStatus.FAIL
            message = "Linting passed" if status == GateStatus.PASS else "Linting failed"
            
            cicd_checks_total.labels(check_type=CheckType.LINT.value, status=status.value).inc()
            cicd_performance_checks.labels(check_type=CheckType.LINT.value).observe(time.time() - start_time)
            
            return QualityGate(
                name="lint_checks",
                check_type=CheckType.LINT,
                threshold=0.0,
                current_value=1.0 if status == GateStatus.PASS else 0.0,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Lint checks failed", error=str(e))
            return QualityGate(
                name="lint_checks",
                check_type=CheckType.LINT,
                threshold=0.0,
                current_value=0.0,
                status=GateStatus.FAIL,
                message=f"Lint checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_type_checks(self) -> QualityGate:
        """Run type checking"""
        start_time = time.time()
        
        try:
            # Python type checking
            result = subprocess.run(
                ["mypy", "."],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            python_types_passed = result.returncode == 0
            
            # TypeScript type checking
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            ts_types_passed = result.returncode == 0
            
            status = GateStatus.PASS if python_types_passed and ts_types_passed else GateStatus.FAIL
            message = "Type checking passed" if status == GateStatus.PASS else "Type checking failed"
            
            cicd_checks_total.labels(check_type=CheckType.TYPE_CHECK.value, status=status.value).inc()
            cicd_performance_checks.labels(check_type=CheckType.TYPE_CHECK.value).observe(time.time() - start_time)
            
            return QualityGate(
                name="type_checks",
                check_type=CheckType.TYPE_CHECK,
                threshold=0.0,
                current_value=1.0 if status == GateStatus.PASS else 0.0,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Type checks failed", error=str(e))
            return QualityGate(
                name="type_checks",
                check_type=CheckType.TYPE_CHECK,
                threshold=0.0,
                current_value=0.0,
                status=GateStatus.FAIL,
                message=f"Type checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_security_checks(self) -> QualityGate:
        """Run security checks"""
        start_time = time.time()
        
        try:
            # Python security check
            result = subprocess.run(
                ["safety", "check"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            python_security_passed = result.returncode == 0
            
            # Node.js security check
            result = subprocess.run(
                ["npm", "audit", "--audit-level=high"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            npm_security_passed = result.returncode == 0
            
            status = GateStatus.PASS if python_security_passed and npm_security_passed else GateStatus.FAIL
            message = "Security checks passed" if status == GateStatus.PASS else "Security vulnerabilities found"
            
            cicd_checks_total.labels(check_type=CheckType.SECURITY.value, status=status.value).inc()
            cicd_performance_checks.labels(check_type=CheckType.SECURITY.value).observe(time.time() - start_time)
            
            return QualityGate(
                name="security_checks",
                check_type=CheckType.SECURITY,
                threshold=0.0,
                current_value=1.0 if status == GateStatus.PASS else 0.0,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Security checks failed", error=str(e))
            return QualityGate(
                name="security_checks",
                check_type=CheckType.SECURITY,
                threshold=0.0,
                current_value=0.0,
                status=GateStatus.FAIL,
                message=f"Security checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_performance_checks(self) -> QualityGate:
        """Run performance checks"""
        start_time = time.time()
        
        try:
            # Get performance metrics from observability service
            async with httpx.AsyncClient() as client:
                response = await client.get("http://observability:8006/metrics/performance")
                if response.status_code == 200:
                    metrics = response.json()
                    
                    ttfr_refine_p95 = metrics.get("ttfr_refine_p95", 0)
                    accept_rate = metrics.get("accept_rate", 0)
                    
                    # Check Guided Prompt performance gates
                    ttfr_pass = ttfr_refine_p95 <= self.gate_thresholds["ttfr_refine_p95"]
                    accept_pass = accept_rate >= self.gate_thresholds["accept_rate"]
                    
                    status = GateStatus.PASS if ttfr_pass and accept_pass else GateStatus.FAIL
                    message = f"TTFR p95: {ttfr_refine_p95}ms, Accept rate: {accept_rate}%"
                    
                    cicd_checks_total.labels(check_type=CheckType.PERFORMANCE.value, status=status.value).inc()
                    cicd_performance_checks.labels(check_type=CheckType.PERFORMANCE.value).observe(time.time() - start_time)
                    
                    return QualityGate(
                        name="performance_checks",
                        check_type=CheckType.PERFORMANCE,
                        threshold=self.gate_thresholds["ttfr_refine_p95"],
                        current_value=ttfr_refine_p95,
                        status=status,
                        message=message,
                        timestamp=datetime.now()
                    )
                else:
                    raise Exception("Failed to get performance metrics")
                    
        except Exception as e:
            logger.error("Performance checks failed", error=str(e))
            return QualityGate(
                name="performance_checks",
                check_type=CheckType.PERFORMANCE,
                threshold=self.gate_thresholds["ttfr_refine_p95"],
                current_value=float('inf'),
                status=GateStatus.FAIL,
                message=f"Performance checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_accessibility_checks(self) -> QualityGate:
        """Run accessibility checks for Guided Prompt"""
        start_time = time.time()
        
        try:
            # Run accessibility tests
            result = subprocess.run(
                ["npm", "run", "test:a11y"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            a11y_passed = result.returncode == 0
            
            status = GateStatus.PASS if a11y_passed else GateStatus.FAIL
            message = "Accessibility tests passed" if status == GateStatus.PASS else "Accessibility tests failed"
            
            cicd_checks_total.labels(check_type=CheckType.ACCESSIBILITY.value, status=status.value).inc()
            cicd_performance_checks.labels(check_type=CheckType.ACCESSIBILITY.value).observe(time.time() - start_time)
            
            return QualityGate(
                name="accessibility_checks",
                check_type=CheckType.ACCESSIBILITY,
                threshold=0.0,
                current_value=1.0 if status == GateStatus.PASS else 0.0,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Accessibility checks failed", error=str(e))
            return QualityGate(
                name="accessibility_checks",
                check_type=CheckType.ACCESSIBILITY,
                threshold=0.0,
                current_value=0.0,
                status=GateStatus.FAIL,
                message=f"Accessibility checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_integration_checks(self) -> QualityGate:
        """Run integration tests"""
        start_time = time.time()
        
        try:
            # Run integration tests
            result = subprocess.run(
                ["pytest", "tests/integration/", "-v"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            
            integration_passed = result.returncode == 0
            
            status = GateStatus.PASS if integration_passed else GateStatus.FAIL
            message = "Integration tests passed" if status == GateStatus.PASS else "Integration tests failed"
            
            cicd_checks_total.labels(check_type=CheckType.INTEGRATION.value, status=status.value).inc()
            cicd_performance_checks.labels(check_type=CheckType.INTEGRATION.value).observe(time.time() - start_time)
            
            return QualityGate(
                name="integration_checks",
                check_type=CheckType.INTEGRATION,
                threshold=0.0,
                current_value=1.0 if status == GateStatus.PASS else 0.0,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Integration checks failed", error=str(e))
            return QualityGate(
                name="integration_checks",
                check_type=CheckType.INTEGRATION,
                threshold=0.0,
                current_value=0.0,
                status=GateStatus.FAIL,
                message=f"Integration checks failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_all_gates(self) -> List[QualityGate]:
        """Run all quality gates"""
        gates = []
        
        # Run all checks in parallel
        tasks = [
            self.run_lint_checks(),
            self.run_type_checks(),
            self.run_security_checks(),
            self.run_performance_checks(),
            self.run_accessibility_checks(),
            self.run_integration_checks()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, QualityGate):
                gates.append(result)
                cicd_gates_total.labels(gate_type=result.check_type.value, result=result.status.value).inc()
            else:
                logger.error("Gate check failed", error=str(result))
        
        return gates
    
    def should_block_merge(self, gates: List[QualityGate]) -> Tuple[bool, List[str]]:
        """Determine if merge should be blocked"""
        blocking_issues = []
        
        for gate in gates:
            if gate.status == GateStatus.FAIL:
                blocking_issues.append(f"{gate.name}: {gate.message}")
        
        return len(blocking_issues) > 0, blocking_issues

class DeploymentManager:
    """Manages deployments and rollbacks"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.deployments = {}
    
    async def start_canary_deployment(self, environment: Environment, version: str) -> DeploymentStatus:
        """Start canary deployment"""
        deployment = DeploymentStatus(
            environment=environment,
            version=version,
            status="canary",
            canary_percentage=5.0,
            start_time=datetime.now(),
            metrics=PerformanceMetrics(
                ttfr_refine_p95=0.0,
                accept_rate=0.0,
                error_rate=0.0,
                response_time_p95=0.0,
                throughput=0.0
            )
        )
        
        self.deployments[f"{environment.value}_{version}"] = deployment
        
        # Store in Redis
        self.redis.setex(
            f"deployment:{environment.value}:{version}",
            3600,  # 1 hour TTL
            json.dumps(asdict(deployment), default=str)
        )
        
        cicd_deployments_total.labels(environment=environment.value, status="canary_started").inc()
        
        logger.info("Canary deployment started", environment=environment.value, version=version)
        
        return deployment
    
    async def update_canary_percentage(self, environment: Environment, version: str, percentage: float):
        """Update canary traffic percentage"""
        key = f"{environment.value}_{version}"
        if key in self.deployments:
            self.deployments[key].canary_percentage = percentage
            
            # Update Redis
            self.redis.setex(
                f"deployment:{environment.value}:{version}",
                3600,
                json.dumps(asdict(self.deployments[key]), default=str)
            )
            
            logger.info("Canary percentage updated", environment=environment.value, version=version, percentage=percentage)
    
    async def promote_deployment(self, environment: Environment, version: str):
        """Promote deployment to 100%"""
        key = f"{environment.value}_{version}"
        if key in self.deployments:
            self.deployments[key].status = "promoted"
            self.deployments[key].canary_percentage = 100.0
            
            # Update Redis
            self.redis.setex(
                f"deployment:{environment.value}:{version}",
                3600,
                json.dumps(asdict(self.deployments[key]), default=str)
            )
            
            cicd_deployments_total.labels(environment=environment.value, status="promoted").inc()
            
            logger.info("Deployment promoted", environment=environment.value, version=version)
    
    async def rollback_deployment(self, environment: Environment, version: str, reason: str):
        """Rollback deployment"""
        key = f"{environment.value}_{version}"
        if key in self.deployments:
            self.deployments[key].status = "rollback"
            self.deployments[key].canary_percentage = 0.0
            
            # Update Redis
            self.redis.setex(
                f"deployment:{environment.value}:{version}",
                3600,
                json.dumps(asdict(self.deployments[key]), default=str)
            )
            
            cicd_rollbacks_total.labels(environment=environment.value, reason=reason).inc()
            
            logger.info("Deployment rolled back", environment=environment.value, version=version, reason=reason)
    
    async def get_deployment_status(self, environment: Environment, version: str) -> Optional[DeploymentStatus]:
        """Get deployment status"""
        key = f"{environment.value}_{version}"
        return self.deployments.get(key)

# FastAPI app
app = FastAPI(
    title="CI/CD Gates & Quality Bars Service", 
    version="2.0.0",
    description="CI/CD gates and quality bars service with automated testing and deployment management"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client
redis_client = redis.Redis.from_url(str(config.redis_url), decode_responses=True)

# Managers
quality_gate_manager = QualityGateManager(redis_client)
deployment_manager = DeploymentManager(redis_client)

# Pydantic models for API
class GateCheckRequest(BaseModel):
    check_types: Optional[List[CheckType]] = None

class DeploymentRequest(BaseModel):
    environment: Environment
    version: str

class CanaryUpdateRequest(BaseModel):
    environment: Environment
    version: str
    percentage: float = Field(..., ge=0, le=100)

class RollbackRequest(BaseModel):
    environment: Environment
    version: str
    reason: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cicd"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check Redis connection
        redis_client.ping()
        return {"status": "ready", "service": "cicd"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and configuration"""
    return {
        "service": "cicd",
        "active_providers": {
            "openai": bool(getattr(config, 'openai_api_key', None)),
            "anthropic": bool(getattr(config, 'anthropic_api_key', None)),
            "google": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(getattr(config, 'huggingface_api_key', None) or getattr(config, 'huggingface_read_token', None) or getattr(config, 'huggingface_write_token', None)),
            "ollama": bool(getattr(config, 'ollama_base_url', None))
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "cicd",
        "version": "2.0.0",
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/gates/check")
async def check_quality_gates(request: GateCheckRequest):
    """Run quality gate checks"""
    try:
        if request.check_types:
            # Run specific checks
            gates = []
            for check_type in request.check_types:
                if check_type == CheckType.LINT:
                    gates.append(await quality_gate_manager.run_lint_checks())
                elif check_type == CheckType.TYPE_CHECK:
                    gates.append(await quality_gate_manager.run_type_checks())
                elif check_type == CheckType.SECURITY:
                    gates.append(await quality_gate_manager.run_security_checks())
                elif check_type == CheckType.PERFORMANCE:
                    gates.append(await quality_gate_manager.run_performance_checks())
                elif check_type == CheckType.ACCESSIBILITY:
                    gates.append(await quality_gate_manager.run_accessibility_checks())
                elif check_type == CheckType.INTEGRATION:
                    gates.append(await quality_gate_manager.run_integration_checks())
        else:
            # Run all checks
            gates = await quality_gate_manager.run_all_gates()
        
        # Check if merge should be blocked
        should_block, blocking_issues = quality_gate_manager.should_block_merge(gates)
        
        return {
            "status": "success",
            "gates": [asdict(gate) for gate in gates],
            "should_block_merge": should_block,
            "blocking_issues": blocking_issues
        }
        
    except Exception as e:
        logger.error("Quality gate check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deployment/start-canary")
async def start_canary_deployment(request: DeploymentRequest):
    """Start canary deployment"""
    try:
        deployment = await deployment_manager.start_canary_deployment(request.environment, request.version)
        
        return {
            "status": "success",
            "deployment": asdict(deployment)
        }
        
    except Exception as e:
        logger.error("Canary deployment start failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deployment/update-canary")
async def update_canary_percentage(request: CanaryUpdateRequest):
    """Update canary traffic percentage"""
    try:
        await deployment_manager.update_canary_percentage(
            request.environment,
            request.version,
            request.percentage
        )
        
        return {
            "status": "success",
            "environment": request.environment.value,
            "version": request.version,
            "percentage": request.percentage
        }
        
    except Exception as e:
        logger.error("Canary update failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deployment/promote")
async def promote_deployment(request: DeploymentRequest):
    """Promote deployment to 100%"""
    try:
        await deployment_manager.promote_deployment(request.environment, request.version)
        
        return {
            "status": "success",
            "environment": request.environment.value,
            "version": request.version,
            "action": "promoted"
        }
        
    except Exception as e:
        logger.error("Deployment promotion failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deployment/rollback")
async def rollback_deployment(request: RollbackRequest):
    """Rollback deployment"""
    try:
        await deployment_manager.rollback_deployment(
            request.environment,
            request.version,
            request.reason
        )
        
        return {
            "status": "success",
            "environment": request.environment.value,
            "version": request.version,
            "action": "rollback",
            "reason": request.reason
        }
        
    except Exception as e:
        logger.error("Deployment rollback failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deployment/status/{environment}/{version}")
async def get_deployment_status(environment: str, version: str):
    """Get deployment status"""
    try:
        env = Environment(environment)
        deployment = await deployment_manager.get_deployment_status(env, version)
        
        if deployment:
            return {
                "status": "success",
                "deployment": asdict(deployment)
            }
        else:
            return {
                "status": "not_found",
                "message": f"Deployment {version} not found in {environment}"
            }
        
    except Exception as e:
        logger.error("Get deployment status failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gates/thresholds")
async def get_gate_thresholds():
    """Get quality gate thresholds"""
    try:
        return {
            "status": "success",
            "thresholds": quality_gate_manager.gate_thresholds
        }
        
    except Exception as e:
        logger.error("Get gate thresholds failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gates/thresholds")
async def update_gate_thresholds(thresholds: Dict[str, float]):
    """Update quality gate thresholds"""
    try:
        quality_gate_manager.gate_thresholds.update(thresholds)
        
        return {
            "status": "success",
            "thresholds": quality_gate_manager.gate_thresholds
        }
        
    except Exception as e:
        logger.error("Update gate thresholds failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Observability middleware
# Always mount Prometheus metrics endpoint
try:
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics endpoint mounted at /metrics")
except Exception as e:
    logger.error(f"Failed to mount Prometheus metrics: {e}")

# Conditional tracing setup - only if keys exist
tracing_enabled = False
if (hasattr(config, 'tracing_enabled') and config.tracing_enabled and 
    hasattr(config, 'jaeger_agent_host') and config.jaeger_agent_host):
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if hasattr(config, 'jaeger_agent_port') and config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        tracing_enabled = True
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")
else:
    logger.info("Tracing disabled - no tracing keys configured")

# Add debug trace endpoint if tracing is enabled
if tracing_enabled:
    @app.get("/_debug/trace")
    async def debug_trace():
        """Debug endpoint to echo trace information when tracing is enabled"""
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            
            # Create a sample span
            with tracer.start_as_current_span("debug_trace_echo") as span:
                span.set_attribute("debug.endpoint", "/_debug/trace")
                span.set_attribute("debug.timestamp", datetime.now().isoformat())
                
                return {
                    "status": "tracing_enabled",
                    "tracer_name": tracer.name,
                    "trace_id": format(span.get_span_context().trace_id, '032x'),
                    "span_id": format(span.get_span_context().span_id, '016x'),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Tracing is active and working"
                }
        except Exception as e:
            logger.error(f"Debug trace endpoint error: {e}")
            return {
                "status": "tracing_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
else:
    @app.get("/_debug/trace")
    async def debug_trace_disabled():
        """Debug endpoint when tracing is disabled"""
        return {
            "status": "tracing_disabled",
            "message": "Tracing is not enabled - no tracing keys configured",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Start FastAPI server with integrated metrics endpoint
    uvicorn.run(app, host="0.0.0.0", port=8010)
