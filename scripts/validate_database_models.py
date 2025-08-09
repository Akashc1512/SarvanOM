#!/usr/bin/env python3
"""
Database Model Validation Script - MAANG Standards

This script validates database models for compliance with MAANG-level standards,
checking data integrity, performance optimizations, and security features.

Validation Checks:
    - Model structure and relationships
    - Index optimization
    - Constraint validation
    - Security features
    - Performance characteristics
    - Documentation quality

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import sys
import os
import inspect
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import models for validation
from shared.models.models import (
    Base,
    User,
    Role,
    UserSession,
    APIKey,
    KnowledgeItem,
    Query,
    AuditLog,
    RecordStatus,
    AuditAction,
)


@dataclass
class ValidationResult:
    """Validation result data structure."""

    check_name: str
    status: str
    message: str
    severity: str  # "ERROR", "WARNING", "INFO"
    details: Optional[Dict[str, Any]] = None


@dataclass
class ModelValidationReport:
    """Model validation report data structure."""

    model_name: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: int
    results: List[ValidationResult]
    score: float


class DatabaseModelValidator:
    """Comprehensive database model validator with MAANG-level standards."""

    def __init__(self):
        self.console = Console()
        self.reports: List[ModelValidationReport] = []
        self.models = [User, Role, UserSession, APIKey, KnowledgeItem, Query, AuditLog]

    def validate_all_models(self) -> None:
        """Validate all database models."""
        self.console.print(
            "[bold blue]Database Model Validation - MAANG Standards[/bold blue]"
        )
        self.console.print("=" * 60)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            for model in self.models:
                task = progress.add_task(f"Validating {model.__name__}...", total=None)
                report = self.validate_model(model)
                self.reports.append(report)
                progress.update(task, completed=True)

        # Generate comprehensive report
        self.generate_validation_report()

    def validate_model(self, model_class) -> ModelValidationReport:
        """Validate a single model class."""
        results = []

        # Run all validation checks
        results.extend(self._validate_model_structure(model_class))
        results.extend(self._validate_relationships(model_class))
        results.extend(self._validate_indexes(model_class))
        results.extend(self._validate_constraints(model_class))
        results.extend(self._validate_security_features(model_class))
        results.extend(self._validate_performance_features(model_class))
        results.extend(self._validate_documentation(model_class))

        # Calculate statistics
        total_checks = len(results)
        passed_checks = len([r for r in results if r.status == "PASSED"])
        failed_checks = len([r for r in results if r.status == "FAILED"])
        warnings = len([r for r in results if r.severity == "WARNING"])

        # Calculate score
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        return ModelValidationReport(
            model_name=model_class.__name__,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            results=results,
            score=score,
        )

    def _validate_model_structure(self, model_class) -> List[ValidationResult]:
        """Validate model structure and basic requirements."""
        results = []

        # Check if model inherits from Base
        if not issubclass(model_class, Base):
            results.append(
                ValidationResult(
                    check_name="Base Model Inheritance",
                    status="FAILED",
                    message=f"{model_class.__name__} must inherit from Base",
                    severity="ERROR",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Base Model Inheritance",
                    status="PASSED",
                    message=f"{model_class.__name__} properly inherits from Base",
                    severity="INFO",
                )
            )

        # Check for required base fields
        required_fields = ["id", "created_at", "updated_at", "status", "version"]
        missing_fields = []

        for field in required_fields:
            if not hasattr(model_class, field):
                missing_fields.append(field)

        if missing_fields:
            results.append(
                ValidationResult(
                    check_name="Required Base Fields",
                    status="FAILED",
                    message=f"Missing required fields: {', '.join(missing_fields)}",
                    severity="ERROR",
                    details={"missing_fields": missing_fields},
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Required Base Fields",
                    status="PASSED",
                    message="All required base fields present",
                    severity="INFO",
                )
            )

        # Check for __tablename__ attribute
        if not hasattr(model_class, "__tablename__"):
            results.append(
                ValidationResult(
                    check_name="Table Name Definition",
                    status="FAILED",
                    message="Model must define __tablename__",
                    severity="ERROR",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Table Name Definition",
                    status="PASSED",
                    message=f"Table name defined: {model_class.__tablename__}",
                    severity="INFO",
                )
            )

        return results

    def _validate_relationships(self, model_class) -> List[ValidationResult]:
        """Validate model relationships."""
        results = []

        # Check for proper relationship definitions
        relationships = []
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, "property") and hasattr(attr.property, "mapper"):
                relationships.append(attr_name)

        if relationships:
            results.append(
                ValidationResult(
                    check_name="Relationship Definitions",
                    status="PASSED",
                    message=f"Found {len(relationships)} relationships: {', '.join(relationships)}",
                    severity="INFO",
                    details={"relationships": relationships},
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Relationship Definitions",
                    status="WARNING",
                    message="No relationships defined",
                    severity="WARNING",
                )
            )

        # Check for proper foreign key constraints
        foreign_keys = []
        for column in model_class.__table__.columns:
            if column.foreign_keys:
                foreign_keys.append(column.name)

        if foreign_keys:
            results.append(
                ValidationResult(
                    check_name="Foreign Key Constraints",
                    status="PASSED",
                    message=f"Found {len(foreign_keys)} foreign keys: {', '.join(foreign_keys)}",
                    severity="INFO",
                    details={"foreign_keys": foreign_keys},
                )
            )

        return results

    def _validate_indexes(self, model_class) -> List[ValidationResult]:
        """Validate model indexes for performance optimization."""
        results = []

        # Check for indexes
        indexes = list(model_class.__table__.indexes)

        if indexes:
            results.append(
                ValidationResult(
                    check_name="Index Definitions",
                    status="PASSED",
                    message=f"Found {len(indexes)} indexes",
                    severity="INFO",
                    details={"indexes": [idx.name for idx in indexes]},
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Index Definitions",
                    status="WARNING",
                    message="No indexes defined - consider adding indexes for performance",
                    severity="WARNING",
                )
            )

        # Check for specific important indexes
        important_indexes = ["email", "username", "created_at", "status"]
        missing_indexes = []

        for field in important_indexes:
            if hasattr(model_class, field):
                field_indexes = [
                    idx for idx in indexes if field in [col.name for col in idx.columns]
                ]
                if not field_indexes:
                    missing_indexes.append(field)

        if missing_indexes:
            results.append(
                ValidationResult(
                    check_name="Important Indexes",
                    status="WARNING",
                    message=f"Consider adding indexes for: {', '.join(missing_indexes)}",
                    severity="WARNING",
                    details={"missing_indexes": missing_indexes},
                )
            )

        return results

    def _validate_constraints(self, model_class) -> List[ValidationResult]:
        """Validate model constraints."""
        results = []

        # Check for constraints
        constraints = []
        if hasattr(model_class, "__table_args__"):
            table_args = model_class.__table_args__
            if isinstance(table_args, tuple):
                for arg in table_args:
                    if (
                        hasattr(arg, "__class__")
                        and "Constraint" in arg.__class__.__name__
                    ):
                        constraints.append(arg.__class__.__name__)

        if constraints:
            results.append(
                ValidationResult(
                    check_name="Constraint Definitions",
                    status="PASSED",
                    message=f"Found {len(constraints)} constraints",
                    severity="INFO",
                    details={"constraints": constraints},
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Constraint Definitions",
                    status="WARNING",
                    message="No constraints defined - consider adding data integrity constraints",
                    severity="WARNING",
                )
            )

        # Check for unique constraints
        unique_constraints = [c for c in constraints if "Unique" in c]
        if unique_constraints:
            results.append(
                ValidationResult(
                    check_name="Unique Constraints",
                    status="PASSED",
                    message=f"Found {len(unique_constraints)} unique constraints",
                    severity="INFO",
                )
            )

        return results

    def _validate_security_features(self, model_class) -> List[ValidationResult]:
        """Validate security features."""
        results = []

        # Check for encrypted fields
        encrypted_fields = []
        for column in model_class.__table__.columns:
            if (
                hasattr(column.type, "__class__")
                and "Encrypted" in column.type.__class__.__name__
            ):
                encrypted_fields.append(column.name)

        if encrypted_fields:
            results.append(
                ValidationResult(
                    check_name="Encrypted Fields",
                    status="PASSED",
                    message=f"Found {len(encrypted_fields)} encrypted fields: {', '.join(encrypted_fields)}",
                    severity="INFO",
                    details={"encrypted_fields": encrypted_fields},
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Encrypted Fields",
                    status="INFO",
                    message="No encrypted fields found",
                    severity="INFO",
                )
            )

        # Check for soft delete functionality
        if hasattr(model_class, "deleted_at") and hasattr(model_class, "soft_delete"):
            results.append(
                ValidationResult(
                    check_name="Soft Delete",
                    status="PASSED",
                    message="Soft delete functionality implemented",
                    severity="INFO",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Soft Delete",
                    status="WARNING",
                    message="Consider implementing soft delete for data recovery",
                    severity="WARNING",
                )
            )

        return results

    def _validate_performance_features(self, model_class) -> List[ValidationResult]:
        """Validate performance features."""
        results = []

        # Check for lazy loading configuration
        lazy_relationships = []
        eager_relationships = []

        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, "property") and hasattr(attr.property, "mapper"):
                if hasattr(attr.property, "lazy"):
                    if attr.property.lazy == "dynamic":
                        lazy_relationships.append(attr_name)
                    elif attr.property.lazy == "joined":
                        eager_relationships.append(attr_name)

        if lazy_relationships:
            results.append(
                ValidationResult(
                    check_name="Lazy Loading",
                    status="PASSED",
                    message=f"Found {len(lazy_relationships)} lazy-loaded relationships",
                    severity="INFO",
                    details={"lazy_relationships": lazy_relationships},
                )
            )

        if eager_relationships:
            results.append(
                ValidationResult(
                    check_name="Eager Loading",
                    status="PASSED",
                    message=f"Found {len(eager_relationships)} eager-loaded relationships",
                    severity="INFO",
                    details={"eager_relationships": eager_relationships},
                )
            )

        # Check for hybrid properties
        hybrid_properties = []
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if (
                hasattr(attr, "fget")
                and hasattr(attr.fget, "__class__")
                and "hybrid_property" in str(attr.fget.__class__)
            ):
                hybrid_properties.append(attr_name)

        if hybrid_properties:
            results.append(
                ValidationResult(
                    check_name="Hybrid Properties",
                    status="PASSED",
                    message=f"Found {len(hybrid_properties)} hybrid properties",
                    severity="INFO",
                    details={"hybrid_properties": hybrid_properties},
                )
            )

        return results

    def _validate_documentation(self, model_class) -> List[ValidationResult]:
        """Validate model documentation."""
        results = []

        # Check for docstring
        if model_class.__doc__:
            doc_length = len(model_class.__doc__.strip())
            if doc_length > 50:
                results.append(
                    ValidationResult(
                        check_name="Model Documentation",
                        status="PASSED",
                        message=f"Model has comprehensive documentation ({doc_length} characters)",
                        severity="INFO",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="Model Documentation",
                        status="WARNING",
                        message="Model documentation is minimal - consider adding more details",
                        severity="WARNING",
                    )
                )
        else:
            results.append(
                ValidationResult(
                    check_name="Model Documentation",
                    status="FAILED",
                    message="Model lacks documentation",
                    severity="ERROR",
                )
            )

        # Check for field comments
        fields_with_comments = []
        fields_without_comments = []

        for column in model_class.__table__.columns:
            if column.comment:
                fields_with_comments.append(column.name)
            else:
                fields_without_comments.append(column.name)

        if fields_with_comments:
            results.append(
                ValidationResult(
                    check_name="Field Documentation",
                    status="PASSED",
                    message=f"Found {len(fields_with_comments)} fields with comments",
                    severity="INFO",
                    details={"fields_with_comments": fields_with_comments},
                )
            )

        if fields_without_comments:
            results.append(
                ValidationResult(
                    check_name="Field Documentation",
                    status="WARNING",
                    message=f"Consider adding comments for {len(fields_without_comments)} fields",
                    severity="WARNING",
                    details={"fields_without_comments": fields_without_comments},
                )
            )

        return results

    def generate_validation_report(self) -> None:
        """Generate comprehensive validation report."""
        self.console.print(
            "\n[bold green]Database Model Validation Report[/bold green]"
        )
        self.console.print("=" * 60)

        # Summary table
        summary_table = Table(title="Model Validation Summary")
        summary_table.add_column("Model", style="cyan")
        summary_table.add_column("Total Checks", justify="right")
        summary_table.add_column("Passed", justify="right")
        summary_table.add_column("Failed", justify="right")
        summary_table.add_column("Warnings", justify="right")
        summary_table.add_column("Score", justify="right")

        total_checks = 0
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        total_score = 0

        for report in self.reports:
            summary_table.add_row(
                report.model_name,
                str(report.total_checks),
                str(report.passed_checks),
                str(report.failed_checks),
                str(report.warnings),
                f"{report.score:.1f}%",
            )

            total_checks += report.total_checks
            total_passed += report.passed_checks
            total_failed += report.failed_checks
            total_warnings += report.warnings
            total_score += report.score

        # Add totals
        avg_score = total_score / len(self.reports) if self.reports else 0
        summary_table.add_row(
            "[bold]TOTAL[/bold]",
            str(total_checks),
            str(total_passed),
            str(total_failed),
            str(total_warnings),
            f"{avg_score:.1f}%",
        )

        self.console.print(summary_table)

        # Detailed results for each model
        for report in self.reports:
            self.console.print(f"\n[bold]{report.model_name}[/bold]")

            # Show failed checks
            failed_checks = [r for r in report.results if r.status == "FAILED"]
            if failed_checks:
                self.console.print("[red]Failed Checks:[/red]")
                for check in failed_checks:
                    self.console.print(f"  - {check.check_name}: {check.message}")

            # Show warnings
            warnings = [r for r in report.results if r.severity == "WARNING"]
            if warnings:
                self.console.print("[yellow]Warnings:[/yellow]")
                for check in warnings:
                    self.console.print(f"  - {check.check_name}: {check.message}")

            # Show passed checks
            passed_checks = [r for r in report.results if r.status == "PASSED"]
            if passed_checks:
                self.console.print("[green]Passed Checks:[/green]")
                for check in passed_checks[:5]:  # Show first 5
                    self.console.print(f"  - {check.check_name}: {check.message}")
                if len(passed_checks) > 5:
                    self.console.print(f"  ... and {len(passed_checks) - 5} more")

        # Overall assessment
        self.console.print("\n[bold]Overall Assessment:[/bold]")
        if avg_score >= 90:
            self.console.print(
                "[green]Excellent - Models meet MAANG-level standards[/green]"
            )
        elif avg_score >= 80:
            self.console.print(
                "[yellow]Good - Models mostly meet standards with minor issues[/yellow]"
            )
        elif avg_score >= 70:
            self.console.print(
                "[orange]Fair - Models need improvements to meet standards[/orange]"
            )
        else:
            self.console.print("[red]Poor - Models need significant improvements[/red]")


def main():
    """Main entry point for database model validation."""
    validator = DatabaseModelValidator()
    validator.validate_all_models()

    # Exit with appropriate code based on results
    total_failed = sum(r.failed_checks for r in validator.reports)
    if total_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
