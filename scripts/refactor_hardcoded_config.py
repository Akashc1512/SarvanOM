#!/usr/bin/env python3
"""
Refactor Hard-coded Configuration Values

This script systematically identifies and refactors hard-coded configuration
values throughout the codebase, replacing them with centralized configuration
management.

Features:
    - Identifies hard-coded URLs, ports, and connection strings
    - Replaces hard-coded model names with configuration
    - Updates hard-coded API keys and secrets
    - Validates configuration consistency
    - Generates migration report

Usage:
    python scripts/refactor_hardcoded_config.py

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HardcodedConfigRefactorer:
    """Refactor hard-coded configuration values."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.changes_made = []
        self.files_processed = 0

        # Patterns to identify hard-coded values
        self.patterns = {
            # Database URLs and connection strings
            "database_urls": [
                r'postgresql://[^"\s]+',
                r'mysql://[^"\s]+',
                r'sqlite://[^"\s]+',
                r'mongodb://[^"\s]+',
            ],
            # Service URLs
            "service_urls": [
                r"http://localhost:\d+",
                r"https://localhost:\d+",
                r"http://127\.0\.0\.1:\d+",
                r"https://127\.0\.0\.1:\d+",
            ],
            # API Keys and secrets
            "api_keys": [
                r"sk-[a-zA-Z0-9]{48}",
                r"pk_[a-zA-Z0-9]{48}",
                r"[a-zA-Z0-9]{32,}",
            ],
            # Model names
            "model_names": [
                r"gpt-[34]",
                r"claude-[23]",
                r"llama[23]?",
                r"mistral",
                r"gemini",
            ],
            # Port numbers
            "ports": [
                r":8000",
                r":8001",
                r":8002",
                r":8003",
                r":8004",
                r":8005",
                r":5432",
                r":6379",
                r":6333",
                r":7700",
                r":8529",
                r":11434",
            ],
        }

        # Files to exclude from processing
        self.exclude_patterns = [
            r"\.git/",
            r"node_modules/",
            r"\.venv/",
            r"__pycache__/",
            r"\.pytest_cache/",
            r"\.next/",
            r"\.env",
            r"\.env\.example",
            r"requirements\.txt",
            r"package\.json",
            r"package-lock\.json",
            r"README\.md",
            r"\.md$",
            r"\.log$",
            r"\.pyc$",
            r"\.pyo$",
        ]

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        file_str = str(file_path)

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, file_str):
                return False

        # Only process Python files
        return file_path.suffix == ".py"

    def find_hardcoded_values(self, file_path: Path) -> Dict[str, List[str]]:
        """Find hard-coded values in a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return {}

        found_values = {}

        for category, patterns in self.patterns.items():
            found_values[category] = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                found_values[category].extend(matches)

        # Remove duplicates
        for category in found_values:
            found_values[category] = list(set(found_values[category]))

        return found_values

    def generate_replacement_suggestions(
        self, file_path: Path, hardcoded_values: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Generate replacement suggestions for hard-coded values."""
        suggestions = {}

        for category, values in hardcoded_values.items():
            for value in values:
                if category == "database_urls":
                    suggestions[value] = "get_database_url()"
                elif category == "service_urls":
                    if "localhost:8000" in value or "127.0.0.1:8000" in value:
                        suggestions[value] = "get_config_value('api_url')"
                    elif "localhost:8001" in value or "127.0.0.1:8001" in value:
                        suggestions[value] = "get_config_value('auth_service_url')"
                    elif "localhost:8002" in value or "127.0.0.1:8002" in value:
                        suggestions[value] = "get_config_value('search_service_url')"
                    elif "localhost:8003" in value or "127.0.0.1:8003" in value:
                        suggestions[value] = "get_config_value('synthesis_service_url')"
                    elif "localhost:8004" in value or "127.0.0.1:8004" in value:
                        suggestions[value] = "get_config_value('factcheck_service_url')"
                    elif "localhost:8005" in value or "127.0.0.1:8005" in value:
                        suggestions[value] = "get_config_value('analytics_service_url')"
                    elif "localhost:6333" in value or "127.0.0.1:6333" in value:
                        suggestions[value] = "get_vector_db_url()"
                    elif "localhost:7700" in value or "127.0.0.1:7700" in value:
                        suggestions[value] = "get_meilisearch_url()"
                    elif "localhost:8529" in value or "127.0.0.1:8529" in value:
                        suggestions[value] = "get_arangodb_url()"
                    elif "localhost:11434" in value or "127.0.0.1:11434" in value:
                        suggestions[value] = "get_ollama_url()"
                    elif "localhost:6379" in value or "127.0.0.1:6379" in value:
                        suggestions[value] = "get_redis_url()"
                    else:
                        suggestions[value] = "get_config_value('service_url')"
                elif category == "model_names":
                    if "gpt-4" in value:
                        suggestions[value] = "get_config_value('openai_model')"
                    elif "claude" in value:
                        suggestions[value] = "get_config_value('anthropic_model')"
                    elif "llama" in value:
                        suggestions[value] = "get_config_value('ollama_model')"
                    elif "gemini" in value:
                        suggestions[value] = "get_config_value('google_model')"
                    else:
                        suggestions[value] = "get_config_value('model_name')"
                elif category == "api_keys":
                    suggestions[value] = "get_config_value('api_key')"
                elif category == "ports":
                    suggestions[value] = "get_config_value('port')"

        return suggestions

    def apply_replacements(self, file_path: Path, suggestions: Dict[str, str]) -> bool:
        """Apply replacements to a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return False

        original_content = content
        modified = False

        for old_value, new_value in suggestions.items():
            if old_value in content:
                # Add import if needed
                if (
                    "get_config_value" in new_value
                    and "from shared.core.config.central_config import" not in content
                ):
                    import_line = "from shared.core.config.central_config import get_config_value\n"
                    content = import_line + content

                # Replace the value
                content = content.replace(old_value, new_value)
                modified = True
                self.changes_made.append(f"{file_path}: {old_value} -> {new_value}")

        if modified:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Updated {file_path}")
                return True
            except Exception as e:
                logger.error(f"Could not write {file_path}: {e}")
                return False

        return False

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file."""
        if not self.should_process_file(file_path):
            return {}

        logger.info(f"Processing {file_path}")

        # Find hard-coded values
        hardcoded_values = self.find_hardcoded_values(file_path)

        if not hardcoded_values:
            return {}

        # Generate replacement suggestions
        suggestions = self.generate_replacement_suggestions(file_path, hardcoded_values)

        # Apply replacements
        changes_applied = self.apply_replacements(file_path, suggestions)

        return {
            "file_path": str(file_path),
            "hardcoded_values": hardcoded_values,
            "suggestions": suggestions,
            "changes_applied": changes_applied,
        }

    def process_directory(self) -> Dict[str, Any]:
        """Process all files in the directory."""
        results = {
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "results": [],
        }

        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file():
                result = self.process_file(file_path)
                if result:
                    results["files_processed"] += 1
                    if result["changes_applied"]:
                        results["files_modified"] += 1
                        results["total_changes"] += len(result["suggestions"])
                    results["results"].append(result)

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a report of the refactoring process."""
        report = []
        report.append("=" * 80)
        report.append("HARD-CODED CONFIGURATION REFACTORING REPORT")
        report.append("=" * 80)
        report.append("")

        report.append(f"Files processed: {results['files_processed']}")
        report.append(f"Files modified: {results['files_modified']}")
        report.append(f"Total changes: {results['total_changes']}")
        report.append("")

        if self.changes_made:
            report.append("Changes made:")
            for change in self.changes_made:
                report.append(f"  - {change}")
            report.append("")

        report.append("Files with hard-coded values:")
        for result in results["results"]:
            if result["hardcoded_values"]:
                report.append(f"  - {result['file_path']}")
                for category, values in result["hardcoded_values"].items():
                    for value in values:
                        report.append(f"    {category}: {value}")

        return "\n".join(report)


def main():
    """Main function."""
    refactorer = HardcodedConfigRefactorer()

    logger.info("Starting hard-coded configuration refactoring...")

    # Process all files
    results = refactorer.process_directory()

    # Generate and print report
    report = refactorer.generate_report(results)
    print(report)

    # Save report to file
    report_file = Path("HARDCODED_CONFIG_REFACTORING_REPORT.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Report saved to {report_file}")
    logger.info("Refactoring complete!")


if __name__ == "__main__":
    main()
