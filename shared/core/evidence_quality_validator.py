#!/usr/bin/env python3
"""
SarvanOM Evidence & Citation Quality Validator
Validates evidence quality, citation requirements, and credibility metadata
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

class CitationQualityLevel(Enum):
    """Citation quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    FAILED = "failed"

class DisagreementType(Enum):
    """Types of disagreement detected"""
    FACTUAL_CONFLICT = "factual_conflict"
    STATISTICAL_DISCREPANCY = "statistical_discrepancy"
    EXPERT_OPINION_DIVISION = "expert_opinion_division"
    SOURCE_CREDIBILITY_ISSUE = "source_credibility_issue"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"

@dataclass
class Citation:
    """Individual citation with metadata"""
    title: str
    url: str
    domain: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    credibility_score: float = 0.0
    authority_level: str = "unknown"
    content_type: str = "unknown"
    inline_marker: Optional[str] = None
    bibliography_entry: Optional[str] = None

@dataclass
class DisagreementEvent:
    """Disagreement detection event"""
    type: DisagreementType
    description: str
    conflicting_sources: List[str]
    severity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    detected_at: str  # timestamp or position

@dataclass
class EvidenceQualityReport:
    """Comprehensive evidence quality assessment"""
    total_citations: int
    unique_domains: int
    unique_sources: int
    quality_level: CitationQualityLevel
    coverage_percentage: float
    credibility_score: float
    disagreement_events: List[DisagreementEvent]
    missing_metadata: List[str]
    quality_issues: List[str]
    inline_markers_present: bool
    bibliography_present: bool
    meets_research_requirements: bool
    meets_technical_requirements: bool
    meets_simple_requirements: bool

