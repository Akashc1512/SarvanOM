"""
Unit Tests for Prompt Template System
Tests the modular prompt template system with validation and formatting.

Authors:
- Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
from typing import Dict, Any

from shared.core.prompt_templates import (
    PromptTemplate,
    PromptTemplateManager,
    TemplateType,
    Language
)


class TestPromptTemplate:
    """Test prompt template functionality."""
    
    def test_prompt_template_creation(self):
        """Test prompt template creation."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, how are you?",
            variables=["name"],
            template_type=TemplateType.SYNTHESIS,
            language=Language.EN,
            version="1.0.0",
            description="Test template",
            max_tokens=500,
            temperature=0.2
        )
        
        assert template.name == "test_template"
        assert template.template == "Hello {name}, how are you?"
        assert template.variables == ["name"]
        assert template.template_type == TemplateType.SYNTHESIS
        assert template.language == Language.EN
        assert template.version == "1.0.0"
        assert template.description == "Test template"
        assert template.max_tokens == 500
        assert template.temperature == 0.2
    
    def test_prompt_template_auto_variable_extraction(self):
        """Test automatic variable extraction from template."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old and live in {city}."
        )
        
        assert "name" in template.variables
        assert "age" in template.variables
        assert "city" in template.variables
        assert len(template.variables) == 3
    
    def test_prompt_template_formatting(self):
        """Test template formatting with variables."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old.",
            variables=["name", "age"]
        )
        
        result = template.format(name="John", age=30)
        assert result == "Hello John, you are 30 years old."
    
    def test_prompt_template_formatting_missing_variable(self):
        """Test template formatting with missing variable."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old.",
            variables=["name", "age"]
        )
        
        with pytest.raises(ValueError, match="Missing required variable"):
            template.format(name="John")
    
    def test_prompt_template_formatting_extra_variable(self):
        """Test template formatting with extra variable."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old.",
            variables=["name", "age"]
        )
        
        result = template.format(name="John", age=30, extra="ignored")
        assert result == "Hello John, you are 30 years old."
    
    def test_prompt_template_validation(self):
        """Test template validation."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old.",
            variables=["name", "age"]
        )
        
        # Valid variables
        assert template.validate_variables(name="John", age=30)
        
        # Missing variables
        assert not template.validate_variables(name="John")
        assert not template.validate_variables(age=30)
        assert not template.validate_variables()
    
    def test_prompt_template_validation_empty_template(self):
        """Test template validation with empty template."""
        with pytest.raises(ValueError, match="Template cannot be empty"):
            PromptTemplate(
                name="test_template",
                template=""
            )
    
    def test_prompt_template_validation_long_template(self):
        """Test template validation with very long template."""
        long_template = "x" * 10001  # Over 10000 character limit
        
        with pytest.raises(ValueError, match="Template too long"):
            PromptTemplate(
                name="test_template",
                template=long_template
            )
    
    def test_prompt_template_to_dict(self):
        """Test template serialization to dictionary."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}",
            variables=["name"],
            template_type=TemplateType.SYNTHESIS,
            language=Language.EN,
            version="1.0.0",
            description="Test template",
            max_tokens=500,
            temperature=0.2
        )
        
        template_dict = template.to_dict()
        
        assert template_dict["name"] == "test_template"
        assert template_dict["template"] == "Hello {name}"
        assert template_dict["variables"] == ["name"]
        assert template_dict["template_type"] == TemplateType.SYNTHESIS.value
        assert template_dict["language"] == Language.EN.value
        assert template_dict["version"] == "1.0.0"
        assert template_dict["description"] == "Test template"
        assert template_dict["max_tokens"] == 500
        assert template_dict["temperature"] == 0.2


