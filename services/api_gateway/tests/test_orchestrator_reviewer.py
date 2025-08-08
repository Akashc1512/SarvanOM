"""
Integration tests for orchestrator with reviewer agent.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.api_gateway.lead_orchestrator import LeadOrchestrator
from shared.core.agents.base_agent import AgentType, AgentResult


pytestmark = pytest.mark.asyncio


class TestOrchestratorReviewer:
    """Test orchestrator integration with reviewer agent."""

    @pytest.fixture
    def orchestrator(self):
        return LeadOrchestrator()

    @pytest.fixture
    def mock_synthesis_result(self):
        return AgentResult(
            success=True,
            data={"answer": "The capital of France is Paris."},
            confidence=0.8,
            execution_time_ms=1000
        )

    @pytest.fixture
    def mock_reviewer_response(self):
        return {
            "success": True,
            "data": {
                "approved": True,
                "final_answer": "The capital of France is Paris.",
                "feedback": "Answer is correct and complete.",
                "confidence": 0.9
            }
        }

    async def test_orchestrator_with_reviewer_enabled(self, orchestrator, mock_synthesis_result, mock_reviewer_response):
        """Test that orchestrator calls reviewer when enabled."""
        with patch("shared.core.config.central_config.get_central_config") as mock_config:
            mock_config.return_value.enable_reviewer_agent = True
            
            with patch.object(orchestrator.agents["REVIEWER"], "process_task") as mock_reviewer:
                mock_reviewer.return_value = mock_reviewer_response
                
                # Mock synthesis result
                results = {AgentType.SYNTHESIS: mock_synthesis_result}
                
                # Execute reviewer phase
                updated_results = await orchestrator._execute_reviewer_phase(
                    MagicMock(query="What is the capital of France?"), results
                )
                
                # Verify reviewer was called
                mock_reviewer.assert_called_once()
                call_args = mock_reviewer.call_args[0][0]
                assert call_args["question"] == "What is the capital of France?"
                assert call_args["draft_answer"] == "The capital of France is Paris."
                
                # Verify synthesis result was updated
                synth_result = updated_results[AgentType.SYNTHESIS]
                assert synth_result.data["answer"] == "The capital of France is Paris."
                assert "review_feedback" in synth_result.data
                assert synth_result.confidence >= 0.8

    async def test_orchestrator_with_reviewer_disabled(self, orchestrator, mock_synthesis_result):
        """Test that orchestrator skips reviewer when disabled."""
        with patch("shared.core.config.central_config.get_central_config") as mock_config:
            mock_config.return_value.enable_reviewer_agent = False
            
            with patch.object(orchestrator.agents["REVIEWER"], "process_task") as mock_reviewer:
                results = {AgentType.SYNTHESIS: mock_synthesis_result}
                
                # Execute reviewer phase
                updated_results = await orchestrator._execute_reviewer_phase(
                    MagicMock(query="What is the capital of France?"), results
                )
                
                # Verify reviewer was not called
                mock_reviewer.assert_not_called()
                
                # Verify results unchanged
                assert updated_results == results

    async def test_orchestrator_reviewer_timeout(self, orchestrator, mock_synthesis_result):
        """Test that orchestrator handles reviewer timeout gracefully."""
        with patch("shared.core.config.central_config.get_central_config") as mock_config:
            mock_config.return_value.enable_reviewer_agent = True
            
            with patch.object(orchestrator.agents["REVIEWER"], "process_task") as mock_reviewer:
                mock_reviewer.side_effect = asyncio.TimeoutError("Reviewer timeout")
                
                results = {AgentType.SYNTHESIS: mock_synthesis_result}
                
                # Execute reviewer phase
                updated_results = await orchestrator._execute_reviewer_phase(
                    MagicMock(query="What is the capital of France?"), results
                )
                
                # Verify results unchanged (fallback to draft)
                assert updated_results == results

    async def test_orchestrator_reviewer_with_sources(self, orchestrator, mock_synthesis_result, mock_reviewer_response):
        """Test that orchestrator passes sources to reviewer."""
        with patch("shared.core.config.central_config.get_central_config") as mock_config:
            mock_config.return_value.enable_reviewer_agent = True
            
            with patch.object(orchestrator.agents["REVIEWER"], "process_task") as mock_reviewer:
                mock_reviewer.return_value = mock_reviewer_response
                
                # Mock retrieval result with sources
                retrieval_result = AgentResult(
                    success=True,
                    data={"documents": [{"title": "Test", "content": "Paris is capital"}]},
                    confidence=0.8
                )
                results = {
                    AgentType.RETRIEVAL: retrieval_result,
                    AgentType.SYNTHESIS: mock_synthesis_result
                }
                
                # Execute reviewer phase
                await orchestrator._execute_reviewer_phase(
                    MagicMock(query="What is the capital of France?"), results
                )
                
                # Verify sources were passed
                call_args = mock_reviewer.call_args[0][0]
                assert "sources" in call_args
                assert len(call_args["sources"]) == 1
                assert call_args["sources"][0]["title"] == "Test"

    async def test_orchestrator_reviewer_improves_answer(self, orchestrator, mock_synthesis_result):
        """Test that orchestrator applies reviewer improvements."""
        with patch("shared.core.config.central_config.get_central_config") as mock_config:
            mock_config.return_value.enable_reviewer_agent = True
            
            improved_response = {
                "success": True,
                "data": {
                    "approved": False,
                    "final_answer": "The capital of France is Paris, located in northern France.",
                    "feedback": "Answer was incomplete, added location information.",
                    "confidence": 0.9
                }
            }
            
            with patch.object(orchestrator.agents["REVIEWER"], "process_task") as mock_reviewer:
                mock_reviewer.return_value = improved_response
                
                results = {AgentType.SYNTHESIS: mock_synthesis_result}
                
                # Execute reviewer phase
                updated_results = await orchestrator._execute_reviewer_phase(
                    MagicMock(query="What is the capital of France?"), results
                )
                
                # Verify synthesis result was improved
                synth_result = updated_results[AgentType.SYNTHESIS]
                assert "Paris, located in northern France" in synth_result.data["answer"]
                assert "incomplete" in synth_result.data["review_feedback"]
                assert synth_result.confidence == 0.9
