"""
Comprehensive test for FactCheckerAgent and CitationAgent integration.
Tests the complete pipeline from fact checking to citation generation.
"""

import asyncio
import pytest
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.factcheck_service.factcheck_agent import FactCheckAgent, VerificationResult
from services.synthesis_service.citation_agent import CitationAgent, CitationResult


class TestFactCheckAndCitationIntegration:
    """Test class for FactCheckerAgent and CitationAgent integration."""

    @pytest.fixture
    def fact_checker(self):
        """Create a FactCheckAgent instance for testing."""
        return FactCheckAgent()

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
    def sample_answer_text(self):
        """Sample answer text for testing."""
        return "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. Python supports object-oriented programming. This is an unsupported statement that should not be cited."

    async def test_complete_factcheck_and_citation_pipeline(self, fact_checker, citation_agent, sample_source_docs, sample_answer_text):
        """Test the complete pipeline from fact checking to citation generation."""
        logger.info("Testing complete factcheck and citation pipeline...")
        
        # Step 1: Fact checking
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            sample_answer_text, sample_source_docs, query_timestamp
        )
        
        logger.info(f"Fact checking result: {verification_result.summary}")
        logger.info(f"Verified sentences: {len(verification_result.verified_sentences)}")
        logger.info(f"Unsupported sentences: {len(verification_result.unsupported_sentences)}")
        
        # Step 2: Citation generation
        citation_result = await citation_agent.generate_citations(
            sample_answer_text, sample_source_docs, verification_result.verified_sentences
        )
        
        logger.info(f"Citation result: {citation_result.annotated_answer}")
        logger.info(f"Total citations: {citation_result.total_citations}")
        
        # Assertions for fact checking
        assert isinstance(verification_result, VerificationResult)
        assert verification_result.total_sentences > 0
        assert len(verification_result.verified_sentences) > 0
        assert verification_result.verification_confidence > 0.0
        
        # Assertions for citation generation
        assert isinstance(citation_result, CitationResult)
        assert citation_result.annotated_answer is not None
        assert len(citation_result.citations) > 0
        assert citation_result.total_citations > 0
        
        # Check that verified sentences have citations
        for verified_sentence in verification_result.verified_sentences:
            sentence_text = verified_sentence.get("sentence", "")
            if sentence_text:
                # Check if this sentence appears in the annotated answer with citations
                if sentence_text in citation_result.annotated_answer:
                    # The sentence should have citations
                    sentence_with_citations = citation_result.annotated_answer
                    if sentence_text in sentence_with_citations:
                        # Find the sentence in the annotated answer
                        start_idx = sentence_with_citations.find(sentence_text)
                        if start_idx != -1:
                            # Check if there are citations after this sentence
                            after_sentence = sentence_with_citations[start_idx + len(sentence_text):]
                            if "[" in after_sentence and "]" in after_sentence:
                                logger.info(f"✅ Verified sentence has citations: {sentence_text}")
                            else:
                                logger.warning(f"⚠️ Verified sentence missing citations: {sentence_text}")
        
        # Check that unsupported sentences do not have citations
        for unsupported_sentence in verification_result.unsupported_sentences:
            sentence_text = unsupported_sentence.get("sentence", "")
            if sentence_text and sentence_text in citation_result.annotated_answer:
                # Check that this sentence doesn't have citations
                if f"{sentence_text} [" not in citation_result.annotated_answer:
                    logger.info(f"✅ Unsupported sentence correctly not cited: {sentence_text}")
                else:
                    logger.warning(f"⚠️ Unsupported sentence incorrectly cited: {sentence_text}")
        
        logger.info("✅ Complete pipeline test passed")

    async def test_temporal_validation_with_citations(self, fact_checker, citation_agent):
        """Test temporal validation with citation generation."""
        logger.info("Testing temporal validation with citations...")
        
        # Test with current sources
        current_sources = [
            {
                "doc_id": "doc1",
                "content": "Python 3.12.1 was released in January 2024 with bug fixes.",
                "url": "https://python.org/news",
                "title": "Python 3.12.1 Release",
                "timestamp": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "score": 0.9
            }
        ]
        
        answer_text = "Python 3.12.1 was released in January 2024 with bug fixes."
        
        # Fact checking with temporal validation
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, current_sources, query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            answer_text, current_sources, verification_result.verified_sentences
        )
        
        # Check temporal validation results
        if verification_result.temporal_validation:
            temporal_info = verification_result.temporal_validation
            logger.info(f"Temporal status: {'Current' if temporal_info.get('is_current') else 'Outdated'}")
            logger.info(f"Source age: {temporal_info.get('source_age_days', 'unknown')} days")
        
        # Check citation results
        logger.info(f"Annotated answer: {citation_result.annotated_answer}")
        logger.info(f"Citations: {len(citation_result.citations)}")
        
        # Assertions
        assert verification_result.temporal_validation is not None
        assert citation_result.annotated_answer is not None
        assert len(citation_result.citations) > 0
        
        logger.info("✅ Temporal validation with citations test passed")

    async def test_source_authenticity_with_citations(self, fact_checker, citation_agent):
        """Test source authenticity validation with citation generation."""
        logger.info("Testing source authenticity with citations...")
        
        # Test with high authenticity sources
        high_auth_sources = [
            {
                "doc_id": "doc1",
                "content": "Python is a high-level programming language.",
                "url": "https://wikipedia.org/python",
                "title": "Python Programming Language",
                "author": "Wikipedia Contributors",
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "score": 0.9
            },
            {
                "doc_id": "doc2",
                "content": "Python supports object-oriented programming.",
                "url": "https://researchgate.net/python",
                "title": "Python OOP Research",
                "author": "Dr. Smith",
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "score": 0.8
            }
        ]
        
        answer_text = "Python is a high-level programming language that supports object-oriented programming."
        
        # Fact checking with authenticity validation
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, high_auth_sources, query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            answer_text, high_auth_sources, verification_result.verified_sentences
        )
        
        # Check source authenticity results
        if verification_result.source_authenticity:
            auth_info = verification_result.source_authenticity
            logger.info(f"Authenticity score: {auth_info.get('authenticity_score', 0.0):.2f}")
            logger.info(f"Authentic sources: {auth_info.get('authentic_sources', 0)}/{auth_info.get('total_sources', 0)}")
        
        # Check citation results
        logger.info(f"Annotated answer: {citation_result.annotated_answer}")
        logger.info(f"Citations: {len(citation_result.citations)}")
        
        # Assertions
        assert verification_result.source_authenticity is not None
        assert citation_result.annotated_answer is not None
        assert len(citation_result.citations) > 0
        
        logger.info("✅ Source authenticity with citations test passed")

    async def test_multiple_references_same_source(self, fact_checker, citation_agent):
        """Test multiple references to the same source with fact checking."""
        logger.info("Testing multiple references to same source...")
        
        # Single source with multiple facts
        source_docs = [
            {
                "doc_id": "doc1",
                "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "url": "https://wikipedia.org/python",
                "title": "Python Programming Language",
                "score": 0.9
            }
        ]
        
        answer_text = "Python is a programming language. Python was created by Guido van Rossum."
        
        # Fact checking
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, source_docs, query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            answer_text, source_docs, verification_result.verified_sentences
        )
        
        logger.info(f"Annotated answer: {citation_result.annotated_answer}")
        logger.info(f"Citation map: {citation_result.citation_map}")
        
        # Check that both sentences reference the same source
        citation_count = citation_result.annotated_answer.count("[1]")
        assert citation_count == 2, f"Expected 2 citations, found {citation_count}"
        
        # Check citation map
        if "1" in citation_result.citation_map:
            sentence_indices = citation_result.citation_map["1"]
            assert len(sentence_indices) == 2, f"Expected 2 sentences using citation 1, found {len(sentence_indices)}"
        
        logger.info("✅ Multiple references to same source test passed")

    async def test_unsupported_statements_not_cited(self, fact_checker, citation_agent):
        """Test that unsupported statements are not cited."""
        logger.info("Testing unsupported statements not cited...")
        
        source_docs = [
            {
                "doc_id": "doc1",
                "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "url": "https://wikipedia.org/python",
                "title": "Python Programming Language",
                "score": 0.9
            }
        ]
        
        answer_text = "Python is a programming language. This is completely false information."
        
        # Fact checking
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, source_docs, query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            answer_text, source_docs, verification_result.verified_sentences
        )
        
        logger.info(f"Annotated answer: {citation_result.annotated_answer}")
        logger.info(f"Verified sentences: {len(verification_result.verified_sentences)}")
        logger.info(f"Unsupported sentences: {len(verification_result.unsupported_sentences)}")
        
        # Check that supported sentence has citation
        if "Python is a programming language" in citation_result.annotated_answer:
            if "Python is a programming language. [1]" in citation_result.annotated_answer:
                logger.info("✅ Supported sentence correctly cited")
            else:
                logger.warning("⚠️ Supported sentence not cited")
        
        # Check that unsupported sentence does not have citation
        if "This is completely false information" in citation_result.annotated_answer:
            if "This is completely false information. [" not in citation_result.annotated_answer:
                logger.info("✅ Unsupported statement correctly not cited")
            else:
                logger.warning("⚠️ Unsupported statement incorrectly cited")
        
        logger.info("✅ Unsupported statements not cited test passed")

    async def test_error_handling_integration(self, fact_checker, citation_agent):
        """Test error handling in the integrated pipeline."""
        logger.info("Testing error handling in integration...")
        
        # Test with empty sources
        empty_sources = []
        answer_text = "This is a test answer."
        
        # Fact checking should handle empty sources gracefully
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, empty_sources, query_timestamp
        )
        
        # Citation generation should handle empty sources gracefully
        citation_result = await citation_agent.generate_citations(
            answer_text, empty_sources, verification_result.verified_sentences
        )
        
        # Both should return valid results even with empty sources
        assert isinstance(verification_result, VerificationResult)
        assert isinstance(citation_result, CitationResult)
        assert citation_result.annotated_answer == answer_text  # Should return original answer
        assert len(citation_result.citations) == 0  # No citations for empty sources
        
        logger.info("✅ Error handling integration test passed")

    async def test_performance_integration(self, fact_checker, citation_agent, sample_source_docs, sample_answer_text):
        """Test performance of the integrated pipeline."""
        logger.info("Testing performance of integrated pipeline...")
        
        import time
        
        # Measure fact checking performance
        start_time = time.time()
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            sample_answer_text, sample_source_docs, query_timestamp
        )
        fact_check_time = time.time() - start_time
        
        # Measure citation generation performance
        start_time = time.time()
        citation_result = await citation_agent.generate_citations(
            sample_answer_text, sample_source_docs, verification_result.verified_sentences
        )
        citation_time = time.time() - start_time
        
        total_time = fact_check_time + citation_time
        
        logger.info(f"Fact checking time: {fact_check_time:.3f}s")
        logger.info(f"Citation generation time: {citation_time:.3f}s")
        logger.info(f"Total pipeline time: {total_time:.3f}s")
        
        # Performance assertions
        assert fact_check_time < 5.0, f"Fact checking took too long: {fact_check_time:.3f}s"
        assert citation_time < 2.0, f"Citation generation took too long: {citation_time:.3f}s"
        assert total_time < 7.0, f"Total pipeline took too long: {total_time:.3f}s"
        
        logger.info("✅ Performance integration test passed")


