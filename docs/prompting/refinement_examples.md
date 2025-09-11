# Guided Prompt Refinement Examples

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Product Team  

## Overview

This document provides comprehensive examples of how the Guided Prompt Confirmation feature refines ambiguous or unclear user queries. Each example demonstrates the transformation from a raw user input to a refined, actionable query that will produce better results.

## Example Categories

### 1. Ambiguous Entity References

#### Example 1: Company vs. Fruit
**Original Query**: "show me apple"
**Analysis**: Ambiguous reference - could refer to Apple Inc. (company) or the fruit
**Refined Query**: "Show me information about Apple Inc. (AAPL) stock performance and company overview"
**Confidence**: 0.85
**Reasoning**: "The query 'apple' is ambiguous. Based on context and common usage patterns, this likely refers to Apple Inc. stock information rather than the fruit."
**Suggested Lane**: Technical
**User Choice**: ✅ Confirmed

#### Example 2: Multiple Companies
**Original Query**: "tesla news"
**Analysis**: Clear entity but could benefit from specificity
**Refined Query**: "Show me the latest news about Tesla Inc. (TSLA) including stock performance, company updates, and industry developments"
**Confidence**: 0.90
**Reasoning**: "Tesla is clearly identified, but adding context about stock performance and industry developments will provide more comprehensive results."
**Suggested Lane**: Research
**User Choice**: ✅ Confirmed

#### Example 3: Geographic Ambiguity
**Original Query**: "weather in paris"
**Analysis**: Geographic ambiguity - multiple cities named Paris
**Refined Query**: "Show me current weather conditions in Paris, France (or specify if you meant Paris, Texas)"
**Confidence**: 0.75
**Reasoning**: "Paris could refer to multiple cities. Paris, France is most common, but clarification helps ensure accurate results."
**Suggested Lane**: Simple
**User Choice**: ✏️ Edited to "weather in paris france"

### 2. Vague Technical Queries

#### Example 4: Programming Language Ambiguity
**Original Query**: "how to sort array"
**Analysis**: Missing programming language context
**Refined Query**: "How to sort an array in [specify programming language: Python, JavaScript, Java, C++, etc.] with code examples and performance considerations"
**Confidence**: 0.80
**Reasoning**: "Array sorting methods vary significantly by programming language. Specifying the language will provide more relevant and accurate code examples."
**Suggested Lane**: Technical
**User Choice**: ✏️ Edited to "how to sort array in python"

#### Example 5: Database Query Ambiguity
**Original Query**: "optimize database"
**Analysis**: Too vague - missing database type and specific optimization goals
**Refined Query**: "How to optimize [specify database: MySQL, PostgreSQL, MongoDB, etc.] performance including indexing, query optimization, and configuration tuning"
**Confidence**: 0.85
**Reasoning**: "Database optimization strategies differ significantly between database types. Specific guidance requires knowing the database system and optimization goals."
**Suggested Lane**: Technical
**User Choice**: ✏️ Edited to "optimize postgresql performance"

#### Example 6: API Integration Ambiguity
**Original Query**: "connect to api"
**Analysis**: Missing API type and integration context
**Refined Query**: "How to connect to [specify API: REST, GraphQL, WebSocket, etc.] with authentication, error handling, and best practices for [specify language/framework]"
**Confidence**: 0.75
**Reasoning**: "API integration approaches vary by API type and technology stack. Specific guidance requires more context about the API and implementation environment."
**Suggested Lane**: Technical
**User Choice**: ✏️ Edited to "connect to rest api in python"

### 3. Research and Analysis Queries

#### Example 7: Market Research Ambiguity
**Original Query**: "market analysis"
**Analysis**: Too broad - missing industry, region, and time frame
**Refined Query**: "Provide market analysis for [specify industry] in [specify region] including market size, growth trends, key players, and competitive landscape for [specify time period]"
**Confidence**: 0.90
**Reasoning**: "Market analysis requires specific industry, geographic, and temporal context to provide actionable insights."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "market analysis for ai industry in north america 2024"

#### Example 8: Academic Research Ambiguity
**Original Query**: "climate change research"
**Analysis**: Too broad - missing specific research focus
**Refined Query**: "Show me recent research on [specify aspect: climate change impacts, mitigation strategies, adaptation measures, policy analysis, etc.] including peer-reviewed studies, key findings, and research gaps"
**Confidence**: 0.85
**Reasoning**: "Climate change research is vast. Specifying the research focus will provide more targeted and relevant academic sources."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "climate change mitigation strategies research"

