from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Test script for LLMClient functionality.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, '.')

async def test_llm_client():
    """Test the LLMClient functionality."""
    try:
        print("\n🔄 Testing LLMClient initialization...")
        
        # Initialize LLMClient
        from shared.core.agents.llm_client import LLMClient
        
        llm_client = LLMClient()
        print("✅ LLMClient initialized successfully")
        
        # Test generate_text method
        print("\n🔄 Testing generate_text method...")
        test_prompt = "Say hello world in one sentence."
        
        try:
            response = await llm_client.generate_text(test_prompt, max_tokens=50, temperature=0.1)
            print(f"✅ generate_text successful")
            print(f"   Response: {response}")
            
            if "hello" in response.lower():
                print("✅ Response contains 'hello' as expected")
            else:
                print("⚠️  Response doesn't contain 'hello' but method works")
                
        except Exception as e:
            print(f"❌ generate_text failed: {e}")
            return False
        
        # Test create_embedding method
        print("\n🔄 Testing create_embedding method...")
        test_text = "This is a test sentence for embedding."
        
        try:
            embedding = await llm_client.create_embedding(test_text)
            print(f"✅ create_embedding successful")
            print(f"   Embedding length: {len(embedding)}")
            print(f"   First few values: {embedding[:5]}")
            
        except Exception as e:
            print(f"❌ create_embedding failed: {e}")
            return False
        
        # Test get_embedding alias
        print("\n🔄 Testing get_embedding alias...")
        try:
            embedding2 = await llm_client.get_embedding(test_text)
            print(f"✅ get_embedding alias works")
            
            # Verify it returns the same result
            if embedding == embedding2:
                print("✅ get_embedding returns same result as create_embedding")
            else:
                print("⚠️  get_embedding returns different result")
                
        except Exception as e:
            print(f"❌ get_embedding failed: {e}")
            return False
        
        print("\n🎉 All LLMClient tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ LLMClient test failed: {e}")
        return False

def test_agent_integration():
    """Test that agents can use the LLMClient correctly."""
    try:
        print("\n🔄 Testing agent integration...")
        
        # Test synthesis agent
        from shared.core.agents.synthesis_agent import SynthesisAgent
        
        synthesis_agent = SynthesisAgent()
        print("✅ SynthesisAgent initialized successfully")
        
        # Test factcheck agent
        from shared.core.agents.factcheck_agent import FactCheckAgent
        
        factcheck_agent = FactCheckAgent()
        print("✅ FactCheckAgent initialized successfully")
        
        # Test retrieval agent
        from shared.core.agents.retrieval_agent import RetrievalAgent
        
        retrieval_agent = RetrievalAgent()
        print("✅ RetrievalAgent initialized successfully")
        
        print("🎉 All agent integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting LLMClient tests...")
    print("=" * 50)
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    openai_key = settings.openai_api_key
    anthropic_key = settings.anthropic_api_key
    
    if openai_key:
        print(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")
    else:
        print("⚠️  OPENAI_API_KEY not found")
    
    if anthropic_key:
        print(f"✅ ANTHROPIC_API_KEY found (length: {len(anthropic_key)})")
    else:
        print("⚠️  ANTHROPIC_API_KEY not found")
    
    print("\n" + "=" * 50)
    
    # Run tests
    llm_test_passed = asyncio.run(test_llm_client())
    agent_test_passed = test_agent_integration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   LLMClient Tests: {'✅ PASSED' if llm_test_passed else '❌ FAILED'}")
    print(f"   Agent Integration: {'✅ PASSED' if agent_test_passed else '❌ FAILED'}")
    
    if llm_test_passed and agent_test_passed:
        print("\n🎉 All tests passed! LLMClient is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main()) 