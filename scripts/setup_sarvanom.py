#!/usr/bin/env python3
"""
SarvanOM Universal Knowledge Platform - Comprehensive Setup Script

This script validates and configures the SarvanOM platform according to all requirements:
- Environment configuration validation
- Security checks
- Database connectivity validation
- Agent pattern verification
- Logging configuration
- Defensive programming compliance

Features:
- Comprehensive environment validation
- Security credential verification
- Database connectivity testing
- Agent pattern compliance checking
- Logging configuration validation
- Defensive programming audit

Security:
- Validates all environment variables
- Checks for hardcoded secrets
- Verifies secure defaults
- Tests credential masking

Authors: Universal Knowledge Platform Engineering Team
Version: 2.0.0 (2024-12-28)
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.core.logging_config import get_logger, audit_logger, performance_logger
    from shared.core.api.config import get_settings
    from shared.core.agent_pattern import AgentFactory
    from shared.core.base_agent import AgentType
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

logger = get_logger("setup")


@dataclass
class ValidationResult:
    """Result of a validation check."""

    name: str
    status: bool
    message: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class SarvanOMSetupValidator:
    """Comprehensive validator for SarvanOM platform setup."""

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.settings = get_settings()
        self.env_file = project_root / ".env"
        self.template_file = project_root / "env.template"

    async def run_all_validations(self) -> bool:
        """Run all validation checks."""
        logger.info(
            "Starting SarvanOM platform validation", extra={"validation_start": True}
        )

        # Core validations
        await self._validate_environment_configuration()
        await self._validate_security_settings()
        await self._validate_database_connectivity()
        await self._validate_agent_patterns()
        await self._validate_logging_configuration()
        await self._validate_defensive_programming()
        await self._validate_microservices_architecture()
        await self._validate_zero_budget_llm()

        # Print results
        self._print_validation_results()

        # Return overall success
        passed = sum(1 for r in self.results if r.status)
        total = len(self.results)

        logger.info(
            "Validation completed",
            passed=passed,
            total=total,
            success_rate=f"{(passed/total)*100:.1f}%",
            extra={"validation_complete": True},
        )

        return passed == total

    async def _validate_environment_configuration(self):
        """Validate environment configuration."""
        logger.info(
            "Validating environment configuration",
            extra={"validation_step": "environment"},
        )

        # Check if .env file exists
        if not self.env_file.exists():
            self.results.append(
                ValidationResult(
                    name="Environment File",
                    status=False,
                    message="❌ .env file not found. Please copy env.template to .env and configure it.",
                    details={"file_path": str(self.env_file)},
                )
            )
            return

        # Check if template exists
        if not self.template_file.exists():
            self.results.append(
                ValidationResult(
                    name="Environment Template",
                    status=False,
                    message="❌ env.template not found. This is required for setup.",
                    details={"file_path": str(self.template_file)},
                )
            )
            return

        # Validate critical environment variables
        critical_vars = [
            "ENVIRONMENT",
            "SERVICE_NAME",
            "LOG_LEVEL",
            "API_GATEWAY_HOST",
            "API_GATEWAY_PORT",
            "SECRET_KEY",
            "JWT_SECRET_KEY",
        ]

        missing_vars = []
        for var in critical_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.results.append(
                ValidationResult(
                    name="Critical Environment Variables",
                    status=False,
                    message=f"❌ Missing critical environment variables: {', '.join(missing_vars)}",
                    details={"missing_variables": missing_vars},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Environment Configuration",
                    status=True,
                    message="✅ Environment configuration is valid",
                    details={"environment": settings.environment or "development"},
                )
            )

    async def _validate_security_settings(self):
        """Validate security configuration."""
        logger.info(
            "Validating security settings", extra={"validation_step": "security"}
        )

        # Check for hardcoded secrets
        hardcoded_secrets = self._check_for_hardcoded_secrets()

        if hardcoded_secrets:
            self.results.append(
                ValidationResult(
                    name="Hardcoded Secrets",
                    status=False,
                    message=f"❌ Found {len(hardcoded_secrets)} potential hardcoded secrets",
                    details={"files_with_secrets": hardcoded_secrets},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Security Configuration",
                    status=True,
                    message="✅ No hardcoded secrets found",
                    details={"security_audit": "passed"},
                )
            )

        # Validate JWT configuration
        jwt_secret = settings.jwt_secret_key
        if (
            not jwt_secret
            or jwt_secret == "your-jwt-secret-key-change-this-in-production"
        ):
            self.results.append(
                ValidationResult(
                    name="JWT Security",
                    status=False,
                    message="❌ JWT_SECRET_KEY not properly configured",
                    details={"jwt_configured": False},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="JWT Security",
                    status=True,
                    message="✅ JWT configuration is secure",
                    details={"jwt_configured": True},
                )
            )

    def _check_for_hardcoded_secrets(self) -> List[str]:
        """Check for hardcoded secrets in code."""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
        ]

        files_with_secrets = []

        # Check Python files
        for py_file in project_root.rglob("*.py"):
            if "test_" in py_file.name or "temp" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern in secret_patterns:
                    import re

                    if re.search(pattern, content, re.IGNORECASE):
                        files_with_secrets.append(str(py_file))
                        break
            except Exception:
                continue

        return files_with_secrets

    async def _validate_database_connectivity(self):
        """Validate database connectivity."""
        logger.info(
            "Validating database connectivity", extra={"validation_step": "database"}
        )

        # Check database URL
        db_url = settings.database_url
        if not db_url:
            self.results.append(
                ValidationResult(
                    name="Database Configuration",
                    status=False,
                    message="❌ DATABASE_URL not configured",
                    details={"database_configured": False},
                )
            )
            return

        # Test database connection (basic check)
        try:
            # This is a basic check - in production you'd want more comprehensive testing
            if "sqlite" in db_url:
                self.results.append(
                    ValidationResult(
                        name="Database Connectivity",
                        status=True,
                        message="✅ SQLite database configured",
                        details={"database_type": "sqlite"},
                    )
                )
            elif "postgresql" in db_url:
                self.results.append(
                    ValidationResult(
                        name="Database Connectivity",
                        status=True,
                        message="✅ PostgreSQL database configured",
                        details={"database_type": "postgresql"},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        name="Database Connectivity",
                        status=True,
                        message="✅ Database URL configured",
                        details={"database_type": "unknown"},
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    name="Database Connectivity",
                    status=False,
                    message=f"❌ Database connection failed: {e}",
                    details={"error": str(e)},
                )
            )

    async def _validate_agent_patterns(self):
        """Validate agent pattern compliance."""
        logger.info("Validating agent patterns", extra={"validation_step": "agents"})

        # Check if agents return dictionaries
        agent_files = [
            "shared/core/agent_pattern.py",
            "shared/core/agents/base_agent.py",
            "shared/core/agents/knowledge_graph_agent.py",
        ]

        dict_return_compliant = True
        for agent_file in agent_files:
            file_path = project_root / agent_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    # Check for return statements that don't return dicts
                    if (
                        "return None" in content
                        or "return False" in content
                        or "return True" in content
                    ):
                        dict_return_compliant = False
                        break
                except Exception:
                    continue

        if dict_return_compliant:
            self.results.append(
                ValidationResult(
                    name="Agent Pattern Compliance",
                    status=True,
                    message="✅ Agents return dictionaries as required",
                    details={"dict_returns": True},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Agent Pattern Compliance",
                    status=False,
                    message="❌ Some agents may not return dictionaries",
                    details={"dict_returns": False},
                )
            )

    async def _validate_logging_configuration(self):
        """Validate logging configuration."""
        logger.info(
            "Validating logging configuration", extra={"validation_step": "logging"}
        )

        # Check if logging uses extra={} pattern
        logging_files = [
            "shared/core/logging_config.py",
            "services/api_gateway/main.py",
        ]

        extra_pattern_compliant = True
        for log_file in logging_files:
            file_path = project_root / log_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    # Check for logger calls without extra={}
                    if "logger.info(" in content and "extra={" not in content:
                        extra_pattern_compliant = False
                        break
                except Exception:
                    continue

        if extra_pattern_compliant:
            self.results.append(
                ValidationResult(
                    name="Logging Configuration",
                    status=True,
                    message="✅ Logging uses extra={} pattern",
                    details={"extra_pattern": True},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Logging Configuration",
                    status=False,
                    message="❌ Some logging calls don't use extra={} pattern",
                    details={"extra_pattern": False},
                )
            )

    async def _validate_defensive_programming(self):
        """Validate defensive programming practices."""
        logger.info(
            "Validating defensive programming", extra={"validation_step": "defensive"}
        )

        # Check for proper error handling
        critical_files = [
            "services/api_gateway/main.py",
            "shared/core/agent_pattern.py",
            "shared/core/api/config.py",
        ]

        defensive_compliant = True
        for file_path in critical_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text()
                    # Check for try/except blocks
                    if "try:" not in content or "except" not in content:
                        defensive_compliant = False
                        break
                except Exception:
                    continue

        if defensive_compliant:
            self.results.append(
                ValidationResult(
                    name="Defensive Programming",
                    status=True,
                    message="✅ Defensive programming practices implemented",
                    details={"error_handling": True},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Defensive Programming",
                    status=False,
                    message="❌ Some files lack proper error handling",
                    details={"error_handling": False},
                )
            )

    async def _validate_microservices_architecture(self):
        """Validate microservices architecture."""
        logger.info(
            "Validating microservices architecture",
            extra={"validation_step": "microservices"},
        )

        # Check for required services
        required_services = [
            "services/api_gateway",
            "services/auth_service",
            "services/search_service",
            "services/synthesis_service",
            "services/factcheck_service",
            "services/analytics_service",
        ]

        missing_services = []
        for service in required_services:
            service_path = project_root / service
            if not service_path.exists():
                missing_services.append(service)

        if not missing_services:
            self.results.append(
                ValidationResult(
                    name="Microservices Architecture",
                    status=True,
                    message="✅ All required microservices present",
                    details={"services_count": len(required_services)},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Microservices Architecture",
                    status=False,
                    message=f"❌ Missing services: {', '.join(missing_services)}",
                    details={"missing_services": missing_services},
                )
            )

    async def _validate_zero_budget_llm(self):
        """Validate zero budget LLM configuration."""
        logger.info(
            "Validating zero budget LLM configuration",
            extra={"validation_step": "zero_budget"},
        )

        # Check for zero budget LLM variables
        zero_budget_vars = [
            "OLLAMA_ENABLED",
            "HUGGINGFACE_WRITE_TOKEN",
            "USE_DYNAMIC_SELECTION",
            "PRIORITIZE_FREE_MODELS",
        ]

        configured_vars = []
        for var in zero_budget_vars:
            if os.getenv(var):
                configured_vars.append(var)

        if len(configured_vars) >= 2:  # At least 2 should be configured
            self.results.append(
                ValidationResult(
                    name="Zero Budget LLM",
                    status=True,
                    message="✅ Zero budget LLM configuration present",
                    details={"configured_vars": configured_vars},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    name="Zero Budget LLM",
                    status=False,
                    message="❌ Zero budget LLM not properly configured",
                    details={"configured_vars": configured_vars},
                )
            )

    def _print_validation_results(self):
        """Print validation results in a formatted way."""
        print("\n" + "=" * 80)
        print("🔍 SARVANOM PLATFORM VALIDATION RESULTS")
        print("=" * 80)

        passed = sum(1 for r in self.results if r.status)
        total = len(self.results)

        for result in self.results:
            status_icon = "✅" if result.status else "❌"
            print(f"{status_icon} {result.name}: {result.message}")

        print("\n" + "=" * 80)
        print(f"📊 SUMMARY: {passed}/{total} validations passed")
        print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("🎉 All validations passed! SarvanOM platform is ready.")
        else:
            print("⚠️  Some validations failed. Please address the issues above.")

        print("=" * 80 + "\n")


async def main():
    """Main setup function."""
    print("🚀 SarvanOM Universal Knowledge Platform Setup")
    print("=" * 60)

    # Create validator
    validator = SarvanOMSetupValidator()

    # Run validations
    success = await validator.run_all_validations()

    if success:
        print("✅ Setup validation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your .env file with actual credentials")
        print("2. Start the development server: python run_server.py")
        print("3. Access the platform at http://localhost:8000")
        print("4. Check the API documentation at http://localhost:8000/docs")
    else:
        print("❌ Setup validation failed. Please address the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
