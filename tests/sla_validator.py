"""
SLA Validator - SarvanOM v2
Service Level Agreement validation framework for comprehensive SLA monitoring and compliance.
"""

import asyncio
import time
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import json
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SLAThreshold(Enum):
    SIMPLE_QUERY = 5.0
    TECHNICAL_QUERY = 7.0
    RESEARCH_QUERY = 10.0
    MULTIMEDIA_QUERY = 10.0
    GATEWAY_ROUTING = 0.1
    RETRIEVAL_SEARCH = 2.0
    SYNTHESIS_GENERATION = 5.0
    FACT_CHECK_VALIDATION = 3.0
    GUIDED_PROMPT_REFINEMENT = 0.8
    QDRANT_VECTOR_SEARCH = 0.05
    ARANGODB_GRAPH_QUERY = 0.1
    MEILISEARCH_FULLTEXT = 0.1
    POSTGRESQL_RELATIONAL = 0.05

class ServiceType(Enum):
    GATEWAY = "gateway"
    RETRIEVAL = "retrieval"
    SYNTHESIS = "synthesis"
    FACT_CHECK = "fact_check"
    GUIDED_PROMPT = "guided_prompt"
    QDRANT = "qdrant"
    ARANGODB = "arangodb"
    MEILISEARCH = "meilisearch"
    POSTGRESQL = "postgresql"

@dataclass
class SLAMeasurement:
    service: str
    operation: str
    response_time: float
    success: bool
    error_type: Optional[str] = None
    timestamp: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class SLACompliance:
    service: str
    operation: str
    threshold: float
    measurements: List[SLAMeasurement]
    compliance_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    availability: float
    sla_violations: int
    total_measurements: int

@dataclass
class SLAAlert:
    alert_id: str
    service: str
    operation: str
    alert_type: str
    severity: str
    message: str
    threshold: float
    actual_value: float
    timestamp: float
    resolved: bool = False

