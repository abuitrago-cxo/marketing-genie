"""
Test Suite for Hito 1: Infrastructure Base
Tests database, memory system, states, and integration patterns
"""

import pytest
import asyncio
import os
from datetime import datetime
from typing import Dict, Any

# Test database connectivity and schema
@pytest.mark.skipif(not os.getenv("POSTGRES_URI"), reason="POSTGRES_URI not set, skipping real DB test")
@pytest.mark.asyncio
async def test_database_connection():
    """Test PostgreSQL database connection and basic operations"""
    try:
        from agent.database import get_database_pool
        
        pool = await get_database_pool()
        assert pool is not None, "Database pool should be created"
        
        # Test basic query
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1, "Basic query should work"
            
        print("✅ Database connection test passed")
        
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

@pytest.mark.asyncio
async def test_database_schema():
    """Test that all required tables exist with correct structure"""
    try:
        from agent.database import get_database_pool
        
        pool = await get_database_pool()
        
        required_tables = [
            'projects',
            'project_tasks', 
            'project_milestones',
            'agent_long_term_memory'
        ]
        
        async with pool.acquire() as conn:
            for table in required_tables:
                # Check if table exists
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                assert exists, f"Table {table} should exist"
                
                # Check table has records capability (insert/select)
                if table == 'projects':
                    # Test projects table structure
                    columns = await conn.fetch(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = $1",
                        table
                    )
                    column_names = [col['column_name'] for col in columns]
                    
                    required_columns = ['id', 'name', 'description', 'status', 'created_at']
                    for col in required_columns:
                        assert col in column_names, f"Column {col} should exist in {table}"
        
        print("✅ Database schema test passed")
        
    except Exception as e:
        pytest.fail(f"Database schema test failed: {e}")

@pytest.mark.asyncio
async def test_memory_system():
    """Test long-term and short-term memory systems"""
    try:
        from memory import get_memory_manager
        
        memory_manager = await get_memory_manager()
        assert memory_manager is not None, "Memory manager should be initialized"
        
        # Test storing memory
        test_content = "Test memory content for infrastructure validation"
        memory_id = await memory_manager.store_memory(
            agent_id="test_agent",
            content=test_content,
            memory_type="test_memory",
            importance_score=0.8,
            metadata={"test": True, "hito": 1}
        )
        
        assert memory_id is not None, "Memory should be stored successfully"
        
        # Test retrieving memory
        memories = await memory_manager.retrieve_memories(
            agent_id="test_agent",
            memory_types=["test_memory"],
            limit=1
        )
        
        assert len(memories) > 0, "Should retrieve stored memory"
        assert memories[0]["content"] == test_content, "Retrieved content should match"
        
        print("✅ Memory system test passed")
        
    except Exception as e:
        pytest.fail(f"Memory system test failed: {e}")

@pytest.mark.asyncio
async def test_specialized_states():
    """Test that all specialized states are properly defined"""
    try:
        from agent.state import (
            CodebaseAnalysisState,
            DocumentationAnalysisState, 
            TaskPlanningState,
            ResearchState,
            QAState,
            OrchestratorState,
            MemoryEnhancedState
        )
        
        # Test CodebaseAnalysisState
        codebase_state = CodebaseAnalysisState()
        assert hasattr(codebase_state, 'repository_url'), "CodebaseAnalysisState should have repository_url"
        assert hasattr(codebase_state, 'analysis_type'), "CodebaseAnalysisState should have analysis_type"
        assert hasattr(codebase_state, 'analysis_results'), "CodebaseAnalysisState should have analysis_results"
        
        # Test MemoryEnhancedState
        memory_state = MemoryEnhancedState()
        assert hasattr(memory_state, 'long_term_memories'), "MemoryEnhancedState should have long_term_memories"
        assert hasattr(memory_state, 'short_term_cache'), "MemoryEnhancedState should have short_term_cache"
        
        print("✅ Specialized states test passed")
        
    except Exception as e:
        pytest.fail(f"Specialized states test failed: {e}")

def test_environment_setup():
    """Test that all required environment variables and dependencies are available"""
    
    # Check Python version
    import sys
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    # Check required packages
    required_packages = [
        'fastapi',
        'asyncpg', 
        'redis',
        'langgraph',
        'pydantic'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            pytest.fail(f"Required package {package} not installed")
    
    print("✅ Environment setup test passed")

if __name__ == "__main__":
    # Run tests individually for debugging
    asyncio.run(test_database_connection())
    asyncio.run(test_database_schema())
    asyncio.run(test_memory_system())
    asyncio.run(test_specialized_states())
    test_environment_setup()
    
    print("\n🎉 All Hito 1 infrastructure tests passed!")
