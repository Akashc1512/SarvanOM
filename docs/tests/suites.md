# Synthetic Prompt Suites & Test Cases

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Engineering Team  

## Overview

This document defines comprehensive synthetic prompt suites for testing SarvanOM v2 across all complexity levels, LLM providers, and use cases. These suites ensure consistent testing and validation of system capabilities.

## Prompt Suite Categories

### Guided Prompt Confirmation Test Scenarios

#### Ambiguous Query Scenarios
```json
{
  "category": "guided_prompt_ambiguous",
  "description": "Test cases for ambiguous queries that require refinement",
  "prompts": [
    {
      "id": "gp_ambiguous_001",
      "prompt": "Show me apple",
      "expected_refinement": "Do you mean Apple Inc. (company) stock performance, or the fruit Apple nutritional info?",
      "refinement_type": "disambiguation",
      "expected_acceptance_rate": 0.7
    },
    {
      "id": "gp_ambiguous_002", 
      "prompt": "Tell me about python",
      "expected_refinement": "Do you mean Python programming language, or the Python snake species?",
      "refinement_type": "disambiguation",
      "expected_acceptance_rate": 0.8
    }
  ]
}
```

#### PII-Heavy Query Scenarios
```json
{
  "category": "guided_prompt_pii",
  "description": "Test cases for queries containing personal information",
  "prompts": [
    {
      "id": "gp_pii_001",
      "prompt": "My email is john.doe@example.com and I need help with my account",
      "expected_refinement": "I can help with account issues. For privacy, I'll remove your email address from this query.",
      "refinement_type": "sanitization",
      "expected_acceptance_rate": 0.9
    },
    {
      "id": "gp_pii_002",
      "prompt": "Call me at 555-123-4567 about the meeting",
      "expected_refinement": "I can help with meeting information. For privacy, I'll remove your phone number from this query.",
      "refinement_type": "sanitization", 
      "expected_acceptance_rate": 0.9
    }
  ]
}
```

#### Multi-lingual Query Scenarios
```json
{
  "category": "guided_prompt_multilingual",
  "description": "Test cases for queries in different languages",
  "prompts": [
    {
      "id": "gp_multilingual_001",
      "prompt": "¿Cuál es la capital de España?",
      "expected_refinement": "I'll search for information about Spain's capital city.",
      "refinement_type": "intent_analysis",
      "expected_acceptance_rate": 0.8
    },
    {
      "id": "gp_multilingual_002",
      "prompt": "東京の人口は何人ですか？",
      "expected_refinement": "I'll search for Tokyo's population information.",
      "refinement_type": "intent_analysis",
      "expected_acceptance_rate": 0.8
    }
  ]
}
```

#### Constraint Application Scenarios
```json
{
  "category": "guided_prompt_constraints",
  "description": "Test cases for applying user constraints",
  "prompts": [
    {
      "id": "gp_constraints_001",
      "prompt": "Show me recent news about AI",
      "expected_refinement": "I'll search for recent AI news. Would you like to specify a time range (last week, month) or particular sources?",
      "refinement_type": "constraint_application",
      "expected_acceptance_rate": 0.6
    },
    {
      "id": "gp_constraints_002",
      "prompt": "Find me stock prices",
      "expected_refinement": "I'll search for stock price information. Which companies or market indices are you interested in?",
      "refinement_type": "constraint_application",
      "expected_acceptance_rate": 0.7
    }
  ]
}
```

### 1. Simple Query Suite (5s SLA)

#### 1.1 Basic Facts
```json
{
  "category": "basic_facts",
  "sla": "5s",
  "prompts": [
    {
      "id": "fact_001",
      "prompt": "What is the capital of France?",
      "expected_elements": ["Paris", "France", "capital"],
      "complexity": "simple"
    },
    {
      "id": "fact_002", 
      "prompt": "Who wrote 'To Kill a Mockingbird'?",
      "expected_elements": ["Harper Lee", "To Kill a Mockingbird", "author"],
      "complexity": "simple"
    },
    {
      "id": "fact_003",
      "prompt": "What is the largest planet in our solar system?",
      "expected_elements": ["Jupiter", "largest", "solar system", "planet"],
      "complexity": "simple"
    }
  ]
}
```

#### 1.2 Definitions
```json
{
  "category": "definitions",
  "sla": "5s",
  "prompts": [
    {
      "id": "def_001",
      "prompt": "Define machine learning",
      "expected_elements": ["artificial intelligence", "algorithms", "data", "learning"],
      "complexity": "simple"
    },
    {
      "id": "def_002",
      "prompt": "What is photosynthesis?",
      "expected_elements": ["plants", "sunlight", "carbon dioxide", "oxygen", "glucose"],
      "complexity": "simple"
    },
    {
      "id": "def_003",
      "prompt": "Explain what a blockchain is",
      "expected_elements": ["distributed ledger", "blocks", "cryptography", "decentralized"],
      "complexity": "simple"
    }
  ]
}
```

