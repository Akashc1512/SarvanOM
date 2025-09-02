#!/usr/bin/env python3
"""
Citations Service - Phase C2 Implementation

This service implements sentence-level citation alignment and bibliography generation:
- Sentence-to-passage alignment using cosine similarity
- Inline citation markers with confidence scores
- Bibliography generation with source metadata
- Disagreement detection and confidence flags
- Export support for Markdown and other formats

Key Features:
- Intelligent claim extraction and source mapping
- Confidence scoring based on source agreement
- Disagreement detection when sources conflict
- Bibliography with proper formatting
- Export-ready citation markers
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

@dataclass
class Claim:
    """A claim or statement that needs citation."""
    text: str
    start_pos: int
    end_pos: int
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    disagreement_detected: bool = False
    disagreement_reason: Optional[str] = None
    
    @property
    def normalized_text(self) -> str:
        """Normalize text for similarity comparison."""
        return re.sub(r'[^\w\s]', '', self.text.lower()).strip()
    
    @property
    def claim_hash(self) -> str:
        """Generate hash for claim identification."""
        return hashlib.md5(self.normalized_text.encode()).hexdigest()

@dataclass
class Citation:
    """A citation linking a claim to a source."""
    claim_text: str
    source_url: str
    source_title: str
    source_provider: str
    confidence: float
    snippet: str
    timestamp: datetime
    marker: str = ""  # e.g., "[1]", "[2]"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "claim_text": self.claim_text,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "source_provider": self.source_provider,
            "confidence": self.confidence,
            "snippet": self.snippet,
            "timestamp": self.timestamp.isoformat(),
            "marker": self.marker
        }

@dataclass
class Bibliography:
    """Complete bibliography with all sources."""
    citations: List[Citation] = field(default_factory=list)
    total_sources: int = 0
    high_confidence_sources: int = 0
    disagreement_count: int = 0
    
    def add_citation(self, citation: Citation):
        """Add a citation to the bibliography."""
        self.citations.append(citation)
        self.total_sources += 1
        if citation.confidence >= 0.8:
            self.high_confidence_sources += 1
    
    def get_by_marker(self, marker: str) -> Optional[Citation]:
        """Get citation by marker."""
        for citation in self.citations:
            if citation.marker == marker:
                return citation
        return None
    
    def to_markdown(self) -> str:
        """Export bibliography to Markdown format."""
        if not self.citations:
            return "No sources cited."
        
        markdown = "## Sources\n\n"
        
        for citation in self.citations:
            markdown += f"{citation.marker} [{citation.source_title}]({citation.source_url})\n"
            markdown += f"   - Provider: {citation.source_provider}\n"
            markdown += f"   - Confidence: {citation.confidence:.2f}\n"
            markdown += f"   - Snippet: {citation.snippet[:100]}...\n\n"
        
        return markdown
    
    def to_bibtex(self) -> str:
        """Export bibliography to BibTeX format."""
        if not self.citations:
            return "% No sources cited."
        
        bibtex = ""
        
        for i, citation in enumerate(self.citations):
            key = f"source{i+1}"
            bibtex += f"@misc{{{key},\n"
            bibtex += f"  title = {{{citation.source_title}}},\n"
            bibtex += f"  url = {{{citation.source_url}}},\n"
            bibtex += f"  author = {{{citation.source_provider}}},\n"
            bibtex += f"  year = {{{citation.timestamp.year}}},\n"
            bibtex += f"  note = {{Confidence: {citation.confidence:.2f}}}\n"
            bibtex += "}\n\n"
        
        return bibtex

class ClaimExtractor:
    """Extract claims from text that need citation."""
    
    def __init__(self):
        """Initialize the claim extractor."""
        # Patterns for identifying claims that need citation
        self.claim_patterns = [
            r'([A-Z][^.!?]*\s+(?:is|are|was|were|has|have|had|can|could|will|would|should|may|might)\s+[^.!?]*[.!?])',
            r'([A-Z][^.!?]*\s+(?:studies|research|data|evidence|analysis|report|survey|study|paper|article)\s+[^.!?]*[.!?])',
            r'([A-Z][^.!?]*\s+(?:according to|based on|as reported by|as stated in|as mentioned in)\s+[^.!?]*[.!?])',
            r'([A-Z][^.!?]*\s+(?:shows|indicates|suggests|implies|demonstrates|reveals|confirms|proves)\s+[^.!?]*[.!?])',
        ]
        
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.claim_patterns]
    
    def extract_claims(self, text: str) -> List[Claim]:
        """Extract claims from text that need citation."""
        claims = []
        
        for pattern in self.compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                claim_text = match.group(1).strip()
                
                # Skip very short claims
                if len(claim_text) < 20:
                    continue
                
                # Skip claims that are already questions
                if claim_text.endswith('?'):
                    continue
                
                claim = Claim(
                    text=claim_text,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.5  # Default confidence
                )
                
                claims.append(claim)
        
        # Remove overlapping claims
        claims = self._remove_overlapping_claims(claims)
        
        logger.info(f"Extracted {len(claims)} claims from text")
        return claims
    
    def _remove_overlapping_claims(self, claims: List[Claim]) -> List[Claim]:
        """Remove claims that overlap significantly."""
        if len(claims) <= 1:
            return claims
        
        # Sort by start position
        claims.sort(key=lambda x: x.start_pos)
        
        filtered_claims = [claims[0]]
        
        for claim in claims[1:]:
            # Check if this claim overlaps significantly with the last one
            last_claim = filtered_claims[-1]
            overlap = min(claim.end_pos, last_claim.end_pos) - max(claim.start_pos, last_claim.start_pos)
            
            if overlap <= 0:
                # No overlap, add this claim
                filtered_claims.append(claim)
            elif overlap < len(claim.text) * 0.5:
                # Minimal overlap, add this claim
                filtered_claims.append(claim)
            # Otherwise, skip this claim (significant overlap)
        
        return filtered_claims

class SourceAligner:
    """Align claims with sources using similarity matching."""
    
    def __init__(self):
        """Initialize the source aligner."""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def align_claims_to_sources(self, claims: List[Claim], sources: List[Dict[str, Any]]) -> List[Citation]:
        """Align claims with sources using similarity matching."""
        if not claims or not sources:
            return []
        
        # Prepare source texts for vectorization
        source_texts = []
        for source in sources:
            # Combine title and snippet for better matching
            source_text = f"{source.get('title', '')} {source.get('snippet', '')}"
            source_texts.append(source_text)
        
        # Vectorize source texts
        try:
            source_vectors = self.vectorizer.fit_transform(source_texts)
        except Exception as e:
            logger.warning(f"Vectorization failed: {e}, using fallback matching")
            return self._fallback_alignment(claims, sources)
        
        citations = []
        
        for claim in claims:
            # Vectorize claim text
            claim_vector = self.vectorizer.transform([claim.text])
            
            # Calculate similarities
            similarities = cosine_similarity(claim_vector, source_vectors).flatten()
            
            # Find best matching sources
            best_matches = self._find_best_matches(claim, sources, similarities)
            
            # Create citations for best matches
            for i, (source, similarity) in enumerate(best_matches):
                citation = Citation(
                    claim_text=claim.text,
                    source_url=source.get('url', ''),
                    source_title=source.get('title', ''),
                    source_provider=source.get('provider', ''),
                    confidence=float(similarity),
                    snippet=source.get('snippet', ''),
                    timestamp=datetime.now(),
                    marker=f"[{len(citations) + 1}]"
                )
                
                citations.append(citation)
                
                # Add source to claim
                claim.sources.append(source.get('url', ''))
        
        return citations
    
    def _find_best_matches(self, claim: Claim, sources: List[Dict[str, Any]], similarities: np.ndarray) -> List[Tuple[Dict[str, Any], float]]:
        """Find the best matching sources for a claim."""
        # Get indices of top matches
        top_indices = np.argsort(similarities)[::-1][:3]  # Top 3 matches
        
        best_matches = []
        for idx in top_indices:
            similarity = similarities[idx]
            if similarity > 0.1:  # Minimum similarity threshold
                best_matches.append((sources[idx], similarity))
        
        return best_matches
    
    def _fallback_alignment(self, claims: List[Claim], sources: List[Dict[str, Any]]) -> List[Citation]:
        """Fallback alignment when vectorization fails."""
        citations = []
        
        for i, claim in enumerate(claims):
            # Simple keyword matching as fallback
            claim_words = set(claim.text.lower().split())
            
            best_source = None
            best_score = 0
            
            for source in sources:
                source_text = f"{source.get('title', '')} {source.get('snippet', '')}".lower()
                source_words = set(source_text.split())
                
                # Calculate word overlap
                overlap = len(claim_words.intersection(source_words))
                score = overlap / len(claim_words) if claim_words else 0
                
                if score > best_score:
                    best_score = score
                    best_source = source
            
            if best_source and best_score > 0.1:
                citation = Citation(
                    claim_text=claim.text,
                    source_url=best_source.get('url', ''),
                    source_title=best_source.get('title', ''),
                    source_provider=best_source.get('provider', ''),
                    confidence=best_score,
                    snippet=best_source.get('snippet', ''),
                    timestamp=datetime.now(),
                    marker=f"[{len(citations) + 1}]"
                )
                
                citations.append(citation)
                claim.sources.append(best_source.get('url', ''))
        
        return citations

class DisagreementDetector:
    """Detect disagreements between sources for the same claim."""
    
    def __init__(self):
        """Initialize the disagreement detector."""
        self.confidence_threshold = 0.7
        self.disagreement_threshold = 0.3
    
    def detect_disagreements(self, claims: List[Claim], citations: List[Citation]) -> List[Claim]:
        """Detect claims with conflicting sources."""
        for claim in claims:
            claim_sources = [c for c in citations if c.claim_text == claim.text]
            
            if len(claim_sources) < 2:
                continue
            
            # Check for disagreements
            disagreements = self._analyze_source_agreement(claim_sources)
            
            if disagreements:
                claim.disagreement_detected = True
                claim.disagreement_reason = disagreements
                claim.confidence = min(c.confidence for c in claim_sources)
                
                logger.info(f"Disagreement detected in claim: {claim.text[:50]}...")
        
        return claims
    
    def _analyze_source_agreement(self, sources: List[Citation]) -> Optional[str]:
        """Analyze agreement between sources."""
        if len(sources) < 2:
            return None
        
        # Check confidence variance
        confidences = [s.confidence for s in sources]
        variance = np.var(confidences)
        
        if variance > self.disagreement_threshold:
            return f"High confidence variance ({variance:.2f}) between sources"
        
        # Check for conflicting information (simplified)
        # In a real implementation, this would use more sophisticated NLP
        return None

class CitationsService:
    """Main service for citation management."""
    
    def __init__(self):
        """Initialize the citations service."""
        self.claim_extractor = ClaimExtractor()
        self.source_aligner = SourceAligner()
        self.disagreement_detector = DisagreementDetector()
    
    async def process_text_with_citations(
        self, 
        text: str, 
        sources: List[Dict[str, Any]]
    ) -> Tuple[str, Bibliography]:
        """
        Process text and add inline citations.
        
        Args:
            text: The text to process
            sources: List of source dictionaries with url, title, snippet, provider
            
        Returns:
            Tuple of (annotated_text, bibliography)
        """
        # Extract claims
        claims = self.claim_extractor.extract_claims(text)
        
        if not claims:
            logger.info("No claims requiring citation found in text")
            return text, Bibliography()
        
        # Align claims with sources
        citations = self.source_aligner.align_claims_to_sources(claims, sources)
        
        if not citations:
            logger.warning("No sources could be aligned with claims")
            return text, Bibliography()
        
        # Detect disagreements
        claims = self.disagreement_detector.detect_disagreements(claims, citations)
        
        # Create bibliography
        bibliography = Bibliography()
        for citation in citations:
            bibliography.add_citation(citation)
        
        # Add citation markers to text
        annotated_text = self._add_citation_markers(text, claims, citations)
        
        # Add disagreement warnings
        annotated_text = self._add_disagreement_warnings(annotated_text, claims)
        
        logger.info(f"Processed text with {len(citations)} citations, {bibliography.disagreement_count} disagreements")
        
        return annotated_text, bibliography
    
    def _add_citation_markers(self, text: str, claims: List[Claim], citations: List[Citation]) -> str:
        """Add citation markers to the text."""
        # Sort claims by position (reverse order to avoid position shifting)
        sorted_claims = sorted(claims, key=lambda x: x.end_pos, reverse=True)
        
        annotated_text = text
        
        for claim in sorted_claims:
            # Find citations for this claim
            claim_citations = [c for c in citations if c.claim_text == claim.text]
            
            if not claim_citations:
                continue
            
            # Create citation marker
            markers = [c.marker for c in claim_citations]
            marker_text = " ".join(markers)
            
            # Insert marker after the claim
            annotated_text = (
                annotated_text[:claim.end_pos] + 
                f" {marker_text}" + 
                annotated_text[claim.end_pos:]
            )
        
        return annotated_text
    
    def _add_disagreement_warnings(self, text: str, claims: List[Claim]) -> str:
        """Add disagreement warnings to the text."""
        # Find claims with disagreements
        disagreed_claims = [c for c in claims if c.disagreement_detected]
        
        if not disagreed_claims:
            return text
        
        # Add warning at the end
        warning_text = "\n\n⚠️ **Note**: Some claims have conflicting sources. Please verify information independently."
        text += warning_text
        
        return text
    
    def export_citations(self, bibliography: Bibliography, format: str = "markdown") -> str:
        """Export citations in various formats."""
        if format.lower() == "markdown":
            return bibliography.to_markdown()
        elif format.lower() == "bibtex":
            return bibliography.to_bibtex()
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global service instance
_citations_service: Optional[CitationsService] = None

def get_citations_service() -> CitationsService:
    """Get or create global citations service."""
    global _citations_service
    
    if _citations_service is None:
        _citations_service = CitationsService()
    
    return _citations_service
