# Cache Manager PostgreSQL Implementation

## Overview

This implementation provides a PostgreSQL-based cache management system using JSONB fields, replacing Redis for zero-budget caching. The system caches retrieval results and LLM answers with automatic TTL management and efficient querying.

## Features

- **PostgreSQL JSONB Storage**: Efficient storage of cache data using JSONB fields
- **Automatic TTL Management**: Configurable expiration with automatic cleanup
- **Cache Key Generation**: Intelligent cache key generation with fingerprinting
- **Zero-Budget Alternative**: No Redis dependency, uses existing PostgreSQL infrastructure
- **GIN Indexes**: Optimized querying for JSONB operations
- **Comprehensive Testing**: Full test suite covering all functionality

## Architecture

### Database Schema

```sql
CREATE TABLE cache_store (
    cache_key VARCHAR(500) PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);
```

### Key Components

1. **CacheStore Model** (`shared/models/cache_store.py`)
   - SQLAlchemy model with JSONB field for cache data
   - Automatic expiration management
   - Built-in TTL validation

2. **CacheManagerPostgres Service** (`shared/core/cache_manager_postgres.py`)
   - Main service for cache operations
   - Integration with existing database infrastructure
   - Comprehensive error handling

3. **Integration Example** (`examples/cache_manager_integration.py`)
   - Demonstrates retrieval engine integration
   - Shows orchestrator integration with caching

## Implementation Details

### Core Methods

#### `set_cache(key: str, data: dict, ttl_minutes: Optional[int] = None) -> bool`

Sets cache data with expiration.

```python
# Example usage
success = await cache_manager.set_cache(
    key="retrieval:python:5",
    data={"results": [...], "total_found": 10},
    ttl_minutes=30
)
```

#### `get_cache(key: str) -> Optional[Dict[str, Any]]`

Gets cached data if not expired.

```python
# Example usage
cached_data = await cache_manager.get_cache("retrieval:python:5")
if cached_data:
    print(f"Cache hit: {cached_data['total_found']} results")
```

#### `delete_cache(key: str) -> bool`

Deletes specific cache entry.

```python
# Example usage
success = await cache_manager.delete_cache("retrieval:python:5")
```

### Cache Key Generation

The system provides intelligent cache key generation:

```python
# Generate cache key from arguments
cache_key = cache_manager.generate_cache_key("retrieval", query, max_results)

# Generate cache key with keyword arguments
cache_key = cache_manager.generate_cache_key("answer", query=query, model="gpt-4")
```

### TTL Management

- **Automatic Expiration**: Cache entries expire based on TTL
- **Configurable TTL**: Default 60 minutes, customizable per cache entry
- **Automatic Cleanup**: Expired entries are automatically skipped in `get_cache`
- **Manual Cleanup**: Available via `clear_expired_cache()` method

## Database Setup

### 1. Create the Table

Run the migration script:

```bash
psql -d your_database -f scripts/create_cache_store_table.sql
```

### 2. Verify Installation

```sql
-- Check table structure
\d cache_store

-- Check indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'cache_store';
```

## Usage Examples

### Basic Usage

```python
from shared.core.cache_manager_postgres import CacheManagerPostgres

# Initialize cache manager
cache_manager = CacheManagerPostgres()

# Set cache
await cache_manager.set_cache("my_key", {"data": "value"}, ttl_minutes=30)

# Get cache
cached_data = await cache_manager.get_cache("my_key")
if cached_data:
    print(f"Cached data: {cached_data}")
```

### Retrieval Engine Integration

```python
class HybridRetrievalEngineWithCache:
    def __init__(self):
        self.cache_manager = CacheManagerPostgres()
    
    async def retrieve(self, query: str, max_results: int = 5):
        # Generate cache key
        cache_key = self.cache_manager.generate_cache_key("retrieval", query, max_results)
        
        # Check cache first
        cached_results = await self.cache_manager.get_cache(cache_key)
        if cached_results:
            return cached_results
        
        # Perform retrieval
        results = await self._perform_retrieval(query, max_results)
        
        # Cache results
        await self.cache_manager.set_cache(cache_key, results, ttl_minutes=30)
        
        return results
```

### Orchestrator Integration

```python
class OrchestratorWithCache:
    def __init__(self):
        self.cache_manager = CacheManagerPostgres()
    
    async def process_query(self, query: str):
        # Generate cache key for answer
        cache_key = self.cache_manager.generate_cache_key("answer", query)
        
        # Check cache first
        cached_answer = await self.cache_manager.get_cache(cache_key)
        if cached_answer:
            return cached_answer
        
        # Generate answer
        answer = await self._generate_answer(query)
        
        # Cache answer
        await self.cache_manager.set_cache(cache_key, answer, ttl_minutes=120)
        
        return answer
```

## Testing

### Run Tests

```bash
# Run all tests
pytest test_cache_manager_postgres.py -v

# Run specific test
pytest test_cache_manager_postgres.py::TestCacheManagerPostgres::test_set_get_cache_flows -v
```

### Test Coverage

The test suite covers:

- ✅ Set/get cache flows
- ✅ TTL expiry handling
- ✅ Retrieval caching logic
- ✅ Answer caching logic
- ✅ Cache key generation
- ✅ Cache deletion
- ✅ Cache statistics
- ✅ Error handling and edge cases
- ✅ Concurrent cache access
- ✅ Large cache operations

## Performance Considerations

### Indexes

The implementation includes optimized indexes:

```sql
-- Primary key index
CREATE INDEX idx_cache_store_cache_key ON cache_store(cache_key);

-- Expiration index for TTL queries
CREATE INDEX idx_cache_store_expires_at ON cache_store(expires_at);

-- GIN index for JSONB operations
CREATE INDEX idx_cache_store_data_gin ON cache_store USING GIN (data);
```

### Query Optimization

- **JSONB Operations**: Efficient querying using GIN indexes
- **TTL Queries**: Optimized expiration checking
- **Connection Pooling**: Uses existing database connection pool
- **Async Operations**: Non-blocking database operations

## Monitoring and Maintenance

### Health Checks

```python
# Check cache manager health
health = await cache_manager.health_check()
print(f"Status: {health['status']}")
print(f"Total entries: {health['total_entries']}")
```

### Cache Statistics

```python
# Get cache statistics
stats = await cache_manager.get_cache_stats()
print(f"Active entries: {stats['active_entries']}")
print(f"Expired entries: {stats['expired_entries']}")
```

### Cleanup Operations

```python
# Clear expired cache entries
cleared_count = await cache_manager.clear_expired_cache()
print(f"Cleared {cleared_count} expired entries")
```

## Migration from Redis

### Benefits of PostgreSQL over Redis

1. **Zero Additional Infrastructure**: Uses existing PostgreSQL
2. **ACID Compliance**: Full transaction support
3. **Complex Queries**: SQL querying capabilities
4. **Backup Integration**: Existing backup strategies
5. **Monitoring**: Existing monitoring tools

### Migration Steps

1. **Deploy PostgreSQL-based cache manager**
2. **Update retrieval engine integration**
3. **Update orchestrator integration**
4. **Test with existing queries**
5. **Monitor performance**
6. **Remove Redis dependency**

## Configuration

### Environment Variables

```bash
# Database configuration (existing)
DATABASE_URL=postgresql://user:password@localhost:5432/database

# Cache manager configuration
CACHE_DEFAULT_TTL_MINUTES=60  # Default TTL in minutes
CACHE_MAX_ENTRIES=10000       # Maximum cache entries
```

### Database Configuration

The cache manager uses the existing database configuration:

```python
from shared.core.database import get_database_service

# Cache manager auto-initializes with existing database service
cache_manager = CacheManagerPostgres()
```

## Error Handling

### Common Error Scenarios

1. **Database Connection Issues**: Graceful fallback with logging
2. **Invalid Cache Keys**: Input validation and error reporting
3. **JSONB Serialization Errors**: Proper error handling for malformed data
4. **Concurrent Access**: Thread-safe operations

### Error Recovery

```python
try:
    await cache_manager.set_cache(key, data, ttl_minutes=30)
except Exception as e:
    logger.error(f"Cache operation failed: {e}")
    # Fallback to direct retrieval or continue without cache
```

## Security Considerations

### Data Protection

- **Input Validation**: All inputs are validated
- **SQL Injection Prevention**: Uses parameterized queries
- **Access Control**: Uses existing database permissions
- **Audit Logging**: Comprehensive logging for debugging

### Privacy

- **Cache Isolation**: Each cache entry is isolated
- **TTL Enforcement**: Automatic cleanup prevents data accumulation
- **No Cross-Cache Access**: Cache entries cannot access other entries

## Future Enhancements

### Planned Features

1. **Compression**: JSONB compression for large cache data
2. **Partitioning**: Table partitioning for high-volume deployments
3. **Replication**: Read replica support for high availability
4. **Analytics**: Cache analytics and insights
5. **Encryption**: Field-level encryption for sensitive data

### Performance Optimizations

1. **Caching Layer**: Redis caching for frequently accessed entries
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

3. **Cache Misses**
   - Check TTL configuration
   - Verify cache key generation
   - Monitor cache statistics

### Debug Commands

```python
# Enable debug logging
logging.getLogger('shared.core.cache_manager_postgres').setLevel(logging.DEBUG)

# Check database connectivity
health = await cache_manager.health_check()
print(health)

# Get all cache keys
keys = await cache_manager.get_all_cache_keys(limit=10)
print(f"Active cache keys: {len(keys)}")
```

## Conclusion

The CacheManagerPostgres implementation provides a robust, scalable solution for cache management using PostgreSQL JSONB fields. It offers zero-budget caching while maintaining all the functionality of Redis-based solutions, with the added benefits of ACID compliance and complex querying capabilities.

The implementation is production-ready with comprehensive testing, error handling, and monitoring capabilities. It integrates seamlessly with the existing retrieval engine and orchestrator architecture and provides a clear migration path from Redis-based solutions.

The system is designed to handle high-volume caching scenarios while maintaining performance and reliability, making it suitable for MAANG/OpenAI application patterns with zero-budget constraints. 