#### 1.3 Simple Calculations
```json
{
  "category": "calculations",
  "sla": "5s",
  "prompts": [
    {
      "id": "calc_001",
      "prompt": "What is 15% of 200?",
      "expected_elements": ["30", "percentage", "calculation"],
      "complexity": "simple"
    },
    {
      "id": "calc_002",
      "prompt": "Convert 25 degrees Celsius to Fahrenheit",
      "expected_elements": ["77", "Fahrenheit", "temperature", "conversion"],
      "complexity": "simple"
    },
    {
      "id": "calc_003",
      "prompt": "What is the area of a circle with radius 5?",
      "expected_elements": ["78.54", "area", "circle", "radius", "π"],
      "complexity": "simple"
    }
  ]
}
```

### 2. Technical Query Suite (7s SLA)

#### 2.1 Code Generation
```json
{
  "category": "code_generation",
  "sla": "7s",
  "prompts": [
    {
      "id": "code_001",
      "prompt": "Write a Python function to sort a list of integers in ascending order",
      "expected_elements": ["def", "sort", "list", "ascending", "Python"],
      "complexity": "technical"
    },
    {
      "id": "code_002",
      "prompt": "Create a JavaScript function that validates an email address using regex",
      "expected_elements": ["function", "email", "regex", "validation", "JavaScript"],
      "complexity": "technical"
    },
    {
      "id": "code_003",
      "prompt": "Write a SQL query to find all users who registered in the last 30 days",
      "expected_elements": ["SELECT", "FROM", "WHERE", "DATE", "users"],
      "complexity": "technical"
    }
  ]
}
```

#### 2.2 Technical Explanations
```json
{
  "category": "technical_explanations",
  "sla": "7s",
  "prompts": [
    {
      "id": "tech_001",
      "prompt": "How does a neural network work?",
      "expected_elements": ["neurons", "layers", "weights", "activation", "training"],
      "complexity": "technical"
    },
    {
      "id": "tech_002",
      "prompt": "Explain the difference between HTTP and HTTPS",
      "expected_elements": ["protocol", "security", "encryption", "SSL", "TLS"],
      "complexity": "technical"
    },
    {
      "id": "tech_003",
      "prompt": "What is the difference between SQL and NoSQL databases?",
      "expected_elements": ["relational", "non-relational", "schema", "scalability", "ACID"],
      "complexity": "technical"
    }
  ]
}
```

#### 2.3 API Documentation
```json
{
  "category": "api_documentation",
  "sla": "7s",
  "prompts": [
    {
      "id": "api_001",
      "prompt": "How do I use the OpenAI API to generate text?",
      "expected_elements": ["API key", "endpoint", "request", "response", "authentication"],
      "complexity": "technical"
    },
    {
      "id": "api_002",
      "prompt": "Show me how to make a POST request to a REST API using Python",
      "expected_elements": ["requests", "POST", "headers", "data", "response"],
      "complexity": "technical"
    },
    {
      "id": "api_003",
      "prompt": "What are the rate limits for the GitHub API?",
      "expected_elements": ["rate limit", "requests per hour", "authentication", "headers"],
      "complexity": "technical"
    }
  ]
}
```

### 3. Research Query Suite (10s SLA)

#### 3.1 Multi-step Reasoning
```json
{
  "category": "multi_step_reasoning",
  "sla": "10s",
  "prompts": [
    {
      "id": "reason_001",
      "prompt": "Compare the pros and cons of different AI approaches for natural language processing",
      "expected_elements": ["rule-based", "statistical", "neural networks", "transformer", "comparison"],
      "complexity": "research"
    },
    {
      "id": "reason_002",
      "prompt": "Analyze the impact of climate change on global food security",
      "expected_elements": ["temperature", "precipitation", "crop yields", "food production", "adaptation"],
      "complexity": "research"
    },
    {
      "id": "reason_003",
      "prompt": "Evaluate the effectiveness of different renewable energy sources",
      "expected_elements": ["solar", "wind", "hydro", "geothermal", "efficiency", "cost"],
      "complexity": "research"
    }
  ]
}
```

#### 3.2 Literature Review
```json
{
  "category": "literature_review",
  "sla": "10s",
  "prompts": [
    {
      "id": "lit_001",
      "prompt": "What are the latest developments in natural language processing?",
      "expected_elements": ["transformer", "GPT", "BERT", "recent", "advances"],
      "complexity": "research"
    },
    {
      "id": "lit_002",
      "prompt": "Review recent research on quantum computing applications",
      "expected_elements": ["quantum", "algorithms", "applications", "recent", "research"],
      "complexity": "research"
    },
    {
      "id": "lit_003",
      "prompt": "What are the current trends in cybersecurity?",
      "expected_elements": ["threats", "defense", "AI", "zero-trust", "trends"],
      "complexity": "research"
    }
  ]
}
```