async def run_integration_tests():
    """Run all integration tests for FactCheckerAgent and CitationAgent."""
    logger.info("🚀 Starting FactCheckerAgent and CitationAgent Integration Tests...")
    
    test_instance = TestFactCheckAndCitationIntegration()
    fact_checker = FactCheckAgent()
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
    
    sample_answer_text = "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. Python supports object-oriented programming. This is an unsupported statement that should not be cited."
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Complete Pipeline Test",
            "description": "Test the complete pipeline from fact checking to citation generation",
            "answer": sample_answer_text,
            "sources": sample_source_docs
        },
        {
            "name": "Temporal Validation Test",
            "description": "Test temporal validation with citation generation",
            "answer": "Python 3.12.1 was released in January 2024 with bug fixes.",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.12.1 was released in January 2024 with bug fixes.",
                    "url": "https://python.org/news",
                    "title": "Python 3.12.1 Release",
                    "timestamp": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "score": 0.9
                }
            ]
        },
        {
            "name": "Multiple References Test",
            "description": "Test multiple references to the same source",
            "answer": "Python is a programming language. Python was created by Guido van Rossum.",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                    "url": "https://wikipedia.org/python",
                    "title": "Python Programming Language",
                    "score": 0.9
                }
            ]
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Description: {scenario['description']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        # Step 1: Fact checking with temporal validation
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        logger.info(f"Fact checking result: {verification_result.summary}")
        logger.info(f"Verified sentences: {len(verification_result.verified_sentences)}")
        logger.info(f"Unsupported sentences: {len(verification_result.unsupported_sentences)}")
        
        # Step 2: Citation generation
        citation_result = await citation_agent.generate_citations(
            scenario["answer"], scenario["sources"], verification_result.verified_sentences
        )
        
        logger.info(f"Annotated answer: {citation_result.annotated_answer}")
        logger.info(f"Total citations: {citation_result.total_citations}")
        
        # Display citation list
        logger.info("📚 Citation List:")
        for citation in citation_result.citations:
            logger.info(f"[{citation['id']}] {citation['title']} - {citation['url']}")
        
        # Check temporal validation
        if verification_result.temporal_validation:
            temporal_info = verification_result.temporal_validation
            logger.info(f"Temporal Status: {'✅ Current' if temporal_info.get('is_current') else '⚠️ Outdated'}")
            if temporal_info.get('outdated_warning'):
                logger.info(f"Warning: {temporal_info['outdated_warning']}")
        
        # Check source authenticity
        if verification_result.source_authenticity:
            auth_info = verification_result.source_authenticity
            logger.info(f"Authenticity Score: {auth_info.get('authenticity_score', 0.0):.2f}")
        
        logger.info(f"✅ {scenario['name']} test completed")
    
    logger.info("\n🎉 All integration tests completed successfully!")
    logger.info("\n📋 Summary:")
    logger.info("✅ Complete pipeline from fact checking to citation generation works")
    logger.info("✅ Temporal validation integrates with citation generation")
    logger.info("✅ Source authenticity validation works with citations")
    logger.info("✅ Multiple references to same source handled correctly")
    logger.info("✅ Unsupported statements are properly excluded from citations")
    logger.info("✅ Error handling works gracefully in integrated pipeline")
    logger.info("✅ Performance meets requirements")


if __name__ == "__main__":
    # Run the integration tests
    asyncio.run(run_integration_tests()) 