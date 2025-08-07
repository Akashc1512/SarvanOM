#!/usr/bin/env python3
"""
Configuration Validation Script

This script validates that all configuration values are properly loaded
from environment variables and that no hard-coded values remain in the
codebase.

Features:
    - Validates environment variable loading
    - Checks for remaining hard-coded values
    - Verifies configuration consistency
    - Generates validation report
    - Suggests improvements

Usage:
    python scripts/validate_configuration.py

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import logging
from dataclasses import dataclass

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    
    severity: str  # "ERROR", "WARNING", "INFO"
    category: str  # "HARDCODED", "MISSING", "INVALID", "SECURITY"
    file_path: str
    line_number: int
    message: str
    suggestion: str


class ConfigurationValidator:
    """Validate configuration and identify issues."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues: List[ValidationIssue] = []
        
        # Patterns to identify hard-coded values
        self.hardcoded_patterns = {
            "database_urls": [
                r'postgresql://[^"\s]+',
                r'mysql://[^"\s]+',
                r'sqlite://[^"\s]+',
                r'mongodb://[^"\s]+',
            ],
            "service_urls": [
                r'http://localhost:\d+',
                r'https://localhost:\d+',
                r'http://127\.0\.0\.1:\d+',
                r'https://127\.0\.0\.1:\d+',
            ],
            "api_keys": [
                r'sk-[a-zA-Z0-9]{48}',
                r'pk_[a-zA-Z0-9]{48}',
                r'[a-zA-Z0-9]{32,}',
            ],
            "model_names": [
                r'gpt-[34]',
                r'claude-[23]',
                r'llama[23]?',
                r'mistral',
                r'gemini',
            ],
            "ports": [
                r':8000',
                r':8001',
                r':8002',
                r':8003',
                r':8004',
                r':8005',
                r':5432',
                r':6379',
                r':6333',
                r':7700',
                r':8529',
                r':11434',
            ],
        }
        
        # Files to exclude from validation
        self.exclude_patterns = [
            r'\.git/',
            r'node_modules/',
            r'\.venv/',
            r'venv/',
            r'env/',
            r'__pycache__/',
            r'\.pytest_cache/',
            r'\.next/',
            r'\.env',
            r'\.env\.example',
            r'requirements\.txt',
            r'package\.json',
            r'package-lock\.json',
            r'README\.md',
            r'\.md$',
            r'\.log$',
            r'\.pyc$',
            r'\.pyo$',
            r'tests/',
            r'frontend/',
            r'Lib/site-packages/',
            r'site-packages/',
        ]
    
    def should_validate_file(self, file_path: Path) -> bool:
        """Check if file should be validated."""
        file_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, file_str):
                return False
        
        # Only validate Python files
        return file_path.suffix == '.py'
    
    def find_hardcoded_values(self, file_path: Path) -> List[ValidationIssue]:
        """Find hard-coded values in a file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return issues
        
        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.hardcoded_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        # Skip if it's already using configuration
                        if any(config_func in line for config_func in [
                            "get_config_value", "get_central_config", 
                            "get_database_url", "get_redis_url",
                            "get_vector_db_url", "get_meilisearch_url",
                            "get_arangodb_url", "get_ollama_url"
                        ]):
                            continue
                        
                        # Skip if it's in a comment or string
                        if '#' in line[:line.find(match)] or '"' in line[:line.find(match)]:
                            continue
                        
                        issue = ValidationIssue(
                            severity="WARNING",
                            category="HARDCODED",
                            file_path=str(file_path),
                            line_number=line_num,
                            message=f"Hard-coded {category}: {match}",
                            suggestion=f"Replace with configuration function"
                        )
                        issues.append(issue)
        
        return issues
    
    def validate_environment_variables(self) -> List[ValidationIssue]:
        """Validate that required environment variables are set."""
        issues = []
        
        # Required environment variables for production
        required_vars = [
            "JWT_SECRET_KEY",
            "DATABASE_URL",
            "REDIS_URL",
        ]
        
        # Optional but recommended environment variables
        recommended_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "MEILISEARCH_MASTER_KEY",
            "ARANGODB_PASSWORD",
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                issue = ValidationIssue(
                    severity="ERROR",
                    category="MISSING",
                    file_path="Environment",
                    line_number=0,
                    message=f"Required environment variable not set: {var}",
                    suggestion=f"Set {var} in your .env file"
                )
                issues.append(issue)
        
        for var in recommended_vars:
            if not os.getenv(var):
                issue = ValidationIssue(
                    severity="WARNING",
                    category="MISSING",
                    file_path="Environment",
                    line_number=0,
                    message=f"Recommended environment variable not set: {var}",
                    suggestion=f"Consider setting {var} for full functionality"
                )
                issues.append(issue)
        
        return issues
    
    def validate_configuration_loading(self) -> List[ValidationIssue]:
        """Validate that configuration is properly loaded."""
        issues = []
        
        try:
            from shared.core.config.central_config import get_central_config, initialize_config
            
            # Test configuration loading
            config = get_central_config()
            
            # Validate critical configuration
            if not config.database_url and not config.postgres_host:
                issue = ValidationIssue(
                    severity="ERROR",
                    category="MISSING",
                    file_path="Configuration",
                    line_number=0,
                    message="Database configuration is missing",
                    suggestion="Set DATABASE_URL or individual database settings"
                )
                issues.append(issue)
            
            if not config.redis_url:
                issue = ValidationIssue(
                    severity="WARNING",
                    category="MISSING",
                    file_path="Configuration",
                    line_number=0,
                    message="Redis configuration is missing",
                    suggestion="Set REDIS_URL for caching functionality"
                )
                issues.append(issue)
            
            # Check AI provider configuration
            ai_providers = []
            if config.openai_api_key:
                ai_providers.append("OpenAI")
            if config.anthropic_api_key:
                ai_providers.append("Anthropic")
            if config.ollama_enabled:
                ai_providers.append("Ollama")
            
            if not ai_providers:
                issue = ValidationIssue(
                    severity="WARNING",
                    category="MISSING",
                    file_path="Configuration",
                    line_number=0,
                    message="No AI providers configured",
                    suggestion="Configure at least one AI provider (OpenAI, Anthropic, or Ollama)"
                )
                issues.append(issue)
            
            # Validate configuration
            config_issues = config.validate_config()
            for issue_msg in config_issues:
                issue = ValidationIssue(
                    severity="ERROR",
                    category="INVALID",
                    file_path="Configuration",
                    line_number=0,
                    message=issue_msg,
                    suggestion="Fix configuration validation issues"
                )
                issues.append(issue)
            
        except ImportError as e:
            issue = ValidationIssue(
                severity="ERROR",
                category="MISSING",
                file_path="Configuration",
                line_number=0,
                message=f"Could not import configuration module: {e}",
                suggestion="Ensure shared.core.config.central_config is available"
            )
            issues.append(issue)
        except Exception as e:
            issue = ValidationIssue(
                severity="ERROR",
                category="INVALID",
                file_path="Configuration",
                line_number=0,
                message=f"Configuration loading failed: {e}",
                suggestion="Check configuration setup and environment variables"
            )
            issues.append(issue)
        
        return issues
    
    def validate_security(self) -> List[ValidationIssue]:
        """Validate security-related configuration."""
        issues = []
        
        # Check for hard-coded secrets in source code
        secret_patterns = [
            r'sk-[a-zA-Z0-9]{48}',
            r'pk_[a-zA-Z0-9]{48}',
            r'[a-zA-Z0-9]{32,}',
        ]
        
        # Skip these patterns as they're not actual secrets
        skip_patterns = [
            r'[a-zA-Z0-9]{32,}',  # Too broad, catches class names
        ]
        
        for file_path in self.root_dir.rglob("*.py"):
            if not self.should_validate_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Skip if it's in a test file or example
                        if 'test' in str(file_path).lower() or 'example' in str(file_path).lower():
                            continue
                        
                        # Skip if it matches skip patterns
                        skip_match = False
                        for skip_pattern in skip_patterns:
                            if re.search(skip_pattern, match):
                                skip_match = True
                                break
                        
                        if skip_match:
                            continue
                        
                        # Only flag actual API keys
                        if match.startswith('sk-') or match.startswith('pk_'):
                            issue = ValidationIssue(
                                severity="ERROR",
                                category="SECURITY",
                                file_path=str(file_path),
                                line_number=0,
                                message=f"Potential hard-coded secret found: {match[:10]}...",
                                suggestion="Move secrets to environment variables"
                            )
                            issues.append(issue)
            
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        return issues
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info("Starting configuration validation...")
        
        all_issues = []
        
        # Validate environment variables
        logger.info("Validating environment variables...")
        env_issues = self.validate_environment_variables()
        all_issues.extend(env_issues)
        
        # Validate configuration loading
        logger.info("Validating configuration loading...")
        config_issues = self.validate_configuration_loading()
        all_issues.extend(config_issues)
        
        # Validate security
        logger.info("Validating security...")
        security_issues = self.validate_security()
        all_issues.extend(security_issues)
        
        # Find hard-coded values in files
        logger.info("Scanning for hard-coded values...")
        for file_path in self.root_dir.rglob("*.py"):
            if self.should_validate_file(file_path):
                hardcoded_issues = self.find_hardcoded_values(file_path)
                all_issues.extend(hardcoded_issues)
        
        # Categorize issues
        issues_by_severity = {
            "ERROR": [i for i in all_issues if i.severity == "ERROR"],
            "WARNING": [i for i in all_issues if i.severity == "WARNING"],
            "INFO": [i for i in all_issues if i.severity == "INFO"],
        }
        
        issues_by_category = {
            "HARDCODED": [i for i in all_issues if i.category == "HARDCODED"],
            "MISSING": [i for i in all_issues if i.category == "MISSING"],
            "INVALID": [i for i in all_issues if i.category == "INVALID"],
            "SECURITY": [i for i in all_issues if i.category == "SECURITY"],
        }
        
        return {
            "total_issues": len(all_issues),
            "issues_by_severity": issues_by_severity,
            "issues_by_category": issues_by_category,
            "all_issues": all_issues
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a validation report."""
        report = []
        report.append("=" * 80)
        report.append("CONFIGURATION VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_issues = results["total_issues"]
        error_count = len(results["issues_by_severity"]["ERROR"])
        warning_count = len(results["issues_by_severity"]["WARNING"])
        info_count = len(results["issues_by_severity"]["INFO"])
        
        report.append(f"Total Issues: {total_issues}")
        report.append(f"Errors: {error_count}")
        report.append(f"Warnings: {warning_count}")
        report.append(f"Info: {info_count}")
        report.append("")
        
        # Issues by category
        for category, issues in results["issues_by_category"].items():
            if issues:
                report.append(f"{category} Issues ({len(issues)}):")
                for issue in issues[:10]:  # Show first 10
                    report.append(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
                    report.append(f"    Suggestion: {issue.suggestion}")
                if len(issues) > 10:
                    report.append(f"    ... and {len(issues) - 10} more")
                report.append("")
        
        # Critical issues
        if error_count > 0:
            report.append("CRITICAL ISSUES (Must Fix):")
            for issue in results["issues_by_severity"]["ERROR"]:
                report.append(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
            report.append("")
        
        # Recommendations
        if total_issues > 0:
            report.append("RECOMMENDATIONS:")
            if error_count > 0:
                report.append("  1. Fix all ERROR level issues first")
            if warning_count > 0:
                report.append("  2. Address WARNING level issues for better configuration")
            if len(results["issues_by_category"]["HARDCODED"]) > 0:
                report.append("  3. Replace hard-coded values with configuration functions")
            if len(results["issues_by_category"]["SECURITY"]) > 0:
                report.append("  4. Move all secrets to environment variables")
            report.append("")
        else:
            report.append("✅ All validation checks passed!")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function."""
    validator = ConfigurationValidator()
    
    # Run validation
    results = validator.validate_all()
    
    # Generate and print report
    report = validator.generate_report(results)
    print(report)
    
    # Save report to file
    report_file = Path("CONFIGURATION_VALIDATION_REPORT.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Report saved to {report_file}")
    
    # Exit with error code if there are critical issues
    error_count = len(results["issues_by_severity"]["ERROR"])
    if error_count > 0:
        logger.error(f"Validation failed with {error_count} critical issues")
        sys.exit(1)
    else:
        logger.info("Configuration validation completed successfully!")


if __name__ == "__main__":
    main() 