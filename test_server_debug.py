#!/usr/bin/env python3
"""
Debug script to test server startup and identify issues.
"""

import asyncio
import sys
import traceback

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    try:
        from services.api_gateway.main import app
        print("✅ API Gateway imports successfully")
    except Exception as e:
        print(f"❌ API Gateway import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from services.api_gateway.integration_layer import UniversalKnowledgePlatformIntegration
        print("✅ Integration layer imports successfully")
    except Exception as e:
        print(f"❌ Integration layer import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from shared.core.llm_client import LLMClient
        print("✅ LLM Client imports successfully")
    except Exception as e:
        print(f"❌ LLM Client import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        print("✅ Lead Orchestrator imports successfully")
    except Exception as e:
        print(f"❌ Lead Orchestrator import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

async def test_integration_layer():
    """Test integration layer initialization."""
    print("\n🔍 Testing integration layer initialization...")
    
    try:
        from services.api_gateway.integration_layer import UniversalKnowledgePlatformIntegration
        
        integration = UniversalKnowledgePlatformIntegration()
        print("✅ Integration layer initialized successfully")
        
        # Test a simple query
        from services.api_gateway.integration_layer import IntegrationRequest
        
        request = IntegrationRequest(
            query="What is Python?",
            user_id="test_user",
            session_id="test_session"
        )
        
        print("✅ Integration request created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration layer test failed: {e}")
        traceback.print_exc()
        return False

async def test_llm_client():
    """Test LLM client initialization."""
    print("\n🔍 Testing LLM client initialization...")
    
    try:
        from shared.core.llm_client import LLMClient
        
        client = LLMClient()
        print("✅ LLM Client initialized successfully")
        
        # Test async method
        result = await client.generate_text("Hello world", max_tokens=10)
        print(f"✅ LLM Client async test successful: {result[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Client test failed: {e}")
        traceback.print_exc()
        return False

async def test_orchestrator():
    """Test orchestrator initialization."""
    print("\n🔍 Testing orchestrator initialization...")
    
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        
        orchestrator = LeadOrchestrator()
        print("✅ Lead Orchestrator initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Lead Orchestrator test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting server debug tests...")
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return
    
    # Test integration layer
    if not await test_integration_layer():
        print("❌ Integration layer test failed")
        return
    
    # Test LLM client
    if not await test_llm_client():
        print("❌ LLM client test failed")
        return
    
    # Test orchestrator
    if not await test_orchestrator():
        print("❌ Orchestrator test failed")
        return
    
    print("\n🎉 All tests passed! Server should be working.")

if __name__ == "__main__":
    asyncio.run(main()) 