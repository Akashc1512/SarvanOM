#!/usr/bin/env python3
"""
Logging Deployment Setup Script

This script sets up the unified logging system for deployment across different environments.
It creates configuration profiles, validates settings, and provides deployment verification.

Usage:
    python scripts/setup_logging_deployment.py --environment production --service-name sarvanom-api
    python scripts/setup_logging_deployment.py --create-configs
    python scripts/setup_logging_deployment.py --validate-all
    python scripts/setup_logging_deployment.py --test-environment development

Features:
- Environment-specific configuration creation
- Configuration validation and testing
- Deployment verification
- Performance and security validation
- Integration testing
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from shared.core.logging_configuration_manager import (
        LoggingConfigurationManager,
        LoggingConfigProfile,
        Environment,
        LogLevel,
        LogFormat,
        initialize_logging_for_environment,
    )
    from shared.core.unified_logging import get_logger, setup_logging
    from shared.core.production_logging import (
        setup_production_logging,
        get_production_log_collector,
        get_health_check_logger,
        get_security_event_logger,
    )

    LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import logging modules: {e}")
    LOGGING_AVAILABLE = False


def create_production_configs():
    """Create production-ready configuration files."""
    print("🔧 Creating Production Configuration Files")
    print("=" * 50)

    if not LOGGING_AVAILABLE:
        print("❌ Logging modules not available")
        return False

    manager = LoggingConfigurationManager()

    # Create comprehensive configuration profiles
    configs = {
        "development": LoggingConfigProfile(
            service_name="sarvanom-dev",
            environment=Environment.DEVELOPMENT,
            log_level=LogLevel.DEBUG,
            log_format=LogFormat.TEXT,
            enable_metrics=False,
            enable_health_logging=True,
            enable_security_logging=False,
            enable_performance_monitoring=False,
            mask_sensitive_data=True,
            audit_enabled=False,
        ),
        "testing": LoggingConfigProfile(
            service_name="sarvanom-test",
            environment=Environment.TESTING,
            log_level=LogLevel.INFO,
            log_format=LogFormat.JSON,
            log_file="/tmp/sarvanom/test.log",
            enable_metrics=True,
            enable_health_logging=True,
            enable_security_logging=True,
            enable_performance_monitoring=True,
            mask_sensitive_data=True,
            audit_enabled=True,
            error_rate_threshold=10.0,  # Higher threshold for testing
            response_time_threshold=10000.0,
        ),
        "staging": LoggingConfigProfile(
            service_name="sarvanom-staging",
            environment=Environment.STAGING,
            log_level=LogLevel.INFO,
            log_format=LogFormat.JSON,
            log_file="/var/log/sarvanom/staging.log",
            max_file_size_mb=50,
            backup_count=10,
            enable_metrics=True,
            enable_health_logging=True,
            enable_security_logging=True,
            enable_performance_monitoring=True,
            mask_sensitive_data=True,
            audit_enabled=True,
            error_rate_threshold=5.0,
            response_time_threshold=5000.0,
            cache_hit_rate_threshold=75.0,
        ),
        "production": LoggingConfigProfile(
            service_name="sarvanom-prod",
            environment=Environment.PRODUCTION,
            log_level=LogLevel.INFO,
            log_format=LogFormat.JSON,
            log_file="/var/log/sarvanom/production.log",
            max_file_size_mb=200,
            backup_count=30,
            buffer_size=50000,
            flush_interval=1,
            enable_metrics=True,
            enable_health_logging=True,
            enable_security_logging=True,
            enable_performance_monitoring=True,
            mask_sensitive_data=True,
            log_user_data=False,
            audit_enabled=True,
            error_rate_threshold=2.0,
            response_time_threshold=3000.0,
            cache_hit_rate_threshold=80.0,
        ),
    }

    success_count = 0
    for env_name, config in configs.items():
        try:
            manager.save_profile(config, f"{env_name}.yaml")
            print(f"✅ Created {env_name} configuration")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to create {env_name} configuration: {e}")

    print(f"\n📊 Created {success_count}/{len(configs)} configuration files")
    return success_count == len(configs)


def validate_all_configurations():
    """Validate all configuration files."""
    print("🔍 Validating All Configuration Files")
    print("=" * 50)

    if not LOGGING_AVAILABLE:
        print("❌ Logging modules not available")
        return False

    manager = LoggingConfigurationManager()
    profiles = manager.list_available_profiles()

    if not profiles:
        print("⚠️ No configuration profiles found")
        return False

    validation_results = {}

    for profile_file in profiles:
        try:
            print(f"\n📋 Validating {profile_file}:")
            profile = manager.load_profile(profile_file)

            # Validate configuration
            errors = manager.validator.validate_profile(profile)
            warnings = manager.validator.validate_environment_consistency(profile)

            if errors:
                print(f"  ❌ Errors: {', '.join(errors)}")
                validation_results[profile_file] = False
            else:
                print(f"  ✅ Configuration valid")
                validation_results[profile_file] = True

            if warnings:
                print(f"  ⚠️ Warnings: {', '.join(warnings)}")

            # Display key settings
            print(f"  📊 Settings:")
            print(f"     Environment: {profile.environment.value}")
            print(f"     Log Level: {profile.log_level.value}")
            print(f"     Log Format: {profile.log_format.value}")
            print(f"     File Logging: {'Yes' if profile.log_file else 'No'}")
            print(
                f"     Production Features: {'Yes' if profile.enable_metrics else 'No'}"
            )

        except Exception as e:
            print(f"  ❌ Failed to load configuration: {e}")
            validation_results[profile_file] = False

    valid_count = sum(validation_results.values())
    total_count = len(validation_results)

    print(f"\n📊 Validation Results: {valid_count}/{total_count} configurations valid")

    return valid_count == total_count


async def test_environment_setup(environment: str):
    """Test logging setup for specific environment."""
    print(f"🧪 Testing {environment.upper()} Environment Setup")
    print("=" * 50)

    if not LOGGING_AVAILABLE:
        print("❌ Logging modules not available")
        return False

    try:
        # Initialize logging for environment
        initialize_logging_for_environment(
            environment=environment,
            service_name=f"test-{environment}",
            enable_monitoring=False,
        )

        logger = get_logger("deployment_test")

        # Test basic logging
        print("✅ Testing basic logging...")
        logger.debug("Debug message test", component="deployment_test")
        logger.info("Info message test", component="deployment_test")
        logger.warning("Warning message test", component="deployment_test")
        logger.error("Error message test", component="deployment_test")

        # Test structured logging
        print("✅ Testing structured logging...")
        logger.info(
            "Structured log test",
            environment=environment,
            request_id="test-req-123",
            user_id="test-user-456",
            metrics={"response_time": 150, "status": "success"},
            component="deployment_test",
        )

        # Test performance logging
        print("✅ Testing performance logging...")
        start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(0.1)
        end_time = asyncio.get_event_loop().time()

        logger.info(
            "Performance test completed",
            duration_ms=round((end_time - start_time) * 1000, 2),
            operation="test_operation",
            component="deployment_test",
        )

        # Test production features if environment supports it
        if environment in ["staging", "production"]:
            print("✅ Testing production features...")

            # Test metrics collection
            collector = get_production_log_collector()
            collector.collect_log_entry(
                "INFO",
                "Test metrics collection",
                request_id="metrics-test",
                duration_ms=200,
            )

            # Test health logging
            health_logger = get_health_check_logger()
            health_logger.log_health_check("test_service", "healthy", {"test": True})

            # Test security logging
            security_logger = get_security_event_logger()
            security_logger.log_authentication_attempt("test_user", True, "127.0.0.1")

        print(f"✅ {environment.upper()} environment test completed successfully")
        return True

    except Exception as e:
        print(f"❌ {environment.upper()} environment test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_deployment():
    """Verify logging deployment is ready for production."""
    print("🔍 Verifying Deployment Readiness")
    print("=" * 50)

    checks = []

    # Check configuration files exist
    manager = LoggingConfigurationManager()
    required_configs = [
        "development.yaml",
        "testing.yaml",
        "staging.yaml",
        "production.yaml",
    ]

    for config_file in required_configs:
        config_path = manager.config_dir / config_file
        if config_path.exists():
            checks.append(f"✅ {config_file} exists")
        else:
            checks.append(f"❌ {config_file} missing")

    # Check log directories for production
    log_dirs = ["/var/log/sarvanom", "/tmp/sarvanom"]
    for log_dir in log_dirs:
        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            checks.append(f"✅ Log directory {log_dir} accessible")
        except Exception as e:
            checks.append(f"⚠️ Log directory {log_dir} not accessible: {e}")

    # Check environment variables
    env_vars = ["LOG_LEVEL", "LOG_FORMAT", "SERVICE_NAME", "APP_ENV"]
    for var in env_vars:
        if os.getenv(var):
            checks.append(f"✅ Environment variable {var} set")
        else:
            checks.append(f"⚠️ Environment variable {var} not set (will use defaults)")

    # Display results
    for check in checks:
        print(f"  {check}")

    success_count = sum(1 for check in checks if check.startswith("✅"))
    total_count = len(checks)

    print(f"\n📊 Deployment Readiness: {success_count}/{total_count} checks passed")

    return success_count >= total_count * 0.8  # 80% success rate


def setup_logging_directories():
    """Set up logging directories with proper permissions."""
    print("📁 Setting Up Logging Directories")
    print("=" * 50)

    directories = ["/var/log/sarvanom", "/tmp/sarvanom", "logs", "config/logging"]

    created_count = 0
    for directory in directories:
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created/verified directory: {directory}")
            created_count += 1
        except Exception as e:
            print(f"⚠️ Could not create directory {directory}: {e}")

    print(f"\n📊 Directory Setup: {created_count}/{len(directories)} directories ready")
    return created_count == len(directories)


async def main():
    """Main deployment setup function."""
    parser = argparse.ArgumentParser(
        description="Setup unified logging system for deployment"
    )
    parser.add_argument(
        "--environment",
        "-e",
        choices=["development", "testing", "staging", "production"],
        help="Target environment for setup",
    )
    parser.add_argument(
        "--service-name",
        "-s",
        default="sarvanom",
        help="Service name for logging configuration",
    )
    parser.add_argument(
        "--create-configs",
        action="store_true",
        help="Create all environment configuration files",
    )
    parser.add_argument(
        "--validate-all", action="store_true", help="Validate all configuration files"
    )
    parser.add_argument(
        "--test-environment", "-t", help="Test logging setup for specific environment"
    )
    parser.add_argument(
        "--verify-deployment", action="store_true", help="Verify deployment readiness"
    )
    parser.add_argument(
        "--setup-directories", action="store_true", help="Set up logging directories"
    )

    args = parser.parse_args()

    print("🚀 Unified Logging Deployment Setup")
    print("=" * 80)

    if not LOGGING_AVAILABLE:
        print("❌ Logging modules not available. Please install dependencies.")
        return 1

    success = True

    try:
        # Set up directories first
        if args.setup_directories or not any(
            [
                args.create_configs,
                args.validate_all,
                args.test_environment,
                args.verify_deployment,
            ]
        ):
            success &= setup_logging_directories()

        # Create configuration files
        if args.create_configs:
            success &= create_production_configs()

        # Validate configurations
        if args.validate_all:
            success &= validate_all_configurations()

        # Test specific environment
        if args.test_environment:
            success &= await test_environment_setup(args.test_environment)

        # Verify deployment
        if args.verify_deployment:
            success &= verify_deployment()

        # Initialize specific environment
        if args.environment:
            print(f"\n🔧 Initializing {args.environment.upper()} Environment")
            print("=" * 50)

            initialize_logging_for_environment(
                environment=args.environment,
                service_name=args.service_name,
                enable_monitoring=True,
            )

            logger = get_logger("deployment")
            logger.info(
                "Logging system initialized for deployment",
                environment=args.environment,
                service_name=args.service_name,
                component="deployment_setup",
            )

            print(f"✅ {args.environment.upper()} environment ready for deployment")

        # Default action if no specific command
        if not any(
            [
                args.create_configs,
                args.validate_all,
                args.test_environment,
                args.verify_deployment,
                args.environment,
                args.setup_directories,
            ]
        ):
            print("\n🔧 Running Full Deployment Setup")
            print("=" * 50)

            success &= setup_logging_directories()
            success &= create_production_configs()
            success &= validate_all_configurations()
            success &= verify_deployment()

        print("\n" + "=" * 80)
        if success:
            print("🎉 LOGGING DEPLOYMENT SETUP COMPLETED SUCCESSFULLY!")
            print("✅ The unified logging system is ready for production deployment")
        else:
            print("⚠️ LOGGING DEPLOYMENT SETUP COMPLETED WITH WARNINGS")
            print("🔍 Review the output above for any issues that need attention")
        print("=" * 80)

        return 0 if success else 1

    except Exception as e:
        print(f"\n❌ Deployment setup failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
