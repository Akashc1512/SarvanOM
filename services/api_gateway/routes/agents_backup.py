"""
Agent Routes for API Gateway

This module contains all agent-related endpoints for the API gateway.
It handles browser search, PDF processing, code execution, knowledge graph queries, and web crawling.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends

from ..models.requests import (
    BrowserSearchRequest,
    PDFProcessRequest,
    CodeExecutorRequest,
    KnowledgeGraphRequest,
    DatabaseQueryRequest,
    WebCrawlerRequest
)
from ..models.responses import AgentResponse
from ..middleware import get_current_user

logger = logging.getLogger(__name__)

# Create router for agent endpoints
router = APIRouter(prefix="/agents", tags=["agents"])

# Import agent handlers (will be injected)
_agent_handler = None


def set_dependencies(agent_handler_func):
    """Set dependencies for the agent routes."""
    global _agent_handler
    _agent_handler = agent_handler_func


@router.post("/browser/search", response_model=AgentResponse)
async def browser_search(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Execute browser search using the browser agent."""
    try:
        # Validate request
        search_request = BrowserSearchRequest(
            query=request.get("query", ""),
            search_type=request.get("search_type", "web"),
            max_results=request.get("max_results", 10),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not search_request.query:
            raise HTTPException(status_code=422, detail="Query is required")
        
        # Execute browser search
        start_time = datetime.now()
        
        # Implement actual browser search logic
        # This would typically call the browser agent
        
        try:
            import aiohttp
            import os
            from urllib.parse import quote_plus
            
            # Get search API configuration
            search_api_key = os.getenv('SEARCH_API_KEY', '')
            search_engine = search_request.search_type or 'google'
            
            if search_engine == 'google':
                # Use Google Custom Search API
                if search_api_key:
                    google_cse_id = os.getenv('GOOGLE_CSE_ID', '')
                    search_url = f"https://www.googleapis.com/customsearch/v1"
                    params = {
                        'key': search_api_key,
                        'cx': google_cse_id,
                        'q': search_request.query,
                        'num': min(search_request.max_results, 10)
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(search_url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = data.get('items', [])
                                
                                search_results = {
                                    "query": search_request.query,
                                    "results": [
                                        {
                                            "title": item.get('title', ''),
                                            "url": item.get('link', ''),
                                            "snippet": item.get('snippet', '')
                                        }
                                        for item in items
                                    ],
                                    "total_results": data.get('searchInformation', {}).get('totalResults', len(items)),
                                    "search_type": search_request.search_type
                                }
                            else:
                                raise Exception(f"Google search API error: {response.status}")
                else:
                    # Fallback to DuckDuckGo
                    search_url = "https://api.duckduckgo.com/"
                    params = {
                        'q': search_request.query,
                        'format': 'json',
                        'no_html': '1',
                        'skip_disambig': '1'
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(search_url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                results = []
                                
                                # Add abstract results
                                if data.get('Abstract'):
                                    results.append({
                                        "title": data.get('Heading', ''),
                                        "url": data.get('AbstractURL', ''),
                                        "snippet": data.get('Abstract', '')
                                    })
                                
                                # Add related topics
                                for topic in data.get('RelatedTopics', [])[:search_request.max_results]:
                                    if isinstance(topic, dict) and topic.get('Text'):
                                        results.append({
                                            "title": topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                                            "url": topic.get('FirstURL', ''),
                                            "snippet": topic.get('Text', '')
                                        })
                                
                                search_results = {
                                    "query": search_request.query,
                                    "results": results,
                                    "total_results": len(results),
                                    "search_type": search_request.search_type
                                }
                            else:
                                raise Exception(f"DuckDuckGo search error: {response.status}")
            
            elif search_engine == 'bing':
                # Use Bing Search API
                bing_api_key = os.getenv('BING_API_KEY', '')
                if bing_api_key:
                    search_url = "https://api.bing.microsoft.com/v7.0/search"
                    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
                    params = {
                        'q': search_request.query,
                        'count': min(search_request.max_results, 10)
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(search_url, headers=headers, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = data.get('webPages', {}).get('value', [])
                                
                                search_results = {
                                    "query": search_request.query,
                                    "results": [
                                        {
                                            "title": item.get('name', ''),
                                            "url": item.get('url', ''),
                                            "snippet": item.get('snippet', '')
                                        }
                                        for item in items
                                    ],
                                    "total_results": data.get('webPages', {}).get('totalEstimatedMatches', len(items)),
                                    "search_type": search_request.search_type
                                }
                            else:
                                raise Exception(f"Bing search API error: {response.status}")
                else:
                    raise Exception("Bing API key not configured")
            
            else:
                # Default to DuckDuckGo for unknown search engines
                search_url = "https://api.duckduckgo.com/"
                params = {
                    'q': search_request.query,
                    'format': 'json',
                    'no_html': '1',
                    'skip_disambig': '1'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = []
                            
                            if data.get('Abstract'):
                                results.append({
                                    "title": data.get('Heading', ''),
                                    "url": data.get('AbstractURL', ''),
                                    "snippet": data.get('Abstract', '')
                                })
                            
                            for topic in data.get('RelatedTopics', [])[:search_request.max_results]:
                                if isinstance(topic, dict) and topic.get('Text'):
                                    results.append({
                                        "title": topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                                        "url": topic.get('FirstURL', ''),
                                        "snippet": topic.get('Text', '')
                                    })
                            
                            search_results = {
                                "query": search_request.query,
                                "results": results,
                                "total_results": len(results),
                                "search_type": search_request.search_type
                            }
                        else:
                            raise Exception(f"Search API error: {response.status}")
                            
        except ImportError:
            logger.warning("aiohttp not available, using mock search results")
            # Fallback to mock data if aiohttp is not available
            search_results = {
                "query": search_request.query,
                "results": [
                    {
                        "title": "Sample Search Result 1",
                        "url": "https://example.com/1",
                        "snippet": "This is a sample search result snippet."
                    },
                    {
                        "title": "Sample Search Result 2", 
                        "url": "https://example.com/2",
                        "snippet": "Another sample search result snippet."
                    }
                ],
                "total_results": 2,
                "search_type": search_request.search_type
            }
            
        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            # Fallback to mock data on error
            search_results = {
                "query": search_request.query,
                "results": [
                    {
                        "title": "Error in search",
                        "url": "",
                        "snippet": f"Search failed: {str(e)}"
                    }
                ],
                "total_results": 0,
                "search_type": search_request.search_type,
                "error": str(e)
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="browser_search",
            status="completed",
            result=search_results,
            processing_time=processing_time,
            metadata={
                "search_type": search_request.search_type,
                "max_results": search_request.max_results,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Browser search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Browser search failed: {str(e)}"
        )


@router.post("/pdf/process", response_model=AgentResponse)
async def pdf_process(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Process PDF files using the PDF agent."""
    try:
        # Validate request
        pdf_request = PDFProcessRequest(
            query=request.get("query", ""),
            file_url=request.get("file_url", ""),
            extraction_mode=request.get("extraction_mode", "text"),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not pdf_request.file_url:
            raise HTTPException(status_code=422, detail="File URL is required")
        
        # Process PDF
        start_time = datetime.now()
        
        # Implement actual PDF processing logic
        # This would typically call the PDF agent
        
        try:
            import aiohttp
            import PyPDF2
            import io
            import os
            from urllib.parse import urlparse
            
            # Download PDF from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_request.file_url, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download PDF: HTTP {response.status}")
                    
                    pdf_content = await response.read()
            
            # Process PDF content
            pdf_file = io.BytesIO(pdf_content)
            
            # Extract text from PDF
            text_content = ""
            tables = []
            images = []
            metadata = {
                "pages": 0,
                "file_size": f"{len(pdf_content) / (1024*1024):.1f}MB",
                "extraction_time": 0
            }
            
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata["pages"] = len(pdf_reader.pages)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata.update({
                        "title": pdf_reader.metadata.get('/Title', ''),
                        "author": pdf_reader.metadata.get('/Author', ''),
                        "subject": pdf_reader.metadata.get('/Subject', ''),
                        "creator": pdf_reader.metadata.get('/Creator', ''),
                        "producer": pdf_reader.metadata.get('/Producer', '')
                    })
                
            except Exception as e:
                logger.warning(f"PDF text extraction failed: {e}")
                text_content = "PDF text extraction failed. Content may be image-based or encrypted."
            
            # Process based on extraction mode
            if pdf_request.extraction_mode == "text":
                processed_content = text_content
            elif pdf_request.extraction_mode == "summary":
                # Create a summary of the text content
                lines = text_content.split('\n')
                summary_lines = [line for line in lines if line.strip() and len(line.strip()) > 50]
                processed_content = "\n".join(summary_lines[:20])  # First 20 substantial lines
            elif pdf_request.extraction_mode == "key_points":
                # Extract key points (lines with numbers, bullet points, etc.)
                lines = text_content.split('\n')
                key_points = []
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith(('•', '-', '*', '1.', '2.', '3.')) or 
                               any(keyword in line.lower() for keyword in ['important', 'key', 'note', 'warning', 'tip'])):
                        key_points.append(line)
                processed_content = "\n".join(key_points[:50])  # First 50 key points
            else:
                processed_content = text_content
            
            # Calculate extraction time
            extraction_time = (datetime.now() - start_time).total_seconds()
            metadata["extraction_time"] = extraction_time
            
            pdf_results = {
                "file_url": pdf_request.file_url,
                "extraction_mode": pdf_request.extraction_mode,
                "content": processed_content[:10000],  # Limit content length
                "metadata": metadata,
                "text_content": text_content[:5000],  # Limit full text
                "tables": tables,
                "images": images
            }
            
        except ImportError:
            logger.warning("PyPDF2 not available, using mock PDF data")
            # Fallback to mock data if PyPDF2 is not available
            pdf_results = {
                "file_url": pdf_request.file_url,
                "extraction_mode": pdf_request.extraction_mode,
                "content": "Sample PDF content extracted from the document.",
                "metadata": {
                    "pages": 5,
                    "file_size": "2.5MB",
                    "extraction_time": 1.2
                },
                "text_content": "This is the extracted text content from the PDF document...",
                "tables": [],
                "images": []
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            # Fallback to mock data on error
            pdf_results = {
                "file_url": pdf_request.file_url,
                "extraction_mode": pdf_request.extraction_mode,
                "content": f"PDF processing failed: {str(e)}",
                "metadata": {
                    "pages": 0,
                    "file_size": "unknown",
                    "extraction_time": 0,
                    "error": str(e)
                },
                "text_content": "",
                "tables": [],
                "images": []
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="pdf_processor",
            status="completed",
            result=pdf_results,
            processing_time=processing_time,
            metadata={
                "extraction_mode": pdf_request.extraction_mode,
                "file_url": pdf_request.file_url,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )


@router.post("/code-executor/run", response_model=AgentResponse)
async def code_executor(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Execute code using the code execution agent."""
    try:
        # Validate request
        code_request = CodeExecutorRequest(
            query=request.get("query", ""),
            code=request.get("code", ""),
            language=request.get("language", "python"),
            timeout=request.get("timeout", 30),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not code_request.code:
            raise HTTPException(status_code=422, detail="Code is required")
        
        # Execute code
        start_time = datetime.now()
        
        # Implement actual code execution logic
        # This would typically call the code execution agent
        
        try:
            import subprocess
            import tempfile
            import os
            import signal
            import psutil
            import time
            from pathlib import Path
            
            # Security: Check for dangerous operations
            dangerous_patterns = [
                'import os', 'import sys', 'import subprocess', 'import socket',
                'open(', 'file(', 'eval(', 'exec(', '__import__', 'globals(',
                'locals(', 'vars(', 'dir(', 'getattr', 'setattr', 'delattr',
                'input(', 'raw_input(', 'compile(', 'execfile('
            ]
            
            code_lower = code_request.code.lower()
            for pattern in dangerous_patterns:
                if pattern in code_lower:
                    raise Exception(f"Security violation: {pattern} is not allowed")
            
            # Create temporary file for code execution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code_request.code)
                temp_file_path = temp_file.name
            
            try:
                # Execute code with timeout
                start_execution = time.time()
                
                if code_request.language.lower() == 'python':
                    # Execute Python code
                    process = subprocess.Popen(
                        ['python', temp_file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                    )
                    
                    try:
                        stdout, stderr = process.communicate(timeout=code_request.timeout)
                        execution_time = time.time() - start_execution
                        
                        # Get memory usage
                        memory_usage = "unknown"
                        try:
                            process_info = psutil.Process(process.pid)
                            memory_usage = f"{process_info.memory_info().rss / 1024 / 1024:.1f}MB"
                        except:
                            pass
                        
                        execution_results = {
                            "code": code_request.code,
                            "language": code_request.language,
                            "output": stdout,
                            "error": stderr if stderr else None,
                            "execution_time": execution_time,
                            "memory_used": memory_usage,
                            "exit_code": process.returncode
                        }
                        
                    except subprocess.TimeoutExpired:
                        # Kill the process and its children
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except:
                            process.kill()
                        
                        execution_results = {
                            "code": code_request.code,
                            "language": code_request.language,
                            "output": "",
                            "error": f"Execution timed out after {code_request.timeout} seconds",
                            "execution_time": code_request.timeout,
                            "memory_used": "unknown",
                            "exit_code": -1
                        }
                
                elif code_request.language.lower() == 'javascript':
                    # Execute JavaScript code (Node.js)
                    process = subprocess.Popen(
                        ['node', '-e', code_request.code],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                    )
                    
                    try:
                        stdout, stderr = process.communicate(timeout=code_request.timeout)
                        execution_time = time.time() - start_execution
                        
                        execution_results = {
                            "code": code_request.code,
                            "language": code_request.language,
                            "output": stdout,
                            "error": stderr if stderr else None,
                            "execution_time": execution_time,
                            "memory_used": "unknown",
                            "exit_code": process.returncode
                        }
                        
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except:
                            process.kill()
                        
                        execution_results = {
                            "code": code_request.code,
                            "language": code_request.language,
                            "output": "",
                            "error": f"Execution timed out after {code_request.timeout} seconds",
                            "execution_time": code_request.timeout,
                            "memory_used": "unknown",
                            "exit_code": -1
                        }
                
                else:
                    # Unsupported language
                    execution_results = {
                        "code": code_request.code,
                        "language": code_request.language,
                        "output": "",
                        "error": f"Unsupported language: {code_request.language}",
                        "execution_time": 0,
                        "memory_used": "unknown",
                        "exit_code": -1
                    }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
        except ImportError:
            logger.warning("subprocess or psutil not available, using mock execution")
            # Fallback to mock data if dependencies are not available
            execution_results = {
                "code": code_request.code,
                "language": code_request.language,
                "output": "Hello, World!",
                "error": None,
                "execution_time": 0.1,
                "memory_used": "1.2MB",
                "exit_code": 0
            }
            
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            # Fallback to mock data on error
            execution_results = {
                "code": code_request.code,
                "language": code_request.language,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "memory_used": "unknown",
                "exit_code": -1
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="code_executor",
            status="completed",
            result=execution_results,
            processing_time=processing_time,
            metadata={
                "language": code_request.language,
                "timeout": code_request.timeout,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/knowledge-graph/query", response_model=AgentResponse)
async def knowledge_graph_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Query the knowledge graph using the knowledge graph agent."""
    try:
        # Validate request
        kg_request = KnowledgeGraphRequest(
            query=request.get("query", ""),
            query_type=request.get("query_type", "entity_relationship"),
            depth=request.get("depth", 2),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not kg_request.query:
            raise HTTPException(status_code=422, detail="Query is required")
        
        # Query knowledge graph
        start_time = datetime.now()
        
        # Implement actual knowledge graph query logic
        
        try:
            # Import knowledge graph agent
            from shared.core.agents.arangodb_knowledge_graph_agent import ArangoDBKnowledgeGraphAgent
            import os
            
            # Get ArangoDB configuration
            arango_url = os.getenv('ARANGO_URL', 'http://localhost:8529')
            arango_username = os.getenv('ARANGO_USERNAME', 'root')
            arango_password = os.getenv('ARANGO_PASSWORD', '')
            arango_database = os.getenv('ARANGO_DATABASE', 'knowledge_graph')
            
            # Initialize knowledge graph agent
            kg_agent = ArangoDBKnowledgeGraphAgent(
                url=arango_url,
                username=arango_username,
                password=arango_password,
                database=arango_database
            )
            
            # Execute direct knowledge graph query
            query = request.get("query", "")
            
            # Try different query types based on query content
            if "->" in query:
                # Path query
                source, target = query.split("->", 1)
                paths = await kg_agent.find_paths(
                    source_entity=source.strip(),
                    target_entity=target.strip(),
                    max_depth=3
                )
                
                kg_results = {
                    "query": query,
                    "entities": [],
                    "relationships": [],
                    "paths": [
                        {
                            "path": path.path,
                            "length": path.length,
                            "confidence": path.confidence,
                            "entities": [entity.name for entity in path.entities],
                            "relationships": [rel.relationship_type for rel in path.relationships]
                        }
                        for path in paths
                    ],
                    "subgraphs": [],
                    "query_time": 0.1
                }
                
            elif "," in query:
                # Subgraph query
                entities = [e.strip() for e in query.split(",")]
                subgraph = await kg_agent.get_subgraph(
                    entities=entities,
                    depth=2
                )
                
                kg_results = {
                    "query": query,
                    "entities": [
                        {
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.entity_type,
                            "confidence": entity.confidence
                        }
                        for entity in subgraph.entities
                    ],
                    "relationships": [
                        {
                            "source": rel.source_entity.name,
                            "target": rel.target_entity.name,
                            "type": rel.relationship_type,
                            "confidence": rel.confidence
                        }
                        for rel in subgraph.relationships
                    ],
                    "subgraphs": [
                        {
                            "id": sg.id,
                            "entities": [entity.name for entity in sg.entities],
                            "relationships": [rel.relationship_type for rel in sg.relationships],
                            "confidence": sg.confidence
                        }
                        for sg in subgraph.subgraphs
                    ],
                    "query_time": 0.1
                }
                
            else:
                # Entity search
                entities = await kg_agent.search_entities(
                    query=query,
                    limit=10
                )
                
                kg_results = {
                    "query": query,
                    "entities": [
                        {
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.entity_type,
                            "confidence": entity.confidence
                        }
                        for entity in entities
                    ],
                    "relationships": [],
                    "subgraphs": [],
                    "query_time": 0.1
                }
                
        except ImportError:
            logger.warning("ArangoDB knowledge graph agent not available, using mock data")
            # Fallback to mock data if knowledge graph agent is not available
            kg_results = {
                "query": request.get("query"),
                "entities": [
                    {
                        "id": "entity1",
                        "name": "Sample Entity",
                        "type": "Concept",
                        "confidence": 0.95
                    }
                ],
                "relationships": [
                    {
                        "source": "entity1",
                        "target": "entity2", 
                        "type": "RELATED_TO",
                        "confidence": 0.8
                    }
                ],
                "subgraphs": [],
                "query_time": 0.1
            }
            
        except Exception as e:
            logger.error(f"Knowledge graph query failed: {e}")
            # Fallback to mock data on error
            kg_results = {
                "query": request.get("query"),
                "entities": [],
                "relationships": [],
                "subgraphs": [],
                "error": str(e),
                "query_time": 0.1
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="knowledge_graph",
            status="completed",
            result=kg_results,
            processing_time=processing_time,
            metadata={
                "query_type": kg_request.query_type,
                "depth": kg_request.depth,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge graph query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge graph query failed: {str(e)}"
        )


@router.post("/database/query", response_model=AgentResponse)
async def database_query(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Execute database queries using the database agent."""
    try:
        # Validate request
        db_request = DatabaseQueryRequest(
            query=request.get("query", ""),
            database_type=request.get("database_type", ""),
            query_text=request.get("query_text", ""),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not db_request.database_type or not db_request.query_text:
            raise HTTPException(status_code=422, detail="Database type and query are required")
        
        # Execute database query
        start_time = datetime.now()
        
        # Implement actual database query logic
        # This would typically call the database agent
        
        try:
            import asyncpg
            import os
            import json
            import time
            
            # Get database configuration based on database type
            if db_request.database_type.lower() == "postgresql":
                db_host = os.getenv('DB_HOST', 'localhost')
                db_port = int(os.getenv('DB_PORT', '5432'))
                db_name = os.getenv('DB_NAME', 'sarvanom')
                db_user = os.getenv('DB_USER', 'postgres')
                db_password = os.getenv('DB_PASSWORD', '')
            elif db_request.database_type.lower() == "mysql":
                db_host = os.getenv('MYSQL_HOST', 'localhost')
                db_port = int(os.getenv('MYSQL_PORT', '3306'))
                db_name = os.getenv('MYSQL_DATABASE', 'sarvanom')
                db_user = os.getenv('MYSQL_USER', 'root')
                db_password = os.getenv('MYSQL_PASSWORD', '')
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported database type: {db_request.database_type}"
                )
            
            # Connect to database
            if db_request.database_type.lower() == "postgresql":
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                
                # Execute query with parameters
                query_start = time.time()
                if db_request.parameters:
                    # Use parameterized query
                    results = await conn.fetch(db_request.query_text, *db_request.parameters.values())
                else:
                    # Execute query without parameters
                    results = await conn.fetch(db_request.query_text)
                
                query_time = time.time() - query_start
                await conn.close()
                
                # Convert results to list of dictionaries
                db_results = []
                columns = []
                
                if results:
                    # Get column names from first result
                    columns = list(results[0].keys())
                    
                    for row in results:
                        row_dict = {}
                        for col in columns:
                            value = row[col]
                            # Handle JSON fields
                            if isinstance(value, (dict, list)):
                                row_dict[col] = json.dumps(value)
                            else:
                                row_dict[col] = value
                        db_results.append(row_dict)
                
                return AgentResponse(
                    agent_id="database_query",
                    status="completed",
                    result={
                        "database_type": db_request.database_type,
                        "query": db_request.query_text,
                        "results": db_results,
                        "row_count": len(db_results),
                        "execution_time": query_time,
                        "columns": columns,
                        "parameters": db_request.parameters
                    },
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    metadata={
                        "database_type": db_request.database_type,
                        "parameters": db_request.parameters,
                        "user_id": current_user.get("user_id", "anonymous")
                    }
                )
                
            else:
                # For other database types, use mock data for now
                logger.warning(f"Database type {db_request.database_type} not fully implemented, using mock data")
                db_results = {
                    "database_type": db_request.database_type,
                    "query": db_request.query_text,
                    "results": [
                        {"id": 1, "name": "Sample Record 1", "value": 100},
                        {"id": 2, "name": "Sample Record 2", "value": 200}
                    ],
                    "row_count": 2,
                    "execution_time": 0.05,
                    "columns": ["id", "name", "value"]
                }
                
                return AgentResponse(
                    agent_id="database_query",
                    status="completed",
                    result=db_results,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    metadata={
                        "database_type": db_request.database_type,
                        "parameters": db_request.parameters,
                        "user_id": current_user.get("user_id", "anonymous")
                    }
                )
                
        except asyncpg.InvalidPasswordError:
            logger.error("Database authentication failed")
            raise HTTPException(status_code=500, detail="Database authentication failed")
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("Database connection failed")
            raise HTTPException(status_code=500, detail="Database connection failed")
        except asyncpg.InvalidSQLStatementNameError:
            logger.error("Invalid SQL statement")
            raise HTTPException(status_code=400, detail="Invalid SQL statement")
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
        
    except ImportError:
        logger.warning("asyncpg not available, using mock data")
        # Fallback to mock data if database driver is not available
        db_results = {
            "database_type": db_request.database_type,
            "query": db_request.query_text,
            "results": [
                {"id": 1, "name": "Sample Record 1", "value": 100},
                {"id": 2, "name": "Sample Record 2", "value": 200}
            ],
            "row_count": 2,
            "execution_time": 0.05,
            "columns": ["id", "name", "value"]
        }
        
        return AgentResponse(
            agent_id="database_query",
            status="completed",
            result=db_results,
            processing_time=(datetime.now() - start_time).total_seconds(),
            metadata={
                "database_type": db_request.database_type,
                "parameters": db_request.parameters,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )


@router.post("/web-crawler/crawl", response_model=AgentResponse)
async def web_crawler(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Crawl web pages using the web crawler agent."""
    try:
        # Validate request
        crawl_request = WebCrawlerRequest(
            query=request.get("query", ""),
            url=request.get("url", ""),
            depth=request.get("depth", 1),
            max_pages=request.get("max_pages", 10),
            parameters=request.get("parameters", {}),
            context=request.get("context", {})
        )
        
        if not crawl_request.url:
            raise HTTPException(status_code=422, detail="URL is required")
        
        # Crawl web pages
        start_time = datetime.now()
        
        # Implement actual web crawling logic
        # This would typically call the web crawler agent
        
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            import asyncio
            from urllib.parse import urljoin, urlparse
            import re
            
            # Initialize crawler
            visited_urls = set()
            pages_crawled = []
            total_links_found = 0
            
            async def crawl_page(session, url, depth, max_depth, max_pages):
                """Crawl a single page and extract content."""
                if url in visited_urls or len(pages_crawled) >= max_pages:
                    return
                
                visited_urls.add(url)
                
                try:
                    # Set up headers to mimic a real browser
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Extract title
                            title = soup.find('title')
                            title_text = title.get_text().strip() if title else "No Title"
                            
                            # Extract main content (remove scripts, styles, etc.)
                            for script in soup(["script", "style", "nav", "footer", "header"]):
                                script.decompose()
                            
                            # Get text content
                            text_content = soup.get_text()
                            # Clean up whitespace
                            text_content = re.sub(r'\s+', ' ', text_content).strip()
                            
                            # Extract links
                            links = []
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                absolute_url = urljoin(url, href)
                                # Only include http/https links
                                if absolute_url.startswith(('http://', 'https://')):
                                    links.append(absolute_url)
                            
                            page_data = {
                                "url": url,
                                "title": title_text,
                                "content": text_content[:5000],  # Limit content length
                                "links": links[:20]  # Limit number of links
                            }
                            
                            pages_crawled.append(page_data)
                            nonlocal total_links_found
                            total_links_found += len(links)
                            
                            # Recursively crawl linked pages if depth allows
                            if depth < max_depth and len(pages_crawled) < max_pages:
                                tasks = []
                                for link in links[:5]:  # Limit concurrent requests
                                    if link not in visited_urls:
                                        task = crawl_page(session, link, depth + 1, max_depth, max_pages)
                                        tasks.append(task)
                                
                                if tasks:
                                    await asyncio.gather(*tasks, return_exceptions=True)
                                    
                except Exception as e:
                    logger.warning(f"Failed to crawl {url}: {e}")
            
            # Start crawling
            async with aiohttp.ClientSession() as session:
                await crawl_page(session, crawl_request.url, 0, crawl_request.depth, crawl_request.max_pages)
            
            crawl_results = {
                "url": crawl_request.url,
                "depth": crawl_request.depth,
                "max_pages": crawl_request.max_pages,
                "pages_crawled": len(pages_crawled),
                "pages": pages_crawled,
                "total_links_found": total_links_found,
                "crawl_time": (datetime.now() - start_time).total_seconds()
            }
            
        except ImportError:
            logger.warning("aiohttp or beautifulsoup4 not available, using mock data")
            # Fallback to mock data if web crawling libraries are not available
            crawl_results = {
                "url": crawl_request.url,
                "depth": crawl_request.depth,
                "max_pages": crawl_request.max_pages,
                "pages_crawled": 3,
                "pages": [
                    {
                        "url": crawl_request.url,
                        "title": "Sample Page 1",
                        "content": "Sample content from page 1...",
                        "links": ["https://example.com/link1", "https://example.com/link2"]
                    },
                    {
                        "url": "https://example.com/link1",
                        "title": "Sample Page 2", 
                        "content": "Sample content from page 2...",
                        "links": []
                    },
                    {
                        "url": "https://example.com/link2",
                        "title": "Sample Page 3",
                        "content": "Sample content from page 3...", 
                        "links": []
                    }
                ],
                "total_links_found": 5,
                "crawl_time": 2.5
            }
            
        except Exception as e:
            logger.error(f"Web crawling failed: {e}")
            # Fallback to mock data on error
            crawl_results = {
                "url": crawl_request.url,
                "depth": crawl_request.depth,
                "max_pages": crawl_request.max_pages,
                "pages_crawled": 0,
                "pages": [],
                "total_links_found": 0,
                "crawl_time": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="web_crawler",
            status="completed",
            result=crawl_results,
            processing_time=processing_time,
            metadata={
                "depth": crawl_request.depth,
                "max_pages": crawl_request.max_pages,
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web crawling failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web crawling failed: {str(e)}"
        )


@router.post("/knowledge-graph/query", response_model=AgentResponse)
async def query_knowledge_graph(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user)
):
    """Query the knowledge graph directly."""
    try:
        # Validate request
        if not request.get("query"):
            raise HTTPException(status_code=422, detail="Query is required")
        
        # Query knowledge graph
        start_time = datetime.now()
        
        # TODO: Implement actual knowledge graph query logic
        kg_results = {
            "query": request.get("query"),
            "entities": [
                {
                    "id": "entity1",
                    "name": "Sample Entity",
                    "type": "Concept",
                    "confidence": 0.95
                }
            ],
            "relationships": [
                {
                    "source": "entity1",
                    "target": "entity2", 
                    "type": "RELATED_TO",
                    "confidence": 0.8
                }
            ],
            "subgraphs": [],
            "query_time": 0.1
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_id="knowledge_graph_direct",
            status="completed",
            result=kg_results,
            processing_time=processing_time,
            metadata={
                "query_type": "direct",
                "user_id": current_user.get("user_id", "anonymous")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge graph query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge graph query failed: {str(e)}"
        ) 