class TestPromptTemplateManager:
    """Test prompt template manager functionality."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_template_manager_initialization(self, template_manager):
        """Test template manager initialization."""
        assert len(template_manager.templates) > 0
        
        # Check that default templates are loaded
        assert "synthesis_answer" in template_manager.templates
        assert "factcheck_verification" in template_manager.templates
        assert "retrieval_query_expansion" in template_manager.templates
    
    def test_template_manager_get_template(self, template_manager):
        """Test getting template by name."""
        template = template_manager.get_template("synthesis_answer")
        
        assert template.name == "synthesis_answer"
        assert template.template_type == TemplateType.SYNTHESIS
        assert "query" in template.variables
        assert "facts" in template.variables
    
    def test_template_manager_get_nonexistent_template(self, template_manager):
        """Test getting nonexistent template."""
        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            template_manager.get_template("nonexistent")
    
    def test_template_manager_get_templates_by_type(self, template_manager):
        """Test getting templates by type."""
        synthesis_templates = template_manager.get_templates_by_type(TemplateType.SYNTHESIS)
        factcheck_templates = template_manager.get_templates_by_type(TemplateType.FACT_CHECK)
        retrieval_templates = template_manager.get_templates_by_type(TemplateType.RETRIEVAL)
        
        assert len(synthesis_templates) > 0
        assert len(factcheck_templates) > 0
        assert len(retrieval_templates) > 0
        
        for template in synthesis_templates:
            assert template.template_type == TemplateType.SYNTHESIS
        
        for template in factcheck_templates:
            assert template.template_type == TemplateType.FACT_CHECK
        
        for template in retrieval_templates:
            assert template.template_type == TemplateType.RETRIEVAL
    
    def test_template_manager_add_template(self, template_manager):
        """Test adding new template."""
        new_template = PromptTemplate(
            name="custom_template",
            template="Custom template with {variable}",
            variables=["variable"],
            template_type=TemplateType.SYNTHESIS
        )
        
        template_manager.add_template(new_template)
        
        assert "custom_template" in template_manager.templates
        assert template_manager.get_template("custom_template") == new_template
    
    def test_template_manager_remove_template(self, template_manager):
        """Test removing template."""
        template_name = "synthesis_answer"
        assert template_name in template_manager.templates
        
        template_manager.remove_template(template_name)
        
        assert template_name not in template_manager.templates
    
    def test_template_manager_remove_nonexistent_template(self, template_manager):
        """Test removing nonexistent template."""
        # Should not raise an error
        template_manager.remove_template("nonexistent")
    
    def test_template_manager_list_templates(self, template_manager):
        """Test listing all template names."""
        template_names = template_manager.list_templates()
        
        assert len(template_names) > 0
        assert "synthesis_answer" in template_names
        assert "factcheck_verification" in template_names
        assert "retrieval_query_expansion" in template_names
    
    def test_template_manager_export_templates(self, template_manager):
        """Test exporting templates as dictionary."""
        templates_dict = template_manager.export_templates()
        
        assert isinstance(templates_dict, dict)
        assert len(templates_dict) > 0
        
        # Check that exported templates have required fields
        for name, template_data in templates_dict.items():
            assert "name" in template_data
            assert "template" in template_data
            assert "variables" in template_data
            assert "template_type" in template_data
    
    def test_template_manager_import_templates(self, template_manager):
        """Test importing templates from dictionary."""
        # Create test templates data
        templates_data = {
            "imported_template_1": {
                "name": "imported_template_1",
                "template": "Imported template 1 with {var1}",
                "variables": ["var1"],
                "template_type": TemplateType.SYNTHESIS.value,
                "language": Language.EN.value,
                "version": "1.0.0",
                "description": "Imported template 1",
                "max_tokens": 500,
                "temperature": 0.2
            },
            "imported_template_2": {
                "name": "imported_template_2",
                "template": "Imported template 2 with {var2}",
                "variables": ["var2"],
                "template_type": TemplateType.FACT_CHECK.value,
                "language": Language.EN.value,
                "version": "1.0.0",
                "description": "Imported template 2",
                "max_tokens": 300,
                "temperature": 0.1
            }
        }
        
        # Import templates
        template_manager.import_templates(templates_data)
        
        # Verify templates were imported
        assert "imported_template_1" in template_manager.templates
        assert "imported_template_2" in template_manager.templates
        
        # Verify template properties
        template1 = template_manager.get_template("imported_template_1")
        assert template1.template_type == TemplateType.SYNTHESIS
        assert template1.variables == ["var1"]
        
        template2 = template_manager.get_template("imported_template_2")
        assert template2.template_type == TemplateType.FACT_CHECK
        assert template2.variables == ["var2"]


class TestSynthesisTemplates:
    """Test synthesis-specific templates."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_synthesis_answer_template(self, template_manager):
        """Test synthesis answer template."""
        template = template_manager.get_template("synthesis_answer")
        
        # Test template properties
        assert template.template_type == TemplateType.SYNTHESIS
        assert "query" in template.variables
        assert "facts" in template.variables
        assert template.max_tokens == 1500
        assert template.temperature == 0.3
        
        # Test template formatting
        result = template.format(
            query="What is machine learning?",
            facts="1. Machine learning is a subset of AI\n2. It uses algorithms to learn patterns"
        )
        
        assert "What is machine learning?" in result
        assert "Machine learning is a subset of AI" in result
        assert "It uses algorithms to learn patterns" in result
        assert "You are an expert knowledge synthesis agent" in result
    
    def test_synthesis_summary_template(self, template_manager):
        """Test synthesis summary template."""
        template = template_manager.get_template("synthesis_summary")
        
        # Test template properties
        assert template.template_type == TemplateType.SYNTHESIS
        assert "content" in template.variables
        assert "max_length" in template.variables
        assert template.max_tokens == 500
        assert template.temperature == 0.2
        
        # Test template formatting
        result = template.format(
            content="This is a long text that needs to be summarized.",
            max_length=100
        )
        
        assert "This is a long text that needs to be summarized" in result
        assert "100" in result
        assert "You are an expert summarization agent" in result
    
    def test_synthesis_comparison_template(self, template_manager):
        """Test synthesis comparison template."""
        template = template_manager.get_template("synthesis_comparison")
        
        # Test template properties
        assert template.template_type == TemplateType.SYNTHESIS
        assert "topic_a" in template.variables
        assert "info_a" in template.variables
        assert "topic_b" in template.variables
        assert "info_b" in template.variables
        
        # Test template formatting
        result = template.format(
            topic_a="Machine Learning",
            info_a="Uses algorithms to learn patterns",
            topic_b="Deep Learning",
            info_b="Uses neural networks with multiple layers"
        )
        
        assert "Machine Learning" in result
        assert "Deep Learning" in result
        assert "Uses algorithms to learn patterns" in result
        assert "Uses neural networks with multiple layers" in result
        assert "You are an expert comparative analysis agent" in result


