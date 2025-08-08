#!/usr/bin/env python3
"""
Test script for web crawl integration in retrieval process
"""

import asyncio
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_web_crawl_fallback():
    """Test web crawl fallback functionality."""
    
    print("🧪 Testing Web Crawl Integration")
    print("=" * 50)
    
    # Import the retrieval agent
    from shared.core.agents.retrieval_agent import RetrievalAgent
    
    # Initialize the retrieval agent
    retrieval_agent = RetrievalAgent()
    
    # Test queries that should trigger web crawl fallback
    test_queries = [
        {
            "query": "What are the latest developments in quantum computing?",
            "description": "Current events query - should trigger web crawl",
            "expected_web_crawl": True
        },
        {
            "query": "Latest news about artificial intelligence",
            "description": "News query with web keywords",
            "expected_web_crawl": True
        },
        {
            "query": "What is machine learning?",
            "description": "Basic factual query - may not need web crawl",
            "expected_web_crawl": False
        },
        {
            "query": "How to implement a REST API in Python",
            "description": "Technical query - should trigger web crawl",
            "expected_web_crawl": True
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        
        try:
            start_time = time.time()
            
            # Create task with web crawl enabled
            task = {
                "query": test_case["query"],
                "search_type": "hybrid",
                "enable_web_fallback": True,
                "web_fallback_timeout": 30,
                "max_web_pages": 3
            }
            
            # Create context
            from shared.core.agents.base_agent import QueryContext
            context = QueryContext(
                query=test_case["query"],
                user_context={"user_id": f"test_user_{i}"},
                trace_id=f"test_trace_{i}"
            )
            
            # Process the task
            result = await retrieval_agent.process_task(task, context)
            
            processing_time = time.time() - start_time
            
            # Analyze results
            if result.get("success", False):
                print(f"✅ Query processed successfully in {processing_time:.2f}s")
                
                data = result.get("data", {})
                metadata = data.get("metadata", {})
                
                # Check if web crawl was used
                web_crawl_used = metadata.get("web_crawl_used", False)
                print(f"   Web crawl used: {web_crawl_used}")
                
                if web_crawl_used:
                    print(f"   Web crawl documents: {metadata.get('web_crawl_documents', 0)}")
                    print(f"   Web crawl time: {metadata.get('web_crawl_time_ms', 0)}ms")
                    print(f"   Merged sources: {metadata.get('merged_sources', [])}")
                
                # Check documents
                documents = data.get("documents", [])
                print(f"   Total documents: {len(documents)}")
                
                # Check document sources
                local_docs = [doc for doc in documents if doc.get("metadata", {}).get("source_type") != "web_crawl"]
                web_docs = [doc for doc in documents if doc.get("metadata", {}).get("source_type") == "web_crawl"]
                
                print(f"   Local documents: {len(local_docs)}")
                print(f"   Web documents: {len(web_docs)}")
                
                # Check confidence
                confidence = result.get("confidence", 0.0)
                print(f"   Confidence: {confidence:.2f}")
                
                # Verify expectations
                if test_case["expected_web_crawl"] and web_crawl_used:
                    print("   ✅ Web crawl triggered as expected")
                elif not test_case["expected_web_crawl"] and not web_crawl_used:
                    print("   ✅ Web crawl not used as expected")
                elif test_case["expected_web_crawl"] and not web_crawl_used:
                    print("   ⚠️ Web crawl expected but not used")
                else:
                    print("   ⚠️ Web crawl used unexpectedly")
                
            else:
                print(f"❌ Query processing failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"✅ Web Crawl Integration Tests Completed!")

async def test_web_crawl_timeout():
    """Test web crawl timeout functionality."""
    
    print(f"\n⏱️ Testing Web Crawl Timeout")
    print("=" * 40)
    
    from shared.core.agents.retrieval_agent import RetrievalAgent
    
    retrieval_agent = RetrievalAgent()
    
    try:
        # Test with a very short timeout
        task = {
            "query": "Latest news about artificial intelligence",
            "search_type": "hybrid",
            "enable_web_fallback": True,
            "web_fallback_timeout": 1,  # Very short timeout
            "max_web_pages": 5
        }
        
        context = QueryContext(
            query=task["query"],
            user_context={"user_id": "timeout_test_user"},
            trace_id="timeout_test_trace"
        )
        
        start_time = time.time()
        result = await retrieval_agent.process_task(task, context)
        processing_time = time.time() - start_time
        
        print(f"Query: {task['query']}")
        print(f"Processing time: {processing_time:.2f}s")
        
        if result.get("success", False):
            print(f"✅ Query completed despite timeout")
            metadata = result.get("data", {}).get("metadata", {})
            web_crawl_used = metadata.get("web_crawl_used", False)
            print(f"   Web crawl used: {web_crawl_used}")
        else:
            print(f"❌ Query failed due to timeout")
            
    except Exception as e:
        print(f"❌ Timeout test error: {e}")

async def test_web_crawl_disabled():
    """Test behavior when web crawl is disabled."""
    
    print(f"\n🚫 Testing Web Crawl Disabled")
    print("=" * 40)
    
    from shared.core.agents.retrieval_agent import RetrievalAgent
    
    retrieval_agent = RetrievalAgent()
    
    try:
        # Test with web crawl disabled
        task = {
            "query": "Latest news about artificial intelligence",
            "search_type": "hybrid",
            "enable_web_fallback": False,  # Disable web crawl
            "web_fallback_timeout": 30,
            "max_web_pages": 5
        }
        
        context = QueryContext(
            query=task["query"],
            user_context={"user_id": "disabled_test_user"},
            trace_id="disabled_test_trace"
        )
        
        start_time = time.time()
        result = await retrieval_agent.process_task(task, context)
        processing_time = time.time() - start_time
        
        print(f"Query: {task['query']}")
        print(f"Processing time: {processing_time:.2f}s")
        
        if result.get("success", False):
            print(f"✅ Query completed without web crawl")
            metadata = result.get("data", {}).get("metadata", {})
            web_crawl_enabled = metadata.get("web_crawl_enabled", True)
            web_crawl_used = metadata.get("web_crawl_used", False)
            print(f"   Web crawl enabled: {web_crawl_enabled}")
            print(f"   Web crawl used: {web_crawl_used}")
            
            if not web_crawl_used:
                print("   ✅ Web crawl correctly disabled")
            else:
                print("   ⚠️ Web crawl used despite being disabled")
        else:
            print(f"❌ Query failed")
            
    except Exception as e:
        print(f"❌ Disabled test error: {e}")

async def test_standardized_pipeline_with_web_crawl():
    """Test the standardized pipeline with web crawl integration."""
    
    print(f"\n🔄 Testing Standardized Pipeline with Web Crawl")
    print("=" * 50)
    
    from shared.core.agents.lead_orchestrator import StandardizedLeadOrchestrator
    
    orchestrator = StandardizedLeadOrchestrator()
    
    # Test queries that should trigger web crawl
    test_queries = [
        {
            "query": "What are the latest developments in quantum computing?",
            "user_context": {"user_id": "pipeline_test_user_1", "model": "auto"},
            "description": "Current events query"
        },
        {
            "query": "Latest news about artificial intelligence",
            "user_context": {"user_id": "pipeline_test_user_2", "model": "gpt-4"},
            "description": "News query with web keywords"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Pipeline Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        
        try:
            start_time = time.time()
            
            # Process the query through the full pipeline
            result = await orchestrator.process_query(
                query=test_case["query"],
                user_context=test_case["user_context"]
            )
            
            processing_time = time.time() - start_time
            
            # Analyze results
            if result.get("success", False):
                print(f"✅ Pipeline completed successfully in {processing_time:.2f}s")
                
                # Check pipeline stages
                pipeline_stages = result.get("metadata", {}).get("pipeline_stages", [])
                print(f"   Pipeline stages: {pipeline_stages}")
                
                # Check if web crawl was used in retrieval
                stage_timings = result.get("metadata", {}).get("stage_timings", {})
                if "retrieval" in stage_timings:
                    print(f"   Retrieval time: {stage_timings['retrieval']:.3f}s")
                
                # Check answer quality
                answer = result.get("answer", "")
                confidence = result.get("confidence", 0.0)
                citations = result.get("citations", [])
                
                print(f"   Answer length: {len(answer)} characters")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Citations: {len(citations)}")
                
                # Check for web sources in citations
                web_citations = [cite for cite in citations if "http" in str(cite)]
                print(f"   Web citations: {len(web_citations)}")
                
                if web_citations:
                    print("   ✅ Web sources included in citations")
                else:
                    print("   ⚠️ No web sources in citations")
                
            else:
                print(f"❌ Pipeline failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Exception during pipeline processing: {e}")
    
    # Cleanup
    try:
        await orchestrator.shutdown()
        print(f"\n✅ Orchestrator shutdown completed")
    except Exception as e:
        print(f"\n❌ Error during shutdown: {e}")

async def main():
    """Run all web crawl integration tests."""
    print("🚀 Starting Web Crawl Integration Tests")
    
    await test_web_crawl_fallback()
    await test_web_crawl_timeout()
    await test_web_crawl_disabled()
    await test_standardized_pipeline_with_web_crawl()
    
    print(f"\n🎉 All web crawl integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 