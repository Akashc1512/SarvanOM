"""
Advanced fact-checking agent that verifies claims against retrieved documents.
Enhanced with temporal validation and source authenticity checking.
"""

import asyncio
import logging
import time
import os
import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

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
from shared.core.agents.data_models import FactCheckResult, VerifiedFactModel, CitationModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
DEFAULT_TOKEN_BUDGET = int(os.getenv("DEFAULT_TOKEN_BUDGET", "1000"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "knowledge_base")
MAX_SOURCE_AGE_DAYS = int(os.getenv("MAX_SOURCE_AGE_DAYS", "365"))  # Default 1 year
MIN_SOURCE_CONFIDENCE = float(os.getenv("MIN_SOURCE_CONFIDENCE", "0.6"))


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
class VerificationResult:
    """Represents the result of answer verification."""
    
    summary: str
    verified_sentences: List[Dict[str, Any]]
    unsupported_sentences: List[Dict[str, Any]]
    total_sentences: int
    verification_confidence: float
    verification_method: str
    outdated_sentences: List[Dict[str, Any]] = None  # New field for outdated sentences
    temporal_validation: Dict[str, Any] = None
    source_authenticity: Dict[str, Any] = None
    source_freshness: Dict[str, Any] = None  # New field for freshness validation
    revised_sentences: List[Dict[str, Any]] = None # New field for revised sentences


@dataclass
class TemporalValidation:
    """Represents temporal validation results."""
    
    query_timestamp: datetime
    latest_source_date: Optional[datetime]
    source_age_days: Optional[int]
    is_current: bool
    temporal_confidence: float
    outdated_warning: Optional[str] = None


@dataclass
class SourceAuthenticity:
    """Represents source authenticity validation."""
    
    total_sources: int
    authentic_sources: int
    high_confidence_sources: int
    average_confidence: float
    authenticity_score: float
    reliability_indicators: List[str] = None


@dataclass
class SourceFreshness:
    """Represents source freshness validation results."""
    
    query_timestamp: datetime
    max_freshness_days: int = 180  # 6 months default
    outdated_sources_count: int = 0
    fresh_sources_count: int = 0
    oldest_source_date: Optional[datetime] = None
    newest_source_date: Optional[datetime] = None
    freshness_warning: Optional[str] = None
    freshness_score: float = 1.0


class FactCheckAgent(BaseAgent):
    """
    Enhanced FactCheckAgent that verifies claims against retrieved documents
    with temporal validation and source authenticity checking.
    """

    def __init__(self):
        """Initialize the fact-checking agent."""
        super().__init__(agent_id="factcheck_agent", agent_type=AgentType.FACT_CHECK)
        self.manual_review_callback: Optional[Callable] = None
        self._embedding_model = None
        self.max_source_age_days = MAX_SOURCE_AGE_DAYS
        self.min_source_confidence = MIN_SOURCE_CONFIDENCE
        logger.info("✅ Enhanced FactCheckAgent initialized successfully")

    def set_manual_review_callback(self, callback: Callable):
        """Set callback for manual review of contested claims."""
        self.manual_review_callback = callback

    async def verify_answer_with_temporal_validation(
        self, 
        answer_text: str, 
        source_docs: List[Dict[str, Any]], 
        query_timestamp: Optional[datetime] = None
    ) -> VerificationResult:
        """
        Verify answer with enhanced temporal validation and source authenticity checking.
        
        Args:
            answer_text: The LLM-generated answer to verify
            source_docs: List of source documents to check against
            query_timestamp: Timestamp when the query was made (defaults to now)
            
        Returns:
            VerificationResult with temporal validation and authenticity info
        """
        start_time = time.time()
        
        if query_timestamp is None:
            query_timestamp = datetime.now()
        
        try:
            # Perform temporal validation
            temporal_validation = await self._validate_temporal_relevance(
                source_docs, query_timestamp
            )
            
            # Perform source authenticity validation
            source_authenticity = await self._validate_source_authenticity(source_docs)
            
            # Perform source freshness validation
            source_freshness = await self._validate_source_freshness(source_docs, query_timestamp)
            
            # Filter sources based on temporal and authenticity criteria
            filtered_sources = await self._filter_sources_by_criteria(
                source_docs, temporal_validation, source_authenticity
            )
            
            # Perform standard verification with filtered sources
            base_result = await self.verify_answer(answer_text, filtered_sources)
            
            # Enhance result with temporal and authenticity information
            enhanced_result = VerificationResult(
                summary=base_result.summary,
                verified_sentences=base_result.verified_sentences,
                unsupported_sentences=base_result.unsupported_sentences,
                total_sentences=base_result.total_sentences,
                verification_confidence=base_result.verification_confidence,
                verification_method=base_result.verification_method,
                temporal_validation=temporal_validation.__dict__,
                source_authenticity=source_authenticity.__dict__,
                source_freshness=source_freshness.__dict__
            )
            
            # Add temporal warnings if needed
            if not temporal_validation.is_current:
                enhanced_result.summary += f" (⚠️ Sources may be outdated: {temporal_validation.outdated_warning})"
            
            # Add authenticity warnings if needed
            if source_authenticity.authenticity_score < 0.7:
                enhanced_result.summary += f" (⚠️ Source authenticity concerns: {source_authenticity.authenticity_score:.2f})"
            
            # Add freshness warnings if needed
            if source_freshness.freshness_warning:
                enhanced_result.summary += f" (⚠️ Source freshness concerns: {source_freshness.freshness_warning})"
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhanced answer verification failed: {str(e)}")
            return VerificationResult(
                summary="Verification failed due to error",
                verified_sentences=[],
                unsupported_sentences=[],
                total_sentences=0,
                verification_confidence=0.0,
                verification_method="error",
                temporal_validation={"error": str(e)},
                source_authenticity={"error": str(e)},
                source_freshness={"error": str(e)}
            )

    async def verify_answer_with_vector_search(
        self, 
        answer_text: str, 
        source_docs: List[Dict[str, Any]], 
        query_timestamp: Optional[datetime] = None
    ) -> VerificationResult:
        """
        Verify answer by iterating over each sentence/fact and performing vector search verification.
        If a fact is unsupported, either mark it or call the LLM to revise the answer.
        
        Args:
            answer_text: The LLM-generated answer to verify
            source_docs: List of source documents to check against
            query_timestamp: Timestamp when the query was made (defaults to now)
            
        Returns:
            VerificationResult with detailed sentence-by-sentence verification
        """
        start_time = time.time()
        
        if query_timestamp is None:
            query_timestamp = datetime.now()
        
        try:
            # Split answer into sentences
            sentences = self._split_into_sentences(answer_text)
            
            verified_sentences = []
            unsupported_sentences = []
            revised_sentences = []
            
            # Initialize vector search engine
            search_engine = await self._get_vector_search_engine()
            
            for i, sentence in enumerate(sentences):
                if len(sentence.strip()) < 10:  # Skip very short sentences
                    continue
                    
                # Check if sentence is factual
                if not self._is_factual_statement(sentence):
                    continue
                
                # Perform vector search verification for this sentence
                verification = await self._verify_sentence_with_vector_search(
                    sentence, search_engine, source_docs
                )
                
                if verification["is_supported"]:
                    verified_sentences.append({
                        "sentence": sentence,
                        "confidence": verification["confidence"],
                        "evidence": verification["evidence"],
                        "source_docs": verification["source_docs"],
                        "verification_method": "vector_search",
                        "sentence_index": i
                    })
                else:
                    # Try to revise the unsupported sentence using LLM
                    revised_sentence = await self._revise_unsupported_sentence(
                        sentence, verification["reason"], source_docs
                    )
                    
                    if revised_sentence and revised_sentence != sentence:
                        # Verify the revised sentence
                        revised_verification = await self._verify_sentence_with_vector_search(
                            revised_sentence, search_engine, source_docs
                        )
                        
                        if revised_verification["is_supported"]:
                            revised_sentences.append({
                                "original_sentence": sentence,
                                "revised_sentence": revised_sentence,
                                "confidence": revised_verification["confidence"],
                                "evidence": revised_verification["evidence"],
                                "source_docs": revised_verification["source_docs"],
                                "verification_method": "vector_search_with_revision",
                                "sentence_index": i,
                                "revision_reason": verification["reason"]
                            })
                        else:
                            unsupported_sentences.append({
                                "sentence": sentence,
                                "confidence": verification["confidence"],
                                "reason": verification["reason"],
                                "revision_attempted": True,
                                "revised_sentence": revised_sentence,
                                "sentence_index": i
                            })
                    else:
                        unsupported_sentences.append({
                            "sentence": sentence,
                            "confidence": verification["confidence"],
                            "reason": verification["reason"],
                            "revision_attempted": False,
                            "sentence_index": i
                        })
            
            # Calculate summary
            total_factual = len(verified_sentences) + len(unsupported_sentences) + len(revised_sentences)
            verified_count = len(verified_sentences)
            revised_count = len(revised_sentences)
            
            if total_factual == 0:
                summary = "No factual statements found to verify"
                verification_confidence = 1.0
            else:
                summary = f"{verified_count}/{total_factual} statements verified"
                if revised_count > 0:
                    summary += f" ({revised_count} revised)"
                verification_confidence = (verified_count + revised_count) / total_factual
            
            processing_time = time.time() - start_time
            
            return VerificationResult(
                summary=summary,
                verified_sentences=verified_sentences,
                unsupported_sentences=unsupported_sentences,
                total_sentences=total_factual,
                verification_confidence=verification_confidence,
                verification_method="vector_search_with_revision",
                revised_sentences=revised_sentences
            )
            
        except Exception as e:
            logger.error(f"Vector search verification failed: {str(e)}")
            return VerificationResult(
                summary="Verification failed due to error",
                verified_sentences=[],
                unsupported_sentences=[],
                total_sentences=0,
                verification_confidence=0.0,
                verification_method="error"
            )

    async def _validate_temporal_relevance(
        self, source_docs: List[Dict[str, Any]], query_timestamp: datetime
    ) -> TemporalValidation:
        """
        Validate temporal relevance of sources.
        
        Args:
            source_docs: Source documents to validate
            query_timestamp: When the query was made
            
        Returns:
            TemporalValidation result
        """
        if not source_docs:
            return TemporalValidation(
                query_timestamp=query_timestamp,
                latest_source_date=None,
                source_age_days=None,
                is_current=False,
                temporal_confidence=0.0,
                outdated_warning="No sources available"
            )
        
        # Extract dates from sources
        source_dates = []
        for doc in source_docs:
            date_str = doc.get("timestamp") or doc.get("date") or doc.get("created_at")
            if date_str:
                try:
                    # Try multiple date formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            source_date = datetime.strptime(date_str, fmt)
                            source_dates.append(source_date)
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.warning(f"Could not parse date '{date_str}': {e}")
        
        if not source_dates:
            return TemporalValidation(
                query_timestamp=query_timestamp,
                latest_source_date=None,
                source_age_days=None,
                is_current=False,
                temporal_confidence=0.3,  # Low confidence without dates
                outdated_warning="No source dates available"
            )
        
        # Find latest source date
        latest_source_date = max(source_dates)
        source_age_days = (query_timestamp - latest_source_date).days
        
        # Determine if sources are current
        is_current = source_age_days <= self.max_source_age_days
        
        # Calculate temporal confidence
        if source_age_days <= 30:
            temporal_confidence = 1.0
        elif source_age_days <= 90:
            temporal_confidence = 0.9
        elif source_age_days <= 180:
            temporal_confidence = 0.7
        elif source_age_days <= 365:
            temporal_confidence = 0.5
        else:
            temporal_confidence = 0.3
        
        # Generate warning for outdated sources
        outdated_warning = None
        if not is_current:
            if source_age_days > 365:
                outdated_warning = f"Sources are over {source_age_days//365} year(s) old"
            else:
                outdated_warning = f"Sources are {source_age_days} days old"
        
        return TemporalValidation(
            query_timestamp=query_timestamp,
            latest_source_date=latest_source_date,
            source_age_days=source_age_days,
            is_current=is_current,
            temporal_confidence=temporal_confidence,
            outdated_warning=outdated_warning
        )

    async def _validate_source_authenticity(self, source_docs: List[Dict[str, Any]]) -> SourceAuthenticity:
        """
        Validate authenticity and reliability of sources.
        
        Args:
            source_docs: Source documents to validate
            
        Returns:
            SourceAuthenticity result
        """
        if not source_docs:
            return SourceAuthenticity(
                total_sources=0,
                authentic_sources=0,
                high_confidence_sources=0,
                average_confidence=0.0,
                authenticity_score=0.0,
                reliability_indicators=[]
            )
        
        total_sources = len(source_docs)
        authentic_sources = 0
        high_confidence_sources = 0
        reliability_indicators = []
        confidence_scores = []
        
        # Define reliable domain patterns
        reliable_domains = [
            "wikipedia.org", "gov", "edu", "ac.uk", "org",
            "researchgate.net", "arxiv.org", "scholar.google.com",
            "ieee.org", "acm.org", "springer.com", "sciencedirect.com"
        ]
        
        for doc in source_docs:
            source_url = doc.get("url", "").lower()
            source_domain = doc.get("domain", "").lower()
            score = doc.get("score", 0.0)
            
            # Check if source is from reliable domain
            is_reliable_domain = any(domain in source_url or domain in source_domain 
                                   for domain in reliable_domains)
            
            # Check for authenticity indicators
            has_author = "author" in doc or "author" in str(doc.get("metadata", {}))
            has_citations = "citations" in doc or "references" in doc
            has_peer_review = "peer_review" in str(doc.get("metadata", {})).lower()
            
            # Calculate source confidence
            source_confidence = score
            if is_reliable_domain:
                source_confidence += 0.2
            if has_author:
                source_confidence += 0.1
            if has_citations:
                source_confidence += 0.1
            if has_peer_review:
                source_confidence += 0.2
            
            source_confidence = min(1.0, source_confidence)
            confidence_scores.append(source_confidence)
            
            # Count authentic sources
            if source_confidence >= self.min_source_confidence:
                authentic_sources += 1
            
            # Count high confidence sources
            if source_confidence >= 0.8:
                high_confidence_sources += 1
            
            # Collect reliability indicators
            if is_reliable_domain:
                reliability_indicators.append("reliable_domain")
            if has_author:
                reliability_indicators.append("has_author")
            if has_citations:
                reliability_indicators.append("has_citations")
            if has_peer_review:
                reliability_indicators.append("peer_reviewed")
        
        # Calculate authenticity score
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        authenticity_score = (authentic_sources / total_sources) * average_confidence if total_sources > 0 else 0.0
        
        return SourceAuthenticity(
            total_sources=total_sources,
            authentic_sources=authentic_sources,
            high_confidence_sources=high_confidence_sources,
            average_confidence=average_confidence,
            authenticity_score=authenticity_score,
            reliability_indicators=list(set(reliability_indicators))
        )

    async def _validate_source_freshness(
        self, source_docs: List[Dict[str, Any]], query_timestamp: datetime
    ) -> SourceFreshness:
        """
        Validate the freshness of source documents based on published_date.
        
        Args:
            source_docs: List of source documents
            query_timestamp: Timestamp of the query
            
        Returns:
            SourceFreshness object with freshness validation results
        """
        max_freshness_days = 180  # 6 months default
        outdated_sources_count = 0
        fresh_sources_count = 0
        source_dates = []
        
        for doc in source_docs:
            # Try to extract published_date from various possible fields
            published_date = None
            
            # Check for published_date field first
            if "published_date" in doc:
                published_date = self._parse_date(doc["published_date"])
            
            # Fallback to timestamp field
            elif "timestamp" in doc:
                published_date = self._parse_date(doc["timestamp"])
            
            # Fallback to date field
            elif "date" in doc:
                published_date = self._parse_date(doc["date"])
            
            # Fallback to created_at field
            elif "created_at" in doc:
                published_date = self._parse_date(doc["created_at"])
            
            if published_date:
                source_dates.append(published_date)
                age_days = (query_timestamp - published_date).days
                
                if age_days > max_freshness_days:
                    outdated_sources_count += 1
                    logger.info(f"Outdated source found: {doc.get('doc_id', 'unknown')} - {age_days} days old")
                else:
                    fresh_sources_count += 1
                    logger.info(f"Fresh source found: {doc.get('doc_id', 'unknown')} - {age_days} days old")
            else:
                # If no date found, count as outdated for safety
                outdated_sources_count += 1
                logger.warning(f"No published_date found for source: {doc.get('doc_id', 'unknown')}")
        
        # Calculate freshness metrics
        total_sources = len(source_docs)
        oldest_source_date = min(source_dates) if source_dates else None
        newest_source_date = max(source_dates) if source_dates else None
        
        # Calculate freshness score
        if total_sources > 0:
            freshness_score = fresh_sources_count / total_sources
        else:
            freshness_score = 1.0  # No sources means no freshness concerns
        
        # Generate warning if needed
        freshness_warning = None
        if outdated_sources_count > 0:
            if fresh_sources_count == 0:
                freshness_warning = f"All sources are older than {max_freshness_days} days"
            else:
                freshness_warning = f"{outdated_sources_count} out of {total_sources} sources are older than {max_freshness_days} days"
        
        return SourceFreshness(
            query_timestamp=query_timestamp,
            max_freshness_days=max_freshness_days,
            outdated_sources_count=outdated_sources_count,
            fresh_sources_count=fresh_sources_count,
            oldest_source_date=oldest_source_date,
            newest_source_date=newest_source_date,
            freshness_warning=freshness_warning,
            freshness_score=freshness_score
        )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            "%Y-%m-%dT%H:%M:%SZ",  # ISO format with Z
            "%Y-%m-%dT%H:%M:%S",   # ISO format without Z
            "%Y-%m-%d %H:%M:%S",   # Space separated
            "%Y-%m-%d",            # Date only
            "%d/%m/%Y",            # DD/MM/YYYY
            "%m/%d/%Y",            # MM/DD/YYYY
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO with milliseconds
            "%Y-%m-%dT%H:%M:%S.%f",   # ISO with milliseconds without Z
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None

    async def _filter_sources_by_criteria(
        self, 
        source_docs: List[Dict[str, Any]], 
        temporal_validation: TemporalValidation,
        source_authenticity: SourceAuthenticity
    ) -> List[Dict[str, Any]]:
        """
        Filter sources based on temporal and authenticity criteria.
        
        Args:
            source_docs: Original source documents
            temporal_validation: Temporal validation results
            source_authenticity: Source authenticity results
            
        Returns:
            Filtered source documents
        """
        if not source_docs:
            return []
        
        filtered_sources = []
        
        for doc in source_docs:
            # Check temporal relevance
            date_str = doc.get("timestamp") or doc.get("date") or doc.get("created_at")
            is_temporally_relevant = True
            
            if date_str and temporal_validation.latest_source_date:
                try:
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            doc_date = datetime.strptime(date_str, fmt)
                            # Prefer recent sources, but don't exclude older ones completely
                            if (temporal_validation.query_timestamp - doc_date).days > self.max_source_age_days * 2:
                                is_temporally_relevant = False
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass  # Keep source if date parsing fails
            
            # Check authenticity
            score = doc.get("score", 0.0)
            is_authentic = score >= self.min_source_confidence
            
            # Include source if it meets basic criteria
            if is_temporally_relevant and is_authentic:
                filtered_sources.append(doc)
            elif is_temporally_relevant:  # Include temporally relevant sources even if lower confidence
                filtered_sources.append(doc)
        
        # If no sources meet strict criteria, include some lower-quality sources
        if not filtered_sources:
            logger.warning("No sources meet strict criteria, including lower-quality sources")
            filtered_sources = source_docs[:3]  # Take top 3 sources
        
        return filtered_sources

    async def verify_answer(self, answer_text: str, source_docs: List[Dict[str, Any]]) -> VerificationResult:
        """
        Verify key statements from LLM answer against retrieved documents.
        Enhanced with source freshness validation.
        
        Args:
            answer_text: The LLM-generated answer to verify
            source_docs: List of source documents to check against
            
        Returns:
            VerificationResult with verification details including freshness validation
        """
        start_time = time.time()
        
        try:
            # Split answer into sentences
            sentences = self._split_into_sentences(answer_text)
            
            verified_sentences = []
            unsupported_sentences = []
            outdated_sentences = []
            
            # Get current timestamp for freshness validation
            query_timestamp = datetime.now()
            
            # Validate source freshness
            source_freshness = await self._validate_source_freshness(source_docs, query_timestamp)
            
            for sentence in sentences:
                if len(sentence.strip()) < 10:  # Skip very short sentences
                    continue
                    
                # Check if sentence is factual
                if not self._is_factual_statement(sentence):
                    continue
                
                # Verify sentence against source documents
                verification = await self._verify_sentence_against_docs(sentence, source_docs)
                
                if verification["is_supported"]:
                    # Check if the supporting sources are outdated
                    is_outdated = self._check_sentence_source_freshness(
                        sentence, verification["source_docs"], source_docs, query_timestamp
                    )
                    
                    if is_outdated:
                        outdated_sentences.append({
                            "sentence": sentence,
                            "confidence": verification["confidence"],
                            "evidence": verification["evidence"],
                            "source_docs": verification["source_docs"],
                            "freshness_status": "outdated",
                            "oldest_source_date": source_freshness.oldest_source_date.isoformat() if source_freshness.oldest_source_date else None
                        })
                    else:
                        verified_sentences.append({
                            "sentence": sentence,
                            "confidence": verification["confidence"],
                            "evidence": verification["evidence"],
                            "source_docs": verification["source_docs"],
                            "freshness_status": "fresh"
                        })
                else:
                    unsupported_sentences.append({
                        "sentence": sentence,
                        "confidence": verification["confidence"],
                        "reason": verification["reason"]
                    })
            
            # Calculate summary
            total_factual = len(verified_sentences) + len(unsupported_sentences) + len(outdated_sentences)
            verified_count = len(verified_sentences)
            outdated_count = len(outdated_sentences)
            
            if total_factual == 0:
                summary = "No factual statements found to verify"
                verification_confidence = 1.0  # No facts to verify
            else:
                summary = f"{verified_count}/{total_factual} statements verified"
                if outdated_count > 0:
                    summary += f" ({outdated_count} outdated)"
                verification_confidence = verified_count / total_factual
            
            processing_time = time.time() - start_time
            
            return VerificationResult(
                summary=summary,
                verified_sentences=verified_sentences,
                unsupported_sentences=unsupported_sentences,
                outdated_sentences=outdated_sentences,
                total_sentences=total_factual,
                verification_confidence=verification_confidence,
                verification_method="embedding_similarity_with_freshness",
                source_freshness=source_freshness.__dict__
            )
            
        except Exception as e:
            logger.error(f"Answer verification failed: {str(e)}")
            return VerificationResult(
                summary="Verification failed due to error",
                verified_sentences=[],
                unsupported_sentences=[],
                outdated_sentences=[],
                total_sentences=0,
                verification_confidence=0.0,
                verification_method="error",
                source_freshness={"error": str(e)}
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

    async def _verify_sentence_against_docs(self, sentence: str, source_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a single sentence against source documents using embedding similarity.
        
        Args:
            sentence: Sentence to verify
            source_docs: Source documents to check against
            
        Returns:
            Verification result dictionary
        """
        if not source_docs:
            return {
                "is_supported": False,
                "confidence": 0.0,
                "evidence": [],
                "source_docs": [],
                "reason": "No source documents available"
            }
        
        try:
            # Get sentence embedding
            sentence_embedding = await self._get_sentence_embedding(sentence)
            
            best_match_score = 0.0
            best_match_content = ""
            best_match_doc_id = ""
            all_evidence = []
            all_source_docs = []
            
            # Check each source document
            for doc in source_docs:
                doc_content = doc.get("content", "")
                doc_id = doc.get("doc_id", "unknown")
                
                if not doc_content:
                    continue
                
                # Split document into chunks for better matching
                doc_chunks = self._split_document_into_chunks(doc_content)
                
                for chunk in doc_chunks:
                    # Get chunk embedding
                    chunk_embedding = await self._get_sentence_embedding(chunk)
                    
                    # Calculate similarity
                    similarity = self._calculate_cosine_similarity(sentence_embedding, chunk_embedding)
                    
                    if similarity > best_match_score:
                        best_match_score = similarity
                        best_match_content = chunk
                        best_match_doc_id = doc_id
                    
                    # Collect evidence if similarity is above threshold
                    if similarity > 0.3:  # Lower threshold for evidence collection
                        all_evidence.append(chunk[:200])  # Limit evidence length
                        all_source_docs.append(doc_id)
            
            # Determine if sentence is supported
            support_threshold = 0.5  # Adjustable threshold
            is_supported = best_match_score >= support_threshold
            
            # Calculate confidence based on similarity and evidence quantity
            confidence = min(1.0, best_match_score + (len(all_evidence) * 0.1))
            
            return {
                "is_supported": is_supported,
                "confidence": confidence,
                "evidence": all_evidence[:3],  # Limit to top 3 pieces of evidence
                "source_docs": list(set(all_source_docs)),  # Remove duplicates
                "reason": f"Best match similarity: {best_match_score:.3f}" if not is_supported else "Supported by evidence"
            }
            
        except Exception as e:
            logger.error(f"Error verifying sentence: {str(e)}")
            return {
                "is_supported": False,
                "confidence": 0.0,
                "evidence": [],
                "source_docs": [],
                "reason": f"Verification error: {str(e)}"
            }

    async def _get_sentence_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a sentence using local HuggingFace model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Lazy load the embedding model
            if self._embedding_model is None:
                await self._load_embedding_model()
            
            # If embedding model failed to load, use fallback
            if self._embedding_model is None:
                return self._fallback_embedding(text)
            
            # Import torch here to avoid import issues
            import torch
            
            # Tokenize and get embeddings
            inputs = self._embedding_tokenizer(
                text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True, 
                padding=True
            )
            
            with torch.no_grad():
                outputs = self._embedding_model(**inputs)
                # Use mean pooling for sentence embedding
                embeddings = outputs.last_hidden_state.mean(dim=1)
                return embeddings[0].numpy().tolist()
                
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Fallback to simple keyword-based approach
            return self._fallback_embedding(text)

    async def _load_embedding_model(self):
        """Load the embedding model lazily."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
            
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            logger.info(f"Loading embedding model: {model_name}")
            
            self._embedding_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._embedding_model = AutoModel.from_pretrained(model_name)
            
            # Set to evaluation mode
            self._embedding_model.eval()
            
            logger.info("✅ Embedding model loaded successfully")
            
        except ImportError:
            logger.warning("Transformers not available, using fallback embedding")
            self._embedding_model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            self._embedding_model = None

    def _fallback_embedding(self, text: str) -> List[float]:
        """
        Fallback embedding method using simple TF-IDF approach.
        
        Args:
            text: Text to embed
            
        Returns:
            Simple embedding vector
        """
        # Simple fallback: create a basic vector based on word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Create a simple frequency-based vector
        word_freq = {}
        for word in words:
            if len(word) > 2:  # Skip very short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Normalize to create a simple embedding
        total_words = sum(word_freq.values())
        if total_words == 0:
            return [0.0] * 100  # Return zero vector
        
        # Create a simple 100-dimensional vector
        embedding = [0.0] * 100
        for i, (word, freq) in enumerate(list(word_freq.items())[:100]):
            embedding[i] = freq / total_words
        
        return embedding

    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        try:
            import numpy as np
            
            # Convert to numpy arrays
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except ImportError:
            # Fallback calculation without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)

    def _split_document_into_chunks(self, content: str, chunk_size: int = 200) -> List[str]:
        """
        Split document content into overlapping chunks.
        
        Args:
            content: Document content
            chunk_size: Size of each chunk in characters
            
        Returns:
            List of document chunks
        """
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), chunk_size // 5):  # Overlap chunks
            chunk_words = words[i:i + chunk_size // 5]
            chunk = " ".join(chunk_words)
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks

    async def process_task(
        self, task: Dict[str, Any], context: QueryContext
    ) -> AgentResult:
        """
        Process fact-checking task by verifying claims against documents.

        Args:
            task: Task data containing documents and query
            context: Query context

        Returns:
            AgentResult with verified facts
        """
        start_time = time.time()

        try:
            # Extract task data
            documents = task.get("documents", [])
            query = task.get("query", "")

            logger.info(f"Fact-checking for query: {query[:50]}...")
            logger.info(f"Number of documents: {len(documents)}")

            # Validate input
            if not documents:
                return AgentResult(
                    success=False,
                    data={},
                    error="No documents provided for fact-checking",
                    confidence=0.0,
                )

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

            processing_time = time.time() - start_time

            # FIXED: Return verified_facts directly in data to match orchestrator expectations
            return AgentResult(
                success=True,
                data={
                    "verified_facts": verified_facts,  # Direct access for orchestrator
                    "contested_claims": contested_claims,
                    "verification_method": "rule_based",
                    "total_claims": len(verifications),
                    "metadata": {
                        "agent_id": self.agent_id,
                        "processing_time_ms": int(processing_time * 1000),
                    },
                },
                confidence=self._calculate_verification_confidence(verifications),
                execution_time_ms=int(processing_time * 1000),
            )

        except Exception as e:
            logger.error(f"Fact-checking failed: {str(e)}")
            return AgentResult(
                success=False,
                data={},
                error=f"Fact-checking failed: {str(e)}",
                confidence=0.0,
            )

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

        # Remove duplicates and low-confidence claims
        unique_claims = self._deduplicate_claims(claims)

        return unique_claims[:10]  # Limit to top 10 claims

    def _extract_claims_from_text(self, text: str) -> List[Claim]:
        """
        Extract claims from text using pattern matching.

        Args:
            text: Text to extract claims from

        Returns:
            List of extracted claims
        """
        claims = []

        # Split into sentences
        sentences = re.split(r"[.!?]+", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue

            # Look for factual statements
            if self._is_factual_statement(sentence):
                confidence = self._calculate_claim_confidence(sentence)
                claim = Claim(text=sentence, confidence=confidence, source="extracted")
                claims.append(claim)

        return claims

    def _is_factual_statement(self, sentence: str) -> bool:
        """
        Determine if a sentence is a factual statement.

        Args:
            sentence: Sentence to analyze

        Returns:
            True if sentence appears to be factual
        """
        sentence_lower = sentence.lower()

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
            "consists",
            "comprises",
            "located",
            "found",
            "discovered",
            "identified",
            "according to",
            "research shows",
            "studies indicate",
        ]

        # Look for opinion indicators (negative)
        opinion_indicators = [
            "i think",
            "i believe",
            "in my opinion",
            "i feel",
            "probably",
            "maybe",
            "perhaps",
            "might",
            "could",
            "seems",
            "appears",
            "looks like",
        ]

        # Check for factual indicators
        has_factual = any(
            indicator in sentence_lower for indicator in factual_indicators
        )

        # Check for opinion indicators
        has_opinion = any(
            indicator in sentence_lower for indicator in opinion_indicators
        )

        return has_factual and not has_opinion

    def _calculate_claim_confidence(self, sentence: str) -> float:
        """
        Calculate confidence for a claim based on its characteristics.

        Args:
            sentence: Claim sentence

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Boost confidence for specific patterns
        if re.search(r"\d{4}", sentence):  # Contains year
            confidence += 0.1

        if re.search(r"according to|research shows|studies indicate", sentence.lower()):
            confidence += 0.2

        if len(sentence.split()) > 10:  # Longer sentences tend to be more specific
            confidence += 0.1

        return min(1.0, confidence)

    def _deduplicate_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Remove duplicate claims and sort by confidence.

        Args:
            claims: List of claims

        Returns:
            Deduplicated and sorted claims
        """
        seen_texts = set()
        unique_claims = []

        for claim in claims:
            # Normalize text for comparison
            normalized_text = re.sub(r"\s+", " ", claim.text.lower().strip())

            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                unique_claims.append(claim)

        # Sort by confidence
        unique_claims.sort(key=lambda x: x.confidence, reverse=True)

        return unique_claims

    async def _verify_claims(
        self, claims: List[Claim], documents: List[Dict]
    ) -> List[Verification]:
        """
        Verify claims against documents.

        Args:
            claims: List of claims to verify
            documents: Retrieved documents

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
        Verify a single claim against documents using LLM-based analysis.

        Args:
            claim: Claim to verify
            documents: Documents to check against

        Returns:
            Verification result
        """
        supporting_evidence = []
        contradicting_evidence = []
        source_docs = []

        claim_keywords = self._extract_keywords(claim.text)

        for doc in documents:
            doc_content = doc.get("content", "").lower()
            doc_score = doc.get("score", 0)

            # Calculate relevance to claim
            relevance_score = self._calculate_relevance(claim_keywords, doc_content)

            if relevance_score > 0.3:  # Threshold for relevance
                source_docs.append(doc.get("doc_id", "unknown"))

                # Use LLM to analyze evidence
                evidence_analysis = await self._analyze_evidence_with_llm(
                    claim.text, doc_content
                )

                if evidence_analysis["supports"]:
                    supporting_evidence.append(doc_content[:200])
                elif evidence_analysis["contradicts"]:
                    contradicting_evidence.append(doc_content[:200])

        # Determine if claim is supported based on evidence analysis
        is_supported = len(supporting_evidence) > len(contradicting_evidence)

        # Calculate confidence based on evidence quality and quantity
        total_evidence = len(supporting_evidence) + len(contradicting_evidence)
        if total_evidence == 0:
            confidence = 0.1  # Low confidence if no evidence
        else:
            support_ratio = len(supporting_evidence) / total_evidence
            confidence = min(0.9, support_ratio + claim.confidence * 0.3)

        return Verification(
            claim=claim.text,
            is_supported=is_supported,
            confidence=confidence,
            evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            source_documents=source_docs,
            verification_method="llm_analysis",
        )

    async def _analyze_evidence_with_llm(
        self, claim: str, document_content: str
    ) -> Dict[str, bool]:
        """
        Use LLM to analyze whether document content supports or contradicts a claim.

        Args:
            claim: The claim to verify
            document_content: Document content to analyze

        Returns:
            Dict with 'supports' and 'contradicts' boolean flags
        """
        try:
            from shared.core.agents.llm_client import LLMClient

            # Create prompt for LLM analysis
            prompt = f"""
            Analyze whether the following document content supports or contradicts the given claim.
            
            Claim: "{claim}"
            
            Document Content: "{document_content[:1000]}"
            
            Please respond with only:
            - "SUPPORTS" if the document content provides evidence that supports the claim
            - "CONTRADICTS" if the document content provides evidence that contradicts the claim  
            - "NEUTRAL" if the document content is not relevant or provides no clear evidence
            
            Response:"""

            llm_client = LLMClient()
            response = await llm_client.generate_text(prompt, max_tokens=50, temperature=0.1)

            response_upper = response.strip().upper()

            return {
                "supports": "SUPPORTS" in response_upper,
                "contradicts": "CONTRADICTS" in response_upper,
                "neutral": "NEUTRAL" in response_upper
                or response_upper not in ["SUPPORTS", "CONTRADICTS"],
            }

        except Exception as e:
            logger.error(f"LLM evidence analysis failed: {e}")
            # Fallback to keyword-based analysis
            return self._fallback_evidence_analysis(claim, document_content)

    def _fallback_evidence_analysis(
        self, claim: str, document_content: str
    ) -> Dict[str, bool]:
        """
        Fallback evidence analysis using keyword matching when LLM is unavailable.

        Args:
            claim: The claim to verify
            document_content: Document content to analyze

        Returns:
            Dict with 'supports' and 'contradicts' boolean flags
        """
        claim_lower = claim.lower()
        content_lower = document_content.lower()

        # Extract key terms from claim
        claim_terms = set(re.findall(r"\b\w+\b", claim_lower))
        claim_terms = {
            term for term in claim_terms if len(term) > 3
        }  # Filter short words

        # Check for supporting evidence
        supports = False
        contradicts = False

        # Look for supporting indicators
        support_indicators = [
            "confirm",
            "support",
            "evidence",
            "prove",
            "demonstrate",
            "show",
            "indicate",
        ]
        for indicator in support_indicators:
            if indicator in content_lower and any(
                term in content_lower for term in claim_terms
            ):
                supports = True
                break

        # Look for contradicting indicators
        contradict_indicators = [
            "contradict",
            "refute",
            "disprove",
            "false",
            "incorrect",
            "wrong",
            "disagree",
        ]
        for indicator in contradict_indicators:
            if indicator in content_lower and any(
                term in content_lower for term in claim_terms
            ):
                contradicts = True
                break

        return {
            "supports": supports,
            "contradicts": contradicts,
            "neutral": not supports and not contradicts,
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Text to extract keywords from

        Returns:
            List of keywords
        """
        # Simple keyword extraction
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 3]

        return keywords[:10]  # Limit to top 10 keywords

    def _calculate_relevance(self, keywords: List[str], content: str) -> float:
        """
        Calculate relevance between keywords and content.

        Args:
            keywords: List of keywords
            content: Content to check against

        Returns:
            Relevance score between 0 and 1
        """
        if not keywords or not content:
            return 0.0

        # Simple keyword matching
        matches = sum(1 for keyword in keywords if keyword in content)
        relevance = matches / len(keywords)

        return relevance

    def _find_supporting_evidence(self, claim: str, content: str) -> bool:
        """
        Check if content supports the claim.

        Args:
            claim: Claim to check
            content: Content to check against

        Returns:
            True if content supports the claim
        """
        claim_lower = claim.lower()
        content_lower = content.lower()

        # Extract key terms from claim
        claim_terms = set(re.findall(r"\b\w+\b", claim_lower))

        # Check if key terms appear in content
        content_terms = set(re.findall(r"\b\w+\b", content_lower))

        # Calculate overlap
        overlap = len(claim_terms.intersection(content_terms))
        overlap_ratio = overlap / len(claim_terms) if claim_terms else 0

        return overlap_ratio > 0.3  # Threshold for support

    def _find_contradicting_evidence(self, claim: str, content: str) -> bool:
        """
        Check if content contradicts the claim.

        Args:
            claim: Claim to check
            content: Content to check against

        Returns:
            True if content contradicts the claim
        """
        # Simple contradiction detection
        contradiction_indicators = [
            "however",
            "but",
            "although",
            "despite",
            "nevertheless",
            "on the other hand",
            "in contrast",
            "unlike",
            "different from",
        ]

        content_lower = content.lower()

        # Check for contradiction indicators
        has_contradiction_indicators = any(
            indicator in content_lower for indicator in contradiction_indicators
        )

        # Check for negation of claim terms
        claim_terms = set(re.findall(r"\b\w+\b", claim.lower()))
        negation_words = {"not", "no", "never", "none", "neither", "nor"}

        has_negation = any(term in content_lower for term in negation_words)

        return has_contradiction_indicators or has_negation

    def _filter_verified_facts(
        self, verifications: List[Verification]
    ) -> List[VerifiedFactModel]:
        """
        Filter verified facts from verifications.

        Args:
            verifications: List of verification results

        Returns:
            List of verified facts
        """
        verified_facts = []

        for verification in verifications:
            if verification.is_supported and verification.confidence > 0.6:
                verified_facts.append(
                    VerifiedFactModel(
                        claim=verification.claim,
                        confidence=verification.confidence,
                        source="fact_check_agent",
                        evidence=verification.evidence,
                        contradicting_evidence=verification.contradicting_evidence,
                        verification_method=verification.verification_method,
                        metadata={
                            "source_documents": verification.source_documents,
                        },
                    )
                )

        return verified_facts

    def _identify_contested_claims(
        self, verifications: List[Verification]
    ) -> List[Dict]:
        """
        Identify claims that need manual review.

        Args:
            verifications: List of verification results

        Returns:
            List of contested claims
        """
        contested_claims = []

        for verification in verifications:
            # Claims with mixed evidence or low confidence
            if (
                len(verification.evidence) > 0
                and len(verification.contradicting_evidence) > 0
            ) or verification.confidence < 0.5:
                contested_claims.append(
                    {
                        "claim": verification.claim,
                        "confidence": verification.confidence,
                        "supporting_evidence": verification.evidence,
                        "contradicting_evidence": verification.contradicting_evidence,
                        "source_documents": verification.source_documents,
                    }
                )

        return contested_claims

    async def _request_manual_review(self, contested_claims: List[Dict]):
        """
        Request manual review for contested claims.

        Args:
            contested_claims: List of claims that need expert review
        """
        try:
            if self.manual_review_callback:
                logger.info(
                    f"Requesting manual review for {len(contested_claims)} contested claims"
                )
                await self.manual_review_callback(contested_claims)
            else:
                # Log contested claims for manual review
                logger.warning(
                    "Contested claims detected but no manual review callback configured",
                    contested_claims=contested_claims,
                )

                # Store for later review
                await self._store_contested_claims(contested_claims)

        except Exception as e:
            logger.error(f"Manual review callback failed: {e}")

    async def _store_contested_claims(self, contested_claims: List[Dict]):
        """
        Store contested claims for later manual review.

        Args:
            contested_claims: List of claims to store
        """
        try:
            # Create review request
            review_request = {
                "id": f"review_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "claims": contested_claims,
                "status": "pending",
                "assigned_expert": None,
                "review_notes": None,
                "final_decision": None,
            }

            # Store in database or file system
            await self._save_review_request(review_request)

            logger.info(
                f"Stored {len(contested_claims)} contested claims for manual review"
            )

        except Exception as e:
            logger.error(f"Failed to store contested claims: {e}")

    async def _save_review_request(self, review_request: Dict):
        """
        Save review request to persistent storage.

        Args:
            review_request: Review request to save
        """
        try:
            # In production, save to database
            # For now, save to file system
            import json
            import os

            review_dir = "data/manual_reviews"
            os.makedirs(review_dir, exist_ok=True)

            filename = f"{review_request['id']}.json"
            filepath = os.path.join(review_dir, filename)

            with open(filepath, "w") as f:
                json.dump(review_request, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save review request: {e}")

    async def get_pending_reviews(self) -> List[Dict]:
        """
        Get list of pending manual reviews.

        Returns:
            List of pending review requests
        """
        try:
            import json
            import os
            import glob

            review_dir = "data/manual_reviews"
            if not os.path.exists(review_dir):
                return []

            pending_reviews = []
            for filepath in glob.glob(os.path.join(review_dir, "*.json")):
                try:
                    with open(filepath, "r") as f:
                        review = json.load(f)
                        if review.get("status") == "pending":
                            pending_reviews.append(review)
                except Exception as e:
                    logger.error(f"Failed to load review from {filepath}: {e}")

            return pending_reviews

        except Exception as e:
            logger.error(f"Failed to get pending reviews: {e}")
            return []

    async def update_review_decision(self, review_id: str, decision: Dict):
        """
        Update a manual review with expert decision.

        Args:
            review_id: ID of the review to update
            decision: Expert decision with notes and final verdict
        """
        try:
            import json
            import os

            review_dir = "data/manual_reviews"
            filepath = os.path.join(review_dir, f"{review_id}.json")

            if not os.path.exists(filepath):
                raise ValueError(f"Review {review_id} not found")

            # Load existing review
            with open(filepath, "r") as f:
                review = json.load(f)

            # Update with expert decision
            review.update(
                {
                    "status": "completed",
                    "assigned_expert": decision.get("expert_id"),
                    "review_notes": decision.get("notes"),
                    "final_decision": decision.get("verdict"),
                    "completed_at": datetime.now().isoformat(),
                }
            )

            # Save updated review
            with open(filepath, "w") as f:
                json.dump(review, f, indent=2)

            logger.info(f"Updated review {review_id} with expert decision")

        except Exception as e:
            logger.error(f"Failed to update review decision: {e}")
            raise

    def _calculate_verification_confidence(
        self, verifications: List[Verification]
    ) -> float:
        """
        Calculate overall verification confidence.

        Args:
            verifications: List of verification results

        Returns:
            Overall confidence score
        """
        if not verifications:
            return 0.0

        # Calculate average confidence
        avg_confidence = sum(v.confidence for v in verifications) / len(verifications)

        # Boost confidence based on number of high-confidence verifications
        high_conf_verifications = [v for v in verifications if v.confidence > 0.8]
        high_conf_boost = min(0.1, len(high_conf_verifications) * 0.02)

        final_confidence = min(1.0, avg_confidence + high_conf_boost)

        return final_confidence

    def _check_sentence_source_freshness(
        self, 
        sentence: str, 
        source_doc_ids: List[str], 
        source_docs: List[Dict[str, Any]], 
        query_timestamp: datetime
    ) -> bool:
        """
        Check if the sources supporting a sentence are outdated.
        
        Args:
            sentence: The sentence being checked
            source_doc_ids: List of source document IDs supporting the sentence
            source_docs: All available source documents
            query_timestamp: Current query timestamp
            
        Returns:
            True if all supporting sources are outdated, False otherwise
        """
        max_freshness_days = 180  # 6 months
        supporting_sources = [doc for doc in source_docs if doc.get("doc_id") in source_doc_ids]
        
        if not supporting_sources:
            return True  # No sources means outdated
        
        # Check if all supporting sources are outdated
        all_outdated = True
        for doc in supporting_sources:
            published_date = None
            
            # Try to extract published_date from various possible fields
            if "published_date" in doc:
                published_date = self._parse_date(doc["published_date"])
            elif "timestamp" in doc:
                published_date = self._parse_date(doc["timestamp"])
            elif "date" in doc:
                published_date = self._parse_date(doc["date"])
            elif "created_at" in doc:
                published_date = self._parse_date(doc["created_at"])
            
            if published_date:
                age_days = (query_timestamp - published_date).days
                if age_days <= max_freshness_days:
                    all_outdated = False
                    break
            else:
                # If no date found, assume it's outdated for safety
                logger.warning(f"No published_date found for source: {doc.get('doc_id', 'unknown')}")
        
        return all_outdated

    async def _get_vector_search_engine(self):
        """
        Get vector search engine for verification.
        
        Returns:
            Search engine instance
        """
        try:
            # Try to use Meilisearch engine
            from services.search_service.core.meilisearch_engine import MeilisearchEngine
            
            meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
            master_key = os.getenv("MEILI_MASTER_KEY")
            
            search_engine = MeilisearchEngine(meilisearch_url, master_key)
            
            # Check if engine is available
            if await search_engine.health_check():
                logger.info("Using Meilisearch for vector search verification")
                return search_engine
            else:
                logger.warning("Meilisearch not available, using fallback verification")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize vector search engine: {str(e)}")
            return None

    async def _verify_sentence_with_vector_search(
        self, 
        sentence: str, 
        search_engine, 
        source_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a single sentence using vector search.
        
        Args:
            sentence: Sentence to verify
            search_engine: Vector search engine
            source_docs: Source documents
            
        Returns:
            Verification result dictionary
        """
        if not search_engine:
            # Fallback to existing verification method
            return await self._verify_sentence_against_docs(sentence, source_docs)
        
        try:
            # Perform vector search for the sentence
            search_results = await search_engine.search(sentence, top_k=5)
            
            if not search_results:
                return {
                    "is_supported": False,
                    "confidence": 0.0,
                    "evidence": [],
                    "source_docs": [],
                    "reason": "No relevant documents found in vector search"
                }
            
            # Check if any search results support the sentence
            best_score = 0.0
            supporting_evidence = []
            supporting_docs = []
            
            for result in search_results:
                # Calculate similarity between sentence and search result
                similarity = self._calculate_sentence_similarity(sentence, result.content)
                
                if similarity > best_score:
                    best_score = similarity
                
                # Collect evidence if similarity is above threshold
                if similarity > 0.4:  # Lower threshold for evidence collection
                    supporting_evidence.append(result.content[:200])
                    supporting_docs.append(result.source)
            
            # Determine if sentence is supported
            support_threshold = 0.6  # Adjustable threshold
            is_supported = best_score >= support_threshold
            
            # Calculate confidence based on similarity and evidence quantity
            confidence = min(1.0, best_score + (len(supporting_evidence) * 0.1))
            
            return {
                "is_supported": is_supported,
                "confidence": confidence,
                "evidence": supporting_evidence[:3],  # Limit to top 3 pieces of evidence
                "source_docs": list(set(supporting_docs)),  # Remove duplicates
                "reason": f"Vector search best match similarity: {best_score:.3f}" if not is_supported else "Supported by vector search"
            }
            
        except Exception as e:
            logger.error(f"Vector search verification error: {str(e)}")
            # Fallback to existing method
            return await self._verify_sentence_against_docs(sentence, source_docs)

    def _calculate_sentence_similarity(self, sentence: str, content: str) -> float:
        """
        Calculate similarity between sentence and content using simple keyword matching.
        
        Args:
            sentence: Sentence to compare
            content: Content to compare against
            
        Returns:
            Similarity score between 0 and 1
        """
        # Extract key terms from sentence
        sentence_terms = set(re.findall(r'\b\w+\b', sentence.lower()))
        sentence_terms = {term for term in sentence_terms if len(term) > 3}
        
        if not sentence_terms:
            return 0.0
        
        # Extract key terms from content
        content_terms = set(re.findall(r'\b\w+\b', content.lower()))
        content_terms = {term for term in content_terms if len(term) > 3}
        
        if not content_terms:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(sentence_terms.intersection(content_terms))
        union = len(sentence_terms.union(content_terms))
        
        if union == 0:
            return 0.0
        
        return intersection / union

    async def _revise_unsupported_sentence(
        self, 
        sentence: str, 
        reason: str, 
        source_docs: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Use LLM to revise an unsupported sentence based on available sources.
        
        Args:
            sentence: Original sentence to revise
            reason: Reason why the sentence was unsupported
            source_docs: Available source documents
            
        Returns:
            Revised sentence or None if revision failed
        """
        try:
            # Extract key information from source documents
            source_summaries = []
            for i, doc in enumerate(source_docs[:3], 1):  # Use top 3 sources
                content = doc.get("content", "")
                if content:
                    # Take first 200 characters as summary
                    summary = content[:200] + "..." if len(content) > 200 else content
                    source_summaries.append(f"Source {i}: {summary}")
            
            sources_text = "\n".join(source_summaries) if source_summaries else "No specific sources available."
            
            # Create revision prompt
            revision_prompt = f"""
            The following sentence could not be verified against our knowledge base:
            
            Original sentence: "{sentence}"
            Reason for rejection: {reason}
            
            Available source information:
            {sources_text}
            
            Please revise the sentence to be more accurate and supported by the available information. 
            If the information cannot be verified, state that clearly.
            
            Guidelines:
            1. Only include information that can be supported by the sources
            2. Be more conservative and less specific if needed
            3. If the claim cannot be verified, use phrases like "may be", "could be", "appears to be"
            4. If no relevant information is available, state "No verified information available"
            
            Revised sentence:"""
            
            # Use LLM for revision
            from shared.core.llm_client_v3 import EnhancedLLMClientV3
            
            llm_client = EnhancedLLMClientV3()
            
            response = await llm_client.generate_text(
                prompt=revision_prompt,
                max_tokens=100,
                temperature=0.3,
                use_dynamic_selection=True
            )
            
            if response and response.strip():
                revised_sentence = response.strip()
                # Clean up the response
                if revised_sentence.startswith('"') and revised_sentence.endswith('"'):
                    revised_sentence = revised_sentence[1:-1]
                
                logger.info(f"Revised sentence: '{sentence}' -> '{revised_sentence}'")
                return revised_sentence
            else:
                logger.warning(f"LLM revision failed for sentence: {sentence}")
                return None
                
        except Exception as e:
            logger.error(f"Error revising sentence: {str(e)}")
            return None


# Example usage
async def main():
    """Example usage of FactCheckAgent."""
    agent = FactCheckAgent()

    # Example documents and query
    documents = [
        {
            "doc_id": "doc1",
            "content": "The Earth orbits around the Sun. This is a well-established fact in astronomy.",
            "score": 0.9,
        },
        {
            "doc_id": "doc2",
            "content": "The Sun is a star located at the center of our solar system.",
            "score": 0.8,
        },
    ]

    task = {
        "documents": documents,
        "query": "What is the relationship between Earth and the Sun?",
    }

    context = QueryContext(query="What is the relationship between Earth and the Sun?")

    result = await agent.process_task(task, context)
    print(f"Success: {result.success}")
    print(f"Verified facts: {len(result.data.get('verified_facts', []))}")
    print(f"Confidence: {result.confidence}")


if __name__ == "__main__":
    asyncio.run(main())
