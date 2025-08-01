#!/usr/bin/env python3
"""
Simple server runner for SarvanOM
Bypasses the problematic startup code in main.py
"""

import uvicorn
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
        # Import the app without running the server startup code
        from services.api_gateway.main import app
        
        # Start the server
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False  # Disable reload to avoid issues
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 