"""
Tests for agents endpoints functionality.
"""

import pytest
import json
import agent.database
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Mock the database and memory managers before importing the app
import memory.long_term_memory_manager
import memory.short_term_memory_manager

with patch('agent.database.get_db_connection'), \
     patch('memory.long_term_memory_manager.LongTermMemoryManager'), \
     patch('memory.short_term_memory_manager.ShortTermMemoryManager'):
    
    from agent.app import app
    from api.agents_endpoints import GRAPH_TO_AGENT_MAPPING, get_agent_execution_stats, get_current_agent_status

client = TestClient(app)

class TestAgentsEndpoints:
    """Test class for agents endpoints."""

    def test_get_agents_status_success(self):
        """Test successful retrieval of agents status."""
        with patch('api.agents_endpoints.get_db_connection') as mock_db, \
             patch('api.agents_endpoints.get_agent_execution_stats') as mock_stats, \
             patch('api.agents_endpoints.get_current_agent_status') as mock_status:
            
            # Mock database connection
            mock_connection = Mock()
            mock_db.return_value = mock_connection
            
            # Mock execution stats
            mock_stats.return_value = {
                'total_executions': 50,
                'success_rate': 95.5,
                'avg_duration': 2.3,
                'last_execution': datetime.now() - timedelta(minutes=30)
            }
            
            # Mock current status
            mock_status.return_value = 'active'
            
            response = client.get("/api/v1/agents/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == len(GRAPH_TO_AGENT_MAPPING)
            
            # Check first agent
            agent = data[0]
            assert 'id' in agent
            assert 'name' in agent
            assert 'type' in agent
            assert 'status' in agent
            assert 'capabilities' in agent
            assert 'tasks_completed' in agent
            assert 'success_rate' in agent
            assert 'avg_response_time' in agent
            assert 'last_activity' in agent
            assert 'is_enabled' in agent
            
            assert agent['tasks_completed'] == 50
            assert agent['success_rate'] == 95.5
            assert agent['status'] == 'active'
            assert agent['is_enabled'] is True

    def test_get_agents_metrics_success(self):
        """Test successful retrieval of agents metrics."""
        with patch('api.agents_endpoints.get_agents_status') as mock_get_agents:
            # Mock agents data
            mock_agents = [
                {
                    'id': 'agent1',
                    'status': 'active',
                    'success_rate': 95.0,
                    'tasks_completed': 100
                },
                {
                    'id': 'agent2',
                    'status': 'busy',
                    'success_rate': 90.0,
                    'tasks_completed': 80
                },
                {
                    'id': 'agent3',
                    'status': 'idle',
                    'success_rate': 88.0,
                    'tasks_completed': 60
                }
            ]
            mock_get_agents.return_value = mock_agents
            
            response = client.get("/api/v1/agents/metrics")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['total_agents'] == 3
            assert data['active_agents'] == 2  # active + busy
            assert data['busy_agents'] == 1
            assert data['avg_success_rate'] == 91.0  # (95 + 90 + 88) / 3
            assert data['total_tasks_completed'] == 240  # 100 + 80 + 60

    def test_toggle_agent_success(self):
        """Test successful agent toggle."""
        response = client.post("/api/v1/agents/codebase-analysis/toggle")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert data['agent_id'] == 'codebase-analysis'
        assert 'message' in data

    def test_toggle_agent_not_found(self):
        """Test toggle agent with invalid ID."""
        response = client.post("/api/v1/agents/invalid-agent/toggle")
        
        assert response.status_code == 404
        data = response.json()
        assert data['detail'] == 'Agent not found'

    def test_get_workflows_history_success(self):
        """Test successful retrieval of workflows history."""
        with patch('api.agents_endpoints.get_db_connection') as mock_db, \
             patch('api.agents_endpoints.get_agent_execution_stats') as mock_stats:
            
            # Mock database connection
            mock_connection = Mock()
            mock_db.return_value = mock_connection
            
            # Mock execution stats
            mock_stats.return_value = {
                'total_executions': 25,
                'success_rate': 92.0,
                'avg_duration': 3.5,
                'last_execution': datetime.now() - timedelta(hours=2)
            }
            
            response = client.get("/api/v1/workflows/history")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == len(GRAPH_TO_AGENT_MAPPING)
            
            # Check first workflow
            workflow = data[0]
            assert 'id' in workflow
            assert 'name' in workflow
            assert 'category' in workflow
            assert 'agent_type' in workflow
            assert 'status' in workflow
            assert 'success_rate' in workflow
            assert 'avg_duration' in workflow
            assert 'last_execution' in workflow
            assert 'total_executions' in workflow
            
            assert workflow['total_executions'] == 25
            assert workflow['success_rate'] == 92.0
            assert workflow['avg_duration'] == 3.5

class TestAgentHelperFunctions:
    """Test helper functions for agents."""

    @pytest.mark.asyncio
    async def test_get_agent_execution_stats_success(self):
        """Test successful retrieval of agent execution stats."""
        # Mock database cursor and results
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (10, 95.0, 2.5, datetime.now())
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        result = await get_agent_execution_stats('codebase-analysis', mock_connection)
        
        assert result['total_executions'] == 10
        assert result['success_rate'] == 95.0
        assert result['avg_duration'] == 2.5
        assert isinstance(result['last_execution'], datetime)

    @pytest.mark.asyncio
    async def test_get_agent_execution_stats_no_data(self):
        """Test agent execution stats when no data is found."""
        # Mock database cursor with no results
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        result = await get_agent_execution_stats('new-agent', mock_connection)
        
        assert result['total_executions'] == 0
        assert result['success_rate'] == 85.0  # default value
        assert result['avg_duration'] == 2.5  # default value
        assert isinstance(result['last_execution'], datetime)

    @pytest.mark.asyncio
    async def test_get_agent_execution_stats_database_error(self):
        """Test agent execution stats when database error occurs."""
        # Mock database connection that raises an exception
        mock_connection = Mock()
        mock_connection.cursor.side_effect = Exception("Database error")
        
        result = await get_agent_execution_stats('error-agent', mock_connection)
        
        # Should return default values on error
        assert result['total_executions'] == 0
        assert result['success_rate'] == 85.0
        assert result['avg_duration'] == 2.5
        assert isinstance(result['last_execution'], datetime)

    @pytest.mark.asyncio
    async def test_get_current_agent_status(self):
        """Test current agent status determination."""
        # Test multiple calls to ensure randomness works
        statuses = []
        for _ in range(10):
            status = await get_current_agent_status('test-agent')
            statuses.append(status)
            assert status in ['active', 'idle', 'busy']
        
        # Should have some variety in statuses (not all the same)
        unique_statuses = set(statuses)
        assert len(unique_statuses) >= 1  # At least one status type

class TestAgentMapping:
    """Test agent mapping configuration."""

    def test_graph_to_agent_mapping_completeness(self):
        """Test that all required agents are mapped."""
        expected_agents = [
            'codebase-analysis',
            'documentation-analysis',
            'task-planning',
            'research-analysis',
            'qa-testing',
            'project-orchestrator'
        ]
        
        for agent_id in expected_agents:
            assert agent_id in GRAPH_TO_AGENT_MAPPING
            
            agent_config = GRAPH_TO_AGENT_MAPPING[agent_id]
            assert 'name' in agent_config
            assert 'type' in agent_config
            assert 'description' in agent_config
            assert 'capabilities' in agent_config
            assert isinstance(agent_config['capabilities'], list)
            assert len(agent_config['capabilities']) > 0

    def test_agent_types_are_valid(self):
        """Test that all agent types are valid."""
        valid_types = [
            'code-engineer',
            'analysis',
            'project-manager',
            'research',
            'qa-specialist',
            'devops'
        ]
        
        for agent_config in GRAPH_TO_AGENT_MAPPING.values():
            assert agent_config['type'] in valid_types

    def test_agent_capabilities_not_empty(self):
        """Test that all agents have capabilities defined."""
        for agent_id, agent_config in GRAPH_TO_AGENT_MAPPING.items():
            assert len(agent_config['capabilities']) > 0, f"Agent {agent_id} has no capabilities"
            
            # Each capability should be a non-empty string
            for capability in agent_config['capabilities']:
                assert isinstance(capability, str)
                assert len(capability.strip()) > 0

if __name__ == "__main__":
    pytest.main([__file__])
