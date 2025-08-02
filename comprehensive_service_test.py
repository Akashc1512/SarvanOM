#!/usr/bin/env python3
"""
Comprehensive test for multi-source retrieval services.
Tests each service individually and confirms they respond to real queries.
"""

import asyncio
import logging
import sys
import os
import time
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.search_service.retrieval_agent import RetrievalAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceHealthChecker:
    """Check health and connectivity of all services."""
    
    def __init__(self):
        self.agent = RetrievalAgent()
        self.results = {}
    
    async def check_vector_search(self) -> Dict[str, Any]:
        """Test vector search service."""
        print("\n🔍 Testing Vector Search Service...")
        
        try:
            start_time = time.time()
            result = await self.agent.vector_search("machine learning", top_k=5)
            query_time = (time.time() - start_time) * 1000
            
            status = {
                "connected": True,
                "query_time_ms": query_time,
                "results_count": len(result.documents),
                "search_type": result.search_type,
                "error": None
            }
            
            if result.documents:
                print(f"✅ Vector Search: {len(result.documents)} results in {query_time:.2f}ms")
                print(f"   Top result: {result.documents[0].content[:100]}...")
            else:
                print(f"⚠️ Vector Search: No results returned")
                
        except Exception as e:
            status = {
                "connected": False,
                "query_time_ms": 0,
                "results_count": 0,
                "search_type": "vector",
                "error": str(e)
            }
            print(f"❌ Vector Search failed: {e}")
        
        self.results["vector_search"] = status
        return status
    
    async def check_meilisearch(self) -> Dict[str, Any]:
        """Test Meilisearch service."""
        print("\n🔍 Testing Meilisearch Service...")
        
        try:
            start_time = time.time()
            result = await self.agent.meilisearch_search("artificial intelligence", top_k=5)
            query_time = (time.time() - start_time) * 1000
            
            status = {
                "connected": True,
                "query_time_ms": query_time,
                "results_count": len(result.documents),
                "search_type": result.search_type,
                "error": None
            }
            
            if result.documents:
                print(f"✅ Meilisearch: {len(result.documents)} results in {query_time:.2f}ms")
                print(f"   Top result: {result.documents[0].content[:100]}...")
            else:
                print(f"⚠️ Meilisearch: No results returned")
                
        except Exception as e:
            status = {
                "connected": False,
                "query_time_ms": 0,
                "results_count": 0,
                "search_type": "meilisearch",
                "error": str(e)
            }
            print(f"❌ Meilisearch failed: {e}")
        
        self.results["meilisearch"] = status
        return status
    
    async def check_arangodb_graph(self) -> Dict[str, Any]:
        """Test ArangoDB graph search service."""
        print("\n🔍 Testing ArangoDB Graph Search Service...")
        
        try:
            start_time = time.time()
            result = await self.agent.arangodb_graph_search("machine learning", top_k=5)
            query_time = (time.time() - start_time) * 1000
            
            status = {
                "connected": True,
                "query_time_ms": query_time,
                "results_count": len(result.documents),
                "search_type": result.search_type,
                "error": None
            }
            
            if result.documents:
                print(f"✅ ArangoDB Graph: {len(result.documents)} results in {query_time:.2f}ms")
                print(f"   Top result: {result.documents[0].content[:100]}...")
            else:
                print(f"⚠️ ArangoDB Graph: No results returned")
                
        except Exception as e:
            status = {
                "connected": False,
                "query_time_ms": 0,
                "results_count": 0,
                "search_type": "arangodb_graph",
                "error": str(e)
            }
            print(f"❌ ArangoDB Graph failed: {e}")
        
        self.results["arangodb_graph"] = status
        return status
    
    async def check_elasticsearch(self) -> Dict[str, Any]:
        """Test Elasticsearch service."""
        print("\n🔍 Testing Elasticsearch Service...")
        
        try:
            start_time = time.time()
            result = await self.agent.keyword_search("deep learning", top_k=5)
            query_time = (time.time() - start_time) * 1000
            
            status = {
                "connected": True,
                "query_time_ms": query_time,
                "results_count": len(result.documents),
                "search_type": result.search_type,
                "error": None
            }
            
            if result.documents:
                print(f"✅ Elasticsearch: {len(result.documents)} results in {query_time:.2f}ms")
                print(f"   Top result: {result.documents[0].content[:100]}...")
            else:
                print(f"⚠️ Elasticsearch: No results returned")
                
        except Exception as e:
            status = {
                "connected": False,
                "query_time_ms": 0,
                "results_count": 0,
                "search_type": "keyword",
                "error": str(e)
            }
            print(f"❌ Elasticsearch failed: {e}")
        
        self.results["elasticsearch"] = status
        return status
    
    async def check_web_search(self) -> Dict[str, Any]:
        """Test web search service."""
        print("\n🔍 Testing Web Search Service...")
        
        try:
            start_time = time.time()
            result = await self.agent.web_search("latest AI developments", top_k=3)
            query_time = (time.time() - start_time) * 1000
            
            status = {
                "connected": True,
                "query_time_ms": query_time,
                "results_count": len(result.documents),
                "search_type": result.search_type,
                "error": None
            }
            
            if result.documents:
                print(f"✅ Web Search: {len(result.documents)} results in {query_time:.2f}ms")
                print(f"   Top result: {result.documents[0].content[:100]}...")
            else:
                print(f"⚠️ Web Search: No results returned")
                
        except Exception as e:
            status = {
                "connected": False,
                "query_time_ms": 0,
                "results_count": 0,
                "search_type": "web_search",
                "error": str(e)
            }
            print(f"❌ Web Search failed: {e}")
        
        self.results["web_search"] = status
        return status


