import requests
import json

def test_with_real_data():
    """Test the backend with real data by indexing documents first."""
    
    print("🚀 Testing Backend with Real Data")
    print("=" * 50)
    
    # Step 1: Index some test documents
    print("\n📚 Step 1: Indexing test documents...")
    try:
        index_data = {
            "ids": ["doc1", "doc2", "doc3"],
            "texts": [
                "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can perform tasks that typically require human intelligence.",
                "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
                "Deep Learning is a type of machine learning that uses neural networks with multiple layers to model and understand complex patterns."
            ],
            "metadatas": [
                {"source": "AI_definition", "category": "technology"},
                {"source": "ML_definition", "category": "technology"},
                {"source": "DL_definition", "category": "technology"}
            ]
        }
        
        response = requests.post("http://localhost:8002/index", json=index_data)
        print(f"Index Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Indexed {result.get('upserted', 0)} documents")
        else:
            print(f"Index failed: {response.text}")
    except Exception as e:
        print(f"Index error: {e}")
    
    # Step 2: Test retrieval with real data
    print("\n🔍 Step 2: Testing retrieval with real data...")
    try:
        search_data = {
            "query": "What is artificial intelligence?",
            "max_results": 5,
            "context": {"user_id": "test"}
        }
        
        response = requests.post("http://localhost:8002/search", json=search_data)
        print(f"Search Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Total results: {result.get('total_results', 0)}")
            print(f"Sources: {len(result.get('sources', []))}")
            if result.get('sources'):
                print("✅ Real vector search working!")
                for i, source in enumerate(result.get('sources', [])[:2]):
                    print(f"  Source {i+1}: {source.get('content', '')[:100]}...")
            else:
                print("⚠️ No sources found - still using fallback")
        else:
            print(f"Search failed: {response.text}")
    except Exception as e:
        print(f"Search error: {e}")
    
    # Step 3: Test complete query through API Gateway
    print("\n🌐 Step 3: Testing complete query through API Gateway...")
    try:
        query_data = {
            "query": "What is artificial intelligence?",
            "max_tokens": 200,
            "confidence_threshold": 0.7
        }
        
        response = requests.post("http://localhost:8000/query", json=query_data)
        print(f"Query Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            if result.get('success'):
                print("🎉 REAL BACKEND RESPONSE RECEIVED!")
                print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
                print(f"Sources: {len(result.get('citations', []))}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"Query failed: {response.text}")
    except Exception as e:
        print(f"Query error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Real Data Testing Complete")

if __name__ == "__main__":
    test_with_real_data()
