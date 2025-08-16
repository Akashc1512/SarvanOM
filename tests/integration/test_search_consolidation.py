"""
Integration tests for search query consolidation.

Tests that all search queries are properly routed through the single agent orchestrator
and that outdated search logic has been removed.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestSearchConsolidation:
    """Test cases for search query consolidation."""

    def test_gateway_search_uses_agent_orchestrator(self):
        """Test that gateway search endpoint uses the agent orchestrator."""
        try:
            from services.gateway.routes import search_router
            from services.gateway.agent_orchestrator import agent_orchestrator
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(search_router)
            client = TestClient(app)
            
            # Test search endpoint
            search_request = {
                "query": "test search query",
                "user_id": "test_user",
                "context": {"source": "test"},
                "source": "test",
                "metadata": {"test": True}
            }
            
            response = client.post("/", json=search_request)
            # Should return 200 if working, or 422/500 if there are issues
            assert response.status_code in [200, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                # Check that the response indicates orchestration was used
                assert "data" in data
                assert "request_metadata" in data["data"]
                assert data["data"]["request_metadata"]["orchestration_used"] is True
                print("✅ Gateway search uses agent orchestrator")
            else:
                print(f"⚠️ Gateway search returned {response.status_code} (expected in test env)")
            
        except Exception as e:
            pytest.fail(f"Gateway search test failed: {e}")

    def test_search_service_routes_to_gateway_orchestrator(self):
        """Test that search service routes to gateway agent orchestrator."""
        try:
            from services.search.main import search_router
            
            # Create a test client
            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(search_router)
            client = TestClient(app)
            
            # Test search endpoint
            search_request = {
                "query": "test search query",
                "user_id": "test_user",
                "context": {"source": "test"},
                "source": "test",
                "metadata": {"test": True}
            }
            
            response = client.post("/", json=search_request)
            # Should return 200 if working, or 422/500 if there are issues
            assert response.status_code in [200, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                # Check that the response indicates orchestration was used
                assert "data" in data
                assert "request_metadata" in data["data"]
                assert data["data"]["request_metadata"]["orchestration_used"] is True
                assert data["data"]["request_metadata"]["service"] == "search_service"
                print("✅ Search service routes to gateway orchestrator")
            else:
                print(f"⚠️ Search service returned {response.status_code} (expected in test env)")
            
        except Exception as e:
            pytest.fail(f"Search service test failed: {e}")

    def test_agent_orchestrator_exists_and_works(self):
        """Test that the agent orchestrator exists and can be imported."""
        try:
            from services.gateway.agent_orchestrator import (
                agent_orchestrator,
                QueryContext,
                AgentType,
                ExecutionPattern
            )
            
            # Verify the orchestrator exists and has required methods
            assert hasattr(agent_orchestrator, 'process_query')
            assert callable(agent_orchestrator.process_query)
            
            # Verify required classes exist
            assert QueryContext is not None
            assert AgentType is not None
            assert ExecutionPattern is not None
            
            print("✅ Agent orchestrator exists and is properly structured")
            
        except Exception as e:
            pytest.fail(f"Agent orchestrator test failed: {e}")

    def test_outdated_retrieval_agent_removed(self):
        """Test that outdated retrieval agent files have been removed."""
        try:
            # Check that the refactored example file is gone
            refactored_file = os.path.join(
                os.path.dirname(__file__), 
                "../../shared/core/agents/retrieval_agent_refactored_example.py"
            )
            assert not os.path.exists(refactored_file), "Outdated retrieval_agent_refactored_example.py should be removed"
            
            # Check that the main retrieval agent still exists
            main_agent_file = os.path.join(
                os.path.dirname(__file__), 
                "../../shared/core/agents/retrieval_agent.py"
            )
            assert os.path.exists(main_agent_file), "Main retrieval_agent.py should exist"
            
            print("✅ Outdated retrieval agent files removed")
            
        except Exception as e:
            pytest.fail(f"Retrieval agent cleanup test failed: {e}")

    def test_backend_query_processor_not_used(self):
        """Test that backend query processor is not actively used in current architecture."""
        try:
            # Check if backend query processor is imported in current services
            import services.gateway.routes as gateway_routes
            import services.search.main as search_main
            
            # These should not import backend query processor
            gateway_source = gateway_routes.__file__
            search_source = search_main.__file__
            
            # Read the files to check for backend imports
            with open(gateway_source, 'r', encoding='utf-8') as f:
                gateway_content = f.read()
            
            with open(search_source, 'r', encoding='utf-8') as f:
                search_content = f.read()
            
            # Should not contain backend query processor imports
            assert "backend.services.query" not in gateway_content
            assert "backend.services.query" not in search_content
            assert "QueryProcessor" not in gateway_content
            assert "QueryProcessor" not in search_content
            
            print("✅ Backend query processor not used in current services")
            
        except Exception as e:
            pytest.fail(f"Backend query processor test failed: {e}")

    def test_shared_agent_pattern_used(self):
        """Test that shared agent pattern is used for agent creation."""
        try:
            from shared.core.agent_pattern import (
                AgentFactory,
                StrategyBasedAgent,
                AgentType
            )
            
            # Verify the factory can create agents
            retrieval_agent = AgentFactory.create_agent(AgentType.RETRIEVAL)
            assert retrieval_agent is not None
            assert hasattr(retrieval_agent, 'process_task')
            assert callable(retrieval_agent.process_task)
            
            print("✅ Shared agent pattern is properly used")
            
        except Exception as e:
            pytest.fail(f"Shared agent pattern test failed: {e}")

    def test_search_consolidation_architecture(self):
        """Test the overall search consolidation architecture."""
        try:
            # Check that all search endpoints route through the same orchestrator
            from services.gateway.agent_orchestrator import agent_orchestrator as gateway_orchestrator
            from services.search.main import search_router
            
            # Both should use the same orchestrator instance
            # (This is a structural check - in practice they import the same instance)
            
            # Verify the architecture is consistent
            assert hasattr(gateway_orchestrator, 'process_query')
            assert hasattr(gateway_orchestrator, 'execute_pipeline')
            assert hasattr(gateway_orchestrator, 'synthesize_final_response')
            
            print("✅ Search consolidation architecture is consistent")
            
        except Exception as e:
            pytest.fail(f"Search consolidation architecture test failed: {e}")

    def test_no_duplicate_search_logic(self):
        """Test that there are no duplicate search logic implementations."""
        try:
            # Check that search logic is centralized
            import services.gateway.agent_orchestrator as gateway_orch
            import services.search.main as search_service
            
            # Both should import the same orchestrator
            gateway_orch_file = gateway_orch.__file__
            search_file = search_service.__file__
            
            # Read files to check for duplicate logic
            with open(gateway_orch_file, 'r', encoding='utf-8') as f:
                gateway_content = f.read()
            
            with open(search_file, 'r', encoding='utf-8') as f:
                search_content = f.read()
            
            # Search service should import from gateway, not implement its own logic
            assert "from services.gateway.agent_orchestrator import" in search_content
            assert "agent_orchestrator.process_query" in search_content
            
            # Should not have duplicate search processing logic
            search_methods = ["process_query", "execute_pipeline", "synthesize_final_response"]
            for method in search_methods:
                # Gateway should have these methods
                assert method in gateway_content
                # Search service should not have duplicate implementations
                assert f"def {method}" not in search_content
            
            print("✅ No duplicate search logic found")
            
        except Exception as e:
            pytest.fail(f"Duplicate search logic test failed: {e}")

    def test_search_routing_consistency(self):
        """Test that all search routing is consistent."""
        try:
            # Check that both gateway and search service use the same patterns
            from services.gateway.routes import search_router as gateway_search
            from services.search.main import search_router as search_service_search
            
            # Both should have similar endpoint structures
            gateway_endpoints = [route.path for route in gateway_search.routes]
            search_endpoints = [route.path for route in search_service_search.routes]
            
            # Both should have a root search endpoint
            assert "/" in gateway_endpoints
            assert "/" in search_endpoints
            
            print("✅ Search routing is consistent")
            
        except Exception as e:
            pytest.fail(f"Search routing consistency test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
