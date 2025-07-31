#!/usr/bin/env python3
"""Debug script to test authentication endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("Testing registration...")
    data = {
        "username": "debuguser2",
        "email": "debug2@test.com",
        "password": "debugpass123",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting login...")
    data = {
        "username": "debuguser2",
        "password": "debugpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login_existing():
    """Test login with existing user"""
    print("\nTesting login with existing user...")
    data = {
        "username": "debuguser",
        "password": "debugpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("\nTesting health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Authentication Endpoints")
    print("=" * 50)
    
    # Test health first
    health_ok = test_health()
    
    # Test registration
    register_ok = test_register()
    
    # Test login with new user
    login_ok = test_login()
    
    # Test login with existing user
    login_existing_ok = test_login_existing()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Register: {'✅' if register_ok else '❌'}")
    print(f"Login (new): {'✅' if login_ok else '❌'}")
    print(f"Login (existing): {'✅' if login_existing_ok else '❌'}") 