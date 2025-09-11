# Test Matrix & Combinatorial Testing

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Engineering Team  

## Overview

This document defines the comprehensive test matrix for SarvanOM v2, covering all combinations of LLM providers, databases, knowledge graphs, and query complexities. The matrix ensures thorough testing of all system components and their interactions.

## Test Dimensions

### 1. LLM Provider Matrix

#### 1.1 Primary Providers
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3.5-sonnet, Claude-3-haiku, Claude-3-opus
- **HuggingFace**: Llama-2-70b, Mistral-7b, CodeLlama-34b
- **Ollama**: Local models (Llama-2, Mistral, CodeLlama)

#### 1.2 Provider Combinations
- **Single Provider**: Each provider tested individually
- **Fallback Chain**: Primary → Secondary → Tertiary
- **Load Balancing**: Round-robin across providers
- **Failover**: Automatic switching on provider failure

### 2. Database Matrix

#### 2.1 Vector Databases
- **Qdrant**: Primary vector store (dev & prod)
- **ChromaDB**: Backup/fallback vector store
- **Collection Types**: Dense vectors, sparse vectors, hybrid

#### 2.2 Knowledge Graph
- **ArangoDB**: Primary knowledge graph
- **Graph Types**: Entity relationships, concept hierarchies, temporal graphs
- **Query Types**: Traversal, pattern matching, aggregation

#### 2.3 Full-Text Search
- **Meilisearch**: Primary full-text search
- **Index Types**: Document search, semantic search, faceted search
- **Query Types**: Boolean, phrase, wildcard, fuzzy

### 3. Query Complexity Matrix

#### 3.1 Simple Queries (5s SLA)
- **Basic Facts**: "What is the capital of France?"
- **Definitions**: "Define machine learning"
- **Simple Calculations**: "What is 15% of 200?"
- **Date/Time**: "What day is it today?"

#### 3.2 Technical Queries (7s SLA)
- **Code Generation**: "Write a Python function to sort a list"
- **Technical Explanations**: "How does a neural network work?"
- **API Documentation**: "How do I use the OpenAI API?"
- **Debugging**: "Why is this code not working?"

#### 3.3 Research Queries (10s SLA)
- **Multi-step Reasoning**: "Compare the pros and cons of different AI approaches"
- **Literature Review**: "What are the latest developments in NLP?"
- **Complex Analysis**: "Analyze the impact of AI on healthcare"
- **Multimodal**: "Describe this image and explain its relevance"

### 4. Guided Prompt Confirmation Matrix

#### 4.1 Refinement Modes
- **ON**: Default mode with refinement enabled
- **OFF**: Refinement disabled for power users
- **ALWAYS_BYPASS**: Always skip refinement for expert users
- **ADAPTIVE**: System learns user preferences and auto-adjusts

#### 4.2 Refinement Types
- **Intent Analysis**: Clarify ambiguous queries
- **Disambiguation**: Resolve multiple possible interpretations
- **Constraint Application**: Apply time, source, cost constraints
- **Sanitization**: Remove PII and harmful content
- **Decomposition**: Break complex queries into steps

#### 4.3 Refinement Scenarios
- **Ambiguous Queries**: "Show me apple" (company vs fruit)
- **PII-Heavy Queries**: Queries containing personal information
- **Multi-lingual Queries**: Queries in different languages
- **Image-Attached Queries**: Queries with image attachments
- **Very Short Queries**: Single word or phrase queries
- **Very Long Queries**: Complex, multi-part queries

#### 4.4 Constraint Chip Testing
- **Time Range**: Today, last week, last month, last year
- **Sources**: All, specific providers, academic sources
- **Citations**: Required, optional, none
- **Cost Ceiling**: Free only, low cost, unlimited
- **Depth**: Simple, technical, research level

### 5. Service Integration Matrix

#### 5.1 Core Services
- **Gateway**: Request routing and orchestration
- **Retrieval**: Document and knowledge retrieval
- **Synthesis**: Response generation and formatting
- **Fact-check**: Information validation and verification

#### 5.2 External Services
- **News APIs**: Real-time news feeds
- **Market APIs**: Financial data and market information
- **Search APIs**: Web search and information gathering
- **Translation APIs**: Multi-language support

## Test Scenarios

### 1. Happy Path Scenarios

#### 1.1 Simple Query Flow
```
User Query → Gateway → Retrieval → Synthesis → Response
- Provider: OpenAI GPT-4
- Database: Qdrant + ArangoDB + Meilisearch
- Complexity: Simple
- Expected SLA: < 5s
```

#### 1.2 Technical Query Flow
```
User Query → Gateway → Retrieval → Synthesis → Fact-check → Response
- Provider: Anthropic Claude-3.5-sonnet
- Database: Qdrant + ArangoDB + Meilisearch
- Complexity: Technical
- Expected SLA: < 7s
```

#### 1.3 Research Query Flow
```
User Query → Gateway → Retrieval → External APIs → Synthesis → Fact-check → Response
- Provider: HuggingFace Llama-2-70b
- Database: Qdrant + ArangoDB + Meilisearch
- Complexity: Research
- Expected SLA: < 10s
```

### 2. Failure Scenarios

#### 2.1 Provider Failure
```
User Query → Gateway → Provider A (FAIL) → Provider B (SUCCESS) → Response
- Test: Primary provider timeout/failure
- Expected: Automatic fallback to secondary provider
- SLA: Maintained despite failure
```

#### 2.2 Database Failure
```
User Query → Gateway → Retrieval → Database A (FAIL) → Database B (SUCCESS) → Response
- Test: Primary database unavailable
- Expected: Fallback to secondary database
- SLA: Maintained with degraded performance
```

