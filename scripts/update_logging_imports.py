#!/usr/bin/env python3
"""
Script to update all services from old logging pattern to unified logging.

This script finds all files using `logger = logging.getLogger(__name__)` and
replaces them with the unified logging import pattern.
"""

import os
import re
from pathlib import Path


def update_logging_import(file_path):
    """Update a single file to use unified logging."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file already uses unified logging
        if "from shared.core.unified_logging import" in content:
            print(f"✅ {file_path} already uses unified logging")
            return False

        # Check if file uses old logging pattern
        if "logger = logging.getLogger(__name__)" not in content:
            print(f"⏭️  {file_path} doesn't use standard logging pattern")
            return False

        # Replace old logging pattern
        old_pattern = r"logger = logging\.getLogger\(__name__\)"

        # Add unified logging import after other imports
        import_pattern = r"(import logging\s*\n)"
        unified_import = r"\1from shared.core.unified_logging import get_logger\n"

        # First add the import
        if "import logging" in content:
            content = re.sub(import_pattern, unified_import, content)
        else:
            # Add import at the top after existing imports
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_pos = i + 1
                elif line.strip() == "" and i > insert_pos:
                    break

            lines.insert(
                insert_pos, "from shared.core.unified_logging import get_logger"
            )
            content = "\n".join(lines)

        # Replace logger initialization
        content = re.sub(old_pattern, "logger = get_logger(__name__)", content)

        # Write updated content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Updated {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def find_and_update_files():
    """Find and update all Python files with old logging pattern."""
    services_dir = Path("services")
    if not services_dir.exists():
        print("❌ Services directory not found")
        return

    updated_count = 0
    total_count = 0

    # Find all Python files in services directory
    for py_file in services_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        total_count += 1
        if update_logging_import(py_file):
            updated_count += 1

    print(f"\n📊 Summary:")
    print(f"   Total files checked: {total_count}")
    print(f"   Files updated: {updated_count}")
    print(f"   Files already using unified logging: {total_count - updated_count}")


if __name__ == "__main__":
    print("🔄 Updating logging imports to unified system...")
    find_and_update_files()
    print("✅ Logging import update complete!")
