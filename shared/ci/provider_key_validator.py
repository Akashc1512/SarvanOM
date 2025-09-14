#!/usr/bin/env python3
"""
Provider Key Validator - SarvanOM v2

Validates provider key requirements and keyless fallback coverage for CI gates.
Implements PR-6 CI hardening requirements for provider key validation.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)

class ValidationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class ProviderKeyStatus:
    """Status of a provider key"""
    provider: str
    key_name: str
    configured: bool
    required: bool
    lane: str
    has_fallback: bool
    fallback_providers: List[str]

@dataclass
class ValidationReport:
    """Validation report for provider keys"""
    overall_status: ValidationResult
    lane_validations: Dict[str, ValidationResult]
    provider_statuses: List[ProviderKeyStatus]
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

class ProviderKeyValidator:
    """Validates provider key requirements for CI gates"""
    
    def __init__(self):
        self.required_lanes = {
            "web_search": {
                "required_providers": ["brave_search", "serpapi"],
                "fallback_providers": ["duckduckgo", "wikipedia", "stackexchange", "mdn"],
                "description": "Web Search Lane"
            },
            "news": {
                "required_providers": ["guardian", "newsapi"],
                "fallback_providers": ["gdelt", "hn_algolia", "rss"],
                "description": "News Lane"
            },
            "markets": {
                "required_providers": ["alphavantage"],
                "fallback_providers": ["finnhub", "fmp", "stooq", "sec_edgar"],
                "description": "Markets Lane"
            },
            "llm": {
                "required_providers": ["openai", "anthropic"],
                "fallback_providers": [],
                "description": "LLM Providers"
            },
            "lmm": {
                "required_providers": ["gemini"],
                "fallback_providers": ["openai_vision"],
                "description": "LMM Providers"
            }
        }
        
        self.key_mappings = {
            "brave_search": "BRAVE_SEARCH_API_KEY",
            "serpapi": "SERPAPI_KEY",
            "guardian": "GUARDIAN_OPEN_PLATFORM_KEY",
            "newsapi": "NEWSAPI_KEY",
            "alphavantage": "ALPHAVANTAGE_KEY",
            "finnhub": "FINNHUB_KEY",
            "fmp": "FMP_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "openai_vision": "OPENAI_API_KEY",  # Same key as OpenAI
            "qdrant": "QDRANT_API_KEY",
            "meili": "MEILI_MASTER_KEY",
            "arango": "ARANGO_USERNAME"
        }
    
    def validate_provider_keys(self, keyless_fallbacks_enabled: bool = True) -> ValidationReport:
        """Validate all provider key requirements"""
        try:
            lane_validations = {}
            provider_statuses = []
            errors = []
            warnings = []
            recommendations = []
            
            # Validate each lane
            for lane, config in self.required_lanes.items():
                lane_result = self._validate_lane(lane, config, keyless_fallbacks_enabled)
                lane_validations[lane] = lane_result["status"]
                provider_statuses.extend(lane_result["providers"])
                errors.extend(lane_result["errors"])
                warnings.extend(lane_result["warnings"])
                recommendations.extend(lane_result["recommendations"])
            
            # Determine overall status
            overall_status = self._determine_overall_status(lane_validations, errors)
            
            return ValidationReport(
                overall_status=overall_status,
                lane_validations=lane_validations,
                provider_statuses=provider_statuses,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to validate provider keys: {e}")
            return ValidationReport(
                overall_status=ValidationResult.FAIL,
                lane_validations={},
                provider_statuses=[],
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                recommendations=[]
            )
    
    def _validate_lane(self, lane: str, config: Dict[str, Any], keyless_fallbacks_enabled: bool) -> Dict[str, Any]:
        """Validate a specific lane"""
        required_providers = config["required_providers"]
        fallback_providers = config["fallback_providers"]
        description = config["description"]
        
        providers = []
        errors = []
        warnings = []
        recommendations = []
        
        # Check required providers
        configured_required = []
        for provider in required_providers:
            key_name = self.key_mappings.get(provider)
            if not key_name:
                errors.append(f"Unknown provider: {provider}")
                continue
            
            configured = self._is_key_configured(key_name)
            providers.append(ProviderKeyStatus(
                provider=provider,
                key_name=key_name,
                configured=configured,
                required=True,
                lane=lane,
                has_fallback=provider in fallback_providers,
                fallback_providers=fallback_providers
            ))
            
            if configured:
                configured_required.append(provider)
        
        # Check if any required providers are configured
        if not configured_required:
            if keyless_fallbacks_enabled and fallback_providers:
                warnings.append(f"{description}: No required providers configured, but keyless fallbacks are enabled")
                recommendations.append(f"Consider configuring at least one of: {', '.join(required_providers)}")
            else:
                errors.append(f"{description}: No required providers configured and keyless fallbacks disabled")
                recommendations.append(f"Configure at least one of: {', '.join(required_providers)}")
        
        # Check fallback providers
        for provider in fallback_providers:
            key_name = self.key_mappings.get(provider)
            if not key_name:
                continue
            
            configured = self._is_key_configured(key_name)
            providers.append(ProviderKeyStatus(
                provider=provider,
                key_name=key_name,
                configured=configured,
                required=False,
                lane=lane,
                has_fallback=True,
                fallback_providers=fallback_providers
            ))
        
        # Determine lane status
        if configured_required:
            status = ValidationResult.PASS
        elif keyless_fallbacks_enabled and fallback_providers:
            status = ValidationResult.WARNING
        else:
            status = ValidationResult.FAIL
        
        return {
            "status": status,
            "providers": providers,
            "errors": errors,
            "warnings": warnings,
            "recommendations": recommendations
        }
    
    def _is_key_configured(self, key_name: str) -> bool:
        """Check if a key is configured"""
        try:
            value = os.getenv(key_name)
            return value is not None and value.strip() != ""
        except Exception:
            return False
    
    def _determine_overall_status(self, lane_validations: Dict[str, ValidationResult], errors: List[str]) -> ValidationResult:
        """Determine overall validation status"""
        if any(status == ValidationResult.FAIL for status in lane_validations.values()):
            return ValidationResult.FAIL
        elif any(status == ValidationResult.WARNING for status in lane_validations.values()):
            return ValidationResult.WARNING
        else:
            return ValidationResult.PASS
    
    def validate_budget_compliance(self, lane: str, keyless_only: bool = False) -> Tuple[bool, List[str]]:
        """Validate budget compliance for a lane"""
        try:
            issues = []
            
            if keyless_only:
                # Check if keyless fallbacks can meet budget requirements
                config = self.required_lanes.get(lane)
                if not config:
                    issues.append(f"Unknown lane: {lane}")
                    return False, issues
                
                fallback_providers = config["fallback_providers"]
                if not fallback_providers:
                    issues.append(f"No keyless fallback providers available for {lane}")
                    return False, issues
                
                # Check if keyless providers are configured
                configured_fallbacks = []
                for provider in fallback_providers:
                    key_name = self.key_mappings.get(provider)
                    if key_name and self._is_key_configured(key_name):
                        configured_fallbacks.append(provider)
                
                if not configured_fallbacks:
                    issues.append(f"No keyless fallback providers configured for {lane}")
                    return False, issues
                
                # Budget requirements
                if lane in ["web_search", "news", "markets"]:
                    max_latency = 800  # 800ms per provider
                    issues.append(f"Keyless-only {lane} must respect ≤{max_latency}ms per-provider timeout")
                
                # End-to-end budget
                if lane == "web_search":
                    issues.append("Keyless-only web search must meet 5s end-to-end budget")
                elif lane == "news":
                    issues.append("Keyless-only news must meet 7s end-to-end budget")
                elif lane == "markets":
                    issues.append("Keyless-only markets must meet 10s end-to-end budget")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            logger.error(f"Failed to validate budget compliance: {e}")
            return False, [f"Budget validation failed: {str(e)}"]
    
    def get_validation_summary(self, report: ValidationReport) -> str:
        """Get a human-readable validation summary"""
        try:
            summary_parts = []
            
            # Overall status
            status_emoji = {
                ValidationResult.PASS: "✅",
                ValidationResult.WARNING: "⚠️",
                ValidationResult.FAIL: "❌"
            }
            
            summary_parts.append(f"{status_emoji[report.overall_status]} Overall Status: {report.overall_status.value.upper()}")
            
            # Lane statuses
            summary_parts.append("\nLane Statuses:")
            for lane, status in report.lane_validations.items():
                emoji = status_emoji[status]
                lane_name = self.required_lanes.get(lane, {}).get("description", lane)
                summary_parts.append(f"  {emoji} {lane_name}: {status.value.upper()}")
            
            # Errors
            if report.errors:
                summary_parts.append("\nErrors:")
                for error in report.errors:
                    summary_parts.append(f"  ❌ {error}")
            
            # Warnings
            if report.warnings:
                summary_parts.append("\nWarnings:")
                for warning in report.warnings:
                    summary_parts.append(f"  ⚠️ {warning}")
            
            # Recommendations
            if report.recommendations:
                summary_parts.append("\nRecommendations:")
                for rec in report.recommendations:
                    summary_parts.append(f"  💡 {rec}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate validation summary: {e}")
            return f"Failed to generate summary: {str(e)}"

# Global validator instance
_validator: Optional[ProviderKeyValidator] = None

def get_provider_key_validator() -> ProviderKeyValidator:
    """Get the global provider key validator"""
    global _validator
    if _validator is None:
        _validator = ProviderKeyValidator()
    return _validator

def validate_provider_keys(keyless_fallbacks_enabled: bool = True) -> ValidationReport:
    """Convenience function to validate provider keys"""
    validator = get_provider_key_validator()
    return validator.validate_provider_keys(keyless_fallbacks_enabled)
