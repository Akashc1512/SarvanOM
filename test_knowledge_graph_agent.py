from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Test script for ArangoDB KnowledgeGraphAgent
Demonstrates the agent's ability to query knowledge graphs with both ArangoDB and mock data.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_knowledge_graph_agent():
    """Test the ArangoDB KnowledgeGraphAgent."""
    
    print("🧪 Testing ArangoDB KnowledgeGraphAgent")
    print("=" * 60)
    
    # Initialize the agent
    agent = KnowledgeGraphAgent()
    
    # Wait a moment for ArangoDB connection to initialize
    await asyncio.sleep(2)
    
    # Test queries
    test_queries = [
        {
            "query": "How is machine learning related to artificial intelligence?",
            "type": "entity_relationship",
            "description": "Entity relationship query"
        },
        {
            "query": "What is the path between Python and React?",
            "type": "path_finding",
            "description": "Path finding query"
        },
        {
            "query": "Tell me about Docker",
            "type": "entity_search",
            "description": "Entity search query"
        },
        {
            "query": "What are the applications of neural networks?",
            "type": "entity_relationship",
            "description": "General knowledge query"
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
    
    print("\n✅ ArangoDB KnowledgeGraphAgent test completed!")


async def test_arangodb_connection():
    """Test ArangoDB connection specifically."""
    
    print("\n🔌 Testing ArangoDB Connection")
    print("=" * 40)
    
    # Check environment variables
    arango_vars = {
        "ARANGO_URL": settings.arango_url,
        "ARANGO_USERNAME": settings.arango_username,
        "ARANGO_PASSWORD": settings.arango_password,
        "ARANGO_DATABASE": settings.arango_database
    }
    
    print("Environment Variables:")
    for key, value in arango_vars.items():
        if key == "ARANGO_PASSWORD" and value:
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value or 'Not set'}")
    
    # Initialize agent
    agent = KnowledgeGraphAgent()
    await asyncio.sleep(2)
    
    print(f"\nArangoDB Connection Status: {'✅ Connected' if agent.connected else '❌ Disconnected'}")
    print(f"Using Mock Data: {not agent.connected}")
    
    if agent.connected:
        print("✅ ArangoDB is available and connected!")
    else:
        print("⚠️  ArangoDB is not available. Using mock data for testing.")
        print("To enable ArangoDB:")
        print("  1. Install ArangoDB driver: pip install python-arango")
        print("  2. Set environment variables: ARANGO_URL, ARANGO_USERNAME, ARANGO_PASSWORD")
        print("  3. Start ArangoDB server")


def main():
    """Main function to run the tests."""
    print("🚀 Starting ArangoDB KnowledgeGraphAgent Tests")
    print("=" * 70)
    
    try:
        # Run tests
        asyncio.run(test_arangodb_connection())
        asyncio.run(test_knowledge_graph_agent())
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    main() 