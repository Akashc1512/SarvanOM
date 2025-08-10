#!/usr/bin/env python3
"""
Advanced test script for backend LLM integration with complex queries
"""

import requests
import json
import time

def test_advanced_llm_capabilities():
    """Test advanced LLM capabilities with complex queries"""
    
    base_url = "http://localhost:8001"
    
    print("🚀 Advanced LLM Integration Test")
    print("=" * 60)
    
    # Test 1: Complex Search Query
    print("\n1. Testing Complex Search Query...")
    complex_search = {
        "query": "Explain the differences between supervised and unsupervised learning in machine learning, with real-world examples",
        "user_id": "advanced_user_456",
        "filters": {"domain": "machine_learning", "complexity": "advanced"}
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/search",
            json=complex_search,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"✅ Complex Search: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Complex Search Failed: {e}")
    
    # Test 2: Advanced Fact Checking
    print("\n2. Testing Advanced Fact Checking...")
    complex_fact_check = {
        "content": "Quantum computers can solve all problems faster than classical computers and will replace traditional computers within 5 years.",
        "user_id": "advanced_user_456",
        "context": "Technology assessment for investment decisions"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/fact-check",
            json=complex_fact_check,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"✅ Advanced Fact Check: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Advanced Fact Check Failed: {e}")
    
    # Test 3: Multi-Source Synthesis
    print("\n3. Testing Multi-Source Synthesis...")
    synthesis_query = {
        "query": "Compare and contrast the environmental impacts of renewable energy sources (solar, wind, hydro) versus fossil fuels",
        "user_id": "advanced_user_456",
        "sources": [
            "https://www.epa.gov/energy",
            "https://www.iea.org/renewables",
            "https://www.nature.com/energy"
        ]
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/synthesize",
            json=synthesis_query,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"✅ Multi-Source Synthesis: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Multi-Source Synthesis Failed: {e}")
    
    # Test 4: Vector Search with Filters
    print("\n4. Testing Vector Search with Filters...")
    vector_query = {
        "query": "neural network architectures for natural language processing",
        "limit": 10,
        "user_id": "advanced_user_456",
        "filters": {
            "category": "ai_research",
            "date_range": "2023-2025",
            "relevance_threshold": 0.8
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/vector/search",
            json=vector_query,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"✅ Vector Search with Filters: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Vector Search Failed: {e}")
    
    # Test 5: Graph Context Analysis
    print("\n5. Testing Graph Context Analysis...")
    graph_query = {
        "topic": "artificial intelligence ethics",
        "depth": 3,
        "user_id": "advanced_user_456"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/graph/context",
            json=graph_query,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"✅ Graph Context Analysis: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Graph Context Analysis Failed: {e}")
    
    # Test 6: Detailed Analytics
    print("\n6. Testing Detailed Analytics...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/analytics/summary?time_range=7d")
        end_time = time.time()
        
        print(f"✅ Detailed Analytics: {response.status_code}")
        print(f"⏱️ Response Time: {(end_time - start_time):.2f}s")
        print(f"📊 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Detailed Analytics Failed: {e}")
    
    # Test 7: Performance Benchmark
    print("\n7. Performance Benchmark Test...")
    benchmark_queries = [
        "What is machine learning?",
        "Explain blockchain technology",
        "How does photosynthesis work?",
        "What are the benefits of exercise?",
        "Explain climate change"
    ]
    
    total_time = 0
    successful_requests = 0
    
    for i, query in enumerate(benchmark_queries, 1):
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/search",
                json={"query": query, "user_id": f"benchmark_user_{i}"},
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                successful_requests += 1
                total_time += (end_time - start_time)
                print(f"✅ Query {i}: {(end_time - start_time):.2f}s")
            else:
                print(f"❌ Query {i}: Failed (Status {response.status_code})")
                
        except Exception as e:
            print(f"❌ Query {i}: Error - {e}")
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"\n📈 Performance Summary:")
        print(f"   Successful Requests: {successful_requests}/{len(benchmark_queries)}")
        print(f"   Average Response Time: {avg_time:.2f}s")
        print(f"   Total Time: {total_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("🎯 Advanced LLM Integration Test Complete!")

if __name__ == "__main__":
    test_advanced_llm_capabilities()
