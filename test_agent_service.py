"""
Test script for Agent Service Migration

This script tests the migrated agent service and router components
to ensure they work correctly in the clean architecture.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.agents.agent_service import AgentService
from backend.services.agents.agent_coordinator import AgentCoordinator
from backend.services.agents.agent_factory import AgentFactory
from backend.models.domain.agent import Agent, AgentType, AgentStatus


async def test_agent_service():
    """Test the migrated agent service."""
    print("Testing Agent Service Migration...")
    
    try:
        # Test AgentService initialization
        print("1. Testing AgentService initialization...")
        agent_service = AgentService()
        print("✅ AgentService initialized successfully")
        
        # Test health status
        print("2. Testing health status...")
        health_status = await agent_service.get_health_status()
        print(f"✅ Health status: {health_status['overall_status']}")
        
        # Test status info
        print("3. Testing status info...")
        status_info = await agent_service.get_status_info()
        print(f"✅ Status info: {status_info['total_agents']} total agents")
        
        # Test browser search
        print("4. Testing browser search...")
        search_results = await agent_service.execute_browser_search(
            query="test query",
            search_type="web",
            max_results=5
        )
        print(f"✅ Browser search completed: {search_results['total_results']} results")
        
        # Test browser content extraction
        print("5. Testing browser content extraction...")
        extraction_results = await agent_service.extract_browser_content(
            url="https://example.com",
            extraction_type="full"
        )
        print(f"✅ Content extraction completed for: {extraction_results['url']}")
        
        # Test PDF processing
        print("6. Testing PDF processing...")
        pdf_results = await agent_service.process_pdf(
            file_data="test file data",
            extraction_type="text"
        )
        print(f"✅ PDF processing completed: {pdf_results['pages']} pages")
        
        # Test knowledge graph query
        print("7. Testing knowledge graph query...")
        knowledge_results = await agent_service.query_knowledge_graph(
            query="test knowledge query",
            query_type="entities"
        )
        print(f"✅ Knowledge graph query completed: {len(knowledge_results['entities'])} entities")
        
        # Test code execution
        print("8. Testing code execution...")
        code_results = await agent_service.execute_code(
            code="print('Hello, World!')",
            language="python"
        )
        print(f"✅ Code execution completed: {code_results['language']}")
        
        # Test database query
        print("9. Testing database query...")
        db_results = await agent_service.execute_database_query(
            query="SELECT * FROM test",
            database_type="postgres"
        )
        print(f"✅ Database query completed: {db_results['row_count']} rows")
        
        # Test website crawling
        print("10. Testing website crawling...")
        crawl_results = await agent_service.crawl_website(
            url="https://example.com",
            crawl_type="full"
        )
        print(f"✅ Website crawling completed: {crawl_results['pages_crawled']} pages")
        print(f"   - Content length: {len(crawl_results['content'])} characters")
        print(f"   - Links found: {len(crawl_results['links'])}")
        
        # Test agent history
        print("11. Testing agent history...")
        history = await agent_service.get_agent_history()
        print(f"✅ Agent history retrieved: {len(history)} entries")
        
        # Test agent cleanup
        print("12. Testing agent cleanup...")
        cleanup_results = await agent_service.cleanup_agents()
        print(f"✅ Agent cleanup completed: {cleanup_results['cleaned_count']} agents cleaned")
        
        print("\n🎉 All agent service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_coordinator():
    """Test the agent coordinator."""
    print("\nTesting Agent Coordinator...")
    
    try:
        coordinator = AgentCoordinator()
        print("✅ AgentCoordinator initialized successfully")
        
        # Test getting all agent status
        statuses = await coordinator.get_all_agent_status()
        print(f"✅ Agent statuses retrieved: {len(statuses)} agents")
        
        # Test getting agent by type
        agent = await coordinator.get_agent(AgentType.RETRIEVAL)
        print(f"✅ Retrieved agent by type: {agent.agent_type}")
        
        # Test getting agent status
        status = await coordinator.get_agent_status(agent.id)
        if status:
            print(f"✅ Retrieved agent status: {status['status']}")
        else:
            print("✅ No agent status found (expected for new agent)")
        
        # Test cleanup
        cleaned_count = await coordinator.cleanup_inactive_agents()
        print(f"✅ Cleanup completed: {cleaned_count} agents cleaned")
        
        print("🎉 All agent coordinator tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent coordinator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_factory():
    """Test the agent factory."""
    print("\nTesting Agent Factory...")
    
    try:
        factory = AgentFactory()
        print("✅ AgentFactory initialized successfully")
        
        # Test creating different agent types
        retrieval_agent = await factory.create_agent(AgentType.RETRIEVAL)
        print(f"✅ Created retrieval agent: {retrieval_agent.agent_type}")
        
        synthesis_agent = await factory.create_agent(AgentType.SYNTHESIS)
        print(f"✅ Created synthesis agent: {synthesis_agent.agent_type}")
        
        fact_check_agent = await factory.create_agent(AgentType.FACT_CHECK)
        print(f"✅ Created fact check agent: {fact_check_agent.agent_type}")
        
        print("🎉 All agent factory tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all agent service tests."""
    print("🧪 Starting Agent Service Migration Tests")
    print("=" * 50)
    
    # Test agent factory
    factory_success = await test_agent_factory()
    
    # Test agent coordinator
    coordinator_success = await test_agent_coordinator()
    
    # Test agent service
    service_success = await test_agent_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Agent Factory: {'✅ PASSED' if factory_success else '❌ FAILED'}")
    print(f"Agent Coordinator: {'✅ PASSED' if coordinator_success else '❌ FAILED'}")
    print(f"Agent Service: {'✅ PASSED' if service_success else '❌ FAILED'}")
    
    if all([factory_success, coordinator_success, service_success]):
        print("\n🎉 All agent service migration tests passed!")
        return True
    else:
        print("\n❌ Some agent service migration tests failed!")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 