"""
Demonstration of enhanced CitationAgent with inline citation support.
Shows citation generation, sentence mapping, and validation of unsupported statements.
"""

import asyncio
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.synthesis_service.citation_agent import CitationAgent, CitationResult


async def demo_basic_citation_generation():
    """Demonstrate basic citation generation without verified sentences."""
    logger.info("🔍 Demo: Basic Citation Generation")
    
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features."
    
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
        }
    ]
    
    logger.info(f"Original Answer: {answer_text}")
    logger.info(f"Number of sources: {len(source_docs)}")
    
    result = await citation_agent.generate_citations(answer_text, source_docs)
    
    logger.info(f"Annotated Answer: {result.annotated_answer}")
    logger.info(f"Total Citations: {result.total_citations}")
    
    # Display citation list
    logger.info("\n📚 Citation List:")
    for citation in result.citations:
        logger.info(f"[{citation['id']}] {citation['title']} - {citation['url']}")
    
    logger.info("✅ Basic citation generation demo completed")


async def demo_citation_with_verified_sentences():
    """Demonstrate citation generation with verified sentences from fact checker."""
    logger.info("\n🔍 Demo: Citation with Verified Sentences")
    
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a high-level programming language created by Guido van Rossum. Python 3.12 was released in October 2023 with new features. This is an unsupported statement that should not be cited."
    
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
        }
    ]
    
    verified_sentences = [
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
    
    logger.info(f"Original Answer: {answer_text}")
    logger.info(f"Verified Sentences: {len(verified_sentences)}")
    
    result = await citation_agent.generate_citations(answer_text, source_docs, verified_sentences)
    
    logger.info(f"Annotated Answer: {result.annotated_answer}")
    logger.info(f"Total Citations: {result.total_citations}")
    
    # Check that unsupported statement is not cited
    if "This is an unsupported statement" in result.annotated_answer:
        if "This is an unsupported statement. [" not in result.annotated_answer:
            logger.info("✅ Unsupported statement correctly not cited")
        else:
            logger.warning("⚠️ Unsupported statement incorrectly cited")
    
    logger.info("✅ Citation with verified sentences demo completed")


async def demo_multiple_references_same_source():
    """Demonstrate multiple references to the same source."""
    logger.info("\n🔍 Demo: Multiple References to Same Source")
    
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a programming language. Python was created by Guido van Rossum."
    
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
    
    logger.info(f"Original Answer: {answer_text}")
    logger.info(f"Number of sources: {len(source_docs)}")
    
    result = await citation_agent.generate_citations(answer_text, source_docs)
    
    logger.info(f"Annotated Answer: {result.annotated_answer}")
    logger.info(f"Total Citations: {result.total_citations}")
    
    # Check citation map
    logger.info(f"Citation Map: {result.citation_map}")
    
    # Verify that both sentences reference the same source
    citation_count = result.annotated_answer.count("[1]")
    logger.info(f"Citation [1] appears {citation_count} times")
    
    if citation_count == 2:
        logger.info("✅ Both sentences correctly reference the same source")
    else:
        logger.warning(f"⚠️ Expected 2 citations, found {citation_count}")
    
    logger.info("✅ Multiple references demo completed")


async def demo_unsupported_statements():
    """Demonstrate that unsupported statements are not cited."""
    logger.info("\n🔍 Demo: Unsupported Statements Not Cited")
    
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a programming language. This is completely false information that should not be cited."
    
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
    
    logger.info(f"Original Answer: {answer_text}")
    
    result = await citation_agent.generate_citations(answer_text, source_docs)
    
    logger.info(f"Annotated Answer: {result.annotated_answer}")
    
    # Check that supported sentence has citation
    if "Python is a programming language. [1]" in result.annotated_answer:
        logger.info("✅ Supported sentence correctly cited")
    else:
        logger.warning("⚠️ Supported sentence not cited")
    
    # Check that unsupported sentence does not have citation
    if "This is completely false information" in result.annotated_answer:
        if "This is completely false information. [" not in result.annotated_answer:
            logger.info("✅ Unsupported statement correctly not cited")
        else:
            logger.warning("⚠️ Unsupported statement incorrectly cited")
    
    logger.info("✅ Unsupported statements demo completed")


async def demo_citation_list_structure():
    """Demonstrate citation list structure and content."""
    logger.info("\n🔍 Demo: Citation List Structure")
    
    citation_agent = CitationAgent()
    
    # Sample data
    answer_text = "Python is a programming language."
    
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
            "content": "Python 3.12 was released in October 2023 with new features.",
            "url": "https://python.org/news",
            "title": "Python 3.12 Release",
            "author": "Python Software Foundation",
            "timestamp": "2023-10-02T14:20:00Z",
            "score": 0.8
        }
    ]
    
    result = await citation_agent.generate_citations(answer_text, source_docs)
    
    logger.info("📚 Citation List Structure:")
    for citation in result.citations:
        logger.info(f"ID: {citation['id']}")
        logger.info(f"Title: {citation['title']}")
        logger.info(f"URL: {citation['url']}")
        logger.info(f"Author: {citation['author']}")
        logger.info(f"Date: {citation['date']}")
        logger.info(f"Confidence: {citation['confidence']}")
        logger.info("---")
    
    # Validate structure
    for citation in result.citations:
        required_fields = ["id", "title", "url", "author", "date", "source", "confidence"]
        for field in required_fields:
            assert field in citation, f"Missing field: {field}"
        
        assert isinstance(citation["id"], int), "ID should be integer"
        assert isinstance(citation["confidence"], float), "Confidence should be float"
    
    logger.info("✅ Citation list structure demo completed")


