#!/usr/bin/env python3
"""
Simple server startup script for SarvanOM
"""

import uvicorn
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the SarvanOM API server"""
    print("🚀 Starting SarvanOM API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health/basic")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "services.api_gateway.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 