class TestFactCheckTemplates:
    """Test fact-checking-specific templates."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_factcheck_verification_template(self, template_manager):
        """Test fact-checking verification template."""
        template = template_manager.get_template("factcheck_verification")
        
        # Test template properties
        assert template.template_type == TemplateType.FACT_CHECK
        assert "claim" in template.variables
        assert "evidence" in template.variables
        assert template.max_tokens == 800
        assert template.temperature == 0.1
        
        # Test template formatting
        result = template.format(
            claim="The Earth is round",
            evidence="Multiple scientific sources confirm that the Earth is spherical."
        )
        
        assert "The Earth is round" in result
        assert "Multiple scientific sources confirm" in result
        assert "You are an expert fact-checking agent" in result
        assert "Verification Result" in result
        assert "Confidence Score" in result
    
    def test_factcheck_decomposition_template(self, template_manager):
        """Test fact-checking decomposition template."""
        template = template_manager.get_template("factcheck_decomposition")
        
        # Test template properties
        assert template.template_type == TemplateType.FACT_CHECK
        assert "claim" in template.variables
        
        # Test template formatting
        result = template.format(
            claim="Machine learning is a subset of artificial intelligence that uses algorithms to learn patterns from data"
        )
        
        assert "Machine learning is a subset of artificial intelligence" in result
        assert "You are an expert claim analysis agent" in result
        assert "Decomposed Claims" in result
        assert "Implicit Assumptions" in result
        assert "Verifiable Statements" in result
    
    def test_factcheck_evidence_evaluation_template(self, template_manager):
        """Test fact-checking evidence evaluation template."""
        template = template_manager.get_template("factcheck_evidence_evaluation")
        
        # Test template properties
        assert template.template_type == TemplateType.FACT_CHECK
        assert "evidence" in template.variables
        assert "claim" in template.variables
        
        # Test template formatting
        result = template.format(
            evidence="Scientific paper published in Nature journal",
            claim="The Earth is round"
        )
        
        assert "Scientific paper published in Nature journal" in result
        assert "The Earth is round" in result
        assert "You are an expert evidence evaluation agent" in result
        assert "Evidence Evaluation" in result
        assert "Relevance" in result
        assert "Reliability" in result


class TestRetrievalTemplates:
    """Test retrieval-specific templates."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_retrieval_query_expansion_template(self, template_manager):
        """Test retrieval query expansion template."""
        template = template_manager.get_template("retrieval_query_expansion")
        
        # Test template properties
        assert template.template_type == TemplateType.RETRIEVAL
        assert "query" in template.variables
        assert template.max_tokens == 400
        assert template.temperature == 0.3
        
        # Test template formatting
        result = template.format(
            query="What is machine learning?"
        )
        
        assert "What is machine learning?" in result
        assert "You are an expert information retrieval agent" in result
        assert "Key Concepts" in result
        assert "Entities" in result
        assert "Related Terms" in result
        assert "Expanded Queries" in result
    
    def test_retrieval_reranking_template(self, template_manager):
        """Test retrieval reranking template."""
        template = template_manager.get_template("retrieval_reranking")
        
        # Test template properties
        assert template.template_type == TemplateType.RETRIEVAL
        assert "query" in template.variables
        assert "results" in template.variables
        assert "top_k" in template.variables
        
        # Test template formatting
        result = template.format(
            query="What is machine learning?",
            results="1. Content: Machine learning is...\n2. Content: AI algorithms...",
            top_k=5
        )
        
        assert "What is machine learning?" in result
        assert "Machine learning is..." in result
        assert "AI algorithms..." in result
        assert "5" in result
        assert "You are an expert information retrieval agent" in result
        assert "Evaluation Criteria" in result
        assert "Reranked Results" in result
    
    def test_retrieval_query_classification_template(self, template_manager):
        """Test retrieval query classification template."""
        template = template_manager.get_template("retrieval_query_classification")
        
        # Test template properties
        assert template.template_type == TemplateType.RETRIEVAL
        assert "query" in template.variables
        assert template.max_tokens == 300
        assert template.temperature == 0.2
        
        # Test template formatting
        result = template.format(
            query="How do I implement a neural network?"
        )
        
        assert "How do I implement a neural network?" in result
        assert "You are an expert query analysis agent" in result
        assert "Query Analysis" in result
        assert "Primary Intent" in result
        assert "Query Type" in result
        assert "Information Depth" in result


