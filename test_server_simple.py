#!/usr/bin/env python3
"""
Simple test server for SarvanOM
"""

import uvicorn
from fastapi import FastAPI
from datetime import datetime

# Create a simple FastAPI app
app = FastAPI(title="SarvanOM Test Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "SarvanOM Test Server is running!", "timestamp": datetime.now().isoformat()}

@app.get("/health/basic")
async def health_check():
    return {
        "status": "healthy",
        "message": "Test server is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/test")
async def test_endpoint():
    return {"test": "success", "message": "Test endpoint working!"}

if __name__ == "__main__":
    print("🚀 Starting SarvanOM Test Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health/basic")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info") 