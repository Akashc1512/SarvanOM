#!/usr/bin/env python3
"""
Debug script to test frontend thoroughly.
"""

import requests
import time

def test_frontend_debug():
    """Debug frontend issues."""
    print("🔍 Frontend Debug Test")
    print("=" * 40)
    
    # Test different ports
    ports = [3000, 3001, 3002]
    
    for port in ports:
        url = f"http://localhost:{port}"
        print(f"\nTesting {url}...")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status Code: {response.status_code}")
            print(f"  Content Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"  Content Length: {len(response.text)}")
            print(f"  Has HTML: {'<html' in response.text.lower()}")
            print(f"  Has React: {'react' in response.text.lower()}")
            print(f"  Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms")
            
            if response.status_code == 200:
                print("  ✅ SUCCESS")
            else:
                print("  ❌ FAILED")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_frontend_debug() 