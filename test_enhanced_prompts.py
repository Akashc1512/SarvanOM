#!/usr/bin/env python3
"""
Test Enhanced Prompt Templates
Validates the improved prompt templates with better factuality and citation instructions.

This script tests:
1. Enhanced synthesis templates with system messages
2. Citation processing with placeholders
3. Hybrid retrieval synthesis
4. Fact-checked synthesis
5. Template validation and formatting

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

from shared.core.prompt_templates import get_template_manager, TemplateType
from shared.core.agents.llm_client import LLMClient
from shared.core.llm_client_v3 import LLMRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedPromptTester:
    """Test enhanced prompt templates for improved factuality and citations."""

    def __init__(self):
        """Initialize the prompt tester."""
        self.template_manager = get_template_manager()
        self.llm_client = LLMClient()

    async def test_synthesis_answer_template(self):
        """Test the enhanced synthesis answer template."""
        logger.info("Testing enhanced synthesis answer template...")

        # Sample data
        query = "What are the main features of Python programming language?"
        documents = [
            "[1] Python is a high-level, interpreted programming language\n   Source: Python.org documentation\n   Confidence: 0.95\n",
            "[2] Python supports object-oriented programming and functional programming\n   Source: Python tutorial\n   Confidence: 0.92\n",
            "[3] Python has a large standard library and extensive third-party packages\n   Source: PyPI documentation\n   Confidence: 0.88\n"
        ]
        max_length = 500

        # Get template
        template = self.template_manager.get_template("synthesis_answer")
        
        # Format prompt
        prompt = template.format(
            query=query,
            documents="\n".join(documents),
            max_length=max_length
        )

        logger.info(f"Generated prompt length: {len(prompt)} characters")
        logger.info("Prompt preview:")
        logger.info(prompt[:500] + "..." if len(prompt) > 500 else prompt)

        return prompt

    async def test_hybrid_retrieval_template(self):
        """Test the hybrid retrieval synthesis template."""
        logger.info("Testing hybrid retrieval synthesis template...")

        # Sample data
        query = "How does machine learning work?"
        retrieved_docs = [
            "[1] Machine learning is a subset of artificial intelligence\n   Source: ML textbook\n   Confidence: 0.94\n",
            "[2] ML algorithms learn patterns from data without explicit programming\n   Source: Research paper\n   Confidence: 0.91\n"
        ]
        kg_info = [
            "[3] Supervised learning uses labeled training data\n   Source: Knowledge Graph\n   Confidence: 0.89\n",
            "[4] Unsupervised learning finds patterns in unlabeled data\n   Source: Knowledge Graph\n   Confidence: 0.87\n"
        ]
        max_length = 600

        # Get template
        template = self.template_manager.get_template("synthesis_hybrid_retrieval")
        
        # Format prompt
        prompt = template.format(
            query=query,
            retrieved_docs="\n".join(retrieved_docs),
            kg_info="\n".join(kg_info),
            max_length=max_length
        )

        logger.info(f"Generated hybrid prompt length: {len(prompt)} characters")
        return prompt

    async def test_citation_generation_template(self):
        """Test the enhanced citation generation template."""
        logger.info("Testing enhanced citation generation template...")

        # Sample data
        answer = """Python is a high-level programming language [1] that supports multiple programming paradigms [2]. It has a large standard library [3] and extensive third-party packages available through PyPI [4].

The language emphasizes code readability and simplicity [1], making it popular for beginners and experienced developers alike [2]. Python's dynamic typing and automatic memory management [3] contribute to its ease of use.

