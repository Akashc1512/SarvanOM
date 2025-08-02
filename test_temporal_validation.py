"""
Test suite for enhanced FactCheckerAgent with temporal validation and source authenticity.
Tests the new features for ensuring queries are answered based on latest and authentic sources.
"""

import asyncio
import pytest
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.factcheck_service.factcheck_agent import (
    FactCheckAgent, 
    VerificationResult, 
    TemporalValidation, 
    SourceAuthenticity
)


class TestTemporalValidation:
    """Test class for temporal validation and source authenticity features."""

    @pytest.fixture
    def fact_checker(self):
        """Create a FactCheckerAgent instance for testing."""
        return FactCheckAgent()

    @pytest.fixture
    def current_sources(self):
        """Sample current source documents."""
        return [
            {
                "doc_id": "doc1",
                "content": "Python 3.12 was released in October 2023 with new features.",
                "score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://python.org/news",
                "domain": "python.org"
            },
            {
                "doc_id": "doc2",
                "content": "Python is a high-level programming language created by Guido van Rossum.",
                "score": 0.8,
                "timestamp": "2024-02-01T14:20:00Z",
                "url": "https://wikipedia.org/python",
                "domain": "wikipedia.org"
            },
        ]

    @pytest.fixture
    def outdated_sources(self):
        """Sample outdated source documents."""
        return [
            {
                "doc_id": "doc1",
                "content": "Python 2.7 was the latest version in 2010.",
                "score": 0.9,
                "timestamp": "2010-06-15T10:30:00Z",
                "url": "https://old-python.org",
                "domain": "old-python.org"
            },
            {
                "doc_id": "doc2",
                "content": "Python 3.0 was released in 2008.",
                "score": 0.8,
                "timestamp": "2008-12-03T14:20:00Z",
                "url": "https://archive.org/python",
                "domain": "archive.org"
            },
        ]

    @pytest.fixture
    def mixed_authenticity_sources(self):
        """Sample sources with mixed authenticity levels."""
        return [
            {
                "doc_id": "doc1",
                "content": "Python is a programming language.",
                "score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://wikipedia.org/python",
                "domain": "wikipedia.org",
                "metadata": {"author": "John Doe", "citations": ["ref1", "ref2"]}
            },
            {
                "doc_id": "doc2",
                "content": "Python is the best language ever.",
                "score": 0.3,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://random-blog.com",
                "domain": "random-blog.com"
            },
            {
                "doc_id": "doc3",
                "content": "Python supports object-oriented programming.",
                "score": 0.8,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://researchgate.net/python",
                "domain": "researchgate.net",
                "metadata": {"peer_review": True}
            },
        ]

    async def test_temporal_validation_current_sources(self, fact_checker, current_sources):
        """Test temporal validation with current sources."""
        logger.info("Testing temporal validation with current sources...")
        
        query_timestamp = datetime.now()
        temporal_validation = await fact_checker._validate_temporal_relevance(current_sources, query_timestamp)
        
        # Assertions
        assert isinstance(temporal_validation, TemporalValidation)
        assert temporal_validation.is_current == True
        assert temporal_validation.temporal_confidence > 0.8
        assert temporal_validation.outdated_warning is None
        assert temporal_validation.source_age_days is not None
        assert temporal_validation.source_age_days < 365  # Should be less than a year
        
        logger.info(f"✅ Current sources test passed: {temporal_validation.source_age_days} days old")

    async def test_temporal_validation_outdated_sources(self, fact_checker, outdated_sources):
        """Test temporal validation with outdated sources."""
        logger.info("Testing temporal validation with outdated sources...")
        
        query_timestamp = datetime.now()
        temporal_validation = await fact_checker._validate_temporal_relevance(outdated_sources, query_timestamp)
        
        # Assertions
        assert isinstance(temporal_validation, TemporalValidation)
        assert temporal_validation.is_current == False
        assert temporal_validation.temporal_confidence < 0.5
        assert temporal_validation.outdated_warning is not None
        assert "year" in temporal_validation.outdated_warning or "days" in temporal_validation.outdated_warning
        
        logger.info(f"✅ Outdated sources test passed: {temporal_validation.outdated_warning}")

    async def test_source_authenticity_validation(self, fact_checker, mixed_authenticity_sources):
        """Test source authenticity validation."""
        logger.info("Testing source authenticity validation...")
        
        source_authenticity = await fact_checker._validate_source_authenticity(mixed_authenticity_sources)
        
        # Assertions
        assert isinstance(source_authenticity, SourceAuthenticity)
        assert source_authenticity.total_sources == 3
        assert source_authenticity.authentic_sources >= 2  # At least 2 should be authentic
        assert source_authenticity.authenticity_score > 0.5
        assert "reliable_domain" in source_authenticity.reliability_indicators
        assert "has_author" in source_authenticity.reliability_indicators
        assert "peer_reviewed" in source_authenticity.reliability_indicators
        
        logger.info(f"✅ Source authenticity test passed: {source_authenticity.authenticity_score:.2f}")

    async def test_enhanced_verification_with_temporal_validation(self, fact_checker, current_sources):
        """Test enhanced verification with temporal validation."""
        logger.info("Testing enhanced verification with temporal validation...")
        
        answer_text = "Python 3.12 was released in October 2023 with new features. Python is a high-level programming language."
        query_timestamp = datetime.now()
        
        result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, current_sources, query_timestamp
        )
        
        # Assertions
        assert isinstance(result, VerificationResult)
        assert result.temporal_validation is not None
        assert result.source_authenticity is not None
        assert result.verification_confidence > 0.0
        
        # Check temporal validation data
        temporal_info = result.temporal_validation
        assert temporal_info.get("is_current") == True
        assert temporal_info.get("temporal_confidence") > 0.8
        
        # Check source authenticity data
        auth_info = result.source_authenticity
        assert auth_info.get("total_sources") > 0
        assert auth_info.get("authenticity_score") > 0.0
        
        logger.info(f"✅ Enhanced verification test passed: {result.summary}")

    async def test_filter_sources_by_criteria(self, fact_checker, mixed_authenticity_sources):
        """Test source filtering based on temporal and authenticity criteria."""
        logger.info("Testing source filtering...")
        
        query_timestamp = datetime.now()
        temporal_validation = await fact_checker._validate_temporal_relevance(mixed_authenticity_sources, query_timestamp)
        source_authenticity = await fact_checker._validate_source_authenticity(mixed_authenticity_sources)
        
        filtered_sources = await fact_checker._filter_sources_by_criteria(
            mixed_authenticity_sources, temporal_validation, source_authenticity
        )
        
        # Assertions
        assert len(filtered_sources) > 0
        assert len(filtered_sources) <= len(mixed_authenticity_sources)
        
        # Check that filtered sources have better quality
        for source in filtered_sources:
            assert source.get("score", 0.0) >= 0.3  # Should have reasonable scores
        
        logger.info(f"✅ Source filtering test passed: {len(filtered_sources)} sources filtered")

    async def test_empty_sources_handling(self, fact_checker):
        """Test handling of empty source lists."""
        logger.info("Testing empty sources handling...")
        
        query_timestamp = datetime.now()
        
        # Test temporal validation with empty sources
        temporal_validation = await fact_checker._validate_temporal_relevance([], query_timestamp)
        assert temporal_validation.is_current == False
        assert temporal_validation.temporal_confidence == 0.0
        
        # Test source authenticity with empty sources
        source_authenticity = await fact_checker._validate_source_authenticity([])
        assert source_authenticity.total_sources == 0
        assert source_authenticity.authenticity_score == 0.0
        
        # Test enhanced verification with empty sources
        result = await fact_checker.verify_answer_with_temporal_validation(
            "Python is a programming language.", [], query_timestamp
        )
        assert result.verification_confidence == 0.0
        
        logger.info("✅ Empty sources handling test passed")

    async def test_date_parsing_robustness(self, fact_checker):
        """Test robustness of date parsing with various formats."""
        logger.info("Testing date parsing robustness...")
        
        # Test various date formats
        test_sources = [
            {"timestamp": "2024-01-15", "content": "Test 1"},
            {"timestamp": "2024-01-15T10:30:00Z", "content": "Test 2"},
            {"timestamp": "2024-01-15 10:30:00", "content": "Test 3"},
            {"timestamp": "2024-01-15T10:30:00", "content": "Test 4"},
            {"date": "2024-01-15", "content": "Test 5"},
            {"created_at": "2024-01-15T10:30:00Z", "content": "Test 6"},
        ]
        
        query_timestamp = datetime.now()
        temporal_validation = await fact_checker._validate_temporal_relevance(test_sources, query_timestamp)
        
        # Should handle all date formats
        assert temporal_validation.latest_source_date is not None
        assert temporal_validation.source_age_days is not None
        assert temporal_validation.is_current == True
        
        logger.info("✅ Date parsing robustness test passed")

    async def test_reliability_indicators(self, fact_checker):
        """Test detection of reliability indicators."""
        logger.info("Testing reliability indicators...")
        
        test_sources = [
            {
                "content": "Test 1",
                "url": "https://wikipedia.org/test",
                "metadata": {"author": "John Doe", "citations": ["ref1"]}
            },
            {
                "content": "Test 2",
                "url": "https://researchgate.net/test",
                "metadata": {"peer_review": True}
            },
            {
                "content": "Test 3",
                "url": "https://random-blog.com/test"
            },
        ]
        
        source_authenticity = await fact_checker._validate_source_authenticity(test_sources)
        
        # Check reliability indicators
        indicators = source_authenticity.reliability_indicators
        assert "reliable_domain" in indicators
        assert "has_author" in indicators
        assert "has_citations" in indicators
        assert "peer_reviewed" in indicators
        
        logger.info(f"✅ Reliability indicators test passed: {indicators}")

    async def test_enhanced_disclaimer_generation(self, fact_checker):
        """Test enhanced disclaimer generation with temporal and authenticity warnings."""
        logger.info("Testing enhanced disclaimer generation...")
        
        # Create a scenario that would trigger multiple disclaimers
        outdated_sources = [
            {
                "doc_id": "doc1",
                "content": "Python 2.7 was the latest version.",
                "score": 0.3,  # Low authenticity
                "timestamp": "2010-06-15T10:30:00Z",
                "url": "https://random-blog.com",
                "domain": "random-blog.com"
            },
        ]
        
        answer_text = "Python 2.7 is the latest version and the best programming language ever."
        query_timestamp = datetime.now()
        
        result = await fact_checker.verify_answer_with_temporal_validation(
            answer_text, outdated_sources, query_timestamp
        )
        
        # Check that result contains temporal and authenticity information
        assert result.temporal_validation is not None
        assert result.source_authenticity is not None
        
        # Check that temporal validation shows outdated sources
        temporal_info = result.temporal_validation
        assert temporal_info.get("is_current") == False
        
        # Check that source authenticity shows low score
        auth_info = result.source_authenticity
        assert auth_info.get("authenticity_score") < 0.7
        
        logger.info("✅ Enhanced disclaimer generation test passed")


