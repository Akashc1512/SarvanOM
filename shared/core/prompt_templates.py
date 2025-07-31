"""
Comprehensive Prompt Template System - MAANG Standards
Modular, reusable prompt templates for all agent types.

Features:
- Modular template system
- Template validation
- Variable substitution
- Template versioning
- Performance optimization
- Multi-language support
- Template testing utilities

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class TemplateType(str, Enum):
    """Template types for different agent functions."""

    SYNTHESIS = "synthesis"
    FACT_CHECK = "fact_check"
    RETRIEVAL = "retrieval"
    CITATION = "citation"
    QUERY_PROCESSING = "query_processing"


class Language(str, Enum):
    """Supported languages."""

    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    ZH = "zh"
    JA = "ja"


@dataclass
class PromptTemplate:
    """Prompt template with metadata and validation."""

    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    template_type: TemplateType = TemplateType.SYNTHESIS
    language: Language = Language.EN
    version: str = "1.0.0"
    description: str = ""
    max_tokens: int = 1000
    temperature: float = 0.2

    def __post_init__(self):
        """Validate template after initialization."""
        self._validate_template()
        self._extract_variables()

    def _validate_template(self):
        """Validate template structure."""
        if not self.template:
            raise ValueError("Template cannot be empty")

        if len(self.template) > 10000:
            raise ValueError("Template too long (max 10000 characters)")

    def _extract_variables(self):
        """Extract variables from template."""
        if not self.variables:
            # Extract variables using regex
            pattern = r"\{([^}]+)\}"
            matches = re.findall(pattern, self.template)
            self.variables = list(set(matches))

    def format(self, **kwargs) -> str:
        """Format template with provided variables."""
        try:
            # Validate required variables
            missing_vars = set(self.variables) - set(kwargs.keys())
            if missing_vars:
                raise ValueError(f"Missing required variables: {missing_vars}")

            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in template {self.name}: {e}")
            raise ValueError(f"Missing variable: {e}")
        except Exception as e:
            logger.error(f"Template formatting error: {e}")
            raise

    def validate_variables(self, **kwargs) -> bool:
        """Validate that all required variables are provided."""
        return all(var in kwargs for var in self.variables)

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
            "template_type": self.template_type.value,
            "language": self.language.value,
            "version": self.version,
            "description": self.description,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


class PromptTemplateManager:
    """Manages prompt templates with versioning and validation."""

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default prompt templates."""

        # Synthesis Templates
        self._add_synthesis_templates()

        # Fact-Checking Templates
        self._add_factcheck_templates()

        # Retrieval Templates
        self._add_retrieval_templates()

        # Citation Templates
        self._add_citation_templates()

        # Query Processing Templates
        self._add_query_processing_templates()

    def _add_synthesis_templates(self):
        """Add synthesis agent templates."""

        # Main synthesis template
        self.templates["synthesis_answer"] = PromptTemplate(
            name="synthesis_answer",
            template="""You are an expert knowledge synthesis agent. Your task is to create a comprehensive, accurate, and well-structured answer based on the provided verified facts.

Query: {query}

Verified Facts:
{facts}

Instructions:
1. Synthesize the facts into a coherent, comprehensive answer
2. Maintain accuracy and avoid speculation
3. Structure the answer logically with clear sections
4. Include relevant details from the facts
5. If facts are contradictory, acknowledge the conflict
6. If insufficient facts are available, state this clearly
7. Use clear, professional language
8. Provide a balanced perspective when multiple viewpoints exist

Answer:""",
            variables=["query", "facts"],
            template_type=TemplateType.SYNTHESIS,
            description="Main synthesis template for creating comprehensive answers",
            max_tokens=1500,
            temperature=0.3,
        )

        # Summary synthesis template
        self.templates["synthesis_summary"] = PromptTemplate(
            name="synthesis_summary",
            template="""You are an expert summarization agent. Create a concise summary of the provided information.

Content:
{content}

Instructions:
1. Create a clear, concise summary
2. Maintain key facts and insights
3. Use bullet points for clarity
4. Keep summary under {max_length} words
5. Focus on the most important information

Summary:""",
            variables=["content", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Summary synthesis template",
            max_tokens=500,
            temperature=0.2,
        )

        # Comparative synthesis template
        self.templates["synthesis_comparison"] = PromptTemplate(
            name="synthesis_comparison",
            template="""You are an expert comparative analysis agent. Compare and contrast the provided information.

Topic A: {topic_a}
Information A: {info_a}

Topic B: {topic_b}
Information B: {info_b}

Instructions:
1. Identify key similarities and differences
2. Provide balanced analysis
3. Use clear comparison structure
4. Support claims with evidence
5. Highlight important distinctions

Comparative Analysis:""",
            variables=["topic_a", "info_a", "topic_b", "info_b"],
            template_type=TemplateType.SYNTHESIS,
            description="Comparative analysis template",
            max_tokens=1000,
            temperature=0.2,
        )

    def _add_factcheck_templates(self):
        """Add fact-checking agent templates."""

        # Main verification template
        self.templates["factcheck_verification"] = PromptTemplate(
            name="factcheck_verification",
            template="""You are an expert fact-checking agent. Your task is to verify claims against provided evidence.

Claim: {claim}

Evidence:
{evidence}

Instructions:
1. Analyze the claim against the provided evidence
2. Determine if the claim is supported, contradicted, or unclear
3. Provide confidence score (0.0 to 1.0)
4. Explain your reasoning clearly
5. Identify specific supporting or contradicting evidence
6. Consider evidence quality and reliability
7. Acknowledge limitations in evidence

Analysis:
- Claim: {claim}
- Evidence Quality: [assess evidence quality and reliability]
- Verification Result: [supported/contradicted/unclear]
- Confidence Score: [0.0-1.0]
- Reasoning: [detailed explanation of analysis]
- Supporting Evidence: [list specific evidence that supports the claim]
- Contradicting Evidence: [list evidence that contradicts the claim]
- Limitations: [acknowledge any limitations in the analysis]""",
            variables=["claim", "evidence"],
            template_type=TemplateType.FACT_CHECK,
            description="Main fact-checking verification template",
            max_tokens=800,
            temperature=0.1,
        )

        # Claim decomposition template
        self.templates["factcheck_decomposition"] = PromptTemplate(
            name="factcheck_decomposition",
            template="""You are an expert claim analysis agent. Break down complex claims into verifiable components.

Complex Claim: {claim}

Instructions:
1. Identify the main components of the claim
2. Break down into specific, verifiable statements
3. Identify implicit assumptions
4. Highlight factual vs. opinion components
5. List specific claims that can be verified

Decomposed Claims:
1. [specific claim 1]
2. [specific claim 2]
3. [specific claim 3]
...

Implicit Assumptions:
- [assumption 1]
- [assumption 2]
...

Verifiable Statements:
- [statement 1]
- [statement 2]
...""",
            variables=["claim"],
            template_type=TemplateType.FACT_CHECK,
            description="Claim decomposition template",
            max_tokens=600,
            temperature=0.2,
        )

        # Evidence evaluation template
        self.templates["factcheck_evidence_evaluation"] = PromptTemplate(
            name="factcheck_evidence_evaluation",
            template="""You are an expert evidence evaluation agent. Assess the quality and reliability of evidence.

Evidence:
{evidence}

Claim: {claim}

Instructions:
1. Evaluate evidence relevance to the claim
2. Assess evidence reliability and credibility
3. Identify potential biases or limitations
4. Rate evidence quality (high/medium/low)
5. Provide specific reasoning for evaluation

Evidence Evaluation:
- Relevance: [high/medium/low] - [explanation]
- Reliability: [high/medium/low] - [explanation]
- Credibility: [high/medium/low] - [explanation]
- Potential Biases: [list any identified biases]
- Limitations: [list limitations]
- Overall Quality: [high/medium/low] - [summary]""",
            variables=["evidence", "claim"],
            template_type=TemplateType.FACT_CHECK,
            description="Evidence evaluation template",
            max_tokens=500,
            temperature=0.1,
        )

    def _add_retrieval_templates(self):
        """Add retrieval agent templates."""

        # Query expansion template
        self.templates["retrieval_query_expansion"] = PromptTemplate(
            name="retrieval_query_expansion",
            template="""You are an expert information retrieval agent. Your task is to expand and refine the query to improve search results.

Original Query: {query}

Instructions:
1. Identify key concepts and entities in the query
2. Generate related terms, synonyms, and alternative phrasings
3. Consider different aspects and perspectives of the query
4. Maintain the original intent and context
5. Generate 3-5 expanded queries that would improve search results
6. Include both broad and specific variations

Key Concepts: [list main concepts]
Entities: [list named entities]
Related Terms: [list related terms]

Expanded Queries:
1. [expanded query 1 - broader scope]
2. [expanded query 2 - specific focus]
3. [expanded query 3 - alternative phrasing]
4. [expanded query 4 - related concept]
5. [expanded query 5 - technical variation]""",
            variables=["query"],
            template_type=TemplateType.RETRIEVAL,
            description="Query expansion template",
            max_tokens=400,
            temperature=0.3,
        )

        # Result reranking template
        self.templates["retrieval_reranking"] = PromptTemplate(
            name="retrieval_reranking",
            template="""You are an expert information retrieval agent. Your task is to rerank search results based on relevance to the query.

Query: {query}

Search Results:
{results}

Instructions:
1. Evaluate each result's relevance to the query
2. Consider accuracy, completeness, recency, and authority
3. Rank results from most to least relevant
4. Provide brief justification for each ranking
5. Consider source credibility and information quality
6. Return only the top {top_k} results

Evaluation Criteria:
- Relevance to query
- Information accuracy
- Completeness of information
- Recency of information
- Source credibility
- Information quality

Reranked Results:
[ranked list with brief justifications for each result]""",
            variables=["query", "results", "top_k"],
            template_type=TemplateType.RETRIEVAL,
            description="Result reranking template",
            max_tokens=600,
            temperature=0.1,
        )

        # Query classification template
        self.templates["retrieval_query_classification"] = PromptTemplate(
            name="retrieval_query_classification",
            template="""You are an expert query analysis agent. Classify the query to determine the best retrieval strategy.

Query: {query}

Instructions:
1. Classify the query type (factual, analytical, procedural, etc.)
2. Identify the query complexity level
3. Determine the best retrieval approach
4. Identify required information types
5. Suggest appropriate search strategies

Query Analysis:
- Query Type: [factual/analytical/procedural/comparative/other]
- Complexity Level: [simple/moderate/complex]
- Information Need: [specific facts/overview/step-by-step/comparison]
- Best Retrieval Strategy: [keyword/vector/hybrid/specialized]
- Required Information Types: [documents/statistics/definitions/examples]
- Suggested Search Terms: [list key search terms]""",
            variables=["query"],
            template_type=TemplateType.RETRIEVAL,
            description="Query classification template",
            max_tokens=300,
            temperature=0.2,
        )

    def _add_citation_templates(self):
        """Add citation agent templates."""

        # Citation generation template
        self.templates["citation_generation"] = PromptTemplate(
            name="citation_generation",
            template="""You are an expert citation agent. Generate proper citations for the provided answer and sources.

Answer: {answer}

Sources:
{sources}

Instructions:
1. Identify which parts of the answer are supported by which sources
2. Generate appropriate citations in {citation_format} format
3. Include page numbers or timestamps when available
4. Ensure citations are accurate and complete
5. Use consistent citation style throughout

Citation Format: {citation_format}

Citations:
[list citations with source references]""",
            variables=["answer", "sources", "citation_format"],
            template_type=TemplateType.CITATION,
            description="Citation generation template",
            max_tokens=500,
            temperature=0.1,
        )

        # Source relevance scoring template
        self.templates["citation_relevance_scoring"] = PromptTemplate(
            name="citation_relevance_scoring",
            template="""You are an expert source evaluation agent. Score the relevance of sources to the query.

Query: {query}

Sources:
{sources}

Instructions:
1. Evaluate each source's relevance to the query
2. Score relevance from 0.0 (irrelevant) to 1.0 (highly relevant)
3. Consider information accuracy, completeness, and recency
4. Provide brief justification for each score
5. Identify the most relevant sources

Relevance Scores:
[source 1]: [score] - [justification]
[source 2]: [score] - [justification]
...

Most Relevant Sources:
[list top 3 most relevant sources]""",
            variables=["query", "sources"],
            template_type=TemplateType.CITATION,
            description="Source relevance scoring template",
            max_tokens=400,
            temperature=0.2,
        )

    def _add_query_processing_templates(self):
        """Add query processing templates."""

        # Query intent classification template
        self.templates["query_intent_classification"] = PromptTemplate(
            name="query_intent_classification",
            template="""You are an expert query analysis agent. Classify the intent and type of the user query.

Query: {query}

Instructions:
1. Identify the primary intent of the query
2. Classify the query type
3. Determine the required information depth
4. Identify any constraints or preferences
5. Suggest appropriate processing approach

Query Analysis:
- Primary Intent: [information seeking/decision making/problem solving/comparison/other]
- Query Type: [factual/analytical/procedural/creative/other]
- Information Depth: [basic/detailed/comprehensive]
- Constraints: [time/scope/complexity/other]
- Processing Approach: [direct retrieval/analysis/synthesis/other]""",
            variables=["query"],
            template_type=TemplateType.QUERY_PROCESSING,
            description="Query intent classification template",
            max_tokens=300,
            temperature=0.2,
        )

        # Query refinement template
        self.templates["query_refinement"] = PromptTemplate(
            name="query_refinement",
            template="""You are an expert query refinement agent. Improve the clarity and specificity of the user query.

Original Query: {query}

Context: {context}

Instructions:
1. Identify ambiguous or unclear aspects of the query
2. Suggest specific refinements to improve clarity
3. Add relevant context or constraints
4. Maintain the original intent
5. Provide 2-3 refined versions of the query

Query Analysis:
- Ambiguous Aspects: [list unclear elements]
- Missing Context: [identify missing information]
- Refinement Suggestions: [list specific improvements]

Refined Queries:
1. [refined query 1 - more specific]
2. [refined query 2 - different focus]
3. [refined query 3 - alternative approach]""",
            variables=["query", "context"],
            template_type=TemplateType.QUERY_PROCESSING,
            description="Query refinement template",
            max_tokens=400,
            temperature=0.3,
        )

    def get_template(self, name: str) -> PromptTemplate:
        """Get a template by name."""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        return self.templates[name]

    def get_templates_by_type(
        self, template_type: TemplateType
    ) -> List[PromptTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.template_type == template_type]

    def add_template(self, template: PromptTemplate):
        """Add a new template."""
        self.templates[template.name] = template
        logger.info(f"Added template: {template.name}")

    def remove_template(self, name: str):
        """Remove a template."""
        if name in self.templates:
            del self.templates[name]
            logger.info(f"Removed template: {name}")

    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.templates.keys())

    def export_templates(self) -> Dict[str, Any]:
        """Export all templates as dictionary."""
        return {name: template.to_dict() for name, template in self.templates.items()}

    def import_templates(self, templates_data: Dict[str, Any]):
        """Import templates from dictionary."""
        for name, data in templates_data.items():
            template = PromptTemplate(
                name=data["name"],
                template=data["template"],
                variables=data.get("variables", []),
                template_type=TemplateType(data["template_type"]),
                language=Language(data["language"]),
                version=data.get("version", "1.0.0"),
                description=data.get("description", ""),
                max_tokens=data.get("max_tokens", 1000),
                temperature=data.get("temperature", 0.2),
            )
            self.templates[name] = template

        logger.info(f"Imported {len(templates_data)} templates")


# Global template manager instance
_template_manager: Optional[PromptTemplateManager] = None


def get_template_manager() -> PromptTemplateManager:
    """Get global template manager instance."""
    global _template_manager

    if _template_manager is None:
        _template_manager = PromptTemplateManager()

    return _template_manager
