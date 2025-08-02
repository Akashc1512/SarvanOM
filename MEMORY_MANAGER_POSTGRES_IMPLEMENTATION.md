# Memory Manager PostgreSQL Implementation

## Overview

This implementation provides a PostgreSQL-based session memory management system using JSONB fields, replacing Redis for zero-budget persistence. The system maintains conversation context across multiple queries with automatic TTL-like behavior.

## Features

- **PostgreSQL JSONB Storage**: Efficient storage of conversation history using JSONB fields
- **Automatic TTL Management**: Manual cleanup of expired interactions (older than 1 day)
- **Session Context Management**: Preload and update session context for orchestrator integration
- **Zero-Budget Alternative**: No Redis dependency, uses existing PostgreSQL infrastructure
- **GIN Indexes**: Optimized querying for JSONB operations
- **Comprehensive Testing**: Full test suite covering all functionality

## Architecture

### Database Schema

```sql
CREATE TABLE session_memory (
    session_id VARCHAR(255) PRIMARY KEY,
    history JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Key Components

1. **SessionMemory Model** (`shared/models/session_memory.py`)
   - SQLAlchemy model with JSONB field for history
   - Automatic timestamp management
   - Built-in TTL-like behavior

2. **MemoryManagerPostgres Service** (`shared/core/memory_manager_postgres.py`)
   - Main service for session memory operations
   - Integration with existing database infrastructure
   - Comprehensive error handling

3. **Integration Example** (`examples/memory_manager_integration.py`)
   - Demonstrates orchestrator integration
   - Shows session context preloading and updating

## Implementation Details

### Core Methods

#### `add_to_memory(session_id: str, query: str, answer: str, timestamp: Optional[datetime] = None) -> bool`

Adds a query-answer interaction to session memory.

```python
# Example usage
success = await memory_manager.add_to_memory(
    session_id="user_123",
    query="What is Python?",
    answer="Python is a high-level programming language."
)
```

#### `get_context(session_id: str, limit: int = 5) -> List[Dict[str, Any]]`

Retrieves the last N interactions for a session, automatically pruning expired interactions.

```python
# Example usage
context = await memory_manager.get_context(session_id="user_123", limit=5)
# Returns: [{"query": "...", "answer": "...", "timestamp": "..."}, ...]
```

#### `clear_memory(session_id: str) -> bool`

Deletes the session record from the table.

```python
# Example usage
success = await memory_manager.clear_memory(session_id="user_123")
```

### TTL-like Behavior

The system implements TTL-like behavior manually:

1. **On each `get_context` call**: Removes interactions older than 1 day
2. **Automatic cleanup**: Available via `cleanup_expired_sessions()` method
3. **Configurable TTL**: Default 24 hours, customizable per session

### Orchestrator Integration

The memory manager integrates seamlessly with the orchestrator:

```python
class OrchestratorWithMemory:
    def __init__(self):
        self.memory_manager = MemoryManagerPostgres()
    
    async def process_query(self, query: str, session_id: str):
        # Step 1: Preload session context
        session_context = await self._preload_session_context(session_id)
        
        # Step 2: Process query with context
        response = await self._process_with_context(query, session_context)
        
        # Step 3: Update session memory
        await self._update_session_memory(session_id, query, response["answer"])
        
        return response
```

## Database Setup

### 1. Create the Table

Run the migration script:

```bash
psql -d your_database -f scripts/create_session_memory_table.sql
```

### 2. Verify Installation

```sql
-- Check table structure
\d session_memory

-- Check indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'session_memory';
```

## Usage Examples

### Basic Usage

```python
from shared.core.memory_manager_postgres import MemoryManagerPostgres

# Initialize memory manager
memory_manager = MemoryManagerPostgres()

# Add interactions
await memory_manager.add_to_memory("session_1", "What is AI?", "AI is artificial intelligence.")
await memory_manager.add_to_memory("session_1", "How does it work?", "AI uses machine learning algorithms.")

# Get context
context = await memory_manager.get_context("session_1", limit=5)
print(f"Retrieved {len(context)} interactions")
```

### Orchestrator Integration

```python
from examples.memory_manager_integration import OrchestratorWithMemory

# Initialize orchestrator with memory
orchestrator = OrchestratorWithMemory()

# Process queries with session memory
response1 = await orchestrator.process_query("What is Python?", "user_123")
response2 = await orchestrator.process_query("How do I install it?", "user_123")

# Get session statistics
stats = await orchestrator.get_session_stats("user_123")
print(f"Session has {stats['history_length']} interactions")
```

## Testing

### Run Tests

```bash
# Run all tests
pytest test_memory_manager_postgres.py -v

# Run specific test
pytest test_memory_manager_postgres.py::TestMemoryManagerPostgres::test_add_multiple_interactions -v
```

### Test Coverage

The test suite covers:

- ✅ Adding multiple interactions to session
- ✅ Validating retrieval order (last N exchanges)
- ✅ Testing memory clearance
- ✅ Simulating expired context pruning
- ✅ Error handling and edge cases
- ✅ Concurrent access testing
- ✅ Large session history handling

## Performance Considerations

### Indexes

The implementation includes optimized indexes:

```sql
-- Primary key index
CREATE INDEX idx_session_memory_session_id ON session_memory(session_id);

