"""
FactCheck Agent - Verifies claims against documents using shared utilities.

This agent has been refactored to use shared utilities for:
- Task processing workflow
- Error handling and response formatting
- Input validation
- Performance monitoring
- Result standardization

This eliminates duplicate logic and ensures consistent behavior.
"""

import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from shared.core.agents.base_agent import BaseAgent, AgentType
# Import utilities from local modules
from .task_processor import AgentTaskProcessor
from .common_validators import CommonValidators
from shared.core.utilities.response_utilities import ResponseFormatter
from .agent_decorators import time_agent_function
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


@dataclass
class Claim:
    """Represents a claim to be verified."""

    text: str
    confidence: float = 0.5
    source: str = "extracted"
    metadata: Dict[str, Any] = None


@dataclass
class Verification:
    """Represents the verification result of a claim."""

    claim: str
    is_supported: bool
    confidence: float
    evidence: List[str]
    contradicting_evidence: List[str]
    source_documents: List[str]
    verification_method: str


@dataclass
class VerifiedFactModel:
    """Represents a verified fact with confidence and source."""

    claim: str
    confidence: float
    source: str
    evidence: List[str] = None
    metadata: Dict[str, Any] = None


class FactCheckAgent(BaseAgent):
    """Agent for fact-checking claims against documents using shared utilities."""

    def __init__(self):
        """Initialize the fact-check agent with shared utilities."""
        super().__init__(agent_id="factcheck_agent", agent_type=AgentType.FACT_CHECK)

        # Initialize shared utilities
        self.task_processor = AgentTaskProcessor(self.agent_id)
        self.logger = get_logger(f"{__name__}.{self.agent_id}")

        # Manual review callback
        self.manual_review_callback: Optional[Callable] = None

        logger.info("✅ FactCheckAgent initialized successfully")

    def set_manual_review_callback(self, callback: Callable):
        """Set callback for manual review of contested claims."""
        self.manual_review_callback = callback

    @time_agent_function("factcheck_agent")
    async def process_task(self, task: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Process fact-checking task using shared utilities.

        This method now uses the standardized workflow from AgentTaskProcessor
        to eliminate duplicate logic and ensure consistent behavior.
        """
        # Use shared task processor with validation
        result = await self.task_processor.process_task_with_workflow(
            task=task,
            context=context,
            processing_func=self._process_fact_checking,
            validation_func=CommonValidators.validate_documents_input,
            timeout_seconds=60,
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

    async def _process_fact_checking(
        self, task: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """
        Core fact-checking processing logic.

        This method contains the actual fact-checking logic, separated from
        the workflow management for better testability and maintainability.
        """
        # Extract task data using shared utilities
        task_data = await CommonProcessors.extract_task_data(
            task, ["documents", "query"]
        )

        documents = task_data.get("documents", [])
        query = task_data.get("query", "")

        self.logger.info(f"Fact-checking for query: {query[:50]}...")
        self.logger.info(f"Number of documents: {len(documents)}")

        # Extract claims from query and documents
        claims = await self._extract_claims(query, documents)

        # Verify claims against documents
        verifications = await self._verify_claims(claims, documents)

        # Filter verified facts
        verified_facts = self._filter_verified_facts(verifications)

        # Handle contested claims
        contested_claims = self._identify_contested_claims(verifications)
        if contested_claims and self.manual_review_callback:
            await self._request_manual_review(contested_claims)

        # Calculate confidence using shared utilities
        confidence = CommonProcessors.calculate_confidence(
            {"verifications": verifications, "verified_facts": verified_facts},
            ["verifications", "verified_facts"],
        )

        return {
            "verified_facts": verified_facts,
            "contested_claims": contested_claims,
            "verification_method": "rule_based",
            "total_claims": len(verifications),
            "confidence": confidence,
        }

    async def _extract_claims(self, query: str, documents: List[Dict]) -> List[Claim]:
        """
        Extract claims from query and documents.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            List of claims to verify
        """
        claims = []

        # Extract claims from query
        query_claims = self._extract_claims_from_text(query)
        claims.extend(query_claims)

        # Extract claims from documents
        for doc in documents:
            content = doc.get("content", "")
            if content:
                doc_claims = self._extract_claims_from_text(content)
                claims.extend(doc_claims)

        # Deduplicate claims
        return self._deduplicate_claims(claims)

    def _extract_claims_from_text(self, text: str) -> List[Claim]:
        """
        Extract factual claims from text.

        Args:
            text: Text to extract claims from

        Returns:
            List of extracted claims
        """
        claims = []
        sentences = text.split(". ")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if sentence contains factual information
            if self._is_factual_statement(sentence):
                confidence = self._calculate_claim_confidence(sentence)
                claim = Claim(
                    text=sentence,
                    confidence=confidence,
                    source="extracted",
                    metadata={"extraction_method": "rule_based"},
                )
                claims.append(claim)

        return claims

    def _is_factual_statement(self, sentence: str) -> bool:
        """
        Determine if a sentence contains factual information.

        Args:
            sentence: Sentence to analyze

        Returns:
            True if sentence contains factual information
        """
        sentence_lower = sentence.lower()

        # Skip questions
        if sentence_lower.startswith(("what", "how", "why", "when", "where", "who")):
            return False

        # Skip opinions and subjective statements
        opinion_indicators = [
            "i think",
            "i believe",
            "in my opinion",
            "it seems",
            "appears",
            "might",
            "could",
            "possibly",
            "probably",
            "maybe",
        ]
        if any(indicator in sentence_lower for indicator in opinion_indicators):
            return False

        # Look for factual indicators
        factual_indicators = [
            "is",
            "are",
            "was",
            "were",
            "has",
            "have",
            "had",
            "contains",
            "includes",
            "consists of",
            "comprises",
            "located",
            "situated",
            "found",
            "discovered",
            "established",
            "founded",
            "created",
            "built",
            "population",
            "area",
            "size",
            "length",
            "width",
            "temperature",
            "pressure",
            "speed",
            "time",
            "date",
        ]

        return any(indicator in sentence_lower for indicator in factual_indicators)

    def _calculate_claim_confidence(self, sentence: str) -> float:
        """
        Calculate confidence score for a claim.

        Args:
            sentence: Sentence containing the claim

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence for specific factual patterns
        if any(word in sentence.lower() for word in ["is", "are", "was", "were"]):
            confidence += 0.2

        # Increase confidence for numerical information
        if any(char.isdigit() for char in sentence):
            confidence += 0.1

        # Increase confidence for specific factual terms
        factual_terms = ["population", "area", "size", "temperature", "date"]
        if any(term in sentence.lower() for term in factual_terms):
            confidence += 0.1

        # Decrease confidence for uncertain language
        uncertain_terms = ["might", "could", "possibly", "probably", "maybe"]
        if any(term in sentence.lower() for term in uncertain_terms):
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _deduplicate_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Remove duplicate claims based on similarity.

        Args:
            claims: List of claims to deduplicate

        Returns:
            Deduplicated list of claims
        """
        if not claims:
            return claims

        unique_claims = []
        seen_texts = set()

        for claim in claims:
            # Normalize claim text for comparison
            normalized_text = claim.text.lower().strip()
            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                unique_claims.append(claim)

        return unique_claims

    async def _verify_claims(
        self, claims: List[Claim], documents: List[Dict]
    ) -> List[Verification]:
        """
        Verify claims against documents.

        Args:
            claims: Claims to verify
            documents: Documents to verify against

        Returns:
            List of verification results
        """
        verifications = []

        for claim in claims:
            verification = await self._verify_single_claim(claim, documents)
            verifications.append(verification)

        return verifications

    async def _verify_single_claim(
        self, claim: Claim, documents: List[Dict]
    ) -> Verification:
        """
        Verify a single claim against documents.

        Args:
            claim: Claim to verify
            documents: Documents to verify against

        Returns:
            Verification result
        """
        supporting_evidence = []
        contradicting_evidence = []
        source_documents = []

        for doc in documents:
            content = doc.get("content", "")
            if not content:
                continue

            # Analyze evidence with LLM if available
            try:
                analysis = await self._analyze_evidence_with_llm(claim.text, content)

                if analysis.get("supports", False):
                    supporting_evidence.append(content[:200] + "...")
                    source_documents.append(doc.get("source", "unknown"))

                if analysis.get("contradicts", False):
                    contradicting_evidence.append(content[:200] + "...")
                    source_documents.append(doc.get("source", "unknown"))

            except Exception as e:
                # Fallback to rule-based analysis
                self.logger.warning(f"LLM analysis failed, using fallback: {e}")
                fallback_analysis = self._fallback_evidence_analysis(
                    claim.text, content
                )

                if fallback_analysis.get("supports", False):
                    supporting_evidence.append(content[:200] + "...")
                    source_documents.append(doc.get("source", "unknown"))

                if fallback_analysis.get("contradicts", False):
                    contradicting_evidence.append(content[:200] + "...")
                    source_documents.append(doc.get("source", "unknown"))

        # Determine verification result
        is_supported = len(supporting_evidence) > 0
        confidence = self._calculate_verification_confidence(
            supporting_evidence, contradicting_evidence
        )

        return Verification(
            claim=claim.text,
            is_supported=is_supported,
            confidence=confidence,
            evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            source_documents=list(set(source_documents)),
            verification_method="llm_enhanced",
        )

    async def _analyze_evidence_with_llm(
        self, claim: str, document_content: str
    ) -> Dict[str, bool]:
        """
        Analyze evidence using LLM for more accurate verification.

        Args:
            claim: Claim to verify
            document_content: Document content to analyze

        Returns:
            Dictionary with support/contradiction analysis
        """
        try:
            from shared.core.llm_client_v3 import LLMClient, LLMRequest

            llm_client = LLMClient()

            # Create analysis prompt
            analysis_prompt = f"""
            Analyze whether the following document content supports or contradicts the claim.
            
            Claim: {claim}
            
            Document Content: {document_content[:1000]}
            
            Please analyze and respond with:
            - supports: true/false (whether the content supports the claim)
            - contradicts: true/false (whether the content contradicts the claim)
            - reasoning: brief explanation
            """

            llm_request = LLMRequest(
                prompt=analysis_prompt, max_tokens=200, temperature=0.1
            )

            response = await llm_client.generate_text(llm_request)

            # Parse response (simplified parsing)
            response_text = response.content.lower()

            return {
                "supports": "supports: true" in response_text
                or "supports: yes" in response_text,
                "contradicts": "contradicts: true" in response_text
                or "contradicts: yes" in response_text,
                "reasoning": response_text,
            }

        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return {
                "supports": False,
                "contradicts": False,
                "reasoning": "Analysis failed",
            }

    def _fallback_evidence_analysis(
        self, claim: str, document_content: str
    ) -> Dict[str, bool]:
        """
        Fallback rule-based evidence analysis.

        Args:
            claim: Claim to verify
            document_content: Document content to analyze

        Returns:
            Dictionary with support/contradiction analysis
        """
        claim_lower = claim.lower()
        content_lower = document_content.lower()

        # Extract keywords from claim
        claim_words = set(claim_lower.split())
        content_words = set(content_lower.split())

        # Calculate word overlap
        overlap = len(claim_words.intersection(content_words))
        overlap_ratio = overlap / len(claim_words) if claim_words else 0

        # Simple rule-based analysis
        supports = overlap_ratio > 0.3  # At least 30% word overlap
        contradicts = (
            False  # Would need more sophisticated logic for contradiction detection
        )

        return {
            "supports": supports,
            "contradicts": contradicts,
            "reasoning": f"Word overlap ratio: {overlap_ratio:.2f}",
        }

    def _filter_verified_facts(
        self, verifications: List[Verification]
    ) -> List[VerifiedFactModel]:
        """
        Filter verified facts from verification results.

        Args:
            verifications: List of verification results

        Returns:
            List of verified facts
        """
        verified_facts = []

        for verification in verifications:
            if verification.is_supported and verification.confidence > 0.6:
                fact = VerifiedFactModel(
                    claim=verification.claim,
                    confidence=verification.confidence,
                    source="verified",
                    evidence=verification.evidence,
                    metadata={
                        "verification_method": verification.verification_method,
                        "source_documents": verification.source_documents,
                    },
                )
                verified_facts.append(fact)

        return verified_facts

    def _identify_contested_claims(
        self, verifications: List[Verification]
    ) -> List[Dict]:
        """
        Identify claims that need manual review.

        Args:
            verifications: List of verification results

        Returns:
            List of contested claims for manual review
        """
        contested_claims = []

        for verification in verifications:
            # Claims with both supporting and contradicting evidence
            if verification.evidence and verification.contradicting_evidence:
                contested_claim = {
                    "claim": verification.claim,
                    "supporting_evidence": verification.evidence,
                    "contradicting_evidence": verification.contradicting_evidence,
                    "confidence": verification.confidence,
                    "source_documents": verification.source_documents,
                    "status": "needs_review",
                }
                contested_claims.append(contested_claim)

        return contested_claims

    async def _request_manual_review(self, contested_claims: List[Dict]):
        """Request manual review for contested claims."""
        if not self.manual_review_callback:
            return

        try:
            await self.manual_review_callback(contested_claims)
            self.logger.info(
                f"Requested manual review for {len(contested_claims)} claims"
            )
        except Exception as e:
            self.logger.error(f"Failed to request manual review: {e}")

    async def _store_contested_claims(self, contested_claims: List[Dict]):
        """Store contested claims for later review."""
        try:
            # Store in database or file system
            review_request = {
                "timestamp": time.time(),
                "claims": contested_claims,
                "status": "pending",
            }

            await self._save_review_request(review_request)
            self.logger.info(f"Stored {len(contested_claims)} contested claims")

        except Exception as e:
            self.logger.error(f"Failed to store contested claims: {e}")

    async def _save_review_request(self, review_request: Dict):
        """Save review request to storage."""
        # Implementation would depend on storage backend
        # For now, just log the request
        self.logger.info(f"Review request saved: {review_request}")

    async def get_pending_reviews(self) -> List[Dict]:
        """Get pending review requests."""
        # Implementation would depend on storage backend
        # For now, return empty list
        return []

    async def update_review_decision(self, review_id: str, decision: Dict):
        """Update review decision."""
        # Implementation would depend on storage backend
        self.logger.info(f"Review decision updated: {review_id} -> {decision}")

    def _calculate_verification_confidence(
        self, supporting_evidence: List[str], contradicting_evidence: List[str]
    ) -> float:
        """
        Calculate confidence based on evidence quality and quantity.

        Args:
            supporting_evidence: List of supporting evidence
            contradicting_evidence: List of contradicting evidence

        Returns:
            Confidence score between 0 and 1
        """
        if not supporting_evidence and not contradicting_evidence:
            return 0.0

        # Base confidence on evidence quantity
        total_evidence = len(supporting_evidence) + len(contradicting_evidence)
        evidence_confidence = min(total_evidence / 5.0, 1.0)

        # Adjust based on evidence balance
        if supporting_evidence and not contradicting_evidence:
            balance_confidence = 1.0
        elif contradicting_evidence and not supporting_evidence:
            balance_confidence = 0.0
        else:
            # Mixed evidence - lower confidence
            balance_confidence = 0.5

        # Combine confidences
        final_confidence = (evidence_confidence + balance_confidence) / 2
        return min(1.0, max(0.0, final_confidence))


async def main():
    """Test the fact-check agent."""
    agent = FactCheckAgent()

    # Test task
    task = {
        "documents": [
            {"content": "Paris is the capital of France.", "source": "test"},
            {"content": "The population of Paris is 2.1 million.", "source": "test"},
        ],
        "query": "What is the capital of France?",
    }

    result = await agent.process_task(task, {})
    print(f"Fact-check result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
