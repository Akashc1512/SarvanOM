"""
Clean Agent Pattern - MAANG Standards
Strategy/Factory pattern for reusable agent architecture.

Features:
- Strategy pattern for different agent types
- Factory pattern for agent creation
- Comprehensive prompt management
- Modular architecture
- Testable components
- Performance monitoring
- Error handling and recovery

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .llm_client_v2 import EnhancedLLMClient, LLMRequest, LLMResponse, LLMError
from .base_agent import BaseAgent, AgentType, AgentResult, QueryContext

logger = structlog.get_logger(__name__)


class AgentStrategy(ABC):
    """Abstract strategy for agent behavior."""

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: QueryContext) -> AgentResult:
        """Execute the agent strategy."""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the strategy name."""
        pass


class PromptTemplate:
    """Prompt template management."""

    def __init__(self, template: str, variables: List[str] = None):
        self.template = template
        self.variables = variables or []

    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required variable in prompt template: {e}")
            raise ValueError(f"Missing required variable: {e}")

    def validate_variables(self, **kwargs) -> bool:
        """Validate that all required variables are provided."""
        for var in self.variables:
            if var not in kwargs:
                return False
        return True


class PromptManager:
    """Manages prompt templates for agents."""

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default prompt templates."""

        # Synthesis agent templates
        self.templates["synthesis_answer"] = PromptTemplate(
            template="""You are an expert knowledge synthesis agent. Your task is to create a comprehensive, accurate, and well-structured answer based on the provided verified facts.

Query: {query}

Verified Facts:
{facts}

Instructions:
1. Synthesize the facts into a coherent, comprehensive answer
2. Maintain accuracy and avoid speculation
3. Structure the answer logically
4. Include relevant details from the facts
5. If facts are contradictory, acknowledge the conflict
6. If insufficient facts are available, state this clearly

Answer:""",
            variables=["query", "facts"],
        )

        # Fact-checking agent templates
        self.templates["factcheck_verification"] = PromptTemplate(
            template="""You are an expert fact-checking agent. Your task is to verify claims against provided evidence.

Claim: {claim}

Evidence:
{evidence}

Instructions:
1. Analyze the claim against the provided evidence
2. Determine if the claim is supported, contradicted, or unclear
3. Provide confidence score (0.0 to 1.0)
4. Explain your reasoning
5. Identify specific supporting or contradicting evidence

Analysis:
- Claim: {claim}
- Evidence Quality: [assess evidence quality]
- Verification Result: [supported/contradicted/unclear]
- Confidence Score: [0.0-1.0]
- Reasoning: [detailed explanation]
- Supporting Evidence: [list specific evidence]
- Contradicting Evidence: [list if any]""",
            variables=["claim", "evidence"],
        )

        # Retrieval agent templates
        self.templates["retrieval_query_expansion"] = PromptTemplate(
            template="""You are an expert information retrieval agent. Your task is to expand and refine the query to improve search results.

Original Query: {query}

Instructions:
1. Identify key concepts and entities
2. Generate related terms and synonyms
3. Consider different aspects of the query
4. Maintain the original intent
5. Generate 3-5 expanded queries

Expanded Queries:
1. [expanded query 1]
2. [expanded query 2]
3. [expanded query 3]
4. [expanded query 4]
5. [expanded query 5]""",
            variables=["query"],
        )

        self.templates["retrieval_reranking"] = PromptTemplate(
            template="""You are an expert information retrieval agent. Your task is to rerank search results based on relevance to the query.

Query: {query}

Search Results:
{results}

Instructions:
1. Evaluate each result's relevance to the query
2. Consider accuracy, completeness, and recency
3. Rank results from most to least relevant
4. Provide brief justification for ranking
5. Return only the top {top_k} results

