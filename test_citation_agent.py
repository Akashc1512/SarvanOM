"""
Test suite for enhanced CitationAgent with inline citation support.
Tests citation generation, sentence mapping, and validation of unsupported statements.
"""

import asyncio
import pytest
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.synthesis_service.citation_agent import CitationAgent, CitationResult


class TestCitationAgent:
    """Test class for CitationAgent functionality."""

    @pytest.fixture
    def citation_agent(self):
        """Create a CitationAgent instance for testing."""
        return CitationAgent()

    @pytest.fixture
    def sample_source_docs(self):
        """Sample source documents for testing."""
        return [
            {
                "doc_id": "doc1",
                "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "url": "https://wikipedia.org/python",
                "title": "Python Programming Language",
                "author": "Wikipedia Contributors",
                "timestamp": "2024-01-15T10:30:00Z",
                "score": 0.9
            },
            {
                "doc_id": "doc2",
                "content": "Python 3.12 was released in October 2023 with new features including improved error messages.",
                "url": "https://python.org/news",
                "title": "Python 3.12 Release",
                "author": "Python Software Foundation",
                "timestamp": "2023-10-02T14:20:00Z",
                "score": 0.8
            },
            {
                "doc_id": "doc3",
                "content": "Python supports object-oriented programming, functional programming, and procedural programming paradigms.",
                "url": "https://docs.python.org/3/tutorial/classes.html",
                "title": "Python Classes and Objects",
                "author": "Python Documentation",
                "timestamp": "2024-02-01T09:15:00Z",
                "score": 0.7
            }
        ]

    @pytest.fixture
    def sample_verified_sentences(self):
        """Sample verified sentences from fact checker."""
        return [
            {
                "sentence": "Python is a high-level programming language created by Guido van Rossum.",
                "confidence": 0.95,
                "evidence": ["Python is a high-level programming language"],
                "source_docs": ["doc1"]
            },
            {
                "sentence": "Python 3.12 was released in October 2023 with new features.",
                "confidence": 0.88,
                "evidence": ["Python 3.12 was released in October 2023"],
                "source_docs": ["doc2"]
            },
            {
                "sentence": "Python supports object-oriented programming.",
                "confidence": 0.82,
                "evidence": ["Python supports object-oriented programming"],
                "source_docs": ["doc3"]
            }
        ]

    @pytest.fixture
    def sample_answer_text(self):
        """Sample answer text for testing."""
        return "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. Python supports object-oriented programming. This is an unsupported statement that should not be cited."

    async def test_generate_citations_basic(self, citation_agent, sample_source_docs, sample_answer_text):
        """Test basic citation generation without verified sentences."""
        logger.info("Testing basic citation generation...")
        
        result = await citation_agent.generate_citations(
            sample_answer_text, sample_source_docs
        )
        
        # Assertions
        assert isinstance(result, CitationResult)
        assert result.annotated_answer is not None
        assert len(result.citations) == 3
        assert result.total_citations == 3
        assert result.citation_style == "inline"
        
        # Check that citations are added to the answer
        assert "[1]" in result.annotated_answer
        assert "[2]" in result.annotated_answer
        assert "[3]" in result.annotated_answer
        
        # Check citation list structure
        for citation in result.citations:
            assert "id" in citation
            assert "title" in citation
            assert "url" in citation
            assert isinstance(citation["id"], int)
        
        logger.info("✅ Basic citation generation test passed")

    async def test_generate_citations_with_verified_sentences(self, citation_agent, sample_source_docs, sample_verified_sentences, sample_answer_text):
        """Test citation generation with verified sentences from fact checker."""
        logger.info("Testing citation generation with verified sentences...")
        
        result = await citation_agent.generate_citations(
            sample_answer_text, sample_source_docs, sample_verified_sentences
        )
        
        # Assertions
        assert isinstance(result, CitationResult)
        assert result.annotated_answer is not None
        assert len(result.citations) == 3
        
        # Check that verified sentences have citations
        assert "Python is a high-level programming language created by Guido van Rossum. [1]" in result.annotated_answer
        assert "Python 3.12 was released in October 2023 with new features. [2]" in result.annotated_answer
        assert "Python supports object-oriented programming. [3]" in result.annotated_answer
        
        # Check that unsupported statement is not cited
        assert "This is an unsupported statement that should not be cited." in result.annotated_answer
        assert "This is an unsupported statement that should not be cited. [" not in result.annotated_answer
        
        logger.info("✅ Citation generation with verified sentences test passed")

    async def test_sentence_splitting(self, citation_agent):
        """Test sentence splitting functionality."""
        logger.info("Testing sentence splitting...")
        
        text = "This is sentence one. This is sentence two! This is sentence three?"
        sentences = citation_agent._split_into_sentences(text)
        
        # Assertions
        assert len(sentences) == 3
        assert "This is sentence one." in sentences
        assert "This is sentence two!" in sentences
        assert "This is sentence three?" in sentences
        
        # Test with empty text
        empty_sentences = citation_agent._split_into_sentences("")
        assert len(empty_sentences) == 0
        
        # Test with single sentence
        single_sentence = citation_agent._split_into_sentences("Single sentence.")
        assert len(single_sentence) == 1
        assert single_sentence[0] == "Single sentence."
        
        logger.info("✅ Sentence splitting test passed")

    async def test_sentence_supported_by_source(self, citation_agent, sample_source_docs):
        """Test sentence support detection."""
        logger.info("Testing sentence support detection...")
        
        # Test supported sentence
        supported_sentence = "Python is a high-level programming language"
        is_supported = citation_agent._sentence_supported_by_source(supported_sentence, sample_source_docs[0])
        assert is_supported == True
        
        # Test unsupported sentence
        unsupported_sentence = "This is completely unrelated to Python"
        is_supported = citation_agent._sentence_supported_by_source(unsupported_sentence, sample_source_docs[0])
        assert is_supported == False
        
        # Test sentence with partial support
        partial_sentence = "Python was created by someone"
        is_supported = citation_agent._sentence_supported_by_source(partial_sentence, sample_source_docs[0])
        # Should be supported because "Python" and "created" are key terms
        assert is_supported == True
        
        logger.info("✅ Sentence support detection test passed")

    async def test_sentences_match(self, citation_agent):
        """Test sentence matching functionality."""
        logger.info("Testing sentence matching...")
        
        # Test matching sentences
        sentence1 = "Python is a programming language"
        sentence2 = "Python is a programming language"
        assert citation_agent._sentences_match(sentence1, sentence2) == True
        
        # Test similar sentences
        sentence1 = "Python is a high-level programming language"
        sentence2 = "Python is a programming language"
        assert citation_agent._sentences_match(sentence1, sentence2) == True
        
        # Test different sentences
        sentence1 = "Python is a programming language"
        sentence2 = "Java is a programming language"
        assert citation_agent._sentences_match(sentence1, sentence2) == False
        
        # Test with empty sentences
        assert citation_agent._sentences_match("", "Python") == False
        assert citation_agent._sentences_match("Python", "") == False
        
        logger.info("✅ Sentence matching test passed")

    async def test_multiple_references_same_source(self, citation_agent):
        """Test handling of multiple references to the same source."""
        logger.info("Testing multiple references to same source...")
        
        source_docs = [
            {
                "doc_id": "doc1",
                "content": "Python is a programming language. Python was created by Guido van Rossum.",
                "url": "https://wikipedia.org/python",
                "title": "Python Programming Language",
                "score": 0.9
            }
        ]
        
        answer_text = "Python is a programming language. Python was created by Guido van Rossum."
        
        result = await citation_agent.generate_citations(answer_text, source_docs)
        
        # Both sentences should reference the same source
        assert "[1]" in result.annotated_answer
        assert result.annotated_answer.count("[1]") == 2  # Same citation used twice
        
        # Check citation map
        assert "1" in result.citation_map
        assert len(result.citation_map["1"]) == 2  # Citation 1 used in sentences 0 and 1
        
        logger.info("✅ Multiple references to same source test passed")

    async def test_unsupported_statements_not_cited(self, citation_agent, sample_source_docs):
        """Test that unsupported statements are not cited."""
        logger.info("Testing that unsupported statements are not cited...")
        
        answer_text = "Python is a programming language. This is completely unsupported information."
        
        result = await citation_agent.generate_citations(answer_text, sample_source_docs)
        
        # Check that supported sentence has citation
        assert "Python is a programming language. [1]" in result.annotated_answer
        
        # Check that unsupported sentence does not have citation
        assert "This is completely unsupported information." in result.annotated_answer
        assert "This is completely unsupported information. [" not in result.annotated_answer
        
        logger.info("✅ Unsupported statements not cited test passed")

    async def test_empty_source_docs(self, citation_agent):
        """Test handling of empty source documents."""
        logger.info("Testing empty source documents...")
        
        answer_text = "This is a test answer."
        empty_sources = []
        
        result = await citation_agent.generate_citations(answer_text, empty_sources)
        
        # Should return original answer without citations
        assert result.annotated_answer == answer_text
        assert len(result.citations) == 0
        assert result.total_citations == 0
        
        logger.info("✅ Empty source documents test passed")

    async def test_citation_list_structure(self, citation_agent, sample_source_docs):
        """Test citation list structure and content."""
        logger.info("Testing citation list structure...")
        
        answer_text = "Python is a programming language."
        
        result = await citation_agent.generate_citations(answer_text, sample_source_docs)
        
        # Check citation list structure
        assert len(result.citations) == 3
        
        for i, citation in enumerate(result.citations, 1):
            assert citation["id"] == i
            assert "title" in citation
            assert "url" in citation
            assert "author" in citation
            assert "date" in citation
            assert "source" in citation
            assert "confidence" in citation
            assert isinstance(citation["confidence"], float)
        
        # Check specific citation content
        assert result.citations[0]["title"] == "Python Programming Language"
        assert result.citations[0]["url"] == "https://wikipedia.org/python"
        
        logger.info("✅ Citation list structure test passed")

    async def test_citation_map_functionality(self, citation_agent, sample_source_docs):
        """Test citation map functionality."""
        logger.info("Testing citation map functionality...")
        
        answer_text = "Python is a programming language. Python 3.12 was released."
        
        result = await citation_agent.generate_citations(answer_text, sample_source_docs)
        
        # Check citation map structure
        assert isinstance(result.citation_map, dict)
        
        # Check that citations are mapped to sentence indices
        for citation_id, sentence_indices in result.citation_map.items():
            assert isinstance(citation_id, str)
            assert isinstance(sentence_indices, list)
            assert all(isinstance(idx, int) for idx in sentence_indices)
        
        logger.info("✅ Citation map functionality test passed")

    async def test_error_handling(self, citation_agent):
        """Test error handling in citation generation."""
        logger.info("Testing error handling...")
        
        # Test with None values
        result = await citation_agent.generate_citations(None, [])
        assert result.citation_style == "error"
        assert result.total_citations == 0
        
        # Test with invalid source documents
        invalid_sources = [{"invalid": "data"}]
        result = await citation_agent.generate_citations("Test", invalid_sources)
        assert isinstance(result, CitationResult)
        assert result.total_citations > 0  # Should still create citations
        
        logger.info("✅ Error handling test passed")


