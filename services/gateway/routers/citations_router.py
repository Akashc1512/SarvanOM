#!/usr/bin/env python3
"""
Citations Router - Phase C2 Implementation

This router exposes the citations service endpoints:
- /citations/process: Process text and add inline citations
- /citations/export: Export citations in various formats
- /citations/analyze: Analyze text for claim extraction
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from shared.core.services.citations_service import get_citations_service, Bibliography

router = APIRouter(prefix="/citations", tags=["citations"])

class ProcessTextRequest(BaseModel):
    """Request model for processing text with citations."""
    text: str
    sources: List[dict]  # List of source dictionaries

class ProcessTextResponse(BaseModel):
    """Response model for processed text with citations."""
    annotated_text: str
    bibliography: dict
    claims_count: int
    citations_count: int
    disagreements_count: int
    processing_time_ms: float

class ExportRequest(BaseModel):
    """Request model for exporting citations."""
    bibliography: dict
    format: str = "markdown"  # "markdown" or "bibtex"

class AnalyzeTextRequest(BaseModel):
    """Request model for analyzing text without processing."""
    text: str

class AnalyzeTextResponse(BaseModel):
    """Response model for text analysis."""
    claims_found: int
    claims: List[dict]
    estimated_citations_needed: int

@router.post("/process", response_model=ProcessTextResponse)
async def process_text_with_citations(request: ProcessTextRequest):
    """
    Process text and add inline citations.
    
    Args:
        request: Text and sources to process
        
    Returns:
        Annotated text with citations and bibliography
    """
    try:
        start_time = datetime.now()
        
        citations_service = get_citations_service()
        
        # Process text with citations
        annotated_text, bibliography = await citations_service.process_text_with_citations(
            text=request.text,
            sources=request.sources
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Convert bibliography to dict for response
        bibliography_dict = {
            "citations": [c.to_dict() for c in bibliography.citations],
            "total_sources": bibliography.total_sources,
            "high_confidence_sources": bibliography.high_confidence_sources,
            "disagreement_count": bibliography.disagreement_count
        }
        
        return ProcessTextResponse(
            annotated_text=annotated_text,
            bibliography=bibliography_dict,
            claims_count=len([c for c in bibliography.citations if c.claim_text]),
            citations_count=len(bibliography.citations),
            disagreements_count=bibliography.disagreement_count,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation processing failed: {str(e)}")

@router.post("/export")
async def export_citations(request: ExportRequest):
    """
    Export citations in various formats.
    
    Args:
        request: Bibliography and export format
        
    Returns:
        Exported citations in requested format
    """
    try:
        citations_service = get_citations_service()
        
        # Reconstruct bibliography from dict
        bibliography = Bibliography()
        for citation_dict in request.bibliography.get("citations", []):
            # This is a simplified reconstruction - in production you'd want proper validation
            bibliography.add_citation(None)  # Placeholder
        
        # Export in requested format
        exported = citations_service.export_citations(bibliography, request.format)
        
        return {
            "format": request.format,
            "content": exported,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/analyze", response_model=AnalyzeTextResponse)
async def analyze_text_for_claims(request: AnalyzeTextRequest):
    """
    Analyze text to identify claims that need citation.
    
    Args:
        request: Text to analyze
        
    Returns:
        Analysis of claims found in text
    """
    try:
        citations_service = get_citations_service()
        
        # Extract claims without processing
        claims = citations_service.claim_extractor.extract_claims(request.text)
        
        # Convert claims to response format
        claims_data = []
        for claim in claims:
            claims_data.append({
                "text": claim.text,
                "start_pos": claim.start_pos,
                "end_pos": claim.end_pos,
                "confidence": claim.confidence
            })
        
        return AnalyzeTextResponse(
            claims_found=len(claims),
            claims=claims_data,
            estimated_citations_needed=len(claims)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check for the citations service.
    
    Returns:
        Health status and basic metrics
    """
    try:
        citations_service = get_citations_service()
        
        # Test basic functionality
        test_text = "This is a test claim that needs citation."
        test_sources = [{
            "url": "https://example.com/test",
            "title": "Test Source",
            "snippet": "Test snippet for testing purposes",
            "provider": "TestProvider"
        }]
        
        # Process test text
        annotated_text, bibliography = await citations_service.process_text_with_citations(
            text=test_text,
            sources=test_sources
        )
        
        return {
            "status": "healthy",
            "service": "Citations Service",
            "test_processed": True,
            "test_citations": len(bibliography.citations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Citations Service",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/formats")
async def get_supported_formats():
    """
    Get supported export formats.
    
    Returns:
        List of supported export formats
    """
    return {
        "supported_formats": [
            {
                "format": "markdown",
                "description": "Markdown format with links and metadata",
                "extension": ".md"
            },
            {
                "format": "bibtex",
                "description": "BibTeX format for academic papers",
                "extension": ".bib"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }
