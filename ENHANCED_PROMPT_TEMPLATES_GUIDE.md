# Enhanced Prompt Templates Guide

## Overview

This document describes the enhanced prompt templates implemented to improve factuality, reduce hallucinations, and encourage proper citations in the LLM-based answer generation system.

## Key Improvements

### 1. Enhanced System Messages

**Before:**
```
You are an expert knowledge synthesis agent. Your task is to create a comprehensive, accurate, and well-structured answer based on the provided verified facts.
```

**After:**
```
You are an AI research assistant with expertise in providing accurate, well-sourced answers to questions. Your role is to synthesize information from provided documents and create comprehensive, factual responses.

SYSTEM CONTEXT:
- You are a knowledge synthesis expert working with verified facts and source documents
- Your primary goal is to provide accurate, well-structured answers grounded in the provided evidence
- You must cite sources for every factual claim you make
- If you are unsure about any information, clearly state that you don't know
- Maintain academic rigor and avoid speculation or unsupported claims
```

### 2. Explicit Citation Instructions

**New Features:**
- **Citation placeholders**: Use `[1]`, `[2]`, etc. format for inline citations
- **Source attribution**: Every factual claim must have a corresponding citation
- **Citation processing**: CitationAgent processes placeholders into formatted citations
- **Source list**: Comprehensive source list at the end of responses

### 3. Enhanced Factuality Guidelines

**Key Principles:**
- Ground answers in retrieved content only
- Acknowledge when information is insufficient
- Present conflicting information clearly
- Maintain transparency about uncertainty
- Avoid speculation and unsupported claims

## Template Types

### 1. Synthesis Answer Template (`synthesis_answer`)

**Purpose:** Main template for creating comprehensive answers from verified facts.

**Key Features:**
- Enhanced system context with factuality guidelines
- Explicit citation requirements
- Clear structure for user questions and documents
- Comprehensive instructions for answer generation

**Usage:**
```python
template = template_manager.get_template("synthesis_answer")
prompt = template.format(
    query="What is Python?",
    documents=documents_text,
    max_length=1000
)
```

### 2. Hybrid Retrieval Template (`synthesis_hybrid_retrieval`)

**Purpose:** Combines retrieved documents with knowledge graph information.

**Key Features:**
- Integrates multiple information sources
- Prioritizes retrieved documents over knowledge graph data
- Handles conflicting information gracefully
- Maintains source attribution for all claims

**Usage:**
```python
template = template_manager.get_template("synthesis_hybrid_retrieval")
prompt = template.format(
    query="How does machine learning work?",
    retrieved_docs=retrieved_documents,
    kg_info=knowledge_graph_data,
    max_length=1000
)
```

### 3. Fact-Checked Template (`synthesis_fact_checked`)

**Purpose:** Creates answers based on verified, fact-checked information.

**Key Features:**
- Works with pre-verified facts
- Includes confidence levels for claims
- Emphasizes transparency about verification status
- Handles incomplete verification gracefully

**Usage:**
```python
template = template_manager.get_template("synthesis_fact_checked")
prompt = template.format(
    query="What are the benefits of renewable energy?",
    verified_facts=verified_facts_list,
    max_length=1000
)
```

### 4. Citation Generation Template (`citation_generation`)

**Purpose:** Processes answers with citation placeholders into properly formatted citations.

**Key Features:**
- Identifies and processes citation placeholders
- Matches placeholders to appropriate sources
- Generates formatted citations in specified style
- Maintains answer readability while adding citations

**Usage:**
```python
template = template_manager.get_template("citation_generation")
prompt = template.format(
    answer=answer_with_placeholders,
    sources=sources_list,
    citation_format="APA"
)
```

## System Message Integration

### Enhanced LLM Client Usage

The enhanced templates work with the LLM client's system message support:

