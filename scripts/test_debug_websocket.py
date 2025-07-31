#!/usr/bin/env python3
"""
Test Debug WebSocket Gateway
"""

import asyncio
import websockets
import json

async def test_debug_websocket():
    """Test debug WebSocket gateway."""
    print("🔍 Testing debug WebSocket gateway...")
    
    try:
        uri = "ws://localhost:8003/ws/collaboration"
        print(f"Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a simple message
            message = {
                "type": "join_session",
                "session_id": "test_session_123",
                "user_id": "test_user"
            }
            
            print(f"Sending message: {message}")
            await websocket.send(json.dumps(message))
            
            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            print(f"✅ Received response: {response_data}")
            
            # Send another message
            message2 = {
                "type": "update_document",
                "session_id": "test_session_123",
                "user_id": "test_user",
                "changes": [{"type": "insert", "position": 0, "text": "Hello World"}]
            }
            
            print(f"Sending second message: {message2}")
            await websocket.send(json.dumps(message2))
            
            # Wait for response
            response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data2 = json.loads(response2)
            
            print(f"✅ Received second response: {response_data2}")
            
            print("✅ All tests passed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

async def test_query_updates():
    """Test query updates WebSocket."""
    print("\n🔍 Testing query updates WebSocket...")
    
    try:
        uri = "ws://localhost:8003/ws/query-updates"
        print(f"Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send subscription message
            message = {
                "type": "subscribe",
                "query_id": "test_query_123"
            }
            
            print(f"Sending message: {message}")
            await websocket.send(json.dumps(message))
            
            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            print(f"✅ Received response: {response_data}")
            
            # Wait for second response (mock query data)
            response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data2 = json.loads(response2)
            
            print(f"✅ Received second response: {response_data2}")
            
            print("✅ Query updates test passed!")
            
    except Exception as e:
        print(f"❌ Query updates test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests."""
    print("🔍 Debug WebSocket Test Suite")
    print("=" * 40)
    
    # Wait for server to start
    print("Waiting for server to start...")
    await asyncio.sleep(3)
    
    # Test collaboration
    await test_debug_websocket()
    
    # Test query updates
    await test_query_updates()
    
    print("\n🏁 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 