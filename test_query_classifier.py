#!/usr/bin/env python3
"""
Test script for QueryClassifier functionality.
Demonstrates query classification with various types of queries.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.core.query_classifier import QueryClassifier, QueryCategory


async def test_query_classifier():
    """Test the QueryClassifier with various query types."""
    
    # Initialize the classifier
    classifier = QueryClassifier()
    
    # Test queries covering different categories
    test_queries = [
        # Knowledge Graph queries
        "What is the relationship between machine learning and artificial intelligence?",
        "How are neural networks connected to deep learning?",
        "What entities are related to blockchain technology?",
        
        # Code queries
        "How to implement a binary search tree in Python?",
        "What's the best way to handle errors in JavaScript?",
        "How to deploy a React app to AWS?",
        "What are the differences between REST and GraphQL APIs?",
        
        # Analytical queries
        "Analyze the impact of cloud computing on software development",
        "Why does machine learning require large datasets?",
        "What causes performance issues in web applications?",
        
        # Comparative queries
        "Compare Python vs JavaScript for web development",
        "What are the pros and cons of microservices vs monoliths?",
        "Which database is better: PostgreSQL or MongoDB?",
        
        # Procedural queries
        "How to set up a development environment for Python?",
        "What are the steps to deploy a Docker container?",
        "How to configure authentication in a web application?",
        
        # Creative queries
        "Design a system for real-time chat application",
        "Create an innovative approach to data visualization",
        "What if we could build AI that understands emotions?",
        
        # Opinion queries
        "What do you think about the future of programming languages?",
        "Should companies invest more in AI research?",
        "What's your opinion on remote work vs office work?",
        
        # General factual queries
        "What is the capital of France?",
        "When was the first computer invented?",
        "Who created the Python programming language?",
        
        # Complex queries
        "How do microservices architecture patterns influence the scalability and maintainability of enterprise applications, and what are the trade-offs between different service mesh implementations?",
        "What are the implications of quantum computing on current cryptographic standards, and how should organizations prepare for post-quantum cryptography?",
    ]
    
    print("🔍 Testing QueryClassifier with various query types...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        
        try:
            # Classify the query
            classification = await classifier.classify_query(query)
            
            # Display results
            print(f"  📊 Category: {classification.category.value}")
            print(f"  🎯 Confidence: {classification.confidence:.2f}")
            print(f"  📈 Complexity: {classification.complexity.value}")
            print(f"  🤖 Suggested Agents: {', '.join(classification.suggested_agents)}")
            print(f"  🎯 Execution Strategy: {classification.routing_hints.get('execution_strategy', 'pipeline')}")
            print(f"  ⚡ Priority: {classification.routing_hints.get('priority_level', 'normal')}")
            
            if classification.detected_patterns:
                print(f"  🔍 Detected Patterns: {', '.join(classification.detected_patterns[:3])}")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error classifying query: {e}\n")
    
    # Test batch classification
    print("🔄 Testing batch classification...")
    try:
        batch_results = await classifier.batch_classify(test_queries[:5])
        print(f"  ✅ Successfully classified {len(batch_results)} queries in batch")
        
        # Show category distribution
        category_counts = {}
        for result in batch_results:
            category = result.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("  📊 Category Distribution:")
        for category, count in category_counts.items():
            print(f"    {category}: {count}")
        
    except Exception as e:
        print(f"  ❌ Error in batch classification: {e}")
    
    # Show classification statistics
    print("\n📈 Classification Statistics:")
    stats = classifier.get_classification_stats()
    print(f"  Total patterns by category:")
    for category, count in stats["total_patterns"].items():
        print(f"    {category}: {count} patterns")
    
    print(f"\n  Complexity indicators:")
    for complexity, count in stats["complexity_indicators"].items():
        print(f"    {complexity}: {count} patterns")


async def test_integration_with_orchestrator():
    """Test how the QueryClassifier integrates with the LeadOrchestrator."""
    
    print("\n🔗 Testing QueryClassifier integration with LeadOrchestrator...")
    
    try:
        from shared.core.agents.lead_orchestrator import LeadOrchestrator
        from shared.core.agents.base_agent import QueryContext
        
        # Initialize orchestrator
        orchestrator = LeadOrchestrator()
        
        # Test queries
        test_queries = [
            "What is the relationship between machine learning and deep learning?",
            "How to implement authentication in a React application?",
            "Compare the performance of different sorting algorithms",
            "What are the steps to deploy a microservice architecture?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            
            # Create query context
            context = QueryContext(query=query)
            
            # Test the analyze_and_plan method
            plan = await orchestrator.analyze_and_plan(context)
            
            print(f"  📋 Execution Plan:")
            print(f"    Pattern: {plan.get('execution_pattern', 'unknown')}")
            print(f"    Category: {plan.get('primary_category', 'unknown')}")
            print(f"    Complexity: {plan.get('complexity_score', 0):.2f}")
            print(f"    Priority: {plan.get('priority_level', 'normal')}")
            print(f"    Suggested Agents: {plan.get('suggested_agents', [])}")
        
        print("\n✅ Integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in integration test: {e}")


if __name__ == "__main__":
    print("🚀 Starting QueryClassifier Tests...\n")
    
    # Run the tests
    asyncio.run(test_query_classifier())
    asyncio.run(test_integration_with_orchestrator())
    
    print("\n🎉 All tests completed!") 