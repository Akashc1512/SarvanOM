#!/usr/bin/env python3
"""
Import validation script for the MAANG-level refactor.
Checks that all imports resolve to actual files/modules.
"""

import os
import sys
import importlib
import ast
from pathlib import Path
from typing import List, Dict, Set


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and other cache directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def extract_imports(file_path: str) -> List[str]:
    """Extract all import statements from a Python file."""
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return imports


def validate_import(import_name: str) -> bool:
    """Validate that an import can be resolved."""
    try:
        # Handle relative imports
        if import_name.startswith("."):
            return True  # Skip relative imports for now

        # Try to import the module
        importlib.import_module(import_name)
        return True
    except ImportError:
        # Check if it's a file path
        if import_name.startswith("shared.core.") or import_name.startswith(
            "services."
        ):
            # Convert to file path
            parts = import_name.split(".")
            if parts[0] == "shared" and parts[1] == "core":
                if len(parts) >= 3:
                    # Check if the file exists
                    file_path = f"shared/core/{'/'.join(parts[2:])}.py"
                    if os.path.exists(file_path):
                        return True
            elif parts[0] == "services":
                if len(parts) >= 2:
                    # Check if the file exists
                    file_path = f"services/{'/'.join(parts[1:])}.py"
                    if os.path.exists(file_path):
                        return True

        return False
    except Exception:
        return False


def main():
    """Main validation function."""
    print("🔍 Validating imports after MAANG-level refactor...")
    print("=" * 60)

    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())

    # Directories to check
    directories = ["services", "shared", "tests"]

    all_issues = []

    for directory in directories:
        if not os.path.exists(directory):
            print(f"⚠️  Directory {directory} not found, skipping...")
            continue

        print(f"\n📁 Checking {directory}/...")
        python_files = find_python_files(directory)

        for file_path in python_files:
            print(f"  📄 {file_path}")
            imports = extract_imports(file_path)

            for import_name in imports:
                if not validate_import(import_name):
                    issue = f"❌ {file_path}: {import_name}"
                    all_issues.append(issue)
                    print(f"    {issue}")

    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    if all_issues:
        print(f"❌ Found {len(all_issues)} import issues:")
        for issue in all_issues:
            print(f"  {issue}")
        return 1
    else:
        print("✅ All imports validated successfully!")
        return 0


if __name__ == "__main__":
    exit(main())
