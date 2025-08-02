from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Add sample documents to Meilisearch for testing.
This script adds realistic documents to enable proper testing of the hybrid retrieval system.
"""

import asyncio
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available")

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.meilisearch_engine import MeilisearchEngine, MeilisearchDocument


async def add_sample_documents():
    """Add sample documents to Meilisearch for testing."""
    print("📚 Adding Sample Documents to Meilisearch...")
    
    # Create Meilisearch engine
    meilisearch_url = settings.meilisearch_url or "http://localhost:7700"
    meilisearch_api_key = settings.meilisearch_api_key
    
    engine = MeilisearchEngine(meilisearch_url, meilisearch_api_key)
    
    # Sample documents covering various real-world scenarios
    sample_documents = [
        # Academic Research Documents
        MeilisearchDocument(
            id="doc_ml_nlp_001",
            title="Machine Learning Algorithms for Natural Language Processing",
            content="This comprehensive guide covers machine learning algorithms specifically designed for natural language processing tasks. We explore transformer architectures, attention mechanisms, and state-of-the-art models like BERT and GPT. The document includes practical implementations, performance comparisons, and real-world applications in text classification, sentiment analysis, and language generation.",
            tags=["machine learning", "natural language processing", "algorithms", "academic"],
            created_at="2024-01-15T10:00:00Z"
        ),
        
        # Business Intelligence Documents
        MeilisearchDocument(
            id="doc_bi_dashboard_001",
            title="Data Analytics Dashboard Implementation Guide",
            content="Learn how to build comprehensive data analytics dashboards for business intelligence. This guide covers data visualization best practices, real-time data processing, interactive charts and graphs, and dashboard design principles. Includes implementation examples using popular BI tools and frameworks for creating actionable business insights.",
            tags=["data analytics", "dashboard", "business intelligence", "visualization"],
            created_at="2024-01-16T14:30:00Z"
        ),
        
        # Technical Documentation
        MeilisearchDocument(
            id="doc_api_auth_001",
            title="API Authentication Best Practices",
            content="Comprehensive guide to implementing secure API authentication. Covers OAuth 2.0, JWT tokens, API keys, and multi-factor authentication. Includes security best practices, token management, rate limiting, and implementation examples in multiple programming languages. Essential reading for developers building secure APIs.",
            tags=["API", "authentication", "security", "best practices"],
            created_at="2024-01-17T09:15:00Z"
        ),
        
        # Programming Language Documents
        MeilisearchDocument(
            id="doc_python_async_001",
            title="Python Async Programming Patterns",
            content="Master asynchronous programming in Python with this comprehensive guide. Learn about asyncio, async/await syntax, coroutines, and concurrent programming patterns. Includes practical examples for web scraping, API calls, database operations, and building high-performance applications. Covers error handling, testing, and debugging async code.",
            tags=["Python", "async", "programming", "asyncio", "patterns"],
            created_at="2024-01-18T11:45:00Z"
        ),
        
        # Framework Documents
        MeilisearchDocument(
            id="doc_react_hooks_001",
            title="React Hooks State Management",
            content="Complete guide to state management using React Hooks. Learn useState, useEffect, useContext, and custom hooks. Includes advanced patterns for complex state management, performance optimization, and best practices. Covers real-world examples, common pitfalls, and integration with external state management libraries.",
            tags=["React", "hooks", "state management", "frontend"],
            created_at="2024-01-19T16:20:00Z"
        ),
        
        # DevOps Documents
        MeilisearchDocument(
            id="doc_k8s_orchestration_001",
            title="Container Orchestration with Kubernetes",
            content="Comprehensive guide to container orchestration using Kubernetes. Learn about pods, services, deployments, and cluster management. Includes practical examples for scaling applications, managing resources, monitoring, and troubleshooting. Covers best practices for production deployments and security considerations.",
            tags=["Kubernetes", "container orchestration", "DevOps", "deployment"],
            created_at="2024-01-20T13:10:00Z"
        ),
        
        # AI/ML Documents
        MeilisearchDocument(
            id="doc_deep_learning_001",
            title="Deep Learning Neural Network Architectures",
            content="Explore advanced deep learning neural network architectures including CNNs, RNNs, LSTM, and transformer models. Learn about architecture design principles, training strategies, and optimization techniques. Includes practical implementations, performance analysis, and real-world applications in computer vision and natural language processing.",
            tags=["deep learning", "neural networks", "AI", "machine learning"],
            created_at="2024-01-21T08:30:00Z"
        ),
        
        # Database Documents
        MeilisearchDocument(
            id="doc_nosql_sql_001",
            title="NoSQL vs SQL Performance Comparison",
            content="Comprehensive comparison of NoSQL and SQL database performance characteristics. Analyze trade-offs between consistency, availability, and partition tolerance. Includes performance benchmarks, use case analysis, and migration strategies. Covers MongoDB, PostgreSQL, Redis, and Cassandra with real-world performance data.",
            tags=["NoSQL", "SQL", "database", "performance", "comparison"],
            created_at="2024-01-22T15:45:00Z"
        ),
        
        # Security Documents
        MeilisearchDocument(
            id="doc_cybersecurity_001",
            title="Cybersecurity Threat Detection Methods",
            content="Advanced guide to cybersecurity threat detection and prevention. Learn about intrusion detection systems, anomaly detection, and security monitoring. Includes machine learning approaches for threat detection, incident response procedures, and security automation. Covers both network and application security with practical examples.",
            tags=["cybersecurity", "threat detection", "security", "monitoring"],
            created_at="2024-01-23T12:00:00Z"
        ),
        
        # Cloud Computing Documents
        MeilisearchDocument(
            id="doc_microservices_001",
            title="Microservices Architecture Patterns",
            content="Complete guide to microservices architecture patterns and best practices. Learn about service decomposition, API design, data management, and deployment strategies. Includes practical examples using Docker, Kubernetes, and cloud platforms. Covers monitoring, testing, and maintaining microservices-based applications.",
            tags=["microservices", "architecture", "patterns", "cloud computing"],
            created_at="2024-01-24T10:30:00Z"
        ),
        
        # Multi-Technology Documents
        MeilisearchDocument(
            id="doc_python_ml_tensorflow_001",
            title="Python Machine Learning with TensorFlow and scikit-learn",
            content="Comprehensive guide to machine learning using Python with TensorFlow and scikit-learn. Learn data preprocessing, model training, evaluation, and deployment. Includes practical examples for classification, regression, clustering, and deep learning. Covers best practices for production ML systems and model optimization.",
            tags=["Python", "machine learning", "TensorFlow", "scikit-learn"],
            created_at="2024-01-25T14:15:00Z"
        ),
        
        # Full-Stack Development Documents
        MeilisearchDocument(
            id="doc_fullstack_react_node_001",
            title="React Frontend with Node.js Backend and MongoDB Database",
            content="Complete full-stack development guide using React, Node.js, and MongoDB. Learn modern web development patterns, API design, database modeling, and deployment strategies. Includes authentication, real-time features, and performance optimization. Covers testing, debugging, and production deployment best practices.",
            tags=["React", "Node.js", "MongoDB", "full-stack", "web development"],
            created_at="2024-01-26T09:45:00Z"
        ),
        
        # AI/ML Pipeline Documents
        MeilisearchDocument(
            id="doc_ml_pipeline_001",
            title="Data Preprocessing with pandas, Model Training with scikit-learn, and Deployment with Flask",
            content="End-to-end machine learning pipeline guide using pandas, scikit-learn, and Flask. Learn data cleaning, feature engineering, model selection, and API deployment. Includes practical examples for building production-ready ML systems. Covers model versioning, monitoring, and continuous integration for ML applications.",
            tags=["pandas", "scikit-learn", "Flask", "machine learning", "pipeline"],
            created_at="2024-01-27T11:20:00Z"
        ),
        
        # DevOps Pipeline Documents
        MeilisearchDocument(
            id="doc_devops_cicd_001",
            title="CI/CD with Jenkins, Docker containers, and Kubernetes deployment",
            content="Complete DevOps pipeline implementation using Jenkins, Docker, and Kubernetes. Learn continuous integration, containerization, and orchestration strategies. Includes practical examples for automated testing, building, and deployment. Covers monitoring, logging, and infrastructure as code best practices.",
            tags=["CI/CD", "Jenkins", "Docker", "Kubernetes", "DevOps"],
            created_at="2024-01-28T16:30:00Z"
        ),
        
        # Security Implementation Documents
        MeilisearchDocument(
            id="doc_security_jwt_oauth_001",
            title="JWT Authentication with OAuth2 and HTTPS encryption",
            content="Comprehensive security implementation guide using JWT, OAuth2, and HTTPS. Learn secure authentication patterns, token management, and encryption best practices. Includes practical examples for implementing secure APIs and web applications. Covers security testing, vulnerability assessment, and compliance considerations.",
            tags=["JWT", "OAuth2", "HTTPS", "authentication", "security"],
            created_at="2024-01-29T13:45:00Z"
        ),
        
        # Performance Optimization Documents
        MeilisearchDocument(
            id="doc_performance_optimization_001",
            title="Database indexing, caching with Redis, and load balancing",
            content="Advanced performance optimization guide covering database indexing, Redis caching, and load balancing strategies. Learn query optimization, cache management, and distributed system design. Includes practical examples for improving application performance and scalability. Covers monitoring, profiling, and optimization techniques.",
            tags=["database", "indexing", "Redis", "caching", "load balancing"],
            created_at="2024-01-30T10:15:00Z"
        ),
        
        # Cloud Architecture Documents
        MeilisearchDocument(
            id="doc_aws_lambda_001",
            title="AWS Lambda functions with API Gateway and DynamoDB",
            content="Serverless architecture implementation using AWS Lambda, API Gateway, and DynamoDB. Learn event-driven programming, serverless patterns, and cloud-native development. Includes practical examples for building scalable, cost-effective applications. Covers monitoring, debugging, and optimization for serverless applications.",
            tags=["AWS", "Lambda", "API Gateway", "DynamoDB", "serverless"],
            created_at="2024-01-31T14:30:00Z"
        )
    ]
    
    try:
        # Check if Meilisearch is running
        if not await engine.health_check():
            print("❌ Meilisearch is not running. Please start Meilisearch first.")
            return False
        
        # Create index
        if not await engine.create_index():
            print("❌ Failed to create Meilisearch index.")
            return False
        
        # Add documents
        success = await engine.add_documents(sample_documents)
        if success:
            print(f"✅ Successfully added {len(sample_documents)} sample documents to Meilisearch")
            
            # Get stats to verify
            stats = await engine.get_stats()
            print(f"📊 Index stats: {stats}")
            
            return True
        else:
            print("❌ Failed to add documents to Meilisearch")
            return False
            
    except Exception as e:
        print(f"❌ Error adding sample documents: {e}")
        return False
    finally:
        await engine.close()


async def main():
    """Main function."""
    try:
        success = await add_sample_documents()
        if success:
            print("\n🎉 Sample documents added successfully!")
            print("📝 You can now run the comprehensive tests with real data.")
        else:
            print("\n❌ Failed to add sample documents.")
            return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 