-- Session Memory Table Migration
-- Universal Knowledge Platform
-- 
-- This script creates the session_memory table for PostgreSQL-based
-- session memory management using JSONB fields.
--
-- Features:
-- - JSONB storage for flexible session data
-- - GIN indexes for efficient querying
-- - Automatic timestamp management
-- - TTL-like behavior support
--
-- Authors:
--     - Universal Knowledge Platform Engineering Team
--
-- Version:
--     1.0.0 (2024-12-28)

-- Create session_memory table
CREATE TABLE IF NOT EXISTS session_memory (
    session_id VARCHAR(255) PRIMARY KEY,
    history JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_session_memory_session_id ON session_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_session_memory_updated_at ON session_memory(updated_at);
CREATE INDEX IF NOT EXISTS idx_session_memory_history_gin ON session_memory USING GIN (history);

-- Add table comment
COMMENT ON TABLE session_memory IS 'Session memory storage with JSONB history';

-- Add column comments
COMMENT ON COLUMN session_memory.session_id IS 'Unique session identifier';
COMMENT ON COLUMN session_memory.history IS 'Conversation history as JSONB array';
COMMENT ON COLUMN session_memory.updated_at IS 'Last update timestamp for TTL management';

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_session_memory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_update_session_memory_updated_at ON session_memory;
CREATE TRIGGER trigger_update_session_memory_updated_at
    BEFORE UPDATE ON session_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_session_memory_updated_at();

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions(max_age_hours INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM session_memory 
    WHERE updated_at < NOW() - INTERVAL '1 hour' * max_age_hours;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get session statistics
CREATE OR REPLACE FUNCTION get_session_stats()
RETURNS TABLE(
    total_sessions BIGINT,
    recent_sessions BIGINT,
    avg_history_length NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_sessions,
        COUNT(*) FILTER (WHERE updated_at >= NOW() - INTERVAL '1 hour')::BIGINT as recent_sessions,
        AVG(jsonb_array_length(history))::NUMERIC as avg_history_length
    FROM session_memory;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON session_memory TO your_app_user;
-- GRANT USAGE ON SCHEMA public TO your_app_user;

-- Verify table creation
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'session_memory'
ORDER BY ordinal_position;

-- Show indexes
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'session_memory'; 