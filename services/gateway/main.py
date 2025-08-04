#!/usr/bin/env python3
"""
API Gateway Main Entry Point

This module provides the main entry point for running the API Gateway service.
"""

import uvicorn
import logging
from services.gateway.gateway_app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the API Gateway."""
    logger.info("🚀 Starting Sarvanom API Gateway...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main() 