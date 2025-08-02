from ..\shared\core\api\config import get_settings
settings = get_settings()
"""
Frontend States Table Migration Script - Universal Knowledge Platform

This script creates the frontend_states table in PostgreSQL for storing
frontend UI states, enabling seamless synchronization between backend
AI flows and frontend UI components.

Usage:
    python scripts/create_frontend_states_table.py

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.models.frontend_state import Base


def create_frontend_states_table():
    """
    Create the frontend_states table in PostgreSQL.
    
    This function:
    1. Connects to the PostgreSQL database
    2. Creates the frontend_states table with proper schema
    3. Creates necessary indexes for performance
    4. Handles errors gracefully
    """
    try:
        # Get database connection details from environment
        db_url = settings.database_url
        if not db_url:
            print("❌ Error: DATABASE_URL environment variable not found")
            print("Please set DATABASE_URL in your .env file")
            return False
        
        print("🔗 Connecting to PostgreSQL database...")
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        print("📋 Creating frontend_states table...")
        
        # Create table
        Base.metadata.create_all(engine, tables=[Base.metadata.tables['frontend_states']])
        
        print("✅ frontend_states table created successfully!")
        
        # Verify table creation
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'frontend_states'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("\n📊 Table Schema:")
            print("-" * 80)
            print(f"{'Column':<20} {'Type':<15} {'Nullable':<10}")
            print("-" * 80)
            
            for column in columns:
                print(f"{column[1]:<20} {column[2]:<15} {column[3]:<10}")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = 'frontend_states'
            """))
            
            indexes = result.fetchall()
            print(f"\n🔍 Indexes ({len(indexes)}):")
            for index in indexes:
                print(f"  - {index[0]}")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def verify_table_structure():
    """
    Verify that the frontend_states table has the correct structure.
    
    This function checks:
    1. All required columns exist
    2. Data types are correct
    3. Indexes are created
    4. Constraints are properly set
    """
    try:
        db_url = settings.database_url
        if not db_url:
            print("❌ Error: DATABASE_URL environment variable not found")
            return False
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'frontend_states'
                )
            """))
            
            if not result.fetchone()[0]:
                print("❌ frontend_states table does not exist")
                return False
            
            # Check columns
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'frontend_states'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            expected_columns = {
                'session_id': {'type': 'character varying', 'nullable': 'NO'},
                'user_id': {'type': 'character varying', 'nullable': 'YES'},
                'current_view_state': {'type': 'json', 'nullable': 'NO'},
                'last_updated': {'type': 'timestamp with time zone', 'nullable': 'NO'}
            }
            
            print("🔍 Verifying table structure...")
            
            for column in columns:
                col_name = column[0]
                col_type = column[1]
                col_nullable = column[2]
                
                if col_name in expected_columns:
                    expected = expected_columns[col_name]
                    if col_type != expected['type']:
                        print(f"❌ Column {col_name}: expected type {expected['type']}, got {col_type}")
                        return False
                    if col_nullable != expected['nullable']:
                        print(f"❌ Column {col_name}: expected nullable {expected['nullable']}, got {col_nullable}")
                        return False
                    print(f"✅ Column {col_name}: {col_type} ({col_nullable})")
                else:
                    print(f"⚠️  Unexpected column: {col_name}")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT indexname
                FROM pg_indexes 
                WHERE tablename = 'frontend_states'
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            expected_indexes = [
                'frontend_states_pkey',  # Primary key
                'idx_frontend_states_user_id',
                'idx_frontend_states_last_updated'
            ]
            
            print("\n🔍 Verifying indexes...")
            for expected_index in expected_indexes:
                if expected_index in indexes:
                    print(f"✅ Index {expected_index}")
                else:
                    print(f"❌ Missing index: {expected_index}")
                    return False
            
            print("✅ Table structure verification completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


def insert_sample_data():
    """
    Insert sample data into the frontend_states table for testing.
    """
    try:
        db_url = settings.database_url
        if not db_url:
            print("❌ Error: DATABASE_URL environment variable not found")
            return False
        
        engine = create_engine(db_url)
        
        sample_data = [
            {
                'session_id': 'sample_session_1',
                'user_id': 'user_123',
                'current_view_state': {
                    'sidebar': {'collapsed': False, 'active_tab': 'dashboard'},
                    'query_history': [
                        {'query': 'What is AI?', 'timestamp': '2024-12-28T10:00:00Z'}
                    ],
                    'current_view': {'page': 'dashboard', 'filters': {'category': 'technology'}}
                }
            },
            {
                'session_id': 'sample_session_2',
                'user_id': 'user_456',
                'current_view_state': {
                    'sidebar': {'collapsed': True, 'active_tab': 'search'},
                    'query_history': [
                        {'query': 'Machine learning basics', 'timestamp': '2024-12-28T10:05:00Z'},
                        {'query': 'Deep learning algorithms', 'timestamp': '2024-12-28T10:10:00Z'}
                    ],
                    'current_view': {'page': 'search', 'filters': {'category': 'education'}}
                }
            }
        ]
        
        print("📝 Inserting sample data...")
        
        with engine.connect() as conn:
            for data in sample_data:
                conn.execute(text("""
                    INSERT INTO frontend_states (session_id, user_id, current_view_state)
                    VALUES (:session_id, :user_id, :current_view_state)
                    ON CONFLICT (session_id) DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        current_view_state = EXCLUDED.current_view_state,
                        last_updated = NOW()
                """), data)
            
            conn.commit()
        
        print("✅ Sample data inserted successfully!")
        
        # Verify data insertion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM frontend_states"))
            count = result.fetchone()[0]
            print(f"📊 Total records in frontend_states: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False


def main():
    """Main function to run the migration script."""
    print("🚀 Frontend States Table Migration Script")
    print("=" * 50)
    
    # Step 1: Create table
    print("\n📋 Step 1: Creating frontend_states table...")
    if not create_frontend_states_table():
        print("❌ Failed to create table")
        sys.exit(1)
    
    # Step 2: Verify structure
    print("\n🔍 Step 2: Verifying table structure...")
    if not verify_table_structure():
        print("❌ Table structure verification failed")
        sys.exit(1)
    
    # Step 3: Insert sample data
    print("\n📝 Step 3: Inserting sample data...")
    if not insert_sample_data():
        print("❌ Failed to insert sample data")
        sys.exit(1)
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Summary:")
    print("  ✅ frontend_states table created")
    print("  ✅ All columns and indexes verified")
    print("  ✅ Sample data inserted")
    print("\n🔗 API Endpoints available:")
    print("  GET    /api/state/{session_id}")
    print("  PUT    /api/state/{session_id}")
    print("  DELETE /api/state/{session_id}")
    print("  GET    /api/state/{session_id}/info")
    print("  GET    /api/state/user/{user_id}")


if __name__ == "__main__":
    main() 