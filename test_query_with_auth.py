#!/usr/bin/env python3
"""Test query endpoint with authentication"""

import requests
import json

def get_auth_token():
    """Get authentication token"""
    url = "http://localhost:8000/auth/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    data = {
        "username": "testuser_simple",
        "password": "simplepass123",
        "grant_type": "password"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_query_endpoint():
    """Test query endpoint with authentication"""
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    print(f"✅ Got auth token: {token[:20]}...")
    
    # Test query endpoint
    url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "query": "What is artificial intelligence?",
        "context": "General knowledge question"
    }
    
    print(f"Testing query with: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print("❌ FAILED")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_metrics_endpoint():
    """Test metrics endpoint with authentication"""
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    # Test metrics endpoint
    url = "http://localhost:8000/metrics"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("Testing metrics endpoint...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print("❌ FAILED")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Query and Metrics Test with Auth")
    print("=" * 40)
    
    # Test query endpoint
    query_ok = test_query_endpoint()
    print(f"Query: {'✅' if query_ok else '❌'}")
    
    # Test metrics endpoint
    metrics_ok = test_metrics_endpoint()
    print(f"Metrics: {'✅' if metrics_ok else '❌'}") 