-- Timestamp index for TTL queries
CREATE INDEX idx_session_memory_updated_at ON session_memory(updated_at);

-- GIN index for JSONB operations
CREATE INDEX idx_session_memory_history_gin ON session_memory USING GIN (history);
```

### Query Optimization

- **JSONB Operations**: Efficient querying using GIN indexes
- **Batch Operations**: Support for bulk operations
- **Connection Pooling**: Uses existing database connection pool
- **Async Operations**: Non-blocking database operations

## Monitoring and Maintenance

### Health Checks

```python
# Check memory manager health
health = await memory_manager.health_check()
print(f"Status: {health['status']}")
print(f"Total sessions: {health['total_sessions']}")
```

### Cleanup Operations

```python
# Clean up expired sessions
cleaned_count = await memory_manager.cleanup_expired_sessions(max_age_hours=24)
print(f"Cleaned up {cleaned_count} expired sessions")
```

### Statistics

```python
# Get session statistics
stats = await memory_manager.get_session_stats("session_123")
print(f"History length: {stats['history_length']}")
print(f"Last updated: {stats['last_updated']}")
```

## Migration from Redis

### Benefits of PostgreSQL over Redis

1. **Zero Additional Infrastructure**: Uses existing PostgreSQL
2. **ACID Compliance**: Full transaction support
3. **Complex Queries**: SQL querying capabilities
4. **Backup Integration**: Existing backup strategies
5. **Monitoring**: Existing monitoring tools

### Migration Steps

1. **Deploy PostgreSQL-based memory manager**
2. **Update orchestrator integration**
3. **Test with existing sessions**
4. **Monitor performance**
5. **Remove Redis dependency**

## Configuration

### Environment Variables

```bash
# Database configuration (existing)
DATABASE_URL=postgresql://user:password@localhost:5432/database

# Memory manager configuration
MEMORY_TTL_HOURS=24  # Default TTL in hours
MEMORY_MAX_CONTEXT_LENGTH=50  # Maximum context length
```

### Database Configuration

The memory manager uses the existing database configuration:

```python
from shared.core.database import get_database_service

# Memory manager auto-initializes with existing database service
memory_manager = MemoryManagerPostgres()
```

## Error Handling

### Common Error Scenarios

1. **Database Connection Issues**: Graceful fallback with logging
2. **Invalid Session IDs**: Input validation and error reporting
3. **JSONB Serialization Errors**: Proper error handling for malformed data
4. **Concurrent Access**: Thread-safe operations

### Error Recovery

```python
try:
    await memory_manager.add_to_memory(session_id, query, answer)
except Exception as e:
    logger.error(f"Memory operation failed: {e}")
    # Fallback to in-memory storage or continue without context
```

## Security Considerations

### Data Protection

- **Input Validation**: All inputs are validated
- **SQL Injection Prevention**: Uses parameterized queries
- **Access Control**: Uses existing database permissions
- **Audit Logging**: Comprehensive logging for debugging

### Privacy

- **Session Isolation**: Each session is isolated
- **TTL Enforcement**: Automatic cleanup prevents data accumulation
- **No Cross-Session Access**: Sessions cannot access other sessions' data

## Future Enhancements

### Planned Features

1. **Compression**: JSONB compression for large histories
2. **Partitioning**: Table partitioning for high-volume deployments
3. **Replication**: Read replica support for high availability
4. **Analytics**: Session analytics and insights
5. **Encryption**: Field-level encryption for sensitive data

### Performance Optimizations

1. **Caching Layer**: Redis caching for frequently accessed sessions
2. **Batch Operations**: Bulk insert/update operations
3. **Connection Pooling**: Optimized connection management
4. **Query Optimization**: Advanced query optimization

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URL configuration
   - Verify database service is running
   - Check network connectivity

2. **Performance Issues**
   - Verify indexes are created
   - Check query execution plans
   - Monitor database performance

3. **Memory Leaks**
   - Run cleanup operations regularly
   - Monitor session growth
   - Check TTL enforcement

### Debug Commands

```python
# Enable debug logging
logging.getLogger('shared.core.memory_manager_postgres').setLevel(logging.DEBUG)

# Check database connectivity
health = await memory_manager.health_check()
print(health)

# Get all sessions
sessions = await memory_manager.get_all_sessions(limit=10)
print(f"Active sessions: {len(sessions)}")
```

## Conclusion

The MemoryManagerPostgres implementation provides a robust, scalable solution for session memory management using PostgreSQL JSONB fields. It offers zero-budget persistence while maintaining all the functionality of Redis-based solutions, with the added benefits of ACID compliance and complex querying capabilities.

The implementation is production-ready with comprehensive testing, error handling, and monitoring capabilities. It integrates seamlessly with the existing orchestrator architecture and provides a clear migration path from Redis-based solutions. 