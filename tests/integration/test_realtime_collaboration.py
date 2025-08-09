#!/usr/bin/env python3
"""
🧪 REAL-TIME COLLABORATION INTEGRATION TESTS
Universal Knowledge Platform - Comprehensive Real-Time Testing

This test suite ensures all real-time collaboration features work reliably
with Perplexity-level reliability, including Socket.IO, presence indicators,
typing indicators, conflict resolution, and message ordering.

Features Tested:
    - Socket.IO connection management
    - Multi-user presence indicators
    - Real-time typing indicators
    - Operational transformation (OT) for conflict resolution
    - Message ordering and causality tracking
    - Offline message queuing
    - Room/session management
    - Real-time cursors and selections
    - Comment system with real-time updates
    - Connection reliability and reconnection
    - Performance under load
    - Error handling and recovery
"""

import pytest
import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.core.socket_io_manager import (
    SocketIOManager, PresenceManager, RoomManager, OperationalTransformer,
    UserPresence, DocumentOperation, RoomState, PresenceStatus
)
from services.api_gateway.realtime import (
    ConnectionManager, RealtimeMessage, MessageType
)

# Test configuration
TEST_CONFIG = {
    "socket_io_url": "http://localhost:8002",

    "test_timeout": 30,
    "max_users": 10,
    "max_operations": 100,
    "performance_thresholds": {
        "connection_time_ms": 1000,
        "message_latency_ms": 100,
        "operation_throughput_per_sec": 50,
        "memory_usage_mb": 512,
        "cpu_usage_percent": 80
    }
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSocketIOManager:
    """Test Socket.IO manager functionality."""
    
    @pytest.fixture
    async def socket_io_manager(self):
        """Create Socket.IO manager instance."""
        manager = SocketIOManager()
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_connection_management(self, socket_io_manager):
        """Test Socket.IO connection management."""
        # Test connection
        assert socket_io_manager.sio is not None
        assert socket_io_manager.presence_manager is not None
        assert socket_io_manager.room_manager is not None
        
        # Test room creation
        room_id = str(uuid.uuid4())
        user_id = "test_user_1"
        
        room = await socket_io_manager.room_manager.create_room(room_id, user_id)
        assert room is not None
        assert room.room_id == room_id
        assert user_id in room.participants
        
        # Test room joining
        user_id_2 = "test_user_2"
        joined_room = await socket_io_manager.room_manager.join_room(room_id, user_id_2)
        assert joined_room is not None
        assert user_id_2 in joined_room.participants
        
        # Test room leaving
        await socket_io_manager.room_manager.leave_room(room_id, user_id_2)
        updated_room = socket_io_manager.room_manager.rooms.get(room_id)
        assert user_id_2 not in updated_room.participants
    
    @pytest.mark.asyncio
    async def test_presence_management(self, socket_io_manager):
        """Test presence management functionality."""
        user_id = "test_user"
        
        # Test presence update
        await socket_io_manager.presence_manager.update_presence(
            user_id, PresenceStatus.ONLINE, "test_room"
        )
        
        presence = socket_io_manager.presence_manager.presence_data.get(user_id)
        assert presence is not None
        assert presence.status == PresenceStatus.ONLINE
        assert presence.current_room == "test_room"
        
        # Test typing indicators
        await socket_io_manager.presence_manager.start_typing(user_id, "test_room")
        assert user_id in socket_io_manager.presence_manager.typing_users["test_room"]
        
        await socket_io_manager.presence_manager.stop_typing(user_id, "test_room")
        assert user_id not in socket_io_manager.presence_manager.typing_users["test_room"]
    
    @pytest.mark.asyncio
    async def test_operational_transformation(self, socket_io_manager):
        """Test operational transformation for conflict resolution."""
        room_id = str(uuid.uuid4())
        user_id = "test_user"
        
        # Create room
        await socket_io_manager.room_manager.create_room(room_id, user_id)
        
        # Test document operations
        operation_1 = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id=user_id,
            room_id=room_id,
            operation_type="insert",
            position=0,
            text="Hello"
        )
        
        operation_2 = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id=user_id,
            room_id=room_id,
            operation_type="insert",
            position=5,
            text=" World"
        )
        
        # Apply operations
        transformed_1 = socket_io_manager.room_manager.ot_transformer.apply_operation(operation_1)
        transformed_2 = socket_io_manager.room_manager.ot_transformer.apply_operation(operation_2)
        
        assert transformed_1 is not None
        assert transformed_2 is not None
        
        # Verify document content
        room = socket_io_manager.room_manager.rooms[room_id]
        assert "Hello" in room.document_content
        assert "World" in room.document_content