#### 2.3 Service Failure
```
User Query → Gateway → Service A (FAIL) → Circuit Breaker → Cached Response
- Test: Core service unavailable
- Expected: Graceful degradation with cached results
- SLA: Maintained with limited functionality
```

### 3. Edge Cases

#### 3.1 High Load Scenarios
- **Concurrent Users**: 100+ simultaneous queries
- **Large Queries**: Multi-paragraph complex questions
- **Rate Limiting**: API rate limit handling
- **Resource Exhaustion**: Memory/CPU limits

#### 3.2 Data Quality Scenarios
- **Missing Data**: Incomplete knowledge base
- **Conflicting Data**: Contradictory information
- **Outdated Data**: Stale information
- **Malformed Data**: Invalid data formats

## Test Execution Matrix

### 1. Unit Tests

#### 1.1 Service Tests
- **Gateway**: Request routing, authentication, rate limiting
- **Retrieval**: Document search, vector similarity, ranking
- **Synthesis**: Response generation, formatting, validation
- **Fact-check**: Information verification, source validation

#### 1.2 Integration Tests
- **Database Integration**: CRUD operations, query performance
- **API Integration**: External service communication
- **Service Communication**: Inter-service messaging
- **Authentication**: Token validation, user permissions

### 2. Performance Tests

#### 2.1 Load Testing
- **Concurrent Users**: 10, 50, 100, 500, 1000 users
- **Query Types**: Simple, technical, research queries
- **Response Times**: P50, P95, P99 percentiles
- **Throughput**: Queries per second

#### 2.2 Stress Testing
- **Resource Limits**: Memory, CPU, disk usage
- **Failure Points**: Service crashes, network issues
- **Recovery Time**: Time to restore service
- **Data Integrity**: Data consistency under stress

### 3. End-to-End Tests

#### 3.1 User Journey Tests
- **Registration**: User signup and verification
- **Query Processing**: End-to-end query flow
- **Result Display**: Response formatting and presentation
- **Error Handling**: User-friendly error messages

#### 3.2 Cross-Platform Tests
- **Web Interface**: Browser compatibility
- **Mobile Interface**: Responsive design
- **API Interface**: REST API functionality
- **CLI Interface**: Command-line tool functionality

## Test Data Management

### 1. Test Datasets

#### 1.1 Query Datasets
- **Simple Queries**: 1000+ basic fact questions
- **Technical Queries**: 500+ code and technical questions
- **Research Queries**: 200+ complex analytical questions
- **Multimodal Queries**: 100+ image and text combinations

#### 1.2 Knowledge Base
- **Document Corpus**: 10,000+ documents across domains
- **Knowledge Graph**: 100,000+ entities and relationships
- **Vector Embeddings**: Pre-computed embeddings for all documents
- **Search Indexes**: Optimized search indexes

### 2. Test Environment Setup

#### 2.1 Environment Configuration
- **Development**: Local development environment
- **Staging**: Production-like staging environment
- **Testing**: Isolated testing environment
- **Performance**: Dedicated performance testing environment

#### 2.2 Data Isolation
- **Test Data**: Separate test databases
- **User Isolation**: Test user accounts
- **API Keys**: Test API keys and quotas
- **External Services**: Mock external services

## Test Automation

### 1. Automated Test Execution

#### 1.1 Continuous Integration
- **PR Tests**: Run on every pull request
- **Nightly Tests**: Full test suite execution
- **Release Tests**: Comprehensive testing before release
- **Regression Tests**: Automated regression detection

#### 1.2 Test Orchestration
- **Test Scheduling**: Automated test scheduling
- **Parallel Execution**: Concurrent test execution
- **Result Aggregation**: Test result collection and analysis
- **Failure Notification**: Automated failure alerts

### 2. Test Reporting

#### 2.1 Test Metrics
- **Pass Rate**: Percentage of tests passing
- **Coverage**: Code and functionality coverage
- **Performance**: Response time and throughput metrics
- **Reliability**: System availability and error rates

#### 2.2 Test Dashboards
- **Real-time Status**: Current test execution status
- **Historical Trends**: Test performance over time
- **Failure Analysis**: Root cause analysis of failures
- **Quality Metrics**: Overall system quality indicators

## Test Maintenance

### 1. Test Updates

#### 1.1 Regular Updates
- **Weekly**: Update test data and scenarios
- **Monthly**: Review and update test coverage
- **Quarterly**: Comprehensive test strategy review
- **Annually**: Test framework and tool evaluation

#### 1.2 Test Optimization
- **Performance**: Optimize test execution time
- **Coverage**: Improve test coverage gaps
- **Reliability**: Reduce test flakiness
- **Maintainability**: Simplify test maintenance

### 2. Test Documentation

#### 2.1 Test Documentation
- **Test Cases**: Detailed test case descriptions
- **Test Data**: Test data specifications and sources
- **Test Environment**: Environment setup and configuration
- **Test Results**: Test execution results and analysis

#### 2.2 Knowledge Sharing
- **Test Training**: Team training on test procedures
- **Best Practices**: Test development best practices
- **Lessons Learned**: Test execution lessons and improvements
- **Tool Usage**: Test tool usage and optimization

---

## Appendix

### A. Test Tools
- **Pytest**: Python testing framework
- **Jest**: JavaScript testing framework
- **K6**: Load testing tool
- **Selenium**: Web UI testing
- **Postman**: API testing
- **Docker**: Test environment containerization

### B. Test Environments
- **Local**: Developer local environment
- **CI/CD**: GitHub Actions environment
- **Staging**: Pre-production environment
- **Performance**: Dedicated performance testing environment

### C. Test Metrics
- **Coverage**: Code coverage percentage
- **Performance**: Response time percentiles
- **Reliability**: System availability percentage
- **Quality**: Defect density and resolution time
