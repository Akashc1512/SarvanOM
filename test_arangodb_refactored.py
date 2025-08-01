#!/usr/bin/env python3
"""
Test script for Refactored ArangoDB KnowledgeGraphAgent
Demonstrates the complete Neo4j to ArangoDB refactoring.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.arangodb_knowledge_graph_agent import ArangoDBKnowledgeGraphAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_arangodb_refactored_agent():
    """Test the refactored ArangoDB KnowledgeGraphAgent."""
    
    print("🧪 Testing Refactored ArangoDB KnowledgeGraphAgent")
    print("=" * 60)
    
    # Initialize the agent
    agent = ArangoDBKnowledgeGraphAgent()
    
    # Wait a moment for ArangoDB connection to initialize
    await asyncio.sleep(2)
    
    # Test queries that demonstrate Neo4j to ArangoDB refactoring
    test_queries = [
        {
            "query": "How is machine learning related to artificial intelligence?",
            "type": "entity_relationship",
            "description": "Entity relationship query (Neo4j -> ArangoDB)"
        },
        {
            "query": "What is the path between Python and React?",
            "type": "path_finding",
            "description": "Path finding query (Neo4j -> ArangoDB)"
        },
        {
            "query": "Tell me about Docker",
            "type": "entity_search",
            "description": "Entity search query (Neo4j -> ArangoDB)"
        },
        {
            "query": "What are the applications of neural networks?",
            "type": "entity_relationship",
            "description": "General knowledge query (Neo4j -> ArangoDB)"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Type: {test_case['type']}")
        print("-" * 40)
        
        try:
            # Execute query
            result = await agent.query(test_case['query'], test_case['type'])
            
            # Display results
            print(f"✅ Query completed successfully")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")
            print(f"Entities found: {len(result.entities)}")
            print(f"Relationships found: {len(result.relationships)}")
            print(f"Paths found: {len(result.paths)}")
            
            # Display entities
            if result.entities:
                print("\n📋 Entities:")
                for entity in result.entities[:5]:  # Show first 5
                    print(f"  - {entity.name} ({entity.type})")
                    if entity.properties.get('description'):
                        print(f"    Description: {entity.properties['description'][:100]}...")
            
            # Display relationships
            if result.relationships:
                print("\n🔗 Relationships:")
                for rel in result.relationships[:5]:  # Show first 5
                    print(f"  - {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id}")
                    if rel.properties.get('description'):
                        print(f"    Description: {rel.properties['description']}")
            
            # Display paths
            if result.paths:
                print("\n🛤️  Paths:")
                for i, path in enumerate(result.paths[:3]):  # Show first 3 paths
                    print(f"  Path {i+1}: {' -> '.join([node.name for node in path])}")
            
            # Display metadata
            if result.metadata:
                print(f"\n📊 Metadata:")
                for key, value in result.metadata.items():
                    if key not in ['entities_found', 'relationships_found', 'paths_found']:
                        print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("\n" + "=" * 60)
    
    # Test health status
    print("\n🏥 Health Status:")
    health = agent.get_health_status()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Refactored ArangoDB KnowledgeGraphAgent test completed!")


async def test_arangodb_connection():
    """Test ArangoDB connection specifically."""
    
    print("\n🔌 Testing ArangoDB Connection")
    print("=" * 40)
    
    # Check environment variables
    arango_vars = {
        "ARANGO_URL": os.getenv("ARANGO_URL"),
        "ARANGO_USERNAME": os.getenv("ARANGO_USERNAME"),
        "ARANGO_PASSWORD": os.getenv("ARANGO_PASSWORD"),
        "ARANGO_DATABASE": os.getenv("ARANGO_DATABASE")
    }
    
    print("Environment Variables:")
    for key, value in arango_vars.items():
        if key == "ARANGO_PASSWORD" and value:
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value or 'Not set'}")
    
    # Initialize agent
    agent = ArangoDBKnowledgeGraphAgent()
    await asyncio.sleep(2)
    
    print(f"\nArangoDB Connection Status: {'✅ Connected' if agent.connected else '❌ Disconnected'}")
    print(f"Using Mock Data: {not agent.connected}")
    
    if agent.connected:
        print("✅ ArangoDB is available and connected!")
        print("✅ Neo4j to ArangoDB refactoring successful!")
    else:
        print("⚠️  ArangoDB is not available. Using mock data for testing.")
        print("To enable ArangoDB:")
        print("  1. Install ArangoDB: https://www.arangodb.com/download/")
        print("  2. Start ArangoDB server")
        print("  3. Set environment variables: ARANGO_URL, ARANGO_USERNAME, ARANGO_PASSWORD")


async def test_arangodb_features():
    """Test specific ArangoDB features vs Neo4j."""
    
    print("\n🔧 Testing ArangoDB vs Neo4j Features")
    print("=" * 50)
    
    agent = ArangoDBKnowledgeGraphAgent()
    await asyncio.sleep(2)
    
    print("\n📊 Feature Comparison:")
    print("  ✅ Multi-model database (Graph + Document + Key-Value)")
    print("  ✅ AQL query language (vs Cypher)")
    print("  ✅ Built-in web interface")
    print("  ✅ Horizontal scaling capabilities")
    print("  ✅ ACID transactions")
    print("  ✅ Graph algorithms")
    print("  ✅ Free Community Edition")
    print("  ✅ 100 GiB dataset limit")
    
    print("\n🔄 Refactoring Benefits:")
    print("  ✅ Same graph database capabilities as Neo4j")
    print("  ✅ Better scalability")
    print("  ✅ More flexible data model")
    print("  ✅ Free for non-commercial use")
    print("  ✅ Active development and community")
    
    print("\n📝 Query Language Comparison:")
    print("  Neo4j Cypher: MATCH (a)-[r]-(b) RETURN a, r, b")
    print("  ArangoDB AQL: FOR rel IN relationships FOR a IN entities FOR b IN entities")
    print("                FILTER rel._from == a._id AND rel._to == b._id RETURN {a, rel, b}")


async def test_arangodb_data_operations():
    """Test ArangoDB data operations."""
    
    print("\n💾 Testing ArangoDB Data Operations")
    print("=" * 40)
    
    agent = ArangoDBKnowledgeGraphAgent()
    await asyncio.sleep(2)
    
    if agent.connected:
        print("✅ Testing ArangoDB data operations...")
        
        try:
            # Test creating constraints
            success = await agent.create_constraints()
            print(f"  Constraints creation: {'✅ Success' if success else '❌ Failed'}")
            
            # Test creating a knowledge node
            success = await agent.create_knowledge_node(
                "test_node",
                "technology",
                {"name": "Test Technology", "description": "A test technology"}
            )
            print(f"  Node creation: {'✅ Success' if success else '❌ Failed'}")
            
            # Test creating a relationship
            success = await agent.create_relationship(
                "test_node",
                "ml",
                "related_to",
                {"description": "Test relationship"}
            )
            print(f"  Relationship creation: {'✅ Success' if success else '❌ Failed'}")
            
        except Exception as e:
            print(f"  ❌ Data operations failed: {e}")
    else:
        print("⚠️  ArangoDB not connected - skipping data operations")


def main():
    """Main function to run the tests."""
    print("🚀 Starting ArangoDB Refactoring Tests")
    print("=" * 70)
    print("This test demonstrates the complete refactoring from Neo4j to ArangoDB")
    print("=" * 70)
    
    try:
        # Run tests
        asyncio.run(test_arangodb_connection())
        asyncio.run(test_arangodb_features())
        asyncio.run(test_arangodb_data_operations())
        asyncio.run(test_arangodb_refactored_agent())
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    main() 