#!/usr/bin/env python3
"""
Test Meilisearch connection - Zero-budget Elasticsearch alternative.
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_meilisearch():
    """Test Meilisearch connection."""
    print("🔍 Testing Meilisearch Connection...")
    print("=" * 50)
    
    # Get Meilisearch configuration
    meili_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meili_master_key = os.getenv("MEILISEARCH_MASTER_KEY")
    
    print(f"URL: {meili_url}")
    print(f"Master Key: {'*' * len(meili_master_key) if meili_master_key else 'NOT SET'}")
    
    # Set headers for authentication if master key is provided
    headers = {}
    if meili_master_key:
        headers["Authorization"] = f"Bearer {meili_master_key}"
        print("🔐 Using master key authentication")
    else:
        print("🔓 No authentication required")
    
    try:
        # Test basic connection
        response = requests.get(f"{meili_url}/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Meilisearch connection successful")
            health_data = response.json()
            print(f"Status: {health_data.get('status', 'available')}")
            return True
        else:
            print(f"❌ Meilisearch connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Meilisearch connection failed: {e}")
        return False

def test_index_creation():
    """Test if we can create and access the index."""
    print("\n📝 Testing Index Operations...")
    print("=" * 50)
    
    meili_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meili_master_key = os.getenv("MEILISEARCH_MASTER_KEY")
    index_name = os.getenv("MEILISEARCH_INDEX", "knowledge_base")
    
    # Set headers for authentication if master key is provided
    headers = {"Content-Type": "application/json"}
    if meili_master_key:
        headers["Authorization"] = f"Bearer {meili_master_key}"
    
    try:
        # Check if index exists
        response = requests.get(f"{meili_url}/indexes/{index_name}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Index '{index_name}' exists")
            index_data = response.json()
            print(f"Primary Key: {index_data.get('primaryKey', 'id')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Index '{index_name}' does not exist, creating...")
            
            # Create index
            index_config = {
                "uid": index_name,
                "primaryKey": "id"
            }
            
            response = requests.post(
                f"{meili_url}/indexes",
                headers=headers,
                json=index_config,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ Index '{index_name}' created successfully")
                return True
            else:
                print(f"❌ Failed to create index: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Index operation failed: {e}")
        return False

def test_document_operations():
    """Test document operations (add, search, delete)."""
    print("\n📄 Testing Document Operations...")
    print("=" * 50)
    
    meili_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meili_master_key = os.getenv("MEILISEARCH_MASTER_KEY")
    index_name = os.getenv("MEILISEARCH_INDEX", "knowledge_base")
    
    # Set headers for authentication if master key is provided
    headers = {"Content-Type": "application/json"}
    if meili_master_key:
        headers["Authorization"] = f"Bearer {meili_master_key}"
    
    try:
        # Test document addition
        test_documents = [
            {
                "id": "test_1",
                "title": "Test Document 1",
                "content": "This is a test document for Meilisearch",
                "tags": ["test", "meilisearch"]
            },
            {
                "id": "test_2", 
                "title": "Test Document 2",
                "content": "Another test document with different content",
                "tags": ["test", "document"]
            }
        ]
        
        # Add documents
        response = requests.post(
            f"{meili_url}/indexes/{index_name}/documents",
            headers=headers,
            json=test_documents,
            timeout=10
        )
        
        if response.status_code == 202:
            print("✅ Documents added successfully")
            
            # Wait a moment for indexing
            import time
            time.sleep(1)
            
            # Test search
            search_query = {
                "q": "test document",
                "limit": 5
            }
            
            response = requests.post(
                f"{meili_url}/indexes/{index_name}/search",
                headers=headers,
                json=search_query,
                timeout=10
            )
            
            if response.status_code == 200:
                search_results = response.json()
                hits = search_results.get("hits", [])
                print(f"✅ Search successful - found {len(hits)} results")
                
                for i, hit in enumerate(hits[:2]):
                    print(f"   {i+1}. {hit.get('title', 'No title')} - Score: {hit.get('_score', 0)}")
                
                # Clean up test documents
                for doc in test_documents:
                    response = requests.delete(
                        f"{meili_url}/indexes/{index_name}/documents/{doc['id']}",
                        headers=headers,
                        timeout=10
                    )
                
                print("✅ Test documents cleaned up")
                return True
            else:
                print(f"❌ Search failed: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to add documents: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document operation failed: {e}")
        return False

def main():
    """Run Meilisearch tests."""
    print("🚀 Meilisearch Connection Test")
    print("=" * 50)
    
    # Test connection
    connection_ok = test_meilisearch()
    
    if connection_ok:
        # Test index operations
        index_ok = test_index_creation()
        
        if index_ok:
            # Test document operations
            doc_ok = test_document_operations()
            
            if doc_ok:
                print("\n🎉 Meilisearch is fully configured and working!")
                print("\n💡 Next steps:")
                print("   1. Update your .env file with MEILISEARCH_URL=http://localhost:7700")
                print("   2. Remove Elasticsearch from docker-compose.yml")
                print("   3. Add Meilisearch to your deployment scripts")
            else:
                print("\n⚠️  Meilisearch connection works but document operations failed")
        else:
            print("\n⚠️  Meilisearch connection works but index operations failed")
    else:
        print("\n❌ Meilisearch connection failed")
        print("\n💡 To start Meilisearch:")
        print("   docker run -p 7700:7700 getmeili/meilisearch:latest")

if __name__ == "__main__":
    main() 