#### 3.3 Complex Analysis
```json
{
  "category": "complex_analysis",
  "sla": "10s",
  "prompts": [
    {
      "id": "analysis_001",
      "prompt": "Analyze the impact of AI on healthcare delivery",
      "expected_elements": ["diagnosis", "treatment", "efficiency", "ethics", "challenges"],
      "complexity": "research"
    },
    {
      "id": "analysis_002",
      "prompt": "Examine the relationship between social media and mental health",
      "expected_elements": ["correlation", "causation", "studies", "impact", "recommendations"],
      "complexity": "research"
    },
    {
      "id": "analysis_003",
      "prompt": "Assess the economic implications of remote work",
      "expected_elements": ["productivity", "costs", "benefits", "challenges", "future"],
      "complexity": "research"
    }
  ]
}
```

### 4. Multimodal Query Suite (10s SLA)

#### 4.1 Image Analysis
```json
{
  "category": "image_analysis",
  "sla": "10s",
  "prompts": [
    {
      "id": "img_001",
      "prompt": "Describe this image and explain its relevance to machine learning",
      "expected_elements": ["image description", "ML relevance", "visual elements", "context"],
      "complexity": "research",
      "multimodal": true
    },
    {
      "id": "img_002",
      "prompt": "What can you tell me about this chart and what insights does it provide?",
      "expected_elements": ["chart analysis", "data interpretation", "insights", "trends"],
      "complexity": "research",
      "multimodal": true
    },
    {
      "id": "img_003",
      "prompt": "Identify the objects in this image and explain their relationship",
      "expected_elements": ["object identification", "relationships", "spatial context", "analysis"],
      "complexity": "research",
      "multimodal": true
    }
  ]
}
```

#### 4.2 Document Analysis
```json
{
  "category": "document_analysis",
  "sla": "10s",
  "prompts": [
    {
      "id": "doc_001",
      "prompt": "Summarize this document and extract the key insights",
      "expected_elements": ["summary", "key insights", "main points", "conclusions"],
      "complexity": "research",
      "multimodal": true
    },
    {
      "id": "doc_002",
      "prompt": "Analyze this technical diagram and explain the process flow",
      "expected_elements": ["process flow", "technical analysis", "diagram interpretation", "steps"],
      "complexity": "research",
      "multimodal": true
    },
    {
      "id": "doc_003",
      "prompt": "Review this code snippet and suggest improvements",
      "expected_elements": ["code review", "improvements", "best practices", "optimization"],
      "complexity": "research",
      "multimodal": true
    }
  ]
}
```

## Test Execution Framework

### 1. Test Runner Configuration

#### 1.1 Test Suite Structure
```python
class TestSuite:
    def __init__(self, name: str, sla: int, complexity: str):
        self.name = name
        self.sla = sla
        self.complexity = complexity
        self.prompts = []
        self.results = []
    
    def add_prompt(self, prompt: dict):
        self.prompts.append(prompt)
    
    def execute(self, provider: str, database: str):
        for prompt in self.prompts:
            result = self.run_prompt(prompt, provider, database)
            self.results.append(result)
    
    def run_prompt(self, prompt: dict, provider: str, database: str):
        start_time = time.time()
        response = self.query_system(prompt, provider, database)
        end_time = time.time()
        
        return {
            "prompt_id": prompt["id"],
            "provider": provider,
            "database": database,
            "response_time": end_time - start_time,
            "sla_met": (end_time - start_time) <= self.sla,
            "response": response,
            "expected_elements": prompt["expected_elements"]
        }
```

#### 1.2 Test Execution Script
```python
def run_test_matrix():
    providers = ["openai", "anthropic", "huggingface", "ollama"]
    databases = ["qdrant", "chromadb", "arango", "meilisearch"]
    complexities = ["simple", "technical", "research"]
    
    for complexity in complexities:
        suite = load_test_suite(complexity)
        for provider in providers:
            for database in databases:
                suite.execute(provider, database)
                save_results(suite.results)
```

### 2. Result Validation

#### 2.1 Response Quality Metrics
```python
def validate_response(result: dict) -> dict:
    validation = {
        "sla_met": result["sla_met"],
        "response_length": len(result["response"]),
        "expected_elements_found": 0,
        "quality_score": 0.0
    }
    
    # Check for expected elements
    for element in result["expected_elements"]:
        if element.lower() in result["response"].lower():
            validation["expected_elements_found"] += 1
    
    # Calculate quality score
    validation["quality_score"] = (
        validation["expected_elements_found"] / 
        len(result["expected_elements"])
    )
    
    return validation
```

