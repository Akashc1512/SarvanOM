"""
Agent handlers for the API Gateway
Provides endpoints for various agent types including browser, PDF, code executor, etc.
"""

import asyncio
import json
import logging
from shared.core.unified_logging import get_logger
import base64
import io
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from fastapi import HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
import PyPDF2
import subprocess
import tempfile
import os
import re

from shared.core.agents.base_agent import BaseAgent
from shared.core.agents.retrieval_agent import RetrievalAgent
from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent
from shared.core.agents.arangodb_knowledge_graph_agent import ArangoDBKnowledgeGraphAgent

logger = get_logger(__name__)

# Pydantic models for agent requests/responses
class BrowserSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Maximum number of results")
    include_snippets: bool = Field(True, description="Include result snippets")

class BrowserSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int
    search_time: float

class PDFProcessRequest(BaseModel):
    file_data: str = Field(..., description="Base64 encoded PDF file")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    extract_text: bool = Field(True, description="Extract text content")
    extract_metadata: bool = Field(True, description="Extract metadata")
    generate_summary: bool = Field(True, description="Generate content summary")

class PDFProcessResponse(BaseModel):
    text_content: str
    metadata: Dict[str, Any]
    summary: str
    page_count: int
    filename: str
    processing_time: float

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    language: str = Field("python", description="Programming language")
    timeout_seconds: int = Field(30, description="Execution timeout")
    sandboxed: bool = Field(True, description="Run in sandboxed environment")
    capture_output: bool = Field(True, description="Capture stdout")
    capture_errors: bool = Field(True, description="Capture stderr")

class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str]
    exit_code: int
    execution_time: float
    language: str
    success: bool

class KnowledgeGraphQueryRequest(BaseModel):
    query: str = Field(..., description="Knowledge graph query")
    query_type: str = Field("entity_search", description="Type of query")
    max_entities: int = Field(10, description="Maximum entities to return")
    max_relationships: int = Field(5, description="Maximum relationships to return")
    include_metadata: bool = Field(True, description="Include entity metadata")
    include_confidence: bool = Field(True, description="Include confidence scores")

class KnowledgeGraphQueryResponse(BaseModel):
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    query: str
    query_type: str
    total_entities: int
    total_relationships: int
    execution_time: float

class DatabaseQueryRequest(BaseModel):
    query: str = Field(..., description="Database query")
    database_type: str = Field("postgres", description="Database type")
    limit: int = Field(100, description="Result limit")
    include_schema: bool = Field(False, description="Include schema information")
    timeout_seconds: int = Field(30, description="Query timeout")
    read_only: bool = Field(True, description="Read-only query")

class DatabaseQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    schema: Optional[Dict[str, Any]]
    row_count: int
    execution_time: float
    database_type: str
    query: str

class WebCrawlerRequest(BaseModel):
    url: str = Field(..., description="URL to crawl")
    depth: int = Field(1, description="Crawl depth")
    max_pages: int = Field(10, description="Maximum pages to crawl")
    extract_text: bool = Field(True, description="Extract text content")
    follow_links: bool = Field(True, description="Follow links")
    respect_robots_txt: bool = Field(True, description="Respect robots.txt")
    user_agent: str = Field("SarvanomBot/1.0", description="User agent string")

class WebCrawlerResponse(BaseModel):
    pages: List[Dict[str, Any]]
    pages_crawled: int
    total_size: int
    url: str
    crawl_time: float

