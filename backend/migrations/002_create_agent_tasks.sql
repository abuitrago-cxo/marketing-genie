-- Migration: 002_create_agent_tasks.sql
-- Creates persistent table for tracking agent tasks

CREATE TABLE IF NOT EXISTS agent_tasks (
    task_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    priority TEXT NOT NULL DEFAULT 'medium',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    execution_time_ms INTEGER
);

-- Index to quickly fetch tasks by agent type and status
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_status
    ON agent_tasks (agent_type, status);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at_agent_tasks()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_updated_at_agent_tasks ON agent_tasks;
CREATE TRIGGER trg_set_updated_at_agent_tasks
    BEFORE UPDATE ON agent_tasks
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at_agent_tasks();
