"""
PDF Agent Route Handler
Handles PDF processing and document analysis operations using PDFService.
"""

import logging
from shared.core.unified_logging import get_logger
import os
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File

from .base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata,
)
from ...models.requests import PDFProcessRequest
from ...models.responses import AgentResponse
from ...middleware import get_current_user
from ...di import get_pdf_service
from ...services.pdf_service import PDFService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/pdf/process")
async def pdf_process(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Process PDF documents for text extraction and analysis using PDF service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["file_path", "operation"])

        pdf_request = PDFProcessRequest(
            file_path=request.get("file_path", ""),
            operation=request.get("operation", "extract_text"),
            parameters=request.get("parameters", {}),
            context=request.get("context", {}),
        )

        # Execute PDF processing using service
        pdf_results = await pdf_service.process_pdf(
            file_path=pdf_request.file_path,
            operation=pdf_request.operation,
            parameters=pdf_request.parameters,
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="pdf_processor",
            result=pdf_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id,
                operation=pdf_request.operation,
                file_path=pdf_request.file_path,
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_processor",
            error=e,
            operation="PDF processing",
            user_id=get_user_id(current_user),
        )


@router.post("/pdf/upload")
async def pdf_upload(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Upload and process PDF file using PDF service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate file
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=422, detail="Only PDF files are supported")

        # Read file content
        file_content = await file.read()

        # Process PDF using service
        pdf_results = await pdf_service.process_pdf(
            file_content=file_content, filename=file.filename
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="pdf_upload",
            result=pdf_results,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, filename=file.filename, file_size=len(file_content)
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_upload",
            error=e,
            operation="PDF upload and processing",
            user_id=get_user_id(current_user),
        )


@router.post("/pdf/extract-text")
async def pdf_extract_text(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Extract text from PDF using PDF service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["file_path"])

        file_path = request.get("file_path", "")
        pages = request.get("pages", None)

        # Extract text using service
        text_result = await pdf_service.extract_text(file_path=file_path, pages=pages)

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="pdf_extract_text",
            result=text_result,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, file_path=file_path, pages=pages
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_extract_text",
            error=e,
            operation="Text extraction",
            user_id=get_user_id(current_user),
        )


@router.post("/pdf/extract-images")
async def pdf_extract_images(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Extract images from PDF using PDF service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["file_path"])

        file_path = request.get("file_path", "")
        pages = request.get("pages", None)
        output_dir = request.get("output_dir", "extracted_images")

        # Extract images using service
        images_result = await pdf_service.extract_images(
            file_path=file_path, pages=pages, output_dir=output_dir
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="pdf_extract_images",
            result=images_result,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, file_path=file_path, pages=pages, output_dir=output_dir
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_extract_images",
            error=e,
            operation="Image extraction",
            user_id=get_user_id(current_user),
        )


@router.post("/pdf/analyze")
async def pdf_analyze(
    request: Dict[str, Any],
    http_request: Request,
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Analyze PDF structure and content using PDF service."""
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()

    try:
        # Validate request
        AgentErrorHandler.validate_request(request, ["file_path"])

        file_path = request.get("file_path", "")
        analysis_type = request.get("analysis_type", "full")

        # Analyze PDF using service
        analysis_result = await pdf_service.analyze_pdf(
            file_path=file_path, analysis_type=analysis_type
        )

        processing_time = tracker.get_processing_time()
        user_id = get_user_id(current_user)

        return AgentResponseFormatter.format_success(
            agent_id="pdf_analyze",
            result=analysis_result,
            processing_time=processing_time,
            metadata=create_agent_metadata(
                user_id=user_id, file_path=file_path, analysis_type=analysis_type
            ),
            user_id=user_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_analyze",
            error=e,
            operation="PDF analysis",
            user_id=get_user_id(current_user),
        )


@router.get("/pdf/health")
async def pdf_health(
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Get PDF service health status."""
    try:
        health_status = await pdf_service.health_check()

        return AgentResponseFormatter.format_success(
            agent_id="pdf_health",
            result=health_status,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user), health_check=True
            ),
            user_id=get_user_id(current_user),
        )

    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_health",
            error=e,
            operation="Health check",
            user_id=get_user_id(current_user),
        )


@router.get("/pdf/status")
async def pdf_status(
    current_user=Depends(get_current_user),
    pdf_service: PDFService = Depends(get_pdf_service),
) -> AgentResponse:
    """Get PDF service detailed status."""
    try:
        status_info = await pdf_service.get_status()

        return AgentResponseFormatter.format_success(
            agent_id="pdf_status",
            result=status_info,
            processing_time=0.0,
            metadata=create_agent_metadata(
                user_id=get_user_id(current_user), status_check=True
            ),
            user_id=get_user_id(current_user),
        )

    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="pdf_status",
            error=e,
            operation="Status check",
            user_id=get_user_id(current_user),
        )
