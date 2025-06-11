#!/usr/bin/env python3
"""
Phase 2 Tools Testing Script

This script tests the new tool integration system to ensure everything works correctly
while maintaining compatibility with the existing Gemini + LangGraph system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

async def test_tool_registry():
    """Test the tool registry system"""
    print("🔧 Testing Tool Registry...")
    
    try:
        from agent.tools import get_tool_registry
        
        registry = get_tool_registry()
        status = registry.get_registry_status()
        
        print(f"✅ Registry loaded with {status['total_tools']} tools")
        print(f"   Categories: {list(status['categories'].keys())}")
        
        # Test each tool
        for tool_name, tool_status in status['tools'].items():
            print(f"   - {tool_name}: {tool_status['status']} ({len(tool_status['capabilities'])} capabilities)")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False


async def test_file_operations():
    """Test file operations tool"""
    print("\n📁 Testing File Operations Tool...")
    
    try:
        from agent.tools import get_tool_registry
        
        registry = get_tool_registry()
        
        # Test list directory
        result = await registry.execute_tool(
            "file_operations", 
            "list_directory", 
            {"directory_path": "."}
        )
        
        if result.success:
            print(f"✅ List directory: Found {len(result.data['items'])} items")
        else:
            print(f"❌ List directory failed: {result.error}")
            return False
        
        # Test create and write file
        test_content = "Hello from Phase 2 Tools!\nThis is a test file."
        result = await registry.execute_tool(
            "file_operations",
            "write_file",
            {
                "file_path": "test_phase2.txt",
                "content": test_content
            }
        )
        
        if result.success:
            print("✅ Write file: Created test file")
        else:
            print(f"❌ Write file failed: {result.error}")
            return False
        
        # Test read file
        result = await registry.execute_tool(
            "file_operations",
            "read_file",
            {"file_path": "test_phase2.txt"}
        )
        
        if result.success and result.data['content'] == test_content:
            print("✅ Read file: Content matches")
        else:
            print(f"❌ Read file failed: {result.error}")
            return False
        
        # Clean up
        result = await registry.execute_tool(
            "file_operations",
            "delete_file",
            {"file_path": "test_phase2.txt"}
        )
        
        if result.success:
            print("✅ Delete file: Cleanup successful")
        else:
            print(f"⚠️ Cleanup warning: {result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False


async def test_project_management():
    """Test project management tool"""
    print("\n📋 Testing Project Management Tool...")
    
    try:
        from agent.tools import get_tool_registry
        
        registry = get_tool_registry()
        
        # Test create task
        result = await registry.execute_tool(
            "project_management",
            "create_task",
            {
                "title": "Test Phase 2 Integration",
                "description": "Verify that all Phase 2 tools work correctly",
                "priority": "high",
                "project_id": "phase2_test"
            }
        )
        
        if result.success:
            task_id = result.data['task']['id']
            print(f"✅ Create task: Created task {task_id}")
        else:
            print(f"❌ Create task failed: {result.error}")
            return False
        
        # Test list tasks
        result = await registry.execute_tool(
            "project_management",
            "list_tasks",
            {"project_id": "phase2_test"}
        )
        
        if result.success and result.data['total_count'] > 0:
            print(f"✅ List tasks: Found {result.data['total_count']} tasks")
        else:
            print(f"❌ List tasks failed: {result.error}")
            return False
        
        # Test project analysis
        result = await registry.execute_tool(
            "project_management",
            "analyze_project",
            {"project_id": "phase2_test"}
        )
        
        if result.success:
            analysis = result.data['analysis']
            print(f"✅ Project analysis: {analysis['total_tasks']} tasks, {analysis['completion_rate']}% complete")
        else:
            print(f"❌ Project analysis failed: {result.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Project management test failed: {e}")
        return False


async def test_web_operations():
    """Test web operations tool"""
    print("\n🌐 Testing Web Operations Tool...")
    
    try:
        from agent.tools import get_tool_registry
        
        registry = get_tool_registry()
        
        # Test URL status check
        result = await registry.execute_tool(
            "web_operations",
            "check_url_status",
            {"url": "https://httpbin.org/status/200"}
        )
        
        if result.success and result.data['is_accessible']:
            print("✅ URL status check: URL is accessible")
        else:
            print(f"❌ URL status check failed: {result.error}")
            return False
        
        # Test HTTP request
        result = await registry.execute_tool(
            "web_operations",
            "http_request",
            {
                "url": "https://httpbin.org/json",
                "method": "GET"
            }
        )
        
        if result.success and result.data['status_code'] == 200:
            print("✅ HTTP request: Successful GET request")
        else:
            print(f"❌ HTTP request failed: {result.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web operations test failed: {e}")
        return False


async def test_enhanced_graph():
    """Test the enhanced graph integration"""
    print("\n🔄 Testing Enhanced Graph...")
    
    try:
        from agent.enhanced_graph import get_enhanced_graph, get_original_graph
        
        # Test graph creation
        enhanced_graph = get_enhanced_graph()
        original_graph = get_original_graph()
        
        print("✅ Enhanced graph: Created successfully")
        print("✅ Original graph: Still available")
        
        # Test graph nodes
        enhanced_nodes = enhanced_graph.get_graph().nodes()
        original_nodes = original_graph.get_graph().nodes()
        
        print(f"   Enhanced graph nodes: {len(enhanced_nodes)}")
        print(f"   Original graph nodes: {len(original_nodes)}")
        
        # Check for new nodes
        new_nodes = set(enhanced_nodes) - set(original_nodes)
        print(f"   New nodes added: {new_nodes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced graph test failed: {e}")
        return False


async def test_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test tools registry endpoint
            try:
                async with session.get('http://localhost:2024/api/v1/enhanced/tools/registry') as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Tools registry API: {data['data']['total_tools']} tools available")
                    else:
                        print(f"⚠️ Tools registry API: Server returned {response.status}")
            except aiohttp.ClientConnectorError:
                print("⚠️ API endpoints: Server not running (this is optional)")
                return True
            
            # Test graph status endpoint
            try:
                async with session.get('http://localhost:2024/api/v1/enhanced/graph/status') as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Graph status API: Available")
                    else:
                        print(f"⚠️ Graph status API: Server returned {response.status}")
            except aiohttp.ClientConnectorError:
                pass
        
        return True
        
    except ImportError:
        print("⚠️ API endpoints: aiohttp not available (install with: pip install aiohttp)")
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Phase 2 Tools Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_tool_registry,
        test_file_operations,
        test_project_management,
        test_web_operations,
        test_enhanced_graph,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 2 integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