Reranked Results:
[ranked list with justifications]""",
            variables=["query", "results", "top_k"],
        )

    def get_template(self, template_name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        return self.templates[template_name]

    def add_template(self, name: str, template: PromptTemplate):
        """Add a new prompt template."""
        self.templates[name] = template

    def list_templates(self) -> List[str]:
        """List all available templates."""
        return list(self.templates.keys())


class AgentMetrics:
    """Agent performance metrics."""

    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.total_tokens_used = 0
        self.llm_calls = 0
        self.fallback_count = 0

    def record_request(self, execution_time: float, success: bool, tokens: int = 0):
        """Record a request metric."""
        self.request_count += 1
        self.total_execution_time += execution_time

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        if tokens > 0:
            self.total_tokens_used += tokens

    def record_llm_call(self, fallback: bool = False):
        """Record an LLM call."""
        self.llm_calls += 1
        if fallback:
            self.fallback_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_time = self.total_execution_time / max(self.request_count, 1)
        success_rate = self.success_count / max(self.request_count, 1)

        return {
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "average_execution_time_ms": avg_time * 1000,
            "total_tokens_used": self.total_tokens_used,
            "llm_calls": self.llm_calls,
            "fallback_count": self.fallback_count,
        }


class BaseAgentStrategy(AgentStrategy):
    """Base strategy with common functionality."""

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.llm_client = EnhancedLLMClient()
        self.prompt_manager = PromptManager()
        self.metrics = AgentMetrics()
        self.logger = structlog.get_logger(f"agent.{agent_id}")

    async def execute(self, task: Dict[str, Any], context: QueryContext) -> AgentResult:
        """Execute the agent strategy with error handling and metrics."""
        start_time = time.time()

        try:
            self.logger.info(f"Executing {self.get_strategy_name()} strategy")

            # Execute the specific strategy
            result = await self._execute_strategy(task, context)

            # Record metrics
            execution_time = time.time() - start_time
            self.metrics.record_request(
                execution_time=execution_time,
                success=result.success,
                tokens=result.token_usage.get("total", 0) if result.token_usage else 0,
            )

            self.logger.info(f"Strategy execution completed: {execution_time:.3f}s")
            return result

        except Exception as e:
            # Record error metrics
            execution_time = time.time() - start_time
            self.metrics.record_request(execution_time, False)

            self.logger.error(f"Strategy execution failed: {str(e)}")

            return AgentResult(
                success=False,
                error=str(e),
                confidence=0.0,
                execution_time_ms=int(execution_time * 1000),
            )

    @abstractmethod
    async def _execute_strategy(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """Execute the specific strategy implementation."""
        pass

    async def _call_llm(
        self, prompt: str, system_message: str = None, **kwargs
    ) -> LLMResponse:
        """Call LLM with error handling and fallback."""
        try:
            request = LLMRequest(prompt=prompt, system_message=system_message, **kwargs)

            response = await self.llm_client.generate_text(request)
            self.metrics.record_llm_call()

            return response

        except LLMError as e:
            self.logger.warning(f"LLM call failed: {e.message}")
            self.metrics.record_llm_call(fallback=True)
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "strategy": self.get_strategy_name(),
            **self.metrics.get_metrics(),
        }


class SynthesisStrategy(BaseAgentStrategy):
    """Synthesis agent strategy."""

    def __init__(self):
        super().__init__("synthesis_agent", AgentType.SYNTHESIS)

    def get_strategy_name(self) -> str:
        return "synthesis"

    async def _execute_strategy(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """Execute synthesis strategy."""

        # Extract task data
        verified_facts = task.get("verified_facts", [])
        query = task.get("query", "")

        if not verified_facts:
            return AgentResult(
                success=False,
                error="No verified facts provided for synthesis",
                confidence=0.0,
            )

        # Format facts for prompt
        facts_text = self._format_facts(verified_facts)

        # Get synthesis prompt
        template = self.prompt_manager.get_template("synthesis_answer")
        prompt = template.format(query=query, facts=facts_text)

        # Call LLM for synthesis
        try:
            response = await self._call_llm(
                prompt=prompt,
                system_message="You are an expert knowledge synthesis agent.",
                max_tokens=1000,
                temperature=0.3,
            )

            # Calculate confidence based on fact quality
            confidence = self._calculate_synthesis_confidence(verified_facts)

            return AgentResult(
                success=True,
                data={
                    "answer": response.content,
                    "synthesis_method": "llm_based",
                    "fact_count": len(verified_facts),
                    "confidence": confidence,
                },
                confidence=confidence,
                token_usage=response.token_usage,
                execution_time_ms=int(response.response_time_ms),
            )

        except Exception as e:
            # Fallback to rule-based synthesis
            self.logger.warning(f"LLM synthesis failed, using fallback: {str(e)}")
            return self._fallback_synthesis(verified_facts, query)

    def _format_facts(self, facts: List[Dict]) -> str:
        """Format facts for prompt."""
        formatted_facts = []
        for i, fact in enumerate(facts, 1):
            claim = fact.get("claim", "")
            confidence = fact.get("confidence", 0.0)
            source = fact.get("source", "unknown")

            formatted_facts.append(
                f"{i}. Claim: {claim}\n"
                f"   Confidence: {confidence:.2f}\n"
                f"   Source: {source}\n"
            )

        return "\n".join(formatted_facts)

    def _calculate_synthesis_confidence(self, facts: List[Dict]) -> float:
        """Calculate synthesis confidence based on fact quality."""
        if not facts:
            return 0.0

        # Average confidence of facts
        avg_confidence = sum(f.get("confidence", 0.0) for f in facts) / len(facts)

        # Penalize for low fact count
        fact_count_penalty = min(len(facts) / 5.0, 1.0)

        return avg_confidence * fact_count_penalty

    def _fallback_synthesis(self, facts: List[Dict], query: str) -> AgentResult:
        """Fallback synthesis using rule-based approach."""
        if not facts:
            return AgentResult(
                success=False, error="No facts available for synthesis", confidence=0.0
            )

        # Simple concatenation of high-confidence facts
        high_confidence_facts = [f for f in facts if f.get("confidence", 0.0) > 0.7]

        if high_confidence_facts:
            answer = "Based on verified facts:\n\n"
            for fact in high_confidence_facts:
                answer += f"• {fact.get('claim', '')}\n"
        else:
            answer = "Insufficient high-confidence facts available for synthesis."

        confidence = self._calculate_synthesis_confidence(facts)

        return AgentResult(
            success=True,
            data={
                "answer": answer,
                "synthesis_method": "rule_based",
                "fact_count": len(facts),
                "confidence": confidence,
            },
            confidence=confidence,
        )


class FactCheckStrategy(BaseAgentStrategy):
    """Fact-checking agent strategy."""

    def __init__(self):
        super().__init__("factcheck_agent", AgentType.FACT_CHECK)

    def get_strategy_name(self) -> str:
        return "fact_check"

    async def _execute_strategy(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """Execute fact-checking strategy."""

        # Extract task data
        documents = task.get("documents", [])
        query = task.get("query", "")

        if not documents:
            return AgentResult(
                success=False,
                error="No documents provided for fact-checking",
                confidence=0.0,
            )

        # Extract claims from query and documents
        claims = await self._extract_claims(query, documents)

        if not claims:
            return AgentResult(
                success=False, error="No claims found to verify", confidence=0.0
            )

        # Verify claims against documents
        verifications = []
        for claim in claims:
            verification = await self._verify_claim(claim, documents)
            verifications.append(verification)

        # Filter verified facts
        verified_facts = self._filter_verified_facts(verifications)

        # Calculate overall confidence
        confidence = self._calculate_verification_confidence(verifications)

        return AgentResult(
            success=True,
            data={
                "verified_facts": verified_facts,
                "total_claims": len(claims),
                "verified_count": len(verified_facts),
                "confidence": confidence,
            },
            confidence=confidence,
        )

    async def _extract_claims(self, query: str, documents: List[Dict]) -> List[str]:
        """Extract claims from query and documents."""
        claims = []

        # Extract claims from query
        query_claims = self._extract_claims_from_text(query)
        claims.extend(query_claims)

        # Extract claims from documents
        for doc in documents:
            content = doc.get("content", "")
            doc_claims = self._extract_claims_from_text(content)
            claims.extend(doc_claims)

        # Deduplicate claims
        return list(set(claims))

    def _extract_claims_from_text(self, text: str) -> List[str]:
        """Extract factual claims from text."""
        claims = []

        # Simple rule-based extraction
        sentences = text.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if self._is_factual_statement(sentence):
                claims.append(sentence)

        return claims

    def _is_factual_statement(self, sentence: str) -> bool:
        """Check if a sentence is a factual statement."""
        # Simple heuristics for factual statements
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
            "consists",
            "comprises",
            "located",
            "found",
            "discovered",
            "established",
        ]

        sentence_lower = sentence.lower()

        # Check for factual indicators
        has_factual_indicator = any(
            indicator in sentence_lower for indicator in factual_indicators
        )

        # Check for specific claims (numbers, dates, names)
        has_specific_info = any(char.isdigit() for char in sentence)

        # Avoid questions and opinions
        is_question = sentence.strip().endswith("?")
        opinion_indicators = [
            "think",
            "believe",
            "feel",
            "opinion",
            "might",
            "could",
            "should",
        ]
        is_opinion = any(
            indicator in sentence_lower for indicator in opinion_indicators
        )

        return (
            has_factual_indicator
            and has_specific_info
            and not is_question
            and not is_opinion
        )

    async def _verify_claim(self, claim: str, documents: List[Dict]) -> Dict[str, Any]:
        """Verify a single claim against documents."""

        # Prepare evidence from documents
        evidence = []
        for doc in documents:
            content = doc.get("content", "")
            if self._is_relevant_to_claim(claim, content):
                evidence.append(content)

        if not evidence:
            return {
                "claim": claim,
                "is_supported": False,
                "confidence": 0.0,
                "evidence": [],
                "reasoning": "No relevant evidence found",
            }

        # Use LLM to verify claim
        try:
            template = self.prompt_manager.get_template("factcheck_verification")
            prompt = template.format(claim=claim, evidence="\n\n".join(evidence))

            response = await self._call_llm(
                prompt=prompt,
                system_message="You are an expert fact-checking agent.",
                max_tokens=500,
                temperature=0.1,
            )

            # Parse LLM response
            verification = self._parse_verification_response(response.content)
            verification["claim"] = claim
            verification["evidence"] = evidence

            return verification

        except Exception as e:
            self.logger.warning(
                f"LLM verification failed for claim '{claim}': {str(e)}"
            )

            # Fallback verification
            return self._fallback_verification(claim, evidence)

    def _is_relevant_to_claim(self, claim: str, content: str) -> bool:
        """Check if content is relevant to the claim."""
        # Simple keyword matching
        claim_words = set(claim.lower().split())
        content_words = set(content.lower().split())

        # Check for overlapping keywords
        overlap = claim_words.intersection(content_words)
        return len(overlap) >= 2  # At least 2 words in common

    def _parse_verification_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM verification response."""
        # Simple parsing - in production, use more robust parsing
        lines = response.split("\n")

        verification_result = "unclear"
        confidence = 0.5

        for line in lines:
            line_lower = line.lower()
            if "supported" in line_lower:
                verification_result = "supported"
                confidence = 0.8
            elif "contradicted" in line_lower:
                verification_result = "contradicted"
                confidence = 0.7
            elif "confidence" in line_lower:
                try:
                    # Extract confidence score
                    import re

                    match = re.search(r"(\d+\.?\d*)", line)
                    if match:
                        confidence = float(match.group(1))
                except:
                    pass

        return {
            "is_supported": verification_result == "supported",
            "confidence": confidence,
            "reasoning": response,
        }

    def _fallback_verification(self, claim: str, evidence: List[str]) -> Dict[str, Any]:
        """Fallback verification using simple heuristics."""
        if not evidence:
            return {
                "claim": claim,
                "is_supported": False,
                "confidence": 0.0,
                "evidence": [],
                "reasoning": "No evidence available",
            }

        # Simple keyword matching
        claim_words = set(claim.lower().split())
        supporting_evidence = []

        for content in evidence:
            content_words = set(content.lower().split())
            overlap = claim_words.intersection(content_words)

            if len(overlap) >= 3:  # Significant overlap
                supporting_evidence.append(content)

        confidence = min(len(supporting_evidence) / len(evidence), 1.0)

        return {
            "claim": claim,
            "is_supported": len(supporting_evidence) > 0,
            "confidence": confidence,
            "evidence": supporting_evidence,
            "reasoning": f"Found {len(supporting_evidence)} supporting documents",
        }

    def _filter_verified_facts(self, verifications: List[Dict]) -> List[Dict]:
        """Filter verified facts based on confidence threshold."""
        threshold = 0.7
        verified_facts = []

        for verification in verifications:
            if verification.get("confidence", 0.0) >= threshold:
                verified_facts.append(
                    {
                        "claim": verification["claim"],
                        "confidence": verification["confidence"],
                        "source": "fact_check_agent",
                        "evidence": verification.get("evidence", []),
                    }
                )

        return verified_facts

    def _calculate_verification_confidence(self, verifications: List[Dict]) -> float:
        """Calculate overall verification confidence."""
        if not verifications:
            return 0.0

        total_confidence = sum(v.get("confidence", 0.0) for v in verifications)
        return total_confidence / len(verifications)


