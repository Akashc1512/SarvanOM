#!/usr/bin/env python3
"""
Test Dynamic Model Selection
Validates the dynamic model selection functionality with various query types.

This script tests:
1. Model selection based on query complexity
2. Model selection based on query category
3. Fallback mechanisms
4. Cost optimization
5. Performance monitoring

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import asyncio
import logging
import sys
import os
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.model_selector import get_model_selector, ModelTier
from shared.core.query_classifier import QueryCategory, QueryComplexity
from shared.core.llm_client_v3 import get_llm_client_v3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicModelSelectionTester:
    """Test dynamic model selection with various query types."""

    def __init__(self):
        """Initialize the tester."""
        self.model_selector = get_model_selector()
        self.llm_client = get_llm_client_v3()

    async def test_simple_queries(self):
        """Test model selection for simple queries."""
        logger.info("Testing simple queries...")
        
        simple_queries = [
            "What is Python?",
            "How do I install pip?",
            "What is the capital of France?",
            "Define machine learning",
            "What is a database?"
        ]
        
        results = []
        for query in simple_queries:
            result = await self.model_selector.select_model(query, estimated_tokens=500)
            results.append({
                "query": query,
                "selected_model": result.selected_model,
                "tier": result.model_tier.value,
                "confidence": result.confidence,
                "estimated_cost": result.estimated_cost,
                "reasoning": result.reasoning
            })
            
            logger.info(f"Query: '{query[:30]}...' -> {result.selected_model} ({result.model_tier.value})")
        
        return results

    async def test_complex_queries(self):
        """Test model selection for complex queries."""
        logger.info("Testing complex queries...")
        
        complex_queries = [
            "Analyze the impact of artificial intelligence on modern software development practices, including ethical considerations and potential future developments",
            "Compare and contrast different approaches to implementing microservices architecture, including their trade-offs, best practices, and real-world applications",
            "Explain the theoretical foundations of quantum computing and its potential applications in cryptography, including current limitations and future prospects",
            "Investigate the relationship between climate change and technological innovation, examining how emerging technologies can both contribute to and mitigate environmental challenges",
            "Provide a comprehensive analysis of the evolution of programming languages from assembly to modern high-level languages, including design principles and paradigm shifts"
        ]
        
        results = []
        for query in complex_queries:
            result = await self.model_selector.select_model(query, estimated_tokens=2000)
            results.append({
                "query": query[:50] + "...",
                "selected_model": result.selected_model,
                "tier": result.model_tier.value,
                "confidence": result.confidence,
                "estimated_cost": result.estimated_cost,
                "reasoning": result.reasoning
            })
            
            logger.info(f"Query: '{query[:30]}...' -> {result.selected_model} ({result.model_tier.value})")
        
        return results

    async def test_code_queries(self):
        """Test model selection for code-related queries."""
        logger.info("Testing code-related queries...")
        
        code_queries = [
            "How do I implement authentication in React using JWT tokens?",
            "Write a Python function to sort a list of dictionaries by multiple keys",
            "Explain the difference between async/await and Promises in JavaScript",
            "How to deploy a Docker container to AWS ECS?",
            "What are the best practices for writing unit tests in Java?"
        ]
        
        results = []
        for query in code_queries:
            result = await self.model_selector.select_model(query, estimated_tokens=1500)
            results.append({
                "query": query[:50] + "...",
                "selected_model": result.selected_model,
                "tier": result.model_tier.value,
                "confidence": result.confidence,
                "estimated_cost": result.estimated_cost,
                "reasoning": result.reasoning
            })
            
            logger.info(f"Query: '{query[:30]}...' -> {result.selected_model} ({result.model_tier.value})")
        
        return results

    async def test_analytical_queries(self):
        """Test model selection for analytical queries."""
        logger.info("Testing analytical queries...")
        
        analytical_queries = [
            "Analyze the performance implications of using NoSQL vs SQL databases for a high-traffic web application",
            "Investigate the security vulnerabilities in modern web applications and propose mitigation strategies",
            "Examine the trade-offs between monolithic and microservices architectures in enterprise software development",
            "Study the impact of containerization on software deployment and maintenance processes",
            "Analyze the effectiveness of different machine learning algorithms for natural language processing tasks"
        ]
        
        results = []
        for query in analytical_queries:
            result = await self.model_selector.select_model(query, estimated_tokens=2500)
            results.append({
                "query": query[:50] + "...",
                "selected_model": result.selected_model,
                "tier": result.model_tier.value,
                "confidence": result.confidence,
                "estimated_cost": result.estimated_cost,
                "reasoning": result.reasoning
            })
            
            logger.info(f"Query: '{query[:30]}...' -> {result.selected_model} ({result.model_tier.value})")
        
        return results

    async def test_llm_generation_with_dynamic_selection(self):
        """Test actual LLM generation with dynamic model selection."""
        logger.info("Testing LLM generation with dynamic model selection...")
        
        test_queries = [
            ("What is Python?", "Simple factual query"),
            ("How do I implement a REST API in Node.js?", "Code-related query"),
            ("Analyze the benefits and drawbacks of microservices architecture", "Analytical query"),
            ("Compare React and Angular for building single-page applications", "Comparative query")
        ]
        
        results = []
        for query, description in test_queries:
            try:
                # Test with dynamic model selection
                response = await self.llm_client.generate_text(
                    prompt=f"Answer this question: {query}",
                    max_tokens=300,
                    temperature=0.2,
                    query=query,
                    use_dynamic_selection=True
                )
                
                results.append({
                    "query": query,
                    "description": description,
                    "response_length": len(response),
                    "success": True,
                    "response_preview": response[:100] + "..." if len(response) > 100 else response
                })
                
                logger.info(f"✅ Successfully generated response for '{query[:30]}...' (length: {len(response)})")
                
            except Exception as e:
                results.append({
                    "query": query,
                    "description": description,
                    "error": str(e),
                    "success": False
                })
                
                logger.error(f"❌ Failed to generate response for '{query[:30]}...': {e}")
        
        return results

    async def test_fallback_mechanisms(self):
        """Test fallback mechanisms when primary models fail."""
        logger.info("Testing fallback mechanisms...")
        
        # Test with a query that should trigger fallbacks
        query = "What is the difference between Python and JavaScript?"
        
        try:
            # Force a tier to test fallback behavior
            result = await self.model_selector.select_model(
                query, 
                estimated_tokens=1000,
                force_tier=ModelTier.POWERFUL
            )
            
            logger.info(f"Primary model: {result.selected_model}")
            logger.info(f"Fallback models: {result.fallback_models}")
            logger.info(f"Reasoning: {result.reasoning}")
            
            return {
                "primary_model": result.selected_model,
                "fallback_models": result.fallback_models,
                "reasoning": result.reasoning,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Fallback test failed: {e}")
            return {"error": str(e), "success": False}

    async def test_cost_optimization(self):
        """Test cost optimization features."""
        logger.info("Testing cost optimization...")
        
        # Test queries with different estimated token counts
        test_cases = [
            ("Short query", "What is AI?", 100),
            ("Medium query", "Explain machine learning algorithms", 500),
            ("Long query", "Provide a comprehensive analysis of modern software development practices", 2000)
        ]
        
        results = []
        for description, query, estimated_tokens in test_cases:
            result = await self.model_selector.select_model(query, estimated_tokens)
            
            results.append({
                "description": description,
                "query": query,
                "estimated_tokens": estimated_tokens,
                "selected_model": result.selected_model,
                "estimated_cost": result.estimated_cost,
                "tier": result.model_tier.value
            })
            
            logger.info(f"{description}: {result.selected_model} (${result.estimated_cost:.4f})")
        
        return results

    async def test_performance_metrics(self):
        """Test performance monitoring and metrics."""
        logger.info("Testing performance metrics...")
        
        # Run some queries to generate metrics
        test_queries = [
            "What is Python?",
            "How do I implement authentication?",
            "Analyze the benefits of microservices"
        ]
        
        for query in test_queries:
            await self.model_selector.select_model(query, estimated_tokens=500)
        
        # Get metrics
        metrics = self.model_selector.get_selection_metrics()
        
        logger.info("Performance Metrics:")
        logger.info(f"Total selections: {metrics.get('total_selections', 0)}")
        logger.info(f"Tier distribution: {metrics.get('tier_distribution', {})}")
        logger.info(f"Category distribution: {metrics.get('category_distribution', {})}")
        logger.info(f"Average selection time: {metrics.get('avg_selection_time_ms', 0):.2f}ms")
        logger.info(f"Total estimated cost: ${metrics.get('total_estimated_cost', 0):.4f}")
        logger.info(f"Average confidence: {metrics.get('avg_confidence', 0):.2f}")
        
        return metrics

    async def run_comprehensive_test(self):
        """Run comprehensive tests of dynamic model selection."""
        logger.info("Starting comprehensive dynamic model selection tests...")
        
        results = {
            "simple_queries": await self.test_simple_queries(),
            "complex_queries": await self.test_complex_queries(),
            "code_queries": await self.test_code_queries(),
            "analytical_queries": await self.test_analytical_queries(),
            "llm_generation": await self.test_llm_generation_with_dynamic_selection(),
            "fallback_mechanisms": await self.test_fallback_mechanisms(),
            "cost_optimization": await self.test_cost_optimization(),
            "performance_metrics": await self.test_performance_metrics()
        }
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("DYNAMIC MODEL SELECTION TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = 0
        successful_tests = 0
        
        for test_name, test_results in results.items():
            if isinstance(test_results, list):
                test_count = len(test_results)
                successful_count = len([r for r in test_results if r.get('success', True)])
                total_tests += test_count
                successful_tests += successful_count
                logger.info(f"{test_name}: {successful_count}/{test_count} successful")
            else:
                total_tests += 1
                if test_results.get('success', True):
                    successful_tests += 1
                logger.info(f"{test_name}: {'✅ PASS' if test_results.get('success', True) else '❌ FAIL'}")
        
        logger.info(f"\nOverall: {successful_tests}/{total_tests} tests successful")
        
        if successful_tests == total_tests:
            logger.info("🎉 All tests passed!")
        else:
            logger.warning(f"⚠️  {total_tests - successful_tests} tests failed")
        
        return results


async def main():
    """Main test function."""
    logger.info("Dynamic Model Selection Test Suite")
    logger.info("Testing intelligent model selection based on query characteristics")
    
    tester = DynamicModelSelectionTester()
    results = await tester.run_comprehensive_test()
    
    logger.info("\nTest completed!")
    return results


if __name__ == "__main__":
    asyncio.run(main()) 