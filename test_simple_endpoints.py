#!/usr/bin/env python3
"""
Simple endpoint test to identify response truncation issues.
"""

import requests
import json

def test_simple_endpoint():
    """Test a simple endpoint to identify issues."""
    try:
        # Test the docs endpoint first (we know this works)
        print("Testing /docs endpoint...")
        response = requests.get("http://localhost:8000/docs", timeout=10)
        print(f"Docs status: {response.status_code}, length: {len(response.text)}")
        
        # Test a simple health endpoint
        print("\nTesting /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health status: {response.status_code}")
        print(f"Health response length: {len(response.text)}")
        print(f"Health response preview: {response.text[:200]}...")
        
        # Test OpenAPI spec
        print("\nTesting /openapi.json endpoint...")
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        print(f"OpenAPI status: {response.status_code}")
        print(f"OpenAPI response length: {len(response.text)}")
        
        # Test search endpoint
        print("\nTesting /search endpoint...")
        response = requests.get("http://localhost:8000/search?q=test", timeout=10)
        print(f"Search status: {response.status_code}")
        print(f"Search response length: {len(response.text)}")
        print(f"Search response preview: {response.text[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()
