#!/usr/bin/env python3
"""
Simple server test
"""
import socket
import requests
import time

def test_ports():
    """Test different ports to see if server is running."""
    ports = [8000, 8001, 8002, 8003, 8004]
    
    for port in ports:
        try:
            # Test if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} is open")
                # Try to connect with HTTP
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
                    print(f"✅ HTTP response from port {port}: {response.status_code}")
                    if response.status_code == 200:
                        print(f"   Response: {response.json()}")
                except Exception as e:
                    print(f"❌ HTTP failed on port {port}: {e}")
            else:
                print(f"❌ Port {port} is closed")
        except Exception as e:
            print(f"❌ Error testing port {port}: {e}")

if __name__ == "__main__":
    print("🔍 Testing server ports...")
    test_ports() 