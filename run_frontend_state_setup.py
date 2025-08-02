"""
Frontend State Setup and Test Script - Universal Knowledge Platform

This script sets up the frontend state database table and runs integration tests
to verify the complete frontend session persistence implementation.

Usage:
    python run_frontend_state_setup.py

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment configuration...")
    
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True


def create_database_table():
    """Create the frontend_states database table."""
    print("\n📋 Creating frontend_states database table...")
    
    try:
        # Run the table creation script
        result = subprocess.run([
            sys.executable, "scripts/create_frontend_states_table.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database table created successfully")
            return True
        else:
            print(f"❌ Failed to create database table: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Table creation script not found: scripts/create_frontend_states_table.py")
        return False
    except Exception as e:
        print(f"❌ Error creating database table: {e}")
        return False


def run_integration_tests():
    """Run the frontend state integration tests."""
    print("\n🧪 Running frontend state integration tests...")
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_frontend_state_postgres.py", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All integration tests passed")
            return True
        else:
            print(f"❌ Some tests failed: {result.stdout}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def test_api_endpoints():
    """Test the API endpoints manually."""
    print("\n🌐 Testing API endpoints...")
    
    try:
        # Import the test client
        from test_frontend_state_postgres import client
        
        # Test data
        session_id = "manual_test_session_123"
        test_state = {
            "sidebar": {"collapsed": False, "active_tab": "dashboard"},
            "current_view": {"page": "dashboard"},
            "user_preferences": {"theme": "dark"}
        }
        
        # Test PUT endpoint
        print("  Testing PUT /api/state/{session_id}...")
        response = client.put(f"/api/state/{session_id}", json=test_state)
        if response.status_code == 200:
            print("  ✅ PUT endpoint working")
        else:
            print(f"  ❌ PUT endpoint failed: {response.status_code}")
            return False
        
        # Test GET endpoint
        print("  Testing GET /api/state/{session_id}...")
        response = client.get(f"/api/state/{session_id}")
        if response.status_code == 200:
            data = response.json()
            if data["success"] and data["data"]["current_view_state"] == test_state:
                print("  ✅ GET endpoint working")
            else:
                print("  ❌ GET endpoint returned unexpected data")
                return False
        else:
            print(f"  ❌ GET endpoint failed: {response.status_code}")
            return False
        
        # Test DELETE endpoint
        print("  Testing DELETE /api/state/{session_id}...")
        response = client.delete(f"/api/state/{session_id}")
        if response.status_code == 200:
            print("  ✅ DELETE endpoint working")
        else:
            print(f"  ❌ DELETE endpoint failed: {response.status_code}")
            return False
        
        print("✅ All API endpoints working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False


def main():
    """Main function to run the complete setup and test process."""
    print("🚀 Frontend State Setup and Test Script")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Create database table
    if not create_database_table():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Step 3: Run integration tests
    if not run_integration_tests():
        print("❌ Integration tests failed")
        sys.exit(1)
    
    # Step 4: Test API endpoints
    if not test_api_endpoints():
        print("❌ API endpoint tests failed")
        sys.exit(1)
    
    print("\n🎉 Frontend State Implementation Complete!")
    print("\n📋 Summary:")
    print("  ✅ Database table created")
    print("  ✅ Integration tests passed")
    print("  ✅ API endpoints working")
    print("\n🔗 Available API Endpoints:")
    print("  GET    /api/state/{session_id} - Get current state")
    print("  PUT    /api/state/{session_id} - Update state")
    print("  DELETE /api/state/{session_id} - Clear state")
    print("  GET    /api/state/{session_id}/info - Get session info")
    print("  GET    /api/state/user/{user_id} - Get all states for user")
    print("  PUT    /api/state/{session_id}/value/{key} - Set specific value")
    print("  GET    /api/state/{session_id}/value/{key} - Get specific value")
    print("  PUT    /api/state/{session_id}/merge - Merge state")
    print("\n💡 Usage Example:")
    print("  # Save UI state")
    print("  curl -X PUT http://localhost:8000/api/state/my_session \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"sidebar\": {\"collapsed\": false}}'")
    print("\n  # Retrieve UI state")
    print("  curl http://localhost:8000/api/state/my_session")


if __name__ == "__main__":
    main() 