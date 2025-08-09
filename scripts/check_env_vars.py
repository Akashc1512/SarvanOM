#!/usr/bin/env python3
"""
Environment Variable Checker for SarvanOM.

This script checks if all required environment variables are set
and validates the configuration system.
"""

import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_required_vars() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""

    app_env = os.getenv("APP_ENV", "development").lower()

    # Required variables for different environments
    required_vars = {
        "development": [
            "APP_ENV",
            "DATABASE_URL",
            "REDIS_URL",
            "MEILISEARCH_URL",
            "ARANGODB_URL",
        ],
        "testing": [
            "APP_ENV",
            "DATABASE_URL",
            "REDIS_URL",
            "MEILISEARCH_URL",
            "ARANGODB_URL",
        ],
        "staging": [
            "APP_ENV",
            "DATABASE_URL",
            "REDIS_URL",
            "MEILISEARCH_URL",
            "ARANGODB_URL",
            "JWT_SECRET_KEY",
        ],
        "production": [
            "APP_ENV",
            "DATABASE_URL",
            "REDIS_URL",
            "MEILISEARCH_URL",
            "ARANGODB_URL",
            "JWT_SECRET_KEY",
            "MEILISEARCH_MASTER_KEY",
        ],
    }

    if app_env not in required_vars:
        print(f"⚠️ Unknown environment '{app_env}', using development requirements")
        app_env = "development"

    missing_vars = []
    for var in required_vars[app_env]:
        if not os.getenv(var):
            missing_vars.append(var)

    return len(missing_vars) == 0, missing_vars


def check_security() -> List[str]:
    """Check security-related configuration."""
    warnings = []
    app_env = os.getenv("APP_ENV", "development").lower()

    # Check JWT secret
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        warnings.append("JWT_SECRET_KEY is not set")
    elif len(jwt_secret) < 32:
        warnings.append("JWT_SECRET_KEY should be at least 32 characters")

    # Check debug mode in production
    debug_mode = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]
    if app_env == "production" and debug_mode:
        warnings.append("DEBUG mode is enabled in production")

    return warnings


def main():
    """Main validation function."""
    print("🔍 Checking SarvanOM Environment Variables...")
    print("=" * 50)

    # Check required variables
    is_valid, missing_vars = check_required_vars()

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print()
    else:
        print("✅ All required environment variables are set")
        print()

    # Check security
    security_warnings = check_security()

    if security_warnings:
        print("⚠️ Security warnings:")
        for warning in security_warnings:
            print(f"  - {warning}")
        print()

    # Print current environment
    app_env = os.getenv("APP_ENV", "development")
    debug_mode = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]

    print("📋 Current Configuration:")
    print(f"  Environment: {app_env}")
    print(f"  Debug mode: {debug_mode}")
    print(f"  Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    print()

    # Final status
    if is_valid:
        print("✅ Environment validation passed!")
        if not security_warnings:
            print("✅ Security configuration looks good!")
        else:
            print("⚠️ Security warnings found - please review")
        return 0
    else:
        print("❌ Environment validation failed!")
        print("💡 Run 'python scripts/create_env_example.py' to create .env.example")
        print("💡 Copy .env.example to .env and fill in your values")
        return 1


if __name__ == "__main__":
    sys.exit(main())
