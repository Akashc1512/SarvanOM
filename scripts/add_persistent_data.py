#!/usr/bin/env python3
"""
Add persistent data to vector store.
"""

import asyncio
import sys

# Add current directory to path
sys.path.append('.')

async def add_persistent_data():
    """Add persistent data to vector store."""
    print("📝 Adding persistent data to vector store...")
    
    try:
        from services.retrieval.main import VECTOR_STORE
        from shared.embeddings.local_embedder import embed_texts
        
        # Sample documents
        sample_documents = [
            {
                "id": "doc1",
                "text": "Artificial intelligence is a branch of computer science that aims to create intelligent machines.",
                "metadata": {
                    "title": "AI Introduction",
                    "source": "test_data",
                    "category": "technology"
                }
            },
            {
                "id": "doc2", 
                "text": "Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed.",
                "metadata": {
                    "title": "Machine Learning Basics",
                    "source": "test_data",
                    "category": "technology"
                }
            },
            {
                "id": "doc3",
                "text": "Deep learning uses neural networks with multiple layers to model complex patterns in data.",
                "metadata": {
                    "title": "Deep Learning",
                    "source": "test_data", 
                    "category": "technology"
                }
            },
            {
                "id": "doc4",
                "text": "Natural language processing enables computers to understand and generate human language.",
                "metadata": {
                    "title": "NLP Overview",
                    "source": "test_data",
                    "category": "technology"
                }
            },
            {
                "id": "doc5",
                "text": "Computer vision allows machines to interpret and understand visual information from the world.",
                "metadata": {
                    "title": "Computer Vision",
                    "source": "test_data",
                    "category": "technology"
                }
            }
        ]
        
        # Generate embeddings
        texts = [doc["text"] for doc in sample_documents]
        embeddings = embed_texts(texts)
        
        # Add documents to vector store
        success = await VECTOR_STORE.add_documents(sample_documents, embeddings)
        
        print(f"📊 Add documents success: {success}")
        
        if success:
            print("✅ Sample data added successfully")
            
            # Test search after adding data
            test_query = "artificial intelligence"
            query_embedding = embed_texts([test_query])[0]
            results = await VECTOR_STORE.search(query_embedding, top_k=5)
            
            print(f"📊 Search results after adding data: {len(results)}")
            
            # Show first result
            if results:
                first_result = results[0]
                print(f"🔍 First result: {first_result}")
            
            return len(results) > 0
        else:
            print("❌ Failed to add sample data")
            return False
        
    except Exception as e:
        print(f"❌ Add persistent data failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the script."""
    print("🚀 ADDING PERSISTENT DATA")
    print("=" * 40)
    
    success = await add_persistent_data()
    
    if success:
        print("✅ Data added successfully!")
    else:
        print("❌ Failed to add data")

if __name__ == "__main__":
    asyncio.run(main())
