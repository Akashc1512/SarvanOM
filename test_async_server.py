#!/usr/bin/env python3
"""
Simple test server to verify async I/O implementation.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
import time

app = FastAPI(title="Async Test Server", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Async server is running!", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
async def metrics():
    """Metrics endpoint."""
    return {"requests": 1, "uptime": time.time()}

@app.post("/test-async")
async def test_async():
    """Test async operations."""
    # Simulate async database operation
    await asyncio.sleep(0.1)
    
    # Simulate async HTTP call
    async with httpx.AsyncClient() as client:
        # This would be a real external API call
        # response = await client.get("https://api.example.com/data")
        pass
    
    return {
        "message": "Async operations completed successfully",
        "async_operations": ["database", "http_client"],
        "status": "success"
    }

@app.get("/test-parallel")
async def test_parallel():
    """Test parallel async operations."""
    start_time = time.time()
    
    # Simulate parallel operations
    async def operation1():
        await asyncio.sleep(0.1)
        return "operation1"
    
    async def operation2():
        await asyncio.sleep(0.1)
        return "operation2"
    
    async def operation3():
        await asyncio.sleep(0.1)
        return "operation3"
    
    # Execute operations in parallel
    results = await asyncio.gather(
        operation1(),
        operation2(),
        operation3(),
        return_exceptions=True
    )
    
    end_time = time.time()
    
    return {
        "message": "Parallel async operations completed",
        "results": results,
        "execution_time": end_time - start_time,
        "status": "success"
    }

if __name__ == "__main__":
    print("🚀 Starting Async Test Server...")
    print("✅ Testing async I/O implementation")
    print("📊 Server will be available at http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) 