#### 2.2 Performance Metrics
```python
def calculate_performance_metrics(results: list) -> dict:
    response_times = [r["response_time"] for r in results]
    sla_violations = [r for r in results if not r["sla_met"]]
    
    return {
        "total_queries": len(results),
        "sla_violations": len(sla_violations),
        "sla_compliance_rate": (len(results) - len(sla_violations)) / len(results),
        "avg_response_time": sum(response_times) / len(response_times),
        "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))],
        "p99_response_time": sorted(response_times)[int(0.99 * len(response_times))]
    }
```

## Test Data Management

### 1. Test Data Sources

#### 1.1 Synthetic Data Generation
```python
def generate_synthetic_prompts(category: str, count: int) -> list:
    templates = load_prompt_templates(category)
    prompts = []
    
    for i in range(count):
        template = random.choice(templates)
        prompt = fill_template(template, generate_variations())
        prompts.append(prompt)
    
    return prompts
```

#### 1.2 Real-world Data Collection
```python
def collect_real_world_prompts() -> list:
    sources = [
        "user_queries.log",
        "support_tickets.json",
        "feedback_surveys.csv",
        "analytics_data.json"
    ]
    
    prompts = []
    for source in sources:
        data = load_data(source)
        prompts.extend(extract_prompts(data))
    
    return prompts
```

### 2. Test Data Validation

#### 2.1 Data Quality Checks
```python
def validate_test_data(prompts: list) -> dict:
    validation = {
        "total_prompts": len(prompts),
        "valid_prompts": 0,
        "invalid_prompts": 0,
        "quality_issues": []
    }
    
    for prompt in prompts:
        if validate_prompt_structure(prompt):
            validation["valid_prompts"] += 1
        else:
            validation["invalid_prompts"] += 1
            validation["quality_issues"].append(prompt["id"])
    
    return validation
```

## Test Reporting

### 1. Test Results Dashboard

#### 1.1 Real-time Monitoring
```python
def generate_test_dashboard(results: list) -> dict:
    dashboard = {
        "overall_status": "healthy",
        "sla_compliance": calculate_sla_compliance(results),
        "performance_metrics": calculate_performance_metrics(results),
        "provider_comparison": compare_providers(results),
        "database_comparison": compare_databases(results),
        "complexity_analysis": analyze_complexity(results)
    }
    
    return dashboard
```

#### 1.2 Historical Trends
```python
def generate_historical_report(results: list, time_period: str) -> dict:
    report = {
        "time_period": time_period,
        "trend_analysis": analyze_trends(results),
        "performance_degradation": detect_degradation(results),
        "improvement_areas": identify_improvements(results),
        "recommendations": generate_recommendations(results)
    }
    
    return report
```

## Test Maintenance

### 1. Regular Updates

#### 1.1 Prompt Suite Updates
- **Weekly**: Add new prompts based on user feedback
- **Monthly**: Review and update existing prompts
- **Quarterly**: Comprehensive prompt suite review
- **Annually**: Complete prompt suite overhaul

#### 1.2 Test Framework Updates
- **Monthly**: Update test execution framework
- **Quarterly**: Review and update validation logic
- **Annually**: Evaluate and update testing tools

### 2. Quality Assurance

#### 2.1 Test Validation
- **Peer Review**: All new prompts reviewed by team
- **Automated Validation**: Automated quality checks
- **User Testing**: Real user validation of prompts
- **Performance Testing**: Regular performance validation

#### 2.2 Continuous Improvement
- **Feedback Loop**: Collect and incorporate feedback
- **Metrics Analysis**: Regular analysis of test metrics
- **Best Practices**: Document and share best practices
- **Tool Evaluation**: Regular evaluation of testing tools

---

## Appendix

### A. Prompt Templates
- **Basic Facts**: 100+ templates for factual questions
- **Definitions**: 50+ templates for definition requests
- **Calculations**: 30+ templates for mathematical problems
- **Code Generation**: 40+ templates for programming tasks
- **Technical Explanations**: 60+ templates for technical concepts
- **Research Questions**: 80+ templates for complex analysis

### B. Test Tools
- **Pytest**: Test execution framework
- **Allure**: Test reporting and visualization
- **JMeter**: Load testing for API endpoints
- **Selenium**: Web UI testing
- **Postman**: API testing and validation

### C. Test Metrics
- **Coverage**: Test coverage percentage
- **Quality**: Response quality scores
- **Performance**: Response time metrics
- **Reliability**: SLA compliance rates
