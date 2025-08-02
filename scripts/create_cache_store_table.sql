-- Cache Store Table Migration
-- Universal Knowledge Platform
-- 
-- This script creates the cache_store table for PostgreSQL-based
-- cache management using JSONB fields.
--
-- Features:
-- - JSONB storage for flexible cache data
-- - GIN indexes for efficient querying
-- - Automatic expiration management
-- - TTL-based cache invalidation
--
-- Authors:
--     - Universal Knowledge Platform Engineering Team
--
-- Version:
--     1.0.0 (2024-12-28)

-- Create cache_store table
CREATE TABLE IF NOT EXISTS cache_store (
    cache_key VARCHAR(500) PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cache_store_cache_key ON cache_store(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_store_expires_at ON cache_store(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_store_data_gin ON cache_store USING GIN (data);

-- Add table comment
COMMENT ON TABLE cache_store IS 'Cache storage with JSONB data and TTL';

-- Add column comments
COMMENT ON COLUMN cache_store.cache_key IS 'Unique cache key identifier';
COMMENT ON COLUMN cache_store.data IS 'Cache data as JSONB';
COMMENT ON COLUMN cache_store.created_at IS 'Cache creation timestamp';
COMMENT ON COLUMN cache_store.expires_at IS 'Cache expiration timestamp';

-- Create function to automatically update created_at timestamp
CREATE OR REPLACE FUNCTION update_cache_store_created_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update created_at
DROP TRIGGER IF EXISTS trigger_update_cache_store_created_at ON cache_store;
CREATE TRIGGER trigger_update_cache_store_created_at
    BEFORE INSERT ON cache_store
    FOR EACH ROW
    EXECUTE FUNCTION update_cache_store_created_at();

-- Create function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM cache_store 
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get cache statistics
CREATE OR REPLACE FUNCTION get_cache_stats()
RETURNS TABLE(
    total_entries BIGINT,
    active_entries BIGINT,
    expired_entries BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_entries,
        COUNT(*) FILTER (WHERE expires_at IS NULL OR expires_at >= NOW())::BIGINT as active_entries,
        COUNT(*) FILTER (WHERE expires_at IS NOT NULL AND expires_at < NOW())::BIGINT as expired_entries
    FROM cache_store;
END;
$$ LANGUAGE plpgsql;

-- Create function to get cache entry with expiration check
CREATE OR REPLACE FUNCTION get_cache_entry(p_key VARCHAR)
RETURNS TABLE(
    cache_key VARCHAR,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_expired BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cs.cache_key,
        cs.data,
        cs.created_at,
        cs.expires_at,
        (cs.expires_at IS NOT NULL AND cs.expires_at < NOW()) as is_expired
    FROM cache_store cs
    WHERE cs.cache_key = p_key;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON cache_store TO your_app_user;
-- GRANT USAGE ON SCHEMA public TO your_app_user;

-- Verify table creation
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'cache_store'
ORDER BY ordinal_position;

-- Show indexes
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'cache_store'; 