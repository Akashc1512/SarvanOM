#!/usr/bin/env python3
"""
CI Gates Service - SarvanOM v2

Implements CI quality gates for provider key validation and budget compliance.
Implements PR-6 CI hardening requirements for automated validation.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import structlog

from .provider_key_validator import (
    ProviderKeyValidator, 
    ValidationResult, 
    ValidationReport,
    get_provider_key_validator
)
from ..observability.fallback_metrics import get_fallback_metrics

logger = structlog.get_logger(__name__)

@dataclass
class CIGateResult:
    """Result of a CI gate check"""
    gate_name: str
    passed: bool
    message: str
    details: Dict[str, Any]
    severity: str  # 'error', 'warning', 'info'

@dataclass
class CIGateReport:
    """Complete CI gate report"""
    overall_passed: bool
    gates: List[CIGateResult]
    summary: str
    timestamp: datetime
    environment: str

class CIGatesService:
    """Service for running CI quality gates"""
    
    def __init__(self):
        self.validator = get_provider_key_validator()
        self.metrics = get_fallback_metrics()
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    def run_all_gates(self) -> CIGateReport:
        """Run all CI quality gates"""
        try:
            gates = []
            
            # Provider key validation gates
            gates.extend(self._run_provider_key_gates())
            
            # Budget compliance gates
            gates.extend(self._run_budget_compliance_gates())
            
            # Keyless fallback coverage gates
            gates.extend(self._run_keyless_fallback_gates())
            
            # Performance gates
            gates.extend(self._run_performance_gates())
            
            # Determine overall result
            overall_passed = all(gate.passed for gate in gates)
            
            # Generate summary
            summary = self._generate_summary(gates, overall_passed)
            
            return CIGateReport(
                overall_passed=overall_passed,
                gates=gates,
                summary=summary,
                timestamp=datetime.utcnow(),
                environment=self.environment
            )
            
        except Exception as e:
            logger.error(f"Failed to run CI gates: {e}")
            return CIGateReport(
                overall_passed=False,
                gates=[CIGateResult(
                    gate_name="ci_gates_error",
                    passed=False,
                    message=f"CI gates failed to run: {str(e)}",
                    details={"error": str(e)},
                    severity="error"
                )],
                summary=f"CI gates failed: {str(e)}",
                timestamp=datetime.utcnow(),
                environment=self.environment
            )
    
    def _run_provider_key_gates(self) -> List[CIGateResult]:
        """Run provider key validation gates"""
        gates = []
        
        try:
            # Check if keyless fallbacks are enabled
            keyless_fallbacks_enabled = os.getenv("KEYLESS_FALLBACKS_ENABLED", "true").lower() == "true"
            
            # Validate provider keys
            report = self.validator.validate_provider_keys(keyless_fallbacks_enabled)
            
            # Overall provider key validation
            gates.append(CIGateResult(
                gate_name="provider_keys_validation",
                passed=report.overall_status != ValidationResult.FAIL,
                message=f"Provider key validation: {report.overall_status.value}",
                details={
                    "overall_status": report.overall_status.value,
                    "lane_validations": {k: v.value for k, v in report.lane_validations.items()},
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "keyless_fallbacks_enabled": keyless_fallbacks_enabled
                },
                severity="error" if report.overall_status == ValidationResult.FAIL else "warning" if report.overall_status == ValidationResult.WARNING else "info"
            ))
            
            # Individual lane validations
            for lane, status in report.lane_validations.items():
                if status == ValidationResult.FAIL:
                    gates.append(CIGateResult(
                        gate_name=f"lane_{lane}_required_keys",
                        passed=False,
                        message=f"Required keys missing for {lane} lane",
                        details={
                            "lane": lane,
                            "status": status.value,
                            "description": self.validator.required_lanes.get(lane, {}).get("description", lane)
                        },
                        severity="error"
                    ))
                elif status == ValidationResult.WARNING:
                    gates.append(CIGateResult(
                        gate_name=f"lane_{lane}_fallback_warning",
                        passed=True,
                        message=f"{lane} lane using fallbacks only",
                        details={
                            "lane": lane,
                            "status": status.value,
                            "description": self.validator.required_lanes.get(lane, {}).get("description", lane)
                        },
                        severity="warning"
                    ))
            
        except Exception as e:
            gates.append(CIGateResult(
                gate_name="provider_keys_error",
                passed=False,
                message=f"Provider key validation failed: {str(e)}",
                details={"error": str(e)},
                severity="error"
            ))
        
        return gates
    
    def _run_budget_compliance_gates(self) -> List[CIGateResult]:
        """Run budget compliance gates"""
        gates = []
        
        try:
            # Check keyless-only lanes for budget compliance
            keyless_fallbacks_enabled = os.getenv("KEYLESS_FALLBACKS_ENABLED", "true").lower() == "true"
            
            if keyless_fallbacks_enabled:
                for lane in ["web_search", "news", "markets"]:
                    # Check if lane is keyless-only
                    config = self.validator.required_lanes.get(lane)
                    if not config:
                        continue
                    
                    required_providers = config["required_providers"]
                    has_required_keys = any(
                        self.validator._is_key_configured(self.validator.key_mappings.get(provider, ""))
                        for provider in required_providers
                    )
                    
                    if not has_required_keys:
                        # Lane is keyless-only, check budget compliance
                        compliant, issues = self.validator.validate_budget_compliance(lane, keyless_only=True)
                        
                        gates.append(CIGateResult(
                            gate_name=f"lane_{lane}_budget_compliance",
                            passed=compliant,
                            message=f"Budget compliance for keyless-only {lane}: {'PASS' if compliant else 'FAIL'}",
                            details={
                                "lane": lane,
                                "keyless_only": True,
                                "compliant": compliant,
                                "issues": issues
                            },
                            severity="error" if not compliant else "info"
                        ))
            
        except Exception as e:
            gates.append(CIGateResult(
                gate_name="budget_compliance_error",
                passed=False,
                message=f"Budget compliance check failed: {str(e)}",
                details={"error": str(e)},
                severity="error"
            ))
        
        return gates
    
    def _run_keyless_fallback_gates(self) -> List[CIGateResult]:
        """Run keyless fallback coverage gates"""
        gates = []
        
        try:
            keyless_fallbacks_enabled = os.getenv("KEYLESS_FALLBACKS_ENABLED", "true").lower() == "true"
            
            if not keyless_fallbacks_enabled:
                gates.append(CIGateResult(
                    gate_name="keyless_fallbacks_disabled",
                    passed=True,
                    message="Keyless fallbacks are disabled",
                    details={"keyless_fallbacks_enabled": False},
                    severity="info"
                ))
                return gates
            
            # Check fallback coverage for each lane
            for lane, config in self.validator.required_lanes.items():
                fallback_providers = config.get("fallback_providers", [])
                if not fallback_providers:
                    continue
                
                # Check if any fallback providers are configured
                configured_fallbacks = []
                for provider in fallback_providers:
                    key_name = self.validator.key_mappings.get(provider)
                    if key_name and self.validator._is_key_configured(key_name):
                        configured_fallbacks.append(provider)
                
                if not configured_fallbacks:
                    gates.append(CIGateResult(
                        gate_name=f"lane_{lane}_fallback_coverage",
                        passed=False,
                        message=f"No fallback providers configured for {lane} lane",
                        details={
                            "lane": lane,
                            "fallback_providers": fallback_providers,
                            "configured_fallbacks": configured_fallbacks
                        },
                        severity="error"
                    ))
                else:
                    gates.append(CIGateResult(
                        gate_name=f"lane_{lane}_fallback_coverage",
                        passed=True,
                        message=f"Fallback coverage available for {lane} lane",
                        details={
                            "lane": lane,
                            "fallback_providers": fallback_providers,
                            "configured_fallbacks": configured_fallbacks
                        },
                        severity="info"
                    ))
            
        except Exception as e:
            gates.append(CIGateResult(
                gate_name="keyless_fallback_error",
                passed=False,
                message=f"Keyless fallback check failed: {str(e)}",
                details={"error": str(e)},
                severity="error"
            ))
        
        return gates
    
    def _run_performance_gates(self) -> List[CIGateResult]:
        """Run performance gates"""
        gates = []
        
        try:
            # Check if we have performance data
            health_summary = self.metrics.get_provider_health_summary()
            
            if not health_summary:
                gates.append(CIGateResult(
                    gate_name="performance_data_available",
                    passed=True,
                    message="No performance data available (first run)",
                    details={"health_summary": {}},
                    severity="info"
                ))
                return gates
            
            # Check provider health
            unhealthy_providers = []
            for key, stats in health_summary.items():
                if stats["health_status"] == "unhealthy":
                    unhealthy_providers.append({
                        "provider": stats["provider"],
                        "lane": stats["lane"],
                        "success_rate": stats["success_rate"],
                        "timeout_rate": stats["timeout_rate"]
                    })
            
            if unhealthy_providers:
                gates.append(CIGateResult(
                    gate_name="provider_health_check",
                    passed=False,
                    message=f"{len(unhealthy_providers)} providers are unhealthy",
                    details={
                        "unhealthy_providers": unhealthy_providers,
                        "total_providers": len(health_summary)
                    },
                    severity="warning"
                ))
            else:
                gates.append(CIGateResult(
                    gate_name="provider_health_check",
                    passed=True,
                    message="All providers are healthy",
                    details={
                        "total_providers": len(health_summary),
                        "health_summary": health_summary
                    },
                    severity="info"
                ))
            
        except Exception as e:
            gates.append(CIGateResult(
                gate_name="performance_gates_error",
                passed=False,
                message=f"Performance gates failed: {str(e)}",
                details={"error": str(e)},
                severity="error"
            ))
        
        return gates
    
    def _generate_summary(self, gates: List[CIGateResult], overall_passed: bool) -> str:
        """Generate a human-readable summary"""
        try:
            error_count = sum(1 for gate in gates if gate.severity == "error")
            warning_count = sum(1 for gate in gates if gate.severity == "warning")
            info_count = sum(1 for gate in gates if gate.severity == "info")
            
            status_emoji = "✅" if overall_passed else "❌"
            status_text = "PASSED" if overall_passed else "FAILED"
            
            summary = f"{status_emoji} CI Gates {status_text}\n"
            summary += f"Environment: {self.environment}\n"
            summary += f"Timestamp: {datetime.utcnow().isoformat()}\n"
            summary += f"Total Gates: {len(gates)}\n"
            summary += f"Errors: {error_count}, Warnings: {warning_count}, Info: {info_count}\n"
            
            if error_count > 0:
                summary += "\n❌ Errors:\n"
                for gate in gates:
                    if gate.severity == "error":
                        summary += f"  - {gate.gate_name}: {gate.message}\n"
            
            if warning_count > 0:
                summary += "\n⚠️ Warnings:\n"
                for gate in gates:
                    if gate.severity == "warning":
                        summary += f"  - {gate.gate_name}: {gate.message}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Failed to generate summary: {str(e)}"
    
    def export_report(self, report: CIGateReport, format: str = "json") -> str:
        """Export report in specified format"""
        try:
            if format == "json":
                return json.dumps(asdict(report), default=str, indent=2)
            elif format == "text":
                return report.summary
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return f"Failed to export report: {str(e)}"

def main():
    """Main function for CLI usage"""
    try:
        service = CIGatesService()
        report = service.run_all_gates()
        
        # Print summary
        print(report.summary)
        
        # Export detailed report
        detailed_report = service.export_report(report, "json")
        print("\nDetailed Report:")
        print(detailed_report)
        
        # Exit with appropriate code
        sys.exit(0 if report.overall_passed else 1)
        
    except Exception as e:
        logger.error(f"CI gates failed: {e}")
        print(f"CI gates failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