class EvidenceQualityValidator:
    """Validates evidence quality and citation requirements"""
    
    def __init__(self):
        self.credibility_domains = {
            # Academic and research institutions
            "edu": 0.9,
            "ac.uk": 0.9,
            "ac.jp": 0.9,
            "ac.in": 0.9,
            # Government sources
            "gov": 0.95,
            "gov.uk": 0.95,
            "gov.au": 0.95,
            "gov.ca": 0.95,
            # Medical and scientific
            "nih.gov": 0.95,
            "who.int": 0.95,
            "cdc.gov": 0.95,
            "nature.com": 0.9,
            "science.org": 0.9,
            "cell.com": 0.9,
            "nejm.org": 0.9,
            "thelancet.com": 0.9,
            # News and media (varies by source)
            "reuters.com": 0.8,
            "ap.org": 0.8,
            "bbc.com": 0.8,
            "bbc.co.uk": 0.8,
            "npr.org": 0.8,
            "pbs.org": 0.8,
            "theguardian.com": 0.7,
            "nytimes.com": 0.7,
            "washingtonpost.com": 0.7,
            "wsj.com": 0.7,
            "ft.com": 0.7,
            # Technology and industry
            "ieee.org": 0.9,
            "acm.org": 0.9,
            "stackoverflow.com": 0.6,
            "github.com": 0.6,
            "wikipedia.org": 0.5,
            "wikimedia.org": 0.5,
        }
        
        self.disagreement_keywords = {
            DisagreementType.FACTUAL_CONFLICT: [
                "disagreement", "conflict", "contradict", "dispute", "debate",
                "controversy", "inconsistency", "divergence", "opposing"
            ],
            DisagreementType.STATISTICAL_DISCREPANCY: [
                "different results", "varying data", "statistical difference",
                "margin of error", "confidence interval", "p-value"
            ],
            DisagreementType.EXPERT_OPINION_DIVISION: [
                "experts disagree", "divided opinion", "mixed views",
                "some argue", "others believe", "consensus lacking"
            ],
            DisagreementType.SOURCE_CREDIBILITY_ISSUE: [
                "unreliable source", "questionable", "bias", "conflict of interest",
                "funding source", "sponsored content"
            ],
            DisagreementType.TEMPORAL_INCONSISTENCY: [
                "outdated", "recent study", "new research", "previously thought",
                "updated findings", "changed understanding"
            ]
        }
        
        # Inline citation patterns
        self.inline_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\([^)]*\d{4}[^)]*\)',  # (Author, 2024)
            r'\([^)]*et al\.?\s*\d{4}[^)]*\)',  # (Smith et al., 2024)
            r'\([^)]*pp\.?\s*\d+[^)]*\)',  # (pp. 123)
            r'\([^)]*p\.?\s*\d+[^)]*\)',  # (p. 123)
        ]
        
        # Bibliography patterns
        self.bibliography_patterns = [
            r'^\d+\.\s+',  # 1. Author, Title...
            r'^\[(\d+)\]\s+',  # [1] Author, Title...
            r'^Author,?\s+[A-Z]',  # Author, Title...
            r'^\w+,?\s+\w+\.?\s+\([^)]*\d{4}[^)]*\)',  # Author, Title (2024)
        ]
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown"
    
    def calculate_credibility_score(self, domain: str, title: str = "", author: str = "") -> float:
        """Calculate credibility score for a source"""
        base_score = self.credibility_domains.get(domain, 0.5)
        
        # Adjust based on title keywords
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in ["peer-reviewed", "journal", "study", "research"]):
            base_score += 0.1
        elif any(keyword in title_lower for keyword in ["blog", "opinion", "personal"]):
            base_score -= 0.2
        
        # Adjust based on author
        if author and any(keyword in author.lower() for keyword in ["dr.", "professor", "phd", "md"]):
            base_score += 0.05
        
        return min(1.0, max(0.0, base_score))
    
    def parse_citations(self, response_data: Dict[str, Any]) -> List[Citation]:
        """Parse citations from response data"""
        citations = []
        sources = response_data.get('sources', [])
        citations_data = response_data.get('citations', [])
        
        # Process sources
        for i, source in enumerate(sources):
            url = source.get('url', '')
            domain = self.extract_domain(url)
            
            citation = Citation(
                title=source.get('title', ''),
                url=url,
                domain=domain,
                author=source.get('author'),
                publication_date=source.get('date'),
                credibility_score=self.calculate_credibility_score(domain, source.get('title', '')),
                authority_level=source.get('authority_level', 'unknown'),
                content_type=source.get('content_type', 'unknown'),
                inline_marker=f"[{i+1}]" if i < len(sources) else None
            )
            citations.append(citation)
        
        # Process citations data if available
        for citation_data in citations_data:
            url = citation_data.get('url', '')
            domain = self.extract_domain(url)
            
            citation = Citation(
                title=citation_data.get('title', ''),
                url=url,
                domain=domain,
                author=citation_data.get('author'),
                publication_date=citation_data.get('date'),
                credibility_score=self.calculate_credibility_score(domain, citation_data.get('title', '')),
                authority_level=citation_data.get('authority_level', 'unknown'),
                content_type=citation_data.get('content_type', 'unknown'),
                inline_marker=citation_data.get('inline_marker'),
                bibliography_entry=citation_data.get('bibliography_entry')
            )
            citations.append(citation)
        
        return citations
    
    def detect_disagreements(self, response_content: str, citations: List[Citation]) -> List[DisagreementEvent]:
        """Detect disagreement events in response content"""
        disagreements = []
        content_lower = response_content.lower()
        
        for disagreement_type, keywords in self.disagreement_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Find the context around the keyword
                    start = content_lower.find(keyword)
                    if start != -1:
                        context_start = max(0, start - 100)
                        context_end = min(len(response_content), start + 100)
                        context = response_content[context_start:context_end]
                        
                        # Determine severity based on keyword and context
                        severity = 0.5
                        if any(strong_word in context_lower for strong_word in ["strongly", "completely", "fundamentally"]):
                            severity = 0.8
                        elif any(weak_word in context_lower for weak_word in ["slightly", "minor", "small"]):
                            severity = 0.3
                        
                        # Determine confidence based on context
                        confidence = 0.7
                        if any(confidence_word in context_lower for confidence_word in ["clearly", "obviously", "evidently"]):
                            confidence = 0.9
                        elif any(uncertainty_word in context_lower for uncertainty_word in ["possibly", "might", "could"]):
                            confidence = 0.5
                        
                        disagreement = DisagreementEvent(
                            type=disagreement_type,
                            description=f"Detected {keyword} in context: {context.strip()}",
                            conflicting_sources=[c.domain for c in citations if c.domain != "unknown"],
                            severity=severity,
                            confidence=confidence,
                            detected_at=f"position_{start}"
                        )
                        disagreements.append(disagreement)
        
        return disagreements
    
    def check_inline_markers(self, response_content: str) -> bool:
        """Check if inline citation markers are present"""
        for pattern in self.inline_patterns:
            if re.search(pattern, response_content):
                return True
        return False
    
    def check_bibliography(self, response_content: str) -> bool:
        """Check if bibliography is present"""
        lines = response_content.split('\n')
        for line in lines:
            for pattern in self.bibliography_patterns:
                if re.search(pattern, line.strip()):
                    return True
        return False
    
    def calculate_coverage_percentage(self, response_content: str, citations: List[Citation]) -> float:
        """Calculate what percentage of claims are covered by citations"""
        # Simple heuristic: count sentences and compare to citation count
        sentences = re.split(r'[.!?]+', response_content)
        claim_sentences = [s for s in sentences if len(s.strip()) > 20]  # Filter out short sentences
        
        if not claim_sentences:
            return 0.0
        
        # Estimate coverage based on citation density
        citation_density = len(citations) / len(claim_sentences)
        coverage = min(1.0, citation_density * 2)  # Assume 2 citations per claim is good coverage
        
        return coverage * 100
    
    def validate_evidence_quality(self, response_data: Dict[str, Any], complexity: str) -> EvidenceQualityReport:
        """Validate evidence quality based on complexity tier"""
        response_content = response_data.get('answer', '')
        citations = self.parse_citations(response_data)
        
        # Deduplicate by domain
        unique_domains = set(c.domain for c in citations if c.domain != "unknown")
        unique_sources = len(set(c.url for c in citations if c.url))
        
        # Detect disagreements
        disagreements = self.detect_disagreements(response_content, citations)
        
        # Check inline markers and bibliography
        inline_markers_present = self.check_inline_markers(response_content)
        bibliography_present = self.check_bibliography(response_content)
        
        # Calculate coverage
        coverage_percentage = self.calculate_coverage_percentage(response_content, citations)
        
        # Calculate average credibility
        credibility_scores = [c.credibility_score for c in citations if c.credibility_score > 0]
        avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.0
        
        # Check missing metadata
        missing_metadata = []
        for citation in citations:
            if not citation.author:
                missing_metadata.append(f"Missing author for {citation.domain}")
            if not citation.publication_date:
                missing_metadata.append(f"Missing date for {citation.domain}")
            if citation.authority_level == "unknown":
                missing_metadata.append(f"Missing authority level for {citation.domain}")
        
        # Quality issues
        quality_issues = []
        if len(unique_domains) < 2:
            quality_issues.append("Insufficient domain diversity")
        if avg_credibility < 0.6:
            quality_issues.append("Low average credibility score")
        if coverage_percentage < 70:
            quality_issues.append("Low citation coverage")
        if disagreements:
            quality_issues.append(f"{len(disagreements)} disagreement events detected")
        
        # Determine quality level
        quality_level = CitationQualityLevel.FAILED
        if len(citations) >= 6 and len(unique_domains) >= 3 and avg_credibility >= 0.7 and coverage_percentage >= 85:
            quality_level = CitationQualityLevel.EXCELLENT
        elif len(citations) >= 4 and len(unique_domains) >= 2 and avg_credibility >= 0.6 and coverage_percentage >= 70:
            quality_level = CitationQualityLevel.GOOD
        elif len(citations) >= 2 and len(unique_domains) >= 1 and avg_credibility >= 0.5 and coverage_percentage >= 50:
            quality_level = CitationQualityLevel.ADEQUATE
        elif len(citations) >= 1:
            quality_level = CitationQualityLevel.POOR
        
        # Check tier-specific requirements
        meets_research_requirements = (
            complexity == "research" and
            len(citations) >= 6 and
            len(unique_domains) >= 3 and
            inline_markers_present and
            bibliography_present and
            coverage_percentage >= 85 and
            avg_credibility >= 0.7
        )
        
        meets_technical_requirements = (
            complexity == "technical" and
            len(citations) >= 3 and
            len(unique_domains) >= 2 and
            coverage_percentage >= 70 and
            avg_credibility >= 0.6
        )
        
        meets_simple_requirements = (
            complexity == "simple" and
            len(citations) >= 1 and
            coverage_percentage >= 50 and
            avg_credibility >= 0.5
        )
        
        return EvidenceQualityReport(
            total_citations=len(citations),
            unique_domains=len(unique_domains),
            unique_sources=unique_sources,
            quality_level=quality_level,
            coverage_percentage=coverage_percentage,
            credibility_score=avg_credibility,
            disagreement_events=disagreements,
            missing_metadata=missing_metadata,
            quality_issues=quality_issues,
            inline_markers_present=inline_markers_present,
            bibliography_present=bibliography_present,
            meets_research_requirements=meets_research_requirements,
            meets_technical_requirements=meets_technical_requirements,
            meets_simple_requirements=meets_simple_requirements
        )
    
    def should_fail_scenario(self, report: EvidenceQualityReport, complexity: str) -> Tuple[bool, List[str]]:
        """Determine if scenario should fail based on evidence quality"""
        failure_reasons = []
        
        # Check tier-specific requirements
        if complexity == "research":
            if not report.meets_research_requirements:
                failure_reasons.append("Research tier requirements not met")
            if report.coverage_percentage < 85:
                failure_reasons.append(f"Citation coverage {report.coverage_percentage:.1f}% < 85%")
            if report.credibility_score < 0.7:
                failure_reasons.append(f"Average credibility {report.credibility_score:.2f} < 0.7")
            if not report.inline_markers_present:
                failure_reasons.append("Missing inline citation markers")
            if not report.bibliography_present:
                failure_reasons.append("Missing bibliography")
        
        elif complexity == "technical":
            if not report.meets_technical_requirements:
                failure_reasons.append("Technical tier requirements not met")
            if report.coverage_percentage < 70:
                failure_reasons.append(f"Citation coverage {report.coverage_percentage:.1f}% < 70%")
            if report.credibility_score < 0.6:
                failure_reasons.append(f"Average credibility {report.credibility_score:.2f} < 0.6")
        
        elif complexity == "simple":
            if not report.meets_simple_requirements:
                failure_reasons.append("Simple tier requirements not met")
            if report.coverage_percentage < 50:
                failure_reasons.append(f"Citation coverage {report.coverage_percentage:.1f}% < 50%")
            if report.credibility_score < 0.5:
                failure_reasons.append(f"Average credibility {report.credibility_score:.2f} < 0.5")
        
        # Check for critical issues
        if report.quality_level == CitationQualityLevel.FAILED:
            failure_reasons.append("Evidence quality level: FAILED")
        
        if len(report.disagreement_events) > 3:
            failure_reasons.append(f"Too many disagreement events: {len(report.disagreement_events)}")
        
        # Check for missing credibility metadata
        if len(report.missing_metadata) > len(report.total_citations) * 0.5:
            failure_reasons.append("Too many sources lack credibility metadata")
        
        should_fail = len(failure_reasons) > 0
        return should_fail, failure_reasons
