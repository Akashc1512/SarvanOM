#!/usr/bin/env python3
"""
Test Intelligent Routing - Demonstrates QueryClassifier integration with conditional routing
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.lead_orchestrator import LeadOrchestrator
from shared.core.agents.base_agent import QueryContext
from shared.core.query_classifier import QueryCategory


async def test_intelligent_routing():
    """Test the intelligent routing functionality with different query types."""
    
    print("🚀 Testing Intelligent Routing with QueryClassifier Integration\n")
    
    # Initialize the orchestrator
    orchestrator = LeadOrchestrator()
    
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
        },
        {
            "query": "What are the steps to deploy a microservice architecture?",
            "expected_category": QueryCategory.CODE.value,
            "description": "Procedural Code Query"
        }
    ]
    
    print("📝 Testing different query types with intelligent routing...\n")
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_category = test_case["expected_category"]
        description = test_case["description"]
        
        print(f"Test {i}: {description}")
        print(f"Query: {query}")
        print(f"Expected Category: {expected_category}")
        
        try:
            # Create query context
            context = QueryContext(query=query)
            
            # Process the query through the orchestrator
            result = await orchestrator.process_query(query)
            
            # Extract classification from result
            classification = result.get("metadata", {}).get("classification", {})
            actual_category = classification.get("category", "unknown")
            confidence = classification.get("confidence", 0.0)
            
            print(f"  📊 Actual Category: {actual_category}")
            print(f"  🎯 Confidence: {confidence:.2f}")
            print(f"  ✅ Success: {result.get('success', False)}")
            
            # Check if routing was successful
            if actual_category == expected_category:
                print(f"  🎉 Category Match: ✅")
            else:
                print(f"  ⚠️ Category Mismatch: Expected {expected_category}, got {actual_category}")
            
            # Show routing details
            routing_info = result.get("metadata", {}).get("routing_info", {})
            if routing_info:
                print(f"  🔗 Routing Path: {routing_info.get('route_taken', 'unknown')}")
                print(f"  📚 Data Source: {routing_info.get('data_source', 'unknown')}")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    
    # Test fallback logic
    print("🔄 Testing Fallback Logic...\n")
    
    # Test a query that might have low confidence
    fallback_query = "What is the relationship between blockchain and quantum computing?"
    
    print(f"Fallback Test Query: {fallback_query}")
    
    try:
        result = await orchestrator.process_query(fallback_query)
        
        classification = result.get("metadata", {}).get("classification", {})
        category = classification.get("category", "unknown")
        confidence = classification.get("confidence", 0.0)
        
        print(f"  📊 Category: {category}")
        print(f"  🎯 Confidence: {confidence:.2f}")
        
        if confidence < 0.4:
            print(f"  🔄 Low confidence detected - fallback logic applied")
        
        print(f"  ✅ Success: {result.get('success', False)}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Intelligent routing tests completed!")


async def test_knowledge_graph_integration():
    """Test the knowledge graph agent integration specifically."""
    
    print("\n🔗 Testing Knowledge Graph Agent Integration...\n")
    
    orchestrator = LeadOrchestrator()
    
    # Test knowledge graph specific queries
    kg_queries = [
        "What is the relationship between machine learning and deep learning?",
        "How are neural networks connected to artificial intelligence?",
        "What entities are related to blockchain technology?",
        "What is the connection between Python and machine learning?"
    ]
    
    for i, query in enumerate(kg_queries, 1):
        print(f"KG Query {i}: {query}")
        
        try:
            # Create query context
            context = QueryContext(query=query)
            
            # Analyze and plan to see classification
            plan = await orchestrator.analyze_and_plan(context)
            classification = plan.get("classification", {})
            category = classification.get("category", "unknown")
            confidence = classification.get("confidence", 0.0)
            
            print(f"  📊 Classification: {category} (confidence: {confidence:.2f})")
            
            if category == QueryCategory.KNOWLEDGE_GRAPH.value:
                print(f"  🔗 Would route to Knowledge Graph Agent")
                
                # Test the knowledge graph agent directly
                kg_result = await orchestrator.knowledge_graph_agent.query(query)
                
                print(f"  📚 Entities found: {len(kg_result.entities)}")
                print(f"  🔗 Relationships found: {len(kg_result.relationships)}")
                print(f"  🛤️ Paths found: {len(kg_result.paths)}")
                
                if kg_result.entities:
                    print(f"  📋 Sample entities:")
                    for entity in kg_result.entities[:3]:  # Show first 3
                        print(f"    - {entity.name} ({entity.type})")
                
            else:
                print(f"  ⚠️ Would route to standard processing")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()


async def test_routing_performance():
    """Test routing performance and timing."""
    
    print("\n⚡ Testing Routing Performance...\n")
    
    orchestrator = LeadOrchestrator()
    
    # Test queries for performance measurement
    performance_queries = [
        "What is the relationship between machine learning and AI?",
        "How to implement authentication in React?",
        "Compare Python vs JavaScript",
        "What is the capital of France?"
    ]
    
    total_time = 0
    successful_routes = 0
    
    for i, query in enumerate(performance_queries, 1):
        print(f"Performance Test {i}: {query[:50]}...")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await orchestrator.process_query(query)
            
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            
            total_time += processing_time
            successful_routes += 1
            
            classification = result.get("metadata", {}).get("classification", {})
            category = classification.get("category", "unknown")
            
            print(f"  ⏱️ Processing Time: {processing_time:.2f}ms")
            print(f"  📊 Category: {category}")
            print(f"  ✅ Success: {result.get('success', False)}")
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            processing_time = (end_time - start_time) * 1000
            total_time += processing_time
            
            print(f"  ⏱️ Processing Time: {processing_time:.2f}ms")
            print(f"  ❌ Error: {e}")
        
        print()
    
    if successful_routes > 0:
        avg_time = total_time / len(performance_queries)
        print(f"📈 Performance Summary:")
        print(f"  Total Queries: {len(performance_queries)}")
        print(f"  Successful Routes: {successful_routes}")
        print(f"  Average Processing Time: {avg_time:.2f}ms")
        print(f"  Total Processing Time: {total_time:.2f}ms")


if __name__ == "__main__":
    print("🚀 Starting Intelligent Routing Tests...\n")
    
    # Run all tests
    asyncio.run(test_intelligent_routing())
    asyncio.run(test_knowledge_graph_integration())
    asyncio.run(test_routing_performance())
    
    print("\n🎉 All intelligent routing tests completed!") 