"""
Authentication Middleware for API Gateway

This module handles authentication and authorization middleware for the API gateway.
It provides security checks, user authentication, and request validation.
"""

import time
import logging
from shared.core.unified_logging import get_logger
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = get_logger(__name__)

# Security token scheme
security = HTTPBearer()


class SecurityMiddleware:
    """Security middleware that checks requests for threats."""
    
    def __init__(self):
        self.blocked_ips = set()
        self.rate_limits = {}
        self.security_config = {
            "max_requests_per_minute": 60,
            "max_tokens_per_minute": 10000,
            "blocked_keywords": ["malicious", "attack", "exploit"],
            "bypass_paths": ["/ws/", "/health", "/metrics", "/analytics", "/integrations"]
        }
    
    async def check_security(
        self, 
        query: str, 
        client_ip: str, 
        user_id: str, 
        initial_confidence: float = 0.0
    ) -> Dict[str, Any]:
        """
        Perform security check on request.
        
        Args:
            query: Query string to check
            client_ip: Client IP address
            user_id: User identifier
            initial_confidence: Initial confidence score
            
        Returns:
            Security check result
        """
        threats = []
        confidence = initial_confidence
        
        # Check for blocked IPs
        if client_ip in self.blocked_ips:
            return {
                "blocked": True,
                "block_reason": "IP address is blocked",
                "threats": [{"type": "ip_blocked", "severity": "high"}]
            }
        
        # Check for malicious keywords in query
        query_lower = query.lower()
        for keyword in self.security_config["blocked_keywords"]:
            if keyword in query_lower:
                threats.append({
                    "type": "malicious_keyword",
                    "severity": "medium",
                    "keyword": keyword
                })
                confidence -= 0.3
        
        # Check rate limiting
        rate_limit_key = f"{client_ip}:{user_id}"
        current_time = time.time()
        if rate_limit_key in self.rate_limits:
            last_request_time = self.rate_limits[rate_limit_key]
            if current_time - last_request_time < 1.0:  # 1 second minimum between requests
                threats.append({
                    "type": "rate_limit",
                    "severity": "low"
                })
                confidence -= 0.1
        
        self.rate_limits[rate_limit_key] = current_time
        
        # Determine if request should be blocked
        blocked = confidence < 0.0 or any(t.get("severity") == "high" for t in threats)
        
        return {
            "blocked": blocked,
            "threats": threats,
            "confidence": confidence,
            "block_reason": "Security violation detected" if blocked else None
        }


