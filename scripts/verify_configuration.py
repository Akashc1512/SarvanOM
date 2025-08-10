#!/usr/bin/env python3
"""
Configuration Verification Script

This script verifies that the configuration management system is working correctly
and that all required environment variables are set for the current environment.

Usage:
    python scripts/verify_configuration.py [environment]

Examples:
    python scripts/verify_configuration.py development
    python scripts/verify_configuration.py testing
    python scripts/verify_configuration.py staging
    python scripts/verify_configuration.py production
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import structlog, fallback to standard logging
try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    # Fallback to standard logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from shared.core.config.environment_manager import EnvironmentManager, Environment


class ConfigurationVerifier:
    """Verifies configuration loading and validation."""

    def __init__(self, environment: str = None):
        """Initialize the configuration verifier."""
        self.environment = environment or os.getenv("APP_ENV", "development")
        self.verification_results = []
        self.errors = []
        self.warnings = []

    def verify_configuration(self) -> bool:
        """Run all configuration verification checks."""
        print(f"\n{'='*60}")
        print(f"🔍 CONFIGURATION VERIFICATION")
        print(f"{'='*60}")
        print(f"📋 Environment: {self.environment.upper()}")
        print(f"{'='*60}")

        try:
            # Test 1: Environment Manager Initialization
            self._test_environment_manager()

            # Test 2: Configuration Loading
            self._test_configuration_loading()

            # Test 3: Environment Variable Loading
            self._test_environment_variables()

            # Test 4: Configuration File Loading
            self._test_configuration_files()

            # Test 5: Validation Rules
            self._test_validation_rules()

            # Test 6: Security Checks
            self._test_security_checks()

            # Test 7: Performance Settings
            self._test_performance_settings()

            # Test 8: Feature Flags
            self._test_feature_flags()

            # Print results
            self._print_results()

            return len(self.errors) == 0

        except Exception as e:
            print(f"❌ Configuration verification failed: {e}")
            return False

    def _test_environment_manager(self) -> None:
        """Test environment manager initialization."""
        try:
            print("\n🔧 Testing Environment Manager...")

            # Test with explicit environment
            env_manager = EnvironmentManager(self.environment)

            # Verify environment is set correctly
            if env_manager.environment.value != self.environment.lower():
                self.errors.append(
                    f"Environment mismatch: expected {self.environment}, got {env_manager.environment.value}"
                )
            else:
                print(
                    f"✅ Environment manager initialized for {env_manager.environment.value}"
                )

            # Verify configuration is loaded
            config = env_manager.get_config()
            if config.name != self.environment.lower():
                self.errors.append(
                    f"Configuration name mismatch: expected {self.environment}, got {config.name}"
                )
            else:
                print(f"✅ Configuration loaded: {config.name}")

            self.verification_results.append("Environment Manager Initialization")

        except Exception as e:
            self.errors.append(f"Environment manager initialization failed: {e}")

    def _test_configuration_loading(self) -> None:
        """Test configuration loading from various sources."""
        try:
            print("\n📄 Testing Configuration Loading...")

            env_manager = EnvironmentManager(self.environment)
            config = env_manager.get_config()

            # Check that required fields are present
            required_fields = [
                "name",
                "debug",
                "testing",
                "log_level",
                "database_url",
                "redis_url",
                "rate_limit_per_minute",
                "max_request_size_mb",
            ]

            for field in required_fields:
                if not hasattr(config, field):
                    self.errors.append(f"Missing required configuration field: {field}")
                else:
                    print(f"✅ Configuration field present: {field}")

            self.verification_results.append("Configuration Loading")

        except Exception as e:
            self.errors.append(f"Configuration loading failed: {e}")

    def _test_environment_variables(self) -> None:
        """Test environment variable loading."""
        try:
            print("\n🌍 Testing Environment Variable Loading...")

            # Test APP_ENV variable
            app_env = os.getenv("APP_ENV")
            if app_env:
                print(f"✅ APP_ENV is set: {app_env}")
            else:
                self.warnings.append("APP_ENV not set, using default 'development'")

            # Test database configuration
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                print(f"✅ DATABASE_URL is set: {database_url[:20]}...")
            else:
                if self.environment in ["production", "staging"]:
                    self.errors.append(
                        "DATABASE_URL is required for production/staging environments"
                    )
                else:
                    self.warnings.append("DATABASE_URL not set, using default SQLite")

            # Test Redis configuration
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                print(f"✅ REDIS_URL is set: {redis_url[:20]}...")
            else:
                if self.environment in ["production", "staging"]:
                    self.errors.append(
                        "REDIS_URL is required for production/staging environments"
                    )
                else:
                    self.warnings.append("REDIS_URL not set, using default localhost")

            # Test AI provider configuration
            openai_key = os.getenv("OPENAI_API_KEY")
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")

            if openai_key or anthropic_key:
                print("✅ AI provider API key is set")
            else:
                if self.environment in ["production", "staging"]:
                    self.errors.append(
                        "At least one AI provider API key is required for production/staging"
                    )
                else:
                    self.warnings.append(
                        "No AI provider API keys set, using mock responses"
                    )

            self.verification_results.append("Environment Variable Loading")

        except Exception as e:
            self.errors.append(f"Environment variable loading failed: {e}")

    def _test_configuration_files(self) -> None:
        """Test configuration file loading."""
        try:
            print("\n📁 Testing Configuration File Loading...")

            config_dir = project_root / "config"
            if not config_dir.exists():
                self.warnings.append(f"Configuration directory not found: {config_dir}")
                return

            # Check for environment-specific config files
            config_files = [
                config_dir / f"{self.environment}.yaml",
                config_dir / f"{self.environment}.yml",
                config_dir / f"{self.environment}.json",
            ]

            found_config = None
            for config_file in config_files:
                if config_file.exists():
                    found_config = config_file
                    break

            if found_config:
                print(f"✅ Configuration file found: {found_config.name}")
            else:
                self.warnings.append(
                    f"No configuration file found for environment: {self.environment}"
                )

            self.verification_results.append("Configuration File Loading")

        except Exception as e:
            self.errors.append(f"Configuration file loading failed: {e}")

    def _test_validation_rules(self) -> None:
        """Test configuration validation rules."""
        try:
            print("\n✅ Testing Configuration Validation...")

            env_manager = EnvironmentManager(self.environment)
            config = env_manager.get_config()

            # Test environment-specific validation rules
            if self.environment == "production":
                if config.debug:
                    self.errors.append("DEBUG should be False in production")
                if config.mock_ai_responses:
                    self.errors.append(
                        "MOCK_AI_RESPONSES should be False in production"
                    )
                if config.skip_authentication:
                    self.errors.append(
                        "SKIP_AUTHENTICATION should be False in production"
                    )
                if config.enable_debug_endpoints:
                    self.errors.append(
                        "ENABLE_DEBUG_ENDPOINTS should be False in production"
                    )
                if not config.database_url:
                    self.errors.append("DATABASE_URL is required for production")
                if not config.redis_url:
                    self.errors.append("REDIS_URL is required for production")
                if not config.jwt_secret_key:
                    self.errors.append("JWT_SECRET_KEY is required for production")

            elif self.environment == "staging":
                if config.debug:
                    self.errors.append("DEBUG should be False in staging")
                if config.mock_ai_responses:
                    self.errors.append("MOCK_AI_RESPONSES should be False in staging")
                if config.skip_authentication:
                    self.errors.append("SKIP_AUTHENTICATION should be False in staging")
                if config.enable_debug_endpoints:
                    self.errors.append(
                        "ENABLE_DEBUG_ENDPOINTS should be False in staging"
                    )
                if not config.database_url:
                    self.errors.append("DATABASE_URL is required for staging")
                if not config.redis_url:
                    self.errors.append("REDIS_URL is required for staging")
                if not config.jwt_secret_key:
                    self.errors.append("JWT_SECRET_KEY is required for staging")

            elif self.environment == "testing":
                if not config.mock_ai_responses:
                    self.errors.append("MOCK_AI_RESPONSES should be True in testing")
                if not config.skip_authentication:
                    self.errors.append("SKIP_AUTHENTICATION should be True in testing")
                if not config.test_mode:
                    self.errors.append("TEST_MODE should be True in testing")

            print("✅ Configuration validation completed")
            self.verification_results.append("Configuration Validation")

        except Exception as e:
            self.errors.append(f"Configuration validation failed: {e}")

    def _test_security_checks(self) -> None:
        """Test security-related configuration."""
        try:
            print("\n🔒 Testing Security Configuration...")

            env_manager = EnvironmentManager(self.environment)
            config = env_manager.get_config()

            # Check for hardcoded secrets in development
            if self.environment == "development":
                if (
                    config.jwt_secret_key
                    and config.jwt_secret_key != "dev-secret-key-change-in-production"
                ):
                    self.warnings.append(
                        "JWT_SECRET_KEY should use default dev value in development"
                    )

            # Check for secure defaults
            if self.environment in ["production", "staging"]:
                if not config.security_headers_enabled:
                    self.warnings.append(
                        "SECURITY_HEADERS_ENABLED should be True in production/staging"
                    )
                if not config.audit_log_enabled:
                    self.warnings.append(
                        "AUDIT_LOG_ENABLED should be True in production/staging"
                    )
                if not config.backup_enabled:
                    self.warnings.append(
                        "BACKUP_ENABLED should be True in production/staging"
                    )

            print("✅ Security configuration checks completed")
            self.verification_results.append("Security Configuration")

        except Exception as e:
            self.errors.append(f"Security configuration checks failed: {e}")

    def _test_performance_settings(self) -> None:
        """Test performance-related configuration."""
        try:
            print("\n⚡ Testing Performance Configuration...")

            env_manager = EnvironmentManager(self.environment)
            config = env_manager.get_config()

            # Check rate limiting
            if config.rate_limit_per_minute < 1:
                self.errors.append("RATE_LIMIT_PER_MINUTE must be at least 1")
            elif config.rate_limit_per_minute > 10000:
                self.warnings.append(
                    "RATE_LIMIT_PER_MINUTE is very high, consider reducing"
                )

            # Check request size limits
            if config.max_request_size_mb < 1:
                self.errors.append("MAX_REQUEST_SIZE_MB must be at least 1")
            elif config.max_request_size_mb > 100:
                self.warnings.append(
                    "MAX_REQUEST_SIZE_MB is very high, consider reducing"
                )

            # Check agent timeouts
            if config.agent_timeout_seconds < 1:
                self.errors.append("AGENT_TIMEOUT_SECONDS must be at least 1")
            elif config.agent_timeout_seconds > 300:
                self.warnings.append(
                    "AGENT_TIMEOUT_SECONDS is very high, consider reducing"
                )

            print("✅ Performance configuration checks completed")
            self.verification_results.append("Performance Configuration")

        except Exception as e:
            self.errors.append(f"Performance configuration checks failed: {e}")

    def _test_feature_flags(self) -> None:
        """Test feature flag configuration."""
        try:
            print("\n🚩 Testing Feature Flags...")

            env_manager = EnvironmentManager(self.environment)
            config = env_manager.get_config()

            # Check feature flags
            enabled_features = [
                name for name, enabled in config.features.items() if enabled
            ]
            disabled_features = [
                name for name, enabled in config.features.items() if not enabled
            ]

            print(f"✅ Enabled features: {len(enabled_features)}")
            print(f"✅ Disabled features: {len(disabled_features)}")

            # Environment-specific feature checks
            if self.environment == "production":
                if config.features.get("admin_panel", False):
                    self.warnings.append("ADMIN_PANEL should be disabled in production")

            elif self.environment == "testing":
                if config.features.get("streaming", False):
                    self.warnings.append("STREAMING should be disabled in testing")
                if config.features.get("websockets", False):
                    self.warnings.append("WEBSOCKETS should be disabled in testing")

            self.verification_results.append("Feature Flags")

        except Exception as e:
            self.errors.append(f"Feature flag checks failed: {e}")

    def _print_results(self) -> None:
        """Print verification results."""
        print(f"\n{'='*60}")
        print(f"📊 VERIFICATION RESULTS")
        print(f"{'='*60}")

        # Print successful verifications
        if self.verification_results:
            print(f"\n✅ Successful Verifications ({len(self.verification_results)}):")
            for result in self.verification_results:
                print(f"   • {result}")

        # Print warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        # Print errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        # Print summary
        print(f"\n{'='*60}")
        if self.errors:
            print(f"❌ CONFIGURATION VERIFICATION FAILED")
            print(f"   Please fix the errors above before proceeding.")
            print(f"   Total errors: {len(self.errors)}")
        else:
            print(f"✅ CONFIGURATION VERIFICATION PASSED")
            print(f"   All configuration checks completed successfully.")

        if self.warnings:
            print(f"   Warnings: {len(self.warnings)} (review recommended)")

        print(f"{'='*60}\n")


def main():
    """Main function to run configuration verification."""
    # Get environment from command line argument or use default
    environment = sys.argv[1] if len(sys.argv) > 1 else None

    # Create verifier and run checks
    verifier = ConfigurationVerifier(environment)
    success = verifier.verify_configuration()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
