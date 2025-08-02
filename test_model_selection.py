#!/usr/bin/env python3
"""
Test script for model selection functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.core.agent_pattern import ModelSelectionStrategy, EnhancedLLMClientWithFallback
from shared.core.api.config import get_settings


async def test_model_selection():
    """Test the model selection functionality."""
    print("🧪 Testing Model Selection Strategy")
    print("=" * 50)
    
    # Get settings
    settings = get_settings()
    print(f"📋 Settings:")
    print(f"  - Prioritize free models: {settings.prioritize_free_models}")
    print(f"  - Use dynamic selection: {settings.use_dynamic_selection}")
    print(f"  - Ollama enabled: {settings.ollama_enabled}")
    print(f"  - OpenAI API key: {'Set' if settings.openai_api_key else 'Not set'}")
    print(f"  - Anthropic API key: {'Set' if settings.anthropic_api_key else 'Not set'}")
    print()
    
    # Create model selector
    selector = ModelSelectionStrategy()
    
    # Test queries
    test_queries = [
        ("What is the capital of France?", "simple"),
        ("Analyze the impact of climate change on global economies", "complex"),
        ("Compare and contrast the benefits of renewable energy sources", "complex"),
        ("What is 2+2?", "simple"),
        ("Research the historical development of artificial intelligence", "complex"),
    ]
    
    print("🔍 Testing Query Classification and Model Selection:")
    print("-" * 50)
    
    for query, expected_complexity in test_queries:
        print(f"\n📝 Query: {query}")
        print(f"   Expected complexity: {expected_complexity}")
        
        try:
            # Test model selection
            selection = await selector.select_model_for_query(query)
            print(f"   ✅ Selected provider: {selection['primary_provider']}")
            print(f"   📊 Complexity: {selection['complexity']}")
            print(f"   🔄 Fallback providers: {selection['fallback_providers']}")
            print(f"   💡 Reason: {selection['reason']}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing Enhanced LLM Client with Fallback")
    print("=" * 50)
    
    # Test the enhanced LLM client
    try:
        client = EnhancedLLMClientWithFallback()
        print("✅ Enhanced LLM Client created successfully")
        
        # Test a simple query
        test_prompt = "What is artificial intelligence?"
        print(f"\n📝 Testing with prompt: {test_prompt}")
        
        try:
            response = await client.generate_text_with_fallback(
                prompt=test_prompt,
                system_message="You are a helpful AI assistant.",
                max_tokens=100
            )
            print(f"✅ Success! Response: {response.content[:100]}...")
            print(f"   Provider: {response.provider}")
            print(f"   Model: {response.model}")
            print(f"   Response time: {response.response_time_ms:.2f}ms")
            
        except Exception as e:
            print(f"❌ LLM generation failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Failed to create Enhanced LLM Client: {str(e)}")


async def test_agent_strategies():
    """Test the agent strategies with the new model selection."""
    print("\n" + "=" * 50)
    print("🧪 Testing Agent Strategies with Model Selection")
    print("=" * 50)
    
    from shared.core.agent_pattern import SynthesisStrategy, FactCheckStrategy, RetrievalStrategy
    from shared.core.base_agent import QueryContext
    
    # Create test context
    context = QueryContext(
        query="test query",
        user_id="test-user",
        session_id="test-session",
        metadata={}
    )
    
    # Test Synthesis Strategy
    print("\n🔬 Testing Synthesis Strategy:")
    synthesis_agent = SynthesisStrategy()
    
    test_facts = [
        {"claim": "Paris is the capital of France", "confidence": 0.95, "source": "geography"},
        {"claim": "France is in Europe", "confidence": 0.98, "source": "geography"},
    ]
    
    task = {
        "query": "What is the capital of France?",
        "verified_facts": test_facts
    }
    
    try:
        result = await synthesis_agent.execute(task, context)
        print(f"✅ Synthesis result: {result.success}")
        if result.success:
            print(f"   Answer: {result.data.get('answer', '')[:100]}...")
            print(f"   Confidence: {result.confidence}")
    except Exception as e:
        print(f"❌ Synthesis failed: {str(e)}")
    
    # Test FactCheck Strategy
    print("\n🔍 Testing FactCheck Strategy:")
    factcheck_agent = FactCheckStrategy()
    
    task = {
        "query": "Is Paris the capital of France?",
        "documents": [
            {"content": "Paris is the capital and largest city of France."}
        ]
    }
    
    try:
        result = await factcheck_agent.execute(task, context)
        print(f"✅ FactCheck result: {result.success}")
        if result.success:
            print(f"   Verified facts: {len(result.data.get('verified_facts', []))}")
            print(f"   Confidence: {result.confidence}")
    except Exception as e:
        print(f"❌ FactCheck failed: {str(e)}")
    
    # Test Retrieval Strategy
    print("\n🔎 Testing Retrieval Strategy:")
    retrieval_agent = RetrievalStrategy()
    
    task = {
        "query": "What is artificial intelligence?"
    }
    
    try:
        result = await retrieval_agent.execute(task, context)
        print(f"✅ Retrieval result: {result.success}")
        if result.success:
            print(f"   Documents found: {len(result.data.get('documents', []))}")
            print(f"   Confidence: {result.confidence}")
    except Exception as e:
        print(f"❌ Retrieval failed: {str(e)}")


async def main():
    """Main test function."""
    print("🚀 Starting Model Selection Tests")
    print("=" * 60)
    
    await test_model_selection()
    await test_agent_strategies()
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 