"""
Code execution agent routes.
Handles code execution, syntax validation, and code analysis using CodeService.
"""

import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from ..base import (
    AgentResponseFormatter,
    AgentErrorHandler,
    AgentPerformanceTracker,
    get_user_id,
    create_agent_metadata
)
from ..models.responses import AgentResponse
from ...middleware import get_current_user
from ...di import get_code_service
from ...services.code_service import CodeService

logger = get_logger(__name__)

code_router = APIRouter(prefix="/code", tags=["code-execution"])


@code_router.post("/execute")
async def execute_code(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """
    Execute code and return results using code service.
    
    Expected request format:
    {
        "code": "print('Hello, World!')",
        "language": "python",
        "timeout": 30,
        "input_data": "optional input for the code"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["code", "language"])
        
        code = request.get("code", "")
        language = request.get("language", "python").lower()
        timeout = request.get("timeout", 30)
        inputs = request.get("input_data", {})
        
        # Execute the code using service
        result = await code_service.execute_code(
            code=code,
            language=language,
            inputs=inputs,
            timeout=timeout
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id, language=language, timeout=timeout)
        
        return AgentResponseFormatter.format_success(
            agent_id="code-executor",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-executor",
            error=e,
            operation="code execution",
            user_id=get_user_id(current_user)
        )


@code_router.post("/validate")
async def validate_code(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """
    Validate code syntax without execution using code service.
    
    Expected request format:
    {
        "code": "def hello(): print('Hello')",
        "language": "python"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["code", "language"])
        
        code = request.get("code", "")
        language = request.get("language", "python").lower()
        
        # Validate code using service
        result = await code_service.validate_syntax(
            code=code,
            language=language
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id, language=language)
        
        return AgentResponseFormatter.format_success(
            agent_id="code-validator",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-validator",
            error=e,
            operation="code validation",
            user_id=get_user_id(current_user)
        )


@code_router.post("/analyze")
async def analyze_code(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """
    Analyze code structure and complexity using code service.
    
    Expected request format:
    {
        "code": "def hello(): print('Hello')",
        "language": "python"
    }
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Validate request
        AgentErrorHandler.validate_request(request, ["code", "language"])
        
        code = request.get("code", "")
        language = request.get("language", "python").lower()
        
        # Analyze code using service
        result = await code_service.analyze_code(
            code=code,
            language=language
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(user_id, language=language)
        
        return AgentResponseFormatter.format_success(
            agent_id="code-analyzer",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-analyzer",
            error=e,
            operation="code analysis",
            user_id=get_user_id(current_user)
        )


@code_router.post("/upload")
async def upload_and_execute(
    file: UploadFile = File(...),
    language: str = "python",
    timeout: int = 30,
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """
    Upload and execute code file using code service.
    """
    tracker = AgentPerformanceTracker()
    tracker.start_tracking()
    
    try:
        user_id = get_user_id(current_user)
        
        # Read file content
        file_content = await file.read()
        
        # Execute uploaded file using service
        result = await code_service.upload_and_execute(
            file_content=file_content,
            filename=file.filename,
            language=language
        )
        
        processing_time = tracker.get_processing_time()
        metadata = create_agent_metadata(
            user_id, 
            filename=file.filename,
            language=language,
            file_size=len(file_content)
        )
        
        return AgentResponseFormatter.format_success(
            agent_id="code-upload-executor",
            result=result,
            processing_time=processing_time,
            metadata=metadata,
            user_id=user_id
        )
        
    except Exception as e:
        processing_time = tracker.get_processing_time()
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-upload-executor",
            error=e,
            operation="file upload and execution",
            user_id=get_user_id(current_user)
        )


@code_router.get("/health")
async def code_health(
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """Get code service health status."""
    try:
        health_status = await code_service.health_check()
        
        return AgentResponseFormatter.format_success(
            agent_id="code-health",
            result=health_status,
            processing_time=0.0,
            metadata=create_agent_metadata(
                get_user_id(current_user),
                health_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-health",
            error=e,
            operation="health check",
            user_id=get_user_id(current_user)
        )


@code_router.get("/status")
async def code_status(
    current_user = Depends(get_current_user),
    code_service: CodeService = Depends(get_code_service)
) -> AgentResponse:
    """Get code service detailed status."""
    try:
        status_info = await code_service.get_status()
        
        return AgentResponseFormatter.format_success(
            agent_id="code-status",
            result=status_info,
            processing_time=0.0,
            metadata=create_agent_metadata(
                get_user_id(current_user),
                status_check=True
            ),
            user_id=get_user_id(current_user)
        )
        
    except Exception as e:
        return AgentErrorHandler.handle_agent_error(
            agent_id="code-status",
            error=e,
            operation="status check",
            user_id=get_user_id(current_user)
        ) 