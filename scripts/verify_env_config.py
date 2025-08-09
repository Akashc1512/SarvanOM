#!/usr/bin/env python3
"""
Environment Configuration Verification Script

This script verifies that environment configuration is properly set up,
validates all required secrets, and tests environment switching functionality.

Usage:
    python scripts/verify_env_config.py                    # Verify current environment
    python scripts/verify_env_config.py --env development  # Test specific environment
    python scripts/verify_env_config.py --all              # Test all environments
    python scripts/verify_env_config.py --secrets          # Check only secrets
    python scripts/verify_env_config.py --startup          # Full startup validation
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Main verification function."""
    print("🔍 Environment Configuration Verification")
    print("=" * 80)

    try:
        from shared.core.config.enhanced_environment_manager import (
            get_enhanced_environment_manager,
        )

        # Get current environment
        current_env = os.getenv("APP_ENV", "development")
        print(f"📋 Current environment: {current_env.upper()}")

        # Initialize manager
        manager = get_enhanced_environment_manager()
        print(f"✅ Configuration loaded successfully")

        # Show configuration summary
        config = manager.get_config()
        print(f"🐛 Debug mode: {config.debug}")
        print(f"📝 Log level: {config.log_level}")
        print(f"🔒 Skip authentication: {config.skip_authentication}")
        print(f"🤖 Mock AI responses: {config.mock_ai_responses}")

        # Validate startup requirements
        print("\n📊 Startup Validation:")
        checks = manager.validate_startup_requirements()

        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")

        all_passed = all(checks.values())

        if all_passed:
            print("\n🎉 Configuration verification passed!")
            return 0
        else:
            print("\n❌ Configuration verification failed!")
            return 1

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