#### Example 9: Historical Research Ambiguity
**Original Query**: "world war 2"
**Analysis**: Too broad - missing specific aspect or focus
**Refined Query**: "Provide information about [specify aspect: causes, major battles, key figures, political developments, social impact, etc.] of World War II with historical context and primary sources"
**Confidence**: 0.80
**Reasoning**: "World War II is a complex historical topic. Specifying the aspect of interest will provide more focused and comprehensive information."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "world war 2 major battles and strategies"

### 4. Business and Finance Queries

#### Example 10: Investment Ambiguity
**Original Query**: "invest in stocks"
**Analysis**: Missing investment strategy and risk profile
**Refined Query**: "Provide investment advice for [specify: beginner, intermediate, advanced] investors including stock selection strategies, risk management, and portfolio diversification for [specify: short-term, long-term] goals"
**Confidence**: 0.85
**Reasoning**: "Investment advice should be tailored to experience level and investment goals. Generic advice may not be appropriate for all investors."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "beginner stock investment strategies"

#### Example 11: Business Strategy Ambiguity
**Original Query**: "business growth"
**Analysis**: Missing business type and growth stage
**Refined Query**: "Show me business growth strategies for [specify: startup, small business, enterprise] in [specify industry] including market expansion, product development, and operational scaling"
**Confidence**: 0.80
**Reasoning**: "Business growth strategies vary significantly by company size, industry, and growth stage. Specific guidance requires more context."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "startup growth strategies for saas companies"

#### Example 12: Financial Planning Ambiguity
**Original Query**: "retirement planning"
**Analysis**: Missing age, income, and retirement goals
**Refined Query**: "Provide retirement planning guidance for [specify age group] with [specify income level] including savings strategies, investment options, and tax considerations for [specify retirement goals]"
**Confidence**: 0.75
**Reasoning**: "Retirement planning is highly personalized. Age, income, and goals significantly impact recommended strategies."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "retirement planning for 30 year old with 100k income"

### 5. Health and Wellness Queries

#### Example 13: Medical Information Ambiguity
**Original Query**: "headache treatment"
**Analysis**: Missing headache type and severity
**Refined Query**: "Provide information about [specify: tension, migraine, cluster, etc.] headache treatment options including home remedies, medications, and when to seek medical attention"
**Confidence**: 0.80
**Reasoning**: "Headache treatment varies by type and severity. Specific guidance requires understanding the headache characteristics."
**Suggested Lane**: Simple
**User Choice**: ✏️ Edited to "migraine headache treatment options"

#### Example 14: Fitness Ambiguity
**Original Query**: "lose weight"
**Analysis**: Missing current fitness level and weight loss goals
**Refined Query**: "Show me weight loss strategies for [specify: beginner, intermediate, advanced] fitness level including diet plans, exercise routines, and realistic timeline for [specify weight loss goal]"
**Confidence**: 0.85
**Reasoning**: "Weight loss strategies should be tailored to fitness level and goals. Generic advice may not be safe or effective for all individuals."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "beginner weight loss plan for 20 pounds"

#### Example 15: Nutrition Ambiguity
**Original Query**: "healthy diet"
**Analysis**: Missing dietary restrictions and health goals
**Refined Query**: "Provide healthy diet recommendations for [specify: weight loss, muscle gain, general health, specific health conditions] considering [specify: dietary restrictions, allergies, preferences]"
**Confidence**: 0.75
**Reasoning**: "Healthy diet recommendations should consider individual health goals, restrictions, and preferences for personalized guidance."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "healthy diet for weight loss with no restrictions"

### 6. Travel and Lifestyle Queries

#### Example 16: Travel Planning Ambiguity
**Original Query**: "travel to europe"
**Analysis**: Missing destination, budget, and travel preferences
**Refined Query**: "Provide travel planning information for [specify: budget, mid-range, luxury] trip to [specify countries/cities] in Europe including attractions, accommodations, transportation, and [specify: solo, couple, family] travel tips"
**Confidence**: 0.85
**Reasoning**: "Europe travel planning requires specific destinations, budget, and travel style for relevant recommendations."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "budget travel to paris and rome for couple"

#### Example 17: Home Improvement Ambiguity
**Original Query**: "kitchen renovation"
**Analysis**: Missing budget, style preferences, and scope
**Refined Query**: "Show me kitchen renovation ideas for [specify: budget range] including [specify: modern, traditional, farmhouse, etc.] style with [specify: minor updates, major renovation, full remodel] scope"
**Confidence**: 0.80
**Reasoning**: "Kitchen renovation advice varies significantly by budget, style, and scope. Specific guidance requires understanding these parameters."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "modern kitchen renovation under 20k"

