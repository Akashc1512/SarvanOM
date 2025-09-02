"""
Synthesis Agent - Combines verified facts into coherent answers using shared utilities.

This agent has been refactored to use shared utilities for:
- Task processing workflow
- Error handling and response formatting
- Input validation
- Performance monitoring
- Result standardization

This eliminates duplicate logic and ensures consistent behavior.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from shared.core.agents.base_agent import BaseAgent, AgentType
# Import utilities from local modules
from .task_processor import AgentTaskProcessor
from .common_validators import CommonValidators
from .common_processors import CommonProcessors
from shared.core.utilities.response_utilities import ResponseFormatter
from .agent_decorators import time_agent_function
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


@dataclass
class VerifiedFact:
    """Represents a verified fact with confidence and source."""

    claim: str
    confidence: float
    source: str
    evidence: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SynthesisResult:
    """Represents a synthesis result with metadata."""

    answer: str
    synthesis_method: str
    fact_count: int
    processing_time_ms: int
    metadata: Dict[str, Any] = None

    def model_dump(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "answer": self.answer,
            "synthesis_method": self.synthesis_method,
            "fact_count": self.fact_count,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata or {},
        }


class SynthesisAgent(BaseAgent):
    """Agent for synthesizing verified facts into coherent answers using shared utilities."""

    def __init__(self):
        """Initialize the synthesis agent with shared utilities."""
        super().__init__(agent_id="synthesis_agent", agent_type=AgentType.SYNTHESIS)

        # Initialize shared utilities
        self.task_processor = AgentTaskProcessor(self.agent_id)
        self.logger = get_logger(f"{__name__}.{self.agent_id}")

        logger.info("✅ SynthesisAgent initialized successfully")

    @time_agent_function("synthesis_agent")
    async def process_task(self, task: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Process synthesis task using shared utilities.

        This method now uses the standardized workflow from AgentTaskProcessor
        to eliminate duplicate logic and ensure consistent behavior.
        """
        # Use shared task processor with validation
        result = await self.task_processor.process_task_with_workflow(
            task=task,
            context=context,
            processing_func=self._process_synthesis,
            validation_func=CommonValidators.validate_required_fields,
            timeout_seconds=60,
            required_fields=["verified_facts", "query"],
        )

        # Convert TaskResult to standard response format
        return ResponseFormatter.format_agent_response(
            success=result.success,
            data=result.data,
            error=result.error,
            confidence=result.confidence,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )

    async def _process_synthesis(
        self, task: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """
        Core synthesis processing logic.

        This method contains the actual synthesis logic, separated from
        the workflow management for better testability and maintainability.
        """
        # Extract task data using shared utilities
        task_data = await CommonProcessors.extract_task_data(
            task, ["verified_facts", "query", "synthesis_params"]
        )

        verified_facts = task_data.get("verified_facts", [])
        query = task_data.get("query", "")
        synthesis_params = task_data.get("synthesis_params", {})

        self.logger.info(f"Synthesizing answer for query: {query[:50]}...")
        self.logger.info(f"Number of verified facts: {len(verified_facts)}")

        # Synthesize answer
        synthesis_result = await self._synthesize_answer(
            verified_facts, query, synthesis_params
        )

        # Calculate confidence based on fact quality
        confidence = self._calculate_synthesis_confidence(verified_facts)

        return {
            "answer": synthesis_result,
            "synthesis_method": "rule_based",
            "fact_count": len(verified_facts),
            "confidence": confidence,
        }

    async def _synthesize_answer(
        self, verified_facts: List[Dict], query: str, params: Dict[str, Any]
    ) -> str:
        """
        Synthesize answer from verified facts using LLMClient with enhanced prompt templates.
        """
        if not verified_facts:
            return "I don't have enough verified information to provide a comprehensive answer."

        try:
            # Import prompt template manager
            from shared.core.prompt_templates import get_template_manager

            template_manager = get_template_manager()

            # Format documents for the enhanced template
            documents_with_sources = []
            for i, fact in enumerate(verified_facts, 1):
                # Handle both dictionary and object formats
                if hasattr(fact, "source"):
                    # Object format (VerifiedFactModel)
                    source = getattr(fact, "source", "Unknown source")
                    claim = getattr(fact, "claim", "")
                    confidence = getattr(fact, "confidence", 0)
                else:
                    # Dictionary format
                    source = fact.get("source", "Unknown source")
                    claim = fact.get("claim", "")
                    confidence = fact.get("confidence", 0)

                documents_with_sources.append(
                    {
                        "id": i,
                        "content": claim,
                        "source": source,
                        "confidence": confidence,
                    }
                )

            # Get synthesis template
            synthesis_template = template_manager.get_template("synthesis")

            # Format the synthesis prompt
            synthesis_prompt = synthesis_template.format(
                query=query, documents=documents_with_sources, **params
            )

            # Use LLM for synthesis
            from shared.core.llm_client_v3 import LLMClient, LLMRequest

            llm_client = LLMClient()

            # Create LLMRequest with system message for synthesis
            system_message = """You are an expert synthesis agent specializing in combining verified facts into coherent, accurate answers. Your role is to:

1. Analyze the provided verified facts
2. Synthesize them into a comprehensive answer
3. Ensure accuracy and coherence
4. Provide clear, well-structured responses
5. Maintain the factual integrity of the source information

Guidelines:
- Use only the provided verified facts
- Maintain accuracy and avoid speculation
- Structure your response logically
- Be comprehensive but concise
- Cite sources when appropriate
- Acknowledge any limitations in the available information"""

            llm_request = LLMRequest(
                prompt=synthesis_prompt,
                system_message=system_message,
                max_tokens=1000,
                temperature=0.3,  # Balanced creativity and accuracy
            )

            # Use dynamic model selection for synthesis
            response = await llm_client.generate_text(llm_request)

            return response.content

        except Exception as e:
            self.logger.error(f"LLM synthesis failed, using fallback: {e}")
            return self._fallback_synthesis(verified_facts, query)

    def _fallback_synthesis(self, verified_facts: List[Dict], query: str) -> str:
        """
        Fallback synthesis when LLM is unavailable.

        Args:
            verified_facts: List of verified facts
            query: User query

        Returns:
            Synthesized answer
        """
        if not verified_facts:
            return "I don't have enough verified information to provide a comprehensive answer."

        # Simple text-based synthesis
        answer_parts = []

        # Add query context
        answer_parts.append(f"Based on verified information about '{query}':")

        # Add facts
        for i, fact in enumerate(verified_facts, 1):
            if hasattr(fact, "claim"):
                claim = fact.claim
                confidence = fact.confidence
                source = fact.source
            else:
                claim = fact.get("claim", "")
                confidence = fact.get("confidence", 0)
                source = fact.get("source", "Unknown")

            if claim:
                answer_parts.append(
                    f"{i}. {claim} (Source: {source}, Confidence: {confidence:.2f})"
                )

        # Add summary
        answer_parts.append(
            f"\nThis synthesis is based on {len(verified_facts)} verified facts."
        )

        return "\n".join(answer_parts)

    def _calculate_synthesis_confidence(self, verified_facts: List[Dict]) -> float:
        """
        Calculate confidence for synthesis based on fact quality.

        Args:
            verified_facts: List of verified facts

        Returns:
            Confidence score between 0 and 1
        """
        if not verified_facts:
            return 0.0

        # Calculate average confidence of facts
        def get_confidence(fact):
            if hasattr(fact, "confidence"):
                return fact.confidence
            return fact.get("confidence", 0.5)

        confidences = [get_confidence(fact) for fact in verified_facts]
        avg_confidence = sum(confidences) / len(confidences)

        # Boost confidence based on number of facts
        fact_count_boost = min(len(verified_facts) / 10.0, 0.2)

        # Boost confidence based on fact quality (high confidence facts)
        high_confidence_facts = [c for c in confidences if c > 0.8]
        quality_boost = min(len(high_confidence_facts) / len(verified_facts), 0.3)

        final_confidence = avg_confidence + fact_count_boost + quality_boost
        return min(1.0, final_confidence)


async def main():
    """Test the synthesis agent."""
    agent = SynthesisAgent()

    # Test task
    task = {
        "verified_facts": [
            {
                "claim": "Paris is the capital of France.",
                "confidence": 0.9,
                "source": "verified_fact",
            },
            {
                "claim": "The population of Paris is approximately 2.1 million.",
                "confidence": 0.8,
                "source": "verified_fact",
            },
        ],
        "query": "What is the capital of France?",
        "synthesis_params": {"style": "informative", "length": "medium"},
    }

    result = await agent.process_task(task, {})
    print(f"Synthesis result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