class SLAMonitor:
    """Real-time SLA monitoring and validation"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[SLAAlert] = []
        self.compliance_history: Dict[str, List[SLACompliance]] = defaultdict(list)
        self.running = False
        self.monitor_thread = None
        
        # SLA thresholds
        self.thresholds = {
            ServiceType.GATEWAY: {
                "routing": SLAThreshold.GATEWAY_ROUTING.value
            },
            ServiceType.RETRIEVAL: {
                "search": SLAThreshold.RETRIEVAL_SEARCH.value
            },
            ServiceType.SYNTHESIS: {
                "generation": SLAThreshold.SYNTHESIS_GENERATION.value
            },
            ServiceType.FACT_CHECK: {
                "validation": SLAThreshold.FACT_CHECK_VALIDATION.value
            },
            ServiceType.GUIDED_PROMPT: {
                "refinement": SLAThreshold.GUIDED_PROMPT_REFINEMENT.value
            },
            ServiceType.QDRANT: {
                "vector_search": SLAThreshold.QDRANT_VECTOR_SEARCH.value
            },
            ServiceType.ARANGODB: {
                "graph_query": SLAThreshold.ARANGODB_GRAPH_QUERY.value
            },
            ServiceType.MEILISEARCH: {
                "fulltext_search": SLAThreshold.MEILISEARCH_FULLTEXT.value
            },
            ServiceType.POSTGRESQL: {
                "relational_query": SLAThreshold.POSTGRESQL_RELATIONAL.value
            }
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            "compliance_rate": 0.95,  # Alert if compliance drops below 95%
            "error_rate": 0.05,       # Alert if error rate exceeds 5%
            "availability": 0.99,     # Alert if availability drops below 99%
            "response_time_spike": 2.0  # Alert if response time spikes 2x threshold
        }

    def record_measurement(self, measurement: SLAMeasurement):
        """Record a new SLA measurement"""
        key = f"{measurement.service}:{measurement.operation}"
        self.measurements[key].append(measurement)
        
        # Check for immediate alerts
        self._check_immediate_alerts(measurement)

    def _check_immediate_alerts(self, measurement: SLAMeasurement):
        """Check for immediate alert conditions"""
        service_type = ServiceType(measurement.service)
        operation = measurement.operation
        
        if service_type in self.thresholds and operation in self.thresholds[service_type]:
            threshold = self.thresholds[service_type][operation]
            
            # Check for response time spike
            if measurement.response_time > threshold * self.alert_thresholds["response_time_spike"]:
                alert = SLAAlert(
                    alert_id=f"spike_{int(time.time())}_{measurement.service}_{measurement.operation}",
                    service=measurement.service,
                    operation=measurement.operation,
                    alert_type="response_time_spike",
                    severity="warning",
                    message=f"Response time spike detected: {measurement.response_time:.3f}s (threshold: {threshold:.3f}s)",
                    threshold=threshold,
                    actual_value=measurement.response_time,
                    timestamp=time.time()
                )
                self.alerts.append(alert)
                logger.warning(f"SLA Alert: {alert.message}")
            
            # Check for SLA violation
            if measurement.response_time > threshold:
                alert = SLAAlert(
                    alert_id=f"violation_{int(time.time())}_{measurement.service}_{measurement.operation}",
                    service=measurement.service,
                    operation=measurement.operation,
                    alert_type="sla_violation",
                    severity="critical",
                    message=f"SLA violation: {measurement.response_time:.3f}s > {threshold:.3f}s",
                    threshold=threshold,
                    actual_value=measurement.response_time,
                    timestamp=time.time()
                )
                self.alerts.append(alert)
                logger.error(f"SLA Alert: {alert.message}")

    def calculate_compliance(self, service: str, operation: str, time_window: int = 3600) -> SLACompliance:
        """Calculate SLA compliance for a specific service and operation"""
        key = f"{service}:{operation}"
        measurements = list(self.measurements[key])
        
        # Filter measurements within time window
        cutoff_time = time.time() - time_window
        recent_measurements = [m for m in measurements if m.timestamp >= cutoff_time]
        
        if not recent_measurements:
            return SLACompliance(
                service=service,
                operation=operation,
                threshold=0.0,
                measurements=[],
                compliance_rate=0.0,
                avg_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                error_rate=0.0,
                availability=0.0,
                sla_violations=0,
                total_measurements=0
            )
        
        # Get threshold
        service_type = ServiceType(service)
        threshold = self.thresholds.get(service_type, {}).get(operation, 0.0)
        
        # Calculate metrics
        successful_measurements = [m for m in recent_measurements if m.success]
        failed_measurements = [m for m in recent_measurements if not m.success]
        
        total_measurements = len(recent_measurements)
        sla_violations = sum(1 for m in successful_measurements if m.response_time > threshold)
        
        compliance_rate = (len(successful_measurements) - sla_violations) / total_measurements if total_measurements > 0 else 0.0
        error_rate = len(failed_measurements) / total_measurements if total_measurements > 0 else 0.0
        availability = len(successful_measurements) / total_measurements if total_measurements > 0 else 0.0
        
        if successful_measurements:
            response_times = [m.response_time for m in successful_measurements]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
            p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = 0.0
        
        compliance = SLACompliance(
            service=service,
            operation=operation,
            threshold=threshold,
            measurements=recent_measurements,
            compliance_rate=compliance_rate,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            error_rate=error_rate,
            availability=availability,
            sla_violations=sla_violations,
            total_measurements=total_measurements
        )
        
        return compliance

    def get_overall_compliance(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get overall SLA compliance across all services"""
        overall_metrics = {
            "total_measurements": 0,
            "total_violations": 0,
            "total_errors": 0,
            "overall_compliance_rate": 0.0,
            "overall_error_rate": 0.0,
            "overall_availability": 0.0,
            "service_compliance": {}
        }
        
        total_compliance = 0.0
        total_services = 0
        
        for service_type in ServiceType:
            service_name = service_type.value
            service_compliance = {}
            
            if service_type in self.thresholds:
                for operation in self.thresholds[service_type]:
                    compliance = self.calculate_compliance(service_name, operation, time_window)
                    service_compliance[operation] = asdict(compliance)
                    
                    overall_metrics["total_measurements"] += compliance.total_measurements
                    overall_metrics["total_violations"] += compliance.sla_violations
                    overall_metrics["total_errors"] += int(compliance.error_rate * compliance.total_measurements)
                    
                    if compliance.total_measurements > 0:
                        total_compliance += compliance.compliance_rate
                        total_services += 1
            
            overall_metrics["service_compliance"][service_name] = service_compliance
        
        if total_services > 0:
            overall_metrics["overall_compliance_rate"] = total_compliance / total_services
        
        if overall_metrics["total_measurements"] > 0:
            overall_metrics["overall_error_rate"] = overall_metrics["total_errors"] / overall_metrics["total_measurements"]
            overall_metrics["overall_availability"] = 1.0 - overall_metrics["overall_error_rate"]
        
        return overall_metrics

    def check_alert_conditions(self):
        """Check for alert conditions across all services"""
        overall_metrics = self.get_overall_compliance()
        
        # Check overall compliance rate
        if overall_metrics["overall_compliance_rate"] < self.alert_thresholds["compliance_rate"]:
            alert = SLAAlert(
                alert_id=f"compliance_{int(time.time())}",
                service="system",
                operation="overall",
                alert_type="compliance_rate",
                severity="critical",
                message=f"Overall SLA compliance below threshold: {overall_metrics['overall_compliance_rate']:.2%} < {self.alert_thresholds['compliance_rate']:.2%}",
                threshold=self.alert_thresholds["compliance_rate"],
                actual_value=overall_metrics["overall_compliance_rate"],
                timestamp=time.time()
            )
            self.alerts.append(alert)
            logger.error(f"SLA Alert: {alert.message}")
        
        # Check overall error rate
        if overall_metrics["overall_error_rate"] > self.alert_thresholds["error_rate"]:
            alert = SLAAlert(
                alert_id=f"error_rate_{int(time.time())}",
                service="system",
                operation="overall",
                alert_type="error_rate",
                severity="critical",
                message=f"Overall error rate above threshold: {overall_metrics['overall_error_rate']:.2%} > {self.alert_thresholds['error_rate']:.2%}",
                threshold=self.alert_thresholds["error_rate"],
                actual_value=overall_metrics["overall_error_rate"],
                timestamp=time.time()
            )
            self.alerts.append(alert)
            logger.error(f"SLA Alert: {alert.message}")
        
        # Check overall availability
        if overall_metrics["overall_availability"] < self.alert_thresholds["availability"]:
            alert = SLAAlert(
                alert_id=f"availability_{int(time.time())}",
                service="system",
                operation="overall",
                alert_type="availability",
                severity="critical",
                message=f"Overall availability below threshold: {overall_metrics['overall_availability']:.2%} < {self.alert_thresholds['availability']:.2%}",
                threshold=self.alert_thresholds["availability"],
                actual_value=overall_metrics["overall_availability"],
                timestamp=time.time()
            )
            self.alerts.append(alert)
            logger.error(f"SLA Alert: {alert.message}")

    async def monitor_service_health(self, service: str, operation: str, endpoint: str):
        """Monitor health of a specific service"""
        while self.running:
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_time = time.time() - start_time
                        success = response.status == 200
                        error_type = None if success else f"HTTP_{response.status}"
                        
                        measurement = SLAMeasurement(
                            service=service,
                            operation=operation,
                            response_time=response_time,
                            success=success,
                            error_type=error_type,
                            timestamp=time.time()
                        )
                        
                        self.record_measurement(measurement)
                        
            except Exception as e:
                response_time = time.time() - start_time
                measurement = SLAMeasurement(
                    service=service,
                    operation=operation,
                    response_time=response_time,
                    success=False,
                    error_type=type(e).__name__,
                    timestamp=time.time()
                )
                self.record_measurement(measurement)
            
            await asyncio.sleep(5)  # Monitor every 5 seconds

    def start_monitoring(self):
        """Start continuous SLA monitoring"""
        if self.running:
            return
        
        self.running = True
        
        # Define service endpoints to monitor
        service_endpoints = {
            (ServiceType.GATEWAY.value, "routing", "/health"),
            (ServiceType.RETRIEVAL.value, "search", "/retrieval/health"),
            (ServiceType.SYNTHESIS.value, "generation", "/synthesis/health"),
            (ServiceType.FACT_CHECK.value, "validation", "/fact-check/health"),
            (ServiceType.GUIDED_PROMPT.value, "refinement", "/guided-prompt/health"),
            (ServiceType.QDRANT.value, "vector_search", "/qdrant/health"),
            (ServiceType.ARANGODB.value, "graph_query", "/arangodb/health"),
            (ServiceType.MEILISEARCH.value, "fulltext_search", "/meilisearch/health"),
            (ServiceType.POSTGRESQL.value, "relational_query", "/postgresql/health")
        }
        
        # Start monitoring tasks
        async def monitor_all_services():
            tasks = []
            for service, operation, endpoint in service_endpoints:
                task = self.monitor_service_health(service, operation, endpoint)
                tasks.append(task)
            
            # Also start alert checking
            async def check_alerts():
                while self.running:
                    self.check_alert_conditions()
                    await asyncio.sleep(60)  # Check alerts every minute
            
            tasks.append(check_alerts())
            await asyncio.gather(*tasks)
        
        # Start monitoring in a separate thread
        def run_monitoring():
            asyncio.run(monitor_all_services())
        
        self.monitor_thread = threading.Thread(target=run_monitoring, daemon=True)
        self.monitor_thread.start()
        
        logger.info("SLA monitoring started")

    def stop_monitoring(self):
        """Stop continuous SLA monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("SLA monitoring stopped")

    def get_active_alerts(self) -> List[SLAAlert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                break

    def generate_sla_report(self, time_window: int = 3600) -> Dict[str, Any]:
        """Generate comprehensive SLA report"""
        overall_metrics = self.get_overall_compliance(time_window)
        active_alerts = self.get_active_alerts()
        
        report = {
            "report_timestamp": time.time(),
            "time_window_seconds": time_window,
            "overall_metrics": overall_metrics,
            "active_alerts": [asdict(alert) for alert in active_alerts],
            "alert_summary": {
                "total_alerts": len(self.alerts),
                "active_alerts": len(active_alerts),
                "resolved_alerts": len(self.alerts) - len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
                "warning_alerts": len([a for a in active_alerts if a.severity == "warning"])
            },
            "sla_thresholds": {
                service_type.value: {
                    operation: threshold 
                    for operation, threshold in operations.items()
                }
                for service_type, operations in self.thresholds.items()
            },
            "recommendations": self._generate_recommendations(overall_metrics, active_alerts)
        }
        
        return report

    def _generate_recommendations(self, overall_metrics: Dict[str, Any], active_alerts: List[SLAAlert]) -> List[str]:
        """Generate recommendations based on SLA metrics and alerts"""
        recommendations = []
        
        if overall_metrics["overall_compliance_rate"] < 0.95:
            recommendations.append("Overall SLA compliance is below 95%. Consider investigating service performance bottlenecks.")
        
        if overall_metrics["overall_error_rate"] > 0.05:
            recommendations.append("Error rate is above 5%. Review error logs and implement better error handling.")
        
        if overall_metrics["overall_availability"] < 0.99:
            recommendations.append("System availability is below 99%. Implement redundancy and failover mechanisms.")
        
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        if critical_alerts:
            recommendations.append(f"Address {len(critical_alerts)} critical SLA alerts immediately.")
        
        # Service-specific recommendations
        for service_name, service_data in overall_metrics["service_compliance"].items():
            for operation, compliance_data in service_data.items():
                if compliance_data["compliance_rate"] < 0.90:
                    recommendations.append(f"Improve {service_name} {operation} performance - compliance rate: {compliance_data['compliance_rate']:.2%}")
        
        return recommendations

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save SLA report to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"sla_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"SLA report saved to {filename}")

# Pytest integration
class TestSLAValidation:
    """Pytest integration for SLA validation"""
    
    @pytest.fixture
    def sla_monitor(self):
        monitor = SLAMonitor()
        yield monitor
        monitor.stop_monitoring()
    
    def test_sla_measurement_recording(self, sla_monitor):
        """Test SLA measurement recording"""
        measurement = SLAMeasurement(
            service="gateway",
            operation="routing",
            response_time=0.05,
            success=True,
            timestamp=time.time()
        )
        
        sla_monitor.record_measurement(measurement)
        
        key = "gateway:routing"
        assert len(sla_monitor.measurements[key]) == 1
        assert sla_monitor.measurements[key][0].response_time == 0.05
    
    def test_sla_compliance_calculation(self, sla_monitor):
        """Test SLA compliance calculation"""
        # Add some test measurements
        for i in range(10):
            measurement = SLAMeasurement(
                service="gateway",
                operation="routing",
                response_time=0.05 + (i * 0.01),  # Varying response times
                success=True,
                timestamp=time.time() - (10 - i) * 60  # Spread over 10 minutes
            )
            sla_monitor.record_measurement(measurement)
        
        compliance = sla_monitor.calculate_compliance("gateway", "routing")
        
        assert compliance.total_measurements == 10
        assert compliance.availability == 1.0  # All successful
        assert compliance.error_rate == 0.0
    
    def test_sla_alert_generation(self, sla_monitor):
        """Test SLA alert generation"""
        # Add a measurement that violates SLA
        measurement = SLAMeasurement(
            service="gateway",
            operation="routing",
            response_time=0.5,  # Exceeds 0.1s threshold
            success=True,
            timestamp=time.time()
        )
        
        sla_monitor.record_measurement(measurement)
        
        # Check that alert was generated
        active_alerts = sla_monitor.get_active_alerts()
        assert len(active_alerts) > 0
        
        violation_alert = next((a for a in active_alerts if a.alert_type == "sla_violation"), None)
        assert violation_alert is not None
        assert violation_alert.severity == "critical"
    
    def test_overall_compliance_calculation(self, sla_monitor):
        """Test overall compliance calculation"""
        # Add measurements for multiple services
        services = ["gateway", "retrieval", "synthesis"]
        for service in services:
            for i in range(5):
                measurement = SLAMeasurement(
                    service=service,
                    operation="test_operation",
                    response_time=0.05,
                    success=True,
                    timestamp=time.time() - (5 - i) * 60
                )
                sla_monitor.record_measurement(measurement)
        
        overall_metrics = sla_monitor.get_overall_compliance()
        
        assert overall_metrics["total_measurements"] > 0
        assert "overall_compliance_rate" in overall_metrics
        assert "service_compliance" in overall_metrics

if __name__ == "__main__":
    async def main():
        monitor = SLAMonitor()
        
        try:
            # Start monitoring
            monitor.start_monitoring()
            
            # Let it run for a bit
            await asyncio.sleep(60)
            
            # Generate report
            report = monitor.generate_sla_report()
            monitor.save_report(report)
            
            # Print summary
            print("\n" + "="*50)
            print("SLA VALIDATION SUMMARY")
            print("="*50)
            print(f"Overall Compliance: {report['overall_metrics']['overall_compliance_rate']:.2%}")
            print(f"Overall Error Rate: {report['overall_metrics']['overall_error_rate']:.2%}")
            print(f"Overall Availability: {report['overall_metrics']['overall_availability']:.2%}")
            print(f"Active Alerts: {report['alert_summary']['active_alerts']}")
            print(f"Critical Alerts: {report['alert_summary']['critical_alerts']}")
            print("="*50)
            
        finally:
            monitor.stop_monitoring()
    
    asyncio.run(main())
