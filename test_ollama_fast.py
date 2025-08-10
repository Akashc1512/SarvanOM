#!/usr/bin/env python3
"""
Fast Ollama Test - Direct API call for 5-second responses
"""

import asyncio
import aiohttp
import json
import time

async def test_ollama_fast():
    """Test Ollama for fast 5-second responses"""
    
    print("🚀 FAST OLLAMA TEST (5-SECOND TARGET)")
    print("=" * 50)
    
    base_url = "http://localhost:11434"
    
    # Simple, fast payload
    payload = {
        "model": "deepseek-r1:8b",
        "prompt": "What is AI? (brief answer)",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 100,  # Short response
            "stop": ["\n\n"],
            "num_ctx": 512  # Small context
        }
    }
    
    print(f"📝 Testing: {payload['prompt']}")
    print(f"🎯 Model: {payload['model']}")
    print(f"⏱️ Target: < 5 seconds")
    print("-" * 30)
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                elapsed = time.time() - start_time
                
                print(f"📡 Status: {response.status}")
                print(f"⏱️ Response Time: {elapsed:.2f}s")
                
                if response.status == 200:
                    try:
                        result = await response.json()
                        response_text = result.get("response", "")
                        
                        print(f"✅ Success!")
                        print(f"📝 Response Length: {len(response_text)} chars")
                        print(f"🤖 Content: {response_text}")
                        
                        if elapsed <= 5:
                            print("🏆 FAST RESPONSE ACHIEVED!")
                        elif elapsed <= 10:
                            print("⚡ ACCEPTABLE RESPONSE TIME")
                        else:
                            print("⚠️ TOO SLOW - NEEDS OPTIMIZATION")
                            
                        return True
                        
                    except Exception as e:
                        print(f"❌ Parse Error: {e}")
                        text = await response.text()
                        print(f"📄 Raw Response: {text[:200]}...")
                        return False
                else:
                    error = await response.text()
                    print(f"❌ API Error: {error}")
                    return False
                    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Exception after {elapsed:.2f}s: {e}")
        return False

async def test_backend_fast():
    """Test backend for fast responses"""
    
    print("\n🔗 TESTING BACKEND (FAST MODE)")
    print("=" * 50)
    
    import requests
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/search",
            json={
                "query": "What is AI?",
                "max_results": 1
            },
            timeout=20
        )
        
        elapsed = time.time() - start_time
        
        print(f"📡 Status: {response.status_code}")
        print(f"⏱️ Response Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("data", {}).get("answer", "")
            
            print(f"📝 Answer Length: {len(answer)} chars")
            print(f"🤖 Preview: {answer[:100]}...")
            
            # Check if real AI response
            is_real = (
                len(answer) > 30 and 
                not any(x in answer for x in ["Unable to process", "try again later", "AI processing completed"]) and
                any(x in answer.lower() for x in ["artificial", "intelligence", "ai", "machine", "computer"])
            )
            
            print(f"✅ Real AI Response: {is_real}")
            
            if elapsed <= 5:
                print("🏆 FAST BACKEND RESPONSE!")
            elif elapsed <= 10:
                print("⚡ ACCEPTABLE BACKEND TIME")
            else:
                print("⚠️ BACKEND TOO SLOW")
                
            return is_real
        else:
            print(f"❌ Backend Error: {response.text}")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Backend Exception after {elapsed:.2f}s: {e}")
        return False

async def main():
    """Run all fast tests"""
    print("🎯 GOAL: 5-SECOND AI RESPONSES")
    print("🔧 Testing Ollama DeepSeek-R1:8b optimization")
    print()
    
    # Test 1: Direct Ollama
    ollama_works = await test_ollama_fast()
    
    # Test 2: Backend integration
    backend_works = await test_backend_fast()
    
    print("\n🎯 FAST RESPONSE SUMMARY")
    print("=" * 50)
    print(f"✅ Ollama Direct: {'WORKING' if ollama_works else 'FAILED'}")
    print(f"✅ Backend Integration: {'WORKING' if backend_works else 'FAILED'}")
    
    if ollama_works and backend_works:
        print("🏆 SUCCESS: Fast AI responses achieved!")
    elif ollama_works:
        print("🔧 Issue: Ollama works but backend needs fixing")
    else:
        print("❌ Issue: Ollama not responding properly")

if __name__ == "__main__":
    asyncio.run(main())
