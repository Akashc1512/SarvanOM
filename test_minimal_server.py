#!/usr/bin/env python3
"""
Minimal test server for backend testing.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Set environment variables for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

# Create FastAPI app
app = FastAPI(
    title="SarvanOM Test Server",
    description="Minimal test server for backend testing",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SarvanOM Test Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "sarvanom-test-server"
    }

@app.get("/health/basic")
async def basic_health():
    """Basic health check."""
    return {"status": "ok"}

@app.get("/docs")
async def docs():
    """API documentation."""
    return {"message": "API documentation available at /docs"}

@app.post("/query")
async def test_query():
    """Test query endpoint."""
    return {
        "query_id": "test-123",
        "status": "processing",
        "message": "Test query received"
    }

if __name__ == "__main__":
    print("🚀 Starting SarvanOM Test Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    ) 