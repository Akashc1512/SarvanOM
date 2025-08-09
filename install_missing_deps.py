#!/usr/bin/env python3
"""
Install Missing Dependencies Script
Installs dependencies that might be missing and causing the critical issues.

This script will:
1. Check for missing packages
2. Install prometheus-client if missing
3. Install other optional dependencies
4. Verify installations
"""

import subprocess
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_package(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name: str) -> bool:
    """Install a package using pip."""
    try:
        logger.info(f"📦 Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install {package_name}: {e}")
        return False


def main():
    """Main installation function."""
    logger.info("🔧 Installing Missing Dependencies")
    logger.info("=" * 50)

    # List of packages to check and install
    packages_to_check = [
        ("prometheus_client", "prometheus-client"),
        ("websockets", "websockets"),
        ("aiohttp", "aiohttp"),
        ("anthropic", "anthropic"),
        ("openai", "openai"),
        ("redis", "redis"),
        ("psutil", "psutil"),
        ("python-dotenv", "python-dotenv"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("tenacity", "tenacity"),
        ("structlog", "structlog"),
    ]

    missing_packages = []
    installed_packages = []

    # Check which packages are missing
    logger.info("🔍 Checking for missing packages...")
    for module_name, package_name in packages_to_check:
        if check_package(module_name):
            logger.info(f"✅ {package_name}: Already installed")
        else:
            logger.warning(f"❌ {package_name}: Missing")
            missing_packages.append((module_name, package_name))

    if not missing_packages:
        logger.info("🎉 All required packages are already installed!")
        return

    # Install missing packages
    logger.info(f"\n📦 Installing {len(missing_packages)} missing packages...")
    for module_name, package_name in missing_packages:
        if install_package(package_name):
            installed_packages.append(package_name)
        else:
            logger.error(f"❌ Failed to install {package_name}")

    # Verify installations
    logger.info("\n🔍 Verifying installations...")
    for module_name, package_name in packages_to_check:
        if check_package(module_name):
            logger.info(f"✅ {package_name}: Verified")
        else:
            logger.error(f"❌ {package_name}: Still missing after installation")

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 INSTALLATION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"✅ Successfully installed: {len(installed_packages)} packages")
    logger.info(
        f"❌ Failed installations: {len(missing_packages) - len(installed_packages)} packages"
    )

    if installed_packages:
        logger.info(f"📦 Installed packages: {', '.join(installed_packages)}")

    # Critical packages check
    critical_packages = ["prometheus_client", "websockets", "aiohttp"]
    missing_critical = [pkg for pkg in critical_packages if not check_package(pkg)]

    if missing_critical:
        logger.error(
            f"❌ Critical packages still missing: {', '.join(missing_critical)}"
        )
        logger.error("These packages are required for the fixes to work properly.")
    else:
        logger.info("✅ All critical packages are available!")

    logger.info("\n💡 Next steps:")
    logger.info("1. Restart your backend server")
    logger.info("2. Run the comprehensive test: python test_comprehensive_fixes.py")
    logger.info("3. Check the logs for any remaining issues")


if __name__ == "__main__":
    main()
