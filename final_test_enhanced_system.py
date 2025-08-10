#!/usr/bin/env python3
"""
Final test of enhanced HuggingFace and Ollama system
"""

import requests
import json

def test_enhanced_system():
    print("🧠 TESTING ENHANCED LLM SYSTEM")
    print("=" * 50)
    print("🎯 Features: HuggingFace free models, Ollama integration, zero-budget priority")
    print()
    
    # Test queries that should trigger different models/providers
    test_cases = [
        {
            "query": "What is artificial intelligence?",
            "expected": "HuggingFace GPT-2 or fallback",
            "type": "Q&A"
        },
        {
            "query": "How to implement binary search in Python?",
            "expected": "Ollama CodeLlama or HuggingFace",
            "type": "Programming"
        },
        {
            "query": "Explain machine learning concepts",
            "expected": "HuggingFace or Ollama",
            "type": "Educational"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"🔬 TEST {i}: {test['type']}")
        print(f"📝 Query: {test['query']}")
        print(f"🎯 Expected: {test['expected']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                "http://localhost:8000/search",
                json={"query": test["query"], "max_results": 2},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result["data"]
                answer = data["answer"]
                
                print(f"✅ Status: SUCCESS")
                print(f"⚡ Processing: {data['execution_time_ms']}ms")
                print(f"🧠 Complexity: {data['complexity']}")
                
                # Analyze response
                if len(answer) > 50 and not answer.startswith("Unable"):
                    print("✅ Real AI Response Generated")
                    print(f"📝 Length: {len(answer)} chars")
                    print(f"📄 Preview: {answer[:100]}...")
                else:
                    print("⚠️ Minimal/Fallback Response")
                    print(f"📝 Response: {answer}")
                
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("✅ Enhanced system testing complete!")

if __name__ == "__main__":
    test_enhanced_system()
