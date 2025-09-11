#!/usr/bin/env python3
"""
Setup Default Users Script for SarvanOM

This script creates default user and admin accounts for development and testing.
Run this script after setting up the database to create initial users.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.repositories.database.user_repository import UserRepository
from shared.core.auth.password_hasher import PasswordHasher
import structlog

logger = structlog.get_logger(__name__)

# Default credentials
DEFAULT_USERS = [
    {
        "username": "user",
        "email": "user@sarvanom.dev",
        "password": "UserPass123!",
        "full_name": "Default User",
        "role": "user"
    },
    {
        "username": "admin",
        "email": "admin@sarvanom.dev", 
        "password": "AdminPass123!",
        "full_name": "Default Admin",
        "role": "admin"
    },
    {
        "username": "expert",
        "email": "expert@sarvanom.dev",
        "password": "ExpertPass123!",
        "full_name": "Default Expert",
        "role": "expert"
    }
]

async def setup_default_users():
    """Create default users in the database."""
    try:
        user_repository = UserRepository()
        password_hasher = PasswordHasher()
        
        logger.info("Starting default user setup...")
        
        for user_data in DEFAULT_USERS:
            try:
                # Check if user already exists
                existing_user = await user_repository.get_by_username(user_data["username"])
                if existing_user:
                    logger.info(f"User '{user_data['username']}' already exists, skipping...")
                    continue
                
                # Create the user
                user = await user_repository.create_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                
                logger.info(f"Created user: {user_data['username']} (role: {user_data['role']})")
                
            except Exception as e:
                logger.error(f"Failed to create user '{user_data['username']}': {e}")
                continue
        
        logger.info("Default user setup completed successfully!")
        
        # Print credentials for easy access
        print("\n" + "="*60)
        print("🎉 DEFAULT USERS CREATED SUCCESSFULLY!")
        print("="*60)
        print("\n📋 LOGIN CREDENTIALS:")
        print("-" * 30)
        
        for user_data in DEFAULT_USERS:
            print(f"👤 {user_data['role'].upper()}:")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Email: {user_data['email']}")
            print()
        
        print("🌐 ACCESS POINTS:")
        print("-" * 15)
        print("Frontend: http://localhost:3000")
        print("Backend:  http://localhost:8005")
        print("Login:    http://localhost:3000/login")
        print("Register: http://localhost:3000/register")
        print()
        print("⚠️  IMPORTANT: Change these passwords in production!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Failed to setup default users: {e}")
        raise

async def main():
    """Main function."""
    try:
        await setup_default_users()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
