#!/usr/bin/env python3
"""
Simple HuggingFace debug test
"""

import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from services.gateway.real_llm_integration import RealLLMProcessor

async def test_hf_direct():
    print("🔧 DEBUGGING HUGGINGFACE DIRECT CALL")
    print("=" * 40)
    
    processor = RealLLMProcessor()
    
    # Check provider health
    print("🔍 Provider Health:")
    for provider, health in processor.provider_health.items():
        print(f"   {provider}: {'✅' if health else '❌'}")
    
    # Test HuggingFace directly
    print(f"\n🔑 HuggingFace API Key: {'✅' if os.getenv('HUGGINGFACE_API_KEY') else '❌'}")
    
    # Test a simple prompt
    test_prompt = "What is AI?"
    print(f"\n🧪 Testing: {test_prompt}")
    
    try:
        result = await processor._call_huggingface(test_prompt, 50, 0.3)
        if result:
            print(f"✅ Success: {result[:100]}...")
        else:
            print("❌ No result returned")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    asyncio.run(test_hf_direct())

if __name__ == "__main__":
    main()
