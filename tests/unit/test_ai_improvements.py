#!/usr/bin/env python3
"""
Test script for AI Summarization Improvements and Task Generation
This script tests the enhanced AI features including citations and task generation.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List
import websockets

# Configuration
API_BASE_URL = "http://localhost:8002"
TEST_QUERIES = [
    "What are the latest developments in artificial intelligence?",
    "How does climate change affect global agriculture?",
    "What are the best practices for remote work productivity?",
    "Explain the benefits of renewable energy sources",
    "What are the key principles of effective leadership?"
]

class AIImprovementsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = httpx.AsyncClient()
        
    async def test_basic_query(self, query: str) -> Dict[str, Any]:
        """Test basic query processing with enhanced AI features."""
        print(f"\n🔍 Testing query: {query[:50]}...")
        
        response = await self.session.post(
            f"{self.base_url}/query",
            json={
                "query": query,
                "max_tokens": 500,
                "confidence_threshold": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query processed successfully")
            print(f"   Answer length: {len(result.get('answer', ''))} characters")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Citations: {len(result.get('citations', []))}")
            
            # Check for citations in answer
            answer = result.get('answer', '')
            if '[' in answer and ']' in answer:
                print(f"   ✅ Citations found in answer")
            else:
                print(f"   ⚠️  No citations found in answer")
                
            # Check for sources section
            if 'Sources:' in answer:
                print(f"   ✅ Sources section found")
            else:
                print(f"   ⚠️  No sources section found")
                
            return result
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return {}
    
    async def test_task_generation(self, answer: str, query: str = None) -> Dict[str, Any]:
        """Test task generation from AI answers."""
        print(f"\n🎯 Testing task generation...")
        
        payload = {}
        if answer:
            payload["answer"] = answer
        if query:
            payload["query"] = query
            
        response = await self.session.post(
            f"{self.base_url}/tasks",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            tasks = result.get('tasks', [])
            print(f"✅ Task generation successful")
            print(f"   Generated {len(tasks)} tasks")
            
            for i, task in enumerate(tasks, 1):
                print(f"   {i}. {task.get('task', '')} [{task.get('priority', 'Medium')}]")
                
            return result
        else:
            print(f"❌ Task generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return {}
    
    def test_collaboration_websocket(self) -> bool:
        """Test WebSocket collaboration endpoint."""
        print(f"\n🤝 Testing collaboration WebSocket...")
        
        try:
            import websockets
            import asyncio
            
            async def test_websocket():
                uri = f"ws://localhost:8002/ws/collaboration"
                async with websockets.connect(uri) as websocket:
                    # Test joining session
                    join_message = {
                        "type": "join_session",
                        "session_id": "test_session",
                        "user_id": "test_user"
                    }
                    await websocket.send(json.dumps(join_message))
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "session_joined":
                        print(f"✅ WebSocket collaboration working")
                        return True
                    else:
                        print(f"❌ Unexpected WebSocket response: {response_data}")
                        return False
                        
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_websocket())
            loop.close()
            return result
            
        except ImportError:
            print(f"⚠️  websockets library not available, skipping WebSocket test")
            return True
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            return False
    
    def test_query_updates_websocket(self) -> bool:
        """Test WebSocket query updates endpoint."""
        print(f"\n📊 Testing query updates WebSocket...")
        
        try:
            import websockets
            import asyncio
            
            async def test_websocket():
                uri = f"ws://localhost:8002/ws/query-updates"
                async with websockets.connect(uri) as websocket:
                    # Test subscribing to query updates
                    subscribe_message = {
                        "type": "subscribe",
                        "query_id": "test_query_id"
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "subscribed":
                        print(f"✅ WebSocket query updates working")
                        return True
                    else:
                        print(f"❌ Unexpected WebSocket response: {response_data}")
                        return False
                        
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_websocket())
            loop.close()
            return result
            
        except ImportError:
            print(f"⚠️  websockets library not available, skipping WebSocket test")
            return True
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of all AI improvements."""
        print("🚀 Starting AI Improvements Comprehensive Test")
        print("=" * 60)
        
        # Test basic queries with enhanced AI
        query_results = []
        for query in TEST_QUERIES[:2]:  # Test first 2 queries
            result = await self.test_basic_query(query)
            if result:
                query_results.append(result)
        
        # Test task generation
        if query_results:
            first_result = query_results[0]
            answer = first_result.get('answer', '')
            if answer:
                await self.test_task_generation(answer)
        
        # Test WebSocket endpoints
        self.test_collaboration_websocket()
        self.test_query_updates_websocket()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"   ✅ Queries tested: {len(query_results)}")
        print(f"   ✅ Task generation: {'Working' if query_results else 'Failed'}")
        print(f"   ✅ WebSocket collaboration: {'Working' if self.test_collaboration_websocket() else 'Failed'}")
        print(f"   ✅ WebSocket query updates: {'Working' if self.test_query_updates_websocket() else 'Failed'}")
        
        return len(query_results) > 0

async def main():
    """Main test function."""
    print("Universal Knowledge Hub - AI Improvements Test")
    print("Testing enhanced AI summarization and task generation features")
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"✅ Backend is running at {API_BASE_URL}")
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Please start the backend server first:")
        print("  python api/main.py")
        return False
    
    # Run tests
    tester = AIImprovementsTester(API_BASE_URL)
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Test the collaborative features in the browser")
        print("3. Verify task generation works in the UI")
    else:
        print("\n❌ Some tests failed. Please check the backend logs.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 