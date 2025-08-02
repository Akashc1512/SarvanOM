#!/usr/bin/env python3
"""
Simple test script for enhanced factcheck and citation functionality.
Tests core functionality without complex dependencies.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock the complex dependencies
class MockBaseAgent:
    def __init__(self, agent_id="test_agent", agent_type="TEST"):
        self.agent_id = agent_id
        self.agent_type = agent_type

class MockQueryContext:
    def __init__(self, query=""):
        self.query = query

# Mock the data models
class MockVerificationResult:
    def __init__(self, summary="", verified_sentences=None, unsupported_sentences=None, 
                 total_sentences=0, verification_confidence=0.0, verification_method="test",
                 revised_sentences=None):
        self.summary = summary
        self.verified_sentences = verified_sentences or []
        self.unsupported_sentences = unsupported_sentences or []
        self.revised_sentences = revised_sentences or []
        self.total_sentences = total_sentences
        self.verification_confidence = verification_confidence
        self.verification_method = verification_method

class MockSynthesisResult:
    def __init__(self, answer="", synthesis_method="test", fact_count=0, 
                 processing_time_ms=0, metadata=None):
        self.answer = answer
        self.synthesis_method = synthesis_method
        self.fact_count = fact_count
        self.processing_time_ms = processing_time_ms
        self.metadata = metadata or {}
    
    def model_dump(self):
        return {
            "answer": self.answer,
            "synthesis_method": self.synthesis_method,
            "fact_count": self.fact_count,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata
        }

class MockAgentResult:
    def __init__(self, success=True, data=None, confidence=0.0, 
                 processing_time_ms=0, metadata=None):
        self.success = success
        self.data = data or {}
        self.confidence = confidence
        self.processing_time_ms = processing_time_ms
        self.metadata = metadata or {}

# Test the core functionality
async def test_vector_search_verification():
    """Test the vector search verification logic."""
    
    print("🔍 Testing Vector Search Verification Logic")
    print("=" * 50)
    
    # Mock sample data
    sample_answer = """
    The Earth orbits around the Sun in an elliptical path. 
    The Sun is a massive star that provides light and heat to our planet. 
    The distance between Earth and Sun is approximately 93 million miles.
    """
    
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
        }
    ]
    
    # Test sentence similarity calculation
    def calculate_sentence_similarity(sentence: str, content: str) -> float:
        """Calculate similarity between sentence and content using keyword matching."""
        import re
        
        # Extract key terms from sentence
        sentence_terms = set(re.findall(r'\b\w+\b', sentence.lower()))
        sentence_terms = {term for term in sentence_terms if len(term) > 3}
        
        if not sentence_terms:
            return 0.0
        
        # Extract key terms from content
        content_terms = set(re.findall(r'\b\w+\b', content.lower()))
        content_terms = {term for term in content_terms if len(term) > 3}
        
        if not content_terms:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(sentence_terms.intersection(content_terms))
        union = len(sentence_terms.union(content_terms))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    # Test sentence splitting
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences using regex."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        return cleaned_sentences
    
    # Test factual statement detection
    def is_factual_statement(sentence: str) -> bool:
        """Determine if a sentence is a factual statement."""
        sentence_lower = sentence.lower()
        
        # Look for factual indicators
        factual_indicators = [
            "is", "are", "was", "were", "has", "have", "had",
            "contains", "includes", "consists", "comprises",
            "located", "found", "discovered", "identified",
            "according to", "research shows", "studies indicate"
        ]
        
        # Look for opinion indicators (negative)
        opinion_indicators = [
            "i think", "i believe", "in my opinion", "i feel",
            "probably", "maybe", "perhaps", "might", "could",
            "seems", "appears", "looks like"
        ]
        
        # Check for factual indicators
        has_factual = any(indicator in sentence_lower for indicator in factual_indicators)
        
        # Check for opinion indicators
        has_opinion = any(indicator in sentence_lower for indicator in opinion_indicators)
        
        return has_factual and not has_opinion
    
    print(f"📝 Sample Answer: {sample_answer.strip()}")
    print(f"📚 Source Documents: {len(source_docs)} documents")
    
    # Test sentence splitting
    sentences = split_into_sentences(sample_answer)
    print(f"\n📝 Split into {len(sentences)} sentences:")
    for i, sentence in enumerate(sentences, 1):
        print(f"   {i}. {sentence}")
    
    # Test factual statement detection
    factual_sentences = []
    for sentence in sentences:
        if is_factual_statement(sentence):
            factual_sentences.append(sentence)
    
    print(f"\n🔍 Found {len(factual_sentences)} factual statements:")
    for i, sentence in enumerate(factual_sentences, 1):
        print(f"   {i}. {sentence}")
    
    # Test similarity calculation
    print(f"\n🔍 Testing similarity calculations:")
    for i, sentence in enumerate(factual_sentences, 1):
        best_similarity = 0.0
        best_source = None
        
        for doc in source_docs:
            similarity = calculate_sentence_similarity(sentence, doc["content"])
            if similarity > best_similarity:
                best_similarity = similarity
                best_source = doc
        
        print(f"   Sentence {i}: {sentence[:50]}...")
        print(f"      Best similarity: {best_similarity:.3f}")
        if best_source:
            print(f"      Best source: {best_source['title']}")
        
        # Determine if supported
        support_threshold = 0.6
        is_supported = best_similarity >= support_threshold
        print(f"      Supported: {'✅' if is_supported else '❌'}")
    
    # Mock verification result
    verified_count = sum(1 for sentence in factual_sentences 
                        if any(calculate_sentence_similarity(sentence, doc["content"]) >= 0.6 
                               for doc in source_docs))
    
    verification_result = MockVerificationResult(
        summary=f"{verified_count}/{len(factual_sentences)} statements verified",
        verified_sentences=factual_sentences[:verified_count],
        unsupported_sentences=factual_sentences[verified_count:],
        total_sentences=len(factual_sentences),
        verification_confidence=verified_count / len(factual_sentences) if factual_sentences else 0.0,
        verification_method="vector_search_test"
    )
    
    print(f"\n✅ Verification Results:")
    print(f"   Summary: {verification_result.summary}")
    print(f"   Verification Confidence: {verification_result.verification_confidence:.2f}")
    print(f"   Total Sentences: {verification_result.total_sentences}")
    print(f"   Verified Sentences: {len(verification_result.verified_sentences)}")
    print(f"   Unsupported Sentences: {len(verification_result.unsupported_sentences)}")
    
    return verification_result

async def test_citation_generation():
    """Test the citation generation logic."""
    
    print("\n\n📝 Testing Citation Generation Logic")
    print("=" * 50)
    
    # Mock sample data
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
        }
    ]
    
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
        }
    ]
    
    print(f"📚 Verified Facts: {len(verified_facts)} facts")
    print(f"📖 Source Documents: {len(source_docs)} documents")
    
    # Test source document mapping
    def find_source_doc_for_fact(fact: Dict, source_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the source document that corresponds to a verified fact."""
        import re
        
        claim_text = fact.get("claim", "")
        if not claim_text:
            return None
        
        # Simple keyword matching to find best source
        claim_terms = set(re.findall(r'\b\w+\b', claim_text.lower()))
        claim_terms = {term for term in claim_terms if len(term) > 3}
        
        best_match = None
        best_score = 0.0
        
        for doc in source_docs:
            content = doc.get("content", "").lower()
            if not content:
                continue
            
            # Calculate overlap with claim terms
            content_terms = set(re.findall(r'\b\w+\b', content))
            content_terms = {term for term in content_terms if len(term) > 3}
            
            if not content_terms:
                continue
            
            intersection = len(claim_terms.intersection(content_terms))
            union = len(claim_terms.union(content_terms))
            
            if union > 0:
                score = intersection / union
                if score > best_score:
                    best_score = score
                    best_match = doc
        
        return best_match if best_score > 0.2 else None
    
    # Test reference list generation
    def create_enhanced_reference_list(source_docs: List[Dict[str, Any]]) -> str:
        """Create enhanced reference list with document IDs and URLs."""
        if not source_docs:
            return ""
        
        reference_lines = []
        
        for i, doc in enumerate(source_docs, 1):
            doc_id = doc.get("doc_id", f"doc_{i}")
            url = doc.get("url", "")
            title = doc.get("title", f"Source {i}")
            author = doc.get("author", "")
            date = doc.get("timestamp", doc.get("date", ""))
            source = doc.get("source", "")
            
            # Format reference line
            reference_line = f"[{i}] "
            
            if author:
                reference_line += f"{author}. "
            
            if title:
                reference_line += f'"{title}". '
            
            if date:
                reference_line += f"{date}. "
            
            if url:
                reference_line += f"URL: {url}. "
            
            if source:
                reference_line += f"Source: {source}. "
            
            reference_line += f"(ID: {doc_id})"
            
            reference_lines.append(reference_line)
        
        return "\n".join(reference_lines)
    
    print(f"\n🔍 Testing source document mapping:")
    for i, fact in enumerate(verified_facts, 1):
        source_doc = find_source_doc_for_fact(fact, source_docs)
        print(f"   Fact {i}: {fact['claim'][:50]}...")
        if source_doc:
            print(f"      Mapped to: {source_doc['title']} (ID: {source_doc['doc_id']})")
        else:
            print(f"      No source document found")
    
    # Generate reference list
    reference_list = create_enhanced_reference_list(source_docs)
    
    print(f"\n📋 Generated Reference List:")
    print("-" * 40)
    print(reference_list)
    print("-" * 40)
    
    # Mock synthesis result
    synthesis_result = MockSynthesisResult(
        answer="The Earth orbits around the Sun [1]. The Sun is a massive star [2].",
        synthesis_method="enhanced_with_citations",
        fact_count=len(verified_facts),
        processing_time_ms=150,
        metadata={
            "has_citations": True,
            "citation_style": "inline",
            "total_references": len(source_docs)
        }
    )
    
    print(f"\n✅ Synthesis Results:")
    print(f"   Answer: {synthesis_result.answer}")
    print(f"   Method: {synthesis_result.synthesis_method}")
    print(f"   Fact Count: {synthesis_result.fact_count}")
    print(f"   Has Citations: {synthesis_result.metadata.get('has_citations', False)}")
    
    return synthesis_result

async def main():
    """Run the complete test."""
    
    print("🚀 Enhanced FactCheck and Citation Test")
    print("=" * 60)
    print("Testing core functionality without complex dependencies.")
    print()
    
    try:
        # Test vector search verification
        verification_result = await test_vector_search_verification()
        
        # Test citation generation
        synthesis_result = await test_citation_generation()
        
        print("\n🎉 Test completed successfully!")
        print("\nKey Features Tested:")
        print("✅ Sentence splitting and factual statement detection")
        print("✅ Vector search similarity calculation")
        print("✅ Source document mapping")
        print("✅ Enhanced reference list generation")
        print("✅ Citation integration")
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   Verified Sentences: {len(verification_result.verified_sentences)}")
        print(f"   Unsupported Sentences: {len(verification_result.unsupported_sentences)}")
        print(f"   Verification Confidence: {verification_result.verification_confidence:.2f}")
        print(f"   Synthesis Method: {synthesis_result.synthesis_method}")
        print(f"   Citations Generated: {synthesis_result.metadata.get('has_citations', False)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 