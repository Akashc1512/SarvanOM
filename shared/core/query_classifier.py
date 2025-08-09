"""
QueryClassifier - Universal Knowledge Platform
Analyzes user queries and categorizes them for intelligent routing.

This module provides query classification functionality to guide the orchestrator
in choosing the right agent or data source based on query characteristics.
"""

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryCategory(str, Enum):
    """Query categories for routing decisions."""

    GENERAL_FACTUAL = "general_factual"
    CODE = "code"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    CREATIVE = "creative"
    OPINION = "opinion"
    UNKNOWN = "unknown"


class QueryComplexity(str, Enum):
    """Query complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class QueryClassification:
    """Result of query classification analysis."""

    category: QueryCategory
    confidence: float
    complexity: QueryComplexity
    detected_patterns: List[str] = field(default_factory=list)
    suggested_agents: List[str] = field(default_factory=list)
    routing_hints: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "complexity": self.complexity.value,
            "detected_patterns": self.detected_patterns,
            "suggested_agents": self.suggested_agents,
            "routing_hints": self.routing_hints,
            "timestamp": self.timestamp.isoformat(),
        }


class QueryClassifier:
    """
    Analyzes user queries and categorizes them for intelligent routing.

    Uses heuristics and regex patterns to classify queries into categories
    that guide the orchestrator in choosing appropriate agents and data sources.
    """

    def __init__(self):
        """Initialize the query classifier with pattern definitions."""
        self._initialize_patterns()
        logger.info("QueryClassifier initialized successfully")

    def _initialize_patterns(self):
        """Initialize classification patterns and keywords."""

        # Knowledge Graph patterns - relationship and entity-focused queries
        self.knowledge_graph_patterns = [
            r"\b(related to|relationship between|connection between|linked to|associated with)\b",
            r"\b(how are|how is|what connects|what links|what relates)\b",
            r"\b(entity|entities|concept|concepts|ontology|taxonomy)\b",
            r"\b(graph|network|structure|hierarchy|classification)\b",
            r"\b(influence|impact|effect|cause|correlation)\b",
            r"\b(similar|different|compare|contrast|versus|vs)\b",
            r"\b(belongs to|part of|member of|category|type)\b",
            r"\b(dependency|dependency on|depends on|requires|needs)\b",
        ]

        # Code/Programming patterns
        self.code_patterns = [
            r"\b(code|programming|program|script|algorithm|function|method|class)\b",
            r"\b(syntax|error|bug|debug|compile|run|execute|test)\b",
            r"\b(api|endpoint|database|query|sql|nosql|orm)\b",
            r"\b(framework|library|package|module|import|export)\b",
            r"\b(loop|condition|variable|parameter|return|void|public|private)\b",
            r"\b(git|version control|commit|branch|merge|pull request)\b",
            r"\b(design pattern|architecture|microservice|monolith)\b",
            r"\b(performance|optimization|scalability|security|authentication)\b",
            r"\b(html|css|javascript|python|java|c\+\+|c#|php|ruby|go|rust)\b",
            r"\b(react|angular|vue|node|express|django|flask|spring)\b",
            r"\b(docker|kubernetes|aws|azure|gcp|cloud|deployment)\b",
            r"\b(unit test|integration test|tdd|bdd|ci|cd|devops)\b",
            r"\b(how to|tutorial|guide|example|sample|snippet)\b.*\b(code|program|script)\b",
            r"\b(implement|create|build|develop|write)\b.*\b(code|program|function)\b",
        ]

        # Analytical patterns
        self.analytical_patterns = [
            r"\b(analyze|analysis|examine|investigate|study|research)\b",
            r"\b(evaluate|assess|review|critique|examine)\b",
            r"\b(why|how does|what causes|what leads to|what results in)\b",
            r"\b(trend|pattern|trends|patterns|statistics|data)\b",
            r"\b(performance|efficiency|effectiveness|quality|metrics)\b",
            r"\b(problem|issue|challenge|difficulty|obstacle)\b",
            r"\b(solution|approach|strategy|method|technique)\b",
        ]

        # Comparative patterns
        self.comparative_patterns = [
            r"\b(compare|comparison|versus|vs|against|contrast)\b",
            r"\b(better|worse|best|worst|superior|inferior)\b",
            r"\b(difference|similarity|same|different|alike|unlike)\b",
            r"\b(pros|cons|advantages|disadvantages|benefits|drawbacks)\b",
            r"\b(which|choose|select|pick|recommend|suggest)\b",
            r"\b(prefer|favorite|optimal|ideal|suitable)\b",
        ]

        # Procedural patterns
        self.procedural_patterns = [
            r"\b(how to|steps|procedure|process|method|approach)\b",
            r"\b(guide|tutorial|instructions|manual|walkthrough)\b",
            r"\b(setup|install|configure|deploy|build|run)\b",
            r"\b(first|second|third|next|then|finally|lastly)\b",
            r"\b(step by step|step-by-step|one by one|sequentially)\b",
            r"\b(prerequisites|requirements|needs|dependencies)\b",
        ]

        # Creative patterns
        self.creative_patterns = [
            r"\b(create|design|invent|innovate|brainstorm|imagine)\b",
            r"\b(generate|produce|develop|build|make|construct)\b",
            r"\b(creative|artistic|original|unique|novel|innovative)\b",
            r"\b(idea|concept|vision|plan|strategy|approach)\b",
            r"\b(what if|suppose|imagine|consider|think about)\b",
            r"\b(possibility|potential|opportunity|chance|option)\b",
        ]

        # Opinion patterns
        self.opinion_patterns = [
            r"\b(opinion|think|believe|feel|view|perspective)\b",
            r"\b(agree|disagree|support|oppose|favor|against)\b",
            r"\b(recommend|suggest|advise|recommendation|suggestion)\b",
            r"\b(experience|personal|subjective|objective|bias)\b",
            r"\b(like|dislike|love|hate|enjoy|prefer)\b",
            r"\b(should|ought to|must|need to|have to)\b",
        ]

        # Complexity indicators
        self.complexity_indicators = {
            "simple": [
                r"\b(what|when|where|who|which)\b",
                r"\b(define|explain|describe|tell|show)\b",
                r"\b(yes|no|true|false|correct|incorrect)\b",
            ],
            "moderate": [
                r"\b(how|why|compare|analyze|evaluate)\b",
                r"\b(relationship|connection|influence|impact)\b",
                r"\b(example|instance|case|scenario)\b",
            ],
            "complex": [
                r"\b(complex|complicated|advanced|sophisticated)\b",
                r"\b(multiple|several|various|different|diverse)\b",
                r"\b(integrate|combine|merge|unify|synthesize)\b",
                r"\b(optimize|maximize|minimize|improve|enhance)\b",
                r"\b(architecture|system|framework|platform|ecosystem)\b",
            ],
        }

    async def classify_query(self, query: str) -> QueryClassification:
        """
        Classify a query and return detailed classification information.

        Args:
            query: The user's query string

        Returns:
            QueryClassification object with category, confidence, and routing hints
        """
        start_time = datetime.now()
        query_lower = query.lower().strip()

        # Initialize classification result
        category = QueryCategory.UNKNOWN
        confidence = 0.0
        detected_patterns = []
        suggested_agents = []
        routing_hints = {}

        # Check each category with pattern matching
        category_scores = {}

        # Knowledge Graph classification
        kg_score = self._calculate_pattern_score(
            query_lower, self.knowledge_graph_patterns
        )
        if kg_score > 0:
            category_scores[QueryCategory.KNOWLEDGE_GRAPH] = kg_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.knowledge_graph_patterns)
            )

        # Code classification
        code_score = self._calculate_pattern_score(query_lower, self.code_patterns)
        if code_score > 0:
            category_scores[QueryCategory.CODE] = code_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.code_patterns)
            )

        # Analytical classification
        analytical_score = self._calculate_pattern_score(
            query_lower, self.analytical_patterns
        )
        if analytical_score > 0:
            category_scores[QueryCategory.ANALYTICAL] = analytical_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.analytical_patterns)
            )

        # Comparative classification
        comparative_score = self._calculate_pattern_score(
            query_lower, self.comparative_patterns
        )
        if comparative_score > 0:
            category_scores[QueryCategory.COMPARATIVE] = comparative_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.comparative_patterns)
            )

        # Procedural classification
        procedural_score = self._calculate_pattern_score(
            query_lower, self.procedural_patterns
        )
        if procedural_score > 0:
            category_scores[QueryCategory.PROCEDURAL] = procedural_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.procedural_patterns)
            )

        # Creative classification
        creative_score = self._calculate_pattern_score(
            query_lower, self.creative_patterns
        )
        if creative_score > 0:
            category_scores[QueryCategory.CREATIVE] = creative_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.creative_patterns)
            )

        # Opinion classification
        opinion_score = self._calculate_pattern_score(
            query_lower, self.opinion_patterns
        )
        if opinion_score > 0:
            category_scores[QueryCategory.OPINION] = opinion_score
            detected_patterns.extend(
                self._get_matched_patterns(query_lower, self.opinion_patterns)
            )

        # Determine the best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            category = best_category
        else:
            # Default to general factual if no specific patterns detected
            category = QueryCategory.GENERAL_FACTUAL
            confidence = 0.3

        # Determine complexity
        complexity = self._determine_complexity(query_lower)

        # Generate routing hints and suggested agents
        routing_hints = self._generate_routing_hints(
            category, complexity, detected_patterns
        )
        suggested_agents = self._suggest_agents(category, complexity)

        # Create classification result
        classification = QueryClassification(
            category=category,
            confidence=confidence,
            complexity=complexity,
            detected_patterns=detected_patterns,
            suggested_agents=suggested_agents,
            routing_hints=routing_hints,
        )

        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"Query classified as {category.value} (confidence: {confidence:.2f}) in {processing_time:.2f}ms"
        )

        return classification

    def _calculate_pattern_score(self, query: str, patterns: List[str]) -> float:
        """Calculate pattern matching score for a set of patterns."""
        total_matches = 0
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            total_matches += len(matches)

        # Normalize score based on pattern count and query length
        if total_matches == 0:
            return 0.0

        # Higher score for more matches relative to query length
        normalized_score = min(total_matches / (len(query.split()) * 0.5), 1.0)
        return normalized_score

    def _get_matched_patterns(self, query: str, patterns: List[str]) -> List[str]:
        """Get list of patterns that matched the query."""
        matched_patterns = []
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                # Extract a readable description from the pattern
                pattern_desc = (
                    pattern.replace(r"\b", "").replace("|", " or ").replace("\\", "")
                )
                matched_patterns.append(pattern_desc)

        return matched_patterns

    def _determine_complexity(self, query: str) -> QueryComplexity:
        """Determine query complexity based on patterns and characteristics."""
        complexity_scores = {
            QueryComplexity.SIMPLE: 0,
            QueryComplexity.MODERATE: 0,
            QueryComplexity.COMPLEX: 0,
        }

        # Check complexity indicators
        for complexity, patterns in self.complexity_indicators.items():
            score = self._calculate_pattern_score(query, patterns)
            complexity_scores[QueryComplexity(complexity)] = score

        # Additional complexity factors
        word_count = len(query.split())
        if word_count > 20:
            complexity_scores[QueryComplexity.COMPLEX] += 0.3
        elif word_count > 10:
            complexity_scores[QueryComplexity.MODERATE] += 0.2
        else:
            complexity_scores[QueryComplexity.SIMPLE] += 0.2

        # Return the highest scoring complexity
        return max(complexity_scores, key=complexity_scores.get)

    def _generate_routing_hints(
        self, category: QueryCategory, complexity: QueryComplexity, patterns: List[str]
    ) -> Dict[str, Any]:
        """Generate routing hints based on classification."""
        hints = {
            "primary_category": category.value,
            "complexity_level": complexity.value,
            "detected_patterns": patterns,
            "execution_strategy": self._suggest_execution_strategy(
                category, complexity
            ),
            "priority_level": self._determine_priority(category, complexity),
            "estimated_tokens": self._estimate_token_usage(complexity),
            "cache_strategy": self._suggest_cache_strategy(category),
        }

        # Category-specific hints
        if category == QueryCategory.KNOWLEDGE_GRAPH:
            hints["graph_queries"] = True
            hints["entity_extraction"] = True
            hints["relationship_focus"] = True
        elif category == QueryCategory.CODE:
            hints["code_analysis"] = True
            hints["syntax_highlighting"] = True
            hints["code_examples"] = True
        elif category == QueryCategory.ANALYTICAL:
            hints["deep_analysis"] = True
            hints["multiple_sources"] = True
            hints["fact_checking"] = True

        return hints

    def _suggest_agents(
        self, category: QueryCategory, complexity: QueryComplexity
    ) -> List[str]:
        """Suggest appropriate agents based on classification."""
        agents = []

        # Base agents for all queries
        agents.extend(["retrieval", "synthesis"])

        # Category-specific agents
        if category == QueryCategory.KNOWLEDGE_GRAPH:
            agents.extend(
                ["retrieval", "synthesis"]
            )  # Knowledge graph queries need good retrieval
        elif category == QueryCategory.CODE:
            agents.extend(
                ["retrieval", "synthesis"]
            )  # Code queries need examples and explanations
        elif category == QueryCategory.ANALYTICAL:
            agents.extend(
                ["fact_check", "citation"]
            )  # Analytical queries need verification
        elif category == QueryCategory.COMPARATIVE:
            agents.extend(
                ["retrieval", "synthesis"]
            )  # Comparative queries need multiple sources
        elif category == QueryCategory.PROCEDURAL:
            agents.extend(
                ["retrieval", "synthesis"]
            )  # Procedural queries need step-by-step guidance
        elif category == QueryCategory.CREATIVE:
            agents.extend(["synthesis"])  # Creative queries need synthesis
        elif category == QueryCategory.OPINION:
            agents.extend(
                ["fact_check", "citation"]
            )  # Opinion queries need fact checking

        # Complexity-based adjustments
        if complexity == QueryComplexity.COMPLEX:
            agents.extend(
                ["fact_check", "citation"]
            )  # Complex queries need verification

        return list(set(agents))  # Remove duplicates

    def _suggest_execution_strategy(
        self, category: QueryCategory, complexity: QueryComplexity
    ) -> str:
        """Suggest execution strategy based on classification."""
        if complexity == QueryComplexity.COMPLEX:
            return "pipeline"  # Complex queries need full pipeline
        elif category in [QueryCategory.ANALYTICAL, QueryCategory.COMPARATIVE]:
            return "fork_join"  # Analytical/comparative queries benefit from parallel processing
        else:
            return "scatter_gather"  # Simple queries can use scatter-gather

    def _determine_priority(
        self, category: QueryCategory, complexity: QueryComplexity
    ) -> str:
        """Determine processing priority."""
        if complexity == QueryComplexity.COMPLEX:
            return "high"
        elif category in [QueryCategory.ANALYTICAL, QueryCategory.KNOWLEDGE_GRAPH]:
            return "medium"
        else:
            return "normal"

    def _estimate_token_usage(self, complexity: QueryComplexity) -> int:
        """Estimate token usage based on complexity."""
        base_tokens = {
            QueryComplexity.SIMPLE: 500,
            QueryComplexity.MODERATE: 1000,
            QueryComplexity.COMPLEX: 2000,
        }
        return base_tokens.get(complexity, 1000)

    def _suggest_cache_strategy(self, category: QueryCategory) -> str:
        """Suggest caching strategy based on category."""
        if category == QueryCategory.GENERAL_FACTUAL:
            return "aggressive"  # Factual queries can be cached longer
        elif category == QueryCategory.CODE:
            return "moderate"  # Code examples can be cached moderately
        else:
            return "conservative"  # Other categories use conservative caching

    async def batch_classify(self, queries: List[str]) -> List[QueryClassification]:
        """Classify multiple queries in batch."""
        results = []
        for query in queries:
            classification = await self.classify_query(query)
            results.append(classification)
        return results

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get statistics about classification patterns."""
        return {
            "total_patterns": {
                "knowledge_graph": len(self.knowledge_graph_patterns),
                "code": len(self.code_patterns),
                "analytical": len(self.analytical_patterns),
                "comparative": len(self.comparative_patterns),
                "procedural": len(self.procedural_patterns),
                "creative": len(self.creative_patterns),
                "opinion": len(self.opinion_patterns),
            },
            "complexity_indicators": {
                complexity: len(patterns)
                for complexity, patterns in self.complexity_indicators.items()
            },
        }
