#!/usr/bin/env python3
"""
Simple verification script for agent restructuring.
This script tests the new modular agent structure without depending on the full application.
"""

import os
import sys
import importlib.util

def test_file_exists(file_path):
    """Test that a file exists."""
    if os.path.exists(file_path):
        print(f"✅ {file_path} exists")
        return True
    else:
        print(f"❌ {file_path} does not exist")
        return False

def test_module_import(module_path, module_name):
    """Test that a module can be imported."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def test_agent_modules():
    """Test all agent modules."""
    print("\n🔍 Testing Agent Modules...")
    
    agent_modules = [
        ("services/api_gateway/routes/agents/base.py", "base"),
        ("services/api_gateway/routes/agents/browser_agent.py", "browser_agent"),
        ("services/api_gateway/routes/agents/pdf_agent.py", "pdf_agent"),
        ("services/api_gateway/routes/agents/knowledge_agent.py", "knowledge_agent"),
        ("services/api_gateway/routes/agents/code_agent.py", "code_agent"),
        ("services/api_gateway/routes/agents/database_agent.py", "database_agent"),
        ("services/api_gateway/routes/agents/crawler_agent.py", "crawler_agent"),
        ("services/api_gateway/routes/agents/__init__.py", "agents_init"),
        ("services/api_gateway/routes/agents_new.py", "agents_new"),
        ("services/api_gateway/routes/agents.py", "agents_main")
    ]
    
    success_count = 0
    total_count = len(agent_modules)
    
    for file_path, module_name in agent_modules:
        if test_file_exists(file_path):
            if test_module_import(file_path, module_name):
                success_count += 1
    
    print(f"\n📊 Agent Modules: {success_count}/{total_count} passed")
    return success_count == total_count

def test_base_utilities():
    """Test base utilities."""
    print("\n🔍 Testing Base Utilities...")
    
    try:
        # Import base utilities
        base_path = "services/api_gateway/routes/agents/base.py"
        spec = importlib.util.spec_from_file_location("base", base_path)
        base_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base_module)
        
        # Test AgentResponseFormatter
        formatter = base_module.AgentResponseFormatter()
        response = formatter.format_success(
            agent_id="test-agent",
            result={"test": "data"},
            processing_time=1.0,
            metadata={"test": True},
            user_id="test-user"
        )
        
        assert response.agent_id == "test-agent"
        assert response.status == "completed"
        print("✅ AgentResponseFormatter works correctly")
        
        # Test AgentErrorHandler
        error_handler = base_module.AgentErrorHandler()
        error_response = error_handler.handle_agent_error(
            agent_id="test-agent",
            error=Exception("Test error"),
            operation="test operation",
            user_id="test-user"
        )
        
        assert error_response.agent_id == "test-agent"
        assert error_response.status == "failed"
        print("✅ AgentErrorHandler works correctly")
        
        # Test AgentPerformanceTracker
        tracker = base_module.AgentPerformanceTracker()
        tracker.start_tracking()
        import time
        time.sleep(0.1)
        processing_time = tracker.get_processing_time()
        assert processing_time > 0.09
        print("✅ AgentPerformanceTracker works correctly")
        
        print("✅ All base utilities work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Base utilities test failed: {e}")
        return False

def test_router_structure():
    """Test router structure."""
    print("\n🔍 Testing Router Structure...")
    
    try:
        # Import agents_new
        agents_new_path = "services/api_gateway/routes/agents_new.py"
        spec = importlib.util.spec_from_file_location("agents_new", agents_new_path)
        agents_new_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agents_new_module)
        
        # Test that agents_router exists
        agents_router = agents_new_module.agents_router
        assert agents_router is not None
        assert hasattr(agents_router, 'routes')
        print("✅ agents_router exists and has routes")
        
        # Test that individual routers are included
        routes = agents_router.routes
        assert len(routes) > 0
        print(f"✅ Router has {len(routes)} routes")
        
        # Check for health and status endpoints
        route_paths = []
        for route in routes:
            if hasattr(route, 'path'):
                route_paths.append(route.path)
        
        print(f"Route paths: {route_paths}")
        
        if "/health" in route_paths:
            print("✅ Health endpoint found")
        else:
            print("⚠️ Health endpoint not found")
            
        if "/status" in route_paths:
            print("✅ Status endpoint found")
        else:
            print("⚠️ Status endpoint not found")
        
        print("✅ Router structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ Router structure test failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility."""
    print("\n🔍 Testing Backward Compatibility...")
    
    try:
        # Import the main agents module
        agents_path = "services/api_gateway/routes/agents.py"
        spec = importlib.util.spec_from_file_location("agents", agents_path)
        agents_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agents_module)
        
        # Test that router exists
        assert hasattr(agents_module, 'router')
        print("✅ Legacy router exists")
        
        # Test that agent_handler exists
        assert hasattr(agents_module, 'agent_handler')
        print("✅ Legacy agent_handler exists")
        
        # Test that set_dependencies exists
        assert hasattr(agents_module, 'set_dependencies')
        print("✅ Legacy set_dependencies exists")
        
        print("✅ Backward compatibility test passed")
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🚀 Starting Agent Restructuring Verification...")
    print("=" * 60)
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    # Run all tests
    tests = [
        test_agent_modules,
        test_base_utilities,
        test_router_structure,
        test_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent restructuring is complete and functional.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 