#!/usr/bin/env python3
"""
Test script to verify backend startup
"""

import asyncio
import sys
import traceback

def test_import():
    """Test if the main app can be imported."""
    try:
        print("Testing app import...")
        from services.api_gateway.main import app
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        traceback.print_exc()
        return False

def test_server_start():
    """Test if the server can start."""
    try:
        print("Testing server startup...")
        import uvicorn
        from services.api_gateway.main import app
        
        # Try to start server in a separate thread
        import threading
        import time
        
        def start_server():
            uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Test if server is responding
        import httpx
        import asyncio
        
        async def test_health():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get('http://localhost:8000/health', timeout=5.0)
                    print(f"✅ Server responding: {response.status_code}")
                    return True
            except Exception as e:
                print(f"❌ Server not responding: {e}")
                return False
        
        result = asyncio.run(test_health())
        return result
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=== Backend Startup Test ===")
    
    # Test 1: Import
    if not test_import():
        print("❌ Import test failed")
        sys.exit(1)
    
    # Test 2: Server startup
    if not test_server_start():
        print("❌ Server startup test failed")
        sys.exit(1)
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    main() 