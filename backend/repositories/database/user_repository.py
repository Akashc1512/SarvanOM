"""
User Repository - PostgreSQL Implementation

This module provides a PostgreSQL-based user repository with:
- User CRUD operations
- Authentication and authorization
- User search and filtering
- Role management
- Session management
- Audit trail integration

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import Session, joinedload

import structlog

from shared.core.database.repository import (
    BaseRepository, QueryOptions, FilterCondition, SortCondition,
    FilterOperator, SortOrder
)
from shared.models.models import User, Role, UserSession, RecordStatus
from shared.core.auth.password_hasher import PasswordHasher

logger = structlog.get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    PostgreSQL-based user repository implementation.
    
    Provides user management functionality including:
    - User CRUD operations
    - Authentication and authorization
    - User search and filtering
    - Role management
    - Session management
    """

    def __init__(self, db_name: str = "primary"):
        """Initialize the user repository."""
        super().__init__(User, db_name)
        self.password_hasher = PasswordHasher()

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create a new user with password hashing."""
        # Check for existing user
        existing_user = await self.get_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")

        existing_email = await self.get_by_email(email)
        if existing_email:
            raise ValueError(f"Email '{email}' already exists")

        # Hash password
        password_hash = self.password_hasher.hash_password(password)

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            **kwargs
        )

        return await self.create(user)

    async def get_by_username(self, username: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by username."""
        async def _get_by_username(session: Session) -> Optional[User]:
            query = select(User).where(User.username == username)
            
            if not include_deleted:
                query = query.where(User.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_retry(_get_by_username)

    async def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email."""
        async def _get_by_email(session: Session) -> Optional[User]:
            query = select(User).where(User.email == email)
            
            if not include_deleted:
                query = query.where(User.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalar_one_or_none()

        return await self._execute_with_retry(_get_by_email)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password."""
        # Try username first, then email
        user = await self.get_by_username(username)
        if not user:
            user = await self.get_by_email(username)

        if not user:
            return None

        # Check if user is active
        if user.status != RecordStatus.ACTIVE:
            logger.warning(f"Authentication failed for inactive user: {username}")
            return None

        # Verify password
        if not self.password_hasher.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed for user: {username}")
            return None

        # Update last login
        await self.update_last_login(user.id)

        return user

    async def update_last_login(self, user_id: str, ip_address: Optional[str] = None) -> bool:
        """Update user's last login information."""
        async def _update_last_login(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.last_login_at = datetime.now(timezone.utc)
            if ip_address:
                user.last_login_ip = ip_address
            user.login_count += 1

            session.flush()
            return True

        return await self._execute_with_retry(_update_last_login)

    async def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user's password."""
        async def _change_password(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            # Hash new password
            password_hash = self.password_hasher.hash_password(new_password)
            user.password_hash = password_hash
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_change_password)

    async def search_users(
        self,
        search_term: str,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[User], int]:
        """Search users by username, email, or full name."""
        async def _search_users(session: Session) -> Tuple[List[User], int]:
            # Build search query
            search_like = f"%{search_term}%"
            
            # Count query
            count_query = select(func.count()).select_from(User).where(
                or_(
                    User.username.ilike(search_like),
                    User.email.ilike(search_like),
                    User.full_name.ilike(search_like)
                )
            )
            
            if not include_deleted:
                count_query = count_query.where(User.deleted_at.is_(None))
            
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = select(User).where(
                or_(
                    User.username.ilike(search_like),
                    User.email.ilike(search_like),
                    User.full_name.ilike(search_like)
                )
            )
            
            if not include_deleted:
                query = query.where(User.deleted_at.is_(None))
            
            query = query.order_by(User.username).offset((page - 1) * page_size).limit(page_size)
            
            result = session.execute(query)
            users = result.scalars().all()
            
            return users, total_count

        return await self._execute_with_retry(_search_users)

    async def get_users_by_role(self, role_name: str, include_deleted: bool = False) -> List[User]:
        """Get all users with a specific role."""
        async def _get_users_by_role(session: Session) -> List[User]:
            query = (
                select(User)
                .join(User.roles)
                .where(Role.name == role_name)
            )
            
            if not include_deleted:
                query = query.where(User.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_users_by_role)

    async def get_active_users(self, limit: Optional[int] = None) -> List[User]:
        """Get all active users."""
        async def _get_active_users(session: Session) -> List[User]:
            query = (
                select(User)
                .where(User.status == RecordStatus.ACTIVE)
                .where(User.deleted_at.is_(None))
                .order_by(User.created_at.desc())
            )
            
            if limit:
                query = query.limit(limit)
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_active_users)

    async def get_users_by_status(self, status: RecordStatus, include_deleted: bool = False) -> List[User]:
        """Get users by status."""
        async def _get_users_by_status(session: Session) -> List[User]:
            query = select(User).where(User.status == status)
            
            if not include_deleted:
                query = query.where(User.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_users_by_status)

    async def get_recent_users(self, days: int = 7) -> List[User]:
        """Get users created in the last N days."""
        async def _get_recent_users(session: Session) -> List[User]:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = (
                select(User)
                .where(User.created_at >= cutoff_date)
                .where(User.deleted_at.is_(None))
                .order_by(User.created_at.desc())
            )
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_recent_users)

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        async def _get_user_stats(session: Session) -> Dict[str, Any]:
            # Total users
            total_query = select(func.count()).select_from(User).where(User.deleted_at.is_(None))
            total_users = session.execute(total_query).scalar()
            
            # Active users
            active_query = select(func.count()).select_from(User).where(
                and_(User.status == RecordStatus.ACTIVE, User.deleted_at.is_(None))
            )
            active_users = session.execute(active_query).scalar()
            
            # Users created today
            today = datetime.now(timezone.utc).date()
            today_query = select(func.count()).select_from(User).where(
                and_(
                    func.date(User.created_at) == today,
                    User.deleted_at.is_(None)
                )
            )
            users_today = session.execute(today_query).scalar()
            
            # Users created this week
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            week_query = select(func.count()).select_from(User).where(
                and_(
                    User.created_at >= week_ago,
                    User.deleted_at.is_(None)
                )
            )
            users_this_week = session.execute(week_query).scalar()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "users_today": users_today,
                "users_this_week": users_this_week,
                "inactive_users": total_users - active_users
            }

        return await self._execute_with_retry(_get_user_stats)

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        async def _deactivate_user(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.status = RecordStatus.INACTIVE
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_deactivate_user)

    async def activate_user(self, user_id: str) -> bool:
        """Activate a user."""
        async def _activate_user(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.status = RecordStatus.ACTIVE
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_activate_user)

    async def verify_email(self, user_id: str, verification_token: str) -> bool:
        """Verify user's email address."""
        async def _verify_email(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            if user.email_verification_token != verification_token:
                return False

            user.email_verified = True
            user.email_verification_token = None
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_verify_email)

    async def set_email_verification_token(self, user_id: str, token: str) -> bool:
        """Set email verification token."""
        async def _set_token(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.email_verification_token = token
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_set_token)

    async def enable_two_factor(self, user_id: str, secret: str) -> bool:
        """Enable two-factor authentication for a user."""
        async def _enable_2fa(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.two_factor_enabled = True
            user.two_factor_secret = secret
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_enable_2fa)

    async def disable_two_factor(self, user_id: str) -> bool:
        """Disable two-factor authentication for a user."""
        async def _disable_2fa(session: Session) -> bool:
            user = session.get(User, user_id)
            if not user:
                return False

            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_disable_2fa)


# Export the repository class
__all__ = ["UserRepository"]
