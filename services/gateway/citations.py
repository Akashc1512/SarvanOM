#!/usr/bin/env python3
"""
Citations & Fact-Check System

Implements citation generation and fact-checking capabilities:
- Sentence-source alignment using cosine similarity
- Citation marker insertion [1][2] format
- Bibliography generation with numbered sources
- Uncertainty detection for unverified claims
- Integration with streaming responses

Following MAANG/OpenAI/Perplexity standards for traceable answers.
"""

import re
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from services.retrieval.free_tier import SearchResult, SearchProvider

# Configure logging
logger = logging.getLogger(__name__)

# Import sentence transformers for similarity calculation
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback similarity")


@dataclass
class Citation:
    """Represents a citation with source information."""
    marker: str  # e.g., "[1]", "[2]"
    source: SearchResult
    confidence: float  # 0.0 to 1.0
    sentence_start: int  # Character position in text
    sentence_end: int
    claim_type: str = "factual"  # factual, opinion, uncertain


@dataclass
class FactCheckResult:
    """Result of fact-checking a piece of text."""
    text: str
    citations: List[Citation]
    bibliography: List[Dict[str, Any]]
    uncertainty_flags: List[str]
    overall_confidence: float


class ClaimType(str, Enum):
    """Types of claims that can be made."""
    FACTUAL = "factual"
    OPINION = "opinion"
    UNCERTAIN = "uncertain"
    UNVERIFIED = "unverified"