```python
from shared.core.llm_client_v3 import LLMRequest

system_message = """You are an AI research assistant with expertise in providing accurate, well-sourced answers to questions. Your role is to synthesize information from provided documents and create comprehensive, factual responses.

Your primary responsibilities:
- Provide accurate, well-structured answers grounded in the provided evidence
- Cite sources for every factual claim you make using [1], [2], etc. format
- If you are unsure about any information, clearly state that you don't know
- Maintain academic rigor and avoid speculation or unsupported claims
- Structure responses logically with clear sections and flow
- If documents contain contradictory information, acknowledge the conflict and present both perspectives
- Keep responses concise but complete and include a "Sources" section at the end"""

llm_request = LLMRequest(
    prompt=formatted_prompt,
    system_message=system_message,
    max_tokens=1000,
    temperature=0.2
)
```

## Citation Processing Workflow

### 1. Synthesis Agent
- Generates answers with citation placeholders `[1]`, `[2]`, etc.
- Includes source list at the end
- Uses enhanced templates for better factuality

### 2. Citation Agent
- Processes answers with citation placeholders
- Matches placeholders to appropriate sources
- Generates properly formatted citations
- Replaces placeholders with citations

### 3. Final Output
- Clean, properly cited answer
- Comprehensive source list
- Academic-quality formatting

## Benefits

### 1. Improved Factuality
- **Reduced hallucinations**: Explicit grounding in provided documents
- **Better source attribution**: Every claim has a corresponding citation
- **Transparency**: Clear indication when information is insufficient
- **Conflict handling**: Acknowledges and presents conflicting information

### 2. Enhanced Citations
- **Consistent formatting**: Standardized citation styles
- **Source tracking**: Complete source list with metadata
- **Placeholder system**: Easy processing by CitationAgent
- **Academic rigor**: Professional citation standards

### 3. Better User Experience
- **Clear structure**: Logical organization of information
- **Source transparency**: Users can verify claims
- **Confidence indicators**: Shows reliability of information
- **Comprehensive answers**: Complete responses with proper attribution

## Testing

### Test Script
Run the comprehensive test suite:

```bash
python test_enhanced_prompts.py
```

### Test Coverage
- Template formatting and validation
- LLM generation with system messages
- Citation processing workflows
- Hybrid retrieval synthesis
- Fact-checked synthesis

## Implementation Details

### Template Structure
```python
@dataclass
class PromptTemplate:
    name: str
    template: str
    variables: List[str]
    template_type: TemplateType
    description: str
    max_tokens: int
    temperature: float
```

### Template Manager
```python
template_manager = get_template_manager()
template = template_manager.get_template("synthesis_answer")
prompt = template.format(**variables)
```

### Integration Points
- **SynthesisAgent**: Uses enhanced templates for answer generation
- **CitationAgent**: Processes citation placeholders
- **LLMClient**: Supports system messages for better context
- **PromptTemplates**: Centralized template management

## Best Practices

### 1. Template Usage
- Always use the template manager for consistency
- Validate variables before formatting
- Use appropriate temperature settings (0.2 for factual content)
- Include system messages for better context

### 2. Citation Management
- Use citation placeholders consistently
- Provide comprehensive source metadata
- Process citations through CitationAgent
- Maintain source list integrity

### 3. Factuality Assurance
- Ground all claims in provided sources
- Acknowledge limitations and uncertainty
- Present conflicting information clearly
- Avoid speculation and unsupported claims

## Future Enhancements

### 1. Additional Templates
- Multi-language support
- Domain-specific templates
- Specialized citation formats
- Advanced fact-checking workflows

### 2. Template Optimization
- Performance improvements
- Better variable validation
- Enhanced error handling
- Template versioning

### 3. Integration Features
- Real-time template updates
- A/B testing capabilities
- Template performance metrics
- Automated template validation

## Conclusion

The enhanced prompt templates significantly improve the factuality and citation quality of LLM-generated answers. By providing clear system messages, explicit citation instructions, and comprehensive factuality guidelines, these templates help reduce hallucinations and ensure proper source attribution throughout the answer generation process.

The modular design allows for easy extension and customization while maintaining consistency across different use cases. The integration with the CitationAgent provides a complete workflow for generating well-sourced, academically rigorous responses. 