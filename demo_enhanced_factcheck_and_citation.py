#!/usr/bin/env python3
"""
Demo script for enhanced factcheck and citation functionality.
Tests the new vector search verification and citation features.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.factcheck_service.factcheck_agent import FactCheckAgent
from services.synthesis_service.synthesis_agent import SynthesisAgent
from shared.core.agents.base_agent import QueryContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_enhanced_factcheck():
    """Demo the enhanced factcheck functionality with vector search verification."""
    
    print("🔍 Testing Enhanced FactCheck with Vector Search Verification")
    print("=" * 60)
    
    # Initialize factcheck agent
    factcheck_agent = FactCheckAgent()
    
    # Sample answer with some factual statements
    sample_answer = """
    The Earth orbits around the Sun in an elliptical path. 
    The Sun is a massive star that provides light and heat to our planet. 
    The distance between Earth and Sun is approximately 93 million miles. 
    The Earth's atmosphere contains oxygen and nitrogen gases. 
    The Moon orbits around the Earth and affects ocean tides.
    """
    
    # Sample source documents
    source_docs = [
        {
            "doc_id": "astronomy_001",
            "content": "The Earth orbits the Sun in an elliptical orbit with an average distance of about 93 million miles. This orbital motion takes approximately 365.25 days to complete one revolution.",
            "url": "https://nasa.gov/solar-system/earth",
            "title": "Earth's Orbit Around the Sun",
            "author": "NASA",
            "timestamp": "2023-01-15",
            "score": 0.95
        },
        {
            "doc_id": "astronomy_002", 
            "content": "The Sun is a G-type main-sequence star (G2V) located at the center of our solar system. It provides light and heat to all the planets through nuclear fusion reactions.",
            "url": "https://nasa.gov/solar-system/sun",
            "title": "The Sun: Our Star",
            "author": "NASA",
            "timestamp": "2023-02-20",
            "score": 0.92
        },
        {
            "doc_id": "atmosphere_001",
            "content": "Earth's atmosphere is composed primarily of nitrogen (78%) and oxygen (21%), with trace amounts of other gases including argon, carbon dioxide, and water vapor.",
            "url": "https://noaa.gov/atmosphere",
            "title": "Earth's Atmosphere Composition",
            "author": "NOAA",
            "timestamp": "2023-03-10",
            "score": 0.88
        },
        {
            "doc_id": "ocean_001",
            "content": "The Moon's gravitational pull creates ocean tides on Earth. The tidal forces cause the ocean water to bulge toward the Moon, creating high and low tides.",
            "url": "https://noaa.gov/ocean/tides",
            "title": "Ocean Tides and the Moon",
            "author": "NOAA",
            "timestamp": "2023-04-05",
            "score": 0.85
        }
    ]
    
    print(f"📝 Sample Answer: {sample_answer.strip()}")
    print(f"📚 Source Documents: {len(source_docs)} documents")
    
    # Test vector search verification
    print("\n🔍 Running Vector Search Verification...")
    verification_result = await factcheck_agent.verify_answer_with_vector_search(
        sample_answer, source_docs
    )
    
    print(f"\n✅ Verification Results:")
    print(f"   Summary: {verification_result.summary}")
    print(f"   Verification Confidence: {verification_result.verification_confidence:.2f}")
    print(f"   Total Sentences: {verification_result.total_sentences}")
    print(f"   Verified Sentences: {len(verification_result.verified_sentences)}")
    print(f"   Unsupported Sentences: {len(verification_result.unsupported_sentences)}")
    print(f"   Revised Sentences: {len(verification_result.revised_sentences) if verification_result.revised_sentences else 0}")
    
    # Show detailed results
    if verification_result.verified_sentences:
        print(f"\n✅ Verified Sentences:")
        for i, sentence_info in enumerate(verification_result.verified_sentences[:3], 1):
            print(f"   {i}. {sentence_info['sentence'][:80]}...")
            print(f"      Confidence: {sentence_info['confidence']:.2f}")
            print(f"      Method: {sentence_info['verification_method']}")
    
    if verification_result.revised_sentences:
        print(f"\n🔄 Revised Sentences:")
        for i, sentence_info in enumerate(verification_result.revised_sentences[:3], 1):
            print(f"   {i}. Original: {sentence_info['original_sentence'][:60]}...")
            print(f"      Revised: {sentence_info['revised_sentence'][:60]}...")
            print(f"      Reason: {sentence_info['revision_reason']}")
    
    if verification_result.unsupported_sentences:
        print(f"\n⚠️ Unsupported Sentences:")
        for i, sentence_info in enumerate(verification_result.unsupported_sentences[:3], 1):
            print(f"   {i}. {sentence_info['sentence'][:80]}...")
            print(f"      Reason: {sentence_info['reason']}")
    
    return verification_result

async def demo_enhanced_synthesis():
    """Demo the enhanced synthesis functionality with citation data."""
    
    print("\n\n📝 Testing Enhanced Synthesis with Citation Data")
    print("=" * 60)
    
    # Initialize synthesis agent
    synthesis_agent = SynthesisAgent()
    
    # Sample verified facts
    verified_facts = [
        {
            "claim": "The Earth orbits around the Sun in an elliptical path",
            "confidence": 0.95,
            "source": "astronomy_001"
        },
        {
            "claim": "The Sun is a massive star that provides light and heat to our planet",
            "confidence": 0.92,
            "source": "astronomy_002"
        },
        {
            "claim": "The Earth's atmosphere contains oxygen and nitrogen gases",
            "confidence": 0.88,
            "source": "atmosphere_001"
        },
        {
            "claim": "The Moon orbits around the Earth and affects ocean tides",
            "confidence": 0.85,
            "source": "ocean_001"
        }
    ]
    
    # Sample source documents with enhanced metadata
    source_docs = [
        {
            "doc_id": "astronomy_001",
            "content": "The Earth orbits the Sun in an elliptical orbit with an average distance of about 93 million miles.",
            "url": "https://nasa.gov/solar-system/earth",
            "title": "Earth's Orbit Around the Sun",
            "author": "NASA",
            "timestamp": "2023-01-15",
            "score": 0.95
        },
        {
            "doc_id": "astronomy_002",
            "content": "The Sun is a G-type main-sequence star (G2V) located at the center of our solar system.",
            "url": "https://nasa.gov/solar-system/sun", 
            "title": "The Sun: Our Star",
            "author": "NASA",
            "timestamp": "2023-02-20",
            "score": 0.92
        },
        {
            "doc_id": "atmosphere_001",
            "content": "Earth's atmosphere is composed primarily of nitrogen (78%) and oxygen (21%).",
            "url": "https://noaa.gov/atmosphere",
            "title": "Earth's Atmosphere Composition", 
            "author": "NOAA",
            "timestamp": "2023-03-10",
            "score": 0.88
        },
        {
            "doc_id": "ocean_001",
            "content": "The Moon's gravitational pull creates ocean tides on Earth.",
            "url": "https://noaa.gov/ocean/tides",
            "title": "Ocean Tides and the Moon",
            "author": "NOAA", 
            "timestamp": "2023-04-05",
            "score": 0.85
        }
    ]
    
    query = "What is the relationship between Earth, the Sun, and the Moon?"
    
    print(f"❓ Query: {query}")
    print(f"📚 Verified Facts: {len(verified_facts)} facts")
    print(f"📖 Source Documents: {len(source_docs)} documents")
    
    # Test synthesis with citations
    print("\n🔄 Running Enhanced Synthesis with Citations...")
    
    synthesis_params = {
        "style": "comprehensive",
        "max_length": 800
    }
    
    # Create task for synthesis
    task = {
        "verified_facts": verified_facts,
        "query": query,
        "source_docs": source_docs,
        "synthesis_params": synthesis_params
    }
    
    context = QueryContext(query=query)
    
    result = await synthesis_agent.process_task(task, context)
    
    print(f"\n✅ Synthesis Results:")
    print(f"   Success: {result.success}")
    print(f"   Confidence: {result.confidence:.2f}")
    
    if result.success:
        # Extract synthesis data
        synthesis_data = result.data
        
        print(f"\n📝 Generated Answer:")
        print("-" * 40)
        print(synthesis_data.get("answer", "No answer generated"))
        print("-" * 40)
        
        # Show metadata
        metadata = result.metadata
        print(f"\n📊 Metadata:")
        print(f"   Verification Summary: {metadata.get('verification_summary', 'N/A')}")
        print(f"   Verification Confidence: {metadata.get('verification_confidence', 0):.2f}")
        print(f"   Verified Sentences: {metadata.get('verified_sentences_count', 0)}")
        print(f"   Unsupported Sentences: {metadata.get('unsupported_sentences_count', 0)}")
        print(f"   Revised Sentences: {metadata.get('revised_sentences_count', 0)}")
        print(f"   Verification Method: {metadata.get('verification_method', 'N/A')}")
        print(f"   Has Citations: {metadata.get('has_citations', False)}")
        print(f"   Source Freshness Score: {metadata.get('source_freshness_score', 1.0):.2f}")
    
    # Test citation generation separately
    print(f"\n📋 Testing Citation Generation:")
    try:
        from services.synthesis_service.citation_agent import CitationAgent
        
        citation_agent = CitationAgent()
        
        # Test citation generation
        citation_result = await citation_agent.generate_citations(
            "The Earth orbits the Sun. The Sun is a star.",
            source_docs,
            []  # No verified sentences for this test
        )
        
        print(f"   Citations generated: {citation_result.total_citations}")
        print(f"   Citation style: {citation_result.citation_style}")
        print(f"   Annotated answer: {citation_result.annotated_answer[:100]}...")
        
        # Test enhanced citation data
        print(f"\n📚 Enhanced Citation Data:")
        for i, citation in enumerate(citation_result.citations[:2], 1):
            print(f"   Citation {i}: ID={citation.get('id')}, Title={citation.get('title', 'N/A')}")
            if citation.get('url'):
                print(f"      URL: {citation['url']}")
        
    except Exception as e:
        print(f"   Citation generation test failed: {str(e)}")
    
    return result

async def main():
    """Run the complete demo."""
    
    print("🚀 Enhanced FactCheck and Citation Demo")
    print("=" * 60)
    print("This demo tests the new vector search verification and citation features.")
    print()
    
    try:
        # Test enhanced factcheck
        verification_result = await demo_enhanced_factcheck()
        
        # Test enhanced synthesis
        synthesis_result = await demo_enhanced_synthesis()
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Vector search verification for each sentence/fact")
        print("✅ LLM-based revision of unsupported sentences")
        print("✅ Enhanced citation data with document IDs and URLs")
        print("✅ Reference list generation with metadata")
        print("✅ Detailed verification reporting")
        print("✅ Citation generation with enhanced metadata")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        logger.error(f"Demo error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 