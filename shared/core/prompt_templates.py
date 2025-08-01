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

        # Main synthesis template with enhanced system message and citation instructions
        self.templates["synthesis_answer"] = PromptTemplate(
            name="synthesis_answer",
            template="""You are an AI research assistant with expertise in providing accurate, well-sourced answers to questions. Your role is to synthesize information from provided documents and create comprehensive, factual responses.

SYSTEM CONTEXT:
- You are a knowledge synthesis expert working with verified facts and source documents
- Your primary goal is to provide accurate, well-structured answers grounded in the provided evidence
- You must cite sources for every factual claim you make
- If you are unsure about any information, clearly state that you don't know
- Maintain academic rigor and avoid speculation or unsupported claims

USER QUESTION: {query}

RELEVANT DOCUMENTS:
{documents}

INSTRUCTIONS:
1. **Answer the question directly and comprehensively** using only the provided documents
2. **Cite the source for each fact** using the format [1], [2], etc. to reference the documents
3. **Ground your answer in the retrieved content** - do not add information not supported by the documents
4. **If the documents are insufficient** to answer the question completely, acknowledge this clearly
5. **Structure your response logically** with clear sections and flow
6. **Use clear, professional language** appropriate for the subject matter
7. **If documents contain contradictory information**, acknowledge the conflict and present both perspectives
8. **Keep the response concise but complete** (max {max_length} words)
9. **Include a "Sources" section** at the end listing all referenced documents with their titles/URLs

RESPONSE FORMAT:
[Your comprehensive answer with inline citations like [1], [2], etc.]

Sources:
[1] [Document title/URL]
[2] [Document title/URL]
...

Answer:""",
            variables=["query", "documents", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Enhanced synthesis template with explicit citation requirements and factuality guidelines",
            max_tokens=2000,
            temperature=0.2,
        )

        # Enhanced synthesis template with retrieval context
        self.templates["synthesis_with_retrieval"] = PromptTemplate(
            name="synthesis_with_retrieval",
            template="""You are an AI research assistant tasked with answering questions based on retrieved documents and knowledge graph information. Your goal is to provide accurate, well-sourced answers that combine the best available information.

SYSTEM CONTEXT:
- You work with both retrieved documents and knowledge graph data
- Every factual claim must be supported by the provided sources
- Use citation placeholders [1], [2], etc. that will be processed by the CitationAgent
- If information is unclear or contradictory, acknowledge this explicitly
- Maintain high standards for factual accuracy and source attribution

USER QUESTION: {query}

RETRIEVED DOCUMENTS:
{retrieved_docs}

KNOWLEDGE GRAPH INFORMATION:
{kg_info}

INSTRUCTIONS:
1. **Synthesize information** from both retrieved documents and knowledge graph data
2. **Cite sources for every fact** using [1], [2], etc. format
3. **Prioritize retrieved documents** when they contain relevant information
4. **Use knowledge graph data** to supplement and enhance the answer
5. **If sources conflict**, present both perspectives clearly
6. **If information is insufficient**, state this explicitly
7. **Structure the answer** with clear sections and logical flow
8. **Keep response within** {max_length} words
9. **Include source list** at the end for the CitationAgent to process

RESPONSE FORMAT:
[Comprehensive answer with inline citations]

Sources:
[1] [Document title/URL]
[2] [Knowledge graph entity/relation]
...

Answer:""",
            variables=["query", "retrieved_docs", "kg_info", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Synthesis template for combining retrieved documents and knowledge graph data",
            max_tokens=2000,
            temperature=0.2,
        )

        # Summary synthesis template
        self.templates["synthesis_summary"] = PromptTemplate(
            name="synthesis_summary",
            template="""You are an expert summarization agent. Create a concise summary of the provided information with proper source attribution.

SYSTEM CONTEXT:
- You are creating summaries that maintain factual accuracy
- Every key point must be traceable to a source
- Use citation placeholders for source attribution
- Focus on the most important and relevant information

CONTENT TO SUMMARIZE:
{content}

INSTRUCTIONS:
1. Create a clear, concise summary of the key points
2. Maintain factual accuracy and source attribution
3. Use bullet points for clarity when appropriate
4. Keep summary under {max_length} words
5. Include citation placeholders [1], [2], etc. for key facts
6. Focus on the most important information
7. Maintain logical structure and flow

Summary:""",
            variables=["content", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Summary synthesis template with citation requirements",
            max_tokens=800,
            temperature=0.2,
        )

        # Comparative synthesis template
        self.templates["synthesis_comparison"] = PromptTemplate(
            name="synthesis_comparison",
            template="""You are an expert comparative analysis agent. Compare and contrast the provided information with proper source attribution.

SYSTEM CONTEXT:
- You are conducting comparative analysis with high factual standards
- All claims must be supported by the provided sources
- Use citation placeholders for source attribution
- Present balanced, objective comparisons

TOPIC A: {topic_a}
INFORMATION A: {info_a}

TOPIC B: {topic_b}
INFORMATION B: {info_b}

INSTRUCTIONS:
1. Identify key similarities and differences between the topics
2. Provide balanced, objective analysis
3. Use clear comparison structure with sections
4. Support all claims with citations [1], [2], etc.
5. Highlight important distinctions and implications
6. Acknowledge any limitations in the available information
7. Present findings in a logical, organized manner

Comparative Analysis:""",
            variables=["topic_a", "info_a", "topic_b", "info_b"],
            template_type=TemplateType.SYNTHESIS,
            description="Comparative analysis template with citation requirements",
            max_tokens=1500,
            temperature=0.2,
        )

        # Hybrid retrieval synthesis template
        self.templates["synthesis_hybrid_retrieval"] = PromptTemplate(
            name="synthesis_hybrid_retrieval",
            template="""You are an AI research assistant tasked with answering questions using a combination of retrieved documents and knowledge graph information. Your goal is to provide accurate, well-sourced answers that leverage the best available information from multiple sources.

SYSTEM CONTEXT:
- You work with both retrieved documents and knowledge graph data
- Every factual claim must be supported by the provided sources
- Use citation placeholders [1], [2], etc. that will be processed by the CitationAgent
- If information is unclear or contradictory, acknowledge this explicitly
- Maintain high standards for factual accuracy and source attribution
- Prioritize retrieved documents when they contain relevant information
- Use knowledge graph data to supplement and enhance the answer

USER QUESTION: {query}

RETRIEVED DOCUMENTS:
{retrieved_docs}

KNOWLEDGE GRAPH INFORMATION:
{kg_info}

INSTRUCTIONS:
1. **Synthesize information** from both retrieved documents and knowledge graph data
2. **Cite sources for every fact** using [1], [2], etc. format
3. **Prioritize retrieved documents** when they contain relevant information
4. **Use knowledge graph data** to supplement and enhance the answer
5. **If sources conflict**, present both perspectives clearly
6. **If information is insufficient**, state this explicitly
7. **Structure the answer** with clear sections and logical flow
8. **Keep response within** {max_length} words
9. **Include source list** at the end for the CitationAgent to process
10. **Ground your answer in the retrieved content** - do not add information not supported by the sources

RESPONSE FORMAT:
[Comprehensive answer with inline citations]

Sources:
[1] [Document title/URL]
[2] [Knowledge graph entity/relation]
...

Answer:""",
            variables=["query", "retrieved_docs", "kg_info", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Hybrid retrieval synthesis template combining documents and knowledge graph data",
            max_tokens=2000,
            temperature=0.2,
        )

        # Fact-checking synthesis template
        self.templates["synthesis_fact_checked"] = PromptTemplate(
            name="synthesis_fact_checked",
            template="""You are an AI research assistant creating answers based on fact-checked information. Your role is to synthesize verified facts into coherent, well-structured responses with proper source attribution.

SYSTEM CONTEXT:
- You are working with fact-checked information that has been verified against reliable sources
- Every claim in your answer should be supported by verified facts
- Use citation placeholders [1], [2], etc. for source attribution
- If facts are contradictory, acknowledge the conflict clearly
- Maintain high standards for factual accuracy and transparency
- If verification is incomplete or uncertain, state this explicitly

USER QUESTION: {query}

VERIFIED FACTS:
{verified_facts}

INSTRUCTIONS:
1. **Synthesize verified facts** into a comprehensive answer
2. **Cite sources for every claim** using [1], [2], etc. format
3. **Address the question directly** using only verified information
4. **If facts are contradictory**, present both perspectives clearly
5. **If verification is incomplete**, acknowledge limitations
6. **Structure the answer** logically with clear sections
7. **Keep response within** {max_length} words
8. **Include confidence levels** for claims when available
9. **Provide a source list** at the end for the CitationAgent

RESPONSE FORMAT:
[Comprehensive answer with inline citations and confidence indicators]

Sources:
[1] [Verified source with confidence level]
[2] [Verified source with confidence level]
...

Answer:""",
            variables=["query", "verified_facts", "max_length"],
            template_type=TemplateType.SYNTHESIS,
            description="Synthesis template for fact-checked information with confidence indicators",
            max_tokens=2000,
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

        # Enhanced citation generation template
        self.templates["citation_generation"] = PromptTemplate(
            name="citation_generation",
            template="""You are an expert citation agent. Process the provided answer and generate proper citations for all source references.

SYSTEM CONTEXT:
- You are processing answers that contain citation placeholders [1], [2], etc.
- Your task is to replace these placeholders with proper formatted citations
- Maintain the academic rigor and accuracy of the original content
- Ensure all citations are complete and properly formatted

ANSWER WITH CITATION PLACEHOLDERS:
{answer}

AVAILABLE SOURCES:
{sources}

CITATION FORMAT: {citation_format}

INSTRUCTIONS:
1. **Identify all citation placeholders** [1], [2], etc. in the answer
2. **Match placeholders to sources** based on content relevance
3. **Generate proper citations** in the specified format ({citation_format})
4. **Replace placeholders** with formatted citations
5. **Ensure citation accuracy** - verify source-content matches
6. **Add missing citations** if facts lack proper attribution
7. **Create a comprehensive source list** at the end
8. **Maintain answer readability** while adding citations

PROCESSING STEPS:
1. Parse the answer for citation placeholders
2. Match each placeholder to the most relevant source
3. Generate formatted citations for each source
4. Replace placeholders with citations
5. Create final source list

FORMATTED ANSWER WITH CITATIONS:
[Answer with proper citations replacing placeholders]

SOURCES:
[Complete list of all referenced sources with full citations]

Processed Answer:""",
            variables=["answer", "sources", "citation_format"],
            template_type=TemplateType.CITATION,
            description="Enhanced citation generation template for processing synthesis outputs",
            max_tokens=1000,
            temperature=0.1,
        )

        # Citation validation template
        self.templates["citation_validation"] = PromptTemplate(
            name="citation_validation",
            template="""You are an expert citation validation agent. Verify that all factual claims in the answer are properly supported by the provided sources.

SYSTEM CONTEXT:
- You are validating the accuracy and completeness of citations
- Every factual claim should have a corresponding source
- Identify any unsupported claims or missing citations
- Ensure citation-source matches are accurate

ANSWER TO VALIDATE:
{answer}

AVAILABLE SOURCES:
{sources}

INSTRUCTIONS:
1. **Identify all factual claims** in the answer
2. **Check each claim** against the available sources
3. **Verify citation accuracy** - ensure citations match sources
4. **Flag unsupported claims** that lack proper citations
5. **Identify missing citations** for factual statements
6. **Assess source quality** and relevance
7. **Provide validation report** with specific issues
8. **Suggest improvements** for citation completeness

VALIDATION REPORT:
- Total factual claims identified: [number]
- Claims with proper citations: [number]
- Claims missing citations: [list]
- Citation-source mismatches: [list]
- Overall citation quality: [excellent/good/fair/poor]
- Recommendations: [specific improvements needed]

Validation Results:""",
            variables=["answer", "sources"],
            template_type=TemplateType.CITATION,
            description="Citation validation template for quality assurance",
            max_tokens=800,
            temperature=0.1,
        )

        # Source relevance scoring template
        self.templates["citation_relevance_scoring"] = PromptTemplate(
            name="citation_relevance_scoring",
            template="""You are an expert source evaluation agent. Score the relevance and reliability of sources for the given query and answer.

SYSTEM CONTEXT:
- You are evaluating source quality and relevance
- Consider information accuracy, completeness, and recency
- Assess source reliability and authority
- Provide detailed scoring with justifications

QUERY: {query}

ANSWER: {answer}

SOURCES TO EVALUATE:
{sources}

INSTRUCTIONS:
1. **Evaluate each source's relevance** to the query (0.0-1.0)
2. **Assess source reliability** and authority
3. **Check information accuracy** and completeness
4. **Consider source recency** and currency
5. **Score information quality** (0.0-1.0)
6. **Provide detailed justifications** for each score
7. **Identify the most relevant sources** for the query
8. **Flag any unreliable or irrelevant sources**

EVALUATION CRITERIA:
- Relevance to query topic
- Information accuracy and completeness
- Source authority and credibility
- Information recency and currency
- Citation quality and formatting

SOURCE SCORES:
[Source 1]: Relevance: [score] - Reliability: [score] - Justification: [details]
[Source 2]: Relevance: [score] - Reliability: [score] - Justification: [details]
...

TOP RECOMMENDED SOURCES:
[list top 3-5 most relevant and reliable sources]

OVERALL ASSESSMENT:
- Average relevance score: [score]
- Average reliability score: [score]
- Quality recommendations: [specific improvements]""",
            variables=["query", "answer", "sources"],
            template_type=TemplateType.CITATION,
            description="Enhanced source relevance scoring template",
            max_tokens=600,
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