async def test_real_queries():
    """Test real queries with hybrid retrieval."""
    print("\n🧪 Testing Real Queries with Hybrid Retrieval")
    print("=" * 60)
    
    agent = RetrievalAgent()
    
    # Real-world test queries
    test_queries = [
        "What is the difference between machine learning and deep learning?",
        "How does Python compare to JavaScript for web development?",
        "Explain the relationship between Docker and Kubernetes",
        "What are the latest developments in artificial intelligence?",
        "How do neural networks work in image recognition?",
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = await agent.hybrid_retrieve(query)
            query_time = (time.time() - start_time) * 1000
            
            print(f"✅ Completed in {query_time:.2f}ms")
            print(f"📊 Total results: {result.total_hits}")
            print(f"🎯 Search type: {result.search_type}")
            
            # Show strategies used
            if result.metadata and 'strategies_used' in result.metadata:
                strategies = result.metadata['strategies_used']
                print(f"🔧 Strategies used: {', '.join(strategies)}")
            
            # Show top 2 results
            print(f"\n📄 Top 2 results:")
            for j, doc in enumerate(result.documents[:2], 1):
                print(f"  {j}. [{doc.source}] Score: {doc.score:.3f}")
                print(f"     {doc.content[:150]}...")
                print()
            
            results.append({
                "query": query,
                "success": True,
                "query_time_ms": query_time,
                "total_hits": result.total_hits,
                "strategies_used": result.metadata.get('strategies_used', []) if result.metadata else []
            })
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    return results


async def test_entity_extraction():
    """Test entity extraction with real queries."""
    print("\n🧪 Testing Entity Extraction")
    print("=" * 40)
    
    agent = RetrievalAgent()
    
    test_queries = [
        "What is the relationship between machine learning and artificial intelligence?",
        "How does Python compare to JavaScript for web development?",
        "Explain the differences between Docker containers and Kubernetes orchestration",
        "What are neural networks and how do they work?",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            entities = await agent._extract_entities(query)
            print(f"✅ Extracted {len(entities)} entities:")
            for entity in entities:
                print(f"  - {entity['text']} ({entity['type']}, confidence: {entity['confidence']:.2f})")
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")


async def generate_service_report(health_checker: ServiceHealthChecker, query_results: List[Dict[str, Any]]):
    """Generate a comprehensive service report."""
    print("\n📊 COMPREHENSIVE SERVICE REPORT")
    print("=" * 60)
    
    # Service Health Summary
    print("\n🔧 SERVICE HEALTH SUMMARY:")
    print("-" * 30)
    
    connected_services = 0
    total_services = len(health_checker.results)
    
    for service_name, status in health_checker.results.items():
        status_icon = "✅" if status["connected"] else "❌"
        print(f"{status_icon} {service_name.upper()}: {'Connected' if status['connected'] else 'Failed'}")
        if status["connected"]:
            connected_services += 1
            print(f"   - Query time: {status['query_time_ms']:.2f}ms")
            print(f"   - Results: {status['results_count']}")
        else:
            print(f"   - Error: {status['error']}")
        print()
    
    print(f"📈 Overall Health: {connected_services}/{total_services} services connected")
    
    # Query Performance Summary
    print("\n🔍 QUERY PERFORMANCE SUMMARY:")
    print("-" * 30)
    
    successful_queries = sum(1 for r in query_results if r["success"])
    total_queries = len(query_results)
    
    if successful_queries > 0:
        avg_query_time = sum(r["query_time_ms"] for r in query_results if r["success"]) / successful_queries
        print(f"✅ Successful queries: {successful_queries}/{total_queries}")
        print(f"⏱️ Average query time: {avg_query_time:.2f}ms")
        
        # Strategy usage analysis
        all_strategies = []
        for result in query_results:
            if result["success"]:
                all_strategies.extend(result.get("strategies_used", []))
        
        if all_strategies:
            strategy_counts = {}
            for strategy in all_strategies:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            print(f"🔧 Strategy usage:")
            for strategy, count in strategy_counts.items():
                percentage = (count / len(query_results)) * 100
                print(f"   - {strategy}: {count} times ({percentage:.1f}%)")
    else:
        print("❌ No successful queries")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 20)
    
    if connected_services == total_services:
        print("✅ All services are connected and working properly!")
    elif connected_services > total_services / 2:
        print("⚠️ Most services are working, but some may need attention.")
    else:
        print("❌ Multiple services are failing. Check service configurations.")
    
    if successful_queries == total_queries:
        print("✅ All test queries completed successfully!")
    elif successful_queries > 0:
        print("⚠️ Some queries failed, but the system is partially functional.")
    else:
        print("❌ All queries failed. Check service connectivity and configurations.")


async def main():
    """Run comprehensive service tests."""
    print("🚀 COMPREHENSIVE SERVICE TEST")
    print("=" * 60)
    
    # Initialize health checker
    health_checker = ServiceHealthChecker()
    
    # Test individual services
    print("\n🔧 Testing Individual Services...")
    await health_checker.check_vector_search()
    await health_checker.check_meilisearch()
    await health_checker.check_arangodb_graph()
    await health_checker.check_elasticsearch()
    await health_checker.check_web_search()
    
    # Test entity extraction
    await test_entity_extraction()
    
    # Test real queries
    query_results = await test_real_queries()
    
    # Generate comprehensive report
    await generate_service_report(health_checker, query_results)
    
    print("\n🎉 Comprehensive service test completed!")


if __name__ == "__main__":
    asyncio.run(main()) 