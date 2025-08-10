#!/usr/bin/env python3
"""
Quick Ollama Status Check
"""

import requests
import json

def check_ollama():
    print("🔍 CHECKING OLLAMA STATUS")
    print("=" * 40)
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            model_names = [m["name"] for m in models.get("models", [])]
            print(f"📋 Available Models: {model_names}")
            
            if model_names:
                print("\n🧪 TESTING SIMPLE GENERATION")
                print("-" * 30)
                
                # Test with first model
                test_model = model_names[0]
                print(f"🎯 Testing: {test_model}")
                
                payload = {
                    "model": test_model,
                    "prompt": "Hi",
                    "stream": False
                }
                
                gen_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=30
                )
                
                print(f"📡 Generation Status: {gen_response.status_code}")
                
                if gen_response.status_code == 200:
                    result = gen_response.json()
                    response_text = result.get("response", "")
                    print(f"✅ Success! Response: {response_text[:100]}...")
                else:
                    print(f"❌ Generation Error: {gen_response.text}")
            else:
                print("❌ No models found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")

if __name__ == "__main__":
    check_ollama()
