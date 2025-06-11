-- =============================================================================
-- Enhanced AI Agent Assistant - Database Initialization Script
-- =============================================================================
-- This script creates the necessary tables and indexes for the AI Agent system
-- with proper security, performance optimizations, and data integrity.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =============================================================================
-- Agent Tasks Management Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agent_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,

    -- Constraints
    CONSTRAINT chk_agent_tasks_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_agent_tasks_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT chk_agent_tasks_execution_time CHECK (execution_time_ms >= 0)
);

-- =============================================================================
-- Agent Performance Metrics Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- =============================================================================
-- System Events and Logging Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS system_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    source VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_system_events_severity CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'))
);

-- =============================================================================
-- User Sessions Management Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT chk_user_sessions_expires_at CHECK (expires_at > created_at)
);

-- =============================================================================
-- MCP Server Registry Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS mcp_server_registry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    base_url VARCHAR(512) UNIQUE NOT NULL,
    description TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    last_known_status VARCHAR(50),
    available_tools_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Enhanced authentication fields
    auth_type VARCHAR(50) DEFAULT 'none',
    auth_config JSONB,
    health_check_interval INTEGER DEFAULT 300,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds DECIMAL(5,2) DEFAULT 30.0,

    -- Constraints
    CONSTRAINT chk_mcp_auth_type CHECK (auth_type IN ('none', 'api_key', 'bearer_token', 'basic_auth')),
    CONSTRAINT chk_mcp_health_interval CHECK (health_check_interval > 0),
    CONSTRAINT chk_mcp_max_retries CHECK (max_retries >= 0),
    CONSTRAINT chk_mcp_timeout CHECK (timeout_seconds > 0)
);

-- =============================================================================
-- Performance Indexes
-- =============================================================================

-- Agent Tasks indexes
CREATE INDEX IF NOT EXISTS idx_agent_tasks_task_id ON agent_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_type ON agent_tasks(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_composite ON agent_tasks(agent_type, status, created_at);

-- Agent Metrics indexes
CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_type ON agent_metrics(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_composite ON agent_metrics(agent_type, metric_name, timestamp);

-- System Events indexes
CREATE INDEX IF NOT EXISTS idx_system_events_event_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events(severity);
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_events_source ON system_events(source);

-- User Sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);

-- MCP Server Registry indexes
CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_name ON mcp_server_registry(name);
CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_base_url ON mcp_server_registry(base_url);
CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_enabled ON mcp_server_registry(enabled);
CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_status ON mcp_server_registry(last_known_status);

-- =============================================================================
-- Triggers for Automatic Timestamp Updates
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to relevant tables
DROP TRIGGER IF EXISTS update_agent_tasks_updated_at ON agent_tasks;
CREATE TRIGGER update_agent_tasks_updated_at
    BEFORE UPDATE ON agent_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON user_sessions;
CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mcp_server_registry_updated_at ON mcp_server_registry;
CREATE TRIGGER update_mcp_server_registry_updated_at
    BEFORE UPDATE ON mcp_server_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Initial Data and Configuration
-- =============================================================================

-- Insert default MCP server entries (if needed)
INSERT INTO mcp_server_registry (name, base_url, description, enabled)
VALUES
    ('Local MCP Server', 'http://localhost:3001', 'Local development MCP server', true)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- Database Security and Performance Settings
-- =============================================================================

-- Create a read-only user for monitoring (optional)
-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ai_agent_readonly') THEN
--         CREATE ROLE ai_agent_readonly WITH LOGIN PASSWORD 'readonly_password_change_this';
--         GRANT CONNECT ON DATABASE postgres TO ai_agent_readonly;
--         GRANT USAGE ON SCHEMA public TO ai_agent_readonly;
--         GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_agent_readonly;
--         ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_agent_readonly;
--     END IF;
-- END
-- $$;

-- Analyze tables for query optimization
ANALYZE agent_tasks;
ANALYZE agent_metrics;
ANALYZE system_events;
ANALYZE user_sessions;
ANALYZE mcp_server_registry;

-- Log successful initialization
INSERT INTO system_events (event_type, event_data, severity, source)
VALUES (
    'database_initialization',
    '{"message": "Database schema initialized successfully", "version": "1.0", "timestamp": "' || NOW() || '"}',
    'info',
    'init_database.sql'
);
