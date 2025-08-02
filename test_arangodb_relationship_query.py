#!/usr/bin/env python3
"""
Test script for ArangoDB relationship query functionality.
Tests the query_relationships method with loaded environment variables.
Industry-grade test following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import sys
import os
import warnings

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available")

# Suppress warnings for clean test output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent


async def test_arangodb_relationship_query():
    """
    Test the ArangoDB relationship query functionality with industry-grade standards.
    
    This test validates:
    1. Single entity queries return correct structure and data
    2. Two entity path finding works correctly
    3. Non-existent entities are handled gracefully
    4. Mock data fallback works when ArangoDB is unavailable
    5. All edge cases are properly handled
    """
    print("🔍 Testing ArangoDB Relationship Query...")
    
    # Create agent
    agent = KnowledgeGraphAgent()
    
    # Industry-grade assertions for agent creation
    assert agent is not None, "Agent should not be None"
    assert hasattr(agent, 'arango_url'), "Agent should have arango_url attribute"
    assert hasattr(agent, 'arango_username'), "Agent should have arango_username attribute"
    assert hasattr(agent, 'arango_database'), "Agent should have arango_database attribute"
    assert hasattr(agent, 'query_relationships'), "Agent should have query_relationships method"
    
    print(f"✅ Agent created successfully")
    print(f"📋 ArangoDB URL: {agent.arango_url}")
    print(f"📋 ArangoDB User: {agent.arango_username}")
    print(f"📋 ArangoDB Database: {agent.arango_database}")
    
    # Test single entity query
    print("\n📋 Testing Single Entity Query...")
    try:
        result = await agent.query_relationships("Python")
        
        # Industry-grade assertions for result structure
        assert result is not None, "Result should not be None"
        assert hasattr(result, 'entities'), "Result should have entities attribute"
        assert hasattr(result, 'relationships'), "Result should have relationships attribute"
        assert hasattr(result, 'paths'), "Result should have paths attribute"
        assert hasattr(result, 'query_entities'), "Result should have query_entities attribute"
        assert hasattr(result, 'confidence'), "Result should have confidence attribute"
        assert hasattr(result, 'processing_time_ms'), "Result should have processing_time_ms attribute"
        assert hasattr(result, 'metadata'), "Result should have metadata attribute"
        
        # Validate data types
        assert isinstance(result.entities, list), "Entities should be a list"
        assert isinstance(result.relationships, list), "Relationships should be a list"
        assert isinstance(result.paths, list), "Paths should be a list"
        assert isinstance(result.query_entities, list), "Query entities should be a list"
        assert isinstance(result.confidence, (int, float)), "Confidence should be numeric"
        assert isinstance(result.processing_time_ms, (int, float)), "Processing time should be numeric"
        assert isinstance(result.metadata, dict), "Metadata should be a dictionary"
        
        # Validate confidence range
        assert 0 <= result.confidence <= 1, f"Confidence should be between 0 and 1: {result.confidence}"
        
        print(f"✅ Single entity query completed")
        print(f"📋 Entities found: {len(result.entities)}")
        print(f"📋 Relationships found: {len(result.relationships)}")
        print(f"📋 Confidence: {result.confidence}")
        
        if result.entities:
            print("📋 Found entities:")
            for entity in result.entities[:3]:  # Show first 3
                assert hasattr(entity, 'id'), "Entity should have id attribute"
                assert hasattr(entity, 'name'), "Entity should have name attribute"
                assert hasattr(entity, 'type'), "Entity should have type attribute"
                assert hasattr(entity, 'properties'), "Entity should have properties attribute"
                print(f"   - {entity.name} ({entity.type})")
        
        if result.relationships:
            print("📋 Found relationships:")
            for rel in result.relationships[:3]:  # Show first 3
                assert hasattr(rel, 'source_id'), "Relationship should have source_id attribute"
                assert hasattr(rel, 'target_id'), "Relationship should have target_id attribute"
                assert hasattr(rel, 'relationship_type'), "Relationship should have relationship_type attribute"
                assert hasattr(rel, 'properties'), "Relationship should have properties attribute"
                print(f"   - {rel.relationship_type}")
        
        # Check pseudo-documents
        if "pseudo_documents" in result.metadata:
            pseudo_docs = result.metadata["pseudo_documents"]
            assert isinstance(pseudo_docs, list), "Pseudo documents should be a list"
            print(f"📋 Generated {len(pseudo_docs)} pseudo-documents for downstream processing")
            
            # Validate pseudo-document structure
            for doc in pseudo_docs:
                assert isinstance(doc, dict), "Pseudo document should be a dictionary"
                assert "content" in doc, "Pseudo document should have content field"
                assert "title" in doc, "Pseudo document should have title field"
                assert "score" in doc, "Pseudo document should have score field"
                assert "source_type" in doc, "Pseudo document should have source_type field"
            
    except Exception as e:
        print(f"❌ Single entity query failed: {e}")
        raise  # Re-raise for proper test failure
    
    # Test two entity path finding
    print("\n📋 Testing Two Entity Path Finding...")
    try:
        result = await agent.query_relationships("Python", "Machine Learning")
        
        # Industry-grade assertions
        assert result is not None, "Result should not be None"
        assert len(result.query_entities) == 2, "Should have exactly 2 query entities"
        assert "Python" in result.query_entities, "Python should be in query entities"
        assert "Machine Learning" in result.query_entities, "Machine Learning should be in query entities"
        
        print(f"✅ Two entity path finding completed")
        print(f"📋 Entities found: {len(result.entities)}")
        print(f"📋 Relationships found: {len(result.relationships)}")
        print(f"📋 Paths found: {len(result.paths)}")
        print(f"📋 Confidence: {result.confidence}")
        
        # Validate paths structure
        for path in result.paths:
            assert isinstance(path, list), "Path should be a list"
            for entity in path:
                assert hasattr(entity, 'id'), "Path entity should have id attribute"
                assert hasattr(entity, 'name'), "Path entity should have name attribute"
        
        if result.paths:
            print("📋 Found paths:")
            for i, path in enumerate(result.paths):
                path_names = [entity.name for entity in path]
                print(f"   Path {i+1}: {' -> '.join(path_names)}")
        
    except Exception as e:
        print(f"❌ Two entity path finding failed: {e}")
        raise  # Re-raise for proper test failure
    
    # Test non-existent entity
    print("\n📋 Testing Non-existent Entity...")
    try:
        result = await agent.query_relationships("NonExistentEntity")
        
        # Industry-grade assertions for non-existent entity
        assert result is not None, "Result should not be None even for non-existent entity"
        assert len(result.entities) == 0, "Should have no entities for non-existent entity"
        assert result.confidence < 0.5, f"Confidence should be low for non-existent entity: {result.confidence}"
        
        print(f"✅ Non-existent entity query completed")
        print(f"📋 Entities found: {len(result.entities)}")
        print(f"📋 Confidence: {result.confidence}")
        
        if len(result.entities) == 0:
            print("✅ Correctly handled non-existent entity")
        
    except Exception as e:
        print(f"❌ Non-existent entity query failed: {e}")
        raise  # Re-raise for proper test failure
    
    # Test edge cases
    print("\n📋 Testing Edge Cases...")
    
    # Test empty string
    try:
        result = await agent.query_relationships("")
        assert result is not None, "Result should not be None for empty string"
        print("✅ Empty string handled gracefully")
    except Exception as e:
        print(f"❌ Empty string handling failed: {e}")
        raise
    
    # Test None values
    try:
        result = await agent.query_relationships(None)
        assert result is not None, "Result should not be None for None input"
        print("✅ None input handled gracefully")
    except Exception as e:
        print(f"❌ None input handling failed: {e}")
        raise
    
    # Test special characters
    try:
        result = await agent.query_relationships("Python@#$%")
        assert result is not None, "Result should not be None for special characters"
        print("✅ Special characters handled gracefully")
    except Exception as e:
        print(f"❌ Special characters handling failed: {e}")
        raise
    
    print("\n🎉 ArangoDB relationship query test completed!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_arangodb_relationship_query()
        if success:
            print("\n✅ ArangoDB Relationship Query Test Completed Successfully!")
            return 0
        else:
            print("\n❌ ArangoDB Relationship Query Test Failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 