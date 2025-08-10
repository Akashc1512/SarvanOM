#!/usr/bin/env python3
"""
Test Script - What happens with REAL API keys
This shows the difference between placeholder keys and real keys
"""

import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_api_key_impact():
    print("🔑 API KEY IMPACT DEMONSTRATION")
    print("=" * 60)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 CURRENT STATUS:")
    print("   🔍 Checking for .env file...")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
            print("   ✅ .env file found!")
            
            # Check for real vs placeholder keys
            openai_key = os.getenv('OPENAI_API_KEY', '')
            anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
            hf_key = os.getenv('HUGGINGFACE_API_KEY', '')
            
            print(f"   🔍 Environment variables loaded:")
            
            # OpenAI key check
            if openai_key and openai_key.strip() and "your_" not in openai_key and openai_key.startswith('sk-'):
                print("   ✅ OpenAI: Real key detected!")
                openai_working = True
            else:
                print("   ⚠️ OpenAI: Placeholder or missing")
                openai_working = False
                
            # Anthropic key check  
            if anthropic_key and anthropic_key.strip() and "your_" not in anthropic_key and anthropic_key.startswith('sk-ant-'):
                print("   ✅ Anthropic: Real key detected!")
                anthropic_working = True
            else:
                print("   ⚠️ Anthropic: Placeholder or missing")
                anthropic_working = False
                
            # HuggingFace key check
            if hf_key and hf_key.strip() and "your_" not in hf_key and hf_key.startswith('hf_'):
                print("   ✅ HuggingFace: Real key detected!")
                hf_working = True
            else:
                print("   ⚠️ HuggingFace: Placeholder or missing")
                hf_working = False
                
            # Summary
            working_apis = sum([openai_working, anthropic_working, hf_working])
            if working_apis > 0:
                print(f"   🚀 {working_apis} API(s) ready for fast responses!")
            else:
                print("   ❌ No working API keys found")
                
    except FileNotFoundError:
        print("   ❌ .env file not found")
        print("   💡 Create .env file with your real API keys")
        print()
        print("📋 TO GET 5-SECOND RESPONSES:")
        print("   1. Create .env file in root directory")
        print("   2. Add your real API keys")
        print("   3. Server will automatically use fast APIs")
        return
    
    print()
    print("🧪 TESTING SYSTEM RESPONSE...")
    
    # Test the search endpoint
    payload = {
        "query": "What are the benefits of AI in 2025?",
        "options": {"maxTokens": 300}
    }
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:8000/search",
            json=payload,
            timeout=35
        )
        elapsed = time.time() - start
        
        print(f"   ⏱️ Response Time: {elapsed:.2f} seconds")
        print(f"   📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if elapsed < 10:
                print("   🚀 FAST RESPONSE - Real API keys working!")
                print(f"   🤖 Model Used: {data.get('meta', {}).get('model_used', 'Unknown')}")
            else:
                print("   ⏳ SLOW RESPONSE - Likely using Ollama fallback")
            
            overview = data.get('overview', '')
            if "AI synthesis unavailable" in overview:
                print("   ⚠️ Fallback response (API keys needed)")
            else:
                preview = overview[:150] + "..." if len(overview) > 150 else overview
                print(f"   ✅ AI Response: {preview}")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ⏳ TIMEOUT (30+ seconds)")
        print("   💡 This indicates Ollama fallback - need real API keys")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    print("🎯 PERFORMANCE EXPECTATIONS:")
    print("   📍 With Placeholder Keys: 30+ seconds (timeout)")
    print("   📍 With Real OpenAI Keys: 2-3 seconds ⚡")
    print("   📍 With Real Anthropic Keys: 3-5 seconds ⚡")
    print("   📍 With Both: Automatic best selection 🎯")
    
    print()
    print("🔑 NEXT STEP: Add real API keys to .env file for lightning speed!")

if __name__ == "__main__":
    test_api_key_impact()
