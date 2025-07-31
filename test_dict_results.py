#!/usr/bin/env python3
"""
Test script to verify that all agents return dictionaries instead of AgentResult objects.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.base_agent import QueryContext
from shared.core.agents.retrieval_agent import RetrievalAgent
from shared.core.agents.factcheck_agent import FactCheckAgent
from shared.core.agents.synthesis_agent import SynthesisAgent
from shared.core.agents.citation_agent import CitationAgent

async def test_agent_dict_results():
    """Test that all agents return dictionaries."""
    print("🔍 Testing agent dictionary results...")
    
    # Create test context
    context = QueryContext(query="test query")
    
    # Test retrieval agent
    print("\n📄 Testing RetrievalAgent...")
    retrieval_agent = RetrievalAgent()
    retrieval_task = {"query": "test query", "search_type": "hybrid", "top_k": 5}
    retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
    print(f"  Type: {type(retrieval_result)}")
    print(f"  Is dict: {isinstance(retrieval_result, dict)}")
    print(f"  Keys: {list(retrieval_result.keys()) if isinstance(retrieval_result, dict) else 'N/A'}")
    
    # Test fact check agent
    print("\n✅ Testing FactCheckAgent...")
    factcheck_agent = FactCheckAgent()
    factcheck_task = {"documents": [{"content": "test document"}], "query": "test query"}
    factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
    print(f"  Type: {type(factcheck_result)}")
    print(f"  Is dict: {isinstance(factcheck_result, dict)}")
    print(f"  Keys: {list(factcheck_result.keys()) if isinstance(factcheck_result, dict) else 'N/A'}")
    
    # Test synthesis agent
    print("\n🧠 Testing SynthesisAgent...")
    synthesis_agent = SynthesisAgent()
    synthesis_task = {"verified_facts": [{"claim": "test fact"}], "query": "test query"}
    synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
    print(f"  Type: {type(synthesis_result)}")
    print(f"  Is dict: {isinstance(synthesis_result, dict)}")
    print(f"  Keys: {list(synthesis_result.keys()) if isinstance(synthesis_result, dict) else 'N/A'}")
    
    # Test citation agent
    print("\n📚 Testing CitationAgent...")
    citation_agent = CitationAgent()
    citation_task = {"content": "test content", "sources": [{"title": "test source"}]}
    citation_result = await citation_agent.process_task(citation_task, context)
    print(f"  Type: {type(citation_result)}")
    print(f"  Is dict: {isinstance(citation_result, dict)}")
    print(f"  Keys: {list(citation_result.keys()) if isinstance(citation_result, dict) else 'N/A'}")
    
    print("\n✅ All agents tested!")

if __name__ == "__main__":
    asyncio.run(test_agent_dict_results()) 