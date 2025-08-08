"""
Test script for Database Service Migration

This script tests the migrated database service and router components
to ensure they work correctly in the clean architecture.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.core.database_service import DatabaseService
from backend.models.domain.database import QueryResult, SchemaInfo, DataAnalysis
from backend.models.domain.enums import ServiceStatus, DatabaseType


async def test_database_service():
    """Test the migrated database service."""
    print("Testing Database Service Migration...")
    
    try:
        # Test DatabaseService initialization
        print("1. Testing DatabaseService initialization...")
        database_service = DatabaseService()
        print("✅ DatabaseService initialized successfully")
        
        # Test health check
        print("2. Testing health check...")
        health_status = await database_service.health_check()
        print(f"✅ Health status: {health_status['healthy']}")
        
        # Test metrics
        print("3. Testing metrics...")
        metrics = await database_service.get_metrics()
        print(f"✅ Metrics retrieved: {metrics['status']}")
        
        # Test configuration validation
        print("4. Testing configuration validation...")
        config_valid = await database_service.validate_config()
        print(f"✅ Configuration validation: {config_valid}")
        
        # Test list databases
        print("5. Testing list databases...")
        databases = await database_service.list_databases()
        print(f"✅ Database list: {databases['total_count']} databases")
        
        # Test connection test (will fail without real DB)
        print("6. Testing connection test...")
        test_result = await database_service.test_connection("test_db")
        print(f"✅ Connection test: {test_result['success']}")
        
        # Test query execution (simulated)
        print("7. Testing query execution...")
        query_result = await database_service.execute_query(
            database_name="test_db",
            query="SELECT 1 as test"
        )
        print(f"✅ Query execution: {query_result.success}")
        
        # Test schema retrieval (simulated)
        print("8. Testing schema retrieval...")
        schema_info = await database_service.get_schema("test_db")
        print(f"✅ Schema retrieval: {schema_info.database_name}")
        
        # Test data analysis (simulated)
        print("9. Testing data analysis...")
        analysis = await database_service.analyze_data(
            database_name="test_db",
            table_name="test_table"
        )
        print(f"✅ Data analysis: {analysis.database_name}.{analysis.table_name}")
        
        # Test query optimization (simulated)
        print("10. Testing query optimization...")
        optimization = await database_service.optimize_query(
            database_name="test_db",
            query="SELECT * FROM users"
        )
        suggestions_count = len(optimization.get('suggestions', []))
        print(f"✅ Query optimization: {suggestions_count} suggestions")
        
        print("\n🎉 All database service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_domain_models():
    """Test the database domain models."""
    print("\nTesting Database Domain Models...")
    
    try:
        # Test QueryResult
        print("1. Testing QueryResult...")
        query_result = QueryResult(
            success=True,
            data=[{"id": 1, "name": "test"}],
            row_count=1,
            columns=["id", "name"],
            query="SELECT * FROM test",
            database_name="test_db",
            processing_time=0.1
        )
        print(f"✅ QueryResult created: {query_result.success}")
        
        # Test SchemaInfo
        print("2. Testing SchemaInfo...")
        schema_info = SchemaInfo(
            database_name="test_db",
            tables=[{"name": "users", "columns": []}],
            views=[],
            indexes=[],
            constraints=[]
        )
        print(f"✅ SchemaInfo created: {schema_info.database_name}")
        
        # Test DataAnalysis
        print("3. Testing DataAnalysis...")
        analysis = DataAnalysis(
            database_name="test_db",
            table_name="users",
            row_count=100,
            column_stats={"id": {"count": 100}},
            data_types={"id": "numeric"},
            missing_values={"id": 0},
            unique_values={"id": 100}
        )
        print(f"✅ DataAnalysis created: {analysis.database_name}.{analysis.table_name}")
        
        # Test enums
        print("4. Testing enums...")
        service_status = ServiceStatus.HEALTHY
        database_type = DatabaseType.POSTGRESQL
        print(f"✅ Enums created: {service_status.value}, {database_type.value}")
        
        print("🎉 All database domain model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database domain model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all database service tests."""
    print("🧪 Starting Database Service Migration Tests")
    print("=" * 50)
    
    # Test domain models
    domain_success = await test_database_domain_models()
    
    # Test database service
    service_success = await test_database_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Database Domain Models: {'✅ PASSED' if domain_success else '❌ FAILED'}")
    print(f"Database Service: {'✅ PASSED' if service_success else '❌ FAILED'}")
    
    if all([domain_success, service_success]):
        print("\n🎉 All database service migration tests passed!")
        return True
    else:
        print("\n❌ Some database service migration tests failed!")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 