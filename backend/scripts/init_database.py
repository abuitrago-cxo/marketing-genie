#!/usr/bin/env python3
"""
Database initialization script for Enhanced AI Agent Assistant
Creates necessary tables and indexes for the enhanced features.
"""

import os
import sys
import asyncio
import logging
from typing import Optional
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add src to path
sys.path.append('/deps/backend/src')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_postgres_uri(uri: str) -> dict:
    """Parse PostgreSQL URI into connection parameters."""
    # Example: postgres://user:password@host:port/database
    import re
    pattern = r'postgres://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)'
    match = re.match(pattern, uri)
    
    if not match:
        raise ValueError(f"Invalid PostgreSQL URI: {uri}")
    
    return {
        'user': match.group(1),
        'password': match.group(2),
        'host': match.group(3),
        'port': int(match.group(4)),
        'database': match.group(5)
    }

def create_database_if_not_exists(conn_params: dict, db_name: str):
    """Create database if it doesn't exist."""
    # Connect to postgres database to create our database
    temp_params = conn_params.copy()
    temp_params['database'] = 'postgres'
    
    try:
        conn = psycopg2.connect(**temp_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cursor.fetchone():
            logger.info(f"Creating database: {db_name}")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
        else:
            logger.info(f"Database {db_name} already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_enhanced_tables(conn_params: dict):
    """Create tables for enhanced features."""
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Agent tasks table
        cursor.execute("""
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
                execution_time_ms INTEGER
            )
        """)
        
        # Agent performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id SERIAL PRIMARY KEY,
                agent_type VARCHAR(100) NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB
            )
        """)
        
        # LLM provider usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_usage (
                id SERIAL PRIMARY KEY,
                provider_id VARCHAR(100) NOT NULL,
                model_name VARCHAR(100) NOT NULL,
                tokens_used INTEGER NOT NULL,
                cost_estimate DECIMAL(10, 6),
                response_time_ms INTEGER,
                success BOOLEAN NOT NULL DEFAULT TRUE,
                error_message TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                task_id VARCHAR(255),
                agent_type VARCHAR(100)
            )
        """)
        
        # System events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB,
                severity VARCHAR(20) NOT NULL DEFAULT 'info',
                source VARCHAR(100),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)

        # MCP Server Registry table
        cursor.execute("""
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
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # User sessions table (for future use)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB
            )
        """)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_type ON agent_tasks(agent_type)",
            "CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_type ON agent_metrics(agent_type)",
            "CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_llm_usage_provider ON llm_usage(provider_id)",
            "CREATE INDEX IF NOT EXISTS idx_llm_usage_timestamp ON llm_usage(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_name ON mcp_server_registry(name)",
            "CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_base_url ON mcp_server_registry(base_url)",
            "CREATE INDEX IF NOT EXISTS idx_mcp_server_registry_enabled ON mcp_server_registry(enabled)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Create updated_at trigger function
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # Create trigger for agent_tasks
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_agent_tasks_updated_at ON agent_tasks;
            CREATE TRIGGER update_agent_tasks_updated_at
                BEFORE UPDATE ON agent_tasks
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create trigger for mcp_server_registry
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_mcp_server_registry_updated_at ON mcp_server_registry;
            CREATE TRIGGER update_mcp_server_registry_updated_at
                BEFORE UPDATE ON mcp_server_registry
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Enhanced tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating enhanced tables: {e}")
        raise

def insert_initial_data(conn_params: dict):
    """Insert initial data for the enhanced features."""
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Insert initial system event
        cursor.execute("""
            INSERT INTO system_events (event_type, event_data, severity, source)
            VALUES ('system_initialized', %s, 'info', 'init_script')
            ON CONFLICT DO NOTHING
        """, ('{"message": "Enhanced AI Agent Assistant initialized"}',))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Initial data inserted successfully")
        
    except Exception as e:
        logger.error(f"Error inserting initial data: {e}")
        raise

def main():
    """Main initialization function."""
    logger.info("🗄️  Initializing Enhanced AI Agent Assistant Database")
    
    # Get PostgreSQL URI from environment
    postgres_uri = os.getenv('POSTGRES_URI')
    if not postgres_uri:
        logger.error("POSTGRES_URI environment variable not set")
        sys.exit(1)
    
    try:
        # Parse connection parameters
        conn_params = parse_postgres_uri(postgres_uri)
        db_name = conn_params['database']
        
        # Create database if needed
        create_database_if_not_exists(conn_params, db_name)
        
        # Create enhanced tables
        create_enhanced_tables(conn_params)
        
        # Insert initial data
        insert_initial_data(conn_params)
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
