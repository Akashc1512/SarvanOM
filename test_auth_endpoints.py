#!/usr/bin/env python3
"""Test auth endpoints with correct OAuth2 format"""

import requests
import json

def test_oauth2_login():
    """Test login with OAuth2 form data format"""
    url = "http://localhost:8000/auth/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    # OAuth2 form data format
    data = {
        "username": "testuser_simple",
        "password": "test_password",
        "grant_type": "password"
    }
    
    print(f"Testing OAuth2 login with: {data}")
    
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

def test_register():
    """Test registration with JSON format"""
    url = "http://localhost:8000/auth/register"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "username": "testuser_oauth2",
        "email": "oauth2@test.com",
        "password": "test_password",
        "full_name": "Test User OAuth2"
    }
    
    print(f"Testing registration with: {json.dumps(data, indent=2)}")
    
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
    print("🔍 OAuth2 Auth Endpoints Test")
    print("=" * 40)
    
    # Test health first
    health_ok = test_health()
    print(f"Health: {'✅' if health_ok else '❌'}")
    
    # Test registration
    register_ok = test_register()
    print(f"Register: {'✅' if register_ok else '❌'}")
    
    # Test OAuth2 login
    login_ok = test_oauth2_login()
    print(f"OAuth2 Login: {'✅' if login_ok else '❌'}") 