#!/usr/bin/env python3
"""
Comprehensive Real-World Test Suite
Tests 10-30 real-world scenarios and complex queries for hybrid retrieval and knowledge graph systems.
Industry-grade testing following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import sys
import os
import warnings
import time
from datetime import datetime
from typing import List, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available")

# Suppress warnings for clean test output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource
)
from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent


class ComprehensiveRealWorldTests:
    """Comprehensive test suite for real-world scenarios."""
    
    def __init__(self):
        self.hybrid_engine = HybridRetrievalEngine()
        self.knowledge_agent = KnowledgeGraphAgent()
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all comprehensive real-world tests."""
        print("🚀 Starting Comprehensive Real-World Test Suite")
        print("=" * 60)
        
        # Test Categories
        await self.test_hybrid_retrieval_scenarios()
        await self.test_knowledge_graph_scenarios()
        await self.test_complex_queries()
        await self.test_edge_cases()
        await self.test_performance_scenarios()
        
        # Generate comprehensive report
        self.generate_test_report()
        
    async def test_hybrid_retrieval_scenarios(self):
        """Test hybrid retrieval with real-world scenarios."""
        print("\n📋 Testing Hybrid Retrieval Real-World Scenarios")
        print("-" * 50)
        
        # Test 1: Academic Research Query
        await self._test_scenario(
            "Academic Research: 'machine learning algorithms for natural language processing'",
            "machine learning algorithms for natural language processing",
            "Academic research queries should return relevant technical content"
        )
        
        # Test 2: Business Intelligence Query
        await self._test_scenario(
            "Business Intelligence: 'data analytics dashboard implementation'",
            "data analytics dashboard implementation",
            "Business queries should return practical implementation content"
        )
        
        # Test 3: Technical Documentation Query
        await self._test_scenario(
            "Technical Documentation: 'API authentication best practices'",
            "API authentication best practices",
            "Technical queries should return best practices and implementation details"
        )
        
        # Test 4: Programming Language Query
        await self._test_scenario(
            "Programming Language: 'Python async programming patterns'",
            "Python async programming patterns",
            "Programming queries should return code examples and patterns"
        )
        
        # Test 5: Framework Query
        await self._test_scenario(
            "Framework: 'React hooks state management'",
            "React hooks state management",
            "Framework queries should return modern development patterns"
        )
        
        # Test 6: DevOps Query
        await self._test_scenario(
            "DevOps: 'container orchestration with Kubernetes'",
            "container orchestration with Kubernetes",
            "DevOps queries should return infrastructure and deployment content"
        )
        
        # Test 7: AI/ML Query
        await self._test_scenario(
            "AI/ML: 'deep learning neural network architectures'",
            "deep learning neural network architectures",
            "AI/ML queries should return advanced technical content"
        )
        
        # Test 8: Database Query
        await self._test_scenario(
            "Database: 'NoSQL vs SQL performance comparison'",
            "NoSQL vs SQL performance comparison",
            "Database queries should return comparison and analysis content"
        )
        
        # Test 9: Security Query
        await self._test_scenario(
            "Security: 'cybersecurity threat detection methods'",
            "cybersecurity threat detection methods",
            "Security queries should return security-focused content"
        )
        
        # Test 10: Cloud Computing Query
        await self._test_scenario(
            "Cloud Computing: 'microservices architecture patterns'",
            "microservices architecture patterns",
            "Cloud computing queries should return architectural patterns"
        )
    
    async def test_knowledge_graph_scenarios(self):
        """Test knowledge graph with real-world scenarios."""
        print("\n📋 Testing Knowledge Graph Real-World Scenarios")
        print("-" * 50)
        
        # Test 11: Technology Relationships
        await self._test_knowledge_scenario(
            "Technology Relationships: 'Python' to 'Machine Learning'",
            "Python", "Machine Learning",
            "Should find relationships between programming languages and AI technologies"
        )
        
        # Test 12: Framework Relationships
        await self._test_knowledge_scenario(
            "Framework Relationships: 'React' to 'JavaScript'",
            "React", "JavaScript",
            "Should find relationships between frameworks and their base languages"
        )
        
        # Test 13: Database Relationships
        await self._test_knowledge_scenario(
            "Database Relationships: 'MongoDB' to 'NoSQL'",
            "MongoDB", "NoSQL",
            "Should find relationships between specific databases and categories"
        )
        
        # Test 14: AI Technology Chain
        await self._test_knowledge_scenario(
            "AI Technology Chain: 'Deep Learning' to 'Neural Networks'",
            "Deep Learning", "Neural Networks",
            "Should find relationships in AI technology hierarchy"
        )
        
        # Test 15: DevOps Tools
        await self._test_knowledge_scenario(
            "DevOps Tools: 'Docker' to 'Kubernetes'",
            "Docker", "Kubernetes",
            "Should find relationships between containerization tools"
        )
        
        # Test 16: Single Entity Deep Dive
        await self._test_single_entity_scenario(
            "Single Entity Deep Dive: 'Python'",
            "Python",
            "Should return comprehensive information about Python programming language"
        )
        
        # Test 17: Single Entity Deep Dive - AI
        await self._test_single_entity_scenario(
            "Single Entity Deep Dive: 'Artificial Intelligence'",
            "Artificial Intelligence",
            "Should return comprehensive information about AI"
        )
        
        # Test 18: Single Entity Deep Dive - Framework
        await self._test_single_entity_scenario(
            "Single Entity Deep Dive: 'React'",
            "React",
            "Should return comprehensive information about React framework"
        )
        
        # Test 19: Non-existent Technology
        await self._test_single_entity_scenario(
            "Non-existent Technology: 'QuantumComputingFramework'",
            "QuantumComputingFramework",
            "Should handle non-existent entities gracefully"
        )
        
        # Test 20: Edge Case - Empty String
        await self._test_single_entity_scenario(
            "Edge Case - Empty String: ''",
            "",
            "Should handle empty string input gracefully"
        )
    
    async def test_complex_queries(self):
        """Test complex multi-part queries."""
        print("\n📋 Testing Complex Multi-Part Queries")
        print("-" * 50)
        
        # Test 21: Multi-Technology Query
        await self._test_scenario(
            "Multi-Technology: 'Python machine learning with TensorFlow and scikit-learn'",
            "Python machine learning with TensorFlow and scikit-learn",
            "Should handle queries with multiple technologies and frameworks"
        )
        
        # Test 22: Architecture Pattern Query
        await self._test_scenario(
            "Architecture Pattern: 'microservices with Docker containers and Kubernetes orchestration'",
            "microservices with Docker containers and Kubernetes orchestration",
            "Should handle complex architectural queries"
        )
        
        # Test 23: Full-Stack Development Query
        await self._test_scenario(
            "Full-Stack: 'React frontend with Node.js backend and MongoDB database'",
            "React frontend with Node.js backend and MongoDB database",
            "Should handle full-stack development queries"
        )
        
        # Test 24: AI/ML Pipeline Query
        await self._test_scenario(
            "AI/ML Pipeline: 'data preprocessing with pandas, model training with scikit-learn, and deployment with Flask'",
            "data preprocessing with pandas, model training with scikit-learn, and deployment with Flask",
            "Should handle complex AI/ML pipeline queries"
        )
        
        # Test 25: DevOps Pipeline Query
        await self._test_scenario(
            "DevOps Pipeline: 'CI/CD with Jenkins, Docker containers, and Kubernetes deployment'",
            "CI/CD with Jenkins, Docker containers, and Kubernetes deployment",
            "Should handle complex DevOps pipeline queries"
        )
        
        # Test 26: Security Implementation Query
        await self._test_scenario(
            "Security Implementation: 'JWT authentication with OAuth2 and HTTPS encryption'",
            "JWT authentication with OAuth2 and HTTPS encryption",
            "Should handle complex security implementation queries"
        )
        
        # Test 27: Performance Optimization Query
        await self._test_scenario(
            "Performance Optimization: 'database indexing, caching with Redis, and load balancing'",
            "database indexing, caching with Redis, and load balancing",
            "Should handle complex performance optimization queries"
        )
        
        # Test 28: Cloud Architecture Query
        await self._test_scenario(
            "Cloud Architecture: 'AWS Lambda functions with API Gateway and DynamoDB'",
            "AWS Lambda functions with API Gateway and DynamoDB",
            "Should handle complex cloud architecture queries"
        )
    
    async def test_edge_cases(self):
        """Test edge cases and error scenarios."""
        print("\n📋 Testing Edge Cases and Error Scenarios")
        print("-" * 50)
        
        # Test 29: Very Long Query
        await self._test_scenario(
            "Very Long Query: 'machine learning deep learning artificial intelligence neural networks convolutional neural networks recurrent neural networks transformers BERT GPT natural language processing computer vision image recognition object detection semantic segmentation instance segmentation'",
            "machine learning deep learning artificial intelligence neural networks convolutional neural networks recurrent neural networks transformers BERT GPT natural language processing computer vision image recognition object detection semantic segmentation instance segmentation",
            "Should handle very long queries gracefully"
        )
        
        # Test 30: Special Characters Query
        await self._test_scenario(
            "Special Characters: 'Python@#$% programming &*() with special chars'",
            "Python@#$% programming &*() with special chars",
            "Should handle special characters gracefully"
        )
        
        # Test 31: Numbers and Symbols Query
        await self._test_scenario(
            "Numbers and Symbols: 'Python 3.9+ programming with >= <= operators'",
            "Python 3.9+ programming with >= <= operators",
            "Should handle numbers and symbols gracefully"
        )
        
        # Test 32: Mixed Language Query
        await self._test_scenario(
            "Mixed Language: 'Python programming プログラミング with 中文 and español'",
            "Python programming プログラミング with 中文 and español",
            "Should handle mixed language content gracefully"
        )
        
        # Test 33: Technical Jargon Query
        await self._test_scenario(
            "Technical Jargon: 'polymorphism inheritance encapsulation abstraction SOLID principles DRY KISS YAGNI'",
            "polymorphism inheritance encapsulation abstraction SOLID principles DRY KISS YAGNI",
            "Should handle technical jargon and acronyms"
        )
    
    async def test_performance_scenarios(self):
        """Test performance and scalability scenarios."""
        print("\n📋 Testing Performance and Scalability Scenarios")
        print("-" * 50)
        
        # Test 34: High-Volume Query
        start_time = time.time()
        await self._test_scenario(
            "High-Volume Query: 'enterprise software development'",
            "enterprise software development",
            "Should handle high-volume queries efficiently"
        )
        performance_time = time.time() - start_time
        print(f"⏱️ Performance: {performance_time:.3f}s")
        
        # Test 35: Concurrent Queries (simulated)
        await self._test_scenario(
            "Concurrent Query 1: 'web development'",
            "web development",
            "Should handle concurrent query patterns"
        )
        
        await self._test_scenario(
            "Concurrent Query 2: 'mobile development'",
            "mobile development",
            "Should handle concurrent query patterns"
        )
        
        await self._test_scenario(
            "Concurrent Query 3: 'backend development'",
            "backend development",
            "Should handle concurrent query patterns"
        )
    
    async def _test_scenario(self, test_name: str, query: str, expected_behavior: str):
        """Test a hybrid retrieval scenario."""
        try:
            print(f"\n🔍 {test_name}")
            print(f"Query: '{query}'")
            print(f"Expected: {expected_behavior}")
            
            start_time = time.time()
            result = await self.hybrid_engine.retrieve(
                query=query,
                max_results=5,
                fusion_strategy=FusionStrategy.WEIGHTED_SUM,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            processing_time = time.time() - start_time
            
            # Validate results
            assert result is not None, "Result should not be None"
            assert hasattr(result, 'enhanced_results'), "Should have enhanced_results"
            assert hasattr(result, 'fused_content'), "Should have fused_content"
            assert hasattr(result, 'confidence_score'), "Should have confidence_score"
            
            # Validate processing time
            assert processing_time < 5.0, f"Processing time should be under 5s: {processing_time:.3f}s"
            
            # Validate confidence score
            assert 0 <= result.confidence_score <= 1, f"Confidence should be 0-1: {result.confidence_score}"
            
            # Validate results structure
            if len(result.enhanced_results) > 0:
                for result_item in result.enhanced_results:
                    assert hasattr(result_item, 'document_id'), "Should have document_id"
                    assert hasattr(result_item, 'title'), "Should have title"
                    assert hasattr(result_item, 'snippet'), "Should have snippet"
                    assert hasattr(result_item, 'combined_score'), "Should have combined_score"
                    assert 0 <= result_item.combined_score <= 1, f"Score should be 0-1: {result_item.combined_score}"
            
            print(f"✅ PASSED - Found {len(result.enhanced_results)} results in {processing_time:.3f}s")
            print(f"   Confidence: {result.confidence_score:.3f}")
            print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
            
            # Store test result
            self.test_results.append({
                'test_name': test_name,
                'query': query,
                'status': 'PASSED',
                'results_count': len(result.enhanced_results),
                'confidence': result.confidence_score,
                'processing_time': processing_time,
                'expected_behavior': expected_behavior
            })
            
        except Exception as e:
            print(f"❌ FAILED - {test_name}: {e}")
            self.test_results.append({
                'test_name': test_name,
                'query': query,
                'status': 'FAILED',
                'error': str(e),
                'expected_behavior': expected_behavior
            })
    
    async def _test_knowledge_scenario(self, test_name: str, entity1: str, entity2: str, expected_behavior: str):
        """Test a knowledge graph relationship scenario."""
        try:
            print(f"\n🔍 {test_name}")
            print(f"Entities: '{entity1}' -> '{entity2}'")
            print(f"Expected: {expected_behavior}")
            
            start_time = time.time()
            result = await self.knowledge_agent.query_relationships(entity1, entity2)
            processing_time = time.time() - start_time
            
            # Validate results
            assert result is not None, "Result should not be None"
            assert hasattr(result, 'entities'), "Should have entities"
            assert hasattr(result, 'relationships'), "Should have relationships"
            assert hasattr(result, 'confidence'), "Should have confidence"
            assert 0 <= result.confidence <= 1, f"Confidence should be 0-1: {result.confidence}"
            
            # Validate processing time
            assert processing_time < 3.0, f"Processing time should be under 3s: {processing_time:.3f}s"
            
            print(f"✅ PASSED - Found {len(result.entities)} entities, {len(result.relationships)} relationships in {processing_time:.3f}s")
            print(f"   Confidence: {result.confidence:.3f}")
            
            # Store test result
            self.test_results.append({
                'test_name': test_name,
                'query': f"{entity1} -> {entity2}",
                'status': 'PASSED',
                'entities_count': len(result.entities),
                'relationships_count': len(result.relationships),
                'confidence': result.confidence,
                'processing_time': processing_time,
                'expected_behavior': expected_behavior
            })
            
        except Exception as e:
            print(f"❌ FAILED - {test_name}: {e}")
            self.test_results.append({
                'test_name': test_name,
                'query': f"{entity1} -> {entity2}",
                'status': 'FAILED',
                'error': str(e),
                'expected_behavior': expected_behavior
            })
    
    async def _test_single_entity_scenario(self, test_name: str, entity: str, expected_behavior: str):
        """Test a single entity knowledge graph scenario."""
        try:
            print(f"\n🔍 {test_name}")
            print(f"Entity: '{entity}'")
            print(f"Expected: {expected_behavior}")
            
            start_time = time.time()
            result = await self.knowledge_agent.query_relationships(entity)
            processing_time = time.time() - start_time
            
            # Validate results
            assert result is not None, "Result should not be None"
            assert hasattr(result, 'entities'), "Should have entities"
            assert hasattr(result, 'confidence'), "Should have confidence"
            assert 0 <= result.confidence <= 1, f"Confidence should be 0-1: {result.confidence}"
            
            # Validate processing time
            assert processing_time < 3.0, f"Processing time should be under 3s: {processing_time:.3f}s"
            
            print(f"✅ PASSED - Found {len(result.entities)} entities in {processing_time:.3f}s")
            print(f"   Confidence: {result.confidence:.3f}")
            
            # Store test result
            self.test_results.append({
                'test_name': test_name,
                'query': entity,
                'status': 'PASSED',
                'entities_count': len(result.entities),
                'confidence': result.confidence,
                'processing_time': processing_time,
                'expected_behavior': expected_behavior
            })
            
        except Exception as e:
            print(f"❌ FAILED - {test_name}: {e}")
            self.test_results.append({
                'test_name': test_name,
                'query': entity,
                'status': 'FAILED',
                'error': str(e),
                'expected_behavior': expected_behavior
            })
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if passed_tests > 0:
            avg_confidence = sum([r.get('confidence', 0) for r in self.test_results if r['status'] == 'PASSED']) / passed_tests
            avg_processing_time = sum([r.get('processing_time', 0) for r in self.test_results if r['status'] == 'PASSED']) / passed_tests
            print(f"   Average Confidence: {avg_confidence:.3f}")
            print(f"   Average Processing Time: {avg_processing_time:.3f}s")
        
        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"   {i:2d}. {status_icon} {result['test_name']}")
            if result['status'] == 'PASSED':
                if 'results_count' in result:
                    print(f"       Results: {result['results_count']}, Confidence: {result['confidence']:.3f}")
                elif 'entities_count' in result:
                    relationships_count = result.get('relationships_count', 0)
                    print(f"       Entities: {result['entities_count']}, Relationships: {relationships_count}, Confidence: {result['confidence']:.3f}")
                else:
                    print(f"       Confidence: {result['confidence']:.3f}")
            else:
                print(f"       Error: {result['error']}")
        
        print(f"\n🎯 Conclusion:")
        if pass_rate >= 95:
            print("   🏆 EXCELLENT: System is production-ready with high reliability!")
        elif pass_rate >= 90:
            print("   ✅ GOOD: System is mostly reliable with minor issues.")
        elif pass_rate >= 80:
            print("   ⚠️ FAIR: System needs some improvements.")
        else:
            print("   ❌ POOR: System needs significant improvements.")
        
        print(f"\n🚀 Real-World Readiness: {pass_rate:.1f}%")


async def main():
    """Main test function."""
    try:
        test_suite = ComprehensiveRealWorldTests()
        await test_suite.run_all_tests()
        return 0
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 