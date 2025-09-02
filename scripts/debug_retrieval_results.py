#!/usr/bin/env python3
"""
Debug script to check retrieval results format and lane metadata.
"""

import asyncio
import sys

# Add current directory to path
sys.path.append('.')

async def debug_retrieval_results():
    """Debug retrieval results to understand the format."""
    print("🔍 Debugging retrieval results...")
    
    try:
        from services.retrieval.orchestrator import get_orchestrator
        from shared.contracts.query import RetrievalSearchRequest
        
        orchestrator = get_orchestrator()
        
        # Test query
        request = RetrievalSearchRequest(
            query="artificial intelligence",
            max_results=5
        )
        
        print("📝 Running retrieval...")
        response = await orchestrator.orchestrate_retrieval(request)
        
        print(f"📊 Total results: {len(response.sources)}")
        print(f"📊 Method: {response.method}")
        
        # Check each result
        for i, source in enumerate(response.sources):
            print(f"\n🔍 Result {i+1}:")
            print(f"   ID: {source.get('id', 'N/A')}")
            print(f"   Content length: {len(source.get('content', ''))}")
            print(f"   Score: {source.get('score', 'N/A')}")
            print(f"   Metadata: {source.get('metadata', {})}")
            
            # Check lane information
            metadata = source.get('metadata', {})
            lane = metadata.get('lane', 'unknown')
            print(f"   Lane: {lane}")
            
            if lane == 'unknown':
                print(f"   ⚠️  WARNING: Lane is 'unknown' - this indicates a metadata issue!")
        
        # Check if we have any results from each lane
        lanes = {}
        for source in response.sources:
            metadata = source.get('metadata', {})
            lane = metadata.get('lane', 'unknown')
            if lane not in lanes:
                lanes[lane] = 0
            lanes[lane] += 1
        
        print(f"\n📊 Lane distribution: {lanes}")
        
        # Check if vector and KG are working
        vector_count = lanes.get('vector_search', 0)
        kg_count = lanes.get('knowledge_graph', 0)
        web_count = lanes.get('web_search', 0)
        
        print(f"\n🎯 Lane Results Summary:")
        print(f"   Vector Search: {vector_count} results")
        print(f"   Knowledge Graph: {kg_count} results")
        print(f"   Web Search: {web_count} results")
        
        if vector_count == 0:
            print("   ❌ Vector search returned 0 results")
        if kg_count == 0:
            print("   ❌ Knowledge graph returned 0 results")
        if web_count == 0:
            print("   ❌ Web search returned 0 results")
        
        return response.sources
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return []

async def debug_vector_store_directly():
    """Debug vector store directly."""
    print("\n🔍 Debugging vector store directly...")
    
    try:
        from services.retrieval.main import VECTOR_STORE
        from shared.embeddings.local_embedder import embed_texts
        
        # Test query
        test_query = "artificial intelligence"
        query_embedding = embed_texts([test_query])[0]
        
        print(f"📝 Searching vector store for: '{test_query}'")
        results = await VECTOR_STORE.search(
            query_embedding=query_embedding,
            top_k=5
        )
        
        print(f"📊 Vector store returned {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"\n🔍 Vector Result {i+1}:")
            print(f"   Type: {type(result)}")
            
            if isinstance(result, tuple):
                doc, score = result
                print(f"   Document ID: {doc.id}")
                print(f"   Document text length: {len(doc.text)}")
                print(f"   Score: {score}")
                print(f"   Metadata: {doc.metadata}")
            elif isinstance(result, dict):
                print(f"   Dict keys: {list(result.keys())}")
                print(f"   Content: {result.get('content', 'N/A')[:100]}...")
                print(f"   Metadata: {result.get('metadata', {})}")
            else:
                print(f"   Unknown format: {result}")
        
        return results
        
    except Exception as e:
        print(f"❌ Vector store debug failed: {e}")
        import traceback
        traceback.print_exc()
        return []

async def debug_kg_directly():
    """Debug knowledge graph directly."""
    print("\n🔍 Debugging knowledge graph directly...")
    
    try:
        from shared.core.agents.knowledge_graph_service import KnowledgeGraphService
        
        kg_service = KnowledgeGraphService()
        
        # Test query
        test_query = "artificial intelligence"
        
        print(f"📝 Querying KG for: '{test_query}'")
        kg_result = await kg_service.query(test_query, "entity_relationship")
        
        print(f"📊 KG returned {len(kg_result.entities)} entities and {len(kg_result.relationships)} relationships")
        print(f"📊 Confidence: {kg_result.confidence}")
        
        if kg_result.entities:
            print(f"\n🔍 First entity: {kg_result.entities[0].name}")
            print(f"   Type: {kg_result.entities[0].type}")
            print(f"   Properties: {kg_result.entities[0].properties}")
        
        if kg_result.relationships:
            print(f"\n🔍 First relationship: {kg_result.relationships[0].relationship_type}")
            print(f"   Source: {kg_result.relationships[0].source_entity}")
            print(f"   Target: {kg_result.relationships[0].target_entity}")
        
        return kg_result
        
    except Exception as e:
        print(f"❌ KG debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run all debug tests."""
    print("🚀 RETRIEVAL DEBUG SESSION")
    print("=" * 50)
    
    # Debug retrieval results
    retrieval_results = await debug_retrieval_results()
    
    # Debug vector store directly
    vector_results = await debug_vector_store_directly()
    
    # Debug KG directly
    kg_results = await debug_kg_directly()
    
    print("\n📊 DEBUG SUMMARY")
    print("=" * 30)
    print(f"   Retrieval results: {len(retrieval_results)}")
    print(f"   Vector store results: {len(vector_results)}")
    print(f"   KG has data: {'Yes' if kg_results and (kg_results.entities or kg_results.relationships) else 'No'}")

if __name__ == "__main__":
    asyncio.run(main())