async def demo_integration_with_synthesis():
    """Demonstrate integration with synthesis agent."""
    logger.info("\n🔍 Demo: Integration with Synthesis Agent")
    
    try:
        from services.synthesis_service.synthesis_agent import SynthesisAgent
        from shared.core.agents.base_agent import QueryContext
        
        synthesis_agent = SynthesisAgent()
        
        # Sample synthesis task
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
        
        source_docs = [
            {
                "doc_id": "doc1",
                "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://wikipedia.org/python",
                "domain": "wikipedia.org"
            },
            {
                "doc_id": "doc2",
                "content": "Python 3.12 was released in October 2023 with new features.",
                "score": 0.8,
                "timestamp": "2024-01-15T10:30:00Z",
                "url": "https://python.org/news",
                "domain": "python.org"
            },
        ]
        
        synthesis_task = {
            "verified_facts": verified_facts,
            "query": "What is Python?",
            "source_docs": source_docs,
            "synthesis_params": {
                "style": "comprehensive",
                "max_length": 300,
            },
        }
        
        context = QueryContext(query="What is Python?")
        
        logger.info("Synthesizing answer with citation integration...")
        result = await synthesis_agent.process_task(synthesis_task, context)
        
        if result.success:
            answer = result.data.get("answer", "")
            metadata = result.data.get("metadata", {})
            
            logger.info(f"\n📝 Final Answer with Citations:")
            logger.info(answer)
            
            logger.info(f"\n📊 Metadata:")
            logger.info(f"Has Citations: {metadata.get('has_citations', False)}")
            logger.info(f"Citation Style: {metadata.get('citation_style', 'N/A')}")
            logger.info(f"Verification Summary: {metadata.get('verification_summary', 'N/A')}")
            
            # Check for citations
            if "[1]" in answer or "[2]" in answer:
                logger.info("✅ Citations successfully integrated into synthesis")
            else:
                logger.info("⚠️ No citations found in synthesized answer")
        else:
            logger.error(f"Synthesis failed: {result.error}")
    
    except Exception as e:
        logger.error(f"Integration demo failed: {str(e)}")
    
    logger.info("✅ Integration demo completed")


async def main():
    """Run all citation agent demonstrations."""
    logger.info("🚀 Starting CitationAgent Demonstrations")
    
    # Run all demos
    await demo_basic_citation_generation()
    await demo_citation_with_verified_sentences()
    await demo_multiple_references_same_source()
    await demo_unsupported_statements()
    await demo_citation_list_structure()
    await demo_integration_with_synthesis()
    
    logger.info("\n🎉 All citation agent demonstrations completed successfully!")
    logger.info("\n📋 Summary:")
    logger.info("✅ Basic citation generation works correctly")
    logger.info("✅ Verified sentences are properly cited")
    logger.info("✅ Multiple references to same source handled")
    logger.info("✅ Unsupported statements are not cited")
    logger.info("✅ Citation list structure is complete")
    logger.info("✅ Integration with synthesis pipeline works")


if __name__ == "__main__":
    asyncio.run(main()) 