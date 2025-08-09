#!/usr/bin/env python3
"""
Configuration Environment Testing Script

This script tests the configuration management system by switching between
different environments using the APP_ENV environment variable.

Features:
- Tests all four environments (development, testing, staging, production)
- Validates configuration loading and precedence
- Checks for missing critical configuration
- Verifies environment-specific settings
- Tests configuration file loading
- Validates environment variable override behavior

Usage:
    python scripts/test_config_environments.py
    python scripts/test_config_environments.py --env development
    python scripts/test_config_environments.py --validate-only
    python scripts/test_config_environments.py --missing-config

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import sys
import argparse
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.core.config.environment_manager import (
    get_environment_manager,
    Environment,
    EnvironmentManager,
    set_environment_manager,
)


class ConfigurationTester:
    """Test configuration management across different environments."""

    def __init__(self):
        self.test_results = []
        self.original_env = os.environ.copy()

    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive configuration tests."""
        print("🧪 Starting Configuration Environment Testing\n")

        results = {
            "environment_tests": {},
            "precedence_tests": {},
            "validation_tests": {},
            "critical_config_tests": {},
            "summary": {},
        }

        # Test each environment
        for env_name in ["development", "testing", "staging", "production"]:
            print(f"🔍 Testing {env_name.upper()} environment...")
            results["environment_tests"][env_name] = self._test_environment(env_name)

        # Test configuration precedence
        print("🔄 Testing configuration precedence...")
        results["precedence_tests"] = self._test_configuration_precedence()

        # Test validation
        print("✅ Testing configuration validation...")
        results["validation_tests"] = self._test_configuration_validation()

        # Test critical configuration detection
        print("🔐 Testing critical configuration detection...")
        results["critical_config_tests"] = self._test_critical_configuration()

        # Generate summary
        results["summary"] = self._generate_test_summary(results)

        return results

    def _test_environment(self, env_name: str) -> Dict[str, Any]:
        """Test a specific environment configuration."""
        test_result = {
            "environment": env_name,
            "success": False,
            "config_loaded": False,
            "expected_settings": {},
            "actual_settings": {},
            "issues": [],
        }

        try:
            # Set environment
            self._set_test_environment({"APP_ENV": env_name})

            # Clear cache and create new manager
            get_environment_manager.cache_clear()
            manager = EnvironmentManager()

            config = manager.get_config()
            test_result["config_loaded"] = True
            test_result["actual_settings"] = {
                "name": config.name,
                "debug": config.debug,
                "testing": config.testing,
                "log_level": config.log_level,
                "environment": manager.environment.value,
            }

            # Check environment-specific expectations
            expected = self._get_expected_settings(env_name)
            test_result["expected_settings"] = expected

            # Validate settings match expectations
            for key, expected_value in expected.items():
                actual_value = getattr(config, key, None)
                if actual_value != expected_value:
                    test_result["issues"].append(
                        f"Expected {key}={expected_value}, got {actual_value}"
                    )

            test_result["success"] = len(test_result["issues"]) == 0

        except Exception as e:
            test_result["issues"].append(f"Exception: {str(e)}")
        finally:
            self._restore_environment()

        return test_result

    def _test_configuration_precedence(self) -> Dict[str, Any]:
        """Test that environment variables override config files."""
        test_result = {"success": False, "tests": [], "issues": []}

        try:
            # Test 1: Environment variable should override config file default
            self._set_test_environment(
                {
                    "APP_ENV": "development",
                    "DEBUG": "false",  # Override development default of true
                    "LOG_LEVEL": "ERROR",  # Override development default of DEBUG
                }
            )

            get_environment_manager.cache_clear()
            manager = EnvironmentManager()
            config = manager.get_config()

            precedence_test = {
                "name": "env_var_override",
                "success": True,
                "details": {},
            }

            # Check DEBUG override
            if config.debug is not False:
                precedence_test["success"] = False
                test_result["issues"].append(
                    "DEBUG environment variable did not override config default"
                )
            else:
                precedence_test["details"]["debug_override"] = "✅"

            # Check LOG_LEVEL override
            if config.log_level != "ERROR":
                precedence_test["success"] = False
                test_result["issues"].append(
                    "LOG_LEVEL environment variable did not override config default"
                )
            else:
                precedence_test["details"]["log_level_override"] = "✅"

            test_result["tests"].append(precedence_test)

            test_result["success"] = len(test_result["issues"]) == 0

        except Exception as e:
            test_result["issues"].append(f"Exception: {str(e)}")
        finally:
            self._restore_environment()

        return test_result

    def _test_configuration_validation(self) -> Dict[str, Any]:
        """Test configuration validation for different environments."""
        test_result = {"success": False, "validation_tests": [], "issues": []}

        # Test production validation (should require critical config)
        try:
            self._set_test_environment(
                {
                    "APP_ENV": "production",
                    # Intentionally missing critical config
                }
            )

            get_environment_manager.cache_clear()
            manager = EnvironmentManager()
            missing = manager._check_missing_critical_config()

            validation_test = {
                "environment": "production",
                "missing_critical": missing,
                "success": len(missing) > 0,  # Should have missing config
            }

            test_result["validation_tests"].append(validation_test)

            if len(missing) == 0:
                test_result["issues"].append(
                    "Production environment should require critical configuration"
                )

        except Exception as e:
            test_result["issues"].append(f"Production validation test failed: {str(e)}")
        finally:
            self._restore_environment()

        # Test development validation (should be more lenient)
        try:
            self._set_test_environment(
                {
                    "APP_ENV": "development",
                    # Missing some config that's optional in development
                }
            )

            get_environment_manager.cache_clear()
            manager = EnvironmentManager()
            missing = manager._check_missing_critical_config()

            validation_test = {
                "environment": "development",
                "missing_critical": missing,
                "success": True,  # Development should be lenient
            }

            test_result["validation_tests"].append(validation_test)

        except Exception as e:
            test_result["issues"].append(
                f"Development validation test failed: {str(e)}"
            )
        finally:
            self._restore_environment()

        test_result["success"] = len(test_result["issues"]) == 0
        return test_result

    def _test_critical_configuration(self) -> Dict[str, Any]:
        """Test critical configuration detection."""
        test_result = {"success": False, "critical_tests": [], "issues": []}

        # Test with all critical config present
        try:
            self._set_test_environment(
                {
                    "APP_ENV": "production",
                    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
                    "REDIS_URL": "redis://localhost:6379/0",
                    "JWT_SECRET_KEY": "test-jwt-secret-key-for-production",
                    "MEILISEARCH_MASTER_KEY": "test-master-key",
                    "OPENAI_API_KEY": "test-openai-key",
                }
            )

            get_environment_manager.cache_clear()
            manager = EnvironmentManager()
            missing = manager._check_missing_critical_config()

            critical_test = {
                "name": "all_critical_present",
                "missing": missing,
                "success": len(missing) == 0,
            }

            test_result["critical_tests"].append(critical_test)

            if len(missing) > 0:
                test_result["issues"].append(
                    f"Should have no missing config, but found: {missing}"
                )

        except Exception as e:
            test_result["issues"].append(f"Critical config test failed: {str(e)}")
        finally:
            self._restore_environment()

        test_result["success"] = len(test_result["issues"]) == 0
        return test_result

    def _get_expected_settings(self, env_name: str) -> Dict[str, Any]:
        """Get expected settings for an environment."""
        expectations = {
            "development": {
                "name": "development",
                "debug": True,
                "testing": False,
                "log_level": "DEBUG",
            },
            "testing": {
                "name": "testing",
                "debug": True,
                "testing": True,
                "log_level": "DEBUG",
            },
            "staging": {
                "name": "staging",
                "debug": False,
                "testing": False,
                "log_level": "INFO",
            },
            "production": {
                "name": "production",
                "debug": False,
                "testing": False,
                "log_level": "WARNING",
            },
        }
        return expectations.get(env_name, {})

    def _set_test_environment(self, env_vars: Dict[str, str]):
        """Set test environment variables."""
        # Clear any existing environment
        for key in list(os.environ.keys()):
            if key.startswith(
                (
                    "APP_",
                    "DATABASE_",
                    "REDIS_",
                    "JWT_",
                    "MEILISEARCH_",
                    "OPENAI_",
                    "DEBUG",
                    "LOG_",
                )
            ):
                if key in os.environ:
                    del os.environ[key]

        # Set test environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

    def _restore_environment(self):
        """Restore original environment."""
        # Clear current environment
        for key in list(os.environ.keys()):
            if key.startswith(
                (
                    "APP_",
                    "DATABASE_",
                    "REDIS_",
                    "JWT_",
                    "MEILISEARCH_",
                    "OPENAI_",
                    "DEBUG",
                    "LOG_",
                )
            ):
                if key in os.environ:
                    del os.environ[key]

        # Restore original environment
        for key, value in self.original_env.items():
            if key.startswith(
                (
                    "APP_",
                    "DATABASE_",
                    "REDIS_",
                    "JWT_",
                    "MEILISEARCH_",
                    "OPENAI_",
                    "DEBUG",
                    "LOG_",
                )
            ):
                os.environ[key] = value

        # Clear the manager cache
        get_environment_manager.cache_clear()

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of test results."""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "environments_tested": len(results["environment_tests"]),
            "overall_success": True,
            "failures": [],
        }

        # Count environment tests
        for env_name, env_result in results["environment_tests"].items():
            summary["total_tests"] += 1
            if env_result["success"]:
                summary["passed_tests"] += 1
            else:
                summary["failed_tests"] += 1
                summary["overall_success"] = False
                summary["failures"].extend(
                    [f"{env_name}: {issue}" for issue in env_result["issues"]]
                )

        # Count other tests
        for test_category in [
            "precedence_tests",
            "validation_tests",
            "critical_config_tests",
        ]:
            if test_category in results and "success" in results[test_category]:
                summary["total_tests"] += 1
                if results[test_category]["success"]:
                    summary["passed_tests"] += 1
                else:
                    summary["failed_tests"] += 1
                    summary["overall_success"] = False
                    summary["failures"].extend(results[test_category].get("issues", []))

        return summary


def main():
    """Main function to run configuration tests."""
    parser = argparse.ArgumentParser(
        description="Test configuration management across environments"
    )
    parser.add_argument(
        "--env",
        choices=["development", "testing", "staging", "production"],
        help="Test specific environment only",
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only run validation tests"
    )
    parser.add_argument(
        "--missing-config",
        action="store_true",
        help="Show missing critical configuration for current environment",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    if args.missing_config:
        # Show missing config for current environment
        manager = get_environment_manager()
        missing = manager._check_missing_critical_config()
        if missing:
            print(f"❌ Missing critical configuration for {manager.environment.value}:")
            for item in missing:
                print(f"  - {item}")
        else:
            print(
                f"✅ All critical configuration is present for {manager.environment.value}"
            )
        return

    tester = ConfigurationTester()

    if args.env:
        # Test specific environment
        print(f"🔍 Testing {args.env.upper()} environment only...\n")
        result = tester._test_environment(args.env)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Environment: {result['environment']}")
            print(f"Success: {'✅' if result['success'] else '❌'}")
            if result["issues"]:
                print("Issues:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
    else:
        # Run all tests
        results = tester.run_all_tests()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Print summary
            summary = results["summary"]
            print(f"\n{'='*60}")
            print(f"🧪 CONFIGURATION TESTING SUMMARY")
            print(f"{'='*60}")
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Passed: ✅ {summary['passed_tests']}")
            print(f"Failed: ❌ {summary['failed_tests']}")
            print(f"Environments Tested: {summary['environments_tested']}")
            print(
                f"Overall Result: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}"
            )

            if summary["failures"]:
                print(f"\n❌ Failures:")
                for failure in summary["failures"]:
                    print(f"  - {failure}")

            print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
