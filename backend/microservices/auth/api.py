"""
Auth Microservice API
RESTful API endpoints for the auth service.

This module provides:
- Authentication endpoints
- User management endpoints
- Token validation endpoints
- Health check endpoints
- Error handling
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .auth_service import AuthService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize service
auth_service = AuthService()

# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user: Optional[Dict[str, Any]]
    token: Optional[str]
    auth_time_ms: int
    status: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class RegisterResponse(BaseModel):
    user: Optional[Dict[str, Any]]
    status: str

class TokenValidationRequest(BaseModel):
    token: str

class TokenValidationResponse(BaseModel):
    valid: bool
    payload: Optional[Dict[str, Any]]
    error: Optional[str]

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    components: Dict[str, str]
    timestamp: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate a user."""
    try:
        logger.info(f"Processing login request for user: {request.username}")
        
        result = await auth_service.authenticate(
            username=request.username,
            password=request.password
        )
        
        return LoginResponse(**result)
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        logger.info(f"Processing registration request for user: {request.username}")
        
        # Validate password confirmation
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        user_data = {
            "username": request.username,
            "email": request.email,
            "password": request.password
        }
        
        result = await auth_service.register_user(user_data)
        
        return RegisterResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(request: TokenValidationRequest):
    """Validate a JWT token."""
    try:
        logger.info("Processing token validation request")
        
        result = await auth_service.validate_token(request.token)
        
        return TokenValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    """Get user by ID."""
    try:
        result = await auth_service.get_user(user_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the auth service."""
    try:
        health = await auth_service.health_check()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/status")
async def service_status():
    """Get detailed service status."""
    try:
        health = await auth_service.health_check()
        return {
            "service": "auth",
            "version": "2.0.0",
            "status": health.get("status", "unknown"),
            "components": health.get("components", {}),
            "endpoints": {
                "login": "/api/v1/auth/login",
                "register": "/api/v1/auth/register",
                "validate_token": "/api/v1/auth/validate-token",
                "health": "/api/v1/auth/health"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 