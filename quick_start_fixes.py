#!/usr/bin/env python3
"""
Quick Start Script for Backend Fixes
One-command solution to install dependencies and test all fixes.

This script will:
1. Install missing dependencies
2. Run comprehensive tests
3. Provide detailed analysis
4. Give actionable recommendations

Usage:
    python quick_start_fixes.py
"""

import subprocess
import sys
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    logger.info(f"🔄 {description}")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False

async def main():
    """Main quick start function."""
    logger.info("🚀 Quick Start: Backend Fixes")
    logger.info("=" * 60)
    
    # Step 1: Install dependencies
    logger.info("📦 Step 1: Installing Dependencies")
    logger.info("-" * 40)
    
    install_success = run_command(
        f"{sys.executable} install_missing_deps.py",
        "Installing missing dependencies"
    )
    
    if not install_success:
        logger.error("❌ Dependency installation failed. Please check the errors above.")
        return
    
    # Step 2: Test if backend is running
    logger.info("\n🔍 Step 2: Checking Backend Status")
    logger.info("-" * 40)
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=5) as response:
                if response.status == 200:
                    logger.info("✅ Backend is running and healthy")
                else:
                    logger.warning(f"⚠️ Backend responded with status {response.status}")
    except Exception as e:
        logger.warning(f"⚠️ Backend not responding: {e}")
        logger.info("💡 Starting backend...")
        
        # Try to start backend
        start_success = run_command(
            f"{sys.executable} -m uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000 --reload",
            "Starting backend server"
        )
        
        if not start_success:
            logger.error("❌ Failed to start backend. Please start manually:")
            logger.error("   python -m uvicorn services.api-gateway.main:app --reload")
            return
    
    # Step 3: Run comprehensive tests
    logger.info("\n🧪 Step 3: Running Comprehensive Tests")
    logger.info("-" * 40)
    
    test_success = run_command(
        f"{sys.executable} test_production_fixes.py",
        "Running production tests"
    )
    
    if not test_success:
        logger.error("❌ Tests failed. Check the test output above.")
        return
    
    # Step 4: Summary and recommendations
    logger.info("\n📊 Step 4: Summary and Recommendations")
    logger.info("-" * 40)
    
    logger.info("✅ Quick start completed!")
    logger.info("\n💡 Next steps:")
    logger.info("1. Check the test results above")
    logger.info("2. Address any failed tests using the recommendations")
    logger.info("3. Monitor backend logs for any issues")
    logger.info("4. Run tests again after fixes: python test_production_fixes.py")
    
    logger.info("\n🔧 Useful commands:")
    logger.info("- Start backend: python -m uvicorn services.api-gateway.main:app --reload")
    logger.info("- Run tests: python test_production_fixes.py")
    logger.info("- Install deps: python install_missing_deps.py")
    logger.info("- Check health: curl http://localhost:8000/health")

if __name__ == "__main__":
    asyncio.run(main()) 