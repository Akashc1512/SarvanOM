#!/usr/bin/env python3
"""
Quick Start Zero Budget LLM
Simple script to test and use the zero-budget LLM integration
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

from shared.core.llm_client_v3 import EnhancedLLMClientV3
from shared.core.model_selector import get_model_selector

def print_banner():
    """Print the welcome banner."""
    print("=" * 60)
    print("🚀 Zero Budget LLM Quick Start")
    print("=" * 60)
    print("This script will help you test the zero-budget LLM integration")
    print("with Ollama and Hugging Face providers.")
    print("=" * 60)

async def test_basic_functionality():
    """Test basic LLM functionality."""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        # Initialize the enhanced LLM client
        client = EnhancedLLMClientV3()
        
        # Test simple generation
        print("📝 Testing text generation...")
        response = await client.generate_text(
            prompt="Hello! Can you tell me a short joke?",
            max_tokens=50,
            temperature=0.7
        )
        
        print(f"✅ Response: {response}")
        
        # Test with dynamic model selection
        print("\n🎯 Testing dynamic model selection...")
        response = await client.generate_text(
            prompt="Write a simple Python function to calculate the factorial of a number.",
            max_tokens=100,
            temperature=0.1,
            use_dynamic_selection=True
        )
        
        print(f"✅ Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_model_selection():
    """Test model selection functionality."""
    print("\n🎯 Testing Model Selection...")
    
    try:
        # Initialize model selector
        selector = get_model_selector()
        
        # Test different query types
        test_queries = [
            ("What is the weather like?", "general"),
            ("Write a Python function", "code"),
            ("Analyze the benefits of renewable energy", "analytical"),
            ("Tell me a joke", "creative")
        ]
        
        for query, expected_type in test_queries:
            print(f"\n🔍 Query: {query}")
            result = await selector.select_model(query)
            
            print(f"   Selected Model: {result.selected_model}")
            print(f"   Provider: {result.selected_provider.value}")
            print(f"   Cost: ${result.estimated_cost:.6f}")
            print(f"   Reasoning: {result.reasoning[:80]}...")
            
            # Check if free model was selected
            if result.estimated_cost == 0.0:
                print("   ✅ FREE MODEL SELECTED!")
            else:
                print(f"   💰 Paid model: ${result.estimated_cost:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model selection test failed: {e}")
        return False

async def test_provider_health():
    """Test provider health status."""
    print("\n🏥 Testing Provider Health...")
    
    try:
        client = EnhancedLLMClientV3()
        
        # Check health status
        health_status = await client.health_check()
        
        print("Provider Health Status:")
        for provider, status in health_status.items():
            status_icon = "🟢" if status else "🔴"
            print(f"   {status_icon} {provider}: {'Healthy' if status else 'Unhealthy'}")
        
        # Get provider info
        print("\nProvider Information:")
        for provider in client.providers:
            info = provider.get_provider_info()
            print(f"   {info['provider']}: {info['model']}")
            print(f"      Cost: ${info['cost_per_1k_tokens']:.6f}/1K tokens")
            print(f"      Capabilities: {', '.join(info['capabilities'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def interactive_demo():
    """Run an interactive demo."""
    print("\n🎮 Interactive Demo")
    print("Type your questions and see the zero-budget LLM in action!")
    print("Type 'quit' to exit.")
    
    try:
        client = EnhancedLLMClientV3()
        
        while True:
            user_input = input("\n🤔 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                print("🤖 Thinking...")
                response = await client.generate_text(
                    prompt=user_input,
                    max_tokens=200,
                    temperature=0.3,
                    use_dynamic_selection=True
                )
                
                print(f"💡 Answer: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Try a different question or check your setup.")
    
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")

def show_setup_instructions():
    """Show setup instructions."""
    print("\n📋 Setup Instructions:")
    print("=" * 60)
    
    print("\n1. 🚀 Automated Setup (Recommended):")
    print("   python scripts/setup_ollama_huggingface.py")
    
    print("\n2. 🔧 Manual Setup:")
    print("   # Install Ollama")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print("   ")
    print("   # Pull models")
    print("   ollama pull llama3.2:3b")
    print("   ollama pull llama3.2:8b")
    print("   ollama pull codellama:7b")
    print("   ollama pull phi3:mini")
    print("   ")
    print("   # Optional: Hugging Face")
    print("   # Get API key from: https://huggingface.co/settings/tokens")
    print("   export HUGGINGFACE_API_KEY=your_key_here")
    
    print("\n3. 🧪 Test Setup:")
    print("   python test_updated_logic.py")
    print("   python test_llm_integration.py")
    
    print("\n4. 📊 Monitor Usage:")
    print("   python scripts/manage_zero_budget_llm.py --dashboard")
    
    print("\n5. 📚 Read Documentation:")
    print("   ZERO_BUDGET_LLM_INTEGRATION_GUIDE.md")

def show_cost_savings():
    """Show cost savings information."""
    print("\n💰 Cost Savings Analysis:")
    print("=" * 60)
    
    print("\n📊 Current Costs (Paid Providers):")
    print("   GPT-4: $0.03 per 1K tokens")
    print("   Claude: $0.015 per 1K tokens")
    print("   GPT-3.5: $0.0015 per 1K tokens")
    
    print("\n🎯 Zero Budget Alternatives:")
    print("   Ollama (Local): $0.00 per 1K tokens")
    print("   Hugging Face (API): $0.00 per 1K tokens")
    
    print("\n💡 Monthly Savings (10K requests):")
    print("   GPT-4: $300.00 → $0.00 (Save $300)")
    print("   Claude: $150.00 → $0.00 (Save $150)")
    print("   GPT-3.5: $15.00 → $0.00 (Save $15)")
    
    print("\n🚀 Total Potential Savings: $800-1600/month")

async def main():
    """Main function."""
    print_banner()
    
    # Check if setup is needed
    print("\n🔍 Checking setup status...")
    
    # Test basic functionality
    basic_test = await test_basic_functionality()
    
    if basic_test:
        print("\n✅ Basic functionality working!")
        
        # Test model selection
        await test_model_selection()
        
        # Test provider health
        await test_provider_health()
        
        # Show cost savings
        show_cost_savings()
        
        # Offer interactive demo
        print("\n🎮 Would you like to try an interactive demo?")
        response = input("   (y/N): ").lower().strip()
        
        if response == 'y':
            await interactive_demo()
        else:
            print("\n📚 Check out the documentation for more features!")
            print("   ZERO_BUDGET_LLM_INTEGRATION_GUIDE.md")
    
    else:
        print("\n❌ Setup issues detected.")
        print("Please run the setup script first:")
        print("   python scripts/setup_ollama_huggingface.py")
        
        # Show setup instructions
        show_setup_instructions()
    
    print("\n🎉 Zero Budget LLM Integration Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 