class TestCitationTemplates:
    """Test citation-specific templates."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_citation_generation_template(self, template_manager):
        """Test citation generation template."""
        template = template_manager.get_template("citation_generation")
        
        # Test template properties
        assert template.template_type == TemplateType.CITATION
        assert "answer" in template.variables
        assert "sources" in template.variables
        assert "citation_format" in template.variables
        
        # Test template formatting
        result = template.format(
            answer="Machine learning is a subset of artificial intelligence.",
            sources="1. Source A: Introduction to ML\n2. Source B: AI Fundamentals",
            citation_format="APA"
        )
        
        assert "Machine learning is a subset of artificial intelligence" in result
        assert "Source A: Introduction to ML" in result
        assert "Source B: AI Fundamentals" in result
        assert "APA" in result
        assert "You are an expert citation agent" in result
        assert "Citations" in result
    
    def test_citation_relevance_scoring_template(self, template_manager):
        """Test citation relevance scoring template."""
        template = template_manager.get_template("citation_relevance_scoring")
        
        # Test template properties
        assert template.template_type == TemplateType.CITATION
        assert "query" in template.variables
        assert "sources" in template.variables
        
        # Test template formatting
        result = template.format(
            query="What is machine learning?",
            sources="1. Source A: Introduction to ML\n2. Source B: Cooking Recipes"
        )
        
        assert "What is machine learning?" in result
        assert "Source A: Introduction to ML" in result
        assert "Source B: Cooking Recipes" in result
        assert "You are an expert source evaluation agent" in result
        assert "Relevance Scores" in result
        assert "Most Relevant Sources" in result


class TestQueryProcessingTemplates:
    """Test query processing-specific templates."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager for testing."""
        return PromptTemplateManager()
    
    def test_query_intent_classification_template(self, template_manager):
        """Test query intent classification template."""
        template = template_manager.get_template("query_intent_classification")
        
        # Test template properties
        assert template.template_type == TemplateType.QUERY_PROCESSING
        assert "query" in template.variables
        assert template.max_tokens == 300
        assert template.temperature == 0.2
        
        # Test template formatting
        result = template.format(
            query="What is the capital of France?"
        )
        
        assert "What is the capital of France?" in result
        assert "You are an expert query analysis agent" in result
        assert "Query Analysis" in result
        assert "Primary Intent" in result
        assert "Query Type" in result
        assert "Information Depth" in result
    
    def test_query_refinement_template(self, template_manager):
        """Test query refinement template."""
        template = template_manager.get_template("query_refinement")
        
        # Test template properties
        assert template.template_type == TemplateType.QUERY_PROCESSING
        assert "query" in template.variables
        assert "context" in template.variables
        
        # Test template formatting
        result = template.format(
            query="ML",
            context="User is interested in machine learning algorithms"
        )
        
        assert "ML" in result
        assert "User is interested in machine learning algorithms" in result
        assert "You are an expert query refinement agent" in result
        assert "Query Analysis" in result
        assert "Ambiguous Aspects" in result
        assert "Missing Context" in result
        assert "Refinement Suggestions" in result
        assert "Refined Queries" in result


if __name__ == "__main__":
    pytest.main([__file__]) 