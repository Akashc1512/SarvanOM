"""
Tests for ReviewerAgent functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch

from shared.core.agents.reviewer_agent import ReviewerAgent


pytestmark = pytest.mark.asyncio


class TestReviewerAgent:
    """Test cases for ReviewerAgent."""

    @pytest.fixture
    def agent(self):
        return ReviewerAgent()

    @pytest.fixture
    def mock_llm_response(self):
        return "approved: true\nfinal_answer: The capital of France is Paris.\nfeedback: Answer is correct and complete."

    async def test_reviewer_approves_good_answer(self, agent, mock_llm_response):
        """Test that reviewer approves a good answer."""
        with patch("shared.core.agents.llm_client.LLMClient") as mock_llm:
            mock_client = AsyncMock()
            mock_client.generate_text.return_value = mock_llm_response
            mock_llm.return_value = mock_client

            task = {
                "question": "What is the capital of France?",
                "draft_answer": "The capital of France is Paris.",
            }

            result = await agent.process_task(task, {})

            assert result["success"] is True
            data = result["data"]
            assert data["approved"] is True
            assert "Paris" in data["final_answer"]
            assert data["confidence"] > 0.5

    async def test_reviewer_improves_bad_answer(self, agent):
        """Test that reviewer improves a bad answer."""
        mock_response = "approved: false\nfinal_answer: The capital of France is Paris.\nfeedback: The answer was incorrect."

        with patch("shared.core.agents.llm_client.LLMClient") as mock_llm:
            mock_client = AsyncMock()
            mock_client.generate_text.return_value = mock_response
            mock_llm.return_value = mock_client

            task = {
                "question": "What is the capital of France?",
                "draft_answer": "The capital of France is London.",
            }

            result = await agent.process_task(task, {})

            assert result["success"] is True
            data = result["data"]
            assert data["approved"] is False
            assert "Paris" in data["final_answer"]
            assert "London" not in data["final_answer"]

    async def test_reviewer_fallback_on_error(self, agent):
        """Test that reviewer falls back to draft answer on error."""
        with patch("shared.core.agents.llm_client.LLMClient") as mock_llm:
            mock_client = AsyncMock()
            mock_client.generate_text.side_effect = Exception("LLM error")
            mock_llm.return_value = mock_client

            task = {
                "question": "What is the capital of France?",
                "draft_answer": "The capital of France is Paris.",
            }

            result = await agent.process_task(task, {})

            assert result["success"] is True
            data = result["data"]
            assert data["approved"] is False
            assert data["final_answer"] == "The capital of France is Paris."
            assert "unavailable" in data["feedback"]

    async def test_reviewer_with_sources(self, agent, mock_llm_response):
        """Test that reviewer includes sources in prompt."""
        with patch("shared.core.agents.llm_client.LLMClient") as mock_llm:
            mock_client = AsyncMock()
            mock_client.generate_text.return_value = mock_llm_response
            mock_llm.return_value = mock_client

            task = {
                "question": "What is the capital of France?",
                "draft_answer": "The capital of France is Paris.",
                "sources": [
                    {"title": "Geography Book", "content": "Paris is the capital of France."},
                    {"title": "Wikipedia", "content": "France's capital city is Paris."},
                ],
            }

            result = await agent.process_task(task, {})

            assert result["success"] is True
            # Verify that sources were included in the prompt
            mock_client.generate_text.assert_called_once()
            call_args = mock_client.generate_text.call_args[0][0]
            assert "Sources:" in call_args
            assert "Geography Book" in call_args

    async def test_reviewer_validation_failure(self, agent):
        """Test that reviewer fails validation for missing required fields."""
        task = {
            "question": "What is the capital of France?",
            # Missing draft_answer
        }

        result = await agent.process_task(task, {})

        assert result["success"] is False
        assert "error" in result