Sources:
[1] Python.org documentation
[2] Python tutorial
[3] Python standard library documentation
[4] PyPI documentation"""

        sources = [
            {"title": "Python Programming Language", "url": "https://python.org", "author": "Python Software Foundation", "date": "2024"},
            {"title": "Python Tutorial", "url": "https://docs.python.org/tutorial", "author": "Python Documentation", "date": "2024"},
            {"title": "Python Standard Library", "url": "https://docs.python.org/library", "author": "Python Documentation", "date": "2024"},
            {"title": "PyPI Documentation", "url": "https://pypi.org", "author": "Python Package Index", "date": "2024"}
        ]

        # Get template
        template = self.template_manager.get_template("citation_generation")
        
        # Format sources for template
        sources_text = ""
        for i, source in enumerate(sources, 1):
            source_text = f"[{i}] {source['title']} by {source['author']} ({source['date']}) - {source['url']}"
            sources_text += source_text + "\n"

        # Format prompt
        prompt = template.format(
            answer=answer,
            sources=sources_text,
            citation_format="APA"
        )

        logger.info(f"Generated citation prompt length: {len(prompt)} characters")
        return prompt

    async def test_fact_checked_template(self):
        """Test the fact-checked synthesis template."""
        logger.info("Testing fact-checked synthesis template...")

        # Sample data
        query = "What are the benefits of renewable energy?"
        verified_facts = [
            "[1] Solar energy reduces greenhouse gas emissions by 95% compared to coal\n   Source: Energy Research Institute\n   Confidence: 0.94\n",
            "[2] Wind energy is cost-competitive with fossil fuels in many regions\n   Source: International Energy Agency\n   Confidence: 0.91\n",
            "[3] Renewable energy creates more jobs per unit of energy than fossil fuels\n   Source: Department of Energy study\n   Confidence: 0.88\n"
        ]
        max_length = 500

        # Get template
        template = self.template_manager.get_template("synthesis_fact_checked")
        
        # Format prompt
        prompt = template.format(
            query=query,
            verified_facts="\n".join(verified_facts),
            max_length=max_length
        )

        logger.info(f"Generated fact-checked prompt length: {len(prompt)} characters")
        return prompt

    async def test_llm_generation(self, prompt: str, system_message: str = None):
        """Test LLM generation with the enhanced prompt."""
        try:
            if system_message:
                # Use LLMRequest with system message
                from shared.core.llm_client_v3 import LLMRequest
                
                llm_request = LLMRequest(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=800,
                    temperature=0.2
                )
                
                response = await self.llm_client._client.generate_text(llm_request)
            else:
                # Use legacy method
                response = await self.llm_client.generate_text(
                    prompt,
                    max_tokens=800,
                    temperature=0.2
                )

            logger.info("LLM Response:")
            logger.info(response)
            return response

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error: {str(e)}"

    async def run_comprehensive_test(self):
        """Run comprehensive tests of all enhanced templates."""
        logger.info("Starting comprehensive prompt template tests...")

        # Test 1: Enhanced synthesis answer template
        synthesis_prompt = await self.test_synthesis_answer_template()
        
        # Test 2: Hybrid retrieval template
        hybrid_prompt = await self.test_hybrid_retrieval_template()
        
        # Test 3: Citation generation template
        citation_prompt = await self.test_citation_generation_template()
        
        # Test 4: Fact-checked template
        fact_checked_prompt = await self.test_fact_checked_template()

        # Test LLM generation with system message
        system_message = """You are an AI research assistant with expertise in providing accurate, well-sourced answers to questions. Your role is to synthesize information from provided documents and create comprehensive, factual responses.

Your primary responsibilities:
- Provide accurate, well-structured answers grounded in the provided evidence
- Cite sources for every factual claim you make using [1], [2], etc. format
- If you are unsure about any information, clearly state that you don't know
- Maintain academic rigor and avoid speculation or unsupported claims
- Structure responses logically with clear sections and flow
- If documents contain contradictory information, acknowledge the conflict and present both perspectives
- Keep responses concise but complete and include a "Sources" section at the end"""

        logger.info("\n" + "="*50)
        logger.info("TESTING LLM GENERATION WITH ENHANCED TEMPLATES")
        logger.info("="*50)

        # Test synthesis with system message
        synthesis_response = await self.test_llm_generation(synthesis_prompt, system_message)
        
        logger.info("\n" + "-"*30)
        logger.info("SYNTHESIS RESPONSE:")
        logger.info("-"*30)
        logger.info(synthesis_response)

        # Test citation processing
        citation_response = await self.test_llm_generation(citation_prompt)
        
        logger.info("\n" + "-"*30)
        logger.info("CITATION PROCESSING RESPONSE:")
        logger.info("-"*30)
        logger.info(citation_response)

        logger.info("\n" + "="*50)
        logger.info("ENHANCED PROMPT TEMPLATE TESTS COMPLETED")
        logger.info("="*50)

        return {
            "synthesis_prompt": synthesis_prompt,
            "hybrid_prompt": hybrid_prompt,
            "citation_prompt": citation_prompt,
            "fact_checked_prompt": fact_checked_prompt,
            "synthesis_response": synthesis_response,
            "citation_response": citation_response
        }


async def main():
    """Main test function."""
    logger.info("Enhanced Prompt Template Test Suite")
    logger.info("Testing improved factuality and citation capabilities")
    
    tester = EnhancedPromptTester()
    results = await tester.run_comprehensive_test()
    
    logger.info("\nTest completed successfully!")
    return results


if __name__ == "__main__":
    asyncio.run(main()) 