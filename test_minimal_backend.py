#!/usr/bin/env python3
"""
Minimal Backend Test
Tests if FastAPI and basic dependencies work correctly.
"""

from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Minimal Test API")

@app.get("/")
async def root():
    return {"message": "Hello World", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) 