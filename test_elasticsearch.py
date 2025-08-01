#!/usr/bin/env python3
"""
Test Elasticsearch connection with provided credentials.
"""

import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

def test_elasticsearch():
    """Test Elasticsearch connection."""
    print("🔍 Testing Elasticsearch Connection...")
    print("=" * 50)
    
    # Get credentials from environment
    es_username = os.getenv("ELASTICSEARCH_USERNAME")
    es_password = os.getenv("ELASTICSEARCH_PASSWORD")
    es_index = os.getenv("ELASTICSEARCH_INDEX")
    
    # Use cloud URL if available, otherwise fallback to local
    cloud_url = os.getenv("ELASTICSEARCH_CLOUD_URL")
    local_url = os.getenv("ELASTICSEARCH_URL")
    
    if cloud_url:
        es_url = cloud_url
        print("🌩️ Using cloud Elasticsearch")
    elif local_url:
        es_url = local_url
        print("🏠 Using local Elasticsearch")
    else:
        print("❌ No Elasticsearch URL found")
        return False
    
    print(f"URL: {es_url}")
    print(f"Username: {es_username}")
    print(f"Index: {es_index}")
    print(f"Password: {'*' * len(es_password) if es_password else 'NOT SET'}")
    
    if not all([es_url, es_username, es_password]):
        print("❌ Missing Elasticsearch credentials")
        return False
    
    try:
        # Test basic connection
        auth = HTTPBasicAuth(es_username, es_password)
        response = requests.get(f"{es_url}/_cluster/health", auth=auth, timeout=10)
        
        if response.status_code == 200:
            print("✅ Elasticsearch connection successful")
            health_data = response.json()
            print(f"Cluster status: {health_data.get('status')}")
            print(f"Number of nodes: {health_data.get('number_of_nodes')}")
            return True
        else:
            print(f"❌ Elasticsearch connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Elasticsearch connection failed: {e}")
        return False

def test_index_creation():
    """Test if we can create and access the index."""
    print("\n📝 Testing Index Operations...")
    print("=" * 50)
    
    es_username = os.getenv("ELASTICSEARCH_USERNAME")
    es_password = os.getenv("ELASTICSEARCH_PASSWORD")
    es_index = os.getenv("ELASTICSEARCH_INDEX")
    
    # Use cloud URL if available, otherwise fallback to local
    cloud_url = os.getenv("ELASTICSEARCH_CLOUD_URL")
    local_url = os.getenv("ELASTICSEARCH_URL")
    
    if cloud_url:
        es_url = cloud_url
    elif local_url:
        es_url = local_url
    else:
        print("❌ No Elasticsearch URL found")
        return False
    
    if not all([es_url, es_username, es_password, es_index]):
        print("❌ Missing Elasticsearch credentials or index name")
        return False
    
    try:
        auth = HTTPBasicAuth(es_username, es_password)
        
        # Check if index exists
        response = requests.head(f"{es_url}/{es_index}", auth=auth, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Index '{es_index}' exists")
        elif response.status_code == 404:
            print(f"⚠️  Index '{es_index}' does not exist, creating...")
            
            # Create index
            index_settings = {
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "title": {"type": "text"},
                        "url": {"type": "keyword"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
            
            create_response = requests.put(
                f"{es_url}/{es_index}",
                json=index_settings,
                auth=auth,
                timeout=10
            )
            
            if create_response.status_code == 200:
                print(f"✅ Index '{es_index}' created successfully")
            else:
                print(f"❌ Failed to create index: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
        
        # Test document insertion
        test_doc = {
            "content": "This is a test document for SarvanOM",
            "title": "Test Document",
            "url": "https://example.com/test",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        doc_response = requests.post(
            f"{es_url}/{es_index}/_doc",
            json=test_doc,
            auth=auth,
            timeout=10
        )
        
        if doc_response.status_code in [200, 201]:
            print("✅ Document insertion successful")
            return True
        else:
            print(f"❌ Document insertion failed: {doc_response.status_code}")
            print(f"Response: {doc_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Index operations failed: {e}")
        return False

def main():
    """Run Elasticsearch tests."""
    print("🚀 Elasticsearch Connection Test")
    print("=" * 50)
    
    # Test basic connection
    connection_ok = test_elasticsearch()
    
    if connection_ok:
        # Test index operations
        index_ok = test_index_creation()
        
        if index_ok:
            print("\n🎉 Elasticsearch is fully configured and working!")
        else:
            print("\n⚠️  Elasticsearch connection works but index operations failed")
    else:
        print("\n❌ Elasticsearch connection failed")
    
    return connection_ok

if __name__ == "__main__":
    main() 