#!/usr/bin/env python3
"""
Test Runner for Hitos 1 and 2
Executes all tests and provides comprehensive reporting
"""

import sys
import asyncio
import traceback
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

async def run_hito1_tests():
    """Run all Hito 1 infrastructure tests"""
    print_section("HITO 1: INFRASTRUCTURE TESTS")
    
    try:
        # Import and run Hito 1 tests
        from test_hito1_infrastructure import (
            test_database_connection,
            test_database_schema,
            test_memory_system,
            test_specialized_states,
            test_environment_setup
        )
        
        tests = [
            ("Environment Setup", test_environment_setup, False),
            ("Database Connection", test_database_connection, True),
            ("Database Schema", test_database_schema, True),
            ("Memory System", test_memory_system, True),
            ("Specialized States", test_specialized_states, True),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func, is_async in tests:
            try:
                print(f"\n🧪 Running: {test_name}")
                if is_async:
                    await test_func()
                else:
                    test_func()
                passed += 1
                print(f"✅ {test_name}: PASSED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name}: FAILED")
                print(f"   Error: {str(e)}")
                if "database" in test_name.lower():
                    print("   Note: Database tests may fail if PostgreSQL is not running")
                elif "memory" in test_name.lower():
                    print("   Note: Memory tests may fail if Redis is not running")
        
        print(f"\n📊 Hito 1 Results: {passed} passed, {failed} failed")
        return passed, failed
        
    except Exception as e:
        print(f"❌ Failed to run Hito 1 tests: {e}")
        traceback.print_exc()
        return 0, 1

async def run_hito2_tests():
    """Run all Hito 2 codebase analysis tests"""
    print_section("HITO 2: CODEBASE ANALYSIS TESTS")
    
    try:
        # Import and run Hito 2 tests
        from test_hito2_codebase_analysis import (
            test_projects_api_health,
            test_create_project_endpoint,
            test_codebase_analysis_endpoint_structure,
            test_memory_integration_in_analysis,
            test_analysis_request_validation,
            test_analysis_response_structure,
            test_codebase_analysis_state,
            test_frontend_integration_types
        )
        
        # Create test client
        from fastapi.testclient import TestClient
        from src.agent.app import app
        client = TestClient(app)
        
        tests = [
            ("API Health Check", lambda: test_projects_api_health(client), False),
            ("Create Project Endpoint", lambda: test_create_project_endpoint(client), False),
            ("Analysis Endpoint Structure", lambda: test_codebase_analysis_endpoint_structure(client), False),
            ("Memory Integration", test_memory_integration_in_analysis, True),
            ("Request Validation", test_analysis_request_validation, False),
            ("Response Structure", test_analysis_response_structure, False),
            ("Analysis State", test_codebase_analysis_state, True),
            ("Frontend Integration", test_frontend_integration_types, False),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func, is_async in tests:
            try:
                print(f"\n🧪 Running: {test_name}")
                if is_async:
                    await test_func()
                else:
                    test_func()
                passed += 1
                print(f"✅ {test_name}: PASSED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name}: FAILED")
                print(f"   Error: {str(e)}")
                if "endpoint" in test_name.lower():
                    print("   Note: API tests may fail if dependencies are not installed")
        
        print(f"\n📊 Hito 2 Results: {passed} passed, {failed} failed")
        return passed, failed
        
    except Exception as e:
        print(f"❌ Failed to run Hito 2 tests: {e}")
        traceback.print_exc()
        return 0, 1

def run_integration_tests():
    """Run integration tests between Hito 1 and 2"""
    print_section("INTEGRATION TESTS")
    
    try:
        print("\n🧪 Running: End-to-End Integration")
        
        # Test that we can import all major components
        from src.agent.app import app
        from src.api.projects_endpoints import projects_router
        from src.agent.state import CodebaseAnalysisState
        
        # Test FastAPI app creation
        assert app is not None, "FastAPI app should be created"
        
        # Test router registration
        assert projects_router is not None, "Projects router should be created"
        
        # Test state creation
        state = CodebaseAnalysisState()
        assert state is not None, "CodebaseAnalysisState should be created"
        
        print("✅ End-to-End Integration: PASSED")
        return 1, 0
        
    except Exception as e:
        print(f"❌ End-to-End Integration: FAILED")
        print(f"   Error: {str(e)}")
        return 0, 1

async def main():
    """Main test runner"""
    print_header("AI AGENT ASSISTANT - TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_passed = 0
    total_failed = 0
    
    # Run Hito 1 tests
    h1_passed, h1_failed = await run_hito1_tests()
    total_passed += h1_passed
    total_failed += h1_failed
    
    # Run Hito 2 tests  
    h2_passed, h2_failed = await run_hito2_tests()
    total_passed += h2_passed
    total_failed += h2_failed
    
    # Run integration tests
    int_passed, int_failed = run_integration_tests()
    total_passed += int_passed
    total_failed += int_failed
    
    # Final report
    print_header("FINAL TEST REPORT")
    print(f"📊 Total Tests: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for production.")
        success_rate = 100
    else:
        success_rate = (total_passed / (total_passed + total_failed)) * 100
        print(f"\n⚠️  Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ System is mostly functional with minor issues.")
        elif success_rate >= 60:
            print("⚠️  System has some issues that should be addressed.")
        else:
            print("❌ System has significant issues that need immediate attention.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
