"""
Advanced citation agent that generates proper citations for sources.
"""

import asyncio
import logging
import time
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from shared.core.agents.base_agent import (
    BaseAgent,
    AgentType,
    AgentMessage,
    AgentResult,
    QueryContext,
)
from shared.core.agents.data_models import CitationResult, CitationModel
from shared.core.agents.agent_utilities import (
    AgentTaskProcessor,
    ResponseFormatter,
    time_agent_function,
)
from shared.core.agents.validation_utilities import CommonValidators

# Configure logging
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

# Environment configuration
DEFAULT_TOKEN_BUDGET = int(os.getenv("DEFAULT_TOKEN_BUDGET", "1000"))


@dataclass
class Citation:
    """Represents a citation with metadata."""

    id: str
    text: str
    url: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary for serialization."""
        return {
            "id": self.id,
            "text": self.text,
            "url": self.url,
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "source": self.source,
            "confidence": self.confidence,
        }


class CitationAgent(BaseAgent):
    """
    CitationAgent that generates proper citations and integrates them into the answer text.
    """

    def __init__(self):
        """Initialize the citation agent."""
        super().__init__(agent_id="citation_agent", agent_type=AgentType.CITATION)

        # Initialize shared utilities
        self.task_processor = AgentTaskProcessor(self.agent_id)
        self.logger = get_logger(f"{__name__}.{self.agent_id}")

        # Initialize citation formats - using generic format for all styles
        self.citation_formats = {
            "academic": self._format_citation,
            "apa": self._format_citation,
            "mla": self._format_citation,
            "chicago": self._format_citation,
            "url": self._format_citation,
        }

        logger.info("✅ CitationAgent initialized successfully")

    @time_agent_function("citation_agent")
    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Process citation task using shared utilities.

        This method now uses the standardized workflow from AgentTaskProcessor
        to eliminate duplicate logic and ensure consistent behavior.
        """
        # Use shared task processor with validation
        result = await self.task_processor.process_task_with_workflow(
            task=task,
            context=context,
            processing_func=self._process_citation_task,
            validation_func=CommonValidators.validate_sources_input,
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

    async def _process_citation_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> Dict[str, Any]:
        """
        Process citation task by generating proper citations for content and sources.

        Args:
            task: Task data containing content and sources
            context: Query context

        Returns:
            Dictionary with cited content
        """
        # Extract task data
        answer = task.get("answer", "")
        sources = task.get("sources", [])
        citation_format = task.get("citation_format", "academic")
        citation_style = task.get("citation_style", "apa")

        logger.info(f"Processing citations for answer of length: {len(answer)}")
        logger.info(f"Number of sources: {len(sources)}")

        # Import prompt template manager
        from shared.core.prompt_templates import get_template_manager

        template_manager = get_template_manager()

        # Use enhanced citation generation template
        citation_template = template_manager.get_template("citation_generation")

        # Format sources for the template
        sources_text = ""
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                title = source.get("title", f"Source {i}")
                url = source.get("url", "")
                author = source.get("author", "")
                date = source.get("date", "")
                source_text = f"[{i}] {title}"
                if author:
                    source_text += f" by {author}"
                if date:
                    source_text += f" ({date})"
                if url:
                    source_text += f" - {url}"
            else:
                source_text = f"[{i}] {str(source)}"
            sources_text += source_text + "\n"

        # Format the citation prompt using the template
        citation_prompt = citation_template.format(
            answer=answer, sources=sources_text, citation_format=citation_format
        )

        # Use LLM for citation processing with dynamic model selection
        from shared.core.agents.llm_client import LLMClient
        from shared.core.llm_client_v3 import LLMRequest

        llm_client = LLMClient()

        # Create LLMRequest with system message for citation processing
        system_message = """You are an expert citation agent specializing in academic and professional citation formatting. Your role is to process answers containing citation placeholders and generate proper, formatted citations.

Your primary responsibilities:
- Identify all citation placeholders [1], [2], etc. in the provided answer
- Match each placeholder to the most relevant source based on content
- Generate proper citations in the specified format (APA, MLA, Chicago, etc.)
- Replace placeholders with formatted citations while maintaining answer readability
- Ensure citation accuracy by verifying source-content matches
- Add missing citations for factual statements that lack proper attribution
- Create a comprehensive source list at the end
- Maintain the academic rigor and accuracy of the original content

Processing guidelines:
- Be precise and accurate in citation formatting
- Maintain consistency throughout the document
- Ensure all factual claims have proper source attribution
- Handle multiple citation formats appropriately
- Provide clear, readable citations that enhance the answer's credibility"""

        llm_request = LLMRequest(
            prompt=citation_prompt,
            system_message=system_message,
            max_tokens=1500,
            temperature=0.1,  # Very low temperature for precise citation formatting
        )

        # Use dynamic model selection for citation processing
        # For citation processing, we'll use a simpler query since it's about formatting
        citation_query = f"Format citations in {citation_format} style"

        response = await llm_client._client.generate_text(
            prompt=citation_prompt,
            max_tokens=1500,
            temperature=0.1,
            query=citation_query,  # Pass citation-specific query for model selection
            use_dynamic_selection=True,
        )

        if response and response.strip():
            # Extract the processed answer from the response
            # Look for the "Processed Answer:" section
            if "Processed Answer:" in response:
                processed_answer = response.split("Processed Answer:")[1].strip()
            else:
                processed_answer = response.strip()

            return {
                "cited_answer": processed_answer,
                "original_answer": answer,
                "sources": sources,
                "citation_format": citation_format,
                "confidence": 0.9,  # High confidence for citation processing
            }
        else:
            # Fallback to basic citation formatting
            return await self._fallback_citation_processing(
                answer, sources, citation_format
            )

    async def _fallback_citation_processing(
        self, answer: str, sources: List[Dict], citation_format: str
    ) -> Dict[str, Any]:
        """
        Fallback citation processing when LLM is unavailable.

        Args:
            answer: Original answer with citation placeholders
            sources: List of sources
            citation_format: Citation format to use

        Returns:
            Dictionary with basic citation processing
        """
        try:
            # Simple placeholder replacement
            processed_answer = answer

            # Replace citation placeholders with basic citations
            for i, source in enumerate(sources, 1):
                if isinstance(source, dict):
                    title = source.get("title", f"Source {i}")
                    url = source.get("url", "")
                    citation_text = f"({title})"
                    if url:
                        citation_text = f"({title}, {url})"
                else:
                    citation_text = f"(Source {i})"

                # Replace [i] placeholders with citations
                processed_answer = processed_answer.replace(f"[{i}]", citation_text)

            return {
                "cited_answer": processed_answer,
                "original_answer": answer,
                "sources": sources,
                "citation_format": citation_format,
                "confidence": 0.7,  # Lower confidence for fallback processing
            }
        except Exception as e:
            logger.error(f"Fallback citation processing failed: {e}")
            return {
                "cited_answer": answer,
                "original_answer": answer,
                "sources": sources,
                "citation_format": citation_format,
                "confidence": 0.0,
                "error": f"Fallback citation processing failed: {str(e)}",
            }

    async def _generate_citations(
        self, sources: List[Dict], style: str
    ) -> List[Citation]:
        """
        Generate citations from sources.

        Args:
            sources: List of source documents
            style: Citation style (APA, MLA, etc.)

        Returns:
            List of Citation objects
        """
        citations = []

        for i, source in enumerate(sources):
            try:
                # Extract metadata from source
                source_id = source.get("doc_id", f"source_{i+1}")
                content = source.get("content", "")
                metadata = source.get("metadata", {})

                # Generate citation text
                citation_text = await self._format_citation(source, style)

                citation = Citation(
                    id=source_id,
                    text=citation_text,
                    url=metadata.get("url"),
                    title=metadata.get("title"),
                    author=metadata.get("author"),
                    date=metadata.get("date"),
                    source=metadata.get("source"),
                    confidence=source.get("score", 1.0),
                )

                citations.append(citation)

            except Exception as e:
                logger.warning(f"Failed to generate citation for source {i}: {e}")
                continue

        return citations

    async def _format_citation(self, source: Dict, style: str) -> str:
        """
        Format citation according to specified style with improved metadata handling.

        Args:
            source: Source document
            style: Citation style

        Returns:
            Formatted citation text
        """
        metadata = source.get("metadata", {})

        # Extract metadata with intelligent fallbacks
        author = self._extract_author(metadata, source)
        title = self._extract_title(metadata, source)
        date = self._extract_date(metadata, source)
        url = self._extract_url(metadata, source)
        source_type = metadata.get("source", "unknown")

        if style.upper() == "APA":
            if url and url.startswith("http"):
                return f"{author} ({date}). {title}. Retrieved from {url}"
            else:
                return f"{author} ({date}). {title}."

        elif style.upper() == "MLA":
            if url and url.startswith("http"):
                return f'"{title}." {author}, {date}, {url}.'
            else:
                return f'"{title}." {author}, {date}.'

        elif style.upper() == "CHICAGO":
            if url and url.startswith("http"):
                return f'{author}. "{title}." {date}. {url}.'
            else:
                return f'{author}. "{title}." {date}.'

        else:
            # Default academic format
            if url and url.startswith("http"):
                return f"{author} ({date}). {title}. {url}"
            else:
                return f"{author} ({date}). {title}."

    def _extract_author(self, metadata: Dict, source: Dict) -> str:
        """Extract author with intelligent fallbacks."""
        # Try multiple possible author fields
        author = (
            metadata.get("author")
            or metadata.get("authors")
            or metadata.get("creator")
            or metadata.get("byline")
            or source.get("author")
        )

        if author:
            return author

        # Try to extract from URL domain
        url = metadata.get("url") or source.get("url") or source.get("link")
        if url:
            try:
                from urllib.parse import urlparse

                domain = urlparse(url).netloc
                if domain and domain != "unknown":
                    return f"{domain.replace('www.', '').title()}"
            except:
                pass

        return "Unknown Author"

    def _extract_title(self, metadata: Dict, source: Dict) -> str:
        """Extract title with intelligent fallbacks."""
        title = metadata.get("title") or metadata.get("name") or source.get("title")

        if title:
            return title

        # Try to extract from content
        content = source.get("content", "")
        if content:
            # Use first sentence as title
            sentences = content.split(".")
            if sentences:
                potential_title = sentences[0].strip()
                if len(potential_title) > 10 and len(potential_title) < 100:
                    return potential_title

        return "Untitled Document"

    def _extract_date(self, metadata: Dict, source: Dict) -> str:
        """Extract date with intelligent fallbacks."""
        date = (
            metadata.get("date")
            or metadata.get("published_date")
            or metadata.get("created_date")
            or source.get("date")
        )

        if date:
            return date

        # Try to extract from URL or content
        url = metadata.get("url") or source.get("url")
        if url:
            # Look for date patterns in URL
            import re

            date_patterns = [
                r"/(\d{4})/(\d{2})/(\d{2})/",  # YYYY/MM/DD
                r"/(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
                r"(\d{4})_(\d{2})_(\d{2})",  # YYYY_MM_DD
            ]

            for pattern in date_patterns:
                match = re.search(pattern, url)
                if match:
                    year, month, day = match.groups()
                    return f"{year}"

        return "n.d."

    def _extract_url(self, metadata: Dict, source: Dict) -> str:
        """Extract URL with intelligent fallbacks."""
        url = (
            metadata.get("url")
            or metadata.get("link")
            or source.get("url")
            or source.get("link")
        )

        if url and url.startswith("http"):
            return url

        # Try to construct URL from source info
        source_type = metadata.get("source", "unknown")
        if source_type == "serp_api" or source_type == "google_cse":
            return "Retrieved from web search"
        elif source_type == "vector_search":
            return "Retrieved from knowledge base"
        elif source_type == "keyword_search":
            return "Retrieved from document search"

        return ""

    async def _integrate_citations(
        self, content: str, sources: List[Dict], citations: List[Citation]
    ) -> str:
        """
        Integrate citations into content text.

        Args:
            content: Original content
            sources: List of source documents
            citations: List of citations

        Returns:
            Tuple of (cited_content, in_text_citations)
        """
        if not citations:
            return content

        cited_content = content

        # Simple citation integration - add citation numbers to sentences
        sentences = re.split(r"[.!?]+", content)
        cited_sentences = []

        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Find relevant citations for this sentence
                relevant_citations = self._find_relevant_citations(sentence, citations)

                if relevant_citations:
                    # Add citation numbers to sentence
                    citation_numbers = [str(cit.id) for cit in relevant_citations]
                    cited_sentence = (
                        f"{sentence.strip()} [{', '.join(citation_numbers)}]."
                    )

                    # Track in-text citations
                    for citation in relevant_citations:
                        # Implement in-text citation tracking
                        citation_text = f" [{citation.source}]"
                        cited_sentence = f"{sentence.strip()}{citation_text}."

                        # Track citation usage for analytics
                        logger.info(
                            "Citation used in sentence",
                            extra={
                                "citation_id": citation.id,
                                "source": citation.source,
                                "sentence_preview": sentence[:100],
                            },
                        )
                else:
                    cited_sentence = f"{sentence.strip()}."

                cited_sentences.append(cited_sentence)

        cited_content = " ".join(cited_sentences)

        return cited_content

    def _find_relevant_citations(
        self, sentence: str, citations: List[Citation]
    ) -> List[Citation]:
        """
        Find citations relevant to a sentence.

        Args:
            sentence: Sentence to find citations for
            citations: List of available citations

        Returns:
            List of relevant citations
        """
        relevant_citations = []

        # Simple keyword matching
        sentence_lower = sentence.lower()

        for citation in citations:
            # Check if citation text contains keywords from sentence
            citation_text_lower = citation.text.lower()

            # Extract key terms from sentence (simple approach)
            words = sentence_lower.split()
            key_words = [w for w in words if len(w) > 3]  # Focus on longer words

            # Check if any key words appear in citation
            for word in key_words:
                if word in citation_text_lower:
                    relevant_citations.append(citation)
                    break

        return relevant_citations[:3]  # Limit to 3 citations per sentence

    async def _generate_bibliography(
        self, citations: List[Citation], style: str
    ) -> List[str]:
        """
        Generate bibliography from citations.

        Args:
            citations: List of citations
            style: Citation style

        Returns:
            List of bibliography entries
        """
        bibliography = []

        for citation in citations:
            bibliography.append(citation.text)

        return bibliography


# Example usage
async def main():
    """Example usage of CitationAgent."""
    agent = CitationAgent()

    # Example content and sources
    content = "The Earth orbits around the Sun. The Sun is a star."
    sources = [
        {
            "doc_id": "source_1",
            "content": "Information about Earth's orbit",
            "metadata": {
                "author": "NASA",
                "title": "Solar System Overview",
                "date": "2023",
                "url": "https://nasa.gov/solar-system",
            },
        },
        {
            "doc_id": "source_2",
            "content": "Information about the Sun",
            "metadata": {
                "author": "Astronomy Society",
                "title": "Stars and Stellar Evolution",
                "date": "2023",
                "url": "https://astronomy.org/stars",
            },
        },
    ]

    task = {"content": content, "sources": sources, "format": "APA"}

    context = QueryContext(query="What is the relationship between Earth and the Sun?")

    result = await agent.process_task(task, context)
    print(f"Success: {result.get('success')}")
    print(f"Cited Content: {result.get('data', {}).get('cited_content', '')}")
    print(f"Bibliography: {result.get('data', {}).get('bibliography', [])}")


if __name__ == "__main__":
    asyncio.run(main())