class AgentHandler:
    """Base class for agent handlers"""
    
    def __init__(self):
        self.retrieval_agent = RetrievalAgent()
        self.knowledge_graph_agent = ArangoDBKnowledgeGraphAgent()
    
    async def handle_browser_search(self, request: BrowserSearchRequest) -> BrowserSearchResponse:
        """Handle web search requests"""
        start_time = datetime.now()
        
        try:
            # Use retrieval agent for web search
            search_results = await self.retrieval_agent.search_web(
                query=request.query,
                max_results=request.max_results
            )
            
            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", "") if request.include_snippets else "",
                    "relevance_score": result.get("relevance_score", 0.0)
                }
                formatted_results.append(formatted_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return BrowserSearchResponse(
                results=formatted_results,
                query=request.query,
                total_results=len(formatted_results),
                search_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Browser search error: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    async def handle_pdf_processing(self, request: PDFProcessRequest) -> PDFProcessResponse:
        """Handle PDF processing requests"""
        start_time = datetime.now()
        
        try:
            # Decode base64 file data
            file_data = base64.b64decode(request.file_data)
            file_stream = io.BytesIO(file_data)
            
            # Extract text and metadata
            text_content = ""
            metadata = {}
            page_count = 0
            
            try:
                pdf_reader = PyPDF2.PdfReader(file_stream)
                page_count = len(pdf_reader.pages)
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "producer": pdf_reader.metadata.get("/Producer", ""),
                        "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        "modification_date": pdf_reader.metadata.get("/ModDate", "")
                    }
                
            except Exception as e:
                logger.error(f"PDF processing error: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
            
            # Generate summary using LLM
            summary = ""
            if request.generate_summary and text_content:
                try:
                    # Use a simple extractive summarization for now
                    sentences = text_content.split('.')
                    summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else text_content
                except Exception as e:
                    logger.warning(f"Summary generation failed: {e}")
                    summary = "Summary generation failed"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PDFProcessResponse(
                text_content=text_content,
                metadata=metadata,
                summary=summary,
                page_count=page_count,
                filename=request.filename,
                processing_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
    
    async def handle_code_execution(self, request: CodeExecutionRequest) -> CodeExecutionResponse:
        """Handle code execution requests"""
        start_time = datetime.now()
        
        try:
            # Validate language
            supported_languages = ["python", "javascript", "bash"]
            if request.language not in supported_languages:
                raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")
            
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{request.language}', delete=False) as f:
                f.write(request.code)
                temp_file = f.name
            
            try:
                # Execute code based on language
                if request.language == "python":
                    result = subprocess.run(
                        ["python", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=request.timeout_seconds,
                        cwd=tempfile.gettempdir()
                    )
                elif request.language == "javascript":
                    result = subprocess.run(
                        ["node", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=request.timeout_seconds,
                        cwd=tempfile.gettempdir()
                    )
                elif request.language == "bash":
                    result = subprocess.run(
                        ["bash", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=request.timeout_seconds,
                        cwd=tempfile.gettempdir()
                    )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return CodeExecutionResponse(
                    output=result.stdout if request.capture_output else "",
                    error=result.stderr if request.capture_errors else "",
                    exit_code=result.returncode,
                    execution_time=execution_time,
                    language=request.language,
                    success=result.returncode == 0
                )
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Code execution timed out")
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")
    
    async def handle_knowledge_graph_query(self, request: KnowledgeGraphQueryRequest) -> KnowledgeGraphQueryResponse:
        """Handle knowledge graph queries"""
        start_time = datetime.now()
        
        try:
            # Use the refactored ArangoDB Knowledge Graph Agent
            result = await self.knowledge_graph_agent.query(
                query=request.query,
                query_type=request.query_type
            )
            
            # Convert entities to dictionary format
            entities = []
            for entity in result.entities:
                entity_dict = {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "confidence": entity.confidence,
                    "properties": entity.properties
                }
                if not request.include_metadata:
                    entity_dict.pop("properties", None)
                if not request.include_confidence:
                    entity_dict.pop("confidence", None)
                entities.append(entity_dict)
            
            # Convert relationships to dictionary format
            relationships = []
            for rel in result.relationships:
                rel_dict = {
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "relationship_type": rel.relationship_type,
                    "confidence": rel.confidence,
                    "properties": rel.properties
                }
                if not request.include_metadata:
                    rel_dict.pop("properties", None)
                if not request.include_confidence:
                    rel_dict.pop("confidence", None)
                relationships.append(rel_dict)
            
            # Limit results based on request parameters
            entities = entities[:request.max_entities]
            relationships = relationships[:request.max_relationships]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return KnowledgeGraphQueryResponse(
                entities=entities,
                relationships=relationships,
                query=request.query,
                query_type=request.query_type,
                total_entities=len(entities),
                total_relationships=len(relationships),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Knowledge graph query error: {e}")
            raise HTTPException(status_code=500, detail=f"Knowledge graph query failed: {str(e)}")
    
    async def handle_database_query(self, request: DatabaseQueryRequest) -> DatabaseQueryResponse:
        """Handle database queries"""
        start_time = datetime.now()
        
        try:
            # For now, return a mock response
            # In a real implementation, this would connect to the actual database
            mock_results = [
                {"id": 1, "name": "Example", "value": "test"},
                {"id": 2, "name": "Sample", "value": "data"}
            ]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return DatabaseQueryResponse(
                results=mock_results,
                schema={"id": "integer", "name": "text", "value": "text"} if request.include_schema else None,
                row_count=len(mock_results),
                execution_time=execution_time,
                database_type=request.database_type,
                query=request.query
            )
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    
    async def handle_web_crawler(self, request: WebCrawlerRequest) -> WebCrawlerResponse:
        """Handle web crawling requests"""
        start_time = datetime.now()
        
        try:
            # For now, return a mock response
            # In a real implementation, this would use a proper web crawler
            mock_pages = [
                {
                    "url": request.url,
                    "title": "Example Page",
                    "content": "This is example content from the crawled page.",
                    "links": []
                }
            ]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return WebCrawlerResponse(
                pages=mock_pages,
                pages_crawled=len(mock_pages),
                total_size=sum(len(page.get("content", "")) for page in mock_pages),
                url=request.url,
                crawl_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Web crawler error: {e}")
            raise HTTPException(status_code=500, detail=f"Web crawling failed: {str(e)}")

# Create global agent handler instance
agent_handler = AgentHandler() 