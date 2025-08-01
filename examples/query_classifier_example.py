#!/usr/bin/env python3
"""
QueryClassifier Example - Practical Usage
Demonstrates how to use the QueryClassifier in a real application.
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.core.query_classifier import QueryClassifier, QueryCategory


class QueryProcessor:
    """Example application that uses QueryClassifier for intelligent query processing."""
    
    def __init__(self):
        """Initialize the query processor with classifier."""
        self.classifier = QueryClassifier()
        self.processing_stats = {
            "total_queries": 0,
            "category_counts": {},
            "avg_confidence": 0.0,
            "processing_times": []
        }
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query using intelligent classification.
        
        Args:
            query: The user's query
            user_context: Optional user context
            
        Returns:
            Processing result with classification and recommendations
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Classify the query
            classification = await self.classifier.classify_query(query)
            
            # Step 2: Generate processing recommendations
            recommendations = await self._generate_recommendations(classification, user_context)
            
            # Step 3: Simulate processing based on classification
            processing_result = await self._simulate_processing(classification, recommendations)
            
            # Step 4: Update statistics
            self._update_stats(classification, asyncio.get_event_loop().time() - start_time)
            
            return {
                "query": query,
                "classification": classification.to_dict(),
                "recommendations": recommendations,
                "processing_result": processing_result,
                "stats": self.processing_stats
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "classification": {
                    "category": "unknown",
                    "confidence": 0.0,
                    "complexity": "simple"
                }
            }
    
    async def _generate_recommendations(self, classification, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate processing recommendations based on classification."""
        
        recommendations = {
            "priority": classification.routing_hints.get("priority_level", "normal"),
            "execution_strategy": classification.routing_hints.get("execution_strategy", "pipeline"),
            "suggested_agents": classification.suggested_agents,
            "estimated_tokens": classification.routing_hints.get("estimated_tokens", 1000),
            "cache_strategy": classification.routing_hints.get("cache_strategy", "conservative"),
            "category_specific_hints": {}
        }
        
        # Category-specific recommendations
        if classification.category == QueryCategory.KNOWLEDGE_GRAPH:
            recommendations["category_specific_hints"] = {
                "use_graph_database": True,
                "extract_entities": True,
                "find_relationships": True,
                "suggested_sources": ["knowledge_graph", "entity_database", "relationship_maps"]
            }
        elif classification.category == QueryCategory.CODE:
            recommendations["category_specific_hints"] = {
                "use_code_analysis": True,
                "syntax_highlighting": True,
                "include_examples": True,
                "suggested_sources": ["code_repositories", "documentation", "tutorials", "stack_overflow"]
            }
        elif classification.category == QueryCategory.ANALYTICAL:
            recommendations["category_specific_hints"] = {
                "deep_analysis": True,
                "multiple_sources": True,
                "fact_checking": True,
                "suggested_sources": ["research_papers", "academic_databases", "expert_opinions"]
            }
        elif classification.category == QueryCategory.COMPARATIVE:
            recommendations["category_specific_hints"] = {
                "comparison_matrix": True,
                "pros_cons_analysis": True,
                "benchmark_data": True,
                "suggested_sources": ["benchmark_reports", "comparison_studies", "expert_reviews"]
            }
        
        return recommendations
    
    async def _simulate_processing(self, classification, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate processing based on classification and recommendations."""
        
        # Simulate different processing approaches based on category
        if classification.category == QueryCategory.KNOWLEDGE_GRAPH:
            return {
                "processing_type": "graph_traversal",
                "steps": [
                    "Extract entities from query",
                    "Find relationships between entities",
                    "Traverse knowledge graph",
                    "Synthesize relationship information"
                ],
                "estimated_time": "2-5 seconds",
                "data_sources": recommendations["category_specific_hints"].get("suggested_sources", [])
            }
        elif classification.category == QueryCategory.CODE:
            return {
                "processing_type": "code_analysis",
                "steps": [
                    "Parse code-related query",
                    "Search code repositories",
                    "Find relevant examples",
                    "Generate code explanations"
                ],
                "estimated_time": "1-3 seconds",
                "data_sources": recommendations["category_specific_hints"].get("suggested_sources", [])
            }
        elif classification.category == QueryCategory.ANALYTICAL:
            return {
                "processing_type": "deep_analysis",
                "steps": [
                    "Analyze query complexity",
                    "Gather multiple data sources",
                    "Perform fact checking",
                    "Synthesize analytical response"
                ],
                "estimated_time": "5-10 seconds",
                "data_sources": recommendations["category_specific_hints"].get("suggested_sources", [])
            }
        else:
            return {
                "processing_type": "standard_processing",
                "steps": [
                    "Standard query processing",
                    "Retrieve relevant information",
                    "Synthesize response"
                ],
                "estimated_time": "1-2 seconds",
                "data_sources": ["general_knowledge_base"]
            }
    
    def _update_stats(self, classification, processing_time: float):
        """Update processing statistics."""
        self.processing_stats["total_queries"] += 1
        
        # Update category counts
        category = classification.category.value
        self.processing_stats["category_counts"][category] = \
            self.processing_stats["category_counts"].get(category, 0) + 1
        
        # Update average confidence
        total_confidence = sum([
            classification.confidence for _ in range(self.processing_stats["total_queries"])
        ])
        self.processing_stats["avg_confidence"] = total_confidence / self.processing_stats["total_queries"]
        
        # Update processing times
        self.processing_stats["processing_times"].append(processing_time)
        if len(self.processing_stats["processing_times"]) > 100:
            self.processing_stats["processing_times"] = self.processing_stats["processing_times"][-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.processing_stats["processing_times"]:
            return {"message": "No queries processed yet"}
        
        avg_time = sum(self.processing_stats["processing_times"]) / len(self.processing_stats["processing_times"])
        max_time = max(self.processing_stats["processing_times"])
        min_time = min(self.processing_stats["processing_times"])
        
        return {
            "total_queries": self.processing_stats["total_queries"],
            "category_distribution": self.processing_stats["category_counts"],
            "average_confidence": self.processing_stats["avg_confidence"],
            "processing_times": {
                "average": avg_time,
                "maximum": max_time,
                "minimum": min_time
            }
        }


async def main():
    """Main example function."""
    
    print("🚀 QueryClassifier Example - Practical Usage\n")
    
    # Initialize the query processor
    processor = QueryProcessor()
    
    # Example queries for different scenarios
    example_queries = [
        {
            "query": "What is the relationship between machine learning and deep learning?",
            "context": {"user_type": "student", "domain": "AI"}
        },
        {
            "query": "How to implement authentication in a React application?",
            "context": {"user_type": "developer", "domain": "web_development"}
        },
        {
            "query": "Compare the performance of different sorting algorithms",
            "context": {"user_type": "researcher", "domain": "algorithms"}
        },
        {
            "query": "Analyze the impact of cloud computing on software development",
            "context": {"user_type": "architect", "domain": "cloud_computing"}
        },
        {
            "query": "What are the steps to deploy a microservice architecture?",
            "context": {"user_type": "devops", "domain": "deployment"}
        }
    ]
    
    print("📝 Processing example queries...\n")
    
    for i, query_data in enumerate(example_queries, 1):
        print(f"Query {i}: {query_data['query']}")
        print(f"Context: {query_data['context']}")
        
        # Process the query
        result = await processor.process_query(query_data['query'], query_data['context'])
        
        # Display results
        classification = result['classification']
        recommendations = result['recommendations']
        processing = result['processing_result']
        
        print(f"  📊 Classification:")
        print(f"    Category: {classification['category']}")
        print(f"    Confidence: {classification['confidence']:.2f}")
        print(f"    Complexity: {classification['complexity']}")
        
        print(f"  🎯 Recommendations:")
        print(f"    Priority: {recommendations['priority']}")
        print(f"    Strategy: {recommendations['execution_strategy']}")
        print(f"    Agents: {', '.join(recommendations['suggested_agents'])}")
        
        print(f"  ⚙️ Processing:")
        print(f"    Type: {processing['processing_type']}")
        print(f"    Estimated Time: {processing['estimated_time']}")
        print(f"    Data Sources: {', '.join(processing['data_sources'])}")
        
        print()
    
    # Show performance summary
    print("📈 Performance Summary:")
    summary = processor.get_performance_summary()
    print(f"  Total Queries: {summary['total_queries']}")
    print(f"  Average Confidence: {summary['average_confidence']:.2f}")
    print(f"  Category Distribution:")
    for category, count in summary['category_distribution'].items():
        print(f"    {category}: {count}")
    print(f"  Average Processing Time: {summary['processing_times']['average']:.3f}s")
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main()) 