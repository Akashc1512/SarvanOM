#!/usr/bin/env python3
"""
Debug WebSocket Gateway
Debug utility for WebSocket gateway.

# DEAD CODE - Candidate for deletion: This test script is not integrated into any test suite
"""

import os
import json
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple connection manager
class SimpleConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Connect a new WebSocket client."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a WebSocket client."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: dict) -> bool:
        """Send message to specific connection."""
        if connection_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            return False

# Global connection manager
connection_manager = SimpleConnectionManager()

# FastAPI app
app = FastAPI(title="Debug WebSocket Gateway", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Debug WebSocket Gateway",
        "version": "1.0.0",
        "status": "running",
        "active_connections": len(connection_manager.active_connections)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(connection_manager.active_connections)
    }

@app.websocket("/ws/collaboration")
async def websocket_collaboration(websocket: WebSocket):
    """WebSocket endpoint for real-time collaboration."""
    connection_id = None
    
    try:
        # Connect to manager
        connection_id = await connection_manager.connect(websocket)
        
        logger.info(f"WebSocket collaboration connected: {connection_id}")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                logger.info(f"Received message: {data}")
                
                # Handle different message types
                message_type = data.get("type")
                
                if message_type == "join_session":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")
                    
                    response = {
                        "type": "session_joined",
                        "session_id": session_id,
                        "user_id": user_id,
                    }
                    
                    logger.info(f"Sending response: {response}")
                    await websocket.send_json(response)
                    
                elif message_type == "update_document":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")
                    changes = data.get("changes", [])
                    
                    response = {
                        "type": "document_updated",
                        "session_id": session_id,
                        "user_id": user_id,
                        "changes": changes,
                    }
                    
                    logger.info(f"Sending response: {response}")
                    await websocket.send_json(response)
                    
                elif message_type == "cursor_update":
                    session_id = data.get("session_id")
                    user_id = data.get("user_id", "anonymous")
                    position = data.get("position", 0)
                    
                    response = {
                        "type": "cursor_updated",
                        "session_id": session_id,
                        "user_id": user_id,
                        "position": position,
                    }
                    
                    logger.info(f"Sending response: {response}")
                    await websocket.send_json(response)
                    
                else:
                    response = {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                    
                    logger.info(f"Sending error response: {response}")
                    await websocket.send_json(response)
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket collaboration disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket collaboration error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if connection_id:
                await connection_manager.disconnect(connection_id)
            
    except Exception as e:
        logger.error(f"WebSocket collaboration setup error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close(code=1011, reason="Internal error")

@app.websocket("/ws/query-updates")
async def websocket_query_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time query status updates."""
    connection_id = None
    
    try:
        # Connect to manager
        connection_id = await connection_manager.connect(websocket)
        
        logger.info(f"WebSocket query updates connected: {connection_id}")
        
        try:
            while True:
                # Receive subscription request
                data = await websocket.receive_json()
                logger.info(f"Received message: {data}")
                
                if data.get("type") == "subscribe":
                    query_id = data.get("query_id")
                    
                    if query_id:
                        # Subscribe to query updates
                        response = {
                            "type": "subscribed",
                            "query_id": query_id
                        }
                        
                        logger.info(f"Sending response: {response}")
                        await websocket.send_json(response)
                        
                        # Send mock query data
                        mock_response = {
                            "type": "query_update",
                            "query_id": query_id,
                            "status": "completed",
                            "progress": 100,
                            "answer": "This is a mock answer for testing.",
                            "confidence": 0.8,
                        }
                        
                        logger.info(f"Sending mock query data: {mock_response}")
                        await websocket.send_json(mock_response)
                    else:
                        response = {
                            "type": "error",
                            "message": "query_id is required"
                        }
                        
                        logger.info(f"Sending error response: {response}")
                        await websocket.send_json(response)
                        
                else:
                    response = {
                        "type": "error",
                        "message": "Invalid message type"
                    }
                    
                    logger.info(f"Sending error response: {response}")
                    await websocket.send_json(response)
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket query updates disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket query updates error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if connection_id:
                await connection_manager.disconnect(connection_id)
            
    except Exception as e:
        logger.error(f"WebSocket query updates setup error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close(code=1011, reason="Internal error")

if __name__ == "__main__":
    print("Starting Debug WebSocket Gateway...")
    print("Available endpoints:")
    print("  GET  / - Root endpoint")
    print("  GET  /health - Health check")
    print("  WS   /ws/collaboration - WebSocket collaboration")
    print("  WS   /ws/query-updates - WebSocket query updates")
    print("\nStarting server on http://localhost:8003")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info") 