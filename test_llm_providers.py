import os
import asyncio
from shared.core.llm_client_v3 import get_llm_client_v3

async def test_llm_providers():
    """Test what LLM providers are available."""
    
    print("🔍 Testing LLM Providers")
    print("=" * 50)
    
    # Set environment variable
    os.environ["USE_MOCK_LLM"] = "true"
    
    try:
        # Get LLM client
        client = get_llm_client_v3()
        
        print(f"✅ LLM Client initialized")
        print(f"📊 Providers loaded: {len(client.providers)}")
        
        for i, provider in enumerate(client.providers):
            info = provider.get_provider_info()
            print(f"  Provider {i+1}: {info}")
        
        # Test health check
        health = await client.health_check()
        print(f"🏥 Health check: {health}")
        
        # Test a simple generation
        print("\n🧪 Testing text generation...")
        try:
            response = await client.generate_text("What is AI?", max_tokens=50)
            print(f"✅ Generation successful: {response[:100]}...")
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            
    except Exception as e:
        print(f"❌ LLM Client initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_providers())