class CitationsManager:
    """Manages citation generation and fact-checking."""
    
    def __init__(self):
        self.similarity_model = None
        self._initialize_similarity_model()
    
    def _initialize_similarity_model(self):
        """Initialize sentence similarity model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight model for speed
                self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Sentence similarity model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize similarity model: {e}")
                self.similarity_model = None
        else:
            logger.warning("Using fallback similarity calculation")
    
    def _calculate_similarity_fallback(self, sentence: str, source_text: str) -> float:
        """Fallback similarity calculation using word overlap."""
        sentence_words = set(sentence.lower().split())
        source_words = set(source_text.lower().split())
        
        if not sentence_words or not source_words:
            return 0.0
        
        intersection = sentence_words.intersection(source_words)
        union = sentence_words.union(source_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _calculate_similarity(self, sentence: str, source_text: str) -> float:
        """Calculate similarity between sentence and source text."""
        if self.similarity_model:
            try:
                # Encode both texts
                embeddings = self.similarity_model.encode([sentence, source_text])
                # Calculate cosine similarity
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
            except Exception as e:
                logger.warning(f"Similarity calculation failed: {e}")
                return self._calculate_similarity_fallback(sentence, source_text)
        else:
            return self._calculate_similarity_fallback(sentence, source_text)
    
    def _extract_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """Extract sentences with their positions in the text."""
        # Simple sentence splitting - can be enhanced with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        result = []
        current_pos = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                start_pos = text.find(sentence, current_pos)
                end_pos = start_pos + len(sentence)
                result.append((sentence, start_pos, end_pos))
                current_pos = end_pos
        
        return result
    
    def _identify_claims(self, sentence: str) -> ClaimType:
        """Identify the type of claim in a sentence."""
        sentence_lower = sentence.lower()
        
        # Uncertainty indicators
        uncertainty_words = [
            "might", "could", "possibly", "perhaps", "maybe", "seems", "appears",
            "suggests", "indicates", "according to", "reported", "claimed"
        ]
        
        # Opinion indicators
        opinion_words = [
            "think", "believe", "feel", "opinion", "view", "perspective",
            "best", "worst", "great", "terrible", "amazing", "awful"
        ]
        
        # Check for uncertainty
        if any(word in sentence_lower for word in uncertainty_words):
            return ClaimType.UNCERTAIN
        
        # Check for opinions
        if any(word in sentence_lower for word in opinion_words):
            return ClaimType.OPINION
        
        # Default to factual
        return ClaimType.FACTUAL
    
    async def align_sentences_with_sources(
        self, 
        text: str, 
        sources: List[SearchResult],
        min_confidence: float = 0.3
    ) -> List[Citation]:
        """Align sentences in text with relevant sources."""
        citations = []
        sentences = self._extract_sentences(text)
        
        for sentence, start_pos, end_pos in sentences:
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
            
            best_source = None
            best_similarity = 0.0
            claim_type = self._identify_claims(sentence)
            
            # Find best matching source
            for source in sources:
                # Combine title and snippet for comparison
                source_text = f"{source.title} {source.snippet}"
                similarity = await self._calculate_similarity(sentence, source_text)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_source = source
            
            # Create citation if similarity is above threshold
            if best_source and best_similarity >= min_confidence:
                citation = Citation(
                    marker=f"[{len(citations) + 1}]",
                    source=best_source,
                    confidence=best_similarity,
                    sentence_start=start_pos,
                    sentence_end=end_pos,
                    claim_type=claim_type.value
                )
                citations.append(citation)
            
            # Add uncertainty flag for unverified factual claims
            elif claim_type == ClaimType.FACTUAL:
                # This is a factual claim without source support
                pass
        
        return citations
    
    def insert_citation_markers(self, text: str, citations: List[Citation]) -> str:
        """Insert citation markers into the text."""
        # Sort citations by position (reverse order to maintain indices)
        sorted_citations = sorted(citations, key=lambda x: x.sentence_end, reverse=True)
        
        result = text
        for citation in sorted_citations:
            # Insert marker at the end of the sentence
            result = (
                result[:citation.sentence_end] + 
                f" {citation.marker}" + 
                result[citation.sentence_end:]
            )
        
        return result
    
    def generate_bibliography(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """Generate numbered bibliography from citations."""
        bibliography = []
        seen_sources = set()
        
        for citation in citations:
            source_id = citation.source.url  # Use URL as unique identifier
            
            if source_id not in seen_sources:
                seen_sources.add(source_id)
                
                entry = {
                    "number": len(bibliography) + 1,
                    "marker": citation.marker,
                    "title": citation.source.title,
                    "url": citation.source.url,
                    "domain": citation.source.domain,
                    "provider": citation.source.provider.value,
                    "snippet": citation.source.snippet[:200] + "..." if len(citation.source.snippet) > 200 else citation.source.snippet,
                    "metadata": citation.source.metadata,
                    "confidence": citation.confidence
                }
                bibliography.append(entry)
        
        return bibliography
    
    def detect_uncertainty(self, text: str, citations: List[Citation]) -> List[str]:
        """Detect uncertain or unverified claims."""
        uncertainty_flags = []
        sentences = self._extract_sentences(text)
        
        for sentence, start_pos, end_pos in sentences:
            # Check if this sentence has a citation
            has_citation = any(
                c.sentence_start <= start_pos and c.sentence_end >= end_pos
                for c in citations
            )
            
            claim_type = self._identify_claims(sentence)
            
            # Flag unverified factual claims
            if claim_type == ClaimType.FACTUAL and not has_citation:
                uncertainty_flags.append(
                    f"Unverified claim: '{sentence[:50]}...' - could not find supporting source"
                )
            
            # Flag uncertain claims
            elif claim_type == ClaimType.UNCERTAIN:
                uncertainty_flags.append(
                    f"Uncertain claim: '{sentence[:50]}...' - marked as uncertain"
                )
        
        return uncertainty_flags
    
    def calculate_overall_confidence(self, citations: List[Citation]) -> float:
        """Calculate overall confidence score for the text."""
        if not citations:
            return 0.0
        
        # Weight by confidence and claim type
        total_weight = 0.0
        weighted_sum = 0.0
        
        for citation in citations:
            # Weight factual claims more heavily
            if citation.claim_type == "factual":
                weight = 1.0
            elif citation.claim_type == "opinion":
                weight = 0.5
            else:  # uncertain
                weight = 0.3
            
            weighted_sum += citation.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def fact_check_text(
        self, 
        text: str, 
        sources: List[SearchResult],
        min_confidence: float = 0.3
    ) -> FactCheckResult:
        """Perform comprehensive fact-checking on text."""
        try:
            # Align sentences with sources
            citations = await self.align_sentences_with_sources(text, sources, min_confidence)
            
            # Insert citation markers
            cited_text = self.insert_citation_markers(text, citations)
            
            # Generate bibliography
            bibliography = self.generate_bibliography(citations)
            
            # Detect uncertainty
            uncertainty_flags = self.detect_uncertainty(text, citations)
            
            # Calculate overall confidence
            overall_confidence = self.calculate_overall_confidence(citations)
            
            return FactCheckResult(
                text=cited_text,
                citations=citations,
                bibliography=bibliography,
                uncertainty_flags=uncertainty_flags,
                overall_confidence=overall_confidence
            )
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            # Return original text with empty citations
            return FactCheckResult(
                text=text,
                citations=[],
                bibliography=[],
                uncertainty_flags=[f"Fact-checking error: {str(e)}"],
                overall_confidence=0.0
            )


# Global citations manager instance
_citations_manager = None

def get_citations_manager() -> CitationsManager:
    """Get the global citations manager instance."""
    global _citations_manager
    if _citations_manager is None:
        _citations_manager = CitationsManager()
    return _citations_manager


async def fact_check_response(
    text: str, 
    sources: List[SearchResult],
    min_confidence: float = 0.3
) -> FactCheckResult:
    """Convenience function for fact-checking responses."""
    manager = get_citations_manager()
    return await manager.fact_check_text(text, sources, min_confidence)
