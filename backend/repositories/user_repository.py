"""
User Repository Implementation

This module contains the repository implementation for User domain entities.
Handles user authentication, profile management, and user-related data persistence.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .base_repository import BaseRepository, InMemoryRepository
from ..models.domain.user import User, UserRole, UserStatus

logger = logging.getLogger(__name__)


class UserRepository(ABC):
    """Abstract interface for User repository operations."""

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        pass

    @abstractmethod
    async def update_user_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user profile information."""
        pass

    @abstractmethod
    async def update_user_status(
        self, user_id: str, status: UserStatus
    ) -> Optional[User]:
        """Update user account status."""
        pass

    @abstractmethod
    async def authenticate_user(
        self, username: str, password_hash: str
    ) -> Optional[User]:
        """Authenticate user with credentials."""
        pass

    @abstractmethod
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        pass

    @abstractmethod
    async def search_users(self, search_term: str) -> List[User]:
        """Search users by username, email, or display name."""
        pass

    @abstractmethod
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        pass


class UserRepositoryImpl(UserRepository, BaseRepository[User]):
    """
    Implementation of User repository using the base repository.

    This implementation can be extended to use different storage backends
    like PostgreSQL, MongoDB, etc.
    """

    def __init__(
        self, connection_string: Optional[str] = None, storage_type: str = "memory"
    ):
        """Initialize the user repository."""
        super().__init__(connection_string)
        self.storage_type = storage_type

        # Initialize database repository if PostgreSQL is configured
        if storage_type == "postgres":
            try:
                from backend.repositories.database.user_repository import UserRepository as DBUserRepository
                self._db_repository = DBUserRepository()
                logger.info("PostgreSQL user repository initialized")
            except ImportError as e:
                logger.warning(f"Could not import database repository: {e}")
                self._db_repository = None
        else:
            self._db_repository = None

        # Fallback to in-memory storage
        if not self._db_repository:
            self._memory_store = InMemoryRepository[User]()
            logger.info(f"User repository initialized with {storage_type} storage")

        # User-specific indices for faster lookups (for in-memory storage)
        if not self._db_repository:
            self._username_index: Dict[str, str] = {}  # username -> user_id
            self._email_index: Dict[str, str] = {}  # email -> user_id
            self._role_index: Dict[UserRole, List[str]] = {}  # role -> [user_ids]
            self._status_index: Dict[UserStatus, List[str]] = {}  # status -> [user_ids]

    async def create(self, entity: User) -> User:
        """Create a new user (BaseRepository interface)."""
        return await self.create_user(entity)

    async def get_by_id(self, entity_id: str) -> Optional[User]:
        """Get user by ID (BaseRepository interface)."""
        return await self.get_user_by_id(entity_id)

    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user (BaseRepository interface)."""
        # Handle specific user updates
        if "status" in updates:
            status = updates.pop("status")
            if isinstance(status, str):
                status = UserStatus(status)
            await self.update_user_status(entity_id, status)

        # Handle profile updates
        if updates:
            return await self.update_user_profile(entity_id, updates)

        return await self.get_user_by_id(entity_id)

    async def delete(self, entity_id: str) -> bool:
        """Delete user (BaseRepository interface)."""
        if self.storage_type == "memory":
            # Also remove from indices
            user = await self.get_user_by_id(entity_id)
            if user:
                await self._remove_from_indices(user)
            return await self._memory_store.delete(entity_id)
        return False

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """List users (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.list(filters, offset, limit)
        return []

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count users (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.count(filters)
        return 0

    async def exists(self, entity_id: str) -> bool:
        """Check if user exists (BaseRepository interface)."""
        if self.storage_type == "memory":
            return await self._memory_store.exists(entity_id)
        return False

    # User-specific methods

    async def create_user(self, user: User) -> User:
        """Create a new user with validation and indexing."""
        try:
            # Use database repository if available
            if self._db_repository:
                return await self._db_repository.create_user(
                    username=user.username,
                    email=user.email,
                    password=user.password_hash,  # Assuming this is already hashed
                    full_name=user.full_name,
                    **{k: v for k, v in user.__dict__.items() if k not in ['username', 'email', 'password_hash', 'full_name']}
                )

            # Fallback to in-memory storage
            # Check for duplicate username
            existing_user = await self.get_user_by_username(user.username)
            if existing_user:
                raise ValueError(f"Username '{user.username}' already exists")

            # Check for duplicate email
            existing_email = await self.get_user_by_email(user.email)
            if existing_email:
                raise ValueError(f"Email '{user.email}' already exists")

            # Store the user
            created_user = await self._memory_store.create(user)

            # Update indices
            await self._add_to_indices(created_user)

            self._track_operation("create_user", success=True)
            logger.info(f"Created user {created_user.id} ({created_user.username})")

            return created_user

        except Exception as e:
            self._track_operation("create_user", success=False)
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        try:
            # Use database repository if available
            if self._db_repository:
                return await self._db_repository.get_by_id(user_id)

            # Fallback to in-memory storage
            user = await self._memory_store.get_by_id(user_id)

            self._track_operation("get_user_by_id", success=True)
            return user

        except Exception as e:
            self._track_operation("get_user_by_id", success=False)
            logger.error(f"Failed to get user {user_id}: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        try:
            # Use database repository if available
            if self._db_repository:
                return await self._db_repository.get_by_username(username)

            # Fallback to in-memory storage
            user_id = self._username_index.get(username)
            if user_id:
                return await self.get_user_by_id(user_id)

            self._track_operation("get_user_by_username", success=True)
            return None

        except Exception as e:
            self._track_operation("get_user_by_username", success=False)
            logger.error(f"Failed to get user by username {username}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        try:
            # Use database repository if available
            if self._db_repository:
                return await self._db_repository.get_by_email(email)

            # Fallback to in-memory storage
            user_id = self._email_index.get(email)
            if user_id:
                return await self.get_user_by_id(user_id)

            self._track_operation("get_user_by_email", success=True)
            return None

        except Exception as e:
            self._track_operation("get_user_by_email", success=False)
            logger.error(f"Failed to get user by email {email}: {e}")
            raise

    async def update_user_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user profile information."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            # Validate email uniqueness if being updated
            if "email" in profile_data:
                new_email = profile_data["email"]
                if new_email != user.email:
                    existing_user = await self.get_user_by_email(new_email)
                    if existing_user and existing_user.id != user_id:
                        raise ValueError(f"Email '{new_email}' already exists")

                    # Update email index
                    if user.email in self._email_index:
                        del self._email_index[user.email]
                    self._email_index[new_email] = user_id

            # Validate username uniqueness if being updated
            if "username" in profile_data:
                new_username = profile_data["username"]
                if new_username != user.username:
                    existing_user = await self.get_user_by_username(new_username)
                    if existing_user and existing_user.id != user_id:
                        raise ValueError(f"Username '{new_username}' already exists")

                    # Update username index
                    if user.username in self._username_index:
                        del self._username_index[user.username]
                    self._username_index[new_username] = user_id

            # Add updated_at timestamp
            profile_data["updated_at"] = datetime.now()

            # Update in storage
            if self.storage_type == "memory":
                updated_user = await self._memory_store.update(user_id, profile_data)
            else:
                # TODO: Implement database update
                updated_user = user
                for key, value in profile_data.items():
                    if hasattr(updated_user, key):
                        setattr(updated_user, key, value)

            self._track_operation("update_user_profile", success=True)
            logger.info(f"Updated profile for user {user_id}")

            return updated_user

        except Exception as e:
            self._track_operation("update_user_profile", success=False)
            logger.error(f"Failed to update user profile for {user_id}: {e}")
            raise

    async def update_user_status(
        self, user_id: str, status: UserStatus
    ) -> Optional[User]:
        """Update user account status."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            old_status = user.status

            # Update in storage
            if self.storage_type == "memory":
                updated_user = await self._memory_store.update(
                    user_id, {"status": status, "updated_at": datetime.now()}
                )
            else:
                # TODO: Implement database update
                user.status = status
                user.updated_at = datetime.now()
                updated_user = user

            # Update status index
            if old_status != status:
                if old_status in self._status_index:
                    if user_id in self._status_index[old_status]:
                        self._status_index[old_status].remove(user_id)

                if status not in self._status_index:
                    self._status_index[status] = []
                self._status_index[status].append(user_id)

            self._track_operation("update_user_status", success=True)
            logger.info(f"Updated user {user_id} status from {old_status} to {status}")

            return updated_user

        except Exception as e:
            self._track_operation("update_user_status", success=False)
            logger.error(f"Failed to update user status for {user_id}: {e}")
            raise

    async def authenticate_user(
        self, username: str, password_hash: str
    ) -> Optional[User]:
        """Authenticate user with credentials."""
        try:
            user = await self.get_user_by_username(username)
            if not user:
                self._track_operation("authenticate_user", success=False)
                return None

            # Check password hash
            if user.password_hash != password_hash:
                self._track_operation("authenticate_user", success=False)
                return None

            # Check if user is active
            if user.status != UserStatus.ACTIVE:
                self._track_operation("authenticate_user", success=False)
                return None

            # Update last login time
            await self.update_user_profile(user.id, {"last_login": datetime.now()})

            self._track_operation("authenticate_user", success=True)
            logger.info(f"User {username} authenticated successfully")

            return user

        except Exception as e:
            self._track_operation("authenticate_user", success=False)
            logger.error(f"Failed to authenticate user {username}: {e}")
            raise

    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        try:
            user_ids = self._role_index.get(role, [])
            users = []

            for user_id in user_ids:
                user = await self.get_user_by_id(user_id)
                if user:
                    users.append(user)

            self._track_operation("get_users_by_role", success=True)
            return users

        except Exception as e:
            self._track_operation("get_users_by_role", success=False)
            logger.error(f"Failed to get users by role {role}: {e}")
            raise

    async def search_users(self, search_term: str) -> List[User]:
        """Search users by username, email, or display name."""
        try:
            if self.storage_type == "memory":
                all_users = await self._memory_store.list()
            else:
                # TODO: Implement database search
                all_users = []

            # Simple text search
            matching_users = []
            search_lower = search_term.lower()

            for user in all_users:
                # Check username
                if search_lower in user.username.lower():
                    matching_users.append(user)
                    continue

                # Check email
                if search_lower in user.email.lower():
                    matching_users.append(user)
                    continue

                # Check display name if available
                if hasattr(user, "display_name") and user.display_name:
                    if search_lower in user.display_name.lower():
                        matching_users.append(user)

            self._track_operation("search_users", success=True)
            return matching_users

        except Exception as e:
            self._track_operation("search_users", success=False)
            logger.error(f"Failed to search users with term '{search_term}': {e}")
            raise

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            if self.storage_type == "memory":
                all_users = await self._memory_store.list()
            else:
                # TODO: Implement database query
                all_users = []

            total_users = len(all_users)

            if total_users == 0:
                return {
                    "total_users": 0,
                    "role_breakdown": {},
                    "status_breakdown": {},
                    "active_users": 0,
                    "new_users_today": 0,
                    "new_users_this_week": 0,
                }

            # Role breakdown
            role_breakdown = {}
            for user in all_users:
                role = user.role.value
                role_breakdown[role] = role_breakdown.get(role, 0) + 1

            # Status breakdown
            status_breakdown = {}
            for user in all_users:
                status = user.status.value
                status_breakdown[status] = status_breakdown.get(status, 0) + 1

            # Active users
            active_users = status_breakdown.get(UserStatus.ACTIVE.value, 0)

            # Time-based counts
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())

            new_users_today = len([u for u in all_users if u.created_at >= today_start])
            new_users_this_week = len(
                [u for u in all_users if u.created_at >= week_start]
            )

            self._track_operation("get_user_statistics", success=True)

            return {
                "total_users": total_users,
                "role_breakdown": role_breakdown,
                "status_breakdown": status_breakdown,
                "active_users": active_users,
                "new_users_today": new_users_today,
                "new_users_this_week": new_users_this_week,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self._track_operation("get_user_statistics", success=False)
            logger.error(f"Failed to get user statistics: {e}")
            raise

    async def _add_to_indices(self, user: User):
        """Add user to various indices for faster lookups."""
        user_id = user.id

        # Username index
        self._username_index[user.username] = user_id

        # Email index
        self._email_index[user.email] = user_id

        # Role index
        role = user.role
        if role not in self._role_index:
            self._role_index[role] = []
        self._role_index[role].append(user_id)

        # Status index
        status = user.status
        if status not in self._status_index:
            self._status_index[status] = []
        self._status_index[status].append(user_id)

    async def _remove_from_indices(self, user: User):
        """Remove user from all indices."""
        user_id = user.id

        # Remove from username index
        if user.username in self._username_index:
            del self._username_index[user.username]

        # Remove from email index
        if user.email in self._email_index:
            del self._email_index[user.email]

        # Remove from role index
        role = user.role
        if role in self._role_index and user_id in self._role_index[role]:
            self._role_index[role].remove(user_id)

        # Remove from status index
        status = user.status
        if status in self._status_index and user_id in self._status_index[status]:
            self._status_index[status].remove(user_id)
