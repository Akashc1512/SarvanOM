#!/usr/bin/env python3
"""
Comprehensive HuggingFace Integration Test
MAANG/OpenAI/Perplexity Standards Implementation
Tests all latest stable features as of August 2025
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_huggingface_comprehensive():
    """Test all HuggingFace features comprehensively"""
    
    print("🔥 COMPREHENSIVE HUGGINGFACE INTEGRATION TEST")
    print("=" * 60)
    print("📋 MAANG/OpenAI/Perplexity Standards - August 2025")
    print()
    
    # Test environment variables
    print("🔐 ENVIRONMENT VARIABLES:")
    print("=" * 40)
    
    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    status = "✅ SET" if hf_token and hf_token != "your_*_here" else "❌ MISSING"
    preview = f"({hf_token[:10]}...)" if hf_token and hf_token != "your_*_here" else ""
    print(f"   HuggingFace Token: {status} {preview}")
    print()
    
    # Test HuggingFace integration directly
    print("🧪 TESTING HUGGINGFACE INTEGRATION:")
    print("=" * 40)
    
    try:
        # Import the integration
        from services.gateway.huggingface_integration import HuggingFaceIntegration
        
        # Initialize integration
        print("\n🚀 Initializing HuggingFace Integration...")
        hf_integration = HuggingFaceIntegration()
        await hf_integration.initialize()
        
        # Test 1: Text Generation
        print("\n📝 TEST 1: Text Generation")
        print("-" * 30)
        await test_text_generation(hf_integration)
        
        # Test 2: Embeddings
        print("\n🔍 TEST 2: Text Embeddings")
        print("-" * 30)
        await test_embeddings(hf_integration)
        
        # Test 3: Sentiment Analysis
        print("\n😊 TEST 3: Sentiment Analysis")
        print("-" * 30)
        await test_sentiment_analysis(hf_integration)
        
        # Test 4: Question Answering
        print("\n❓ TEST 4: Question Answering")
        print("-" * 30)
        await test_question_answering(hf_integration)
        
        # Test 5: Summarization
        print("\n📄 TEST 5: Text Summarization")
        print("-" * 30)
        await test_summarization(hf_integration)
        
        # Test 6: Zero-shot Classification
        print("\n🎯 TEST 6: Zero-shot Classification")
        print("-" * 30)
        await test_zero_shot_classification(hf_integration)
        
        print("\n✅ ALL HUGGINGFACE TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ HuggingFace integration test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_text_generation(hf_integration):
    """Test text generation with latest models"""
    try:
        prompt = "Artificial intelligence is"
        response = await hf_integration.generate_text(
            prompt=prompt,
            model_name="microsoft/DialoGPT-medium",
            max_length=50,
            temperature=0.7
        )
        
        print(f"   ✅ Text Generation: {response.result[:100]}...")
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        print(f"   🤖 Model: {response.model_name}")
        
    except Exception as e:
        print(f"   ❌ Text Generation Failed: {e}")

async def test_embeddings(hf_integration):
    """Test text embeddings"""
    try:
        texts = [
                    "Artificial intelligence is transforming the world",
                    "Machine learning is a subset of AI",
            "The weather is nice today"
        ]
        
        response = await hf_integration.get_embeddings(texts)
        
        print(f"   ✅ Embeddings Generated: {len(response.result)} vectors")
        print(f"   📊 Vector Dimensions: {len(response.result[0])}")
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        print(f"   🤖 Model: {response.model_name}")
        
    except Exception as e:
        print(f"   ❌ Embeddings Failed: {e}")

async def test_sentiment_analysis(hf_integration):
    """Test sentiment analysis"""
    try:
        texts = [
            "I love this new AI technology!",
            "This is terrible and disappointing",
            "The weather is neutral today"
        ]
        
        for text in texts:
            response = await hf_integration.analyze_sentiment(text)
            sentiment = response.result[0]['label']
            score = response.result[0]['score']
            print(f"   📝 '{text[:30]}...' → {sentiment} ({score:.3f})")
        
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        print(f"   🤖 Model: {response.model_name}")
        
    except Exception as e:
        print(f"   ❌ Sentiment Analysis Failed: {e}")

async def test_question_answering(hf_integration):
    """Test question answering"""
    try:
        context = "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals."
        question = "What is artificial intelligence?"
        
        response = await hf_integration.answer_question(question, context)
        
        print(f"   ❓ Question: {question}")
        print(f"   📖 Context: {context[:50]}...")
        print(f"   ✅ Answer: {response.result['answer']}")
        print(f"   📊 Confidence: {response.result['score']:.3f}")
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Question Answering Failed: {e}")

async def test_summarization(hf_integration):
    """Test text summarization"""
    try:
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. 
        Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
        """
        
        response = await hf_integration.summarize_text(text)
        
        print(f"   📄 Original: {len(text)} characters")
        print(f"   📝 Summary: {response.result[0]['summary_text']}")
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Summarization Failed: {e}")

async def test_zero_shot_classification(hf_integration):
    """Test zero-shot classification"""
    try:
        text = "I love this new AI technology!"
        candidate_labels = ["positive", "negative", "neutral"]
        
        response = await hf_integration.zero_shot_classify(text, candidate_labels)
        
        print(f"   📝 Text: {text}")
        print(f"   🏷️ Labels: {candidate_labels}")
        print(f"   ✅ Classification: {response.result['labels'][0]} ({response.result['scores'][0]:.3f})")
        print(f"   ⏱️ Processing Time: {response.processing_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Zero-shot Classification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_huggingface_comprehensive())
