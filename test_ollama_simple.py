#!/usr/bin/env python3
"""
Simple test to check if Ollama is working.
"""

import asyncio
import aiohttp
import json


async def test_ollama_connection():
    """Test basic Ollama connection."""
    print("🧪 Testing Ollama Connection")
    print("=" * 40)
    
    # Test 1: Check if Ollama is running
    print("1. Checking if Ollama is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Ollama is running! Available models: {len(data.get('models', []))}")
                    for model in data.get('models', []):
                        print(f"   - {model.get('name', 'Unknown')}")
                else:
                    print(f"❌ Ollama responded with status: {response.status}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {str(e)}")
        return False
    
    # Test 2: Try a simple generation
    print("\n2. Testing simple generation...")
    try:
        payload = {
            "model": "llama3.2:3b",
            "prompt": "Hello, how are you?",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 50
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("response", "")
                    print(f"✅ Generation successful!")
                    print(f"   Response: {content[:100]}...")
                    return True
                else:
                    print(f"❌ Generation failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Ollama Connection Test")
    print("=" * 50)
    
    success = await test_ollama_connection()
    
    if success:
        print("\n✅ Ollama is working correctly!")
    else:
        print("\n❌ Ollama has issues. Please check:")
        print("   - Is Ollama installed?")
        print("   - Is Ollama running? (ollama serve)")
        print("   - Are models downloaded? (ollama pull llama3.2:3b)")
        print("   - Is the API accessible at http://localhost:11434?")


if __name__ == "__main__":
    asyncio.run(main()) 