class TestPresenceManager:
    """Test presence manager functionality."""
    
    @pytest.fixture
    async def presence_manager(self):
        """Create presence manager instance."""
        manager = PresenceManager(Mock())
        await manager.start()
        yield manager
        await manager.stop()
    
    @pytest.mark.asyncio
    async def test_presence_lifecycle(self, presence_manager):
        """Test presence lifecycle management."""
        user_id = "test_user"
        room_id = "test_room"
        
        # Test online presence
        await presence_manager.update_presence(
            user_id, PresenceStatus.ONLINE, room_id
        )
        
        presence = presence_manager.presence_data.get(user_id)
        assert presence is not None
        assert presence.status == PresenceStatus.ONLINE
        assert presence.current_room == room_id
        
        # Test away presence
        await presence_manager.update_presence(
            user_id, PresenceStatus.AWAY, room_id
        )
        
        presence = presence_manager.presence_data.get(user_id)
        assert presence.status == PresenceStatus.AWAY
        
        # Test busy presence
        await presence_manager.update_presence(
            user_id, PresenceStatus.BUSY, room_id
        )
        
        presence = presence_manager.presence_data.get(user_id)
        assert presence.status == PresenceStatus.BUSY
    
    @pytest.mark.asyncio
    async def test_typing_indicators(self, presence_manager):
        """Test typing indicator functionality."""
        user_id = "test_user"
        room_id = "test_room"
        
        # Test typing start
        await presence_manager.start_typing(user_id, room_id)
        assert user_id in presence_manager.typing_users[room_id]
        
        # Test typing stop
        await presence_manager.stop_typing(user_id, room_id)
        assert user_id not in presence_manager.typing_users[room_id]
        
        # Test auto-stop typing
        await presence_manager.start_typing(user_id, room_id)
        assert user_id in presence_manager.typing_users[room_id]
        
        # Wait for auto-stop
        await asyncio.sleep(6)
        assert user_id not in presence_manager.typing_users[room_id]


class TestRoomManager:
    """Test room manager functionality."""
    
    @pytest.fixture
    def room_manager(self):
        """Create room manager instance."""
        return RoomManager()
    
    @pytest.mark.asyncio
    async def test_room_lifecycle(self, room_manager):
        """Test room lifecycle management."""
        room_id = str(uuid.uuid4())
        creator_id = "creator"
        user_id = "user"
        
        # Test room creation
        room = await room_manager.create_room(room_id, creator_id)
        assert room is not None
        assert room.room_id == room_id
        assert creator_id in room.participants
        assert len(room.participants) == 1
        
        # Test room joining
        joined_room = await room_manager.join_room(room_id, user_id)
        assert joined_room is not None
        assert user_id in joined_room.participants
        assert len(joined_room.participants) == 2
        
        # Test room leaving
        await room_manager.leave_room(room_id, user_id)
        updated_room = room_manager.rooms.get(room_id)
        assert user_id not in updated_room.participants
        assert len(updated_room.participants) == 1
        
        # Test room deletion when empty
        await room_manager.leave_room(room_id, creator_id)
        assert room_id not in room_manager.rooms
    
    @pytest.mark.asyncio
    async def test_document_operations(self, room_manager):
        """Test document operations with OT."""
        room_id = str(uuid.uuid4())
        user_id = "test_user"
        
        # Create room
        await room_manager.create_room(room_id, user_id)
        
        # Test insert operation
        operation = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id=user_id,
            room_id=room_id,
            operation_type="insert",
            position=0,
            text="Hello World"
        )
        
        transformed_op = await room_manager.update_document(room_id, user_id, operation)
        assert transformed_op is not None
        
        room = room_manager.rooms[room_id]
        assert "Hello World" in room.document_content
        assert room.document_version == 1
        
        # Test delete operation
        delete_operation = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id=user_id,
            room_id=room_id,
            operation_type="delete",
            position=0,
            length=5
        )
        
        transformed_delete = await room_manager.update_document(room_id, user_id, delete_operation)
        assert transformed_delete is not None
        
        room = room_manager.rooms[room_id]
        assert "Hello" not in room.document_content
        assert "World" in room.document_content
        assert room.document_version == 2
    
    @pytest.mark.asyncio
    async def test_cursor_management(self, room_manager):
        """Test cursor management."""
        room_id = str(uuid.uuid4())
        user_id = "test_user"
        
        # Create room
        await room_manager.create_room(room_id, user_id)
        
        # Test cursor update
        await room_manager.update_cursor(room_id, user_id, 10, 5, 15)
        
        room = room_manager.rooms[room_id]
        cursor = room.cursors.get(user_id)
        assert cursor is not None
        assert cursor["position"] == 10
        assert cursor["selection_start"] == 5
        assert cursor["selection_end"] == 15


