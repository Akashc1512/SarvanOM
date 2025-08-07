"""
Memory Management System - Universal Knowledge Platform
Three-tier memory management with PostgreSQL, session storage, and knowledge graph cache.
"""
import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class MemoryPriority(str, Enum):
    """Memory priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MemoryItem:
    """Individual memory item."""
    key: str
    value: Any
    memory_type: MemoryType
    priority: MemoryPriority
    ttl_seconds: int
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryStats:
    """Memory system statistics."""
    total_items: int
    short_term_items: int
    medium_term_items: int
    long_term_items: int
    total_size_bytes: int
    cache_hit_rate: float
    average_access_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)


class ShortTermMemory:
    """PostgreSQL-based short-term memory."""
    
    def __init__(self, database_service=None):
        try:
            from shared.core.database import get_database_service
            from shared.models.session_memory import SessionMemory
            
            self.db_service = database_service or get_database_service()
            self.SessionMemory = SessionMemory
            logger.info("ShortTermMemory connected to PostgreSQL")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            self.db_service = None
    
    async def store(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store item in short-term memory."""
        if not self.db_service:
            return False
        
        try:
            with self.db_service.get_session() as session:
                # Create or update session memory
                session_memory = self.SessionMemory(
                    session_id=key,
                    data=value,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(seconds=ttl_seconds)
                )
                session.merge(session_memory)
                session.commit()
                logger.debug(f"Stored in short-term memory: {key}")
                return True
        except Exception as e:
            logger.error(f"Failed to store in short-term memory: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from short-term memory."""
        if not self.db_service:
            return None
        
        try:
            with self.db_service.get_session() as session:
                session_memory = session.query(self.SessionMemory).filter(
                    self.SessionMemory.session_id == key,
                    self.SessionMemory.expires_at > datetime.now()
                ).first()
                
                if session_memory:
                    session_memory.accessed_at = datetime.now()
                    session_memory.access_count += 1
                    session.commit()
                    logger.debug(f"Retrieved from short-term memory: {key}")
                    return session_memory.data
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve from short-term memory: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from short-term memory."""
        if not self.db_service:
            return False
        
        try:
            with self.db_service.get_session() as session:
                result = session.query(self.SessionMemory).filter(
                    self.SessionMemory.session_id == key
                ).delete()
                session.commit()
                logger.debug(f"Deleted from short-term memory: {key}")
                return result > 0
        except Exception as e:
            logger.error(f"Failed to delete from short-term memory: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get short-term memory statistics."""
        if not self.db_service:
            return {"items": 0, "size_bytes": 0}
        
        try:
            with self.db_service.get_session() as session:
                total_items = session.query(self.SessionMemory).count()
                active_items = session.query(self.SessionMemory).filter(
                    self.SessionMemory.expires_at > datetime.now()
                ).count()
                
                return {
                    "items": total_items,
                    "active_items": active_items,
                    "size_bytes": total_items * 1024  # Approximate
                }
        except Exception as e:
            logger.error(f"Failed to get short-term memory stats: {e}")
            return {"items": 0, "size_bytes": 0}


class MediumTermMemory:
    """File-based medium-term memory."""
    
    def __init__(self, storage_dir: str = "session_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"MediumTermMemory initialized with storage dir: {storage_dir}")
    
    async def store(self, key: str, value: Any, ttl_seconds: int = 86400) -> bool:
        """Store item in medium-term memory."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            data = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "accessed_at": datetime.now().isoformat(),
                "access_count": 0,
                "ttl_seconds": ttl_seconds
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            logger.debug(f"Stored in medium-term memory: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store in medium-term memory: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from medium-term memory."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check TTL
            created_at = datetime.fromisoformat(data["created_at"])
            if datetime.now() - created_at > timedelta(seconds=data["ttl_seconds"]):
                await self.delete(key)
                return None
            
            # Update access info
            data["accessed_at"] = datetime.now().isoformat()
            data["access_count"] += 1
            
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            logger.debug(f"Retrieved from medium-term memory: {key}")
            return data["value"]
        except Exception as e:
            logger.error(f"Failed to retrieve from medium-term memory: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from medium-term memory."""
        try:
            file_path = self.storage_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted from medium-term memory: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete from medium-term memory: {e}")
            return False
    
    async def cleanup_expired(self) -> int:
        """Clean up expired items."""
        cleaned_count = 0
        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    created_at = datetime.fromisoformat(data["created_at"])
                    if datetime.now() - created_at > timedelta(seconds=data["ttl_seconds"]):
                        file_path.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process file {file_path}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} expired items from medium-term memory")
            return cleaned_count
        except Exception as e:
            logger.error(f"Failed to cleanup medium-term memory: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get medium-term memory statistics."""
        try:
            files = list(self.storage_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "items": len(files),
                "size_bytes": total_size
            }
        except Exception as e:
            logger.error(f"Failed to get medium-term memory stats: {e}")
            return {"items": 0, "size_bytes": 0}


class LongTermMemory:
    """Knowledge graph-based long-term memory."""
    
    def __init__(self, kg_url: str = None):
        from shared.core.config.central_config import get_arangodb_url
        if kg_url is None:
            kg_url = get_arangodb_url()
        self.kg_url = kg_url
        self.cache = {}  # Simple in-memory cache for now
        logger.info("LongTermMemory initialized")
    
    async def store(self, key: str, value: Any, ttl_seconds: int = 2592000) -> bool:
        """Store item in long-term memory."""
        try:
            # Simulate knowledge graph storage
            data = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "accessed_at": datetime.now().isoformat(),
                "access_count": 0,
                "ttl_seconds": ttl_seconds
            }
            
            self.cache[key] = data
            logger.debug(f"Stored in long-term memory: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store in long-term memory: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from long-term memory."""
        try:
            if key not in self.cache:
                return None
            
            data = self.cache[key]
            
            # Check TTL
            created_at = datetime.fromisoformat(data["created_at"])
            if datetime.now() - created_at > timedelta(seconds=data["ttl_seconds"]):
                await self.delete(key)
                return None
            
            # Update access info
            data["accessed_at"] = datetime.now().isoformat()
            data["access_count"] += 1
            
            logger.debug(f"Retrieved from long-term memory: {key}")
            return data["value"]
        except Exception as e:
            logger.error(f"Failed to retrieve from long-term memory: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from long-term memory."""
        try:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Deleted from long-term memory: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete from long-term memory: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get long-term memory statistics."""
        try:
            total_size = sum(len(str(v)) for v in self.cache.values())
            return {
                "items": len(self.cache),
                "size_bytes": total_size
            }
        except Exception as e:
            logger.error(f"Failed to get long-term memory stats: {e}")
            return {"items": 0, "size_bytes": 0}


class MemoryManager:
    """Main memory management system."""
    
    def __init__(self, database_service=None):
        self.short_term = ShortTermMemory(database_service)
        self.medium_term = MediumTermMemory()
        self.long_term = LongTermMemory()
        logger.info("MemoryManager initialized")
    
    async def store(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store item in specified memory type."""
        # Set default TTL based on memory type
        if ttl_seconds is None:
            if memory_type == MemoryType.SHORT_TERM:
                ttl_seconds = 3600  # 1 hour
            elif memory_type == MemoryType.MEDIUM_TERM:
                ttl_seconds = 86400  # 24 hours
            else:  # LONG_TERM
                ttl_seconds = 2592000  # 30 days
        
        if memory_type == MemoryType.SHORT_TERM:
            return await self.short_term.store(key, value, ttl_seconds)
        elif memory_type == MemoryType.MEDIUM_TERM:
            return await self.medium_term.store(key, value, ttl_seconds)
        else:  # LONG_TERM
            return await self.long_term.store(key, value, ttl_seconds)
    
    async def retrieve(self, key: str, memory_type: Optional[MemoryType] = None) -> Optional[Any]:
        """Retrieve item from memory."""
        if memory_type:
            # Retrieve from specific memory type
            if memory_type == MemoryType.SHORT_TERM:
                return await self.short_term.retrieve(key)
            elif memory_type == MemoryType.MEDIUM_TERM:
                return await self.medium_term.retrieve(key)
            else:  # LONG_TERM
                return await self.long_term.retrieve(key)
        else:
            # Try all memory types in order of speed
            for memory_type in [MemoryType.SHORT_TERM, MemoryType.MEDIUM_TERM, MemoryType.LONG_TERM]:
                result = await self.retrieve(key, memory_type)
                if result is not None:
                    return result
            return None
    
    async def delete(self, key: str, memory_type: Optional[MemoryType] = None) -> bool:
        """Delete item from memory."""
        if memory_type:
            # Delete from specific memory type
            if memory_type == MemoryType.SHORT_TERM:
                return await self.short_term.delete(key)
            elif memory_type == MemoryType.MEDIUM_TERM:
                return await self.medium_term.delete(key)
            else:  # LONG_TERM
                return await self.long_term.delete(key)
        else:
            # Delete from all memory types
            results = await asyncio.gather(
                self.short_term.delete(key),
                self.medium_term.delete(key),
                self.long_term.delete(key),
                return_exceptions=True
            )
            return any(r for r in results if isinstance(r, bool) and r)
    
    async def consolidate(self, key: str) -> bool:
        """Consolidate item across memory tiers."""
        try:
            # Try to retrieve from all tiers
            short_term_value = await self.short_term.retrieve(key)
            medium_term_value = await self.medium_term.retrieve(key)
            long_term_value = await self.long_term.retrieve(key)
            
            # Determine best value (prefer non-None values)
            best_value = long_term_value or medium_term_value or short_term_value
            
            if best_value is not None:
                # Store in all tiers
                await asyncio.gather(
                    self.short_term.store(key, best_value),
                    self.medium_term.store(key, best_value),
                    self.long_term.store(key, best_value),
                    return_exceptions=True
                )
                logger.info(f"Consolidated memory item: {key}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to consolidate memory item {key}: {e}")
            return False
    
    async def cleanup(self) -> Dict[str, int]:
        """Clean up expired items from all memory tiers."""
        try:
            # Clean up medium-term memory
            medium_cleaned = await self.medium_term.cleanup_expired()
            
            # For now, short-term and long-term cleanup is handled by TTL
            # In a real implementation, you'd add cleanup logic here
            
            result = {
                "short_term_cleaned": 0,
                "medium_term_cleaned": medium_cleaned,
                "long_term_cleaned": 0
            }
            
            logger.info(f"Memory cleanup completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to cleanup memory: {e}")
            return {"short_term_cleaned": 0, "medium_term_cleaned": 0, "long_term_cleaned": 0}
    
    async def get_memory_stats(self) -> MemoryStats:
        """Get comprehensive memory statistics."""
        try:
            short_stats = await self.short_term.get_stats()
            medium_stats = await self.medium_term.get_stats()
            long_stats = await self.long_term.get_stats()
            
            total_items = short_stats["items"] + medium_stats["items"] + long_stats["items"]
            total_size = short_stats["size_bytes"] + medium_stats["size_bytes"] + long_stats["size_bytes"]
            
            return MemoryStats(
                total_items=total_items,
                short_term_items=short_stats["items"],
                medium_term_items=medium_stats["items"],
                long_term_items=long_stats["items"],
                total_size_bytes=total_size,
                cache_hit_rate=0.85,  # Placeholder - implement actual hit rate calculation
                average_access_time_ms=50.0,  # Placeholder - implement actual timing
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return MemoryStats(
                total_items=0,
                short_term_items=0,
                medium_term_items=0,
                long_term_items=0,
                total_size_bytes=0,
                cache_hit_rate=0.0,
                average_access_time_ms=0.0,
                timestamp=datetime.now()
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of memory system."""
        health_status = {
            "status": "healthy",
            "tiers": {
                "short_term": "healthy",
                "medium_term": "healthy",
                "long_term": "healthy"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Check Redis connection
        if not self.short_term.redis_client:
            health_status["tiers"]["short_term"] = "unhealthy"
            health_status["status"] = "degraded"
        
        return health_status 