class RetrievalStrategy(BaseAgentStrategy):
    """Retrieval agent strategy."""

    def __init__(self):
        super().__init__("retrieval_agent", AgentType.RETRIEVAL)

    def get_strategy_name(self) -> str:
        return "retrieval"

    async def _execute_strategy(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """Execute retrieval strategy."""

        query = task.get("query", "")
        if not query:
            return AgentResult(
                success=False, error="No query provided for retrieval", confidence=0.0
            )

        # Expand query for better retrieval
        expanded_queries = await self._expand_query(query)

        # Perform retrieval for each expanded query
        all_results = []
        for expanded_query in expanded_queries:
            results = await self._retrieve_documents(expanded_query)
            all_results.extend(results)

        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = await self._rank_results(query, unique_results)

        # Calculate confidence based on result quality
        confidence = self._calculate_retrieval_confidence(ranked_results)

        return AgentResult(
            success=True,
            data={
                "documents": ranked_results,
                "query": query,
                "expanded_queries": expanded_queries,
                "total_results": len(ranked_results),
            },
            confidence=confidence,
        )

    async def _expand_query(self, query: str) -> List[str]:
        """Expand query for better retrieval."""
        try:
            template = self.prompt_manager.get_template("retrieval_query_expansion")
            prompt = template.format(query=query)

            response = await self._call_llm(
                prompt=prompt,
                system_message="You are an expert information retrieval agent.",
                max_tokens=300,
                temperature=0.3,
            )

            # Parse expanded queries
            expanded_queries = self._parse_expanded_queries(response.content)
            return [query] + expanded_queries  # Include original query

        except Exception as e:
            self.logger.warning(f"Query expansion failed: {str(e)}")
            return [query]  # Fallback to original query

    def _parse_expanded_queries(self, response: str) -> List[str]:
        """Parse expanded queries from LLM response."""
        queries = []
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract query from numbered list
                if ". " in line:
                    query = line.split(". ", 1)[1]
                    queries.append(query)
                elif line.startswith("- "):
                    query = line[2:]
                    queries.append(query)

        return queries[:5]  # Limit to 5 expanded queries

    async def _retrieve_documents(self, query: str) -> List[Dict]:
        """Retrieve documents for a query."""
        # Mock document retrieval - in production, integrate with actual search
        mock_documents = [
            {
                "content": f"Document about {query}",
                "source": "mock_source_1",
                "score": 0.9,
                "metadata": {"type": "document"},
            },
            {
                "content": f"Another document about {query}",
                "source": "mock_source_2",
                "score": 0.8,
                "metadata": {"type": "document"},
            },
        ]

        return mock_documents

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Deduplicate search results."""
        seen_content = set()
        unique_results = []

        for result in results:
            content_hash = hash(result.get("content", ""))
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)

        return unique_results

    async def _rank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rank results by relevance to query."""
        if not results:
            return []

        try:
            template = self.prompt_manager.get_template("retrieval_reranking")
            results_text = self._format_results_for_ranking(results)
            prompt = template.format(
                query=query, results=results_text, top_k=len(results)
            )

            response = await self._call_llm(
                prompt=prompt,
                system_message="You are an expert information retrieval agent.",
                max_tokens=500,
                temperature=0.1,
            )

            # Parse ranked results
            ranked_results = self._parse_ranked_results(response.content, results)
            return ranked_results

        except Exception as e:
            self.logger.warning(f"Result ranking failed: {str(e)}")
            # Fallback to score-based ranking
            return sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)

    def _format_results_for_ranking(self, results: List[Dict]) -> str:
        """Format results for ranking prompt."""
        formatted = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")[:200]  # Truncate for prompt
            score = result.get("score", 0.0)
            source = result.get("source", "unknown")

            formatted.append(
                f"{i}. Content: {content}\n"
                f"   Score: {score:.2f}\n"
                f"   Source: {source}\n"
            )

        return "\n".join(formatted)

    def _parse_ranked_results(
        self, response: str, original_results: List[Dict]
    ) -> List[Dict]:
        """Parse ranked results from LLM response."""
        # Simple parsing - in production, use more robust parsing
        ranked_indices = []
        lines = response.split("\n")

        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                try:
                    index = int(line.split(".")[0]) - 1
                    if 0 <= index < len(original_results):
                        ranked_indices.append(index)
                except:
                    pass

        # Return results in ranked order
        ranked_results = []
        for index in ranked_indices:
            if index < len(original_results):
                ranked_results.append(original_results[index])

        # Add any remaining results
        for i, result in enumerate(original_results):
            if i not in ranked_indices:
                ranked_results.append(result)

        return ranked_results

    def _calculate_retrieval_confidence(self, results: List[Dict]) -> float:
        """Calculate retrieval confidence based on result quality."""
        if not results:
            return 0.0

        # Average score of top results
        scores = [r.get("score", 0.0) for r in results[:5]]
        avg_score = sum(scores) / len(scores)

        # Penalize for low result count
        count_penalty = min(len(results) / 10.0, 1.0)

        return avg_score * count_penalty


