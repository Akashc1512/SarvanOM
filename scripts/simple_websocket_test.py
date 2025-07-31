#!/usr/bin/env python3
"""
Simple WebSocket Test
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket endpoints."""
    
    print("🔗 Testing WebSocket endpoints...")
    
    # Test collaboration endpoint
    try:
        print("Testing /ws/collaboration...")
        async with websockets.connect('ws://localhost:8002/ws/collaboration') as websocket:
            # Send a simple message
            message = {
                "type": "join_session",
                "session_id": "test_session",
                "user_id": "test_user"
            }
            await websocket.send(json.dumps(message))
            
            # Wait for response
            response = await websocket.recv()
            print(f"✅ Collaboration response: {response}")
            
    except Exception as e:
        print(f"❌ Collaboration error: {e}")
    
    # Test query updates endpoint
    try:
        print("Testing /ws/query-updates...")
        async with websockets.connect('ws://localhost:8002/ws/query-updates') as websocket:
            # Send a simple message
            message = {
                "type": "subscribe",
                "query_id": "test_query"
            }
            await websocket.send(json.dumps(message))
            
            # Wait for response
            response = await websocket.recv()
            print(f"✅ Query updates response: {response}")
            
    except Exception as e:
        print(f"❌ Query updates error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 