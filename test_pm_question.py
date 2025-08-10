#!/usr/bin/env python3
"""
Test script to ask LLM about current PM of India's birthplace
"""

import requests
import json

def test_pm_question():
    """Test the LLM with a specific question about India's PM"""
    
    base_url = "http://localhost:8001"
    search_data = {
        "query": "What is the birth place of current PM of India?",
        "user_id": "test_user_123"
    }
    
    print("🔍 Asking LLM: 'What is the birth place of current PM of India?'")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{base_url}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"⏱️ Processing Time: {result.get('processing_time_ms', 0)}ms")
            print(f"🤖 AI Analysis:")
            print(json.dumps(result.get("ai_analysis", "No analysis available"), indent=2))
            print(f"📊 Query Classification: {result.get('query_classification', 'Unknown')}")
            print(f"🎯 Selected Provider: {result.get('selected_provider', 'Unknown')}")
            
            # Also test fact-check endpoint with the same question
            print("\n" + "=" * 60)
            print("🔍 Testing Fact-Check with the same question...")
            
            fact_check_data = {
                "content": "The current Prime Minister of India was born in Vadnagar, Gujarat",
                "user_id": "test_user_123",
                "context": "Fact checking about India's current PM birthplace"
            }
            
            fact_response = requests.post(
                f"{base_url}/fact-check",
                json=fact_check_data,
                headers={"Content-Type": "application/json"}
            )
            
            if fact_response.status_code == 200:
                fact_result = fact_response.json()
                print(f"✅ Fact-Check Status: {fact_response.status_code}")
                print(f"⏱️ Processing Time: {fact_result.get('processing_time_ms', 0)}ms")
                print(f"🔍 Verification Status: {fact_result.get('verification_status', 'Unknown')}")
                print(f"📊 Confidence Score: {fact_result.get('confidence_score', 0)}")
                print(f"🤖 Expert Analysis:")
                print(json.dumps(fact_result.get("verification_details", "No details available"), indent=2))
            else:
                print(f"❌ Fact-Check Error: {fact_response.status_code}")
                print(f"Response: {fact_response.text}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_pm_question()
