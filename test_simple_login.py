#!/usr/bin/env python3
"""Simple test to debug login endpoint"""

import requests
import json

def test_simple_login():
    """Test login with minimal data"""
    url = "http://localhost:8000/auth/login"
    headers = {"Content-Type": "application/json"}
    
    # Test with existing user
    data = {"username": "testuser_simple", "password": "test_password"}
    
    print(f"Testing login with data: {json.dumps(data, indent=2)}")
    
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

def test_register_new_user():
    """Register a new user for testing"""
    url = "http://localhost:8000/auth/register"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "username": "testuser_simple2",
        "email": "simple2@test.com",
        "password": "test_password",
        "role": "user"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Register Status: {response.status_code}")
        print(f"Register Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Register Error: {e}")
        return False

def test_raw_request():
    """Test with raw request data"""
    url = "http://localhost:8000/auth/login"
    headers = {"Content-Type": "application/json"}
    
    # Test with raw JSON string
    data = '{"username": "testuser_simple", "password": "test_password"}'
    
    print(f"Testing with raw data: {data}")
    
    try:
        response = requests.post(url, data=data, headers=headers)
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
    print("🔍 Simple Login Debug Test")
    print("=" * 40)
    
    # Try registration first
    register_success = test_register_new_user()
    
    # Test login with existing user
    print("\n✅ Testing login with existing user...")
    login_success = test_simple_login()
    
    if not login_success:
        print("\n🔄 Trying raw request...")
        test_raw_request() 