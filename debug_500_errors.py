#!/usr/bin/env python3
"""Debug script to identify 500 errors"""

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

def debug_query_endpoint():
    """Debug query endpoint"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "query": "What is artificial intelligence?",
        "context": "General knowledge question"
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("🔍 500 Error detected - checking response details...")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
        
    except Exception as e:
        print(f"Request Error: {e}")

def debug_metrics_endpoint():
    """Debug metrics endpoint"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    url = "http://localhost:8000/metrics"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("🔍 500 Error detected - checking response details...")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
        
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    print("🔍 Debugging 500 Errors")
    print("=" * 40)
    
    print("\n1. Debugging Query Endpoint...")
    debug_query_endpoint()
    
    print("\n2. Debugging Metrics Endpoint...")
    debug_metrics_endpoint() 