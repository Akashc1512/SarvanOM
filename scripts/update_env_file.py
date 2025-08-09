#!/usr/bin/env python3
"""
Update .env file with required environment variables for development.

This script ensures all required environment variables are set in the .env file.
"""

import os
import re


def update_env_file():
    """Update .env file with required variables."""

    env_file = ".env"

    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found!")
        return False

    # Read current .env file
    with open(env_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Required variables for development
    required_vars = {
        "APP_ENV": "development",
        "DATABASE_URL": "postgresql://postgres:password@localhost:5432/sarvanom",
        "REDIS_URL": "redis://localhost:6379/0",
        "MEILISEARCH_URL": "http://localhost:7700",
        "ARANGODB_URL": "http://localhost:8529",
        "JWT_SECRET_KEY": "your-super-secret-jwt-key-here-minimum-32-characters-for-development-only",
    }

    # Update or add each required variable
    updated = False
    for var_name, var_value in required_vars.items():
        # Check if variable already exists
        pattern = rf"^{var_name}=.*$"
        if re.search(pattern, content, re.MULTILINE):
            # Variable exists, update it if it's commented or has a placeholder
            old_pattern = rf"^{var_name}=.*$"
            new_line = f"{var_name}={var_value}"
            if re.sub(old_pattern, new_line, content, flags=re.MULTILINE) != content:
                content = re.sub(old_pattern, new_line, content, flags=re.MULTILINE)
                updated = True
                print(f"✅ Updated {var_name}")
        else:
            # Variable doesn't exist, add it
            # Find a good place to add it (after the core settings section)
            if "APP_ENV=" in content:
                # Add after APP_ENV
                content = re.sub(
                    rf"^(APP_ENV=.*)$",
                    rf"\1\n{var_name}={var_value}",
                    content,
                    flags=re.MULTILINE,
                )
            else:
                # Add at the beginning
                content = f"{var_name}={var_value}\n{content}"
            updated = True
            print(f"✅ Added {var_name}")

    # Write updated content
    if updated:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ Updated {env_file} with required variables")
        return True
    else:
        print(f"\n✅ {env_file} already has all required variables")
        return True


if __name__ == "__main__":
    update_env_file()
