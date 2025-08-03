#!/usr/bin/env python3
"""
Setup Development Credentials for Universal Knowledge Platform
Creates specific user and admin accounts with easy-to-remember passwords for development and testing.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from passlib.context import CryptContext

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service.user_management import UserManager, UserCreate, UserRole

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def setup_dev_credentials():
    """Setup development and testing credentials."""
    print("🔐 Setting up Development Credentials for Universal Knowledge Platform")
    print("=" * 70)
    
    # Define development users with easy-to-remember credentials
    dev_users = [
        {
            "username": "admin",
            "email": "admin@sarvanom.ai",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "full_name": "Development Administrator",
            "description": "Full admin access for development"
        },
        {
            "username": "user",
            "email": "user@sarvanom.ai", 
            "password": "user123",
            "role": UserRole.USER,
            "full_name": "Development User",
            "description": "Regular user for testing"
        },
        {
            "username": "testadmin",
            "email": "testadmin@sarvanom.ai",
            "password": "testadmin123",
            "role": UserRole.ADMIN,
            "full_name": "Test Administrator",
            "description": "Admin account for testing"
        },
        {
            "username": "testuser",
            "email": "testuser@sarvanom.ai",
            "password": "testuser123", 
            "role": UserRole.USER,
            "full_name": "Test User",
            "description": "User account for testing"
        },
        {
            "username": "dev",
            "email": "dev@sarvanom.ai",
            "password": "dev123",
            "role": UserRole.ADMIN,
            "full_name": "Developer Account",
            "description": "Developer account with admin privileges"
        },
        {
            "username": "demo",
            "email": "demo@sarvanom.ai",
            "password": "demo123",
            "role": UserRole.USER,
            "full_name": "Demo User",
            "description": "Demo account for presentations"
        }
    ]
    
    # Load existing users
    users_file = Path("data/users.json")
    existing_users = {}
    
    if users_file.exists():
        try:
            with open(users_file, "r") as f:
                existing_users = json.load(f)
            print(f"📋 Found {len(existing_users)} existing users")
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing users: {e}")
    
    # Create new users or update existing ones
    updated_users = {}
    created_count = 0
    updated_count = 0
    
    for user_data in dev_users:
        username = user_data["username"]
        hashed_password = hash_password(user_data["password"])
        
        user_entry = {
            "username": username,
            "email": user_data["email"],
            "hashed_password": hashed_password,
            "role": user_data["role"],
            "full_name": user_data["full_name"],
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        if username in existing_users:
            # Update existing user
            existing_user = existing_users[username]
            user_entry["created_at"] = existing_user.get("created_at", datetime.now().isoformat())
            user_entry["last_login"] = existing_user.get("last_login")
            updated_users[username] = user_entry
            updated_count += 1
            print(f"🔄 Updated user: {username}")
        else:
            # Create new user
            updated_users[username] = user_entry
            created_count += 1
            print(f"✅ Created user: {username}")
    
    # Save updated users
    try:
        with open(users_file, "w") as f:
            json.dump(updated_users, f, indent=2)
        print(f"\n💾 Saved {len(updated_users)} users to {users_file}")
    except Exception as e:
        print(f"❌ Error saving users: {e}")
        return False
    
    # Print credentials summary
    print("\n" + "=" * 70)
    print("🔑 DEVELOPMENT CREDENTIALS")
    print("=" * 70)
    print("⚠️  WARNING: These are development credentials only!")
    print("   Do NOT use these passwords in production!")
    print("=" * 70)
    
    for user_data in dev_users:
        username = user_data["username"]
        password = user_data["password"]
        role = user_data["role"]
        description = user_data["description"]
        
        print(f"\n👤 {username.upper()}")
        print(f"   Role: {role}")
        print(f"   Description: {description}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {user_data['email']}")
    
    print("\n" + "=" * 70)
    print("📡 LOGIN ENDPOINTS")
    print("=" * 70)
    print("Frontend Login: http://localhost:3000/login")
    print("API Login: POST http://localhost:8002/auth/login")
    print("\n🔧 ADMIN ENDPOINTS")
    print("Admin Dashboard: http://localhost:3000/admin/dashboard")
    print("User Management: http://localhost:3000/admin/users")
    
    print("\n" + "=" * 70)
    print("🧪 TESTING CREDENTIALS")
    print("=" * 70)
    print("For automated testing, use:")
    print("  Username: testuser")
    print("  Password: testuser123")
    print("\nFor admin testing:")
    print("  Username: testadmin") 
    print("  Password: testadmin123")
    
    print("\n" + "=" * 70)
    print("✅ Development credentials setup complete!")
    print(f"   Created: {created_count} new users")
    print(f"   Updated: {updated_count} existing users")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = setup_dev_credentials()
        if success:
            print("\n🎉 Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1) 