#### Example 18: Career Development Ambiguity
**Original Query**: "career change"
**Analysis**: Missing current field and target industry
**Refined Query**: "Provide career change guidance for transitioning from [specify current field] to [specify target industry] including skill development, networking strategies, and timeline considerations"
**Confidence**: 0.75
**Reasoning**: "Career change strategies vary by current field and target industry. Specific guidance requires understanding both contexts."
**Suggested Lane**: Research
**User Choice**: ✏️ Edited to "career change from marketing to software development"

### 7. Technology and Innovation Queries

#### Example 19: AI/ML Ambiguity
**Original Query**: "machine learning"
**Analysis**: Missing application area and experience level
**Refined Query**: "Show me machine learning information for [specify: beginners, intermediate, advanced] including [specify: theory, practical applications, specific algorithms, tools, etc.] in [specify domain: healthcare, finance, marketing, etc.]"
**Confidence**: 0.85
**Reasoning**: "Machine learning is a broad field. Specific guidance requires understanding the application area and experience level."
**Suggested Lane**: Technical
**User Choice**: ✏️ Edited to "machine learning for beginners in healthcare"

#### Example 20: Blockchain Ambiguity
**Original Query**: "blockchain technology"
**Analysis**: Missing specific aspect and use case
**Refined Query**: "Provide information about [specify: blockchain basics, cryptocurrency, smart contracts, DeFi, NFTs, etc.] including [specify: technical details, business applications, investment opportunities, etc.]"
**Confidence**: 0.80
**Reasoning**: "Blockchain technology encompasses many aspects. Specific guidance requires understanding the area of interest."
**Suggested Lane**: Technical
**User Choice**: ✏️ Edited to "blockchain smart contracts for business applications"

## User Interaction Patterns

### 1. High Acceptance Rate Examples
- **Financial Queries**: Users typically accept refinements for investment and business queries
- **Technical Queries**: Developers often accept refinements for programming and system queries
- **Research Queries**: Students and researchers frequently accept refinements for academic queries

### 2. High Edit Rate Examples
- **Personal Queries**: Users often edit refinements for health, fitness, and personal finance
- **Location-Specific Queries**: Users frequently edit geographic refinements
- **Time-Sensitive Queries**: Users often edit refinements for current events and news

### 3. High Skip Rate Examples
- **Simple Factual Queries**: Users often skip refinements for basic information requests
- **Well-Formed Queries**: Users typically skip refinements for already clear queries
- **Urgent Queries**: Users frequently skip refinements when they need immediate answers

## Confidence Score Guidelines

### 1. High Confidence (0.8-1.0)
- Clear ambiguity with obvious resolution
- Well-established patterns and common use cases
- Specific domain knowledge requirements

### 2. Medium Confidence (0.5-0.8)
- Moderate ambiguity with likely resolution
- Some context clues available
- General domain knowledge helpful

### 3. Low Confidence (0.0-0.5)
- Minimal ambiguity or unclear resolution
- Limited context clues
- Generic or overly broad queries

## Refinement Quality Metrics

### 1. Acceptance Rate by Category
```yaml
acceptance_rates:
  financial_queries: 0.85
  technical_queries: 0.80
  research_queries: 0.75
  health_queries: 0.70
  travel_queries: 0.65
  general_queries: 0.60
```

### 2. Edit Rate by Category
```yaml
edit_rates:
  personal_queries: 0.40
  location_queries: 0.35
  time_sensitive_queries: 0.30
  technical_queries: 0.25
  financial_queries: 0.20
  research_queries: 0.15
```

### 3. Skip Rate by Category
```yaml
skip_rates:
  simple_factual: 0.50
  well_formed: 0.45
  urgent_queries: 0.40
  personal_queries: 0.30
  technical_queries: 0.20
  research_queries: 0.15
```

## Best Practices for Refinement

### 1. Refinement Principles
- **Clarity**: Make the query more specific and actionable
- **Context**: Add relevant context and constraints
- **Completeness**: Ensure all necessary information is included
- **Accuracy**: Maintain the original intent while improving clarity

### 2. Refinement Techniques
- **Entity Disambiguation**: Resolve ambiguous references
- **Context Addition**: Add relevant background information
- **Constraint Specification**: Include specific requirements
- **Scope Definition**: Define the scope and boundaries

### 3. Refinement Quality Checks
- **Intent Preservation**: Ensure original intent is maintained
- **Clarity Improvement**: Verify the refined query is clearer
- **Completeness**: Check that all necessary information is included
- **Accuracy**: Validate that the refinement is factually correct

---

## Appendix

### A. Refinement Templates
- Entity disambiguation template
- Context addition template
- Constraint specification template
- Scope definition template

### B. Quality Metrics
- Acceptance rate tracking
- Edit rate analysis
- Skip rate monitoring
- User satisfaction scores

### C. Continuous Improvement
- Refinement pattern analysis
- User feedback integration
- A/B testing results
- Performance optimization
