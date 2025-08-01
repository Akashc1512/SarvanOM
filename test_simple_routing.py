#!/usr/bin/env python3
"""
Simple Test for Intelligent Routing - Tests the routing logic without external dependencies
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.core.query_classifier import QueryClassifier, QueryCategory


async def test_classification_and_routing():
    """Test the classification and routing logic."""
    
    print("🚀 Testing Query Classification and Routing Logic\n")
    
    # Initialize the classifier
    classifier = QueryClassifier()
    
    # Test queries for different categories
    test_queries = [
        {
            "query": "What is the relationship between machine learning and artificial intelligence?",
            "expected_category": QueryCategory.KNOWLEDGE_GRAPH.value,
            "description": "Knowledge Graph Query"
        },
        {
            "query": "How to implement authentication in a React application?",
            "expected_category": QueryCategory.CODE.value,
            "description": "Code Query"
        },
        {
            "query": "Analyze the impact of cloud computing on software development",
            "expected_category": QueryCategory.ANALYTICAL.value,
            "description": "Analytical Query"
        },
        {
            "query": "Compare Python vs JavaScript for web development",
            "expected_category": QueryCategory.COMPARATIVE.value,
            "description": "Comparative Query"
        },
        {
            "query": "What is the capital of France?",
            "expected_category": QueryCategory.GENERAL_FACTUAL.value,
            "description": "General Factual Query"
        }
    ]
    
    print("📝 Testing query classification...\n")
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_category = test_case["expected_category"]
        description = test_case["description"]
        
        print(f"Test {i}: {description}")
        print(f"Query: {query}")
        print(f"Expected Category: {expected_category}")
        
        try:
            # Classify the query
            classification = await classifier.classify_query(query)
            
            actual_category = classification.category.value
            confidence = classification.confidence
            complexity = classification.complexity.value
            suggested_agents = classification.suggested_agents
            routing_hints = classification.routing_hints
            
            print(f"  📊 Actual Category: {actual_category}")
            print(f"  🎯 Confidence: {confidence:.2f}")
            print(f"  📈 Complexity: {complexity}")
            print(f"  🤖 Suggested Agents: {suggested_agents}")
            print(f"  🎯 Execution Strategy: {routing_hints.get('execution_strategy', 'unknown')}")
            print(f"  ⚡ Priority: {routing_hints.get('priority_level', 'unknown')}")
            
            # Check if classification was successful
            if actual_category == expected_category:
                print(f"  🎉 Category Match: ✅")
            else:
                print(f"  ⚠️ Category Mismatch: Expected {expected_category}, got {actual_category}")
            
            # Show routing decision
            print(f"  🔗 Routing Decision:")
            if actual_category == QueryCategory.KNOWLEDGE_GRAPH.value:
                print(f"    → Route to Knowledge Graph Agent")
            elif actual_category == QueryCategory.CODE.value:
                print(f"    → Route to Code-Specific Processing")
            elif actual_category == QueryCategory.ANALYTICAL.value:
                print(f"    → Route to Analytical Processing")
            elif actual_category == QueryCategory.COMPARATIVE.value:
                print(f"    → Route to Comparative Processing")
            else:
                print(f"    → Route to General Factual Processing")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    
    print("✅ Classification and routing tests completed!")


async def test_fallback_logic():
    """Test the fallback logic for low-confidence classifications."""
    
    print("\n🔄 Testing Fallback Logic...\n")
    
    classifier = QueryClassifier()
    
    # Test queries that might have low confidence
    fallback_queries = [
        "What is the relationship between blockchain and quantum computing?",
        "How does machine learning relate to data science?",
        "What connects artificial intelligence with robotics?"
    ]
    
    for i, query in enumerate(fallback_queries, 1):
        print(f"Fallback Test {i}: {query}")
        
        try:
            classification = await classifier.classify_query(query)
            
            category = classification.category.value
            confidence = classification.confidence
            
            print(f"  📊 Category: {category}")
            print(f"  🎯 Confidence: {confidence:.2f}")
            
            if confidence < 0.4:
                print(f"  🔄 Low confidence detected - would apply fallback logic")
                print(f"  🔄 Would try Knowledge Graph as fallback")
            else:
                print(f"  ✅ Sufficient confidence - no fallback needed")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    
    print("✅ Fallback logic tests completed!")


async def test_batch_classification():
    """Test batch classification performance."""
    
    print("\n⚡ Testing Batch Classification...\n")
    
    classifier = QueryClassifier()
    
    # Test queries for batch processing
    batch_queries = [
        "What is the relationship between machine learning and AI?",
        "How to implement authentication in React?",
        "Compare Python vs JavaScript",
        "What is the capital of France?",
        "Analyze the impact of cloud computing"
    ]
    
    print(f"Processing {len(batch_queries)} queries in batch...")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        batch_results = await classifier.batch_classify(batch_queries)
        
        end_time = asyncio.get_event_loop().time()
        processing_time = (end_time - start_time) * 1000
        
        print(f"  ⏱️ Batch Processing Time: {processing_time:.2f}ms")
        print(f"  📊 Results:")
        
        for i, result in enumerate(batch_results, 1):
            print(f"    {i}. {batch_queries[i-1][:30]}... → {result.category.value} (confidence: {result.confidence:.2f})")
        
        # Show category distribution
        category_counts = {}
        for result in batch_results:
            category = result.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"  📈 Category Distribution:")
        for category, count in category_counts.items():
            print(f"    {category}: {count}")
        
    except Exception as e:
        print(f"  ❌ Batch classification error: {e}")
    
    print("✅ Batch classification test completed!")


if __name__ == "__main__":
    print("🚀 Starting Simple Routing Tests...\n")
    
    # Run all tests
    asyncio.run(test_classification_and_routing())
    asyncio.run(test_fallback_logic())
    asyncio.run(test_batch_classification())
    
    print("\n🎉 All simple routing tests completed!") 