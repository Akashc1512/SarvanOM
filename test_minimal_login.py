#!/usr/bin/env python3
"""Minimal test to isolate login issue"""

import requests
import json

def test_minimal_login():
    """Test login with minimal setup"""
    url = "http://localhost:8000/auth/login"
    headers = {"Content-Type": "application/json"}
    
    # Test with a simple payload
    data = {"username": "testuser_simple", "password": "simplepass123"}
    
    print(f"Testing login with: {json.dumps(data)}")
    
    try:
        # Use requests with explicit data
        response = requests.post(url, data=json.dumps(data), headers=headers)
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

def test_health():
    """Test health endpoint for comparison"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        print(f"Health Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Minimal Login Test")
    print("=" * 30)
    
    # Test health first
    health_ok = test_health()
    print(f"Health: {'✅' if health_ok else '❌'}")
    
    # Test login
    login_ok = test_minimal_login()
    print(f"Login: {'✅' if login_ok else '❌'}") 