"""
Citation Agent

This module provides the citation agent for the backend synthesis service.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@dataclass
class CitationResult:
    """Represents the result of citation generation."""
    
    annotated_answer: str
    citations: List[Dict[str, Any]]
    citation_map: Dict[str, List[int]]  # Maps citation IDs to sentence indices
    total_citations: int
    citation_style: str


class CitationAgent(BaseAgent):
    """
    Enhanced CitationAgent that generates proper citations and integrates them into the answer text.
    """

    def __init__(self):
        """Initialize the citation agent."""
        super().__init__(agent_id="citation_agent", agent_type=AgentType.CITATION)

        # Initialize citation formats - using generic format for all styles
        self.citation_formats = {
            "academic": self._format_citation,
            "apa": self._format_citation,
            "mla": self._format_citation,
            "chicago": self._format_citation,
            "url": self._format_citation,
        }

        logger.info("✅ Enhanced CitationAgent initialized successfully")

    async def generate_citations(
        self, 
        answer_text: str, 
        source_docs: List[Dict[str, Any]], 
        verified_sentences: Optional[List[Dict[str, Any]]] = None
    ) -> CitationResult:
        """
        Generate inline citations for the answer text based on source documents.
        
        Args:
            answer_text: The answer text to annotate with citations
            source_docs: List of source documents
            verified_sentences: Optional list of verified sentences from fact checker
            
        Returns:
            CitationResult with annotated answer and citation list
        """
        start_time = time.time()
        
        try:
            # Split answer into sentences
            sentences = self._split_into_sentences(answer_text)
            
            # Create citation list from source documents
            citations = await self._create_citation_list(source_docs)
            
            # Map sentences to supporting sources
            sentence_citations = await self._map_sentences_to_sources(
                sentences, source_docs, verified_sentences
            )
            
            # Generate annotated answer with inline citations
            annotated_answer = self._add_inline_citations(
                sentences, sentence_citations, citations
            )
            
            # Create citation list for the end
            citation_list = self._create_citation_list_for_output(citations)
            
            # Create citation map for tracking
            citation_map = self._create_citation_map(sentence_citations, citations)
            
            processing_time = time.time() - start_time
            
            return CitationResult(
                annotated_answer=annotated_answer,
                citations=citation_list,
                citation_map=citation_map,
                total_citations=len(citations),
                citation_style="inline"
            )
            
        except Exception as e:
            logger.error(f"Citation generation failed: {str(e)}")
            return CitationResult(
                annotated_answer=answer_text,
                citations=[],
                citation_map={},
                total_citations=0,
                citation_style="error"
            )

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split on sentence endings, but be careful with abbreviations
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences

    async def _create_citation_list(self, source_docs: List[Dict[str, Any]]) -> List[Citation]:
        """
        Create citation list from source documents.
        
        Args:
            source_docs: Source documents
            
        Returns:
            List of Citation objects
        """
        citations = []
        
        for i, doc in enumerate(source_docs, 1):
            citation = Citation(
                id=str(i),
                text=doc.get("content", "")[:100] + "...",
                url=doc.get("url", ""),
                title=doc.get("title", f"Source {i}"),
                author=doc.get("author", ""),
                date=doc.get("timestamp", doc.get("date", "")),
                source=doc.get("source", ""),
                confidence=doc.get("score", 1.0)
            )
            citations.append(citation)
        
        return citations

    async def _map_sentences_to_sources(
        self, 
        sentences: List[str], 
        source_docs: List[Dict[str, Any]], 
        verified_sentences: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[int, List[str]]:
        """
        Map sentences to supporting source citations.
        
        Args:
            sentences: List of sentences from answer
            source_docs: Source documents
            verified_sentences: Optional verified sentences from fact checker
            
        Returns:
            Dictionary mapping sentence index to list of citation IDs
        """
        sentence_citations = {}
        
        for i, sentence in enumerate(sentences):
            supporting_citations = []
            
            # If we have verified sentences from fact checker, use that information
            if verified_sentences:
                # Check if this sentence is in verified sentences
                sentence_text = sentence.lower().strip()
                for verified in verified_sentences:
                    verified_text = verified.get("sentence", "").lower().strip()
                    if self._sentences_match(sentence_text, verified_text):
                        # Use the source documents from verified sentence
                        source_doc_ids = verified.get("source_docs", [])
                        for doc_id in source_doc_ids:
                            # Find the corresponding citation ID
                            for j, doc in enumerate(source_docs, 1):
                                if doc.get("doc_id") == doc_id:
                                    supporting_citations.append(str(j))
                                    break
                        break
            else:
                # Fallback to semantic similarity matching
                for j, doc in enumerate(source_docs, 1):
                    if self._sentence_supported_by_source(sentence, doc):
                        supporting_citations.append(str(j))
            
            if supporting_citations:
                sentence_citations[i] = supporting_citations
        
        return sentence_citations

    def _sentences_match(self, sentence1: str, sentence2: str) -> bool:
        """
        Check if two sentences match (for verified sentence mapping).
        
        Args:
            sentence1: First sentence
            sentence2: Second sentence
            
        Returns:
            True if sentences match
        """
        # Simple similarity check
        words1 = set(re.findall(r'\b\w+\b', sentence1.lower()))
        words2 = set(re.findall(r'\b\w+\b', sentence2.lower()))
        
        if not words1 or not words2:
            return False
        
        # Calculate overlap
        overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        
        similarity = overlap / total_words if total_words > 0 else 0
        return similarity > 0.6  # 60% similarity threshold

    def _sentence_supported_by_source(self, sentence: str, source_doc: Dict[str, Any]) -> bool:
        """
        Check if a sentence is supported by a source document.
        
        Args:
            sentence: Sentence to check
            source_doc: Source document
            
        Returns:
            True if sentence is supported by source
        """
        sentence_lower = sentence.lower()
        source_content = source_doc.get("content", "").lower()
        
        # Extract key terms from sentence
        sentence_terms = set(re.findall(r'\b\w+\b', sentence_lower))
        sentence_terms = {term for term in sentence_terms if len(term) > 3}
        
        if not sentence_terms:
            return False
        
        # Check if key terms appear in source content
        matches = sum(1 for term in sentence_terms if term in source_content)
        match_ratio = matches / len(sentence_terms) if sentence_terms else 0
        
        return match_ratio > 0.3  # 30% of key terms must match

    def _add_inline_citations(
        self, 
        sentences: List[str], 
        sentence_citations: Dict[int, List[str]], 
        citations: List[Citation]
    ) -> str:
        """
        Add inline citations to sentences.
        
        Args:
            sentences: List of sentences
            sentence_citations: Mapping of sentence index to citation IDs
            citations: List of citation objects
            
        Returns:
            Annotated answer with inline citations
        """
        annotated_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i in sentence_citations:
                # Add citation tags to the sentence
                citation_ids = sentence_citations[i]
                citation_tags = [f"[{cid}]" for cid in citation_ids]
                annotated_sentence = f"{sentence} {' '.join(citation_tags)}"
                annotated_sentences.append(annotated_sentence)
            else:
                # No citations for this sentence
                annotated_sentences.append(sentence)
        
        return " ".join(annotated_sentences)

    def _create_citation_list_for_output(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """
        Create citation list for output format.
        
        Args:
            citations: List of citation objects
            
        Returns:
            List of citation dictionaries
        """
        citation_list = []
        
        for citation in citations:
            citation_dict = {
                "id": int(citation.id),
                "title": citation.title or f"Source {citation.id}",
                "url": citation.url or "",
                "author": citation.author or "",
                "date": citation.date or "",
                "source": citation.source or "",
                "confidence": citation.confidence
            }
            citation_list.append(citation_dict)
        
        return citation_list

    def _create_citation_map(
        self, 
        sentence_citations: Dict[int, List[str]], 
        citations: List[Citation]
    ) -> Dict[str, List[int]]:
        """
        Create citation map for tracking which sentences use which citations.
        
        Args:
            sentence_citations: Mapping of sentence index to citation IDs
            citations: List of citation objects
            
        Returns:
            Dictionary mapping citation ID to list of sentence indices
        """
        citation_map = {}
        
        for sentence_idx, citation_ids in sentence_citations.items():
            for citation_id in citation_ids:
                if citation_id not in citation_map:
                    citation_map[citation_id] = []
                citation_map[citation_id].append(sentence_idx)
        
        return citation_map

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """
        Process citation task by generating proper citations for content and sources.

        Args:
            task: Task data containing content and sources
            context: Query context

        Returns:
            AgentResult with cited content
        """
        start_time = time.time()

        try:
            # Extract task data
            content = task.get("content", "")
            sources = task.get("sources", [])
            verified_sentences = task.get("verified_sentences", None)
            citation_style = task.get("citation_style", "inline")

            logger.info(f"Generating citations for content: {content[:50]}...")
            logger.info(f"Number of sources: {len(sources)}")

            # Generate citations using the new method
            citation_result = await self.generate_citations(content, sources, verified_sentences)

            processing_time = time.time() - start_time

            # Create standardized citation result
            citation_data = CitationResult(
                cited_content=citation_result.annotated_answer,
                bibliography=[f"{c['id']}. {c['title']} - {c['url']}" for c in citation_result.citations],
                in_text_citations=citation_result.citations,
                citation_style=citation_style,
                metadata={
                    "agent_id": self.agent_id,
                    "total_citations": citation_result.total_citations,
                    "citation_map": citation_result.citation_map,
                },
            )

            return AgentResult(
                success=True,
                data=citation_data.model_dump(),
                confidence=1.0,
                execution_time_ms=int(processing_time * 1000),
            )

        except Exception as e:
            logger.error(f"Citation generation failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=f"Citation generation failed: {str(e)}",
                confidence=0.0,
            )

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
                            citation_id=citation.id,
                            source=citation.source,
                            sentence_preview=sentence[:100],
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
    print(f"Success: {result.success}")
    print(f"Cited Content: {result.data.get('cited_content', '')}")
    print(f"Bibliography: {result.data.get('bibliography', [])}")


if __name__ == "__main__":
    asyncio.run(main())
