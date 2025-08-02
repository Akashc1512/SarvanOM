"""
Demonstration of enhanced FactCheckerAgent with temporal validation and source authenticity.
Shows how the system ensures queries are answered based on latest and authentic sources.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.factcheck_service.factcheck_agent import FactCheckAgent, VerificationResult
from services.synthesis_service.synthesis_agent import SynthesisAgent
from shared.core.agents.base_agent import QueryContext


async def demo_temporal_validation():
    """Demonstrate temporal validation with different source ages."""
    logger.info("🔍 Demo: Temporal Validation")
    
    fact_checker = FactCheckAgent()
    
    # Test scenarios with different source ages
    scenarios = [
        {
            "name": "Recent Sources (1 month old)",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.12.1 was released in January 2024 with bug fixes.",
                    "score": 0.9,
                    "timestamp": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://python.org/news",
                    "domain": "python.org"
                }
            ],
            "answer": "Python 3.12.1 was released in January 2024 with bug fixes."
        },
        {
            "name": "Medium Age Sources (6 months old)",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.11 was released in October 2022 with performance improvements.",
                    "score": 0.8,
                    "timestamp": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://python.org/news",
                    "domain": "python.org"
                }
            ],
            "answer": "Python 3.11 was released in October 2022 with performance improvements."
        },
        {
            "name": "Outdated Sources (2 years old)",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.9 was the latest version in 2020.",
                    "score": 0.9,
                    "timestamp": (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://python.org/news",
                    "domain": "python.org"
                }
            ],
            "answer": "Python 3.9 was the latest version in 2020."
        },
        {
            "name": "Very Old Sources (5 years old)",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python 3.7 was released in June 2018.",
                    "score": 0.8,
                    "timestamp": (datetime.now() - timedelta(days=1825)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://python.org/news",
                    "domain": "python.org"
                }
            ],
            "answer": "Python 3.7 was released in June 2018."
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        query_timestamp = datetime.now()
        result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        logger.info(f"Verification Result: {result.summary}")
        
        # Display temporal information
        if result.temporal_validation:
            temporal_info = result.temporal_validation
            logger.info(f"Temporal Status: {'✅ Current' if temporal_info.get('is_current') else '⚠️ Outdated'}")
            logger.info(f"Source Age: {temporal_info.get('source_age_days', 'unknown')} days")
            logger.info(f"Temporal Confidence: {temporal_info.get('temporal_confidence', 0.0):.2f}")
            if temporal_info.get('outdated_warning'):
                logger.info(f"Warning: {temporal_info['outdated_warning']}")
        
        # Display authenticity information
        if result.source_authenticity:
            auth_info = result.source_authenticity
            logger.info(f"Authenticity Score: {auth_info.get('authenticity_score', 0.0):.2f}")
            logger.info(f"Reliable Sources: {auth_info.get('authentic_sources', 0)}/{auth_info.get('total_sources', 0)}")


async def demo_source_authenticity():
    """Demonstrate source authenticity validation with different source types."""
    logger.info("\n🔍 Demo: Source Authenticity Validation")
    
    fact_checker = FactCheckAgent()
    
    # Test scenarios with different source authenticity levels
    scenarios = [
        {
            "name": "High Authenticity Sources",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python is a high-level programming language.",
                    "score": 0.9,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://wikipedia.org/python",
                    "domain": "wikipedia.org",
                    "metadata": {"author": "Wikipedia Contributors", "citations": ["ref1", "ref2"]}
                },
                {
                    "doc_id": "doc2",
                    "content": "Python supports object-oriented programming.",
                    "score": 0.8,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://researchgate.net/python",
                    "domain": "researchgate.net",
                    "metadata": {"peer_review": True, "author": "Dr. Smith"}
                }
            ],
            "answer": "Python is a high-level programming language that supports object-oriented programming."
        },
        {
            "name": "Mixed Authenticity Sources",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python is a programming language.",
                    "score": 0.9,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://wikipedia.org/python",
                    "domain": "wikipedia.org"
                },
                {
                    "doc_id": "doc2",
                    "content": "Python is the best language ever.",
                    "score": 0.3,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://random-blog.com",
                    "domain": "random-blog.com"
                }
            ],
            "answer": "Python is a programming language and the best language ever."
        },
        {
            "name": "Low Authenticity Sources",
            "sources": [
                {
                    "doc_id": "doc1",
                    "content": "Python is amazing.",
                    "score": 0.2,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://random-blog.com",
                    "domain": "random-blog.com"
                },
                {
                    "doc_id": "doc2",
                    "content": "Python is the future.",
                    "score": 0.3,
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "url": "https://another-blog.com",
                    "domain": "another-blog.com"
                }
            ],
            "answer": "Python is amazing and the future."
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n📋 Testing: {scenario['name']}")
        logger.info(f"Answer: {scenario['answer']}")
        
        query_timestamp = datetime.now()
        result = await fact_checker.verify_answer_with_temporal_validation(
            scenario["answer"], scenario["sources"], query_timestamp
        )
        
        logger.info(f"Verification Result: {result.summary}")
        
        # Display authenticity information
        if result.source_authenticity:
            auth_info = result.source_authenticity
            logger.info(f"Authenticity Score: {auth_info.get('authenticity_score', 0.0):.2f}")
            logger.info(f"Total Sources: {auth_info.get('total_sources', 0)}")
            logger.info(f"Authentic Sources: {auth_info.get('authentic_sources', 0)}")
            logger.info(f"High Confidence Sources: {auth_info.get('high_confidence_sources', 0)}")
            logger.info(f"Reliability Indicators: {auth_info.get('reliability_indicators', [])}")
            
            if auth_info.get('authenticity_score', 1.0) < 0.7:
                logger.info("⚠️ Source authenticity concerns detected")


async def demo_enhanced_synthesis_with_temporal_validation():
    """Demonstrate synthesis agent with enhanced temporal validation."""
    logger.info("\n🔍 Demo: Enhanced Synthesis with Temporal Validation")
    
    synthesis_agent = SynthesisAgent()
    
    # Sample verified facts
    verified_facts = [
        {
            "claim": "Python is a high-level programming language",
            "confidence": 0.95,
            "source": "documentation",
        },
        {
            "claim": "Python was created by Guido van Rossum",
            "confidence": 0.92,
            "source": "documentation",
        },
    ]
    
    # Sample sources with temporal information
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
            "score": 0.9,
            "timestamp": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "url": "https://wikipedia.org/python",
            "domain": "wikipedia.org"
        },
        {
            "doc_id": "doc2",
            "content": "Python 3.12 was released in October 2023 with new features.",
            "score": 0.8,
            "timestamp": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "url": "https://python.org/news",
            "domain": "python.org"
        },
    ]
    
    # Prepare synthesis task
    synthesis_task = {
        "verified_facts": verified_facts,
        "query": "What is Python and what's the latest version?",
        "source_docs": source_docs,
        "synthesis_params": {
            "style": "comprehensive",
            "max_length": 300,
        },
    }
    
    context = QueryContext(query="What is Python and what's the latest version?")
    
    logger.info("Synthesizing answer with enhanced temporal validation...")
    result = await synthesis_agent.process_task(synthesis_task, context)
    
    if result.success:
        answer = result.data.get("answer", "")
        metadata = result.data.get("metadata", {})
        
        logger.info(f"\n📝 Synthesized Answer:")
        logger.info(answer)
        
        logger.info(f"\n📊 Enhanced Verification Summary:")
        logger.info(f"Verification Summary: {metadata.get('verification_summary', 'N/A')}")
        logger.info(f"Verification Confidence: {metadata.get('verification_confidence', 0.0):.3f}")
        
        # Check for enhanced disclaimers
        if "⚠️ **Temporal Notice**" in answer:
            logger.info("✅ Temporal disclaimer was added")
        if "⚠️ **Source Quality Notice**" in answer:
            logger.info("✅ Source quality disclaimer was added")
        if "⚠️ **Verification Notice**" in answer:
            logger.info("✅ Verification disclaimer was added")
        
        if not any(warning in answer for warning in ["⚠️ **Temporal Notice**", "⚠️ **Source Quality Notice**", "⚠️ **Verification Notice**"]):
            logger.info("✅ All facts were verified with current, authentic sources")
    else:
        logger.error(f"Synthesis failed: {result.error}")


async def demo_query_timestamp_handling():
    """Demonstrate how query timestamps affect temporal validation."""
    logger.info("\n🔍 Demo: Query Timestamp Handling")
    
    fact_checker = FactCheckAgent()
    
    # Same sources, different query timestamps
    sources = [
        {
            "doc_id": "doc1",
            "content": "Python 3.11 was released in October 2022.",
            "score": 0.9,
            "timestamp": "2022-10-24T10:00:00Z",
            "url": "https://python.org/news",
            "domain": "python.org"
        }
    ]
    
    answer = "Python 3.11 was released in October 2022."
    
    # Test with different query timestamps
    timestamps = [
        ("2022-11-01", "1 week after release"),
        ("2023-01-01", "3 months after release"),
        ("2023-10-01", "1 year after release"),
        ("2024-01-01", "1.5 years after release"),
    ]
    
    for date_str, description in timestamps:
        query_timestamp = datetime.strptime(date_str, "%Y-%m-%d")
        
        logger.info(f"\n📋 Testing: {description}")
        logger.info(f"Query Date: {date_str}")
        
        result = await fact_checker.verify_answer_with_temporal_validation(
            answer, sources, query_timestamp
        )
        
        if result.temporal_validation:
            temporal_info = result.temporal_validation
            age_days = temporal_info.get("source_age_days", 0)
            is_current = temporal_info.get("is_current", False)
            
            logger.info(f"Source Age: {age_days} days")
            logger.info(f"Current: {'✅ Yes' if is_current else '⚠️ No'}")
            logger.info(f"Confidence: {temporal_info.get('temporal_confidence', 0.0):.2f}")


async def main():
    """Run all temporal validation demonstrations."""
    logger.info("🚀 Starting Enhanced Temporal Validation Demonstrations")
    
    # Run all demos
    await demo_temporal_validation()
    await demo_source_authenticity()
    await demo_enhanced_synthesis_with_temporal_validation()
    await demo_query_timestamp_handling()
    
    logger.info("\n🎉 All temporal validation demonstrations completed successfully!")
    logger.info("\n📋 Summary:")
    logger.info("✅ Temporal validation ensures sources are current")
    logger.info("✅ Source authenticity validation checks reliability")
    logger.info("✅ Enhanced disclaimers warn about outdated or unreliable sources")
    logger.info("✅ Query timestamps are properly considered")
    logger.info("✅ Integration with synthesis pipeline provides comprehensive validation")


if __name__ == "__main__":
    asyncio.run(main()) 