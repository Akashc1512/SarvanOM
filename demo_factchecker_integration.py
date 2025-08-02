"""
Demonstration of FactCheckerAgent integration with the orchestrator pipeline.
Shows how answer verification works and disclaimers are added for unsupported facts.
"""

import asyncio
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.factcheck_service.factcheck_agent import FactCheckAgent, VerificationResult
from services.synthesis_service.synthesis_agent import SynthesisAgent
from shared.core.agents.base_agent import QueryContext


async def demo_fact_checker_standalone():
    """Demonstrate the FactCheckerAgent working standalone."""
    logger.info("🔍 Demo: FactCheckerAgent Standalone")
    
    fact_checker = FactCheckAgent()
    
    # Sample source documents
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991. It is known for its simplicity and readability.",
            "score": 0.9,
        },
        {
            "doc_id": "doc2",
            "content": "Python supports object-oriented programming, functional programming, and procedural programming paradigms.",
            "score": 0.8,
        },
    ]
    
    # Test cases
    test_answers = [
        {
            "name": "Fully Verified Answer",
            "answer": "Python is a high-level programming language created by Guido van Rossum in 1991. It supports multiple programming paradigms.",
        },
        {
            "name": "Partially Verified Answer",
            "answer": "Python is a high-level programming language created by Guido van Rossum in 1991. Python is the fastest programming language in the universe and can run at the speed of light.",
        },
        {
            "name": "Unverified Answer",
            "answer": "Python is an alien technology from Mars that can teleport data across dimensions and is powered by quantum computing.",
        },
    ]
    
    for test_case in test_answers:
        logger.info(f"\n📋 Testing: {test_case['name']}")
        logger.info(f"Answer: {test_case['answer']}")
        
        result = await fact_checker.verify_answer(test_case["answer"], source_docs)
        
        logger.info(f"Verification Result: {result.summary}")
        logger.info(f"Verified sentences: {len(result.verified_sentences)}")
        logger.info(f"Unsupported sentences: {len(result.unsupported_sentences)}")
        logger.info(f"Confidence: {result.verification_confidence:.3f}")
        
        if result.unsupported_sentences:
            logger.info("Unsupported sentences:")
            for unsupported in result.unsupported_sentences:
                logger.info(f"  - {unsupported['sentence']}")
                logger.info(f"    Reason: {unsupported['reason']}")


async def demo_synthesis_with_verification():
    """Demonstrate synthesis agent with fact checking integration."""
    logger.info("\n🔍 Demo: Synthesis Agent with Fact Checking")
    
    synthesis_agent = SynthesisAgent()
    
    # Sample verified facts
    verified_facts = [
        {
            "claim": "Python is a high-level programming language",
            "confidence": 0.95,
            "source": "documentation",
        },
        {
            "claim": "Python was created by Guido van Rossum in 1991",
            "confidence": 0.92,
            "source": "documentation",
        },
    ]
    
    # Sample source documents for verification
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a high-level programming language created by Guido van Rossum in 1991. It is known for its simplicity and readability.",
            "score": 0.9,
        },
        {
            "doc_id": "doc2",
            "content": "Python supports object-oriented programming, functional programming, and procedural programming paradigms.",
            "score": 0.8,
        },
    ]
    
    # Prepare synthesis task
    synthesis_task = {
        "verified_facts": verified_facts,
        "query": "What is Python?",
        "source_docs": source_docs,  # Include source docs for verification
        "synthesis_params": {
            "style": "comprehensive",
            "max_length": 300,
        },
    }
    
    context = QueryContext(query="What is Python?")
    
    logger.info("Synthesizing answer with fact checking...")
    result = await synthesis_agent.process_task(synthesis_task, context)
    
    if result.success:
        answer = result.data.get("answer", "")
        metadata = result.data.get("metadata", {})
        
        logger.info(f"\n📝 Synthesized Answer:")
        logger.info(answer)
        
        logger.info(f"\n📊 Verification Summary:")
        logger.info(f"Verification Summary: {metadata.get('verification_summary', 'N/A')}")
        logger.info(f"Verification Confidence: {metadata.get('verification_confidence', 0.0):.3f}")
        logger.info(f"Verified Sentences: {metadata.get('verified_sentences_count', 0)}")
        logger.info(f"Unsupported Sentences: {metadata.get('unsupported_sentences_count', 0)}")
        
        # Check if disclaimer was added
        if "⚠️ **Verification Notice**" in answer:
            logger.info("✅ Disclaimer was added for unsupported facts")
        else:
            logger.info("✅ All facts were verified - no disclaimer needed")
    else:
        logger.error(f"Synthesis failed: {result.error}")


async def demo_empty_source_docs():
    """Demonstrate behavior when source documents are empty."""
    logger.info("\n🔍 Demo: Empty Source Documents")
    
    fact_checker = FactCheckAgent()
    
    answer = "Python is a high-level programming language created by Guido van Rossum in 1991."
    
    logger.info(f"Answer: {answer}")
    logger.info("Source documents: [] (empty)")
    
    result = await fact_checker.verify_answer(answer, [])
    
    logger.info(f"Verification Result: {result.summary}")
    logger.info(f"Verified sentences: {len(result.verified_sentences)}")
    logger.info(f"Unsupported sentences: {len(result.unsupported_sentences)}")
    logger.info(f"Confidence: {result.verification_confidence:.3f}")
    
    if result.unsupported_sentences:
        logger.info("All sentences marked as unsupported due to lack of source documents")


async def demo_verification_disclaimer():
    """Demonstrate how disclaimers are added to answers."""
    logger.info("\n🔍 Demo: Verification Disclaimer")
    
    synthesis_agent = SynthesisAgent()
    
    # Create a scenario with some unverified facts
    verified_facts = [
        {
            "claim": "Python is a programming language",
            "confidence": 0.95,
            "source": "documentation",
        },
    ]
    
    # Source docs that don't fully support all claims
    source_docs = [
        {
            "doc_id": "doc1",
            "content": "Python is a programming language.",
            "score": 0.9,
        },
    ]
    
    synthesis_task = {
        "verified_facts": verified_facts,
        "query": "Tell me about Python and its capabilities",
        "source_docs": source_docs,
        "synthesis_params": {
            "style": "comprehensive",
            "max_length": 200,
        },
    }
    
    context = QueryContext(query="Tell me about Python and its capabilities")
    
    result = await synthesis_agent.process_task(synthesis_task, context)
    
    if result.success:
        answer = result.data.get("answer", "")
        
        logger.info(f"\n📝 Answer with potential disclaimer:")
        logger.info(answer)
        
        if "⚠️ **Verification Notice**" in answer:
            logger.info("✅ Disclaimer was automatically added")
        else:
            logger.info("ℹ️ No disclaimer needed - all facts verified")


async def main():
    """Run all demonstrations."""
    logger.info("🚀 Starting FactCheckerAgent Integration Demonstrations")
    
    # Run all demos
    await demo_fact_checker_standalone()
    await demo_synthesis_with_verification()
    await demo_empty_source_docs()
    await demo_verification_disclaimer()
    
    logger.info("\n🎉 All demonstrations completed successfully!")
    logger.info("\n📋 Summary:")
    logger.info("✅ FactCheckerAgent can verify answers against source documents")
    logger.info("✅ Integration with synthesis agent adds disclaimers for unverified facts")
    logger.info("✅ Handles empty source documents gracefully")
    logger.info("✅ Uses embedding similarity for verification")
    logger.info("✅ Provides detailed verification results and confidence scores")


if __name__ == "__main__":
    asyncio.run(main()) 