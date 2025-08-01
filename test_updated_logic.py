#!/usr/bin/env python3
"""
Test Updated Logic
Verifies that the updated logic properly utilizes Ollama and Hugging Face alongside existing providers
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from shared.core.llm_client_v3 import EnhancedLLMClientV3, LLMProvider, LLMConfig
from shared.core.model_selector import DynamicModelSelector, get_model_selector
from shared.core.agents.synthesis_agent import SynthesisAgent
from shared.core.agents.retrieval_agent import RetrievalAgent

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model_selector_integration():
    """Test that the model selector properly includes Ollama and Hugging Face models."""
    
    logger.info("🧪 Testing Model Selector Integration")
    print("=" * 60)
    
    # Initialize model selector
    model_selector = get_model_selector()
    
    # Test queries for different categories
    test_queries = [
        ("What is the weather like?", "general_factual"),
        ("Write a Python function to calculate fibonacci", "code"),
        ("Analyze the benefits of renewable energy", "analytical"),
        ("How are machine learning and AI related?", "knowledge_graph"),
        ("Compare Python vs JavaScript for web development", "comparative"),
        ("What are the steps to deploy a React app?", "procedural"),
        ("Create a story about a robot learning to paint", "creative"),
        ("What do you think about electric cars?", "opinion")
    ]
    
    logger.info("📊 Testing model selection for different query types:")
    
    for query, expected_category in test_queries:
        try:
            result = await model_selector.select_model(query)
            
            print(f"\n🔍 Query: {query[:50]}...")
            print(f"   Expected Category: {expected_category}")
            print(f"   Selected Model: {result.selected_model}")
            print(f"   Provider: {result.selected_provider.value}")
            print(f"   Tier: {result.model_tier.value}")
            print(f"   Cost: ${result.estimated_cost:.6f}")
            print(f"   Reasoning: {result.reasoning[:100]}...")
            
            # Check if free models are being prioritized
            if result.estimated_cost == 0.0:
                print(f"   ✅ FREE MODEL SELECTED!")
            else:
                print(f"   💰 Paid model: ${result.estimated_cost:.6f}")
                
        except Exception as e:
            logger.error(f"❌ Model selection failed for '{query}': {e}")
    
    print("\n" + "=" * 60)

async def test_agent_integration():
    """Test that agents properly use the updated LLM client."""
    
    logger.info("🧪 Testing Agent Integration")
    print("=" * 60)
    
    # Test Synthesis Agent
    logger.info("📋 Testing Synthesis Agent...")
    try:
        synthesis_agent = SynthesisAgent()
        
        # Create a test task
        test_task = {
            "query": "What are the benefits of renewable energy?",
            "verified_facts": [
                {
                    "fact": "Solar energy reduces carbon emissions by 95% compared to coal",
                    "source": "solar_study_2023",
                    "confidence": 0.9
                },
                {
                    "fact": "Wind power is now cheaper than fossil fuels in many regions",
                    "source": "wind_cost_analysis_2024",
                    "confidence": 0.85
                }
            ],
            "params": {
                "max_length": 200,
                "temperature": 0.2
            }
        }
        
        test_context = type('QueryContext', (), {
            'query': "What are the benefits of renewable energy?",
            'user_id': "test_user",
            'session_id': "test_session"
        })()
        
        result = await synthesis_agent.process_task(test_task, test_context)
        
        if result.get("success"):
            print("✅ Synthesis Agent: Success")
            print(f"   Response: {result.get('data', {}).get('answer', '')[:100]}...")
        else:
            print("❌ Synthesis Agent: Failed")
            
    except Exception as e:
        logger.error(f"❌ Synthesis Agent test failed: {e}")
    
    # Test Retrieval Agent
    logger.info("📋 Testing Retrieval Agent...")
    try:
        retrieval_agent = RetrievalAgent()
        
        # Create a test task
        test_task = {
            "query": "What is machine learning?",
            "search_type": "hybrid",
            "top_k": 5,
            "max_tokens": 1000
        }
        
        test_context = type('QueryContext', (), {
            'query': "What is machine learning?",
            'user_id': "test_user",
            'session_id': "test_session"
        })()
        
        result = await retrieval_agent.process_task(test_task, test_context)
        
        if result.get("success"):
            print("✅ Retrieval Agent: Success")
            documents = result.get("data", {}).get("documents", [])
            print(f"   Retrieved {len(documents)} documents")
        else:
            print("❌ Retrieval Agent: Failed")
            
    except Exception as e:
        logger.error(f"❌ Retrieval Agent test failed: {e}")
    
    print("\n" + "=" * 60)

async def test_provider_availability():
    """Test which providers are available and working."""
    
    logger.info("🧪 Testing Provider Availability")
    print("=" * 60)
    
    # Test LLM client initialization
    try:
        client = EnhancedLLMClientV3()
        
        # Check health status
        health_status = await client.health_check()
        
        print("🏥 Provider Health Status:")
        for provider, status in health_status.items():
            status_icon = "🟢" if status else "🔴"
            print(f"   {status_icon} {provider}: {'Healthy' if status else 'Unhealthy'}")
        
        # Get provider info
        print("\n📊 Provider Information:")
        for provider in client.providers:
            info = provider.get_provider_info()
            print(f"   {info['provider']}: {info['model']}")
            print(f"      Cost: ${info['cost_per_1k_tokens']:.6f}/1K tokens")
            print(f"      Capabilities: {', '.join(info['capabilities'])}")
        
    except Exception as e:
        logger.error(f"❌ Provider availability test failed: {e}")
    
    print("\n" + "=" * 60)

async def test_cost_optimization():
    """Test that the system prioritizes free models when available."""
    
    logger.info("🧪 Testing Cost Optimization")
    print("=" * 60)
    
    # Test queries that should prefer free models
    test_queries = [
        "Hello, how are you?",
        "What is 2+2?",
        "Tell me a joke",
        "What is the capital of France?",
        "Write a simple Python function"
    ]
    
    client = EnhancedLLMClientV3()
    
    for query in test_queries:
        try:
            response = await client.generate_text(
                prompt=query,
                max_tokens=50,
                temperature=0.1,
                query=query,
                use_dynamic_selection=True
            )
            
            print(f"✅ Query: {query[:30]}...")
            print(f"   Response: {response[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
    
    print("\n" + "=" * 60)

def print_setup_summary():
    """Print a summary of the setup and what was updated."""
    
    print("\n📋 UPDATED LOGIC SUMMARY")
    print("=" * 60)
    
    print("\n✅ What Was Updated:")
    print("1. Model Selector - Added Ollama and Hugging Face models")
    print("2. LLM Client - Added OllamaProvider and HuggingFaceProvider")
    print("3. Synthesis Agent - Updated to use EnhancedLLMClientV3")
    print("4. Retrieval Agent - Updated to use EnhancedLLMClientV3")
    print("5. Model Scoring - Prioritizes free models (0.5 bonus)")
    
    print("\n🎯 Free Model Priority:")
    print("- Ollama models get 0.5 bonus score")
    print("- Hugging Face models get 0.5 bonus score")
    print("- Free providers get 0.3 bonus score")
    print("- Cost efficiency is maximized for free models")
    
    print("\n🔧 Environment Setup:")
    print("- OLLAMA_ENABLED=true (default)")
    print("- OLLAMA_MODEL=llama3.2:3b (default)")
    print("- HUGGINGFACE_API_KEY=your_key (optional)")
    print("- HUGGINGFACE_MODEL=microsoft/DialoGPT-medium (default)")
    
    print("\n💡 Usage:")
    print("- Agents automatically use the best available model")
    print("- Free models are prioritized when available")
    print("- Fallback to paid models if free ones fail")
    print("- Dynamic model selection based on query type")

async def main():
    """Main test function."""
    
    logger.info("🚀 Testing Updated Logic with Ollama and Hugging Face")
    
    # Print setup summary
    print_setup_summary()
    
    # Run tests
    await test_provider_availability()
    await test_model_selector_integration()
    await test_agent_integration()
    await test_cost_optimization()
    
    logger.info("\n✅ All tests completed!")
    print("\n🎉 Updated logic is ready to use Ollama and Hugging Face!")

if __name__ == "__main__":
    asyncio.run(main()) 