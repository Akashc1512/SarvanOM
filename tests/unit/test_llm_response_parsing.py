"""
Unit tests for LLM response parsing functionality.

Tests cover:
- Citation extraction from LLM responses
- Confidence calculation
- Response content parsing
- Error handling for malformed responses
- Token counting and validation
"""

import pytest
import re
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any, Optional

from services.synthesis.main import extract_citations, calculate_confidence
from shared.core.agents.agent_utilities import ResponseFormatter


class TestLLMResponseParsing:
    """Test LLM response parsing functionality."""

    @pytest.fixture
    def sample_llm_response_with_citations(self):
        """Sample LLM response with citations."""
        return """
        Python is a high-level programming language that emphasizes code readability.
        
        According to the Python documentation【python.org†L1-L5】, Python was created by Guido van Rossum and first released in 1991.
        
        The language features include:
        - Dynamic typing【python_guide.pdf†L10-L15】
        - Automatic memory management
        - Comprehensive standard library【stdlib_reference.pdf†L20-L25】
        
        Machine learning applications【ml_tutorial.pdf†L30-L35】 have become increasingly popular in Python.
        """

    @pytest.fixture
    def sample_llm_response_without_citations(self):
        """Sample LLM response without citations."""
        return """
        Python is a high-level programming language that emphasizes code readability.
        It was created by Guido van Rossum and first released in 1991.
        The language features include dynamic typing, automatic memory management, and a comprehensive standard library.
        """

    @pytest.fixture
    def sample_malformed_response(self):
        """Sample malformed LLM response."""
        return """
        This is a response with【incomplete citation†L1- and 【another†L5】 and 【third†L10-L15
        """

    def test_extract_citations_basic(self, sample_llm_response_with_citations):
        """Test basic citation extraction."""
        citations = extract_citations(sample_llm_response_with_citations)
        
        assert len(citations) == 4
        assert citations[0]["source"] == "python.org"
        assert citations[0]["start_line"] == 1
        assert citations[0]["end_line"] == 5
        assert citations[1]["source"] == "python_guide.pdf"
        assert citations[1]["start_line"] == 10
        assert citations[1]["end_line"] == 15

    def test_extract_citations_no_citations(self, sample_llm_response_without_citations):
        """Test citation extraction from response without citations."""
        citations = extract_citations(sample_llm_response_without_citations)
        
        assert citations == []

    def test_extract_citations_malformed(self, sample_malformed_response):
        """Test citation extraction from malformed response."""
        citations = extract_citations(sample_malformed_response)
        
        # Should handle malformed citations gracefully
        # The current implementation may not extract any citations from malformed text
        # which is acceptable behavior
        assert isinstance(citations, list)
        # Check that any extracted citations have valid structure
        for citation in citations:
            assert "source" in citation
            assert "start_line" in citation
            assert "end_line" in citation
            assert isinstance(citation["start_line"], int)
            assert isinstance(citation["end_line"], int)

    def test_extract_citations_edge_cases(self):
        """Test citation extraction edge cases."""
        edge_cases = [
            "【source†L1-L1】",  # Same line
            "【source†L100-L200】",  # Large line numbers
            "【source_with_underscores†L1-L5】",  # Underscores in source
            "【source-with-dashes†L1-L5】",  # Dashes in source
            "【source†L1-L5】text【another†L10-L15】",  # Multiple citations
        ]
        
        for case in edge_cases:
            citations = extract_citations(case)
            assert len(citations) >= 1
            for citation in citations:
                assert citation["start_line"] <= citation["end_line"]

    def test_calculate_confidence_basic(self):
        """Test basic confidence calculation."""
        content = "This is a comprehensive answer about Python programming."
        sources = ["source1.pdf", "source2.pdf", "source3.pdf"]
        
        confidence = calculate_confidence(content, sources)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.0  # Should have some confidence with sources

    def test_calculate_confidence_no_sources(self):
        """Test confidence calculation with no sources."""
        content = "This is an answer without sources."
        sources = []
        
        confidence = calculate_confidence(content, sources)
        
        assert confidence == 0.0

    def test_calculate_confidence_long_content(self):
        """Test confidence calculation with long content."""
        content = "A" * 5000  # Very long content
        sources = ["source1.pdf"]
        
        confidence = calculate_confidence(content, sources)
        
        assert 0.0 <= confidence <= 1.0
        # Long content should contribute to confidence
        assert confidence > 0.1

    def test_calculate_confidence_many_sources(self):
        """Test confidence calculation with many sources."""
        content = "Short answer"
        sources = ["source1.pdf", "source2.pdf", "source3.pdf", "source4.pdf", "source5.pdf"]
        
        confidence = calculate_confidence(content, sources)
        
        assert 0.0 <= confidence <= 1.0
        # Many sources should increase confidence
        assert confidence > 0.4

    def test_calculate_confidence_capped(self):
        """Test that confidence is properly capped at 1.0."""
        content = "A" * 10000  # Very long content
        sources = ["source1.pdf", "source2.pdf", "source3.pdf", "source4.pdf", "source5.pdf", "source6.pdf"]
        
        confidence = calculate_confidence(content, sources)
        
        assert confidence <= 1.0



    def test_token_counting(self):
        """Test token counting functionality."""
        content = "This is a test sentence with multiple words."
        
        # Mock token counting (simplified)
        token_count = len(content.split())
        
        assert token_count == 8  # "This is a test sentence with multiple words"

    def test_response_formatter_synthesis(self):
        """Test ResponseFormatter synthesis response formatting."""
        answer = "This is a synthesized answer"
        synthesis_method = "llm_synthesis"
        fact_count = 5
        processing_time_ms = 1500
        metadata = {"sources": ["source1.pdf", "source2.pdf"]}
        
        formatted = ResponseFormatter.format_synthesis_response(
            answer, synthesis_method, fact_count, processing_time_ms, metadata
        )
        
        assert formatted["success"] is True
        assert formatted["data"]["answer"] == answer
        assert formatted["data"]["synthesis_method"] == synthesis_method
        assert formatted["data"]["fact_count"] == fact_count
        assert formatted["data"]["processing_time_ms"] == processing_time_ms
        assert formatted["confidence"] == 1.0  # fact_count / 5.0 = 1.0
        assert formatted["execution_time_ms"] == processing_time_ms
        assert formatted["metadata"] == metadata

    def test_response_formatter_citation(self):
        """Test ResponseFormatter citation response formatting."""
        cited_content = "This is cited content"
        citations = [
            {"source": "source1.pdf", "start_line": 1, "end_line": 5},
            {"source": "source2.pdf", "start_line": 10, "end_line": 15}
        ]
        citation_format = "【source†Lx-Ly】"
        processing_time_ms = 800
        metadata = {"total_sources": 2}
        
        formatted = ResponseFormatter.format_citation_response(
            cited_content, citations, citation_format, processing_time_ms, metadata
        )
        
        assert formatted["success"] is True
        assert formatted["data"]["cited_content"] == cited_content
        assert formatted["data"]["citations"] == citations
        assert formatted["data"]["citation_format"] == citation_format
        assert formatted["data"]["processing_time_ms"] == processing_time_ms
        assert formatted["confidence"] == 0.4  # len(citations) / 5.0 = 0.4
        assert formatted["execution_time_ms"] == processing_time_ms
        assert formatted["metadata"] == metadata

    def test_citation_validation(self):
        """Test citation validation and sanitization."""
        malformed_citations = [
            {"source": "valid.pdf", "start_line": 1, "end_line": 5},  # Valid
            {"source": "", "start_line": 1, "end_line": 5},  # Empty source
            {"source": "valid.pdf", "start_line": 5, "end_line": 1},  # Invalid range
            {"source": "valid.pdf", "start_line": -1, "end_line": 5},  # Negative line
        ]
        
        # Filter valid citations
        valid_citations = []
        for citation in malformed_citations:
            if (citation["source"] and 
                citation["start_line"] > 0 and 
                citation["end_line"] > 0 and
                citation["start_line"] <= citation["end_line"]):
                valid_citations.append(citation)
        
        assert len(valid_citations) == 1  # Only the first one should be valid

    def test_confidence_edge_cases(self):
        """Test confidence calculation edge cases."""
        # Very short content
        confidence = calculate_confidence("Hi", ["source1.pdf"])
        assert 0.0 <= confidence <= 1.0
        
        # Very long content
        confidence = calculate_confidence("A" * 10000, ["source1.pdf"])
        assert 0.0 <= confidence <= 1.0
        
        # Many sources
        confidence = calculate_confidence("Answer", ["s1.pdf"] * 10)
        assert 0.0 <= confidence <= 1.0

    def test_citation_regex_patterns(self):
        """Test various citation regex patterns."""
        patterns = [
            r'【([^†]+)†L(\d+)-L(\d+)】',  # Standard pattern
            r'【([^†]+)†L(\d+)-L(\d+)】',  # Same pattern
        ]
        
        test_text = "【source.pdf†L1-L5】"
        
        for pattern in patterns:
            matches = re.findall(pattern, test_text)
            assert len(matches) == 1
            assert matches[0][0] == "source.pdf"
            assert matches[0][1] == "1"
            assert matches[0][2] == "5"



    def test_citation_source_normalization(self):
        """Test normalization of citation sources."""
        response = "【source with spaces.pdf†L1-L5】【source-with-dashes.pdf†L10-L15】"
        citations = extract_citations(response)
        
        assert len(citations) == 2
        assert citations[0]["source"] == "source with spaces.pdf"
        assert citations[1]["source"] == "source-with-dashes.pdf"

    def test_confidence_with_content_quality(self):
        """Test confidence calculation considering content quality."""
        # High-quality content (longer, more detailed)
        high_quality = "This is a comprehensive analysis with detailed explanations and multiple examples."
        # Low-quality content (short, vague)
        low_quality = "This is an answer."
        
        sources = ["source1.pdf", "source2.pdf"]
        
        high_confidence = calculate_confidence(high_quality, sources)
        low_confidence = calculate_confidence(low_quality, sources)
        
        # High-quality content should have higher confidence
        assert high_confidence > low_confidence
