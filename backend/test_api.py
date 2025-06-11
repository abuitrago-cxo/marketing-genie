"""
LangGraph API Test Script

This script tests the complete functionality of the LangGraph API endpoints
to ensure they are properly registered and working.
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any, List, Optional
import pytest
pytest.skip("Standalone test script; skip in pytest", allow_module_level=True)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# API configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30  # seconds

# Terminal colors for readability
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str) -> None:
    """Print an informational message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def health_endpoint(path: str) -> bool:
    """Test a health endpoint."""
    endpoint = f"{API_BASE_URL}{path}"
    print_info(f"Testing health endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check successful: {response.status_code}")
            print_info(f"Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"Failed to connect to health endpoint: {e}")
        return False

def api_health() -> bool:
    """Test the API health endpoint."""
    endpoint = f"{API_BASE_URL}/api/health"
    print_info(f"Testing API health endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API health check successful: {response.status_code}")
            print_info(f"API Version: {data.get('api_version', 'Unknown')}")
            print_info(f"Endpoints available: {', '.join(data.get('endpoints', {}).keys())}")
            return True
        else:
            print_error(f"API health check failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print_error(f"Failed to connect to API health endpoint: {e}")
        return False

def specialized_query(query: str = "What are LangGraph's main features?") -> bool:
    """Test the specialized query endpoint."""
    endpoint = f"{API_BASE_URL}/api/v1/specialized/query"
    print_info(f"Testing specialized query endpoint: {endpoint}")
    
    data = {
        "query": query,
        "max_research_iterations": 1,
        "enable_tracing": True,
        "use_multi_agent": False
    }
    
    try:
        print_info(f"Sending query: '{query}'")
        response = requests.post(endpoint, json=data, timeout=API_TIMEOUT * 2)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Specialized query successful: {response.status_code}")
            print_info(f"Answer: {result.get('final_answer', '')[:100]}...")
            print_info(f"Quality Score: {result.get('quality_score', 0)}")
            print_info(f"Citations: {len(result.get('citations', []))}")
            return True
        else:
            print_error(f"Specialized query failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print_error(f"Failed to connect to specialized query endpoint: {e}")
        return False

def specialized_chat() -> bool:
    """Test the specialized chat endpoint."""
    endpoint = f"{API_BASE_URL}/api/v1/specialized/chat"
    print_info(f"Testing specialized chat endpoint: {endpoint}")
    
    data = {
        "query": "What is the difference between LangChain and LangGraph?",
        "max_research_iterations": 1,
        "enable_tracing": True,
        "use_real_agents": True,
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(endpoint, json=data, timeout=API_TIMEOUT * 2)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Specialized chat successful: {response.status_code}")
            print_info(f"Answer: {result.get('final_answer', '')[:100]}...")
            print_info(f"Trace ID: {result.get('trace_id', 'None')}")
            return True
        else:
            print_error(f"Specialized chat failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print_error(f"Failed to connect to specialized chat endpoint: {e}")
        return False

def api_routes() -> Dict[str, bool]:
    """Test all API routes and return results."""
    results = {}
    
    # Basic health checks
    print_header("Testing Basic Health Endpoints")
    results["system_health"] = health_endpoint("/health")
    results["api_health"] = api_health()
    
    # Specialized endpoints
    print_header("Testing Specialized Agent Endpoints")
    results["specialized_query"] = specialized_query()
    results["specialized_chat"] = specialized_chat()
    
    # Summary
    print_header("Test Results Summary")
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print_info(f"Total tests: {total_tests}")
    print_info(f"Passed: {passed_tests}")
    print_info(f"Failed: {total_tests - passed_tests}")
    
    for endpoint, result in results.items():
        if result:
            print_success(f"{endpoint}: PASS")
        else:
            print_error(f"{endpoint}: FAIL")
    
    return results

def wait_for_api_ready(max_attempts: int = 10, delay: int = 2) -> bool:
    """Wait for the API to become available."""
    print_header("Waiting for API to become available")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print_info(f"Attempt {attempt}/{max_attempts}: Checking if API is ready...")
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"API is ready after {attempt} attempts!")
                return True
            else:
                print_warning(f"API returned status code {response.status_code}, waiting...")
        except requests.RequestException as e:
            print_warning(f"API not ready yet: {e}")
        
        if attempt < max_attempts:
            time.sleep(delay)
    
    print_error(f"API did not become ready after {max_attempts} attempts.")
    return False

if __name__ == "__main__":
    print_header("LangGraph API Test Script")
    
    if wait_for_api_ready():
        results = api_routes()
        success_rate = sum(1 for result in results.values() if result) / len(results) if results else 0
        
        print_header("Overall Test Result")
        if success_rate == 1.0:
            print_success(f"All tests passed! Success rate: {success_rate * 100:.1f}%")
            sys.exit(0)
        elif success_rate >= 0.8:
            print_warning(f"Most tests passed. Success rate: {success_rate * 100:.1f}%")
            sys.exit(1)
        else:
            print_error(f"Significant test failures. Success rate: {success_rate * 100:.1f}%")
            sys.exit(2)
    else:
        print_error("Could not connect to the API. Is the server running?")
        sys.exit(3)