class AgentFactory:
    """Factory for creating agents with different strategies."""

    _strategies = {
        AgentType.SYNTHESIS: SynthesisStrategy,
        AgentType.FACT_CHECK: FactCheckStrategy,
        AgentType.RETRIEVAL: RetrievalStrategy,
    }

    @classmethod
    def create_agent(cls, agent_type: AgentType, agent_id: str = None) -> BaseAgent:
        """Create an agent with the specified type."""
        if agent_type not in cls._strategies:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        strategy_class = cls._strategies[agent_type]
        strategy = strategy_class()

        # Create agent with strategy
        agent = StrategyBasedAgent(
            agent_id or f"{agent_type.value}_agent", agent_type, strategy
        )

        return agent

    @classmethod
    def register_strategy(
        cls, agent_type: AgentType, strategy_class: Type[AgentStrategy]
    ):
        """Register a new strategy for an agent type."""
        cls._strategies[agent_type] = strategy_class

    @classmethod
    def list_supported_types(cls) -> List[AgentType]:
        """List supported agent types."""
        return list(cls._strategies.keys())


class StrategyBasedAgent(BaseAgent):
    """Agent implementation using strategy pattern."""

    def __init__(self, agent_id: str, agent_type: AgentType, strategy: AgentStrategy):
        super().__init__(agent_id, agent_type)
        self.strategy = strategy

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """Process task using the configured strategy."""
        return await self.strategy.execute(task, context)

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics including strategy metrics."""
        base_metrics = super().get_metrics()
        strategy_metrics = self.strategy.get_metrics()

        return {**base_metrics, "strategy_metrics": strategy_metrics}
