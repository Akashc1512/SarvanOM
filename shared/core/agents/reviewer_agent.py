"""
Reviewer Agent - Expert validator to critique and improve draft answers.

Asynchronous agent that takes the original question, a draft answer, and optional
sources, then asks an LLM to review, correct, and improve the answer. Returns a
finalized answer and structured feedback.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from shared.core.agents.base_agent import BaseAgent, AgentType
from shared.core.agents.agent_utilities import (
    AgentTaskProcessor,
    CommonValidators,
    ResponseFormatter,
    time_agent_function,
)
from shared.core.unified_logging import get_logger


logger = get_logger(__name__)


@dataclass
class ReviewResult:
    approved: bool
    final_answer: str
    feedback: str
    confidence: float


class ReviewerAgent(BaseAgent):
    """Expert reviewer that validates and improves draft answers."""

    def __init__(self) -> None:
        super().__init__(agent_id="reviewer_agent", agent_type=AgentType.SYNTHESIS)
        # Note: Using SYNTHESIS type to avoid expanding enums across codebase.
        self.task_processor = AgentTaskProcessor(self.agent_id)
        self.logger = get_logger(f"{__name__}.{self.agent_id}")

    @time_agent_function("reviewer_agent")
    async def process_task(self, task: Dict[str, Any], context: Any) -> Dict[str, Any]:
        result = await self.task_processor.process_task_with_workflow(
            task=task,
            context=context,
            processing_func=self._process_review,
            validation_func=CommonValidators.validate_required_fields,
            timeout_seconds=45,
            required_fields=["question", "draft_answer"],
        )

        return ResponseFormatter.format_agent_response(
            success=result.success,
            data=result.data,
            error=result.error,
            confidence=result.confidence,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )

    async def _process_review(self, task: Dict[str, Any], context: Any) -> Dict[str, Any]:
        question: str = task.get("question", "").strip()
        draft_answer: str = task.get("draft_answer", "").strip()
        sources: Optional[List[Dict[str, Any]]] = task.get("sources")

        # Get configuration
        try:
            from shared.core.config import get_central_config
            config = get_central_config()
            temperature = config.reviewer_temperature
            max_tokens = config.reviewer_max_tokens
            timeout_seconds = config.reviewer_timeout_seconds
        except Exception:
            temperature = 0.2
            max_tokens = 800
            timeout_seconds = 45

        # Build the reviewer prompt
        sources_text = ""
        if sources:
            try:
                src_lines = []
                for s in sources[:10]:
                    title = s.get("title") or s.get("source") or "source"
                    snippet = (s.get("content") or "")[:300]
                    src_lines.append(f"- {title}: {snippet}")
                sources_text = "\nSources:\n" + "\n".join(src_lines)
            except Exception:
                sources_text = ""

        review_prompt = (
            "You are a domain expert reviewer. Given the user question and the draft answer, "
            "critique the answer for factual accuracy, completeness, clarity, and safety. "
            "If the answer is correct, explicitly state APPROVED and optionally small tweaks. "
            "If improvements are needed, provide a corrected FINAL ANSWER.\n\n"
            f"Question: {question}\n\nDraft Answer:\n{draft_answer}\n\n"
            f"{sources_text}\n\n"
            "Respond in the following JSON-like format:\n"
            "approved: true|false\n"
            "final_answer: <improved or confirmed answer>\n"
            "feedback: <specific critique and reasoning>"
        )

        try:
            # Prefer the agent-level LLM wrapper for consistency
            from shared.core.agents.llm_client import LLMClient

            llm = LLMClient()
            response_text: str = await llm.generate_text(review_prompt, max_tokens=max_tokens, temperature=temperature)

            approved = ("approved: true" in response_text.lower()) or ("approved" in response_text.lower() and "false" not in response_text.lower())

            # Heuristic parsing of final answer and feedback
            final_answer = draft_answer
            feedback = response_text.strip()

            # Try to extract lines
            for line in response_text.splitlines():
                low = line.lower()
                if low.startswith("final_answer:") or low.startswith("final answer:"):
                    final_answer = line.split(":", 1)[1].strip() or final_answer
                elif low.startswith("feedback:"):
                    feedback = line.split(":", 1)[1].strip() or feedback

            confidence = 0.7 if approved else 0.6

            return {
                "approved": approved,
                "final_answer": final_answer,
                "feedback": feedback,
                "confidence": confidence,
            }

        except Exception as e:
            self.logger.warning(f"ReviewerAgent failed, falling back to draft: {e}")
            return {
                "approved": False,
                "final_answer": draft_answer,
                "feedback": "Reviewer unavailable; returning draft answer.",
                "confidence": 0.5,
            }


