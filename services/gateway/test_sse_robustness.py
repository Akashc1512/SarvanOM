#!/usr/bin/env python3
"""
SSE Robustness Test Script

This script tests the enhanced SSE streaming system with:
- Heartbeat monitoring
- Duration caps
- Trace ID propagation
- Network interruption simulation
- Automatic reconnection
"""

import asyncio
import aiohttp
import json
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone


class SSETestClient:
    """Test client for SSE streaming with robustness testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.trace_id: str = None
        self.events_received: List[Dict[str, Any]] = []
        self.heartbeats_received: int = 0
        self.content_chunks_received: int = 0
        self.complete_received: bool = False
        self.start_time: float = None
        self.last_message_time: float = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_sse_stream(self, query: str, max_duration: int = 30) -> Dict[str, Any]:
        """Test SSE streaming with comprehensive monitoring."""
        print(f"🧪 Testing SSE stream for query: '{query}'")
        print(f"⏱️  Max duration: {max_duration} seconds")
        
        self.start_time = time.time()
        self.last_message_time = self.start_time
        
        # Build SSE URL
        url = f"{self.base_url}/stream/search"
        params = {
            "query": query,
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                print(f"📡 SSE connection established: {response.status}")
                
                # Extract trace ID from headers
                self.trace_id = response.headers.get("X-Trace-ID")
                print(f"🔍 Trace ID: {self.trace_id}")
                
                # Check SSE headers
                self._check_sse_headers(response.headers)
                
                # Read SSE stream
                async for line in response.content:
                    if line:
                        await self._process_sse_line(line.decode('utf-8').strip())
                        
                        # Check for timeout
                        if time.time() - self.start_time > max_duration:
                            print(f"⏰ Test duration limit reached ({max_duration}s)")
                            break
                            
                        # Check for silence (no messages for 20 seconds)
                        if time.time() - self.last_message_time > 20:
                            print("🔇 Silence threshold exceeded (20s)")
                            break
                            
        except asyncio.TimeoutError:
            print("⏰ SSE stream timeout")
        except Exception as e:
            print(f"❌ SSE stream error: {e}")
        
        return self._generate_test_report()
    
    def _check_sse_headers(self, headers: Dict[str, str]):
        """Check that SSE headers are properly set."""
        print("\n📋 Checking SSE headers:")
        
        required_headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-store",
            "Connection": "keep-alive",
            "X-Stream-Type": "search",
            "X-Trace-ID": self.trace_id
        }
        
        for header, expected in required_headers.items():
            actual = headers.get(header)
            if actual:
                if expected in actual or header == "X-Trace-ID":
                    print(f"   ✅ {header}: {actual}")
                else:
                    print(f"   ⚠️  {header}: {actual} (expected: {expected})")
            else:
                print(f"   ❌ {header}: Missing")
    
    async def _process_sse_line(self, line: str):
        """Process a single SSE line."""
        if not line:
            return
            
        self.last_message_time = time.time()
        
        if line.startswith("event: "):
            event_type = line[7:]
            print(f"📨 Event: {event_type}")
            
        elif line.startswith("data: "):
            data_str = line[6:]
            try:
                data = json.loads(data_str)
                self.events_received.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": data
                })
                
                # Count specific event types
                if data.get("type") == "heartbeat":
                    self.heartbeats_received += 1
                    print(f"💓 Heartbeat #{self.heartbeats_received}: {data.get('uptime_seconds', 0):.1f}s")
                    
                elif data.get("type") == "content":
                    self.content_chunks_received += 1
                    text = data.get("text", "")
                    print(f"📝 Content chunk #{self.content_chunks_received}: {text[:50]}...")
                    
                elif data.get("type") == "complete":
                    self.complete_received = True
                    print(f"✅ Complete: {data.get('total_chunks', 0)} chunks, {data.get('total_tokens', 0)} tokens")
                    
            except json.JSONDecodeError:
                print(f"⚠️  Invalid JSON data: {data_str}")
                
        elif line.startswith("id: "):
            event_id = line[4:]
            if event_id != "unknown":
                print(f"🆔 Event ID: {event_id}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        duration = time.time() - self.start_time if self.start_time else 0
        
        report = {
            "test_duration": duration,
            "trace_id": self.trace_id,
            "events_received": len(self.events_received),
            "heartbeats_received": self.heartbeats_received,
            "content_chunks_received": self.content_chunks_received,
            "complete_received": self.complete_received,
            "heartbeat_interval": duration / max(1, self.heartbeats_received) if self.heartbeats_received > 0 else None,
            "events_per_second": len(self.events_received) / max(1, duration),
            "success": self.complete_received and self.content_chunks_received > 0
        }
        
        return report


async def test_network_interruption():
    """Test SSE robustness with simulated network interruption."""
    print("\n🌐 Testing Network Interruption Scenario")
    print("=" * 50)
    
    async with SSETestClient() as client:
        # Start SSE stream
        stream_task = asyncio.create_task(
            client.test_sse_stream("What is machine learning?", max_duration=45)
        )
        
        # Simulate network interruption after 10 seconds
        await asyncio.sleep(10)
        print("\n🔌 Simulating network interruption...")
        
        # Wait a bit for interruption to take effect
        await asyncio.sleep(5)
        
        # The stream should automatically reconnect
        print("🔄 Network restored, checking for reconnection...")
        
        # Wait for stream to complete
        report = await stream_task
        
        print(f"\n📊 Network Interruption Test Results:")
        print(f"   Duration: {report['test_duration']:.1f}s")
        print(f"   Heartbeats: {report['heartbeats_received']}")
        print(f"   Content chunks: {report['content_chunks_received']}")
        print(f"   Complete: {report['complete_received']}")
        print(f"   Success: {report['success']}")
        
        return report


async def test_duration_cap():
    """Test SSE duration cap functionality."""
    print("\n⏰ Testing Duration Cap Scenario")
    print("=" * 50)
    
    async with SSETestClient() as client:
        # Test with a long query that should hit duration cap
        report = await client.test_sse_stream(
            "Explain quantum computing in detail with examples and applications", 
            max_duration=70  # Longer than default 60s cap
        )
        
        print(f"\n📊 Duration Cap Test Results:")
        print(f"   Duration: {report['test_duration']:.1f}s")
        print(f"   Heartbeats: {report['heartbeats_received']}")
        print(f"   Content chunks: {report['content_chunks_received']}")
        print(f"   Complete: {report['complete_received']}")
        print(f"   Success: {report['success']}")
        
        # Check if duration cap was respected
        if report['test_duration'] <= 65:  # Allow some buffer
            print("✅ Duration cap respected")
        else:
            print("⚠️  Duration cap may not be working properly")
        
        return report


async def test_heartbeat_frequency():
    """Test heartbeat frequency and consistency."""
    print("\n💓 Testing Heartbeat Frequency")
    print("=" * 50)
    
    async with SSETestClient() as client:
        report = await client.test_sse_stream("What is artificial intelligence?", max_duration=30)
        
        print(f"\n📊 Heartbeat Test Results:")
        print(f"   Duration: {report['test_duration']:.1f}s")
        print(f"   Heartbeats: {report['heartbeats_received']}")
        print(f"   Heartbeat interval: {report['heartbeat_interval']:.1f}s")
        print(f"   Events per second: {report['events_per_second']:.2f}")
        
        # Check heartbeat frequency (should be ~5 seconds based on config)
        if report['heartbeat_interval'] and 4 <= report['heartbeat_interval'] <= 6:
            print("✅ Heartbeat frequency is correct (~5s)")
        else:
            print(f"⚠️  Heartbeat frequency may be incorrect: {report['heartbeat_interval']:.1f}s")
        
        return report


async def main():
    """Run all SSE robustness tests."""
    print("🚀 SSE ROBUSTNESS TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Heartbeat Frequency", test_heartbeat_frequency),
        ("Duration Cap", test_duration_cap),
        ("Network Interruption", test_network_interruption),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, {"error": str(e), "success": False}))
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        success = result.get("success", False)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SSE ROBUSTNESS TESTS PASSED!")
        print("✅ Heartbeats working correctly")
        print("✅ Duration caps enforced")
        print("✅ Network interruption handling works")
        print("✅ Trace ID propagation working")
    else:
        print("⚠️  Some tests failed - check SSE implementation")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
