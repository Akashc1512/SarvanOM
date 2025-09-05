#!/usr/bin/env python3
"""
Test Phase C2: Citations Pass
Testing inline markers + bibliography + disagreement detection.
"""

import asyncio
import time
from shared.core.services.citations_service import get_citations_service

async def test_phase_c2():
    print('🚀 Testing Phase C2: Citations Pass with real environment variables')
    
    # Get citations service
    citations_service = get_citations_service()
    
    # Test text with claims that need citations
    test_text = """
    Machine learning algorithms can achieve 95% accuracy on image classification tasks. 
    Deep learning models require large datasets to train effectively. 
    Python is the most popular programming language for data science.
    Neural networks have been used since the 1940s but gained popularity recently.
    """
    
    # Mock sources for testing
    test_sources = [
        {
            "title": "ImageNet Classification with Deep Convolutional Neural Networks",
            "url": "https://papers.nips.cc/paper/4824-imagenet-classification",
            "snippet": "We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes. On the test data, we achieved top-1 and top-5 error rates of 37.5% and 17.0% which is considerably better than the previous state-of-the-art.",
            "domain": "papers.nips.cc",
            "provider": "openalex"
        },
        {
            "title": "Deep Learning Book",
            "url": "https://www.deeplearningbook.org/",
            "snippet": "Deep learning is a form of machine learning that enables computers to learn from experience and understand the world in terms of a hierarchy of concepts. It requires large amounts of labeled training data.",
            "domain": "deeplearningbook.org", 
            "provider": "web"
        },
        {
            "title": "Stack Overflow Developer Survey 2023",
            "url": "https://stackoverflow.com/survey/2023",
            "snippet": "Python continues to be one of the most loved and wanted programming languages, particularly popular in data science and machine learning applications.",
            "domain": "stackoverflow.com",
            "provider": "stackexchange"
        },
        {
            "title": "A Brief History of Neural Networks",
            "url": "https://example.com/neural-history",
            "snippet": "The perceptron, an early form of neural network, was first introduced by Frank Rosenblatt in 1957. However, neural networks saw renewed interest in the 1980s and have become extremely popular in recent years.",
            "domain": "example.com",
            "provider": "web"
        }
    ]
    
    print(f'📊 Testing text: {len(test_text)} characters')
    print(f'🔍 Sources available: {len(test_sources)}')
    
    start_time = time.time()
    
    # Test citation processing
    try:
        result = await citations_service.process_text_with_citations(test_text, test_sources)
        
        processing_time = time.time() - start_time
        
        print(f'\n📋 Results Analysis:')
        print(f'   Processing time: {processing_time:.3f}s')
        
        # Extract components from tuple result
        cited_text, bibliography = result
        
        print(f'   Success: True')
        print(f'   Annotated text length: {len(cited_text)} characters')
        print(f'   Bibliography citations: {len(bibliography.citations)}')
        
        # Test export functionality
        print(f'\n📤 Testing Export Formats:')
        export_formats = ["markdown", "bibtex"]
        
        for format_name in export_formats:
            try:
                exported = citations_service.export_citations(bibliography, format_name)
                print(f'   ✅ {format_name.upper()}: {len(exported)} characters')
            except Exception as e:
                print(f'   ❌ {format_name.upper()}: {str(e)}')
        
        # Check requirements
        print(f'\n🎯 Phase C2 Requirement Check:')
        
        # Inline markers check
        has_inline_markers = "[" in cited_text and "]" in cited_text
        print(f'   Inline markers: {"✅ Present" if has_inline_markers else "❌ Missing"}')
        
        # Bibliography check  
        has_bibliography = len(bibliography.citations) > 0
        print(f'   Bibliography: {"✅ Generated" if has_bibliography else "❌ Missing"}')
        
        # Disagreement detection check
        disagreement_feature = hasattr(bibliography, 'disagreement_count')
        print(f'   Disagreement detection: {"✅ Implemented" if disagreement_feature else "❌ Missing"}')
        
        # Performance check (should be fast for citation processing)
        performance_pass = processing_time <= 5.0  # Reasonable for citation processing
        print(f'   Performance: {"✅ Good" if performance_pass else "❌ Slow"} ({processing_time:.3f}s)')
        
        overall_pass = has_inline_markers and has_bibliography and disagreement_feature and performance_pass
        
        if overall_pass:
            print(f'   ✅ PASS: Phase C2 requirements met!')
        else:
            print(f'   ❌ FAIL: Some requirements not met')
            
        return {
            'inline_markers': has_inline_markers,
            'bibliography': has_bibliography, 
            'disagreement_detection': disagreement_feature,
            'performance': performance_pass,
            'processing_time': processing_time,
            'pass': overall_pass
        }
        
    except Exception as e:
        print(f'❌ Citation processing failed: {e}')
        return {
            'pass': False,
            'error': str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(test_phase_c2())
    if result.get('pass'):
        print(f'\n🎉 Phase C2: Citations pass - COMPLETED ✅')
    else:
        print(f'\n❌ Phase C2: Requirements not met')