async def run_citation_agent_tests():
    """Run all citation agent tests."""
    logger.info("🚀 Starting CitationAgent Tests...")
    
    test_instance = TestCitationAgent()
    citation_agent = CitationAgent()
    
    # Test data
    sample_source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "url": "https://wikipedia.org/python",
            "title": "Python Programming Language",
            "author": "Wikipedia Contributors",
            "timestamp": "2024-01-15T10:30:00Z",
            "score": 0.9
        },
        {
            "doc_id": "doc2",
            "content": "Python 3.12 was released in October 2023 with new features including improved error messages.",
            "url": "https://python.org/news",
            "title": "Python 3.12 Release",
            "author": "Python Software Foundation",
            "timestamp": "2023-10-02T14:20:00Z",
            "score": 0.8
        }
    ]
    
    sample_verified_sentences = [
        {
            "sentence": "Python is a high-level programming language created by Guido van Rossum.",
            "confidence": 0.95,
            "evidence": ["Python is a high-level programming language"],
            "source_docs": ["doc1"]
        },
        {
            "sentence": "Python 3.12 was released in October 2023 with new features.",
            "confidence": 0.88,
            "evidence": ["Python 3.12 was released in October 2023"],
            "source_docs": ["doc2"]
        }
    ]
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Citation Generation",
            "answer": "Python is a programming language. Python 3.12 was released.",
            "sources": sample_source_docs,
            "verified_sentences": None,
            "expected_citations": 2  # All sources are included in citation list
        },
        {
            "name": "Citation with Verified Sentences",
            "answer": "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. This is unsupported.",
            "sources": sample_source_docs,
            "verified_sentences": sample_verified_sentences,
            "expected_citations": 2  # All sources are included in citation list
        },
        {
            "name": "Multiple References Same Source",
            "answer": "Python is a programming language. Python was created by Guido van Rossum.",
            "sources": [sample_source_docs[0]],
            "verified_sentences": None,
            "expected_citations": 1  # Only one source
        },
        {
            "name": "Unsupported Statements",
            "answer": "Python is a programming language. This is completely false information.",
            "sources": sample_source_docs,
            "verified_sentences": None,
            "expected_citations": 2  # All sources are included in citation list
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        result = await citation_agent.generate_citations(
            scenario["answer"], 
            scenario["sources"], 
            scenario["verified_sentences"]
        )
        
        logger.info(f"Result: {result.annotated_answer}")
        logger.info(f"Citations: {len(result.citations)}")
        
        # Validate results
        assert len(result.citations) == scenario["expected_citations"]
        assert result.annotated_answer is not None
        
        # Check that citations are properly formatted
        if scenario["expected_citations"] > 0:
            assert "[" in result.annotated_answer
            assert "]" in result.annotated_answer
        
        # Check that unsupported statements are not cited
        if "unsupported" in scenario["answer"].lower() or "false" in scenario["answer"].lower():
            unsupported_parts = [part for part in scenario["answer"].split(".") if "unsupported" in part.lower() or "false" in part.lower()]
            for part in unsupported_parts:
                if part.strip():
                    assert f"{part.strip()}. [" not in result.annotated_answer
        
        logger.info(f"✅ {scenario['name']} test completed")
    
    logger.info("\n🎉 All citation agent tests completed successfully!")


if __name__ == "__main__":
    # Run the citation agent tests
    asyncio.run(run_citation_agent_tests()) 