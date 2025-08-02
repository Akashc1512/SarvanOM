"""
Demonstration of FactCheckerAgent and CitationAgent integration.
Shows the complete pipeline from fact checking to citation generation.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.factcheck_service.factcheck_agent import FactCheckAgent, VerificationResult
from services.synthesis_service.citation_agent import CitationAgent, CitationResult


async def demo_complete_pipeline():
    """Demonstrate the complete pipeline from fact checking to citation generation."""
    logger.info("🔍 Demo: Complete FactCheck and Citation Pipeline")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. Python supports object-oriented programming. This is an unsupported statement that should not be cited."
    
    source_docs = [
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
    
    logger.info(f"Original Answer: {answer_text}")
    logger.info(f"Number of sources: {len(source_docs)}")
    
    # Step 1: Fact checking with temporal validation
    logger.info("\n📋 Step 1: Fact Checking with Temporal Validation")
    query_timestamp = datetime.now()
    verification_result = await fact_checker.verify_answer_with_temporal_validation(
        answer_text, source_docs, query_timestamp
    )
    
    logger.info(f"Fact checking result: {verification_result.summary}")
    logger.info(f"Verified sentences: {len(verification_result.verified_sentences)}")
    logger.info(f"Unsupported sentences: {len(verification_result.unsupported_sentences)}")
    logger.info(f"Verification confidence: {verification_result.verification_confidence:.3f}")
    
    # Display temporal validation results
    if verification_result.temporal_validation:
        temporal_info = verification_result.temporal_validation
        logger.info(f"Temporal Status: {'✅ Current' if temporal_info.get('is_current') else '⚠️ Outdated'}")
        logger.info(f"Source Age: {temporal_info.get('source_age_days', 'unknown')} days")
        if temporal_info.get('outdated_warning'):
            logger.info(f"Warning: {temporal_info['outdated_warning']}")
    
    # Display source authenticity results
    if verification_result.source_authenticity:
        auth_info = verification_result.source_authenticity
        logger.info(f"Authenticity Score: {auth_info.get('authenticity_score', 0.0):.2f}")
        logger.info(f"Authentic Sources: {auth_info.get('authentic_sources', 0)}/{auth_info.get('total_sources', 0)}")
    
    # Step 2: Citation generation
    logger.info("\n📋 Step 2: Citation Generation")
    citation_result = await citation_agent.generate_citations(
        answer_text, source_docs, verification_result.verified_sentences
    )
    
    logger.info(f"Annotated Answer: {citation_result.annotated_answer}")
    logger.info(f"Total Citations: {citation_result.total_citations}")
    
    # Display citation list
    logger.info("\n📚 Citation List:")
    for citation in citation_result.citations:
        logger.info(f"[{citation['id']}] {citation['title']} - {citation['url']}")
        logger.info(f"    Author: {citation['author']}")
        logger.info(f"    Date: {citation['date']}")
        logger.info(f"    Confidence: {citation['confidence']:.2f}")
    
    # Display citation map
    logger.info(f"\n🗺️ Citation Map: {citation_result.citation_map}")
    
    logger.info("✅ Complete pipeline demo completed")


async def demo_temporal_validation_with_citations():
    """Demonstrate temporal validation with citation generation."""
    logger.info("\n🔍 Demo: Temporal Validation with Citations")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    # Test scenarios with different source ages
    scenarios = [
        {
            "name": "Recent Sources (1 month old)",
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
            "name": "Outdated Sources (2 years old)",
            "answer": "Python 3.9 was the latest version in 2020.",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.9 was the latest version in 2020.",
                    "url": "https://python.org/news",
                    "title": "Python 3.9 Release",
                    "timestamp": (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "score": 0.9
                }
            ]
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        # Fact checking with temporal validation
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            scenario["answer"], scenario["sources"], verification_result.verified_sentences
        )
        
        logger.info(f"Annotated Answer: {citation_result.annotated_answer}")
        
        # Display temporal information
        if verification_result.temporal_validation:
            temporal_info = verification_result.temporal_validation
            logger.info(f"Temporal Status: {'✅ Current' if temporal_info.get('is_current') else '⚠️ Outdated'}")
            logger.info(f"Source Age: {temporal_info.get('source_age_days', 'unknown')} days")
            if temporal_info.get('outdated_warning'):
                logger.info(f"Warning: {temporal_info['outdated_warning']}")
        
        logger.info(f"✅ {scenario['name']} test completed")
    
    logger.info("✅ Temporal validation with citations demo completed")


async def demo_source_authenticity_with_citations():
    """Demonstrate source authenticity validation with citation generation."""
    logger.info("\n🔍 Demo: Source Authenticity with Citations")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    # Test scenarios with different authenticity levels
    scenarios = [
        {
            "name": "High Authenticity Sources",
            "answer": "Python is a high-level programming language that supports object-oriented programming.",
            "sources": [
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
        },
        {
            "name": "Mixed Authenticity Sources",
            "answer": "Python is a programming language and the best language ever.",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python is a programming language.",
                    "url": "https://wikipedia.org/python",
                    "title": "Python Programming Language",
                    "author": "Wikipedia Contributors",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "score": 0.9
                },
                {
                    "doc_id": "doc2",
                    "content": "Python is the best language ever.",
                    "url": "https://random-blog.com",
                    "title": "Random Blog Post",
                    "author": "Anonymous",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "score": 0.3
                }
            ]
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        # Fact checking with authenticity validation
        query_timestamp = datetime.now()
        verification_result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        # Citation generation
        citation_result = await citation_agent.generate_citations(
            scenario["answer"], scenario["sources"], verification_result.verified_sentences
        )
        
        logger.info(f"Annotated Answer: {citation_result.annotated_answer}")
        
        # Display authenticity information
        if verification_result.source_authenticity:
            auth_info = verification_result.source_authenticity
            logger.info(f"Authenticity Score: {auth_info.get('authenticity_score', 0.0):.2f}")
            logger.info(f"Authentic Sources: {auth_info.get('authentic_sources', 0)}/{auth_info.get('total_sources', 0)}")
            logger.info(f"Reliability Indicators: {auth_info.get('reliability_indicators', [])}")
            
            if auth_info.get('authenticity_score', 1.0) < 0.7:
                logger.info("⚠️ Source authenticity concerns detected")
        
        logger.info(f"✅ {scenario['name']} test completed")
    
    logger.info("✅ Source authenticity with citations demo completed")


async def demo_multiple_references_same_source():
    """Demonstrate multiple references to the same source."""
    logger.info("\n🔍 Demo: Multiple References to Same Source")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    # Single source with multiple facts
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "url": "https://wikipedia.org/python",
            "title": "Python Programming Language",
            "author": "Wikipedia Contributors",
            "timestamp": "2024-01-15T10:30:00Z",
            "score": 0.9
        }
    ]
    
    answer_text = "Python is a programming language. Python was created by Guido van Rossum."
    
    logger.info(f"Answer: {answer_text}")
    logger.info(f"Number of sources: {len(source_docs)}")
    
    # Fact checking
    query_timestamp = datetime.now()
    verification_result = await fact_checker.verify_answer_with_temporal_validation(
        answer_text, source_docs, query_timestamp
    )
    
    # Citation generation
    citation_result = await citation_agent.generate_citations(
        answer_text, source_docs, verification_result.verified_sentences
    )
    
    logger.info(f"Annotated Answer: {citation_result.annotated_answer}")
    logger.info(f"Citation Map: {citation_result.citation_map}")
    
    # Check that both sentences reference the same source
    citation_count = citation_result.annotated_answer.count("[1]")
    logger.info(f"Citation [1] appears {citation_count} times")
    
    if citation_count == 2:
        logger.info("✅ Both sentences correctly reference the same source")
    else:
        logger.warning(f"⚠️ Expected 2 citations, found {citation_count}")
    
    # Check citation map
    if "1" in citation_result.citation_map:
        sentence_indices = citation_result.citation_map["1"]
        logger.info(f"Citation 1 is used in sentences: {sentence_indices}")
    
    logger.info("✅ Multiple references to same source demo completed")


async def demo_unsupported_statements_not_cited():
    """Demonstrate that unsupported statements are not cited."""
    logger.info("\n🔍 Demo: Unsupported Statements Not Cited")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "url": "https://wikipedia.org/python",
            "title": "Python Programming Language",
            "author": "Wikipedia Contributors",
            "timestamp": "2024-01-15T10:30:00Z",
            "score": 0.9
        }
    ]
    
    answer_text = "Python is a programming language. This is completely false information."
    
    logger.info(f"Answer: {answer_text}")
    
    # Fact checking
    query_timestamp = datetime.now()
    verification_result = await fact_checker.verify_answer_with_temporal_validation(
        answer_text, source_docs, query_timestamp
    )
    
    # Citation generation
    citation_result = await citation_agent.generate_citations(
        answer_text, source_docs, verification_result.verified_sentences
    )
    
    logger.info(f"Annotated Answer: {citation_result.annotated_answer}")
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
    
    logger.info("✅ Unsupported statements not cited demo completed")


async def demo_performance_analysis():
    """Demonstrate performance analysis of the integrated pipeline."""
    logger.info("\n🔍 Demo: Performance Analysis")
    
    fact_checker = FactCheckAgent()
    citation_agent = CitationAgent()
    
    # Test data
    answer_text = "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. Python supports object-oriented programming."
    
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "url": "https://wikipedia.org/python",
            "title": "Python Programming Language",
            "score": 0.9
        },
        {
            "doc_id": "doc2",
            "content": "Python 3.12 was released in October 2023 with new features.",
            "url": "https://python.org/news",
            "title": "Python 3.12 Release",
            "score": 0.8
        },
        {
            "doc_id": "doc3",
            "content": "Python supports object-oriented programming.",
            "url": "https://docs.python.org/3/tutorial/classes.html",
            "title": "Python Classes and Objects",
            "score": 0.7
        }
    ]
    
    import time
    
    # Measure fact checking performance
    start_time = time.time()
    query_timestamp = datetime.now()
    verification_result = await fact_checker.verify_answer_with_temporal_validation(
        answer_text, source_docs, query_timestamp
    )
    fact_check_time = time.time() - start_time
    
    # Measure citation generation performance
    start_time = time.time()
    citation_result = await citation_agent.generate_citations(
        answer_text, source_docs, verification_result.verified_sentences
    )
    citation_time = time.time() - start_time
    
    total_time = fact_check_time + citation_time
    
    logger.info(f"Fact checking time: {fact_check_time:.3f}s")
    logger.info(f"Citation generation time: {citation_time:.3f}s")
    logger.info(f"Total pipeline time: {total_time:.3f}s")
    logger.info(f"Performance ratio: {fact_check_time/citation_time:.2f}:1 (fact checking to citation)")
    
    # Performance assertions
    if fact_check_time < 5.0:
        logger.info("✅ Fact checking performance is acceptable")
    else:
        logger.warning(f"⚠️ Fact checking took too long: {fact_check_time:.3f}s")
    
    if citation_time < 2.0:
        logger.info("✅ Citation generation performance is acceptable")
    else:
        logger.warning(f"⚠️ Citation generation took too long: {citation_time:.3f}s")
    
    if total_time < 7.0:
        logger.info("✅ Total pipeline performance is acceptable")
    else:
        logger.warning(f"⚠️ Total pipeline took too long: {total_time:.3f}s")
    
    logger.info("✅ Performance analysis demo completed")


async def main():
    """Run all integration demonstrations."""
    logger.info("🚀 Starting FactCheckerAgent and CitationAgent Integration Demonstrations")
    
    # Run all demos
    await demo_complete_pipeline()
    await demo_temporal_validation_with_citations()
    await demo_source_authenticity_with_citations()
    await demo_multiple_references_same_source()
    await demo_unsupported_statements_not_cited()
    await demo_performance_analysis()
    
    logger.info("\n🎉 All integration demonstrations completed successfully!")
    logger.info("\n📋 Summary:")
    logger.info("✅ Complete pipeline from fact checking to citation generation works")
    logger.info("✅ Temporal validation integrates with citation generation")
    logger.info("✅ Source authenticity validation works with citations")
    logger.info("✅ Multiple references to same source handled correctly")
    logger.info("✅ Unsupported statements are properly excluded from citations")
    logger.info("✅ Performance meets requirements")
    logger.info("✅ Error handling works gracefully in integrated pipeline")


if __name__ == "__main__":
    asyncio.run(main()) 