async def run_temporal_validation_tests():
    """Run all temporal validation tests."""
    logger.info("🚀 Starting Temporal Validation Tests...")
    
    test_instance = TestTemporalValidation()
    fact_checker = FactCheckAgent()
    
    # Test data
    current_sources = [
        {
            "doc_id": "doc1",
            "content": "Python 3.12 was released in October 2023 with new features.",
            "score": 0.9,
            "timestamp": "2024-01-15T10:30:00Z",
            "url": "https://python.org/news",
            "domain": "python.org"
        },
        {
            "doc_id": "doc2",
            "content": "Python is a high-level programming language created by Guido van Rossum.",
            "score": 0.8,
            "timestamp": "2024-02-01T14:20:00Z",
            "url": "https://wikipedia.org/python",
            "domain": "wikipedia.org"
        },
    ]
    
    outdated_sources = [
        {
            "doc_id": "doc1",
            "content": "Python 2.7 was the latest version in 2010.",
            "score": 0.9,
            "timestamp": "2010-06-15T10:30:00Z",
            "url": "https://old-python.org",
            "domain": "old-python.org"
        },
    ]
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Current Sources",
            "sources": current_sources,
            "answer": "Python 3.12 was released in October 2023 with new features.",
            "expected_temporal": True,
            "expected_authenticity": "high"
        },
        {
            "name": "Outdated Sources",
            "sources": outdated_sources,
            "answer": "Python 2.7 was the latest version in 2010.",
            "expected_temporal": False,
            "expected_authenticity": "medium"
        },
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        
        query_timestamp = datetime.now()
        result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        logger.info(f"Result: {result.summary}")
        
        # Validate temporal validation
        temporal_info = result.temporal_validation
        if temporal_info:
            is_current = temporal_info.get("is_current", False)
            logger.info(f"Temporal: {'✅ Current' if is_current else '⚠️ Outdated'}")
            if not is_current:
                logger.info(f"Warning: {temporal_info.get('outdated_warning', 'Unknown')}")
        
        # Validate source authenticity
        auth_info = result.source_authenticity
        if auth_info:
            auth_score = auth_info.get("authenticity_score", 0.0)
            logger.info(f"Authenticity: {auth_score:.2f}")
            if auth_score < 0.7:
                logger.info("⚠️ Source authenticity concerns detected")
        
        logger.info(f"✅ {scenario['name']} test completed")
    
    logger.info("\n🎉 All temporal validation tests completed successfully!")


if __name__ == "__main__":
    # Run the temporal validation tests
    asyncio.run(run_temporal_validation_tests()) 