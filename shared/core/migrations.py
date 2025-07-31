"""
Database Migrations - Universal Knowledge Platform
Alembic-based migration system with version control and rollback capabilities.

Features:
- Automated migration generation
- Schema versioning and rollback
- Data migration support
- Migration validation and testing
- Multi-environment support
- Backup and restore procedures

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import subprocess
import json

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.script.revision import Revision

import structlog

logger = structlog.get_logger(__name__)


class MigrationManager:
    """Database migration manager with Alembic integration."""

    def __init__(self, alembic_cfg_path: str, db_url: str):
        self.alembic_cfg_path = alembic_cfg_path
        self.db_url = db_url
        self.config = Config(alembic_cfg_path)
        self.config.set_main_option("sqlalchemy.url", db_url)
        self.script_dir = ScriptDirectory.from_config(self.config)

    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            with self.config.get_connection() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error("Failed to get current revision", error=str(e))
            return None

    def get_head_revision(self) -> Optional[str]:
        """Get head revision from migration scripts."""
        try:
            return self.script_dir.get_current_head()
        except Exception as e:
            logger.error("Failed to get head revision", error=str(e))
            return None

    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history with details."""
        try:
            revisions = []
            for revision in self.script_dir.walk_revisions():
                revisions.append(
                    {
                        "revision": revision.revision,
                        "down_revision": revision.down_revision,
                        "message": revision.message,
                        "date": revision.date,
                        "branch_labels": revision.branch_labels,
                        "dependencies": revision.dependencies,
                    }
                )
            return sorted(revisions, key=lambda x: x["date"] or datetime.min)
        except Exception as e:
            logger.error("Failed to get migration history", error=str(e))
            return []

    def create_migration(
        self, message: str, autogenerate: bool = True
    ) -> Optional[str]:
        """Create a new migration."""
        try:
            if autogenerate:
                command.revision(self.config, message=message, autogenerate=True)
            else:
                command.revision(self.config, message=message)

            # Get the latest revision
            head_revision = self.get_head_revision()
            logger.info("Created migration", revision=head_revision, message=message)
            return head_revision
        except Exception as e:
            logger.error("Failed to create migration", error=str(e))
            return None

    def upgrade(self, target_revision: Optional[str] = None) -> bool:
        """Upgrade database to target revision (or head)."""
        try:
            if target_revision is None:
                target_revision = "head"

            command.upgrade(self.config, target_revision)
            logger.info("Database upgraded", target_revision=target_revision)
            return True
        except Exception as e:
            logger.error("Failed to upgrade database", error=str(e))
            return False

    def downgrade(self, target_revision: str) -> bool:
        """Downgrade database to target revision."""
        try:
            command.downgrade(self.config, target_revision)
            logger.info("Database downgraded", target_revision=target_revision)
            return True
        except Exception as e:
            logger.error("Failed to downgrade database", error=str(e))
            return False

    def stamp(self, revision: str) -> bool:
        """Stamp database with revision without running migrations."""
        try:
            command.stamp(self.config, revision)
            logger.info("Database stamped", revision=revision)
            return True
        except Exception as e:
            logger.error("Failed to stamp database", error=str(e))
            return False

    def check_migration_status(self) -> Dict[str, Any]:
        """Check migration status and consistency."""
        current_revision = self.get_current_revision()
        head_revision = self.get_head_revision()

        status = {
            "current_revision": current_revision,
            "head_revision": head_revision,
            "is_up_to_date": current_revision == head_revision,
            "pending_migrations": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if current_revision != head_revision:
            # Get pending migrations
            try:
                pending = command.check(self.config)
                status["pending_migrations"] = pending
            except Exception as e:
                logger.error("Failed to get pending migrations", error=str(e))

        return status

    def validate_migrations(self) -> Dict[str, Any]:
        """Validate migration scripts for consistency."""
        try:
            # Check for duplicate revisions
            revisions = {}
            for revision in self.script_dir.walk_revisions():
                if revision.revision in revisions:
                    return {
                        "valid": False,
                        "error": f"Duplicate revision: {revision.revision}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                revisions[revision.revision] = revision

            # Check for circular dependencies
            visited = set()
            rec_stack = set()

            def has_cycle(revision_id: str) -> bool:
                if revision_id in rec_stack:
                    return True
                if revision_id in visited:
                    return False

                visited.add(revision_id)
                rec_stack.add(revision_id)

                revision = revisions.get(revision_id)
                if revision and revision.down_revision:
                    if has_cycle(revision.down_revision):
                        return True

                rec_stack.remove(revision_id)
                return False

            for revision_id in revisions:
                if has_cycle(revision_id):
                    return {
                        "valid": False,
                        "error": f"Circular dependency detected at revision: {revision_id}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }

            return {
                "valid": True,
                "revision_count": len(revisions),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error("Failed to validate migrations", error=str(e))
            return {
                "valid": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


class DataMigration:
    """Data migration utilities for complex data transformations."""

    def __init__(self, db_service):
        self.db_service = db_service

    def migrate_user_data(self, batch_size: int = 1000) -> Dict[str, Any]:
        """Migrate user data with batching for performance."""
        try:
            with self.db_service.get_session() as session:
                # Example: Migrate user preferences to new format
                total_migrated = 0
                total_batches = 0

                while True:
                    # Get batch of users to migrate
                    users = session.session.execute(
                        text(
                            "SELECT id, preferences FROM users WHERE preferences_migrated = false LIMIT :limit"
                        ),
                        {"limit": batch_size},
                    ).fetchall()

                    if not users:
                        break

                    for user in users:
                        # Transform preferences
                        old_prefs = user.preferences or {}
                        new_prefs = self._transform_user_preferences(old_prefs)

                        # Update user
                        session.session.execute(
                            text(
                                "UPDATE users SET preferences = :prefs, preferences_migrated = true WHERE id = :id"
                            ),
                            {"prefs": json.dumps(new_prefs), "id": user.id},
                        )
                        total_migrated += 1

                    session.session.commit()
                    total_batches += 1

                return {
                    "success": True,
                    "total_migrated": total_migrated,
                    "total_batches": total_batches,
                }
        except Exception as e:
            logger.error("User data migration failed", error=str(e))
            return {"success": False, "error": str(e)}

    def _transform_user_preferences(self, old_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Transform user preferences to new format."""
        # Example transformation
        new_prefs = {
            "theme": old_prefs.get("theme", "light"),
            "language": old_prefs.get("language", "en"),
            "notifications": {
                "email": old_prefs.get("email_notifications", True),
                "push": old_prefs.get("push_notifications", False),
            },
            "privacy": {
                "profile_visible": old_prefs.get("profile_visible", True),
                "search_visible": old_prefs.get("search_visible", True),
            },
        }
        return new_prefs

    def migrate_knowledge_items(self, batch_size: int = 1000) -> Dict[str, Any]:
        """Migrate knowledge items with vector embeddings."""
        try:
            with self.db_service.get_session() as session:
                total_migrated = 0
                total_batches = 0

                while True:
                    # Get batch of items without embeddings
                    items = session.session.execute(
                        text(
                            "SELECT id, title, content FROM knowledge_items WHERE embedding IS NULL LIMIT :limit"
                        ),
                        {"limit": batch_size},
                    ).fetchall()

                    if not items:
                        break

                    for item in items:
                        # Generate embedding (this would integrate with your embedding service)
                        embedding = self._generate_embedding(
                            f"{item.title} {item.content}"
                        )

                        # Update item with embedding
                        session.session.execute(
                            text(
                                "UPDATE knowledge_items SET embedding = :embedding WHERE id = :id"
                            ),
                            {"embedding": embedding, "id": item.id},
                        )
                        total_migrated += 1

                    session.session.commit()
                    total_batches += 1

                return {
                    "success": True,
                    "total_migrated": total_migrated,
                    "total_batches": total_batches,
                }
        except Exception as e:
            logger.error("Knowledge items migration failed", error=str(e))
            return {"success": False, "error": str(e)}

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder implementation)."""
        # This would integrate with your embedding service (OpenAI, etc.)
        # For now, return a dummy embedding
        return [0.0] * 1536  # OpenAI embedding size


class MigrationBackup:
    """Database backup and restore utilities."""

    def __init__(self, db_url: str, backup_dir: str = "backups"):
        self.db_url = db_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, backup_name: Optional[str] = None) -> Optional[str]:
        """Create database backup."""
        try:
            if backup_name is None:
                backup_name = (
                    f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.sql"
                )

            backup_path = self.backup_dir / backup_name

            # Extract database connection info
            # This is a simplified example - you'd need to parse the URL properly
            if "postgresql://" in self.db_url:
                # PostgreSQL backup
                cmd = [
                    "pg_dump",
                    "--dbname",
                    self.db_url,
                    "--file",
                    str(backup_path),
                    "--verbose",
                    "--no-password",
                ]
            else:
                raise ValueError("Unsupported database type")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Database backup created", path=str(backup_path))
                return str(backup_path)
            else:
                logger.error("Backup failed", error=result.stderr)
                return None
        except Exception as e:
            logger.error("Failed to create backup", error=str(e))
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            # Extract database connection info
            if "postgresql://" in self.db_url:
                # PostgreSQL restore
                cmd = [
                    "psql",
                    "--dbname",
                    self.db_url,
                    "--file",
                    str(backup_file),
                    "--verbose",
                    "--no-password",
                ]
            else:
                raise ValueError("Unsupported database type")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Database restored from backup", path=str(backup_path))
                return True
            else:
                logger.error("Restore failed", error=result.stderr)
                return False
        except Exception as e:
            logger.error("Failed to restore backup", error=str(e))
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        for backup_file in self.backup_dir.glob("*.sql"):
            stat = backup_file.stat()
            backups.append(
                {
                    "name": backup_file.name,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(
                        stat.st_ctime, tz=timezone.utc
                    ).isoformat(),
                    "path": str(backup_file),
                }
            )
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)


# Migration utilities
def create_alembic_config(project_root: str, db_url: str) -> str:
    """Create Alembic configuration file."""
    config_content = f"""[alembic]
script_location = {project_root}/migrations
sqlalchemy.url = {db_url}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    config_path = Path(project_root) / "alembic.ini"
    config_path.write_text(config_content)

    return str(config_path)


def initialize_migrations(project_root: str, db_url: str) -> bool:
    """Initialize migration system."""
    try:
        # Create migrations directory
        migrations_dir = Path(project_root) / "migrations"
        migrations_dir.mkdir(exist_ok=True)

        # Create Alembic config
        config_path = create_alembic_config(project_root, db_url)

        # Initialize Alembic
        config = Config(config_path)
        command.init(config, str(migrations_dir))

        logger.info(
            "Migration system initialized",
            project_root=project_root,
            migrations_dir=str(migrations_dir),
        )
        return True
    except Exception as e:
        logger.error("Failed to initialize migrations", error=str(e))
        return False


# Export main classes
__all__ = [
    "MigrationManager",
    "DataMigration",
    "MigrationBackup",
    "create_alembic_config",
    "initialize_migrations",
]
