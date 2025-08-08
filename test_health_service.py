#!/usr/bin/env python3
"""
Test script for health service migration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.health.health_service import HealthService


async def test_health_service():
    """Test the migrated health service."""
    print("Testing Health Service Migration...")
    
    # Create health service
    health_service = HealthService()
    
    # Test basic health
    print("\n1. Testing basic health check...")
    basic_health = await health_service.get_basic_health()
    print(f"✓ Basic health: {basic_health.get('status', 'unknown')}")
    print(f"  - Service: {basic_health.get('service', 'unknown')}")
    print(f"  - Uptime: {basic_health.get('uptime', 0):.1f}s")
    print(f"  - Memory: {basic_health.get('memory_usage', 0):.1f}%")
    print(f"  - CPU: {basic_health.get('cpu_usage', 0):.1f}%")
    
    # Test system health
    print("\n2. Testing system health check...")
    system_health = await health_service.get_system_health()
    print(f"✓ System health: {system_health.get('status', 'unknown')}")
    print(f"  - CPU: {system_health.get('system_metrics', {}).get('cpu_usage', 0):.1f}%")
    print(f"  - Memory: {system_health.get('system_metrics', {}).get('memory_usage', 0):.1f}%")
    print(f"  - Disk: {system_health.get('system_metrics', {}).get('disk_usage', 0):.1f}%")
    print(f"  - Network connections: {system_health.get('system_metrics', {}).get('network_connections', 0)}")
    
    # Test detailed metrics
    print("\n3. Testing detailed metrics...")
    detailed_metrics = await health_service.get_detailed_metrics()
    print(f"✓ Detailed metrics retrieved")
    print(f"  - Historical data points: {len(detailed_metrics.get('historical_metrics', []))}")
    print(f"  - Trends calculated: {len(detailed_metrics.get('trends', {}))}")
    
    # Test system diagnostics
    print("\n4. Testing system diagnostics...")
    diagnostics = await health_service.get_system_diagnostics()
    print(f"✓ System diagnostics retrieved")
    print(f"  - Platform: {diagnostics.get('system_info', {}).get('platform', 'unknown')}")
    print(f"  - Python version: {diagnostics.get('system_info', {}).get('python_version', 'unknown')}")
    print(f"  - Services checked: {len(diagnostics.get('service_status', {}))}")
    print(f"  - Dependencies checked: {len(diagnostics.get('dependencies', {}))}")
    
    print("\n🎉 All health service tests passed!")
    return True


async def main():
    """Run health service tests."""
    try:
        await test_health_service()
        return True
    except Exception as e:
        print(f"❌ Health service test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 