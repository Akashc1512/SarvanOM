#!/usr/bin/env python3
"""
Test script to isolate health endpoints encoding issue.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_health_endpoints():
    """Test health endpoints with proper encoding handling."""
    try:
        # Import the integration layer
        from services.api_gateway.integration_layer import UniversalKnowledgePlatformIntegration
        
        # Initialize integration layer
        integration = UniversalKnowledgePlatformIntegration()
        
        # Test system health
        print("Testing system health...")
        health_status = await integration.get_system_health()
        
        # Print health status with proper encoding
        print("Health Status:")
        print(f"Status: {health_status.get('status', 'unknown')}")
        print(f"Timestamp: {health_status.get('timestamp', 'unknown')}")
        
        if 'components' in health_status:
            print("Components:")
            for component, status in health_status['components'].items():
                print(f"  {component}: {status.get('status', 'unknown')}")
        
        print("✅ Health endpoints test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Health endpoints test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding for stdout
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    
    # Run the test
    result = asyncio.run(test_health_endpoints())
    sys.exit(0 if result else 1) 