#!/usr/bin/env python3
"""
Test Ollama Only - Working with DeepSeek-R1:8b
Since only Ollama is properly configured, let's test it thoroughly
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ollama_deepseek():
    """Test Ollama with DeepSeek-R1:8b model"""
    
    print("🚀 TESTING OLLAMA DEEPSEEK-R1:8B (2025 LATEST)")
    print("=" * 60)
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        async with aiohttp.ClientSession() as session:
            # First check available models
            print("📋 Checking available models...")
            async with session.get(f"{base_url}/api/tags", timeout=10) as response:
                if response.status == 200:
                    models = await response.json()
                    model_names = [m["name"] for m in models.get("models", [])]
                    print(f"   ✅ Available: {model_names}")
                    
                    if "deepseek-r1:8b" in model_names:
                        print("   🎯 DeepSeek-R1:8b found - testing...")
                        
                        # Test with DeepSeek-R1:8b
                        test_queries = [
                            "What is artificial intelligence?",
                            "Explain machine learning in simple terms",
                            "Write a Python function to sort a list"
                        ]
                        
                        for i, query in enumerate(test_queries, 1):
                            print(f"\n🔬 TEST {i}: {query}")
                            print("-" * 40)
                            
                            payload = {
                                "model": "deepseek-r1:8b",
                                "prompt": query,
                                "stream": False,
                                "options": {
                                    "temperature": 0.7,
                                    "top_p": 0.9,
                                    "top_k": 40
                                }
                            }
                            
                            async with session.post(
                                f"{base_url}/api/generate",
                                json=payload,
                                timeout=60
                            ) as gen_response:
                                if gen_response.status == 200:
                                    result = await gen_response.json()
                                    response_text = result.get("response", "")
                                    
                                    if response_text:
                                        print(f"   ✅ Success! Generated {len(response_text)} chars")
                                        print(f"   🎯 Response: {response_text[:200]}...")
                                        
                                        # Test if it's a real AI response
                                        if len(response_text) > 50 and any(word in response_text.lower() for word in ["artificial", "intelligence", "machine", "learning", "function", "python"]):
                                            print("   🤖 REAL AI RESPONSE DETECTED!")
                                        else:
                                            print("   ⚠️ Response seems generic")
                                    else:
                                        print("   ❌ Empty response")
                                        
                                else:
                                    error = await gen_response.text()
                                    print(f"   ❌ Error {gen_response.status}: {error}")
                    else:
                        print("   ❌ DeepSeek-R1:8b not found")
                        print(f"   🔧 Available models: {model_names}")
                        
                        # Try with any available model
                        if model_names:
                            test_model = model_names[0]
                            print(f"\n🔄 Trying with {test_model}...")
                            
                            payload = {
                                "model": test_model,
                                "prompt": "What is AI?",
                                "stream": False
                            }
                            
                            async with session.post(
                                f"{base_url}/api/generate",
                                json=payload,
                                timeout=30
                            ) as gen_response:
                                if gen_response.status == 200:
                                    result = await gen_response.json()
                                    response_text = result.get("response", "")
                                    print(f"   ✅ {test_model} works! Response: {response_text[:100]}...")
                                else:
                                    error = await gen_response.text()
                                    print(f"   ❌ {test_model} failed: {error}")
                else:
                    print(f"   ❌ Cannot connect to Ollama: {response.status}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

async def test_backend_with_ollama():
    """Test our backend specifically with Ollama"""
    
    print("\n🔗 TESTING BACKEND WITH OLLAMA")
    print("=" * 60)
    
    try:
        import requests
        
        # Test with a simple query
        response = requests.post(
            "http://localhost:8000/search",
            json={
                "query": "What is machine learning?",
                "max_results": 2
            },
            timeout=60
        )
        
        print(f"📡 Backend Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            answer = data.get("answer", "")
            
            print(f"📊 Response structure: {list(result.keys())}")
            print(f"🤖 Answer length: {len(answer)} chars")
            print(f"📝 Answer preview: {answer[:200]}...")
            
            # Check if it's a real AI response
            if "Unable to process" in answer or "try again later" in answer:
                print("❌ Getting fallback response - LLM not working")
            elif len(answer) > 100:
                print("✅ REAL AI RESPONSE FROM BACKEND!")
            else:
                print("⚠️ Short response - might be fallback")
                
        else:
            print(f"❌ Backend error: {response.text}")
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

async def main():
    """Run all Ollama tests"""
    await test_ollama_deepseek()
    await test_backend_with_ollama()
    
    print("\n🎯 OLLAMA TEST SUMMARY")
    print("=" * 60)
    print("✅ Ollama is our only working provider")
    print("🎯 DeepSeek-R1:8b is the latest reasoning model (Jan 2025)")
    print("🔧 Need to fix backend integration to use Ollama responses")
    print("💡 API keys for HuggingFace/OpenAI/Anthropic need real values")

if __name__ == "__main__":
    asyncio.run(main())