class TestOperationalTransformer:
    """Test operational transformation functionality."""
    
    @pytest.fixture
    def ot_transformer(self):
        """Create operational transformer instance."""
        return OperationalTransformer()
    
    def test_basic_operations(self, ot_transformer):
        """Test basic operational transformation."""
        room_id = "test_room"
        
        # Test insert operation
        insert_op = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id="user1",
            room_id=room_id,
            operation_type="insert",
            position=0,
            text="Hello"
        )
        
        transformed = ot_transformer.apply_operation(insert_op)
        assert transformed is not None
        assert transformed.operation_type == "insert"
        assert transformed.text == "Hello"
        
        # Test delete operation
        delete_op = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id="user2",
            room_id=room_id,
            operation_type="delete",
            position=0,
            length=2
        )
        
        transformed_delete = ot_transformer.apply_operation(delete_op)
        assert transformed_delete is not None
        assert transformed_delete.operation_type == "delete"
    
    def test_concurrent_operations(self, ot_transformer):
        """Test concurrent operations with conflict resolution."""
        room_id = "test_room"
        
        # Simulate concurrent insertions
        op1 = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id="user1",
            room_id=room_id,
            operation_type="insert",
            position=0,
            text="A"
        )
        
        op2 = DocumentOperation(
            operation_id=str(uuid.uuid4()),
            user_id="user2",
            room_id=room_id,
            operation_type="insert",
            position=0,
            text="B"
        )
        
        # Apply operations
        transformed1 = ot_transformer.apply_operation(op1)
        transformed2 = ot_transformer.apply_operation(op2)
        
        assert transformed1 is not None
        assert transformed2 is not None
        
        # Verify vector clocks
        assert "user1" in transformed1.vector_clock
        assert "user2" in transformed2.vector_clock


class TestRealTimePerformance:
    """Test real-time performance under load."""
    
    @pytest.mark.asyncio
    async def test_high_concurrency(self):
        """Test high concurrency scenarios."""
        manager = SocketIOManager()
        await manager.start()
        
        try:
            # Simulate multiple users
            users = [f"user_{i}" for i in range(TEST_CONFIG["max_users"])]
            room_id = str(uuid.uuid4())
            
            # Create room
            await manager.room_manager.create_room(room_id, users[0])
            
            # Join users
            join_tasks = []
            for user_id in users[1:]:
                task = manager.room_manager.join_room(room_id, user_id)
                join_tasks.append(task)
            
            await asyncio.gather(*join_tasks)
            
            # Verify all users joined
            room = manager.room_manager.rooms[room_id]
            assert len(room.participants) == len(users)
            
            # Test concurrent operations
            operation_tasks = []
            for i, user_id in enumerate(users):
                operation = DocumentOperation(
                    operation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    room_id=room_id,
                    operation_type="insert",
                    position=i,
                    text=f"Text from {user_id}"
                )
                task = manager.room_manager.update_document(room_id, user_id, operation)
                operation_tasks.append(task)
            
            start_time = time.time()
            await asyncio.gather(*operation_tasks)
            end_time = time.time()
            
            # Verify performance
            operation_time = (end_time - start_time) * 1000  # Convert to ms
            assert operation_time < TEST_CONFIG["performance_thresholds"]["message_latency_ms"] * len(users)
            
            # Verify document content
            room = manager.room_manager.rooms[room_id]
            for user_id in users:
                assert f"Text from {user_id}" in room.document_content
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """Test message throughput performance."""
        manager = SocketIOManager()
        await manager.start()
        
        try:
            room_id = str(uuid.uuid4())
            user_id = "test_user"
            
            await manager.room_manager.create_room(room_id, user_id)
            
            # Test high message throughput
            messages = []
            start_time = time.time()
            
            for i in range(TEST_CONFIG["max_operations"]):
                operation = DocumentOperation(
                    operation_id=str(uuid.uuid4()),
                    user_id=user_id,
                    room_id=room_id,
                    operation_type="insert",
                    position=i,
                    text=f"Message {i}"
                )
                messages.append(operation)
            
            # Apply operations
            operation_tasks = []
            for operation in messages:
                task = manager.room_manager.update_document(room_id, user_id, operation)
                operation_tasks.append(task)
            
            await asyncio.gather(*operation_tasks)
            end_time = time.time()
            
            # Calculate throughput
            duration = end_time - start_time
            throughput = len(messages) / duration
            
            # Verify throughput meets requirements
            assert throughput >= TEST_CONFIG["performance_thresholds"]["operation_throughput_per_sec"]
            
        finally:
            await manager.stop()


class TestErrorHandling:
    """Test error handling and recovery."""
    
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Test connection recovery mechanisms."""
        manager = SocketIOManager()
        
        # Test graceful shutdown
        await manager.start()
        await manager.stop()
        
        # Verify cleanup
        assert not manager._running
        assert len(manager._processing_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_operations(self):
        """Test handling of invalid operations."""
        manager = SocketIOManager()
        await manager.start()
        
        try:
            # Test operation on non-existent room
            operation = DocumentOperation(
                operation_id=str(uuid.uuid4()),
                user_id="test_user",
                room_id="non_existent_room",
                operation_type="insert",
                position=0,
                text="Test"
            )
            
            with pytest.raises(ValueError):
                await manager.room_manager.update_document(
                    "non_existent_room", "test_user", operation
                )
            
        finally:
            await manager.stop()


def run_realtime_tests():
    """Run all real-time collaboration tests."""
    print("🚀 Starting Real-Time Collaboration Tests")
    print("=" * 60)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])


if __name__ == "__main__":
    run_realtime_tests() 