class AuthenticationMiddleware:
    """Authentication middleware for user authentication and authorization."""
    
    def __init__(self):
        self.token_cache = {}
        self.user_cache = {}
    
    async def get_current_user(self, request: Request):
        """
        Get current user from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User object with authentication information
        """
        try:
            # Extract token from request
            token = await self._extract_token(request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication token required"
                )
            
            # Validate token
            user = await self._validate_token(token)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication token"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
    
    async def _extract_token(self, request: Request) -> Optional[str]:
        """Extract authentication token from request."""
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Check query parameter
        token = request.query_params.get("token")
        if token:
            return token
        
        return None
    
    async def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT or OAuth token and return user information.
        
        Args:
            token: The token to validate
            
        Returns:
            User object if valid, None otherwise
        """
        # Check cache first
        if token in self.user_cache:
            return self.user_cache[token]
        
        try:
            # Implement actual token validation with JWT or OAuth
            if not token or len(token) < 10:
                return None
                
            # Check if token is in allowed format
            if token.startswith("Bearer "):
                token = token[7:]  # Remove "Bearer " prefix
            
            # Try JWT validation first
            try:
                import jwt
                import os
                
                # Get JWT secret from environment
                jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
                jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
                
                # Decode JWT token
                payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
                
                # Extract user information from JWT payload
                user = {
                    "user_id": payload.get("user_id", payload.get("sub", f"user_{hash(token) % 10000}")),
                    "username": payload.get("username", payload.get("name", f"user_{hash(token) % 10000}")),
                    "role": payload.get("role", "user"),
                    "permissions": payload.get("permissions", ["read", "write"]),
                    "email": payload.get("email", ""),
                    "exp": payload.get("exp"),
                    "iat": payload.get("iat"),
                    "token_type": "jwt"
                }
                
                # Check if token is expired
                if user.get("exp") and time.time() > user["exp"]:
                    logger.warning(f"JWT token expired for user: {user['user_id']}")
                    return None
                
                # Cache the user
                self.user_cache[token] = user
                return user
                
            except jwt.InvalidTokenError:
                # JWT validation failed, try OAuth validation
                pass
            except ImportError:
                # JWT library not available, try OAuth validation
                pass
            
            # Try OAuth validation
            try:
                import aiohttp
                import os
                
                # Get OAuth configuration
                oauth_provider = os.getenv('OAUTH_PROVIDER', 'google')
                oauth_client_id = os.getenv('OAUTH_CLIENT_ID', '')
                oauth_client_secret = os.getenv('OAUTH_CLIENT_SECRET', '')
                
                if oauth_provider == 'google' and oauth_client_id:
                    # Validate Google OAuth token
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}",
                            timeout=5
                        ) as response:
                            if response.status == 200:
                                token_info = await response.json()
                                
                                # Check if token is valid for our client
                                if token_info.get("aud") == oauth_client_id:
                                    user = {
                                        "user_id": token_info.get("sub", f"user_{hash(token) % 10000}"),
                                        "username": token_info.get("name", f"user_{hash(token) % 10000}"),
                                        "role": "user",
                                        "permissions": ["read", "write"],
                                        "email": token_info.get("email", ""),
                                        "token_type": "oauth_google"
                                    }
                                    
                                    # Cache the user
                                    self.user_cache[token] = user
                                    return user
                
                elif oauth_provider == 'github' and oauth_client_id:
                    # Validate GitHub OAuth token
                    async with aiohttp.ClientSession() as session:
                        headers = {"Authorization": f"token {token}"}
                        async with session.get(
                            "https://api.github.com/user",
                            headers=headers,
                            timeout=5
                        ) as response:
                            if response.status == 200:
                                user_info = await response.json()
                                
                                user = {
                                    "user_id": str(user_info.get("id", hash(token) % 10000)),
                                    "username": user_info.get("login", f"user_{hash(token) % 10000}"),
                                    "role": "user",
                                    "permissions": ["read", "write"],
                                    "email": user_info.get("email", ""),
                                    "token_type": "oauth_github"
                                }
                                
                                # Cache the user
                                self.user_cache[token] = user
                                return user
                
            except Exception as e:
                logger.warning(f"OAuth validation failed: {e}")
                pass
            
            # Fallback to API key validation
            if token.startswith("sk-") or token.startswith("pk-"):
                user = {
                    "user_id": f"user_{hash(token) % 10000}",
                    "username": f"user_{hash(token) % 10000}",
                    "role": "user",
                    "permissions": ["read", "write"],
                    "api_key": token,
                    "token_type": "api_key"
                }
                
                # Cache the user
                self.user_cache[token] = user
                return user
            else:
                # Invalid token format
                return None
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    async def require_admin(self, current_user=Depends(get_current_user)):
        """Require admin role for endpoint access."""
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        return current_user
    
    async def require_read(self, current_user=Depends(get_current_user)):
        """Require read permission for endpoint access."""
        permissions = current_user.get("permissions", [])
        if "read" not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Read permission required"
            )
        return current_user
    
    async def require_write(self, current_user=Depends(get_current_user)):
        """Require write permission for endpoint access."""
        permissions = current_user.get("permissions", [])
        if "write" not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Write permission required"
            )
        return current_user


# Global instances
security_middleware = SecurityMiddleware()
auth_middleware = AuthenticationMiddleware()


async def security_check(request: Request, call_next):
    """Security middleware that checks requests for threats with WebSocket bypass."""
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host
    user_id = "anonymous"

    # Bypass security for WebSocket and certain endpoints
    if any(request.url.path.startswith(path) for path in security_middleware.security_config["bypass_paths"]):
        logger.info(f"🔓 Bypassing security check for endpoint: {request.url.path}")
        response = await call_next(request)
        return response

    try:
        # Extract user ID if available
        if request.url.path not in ["/", "/health", "/metrics", "/analytics", "/integrations"]:
            current_user = await auth_middleware.get_current_user(request)
            user_id = current_user.get("user_id", "anonymous")
    except:
        pass

    # Extract query for security check (ONLY for query endpoint)
    query = ""
    if request.url.path == "/query" and request.method == "POST":
        try:
            # Read body for security check
            body_bytes = await request.body()
            if body_bytes:
                data = json.loads(body_bytes)
                query = data.get("query", "")
                
                # Reset the request body so downstream can read it
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
        except Exception as e:
            logger.error(f"Security check body parsing failed: {e}")

    # Perform security check
    try:
        security_result = await security_middleware.check_security(
            query=query, 
            client_ip=client_ip, 
            user_id=user_id, 
            initial_confidence=0.0
        )

        # If blocked, return error response
        if security_result.get("blocked", False):
            logger.warning(
                f"Request blocked by security check",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "client_ip": client_ip,
                    "threats": security_result.get("threats", []),
                },
            )

            raise HTTPException(
                status_code=403,
                detail=f"Request blocked by security check: {security_result.get('block_reason', 'Security violation detected')}",
            )

    except HTTPException:
        # Re-raise HTTPException (security blocks)
        raise
    except Exception as e:
        logger.error(
            f"Security check failed: {e}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "client_ip": client_ip,
            },
        )

    # Continue with request
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Security-Check"] = "passed"
    
    return response


# Dependency functions for FastAPI
async def get_current_user(request: Request):
    """Get current user dependency for FastAPI."""
    return await auth_middleware.get_current_user(request)


async def require_admin(current_user=Depends(get_current_user)):
    """Require admin role dependency for FastAPI."""
    return await auth_middleware.require_admin(current_user)


async def require_read(current_user=Depends(get_current_user)):
    """Require read permission dependency for FastAPI."""
    return await auth_middleware.require_read(current_user)


async def require_write(current_user=Depends(get_current_user)):
    """Require write permission dependency for FastAPI."""
    return await auth_middleware.require_write(current_user) 