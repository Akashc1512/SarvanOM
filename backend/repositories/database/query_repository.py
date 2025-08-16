"""
Query Repository - PostgreSQL Implementation

This module provides a PostgreSQL-based query repository with:
- Query CRUD operations
- Query search and filtering
- Query history and analytics
- User query tracking
- Query status management
- Performance optimization

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, text, case
from sqlalchemy.orm import Session, joinedload

import structlog

from shared.core.database.repository import (
    BaseRepository, QueryOptions, FilterCondition, SortCondition,
    FilterOperator, SortOrder
)
from shared.models.models import Query, User, RecordStatus

logger = structlog.get_logger(__name__)


class QueryRepository(BaseRepository[Query]):
    """
    PostgreSQL-based query repository implementation.
    
    Provides query management functionality including:
    - Query CRUD operations
    - Query search and filtering
    - Query history and analytics
    - User query tracking
    - Query status management
    """

    def __init__(self, db_name: str = "primary"):
        """Initialize the query repository."""
        super().__init__(Query, db_name)

    async def create_query(
        self,
        user_id: str,
        query_text: str,
        query_type: str = "search",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Query:
        """Create a new query."""
        query = Query(
            user_id=user_id,
            query_text=query_text,
            query_type=query_type,
            context=context or {},
            **kwargs
        )

        return await self.create(query)

    async def get_queries_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Get queries by user with pagination."""
        async def _get_queries_by_user(session: Session) -> Tuple[List[Query], int]:
            # Count query
            count_query = select(func.count()).select_from(Query).where(Query.user_id == user_id)
            
            if not include_deleted:
                count_query = count_query.where(Query.deleted_at.is_(None))
            
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(Query.user_id == user_id)
                .order_by(Query.created_at.desc())
            )
            
            if not include_deleted:
                query = query.where(Query.deleted_at.is_(None))
            
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_get_queries_by_user)

    async def get_recent_queries(
        self,
        user_id: str,
        limit: int = 10,
        include_deleted: bool = False
    ) -> List[Query]:
        """Get recent queries for a user."""
        async def _get_recent_queries(session: Session) -> List[Query]:
            query = (
                select(Query)
                .where(Query.user_id == user_id)
                .order_by(Query.created_at.desc())
                .limit(limit)
            )
            
            if not include_deleted:
                query = query.where(Query.deleted_at.is_(None))
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_recent_queries)

    async def search_queries(
        self,
        search_term: str,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Search queries by text content."""
        async def _search_queries(session: Session) -> Tuple[List[Query], int]:
            search_like = f"%{search_term}%"
            
            # Build where conditions
            where_conditions = [Query.query_text.ilike(search_like)]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            # Count query
            count_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_search_queries)

    async def get_queries_by_status(
        self,
        status: str,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Get queries by status."""
        async def _get_queries_by_status(session: Session) -> Tuple[List[Query], int]:
            # Build where conditions
            where_conditions = [Query.status == status]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            # Count query
            count_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_get_queries_by_status)

    async def get_queries_by_type(
        self,
        query_type: str,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Get queries by type."""
        async def _get_queries_by_type(session: Session) -> Tuple[List[Query], int]:
            # Build where conditions
            where_conditions = [Query.query_type == query_type]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            # Count query
            count_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_get_queries_by_type)

    async def get_popular_queries(
        self,
        days: int = 7,
        limit: int = 20,
        user_id: Optional[str] = None
    ) -> List[Tuple[str, int]]:
        """Get popular queries based on frequency."""
        async def _get_popular_queries(session: Session) -> List[Tuple[str, int]]:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Build where conditions
            where_conditions = [Query.created_at >= cutoff_date]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            where_conditions.append(Query.deleted_at.is_(None))
            
            query = (
                select(Query.query_text, func.count(Query.id).label('count'))
                .where(and_(*where_conditions))
                .group_by(Query.query_text)
                .order_by(func.count(Query.id).desc())
                .limit(limit)
            )
            
            result = session.execute(query)
            return [(row.query_text, row.count) for row in result]

        return await self._execute_with_retry(_get_popular_queries)

    async def get_query_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get query analytics and statistics."""
        async def _get_query_analytics(session: Session) -> Dict[str, Any]:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Build where conditions
            where_conditions = [Query.created_at >= cutoff_date]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            where_conditions.append(Query.deleted_at.is_(None))
            
            # Total queries
            total_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_queries = session.execute(total_query).scalar()
            
            # Queries by status
            status_query = (
                select(Query.status, func.count(Query.id))
                .where(and_(*where_conditions))
                .group_by(Query.status)
            )
            status_result = session.execute(status_query)
            queries_by_status = {row.status: row.count for row in status_result}
            
            # Queries by type
            type_query = (
                select(Query.query_type, func.count(Query.id))
                .where(and_(*where_conditions))
                .group_by(Query.query_type)
            )
            type_result = session.execute(type_query)
            queries_by_type = {row.query_type: row.count for row in type_result}
            
            # Average response time
            avg_time_query = (
                select(func.avg(Query.response_time))
                .where(and_(*where_conditions, Query.response_time.is_not(None)))
            )
            avg_response_time = session.execute(avg_time_query).scalar()
            
            # Queries per day
            daily_query = (
                select(
                    func.date(Query.created_at).label('date'),
                    func.count(Query.id).label('count')
                )
                .where(and_(*where_conditions))
                .group_by(func.date(Query.created_at))
                .order_by(func.date(Query.created_at))
            )
            daily_result = session.execute(daily_query)
            queries_per_day = {str(row.date): row.count for row in daily_result}
            
            return {
                "total_queries": total_queries,
                "queries_by_status": queries_by_status,
                "queries_by_type": queries_by_type,
                "avg_response_time": float(avg_response_time) if avg_response_time else 0,
                "queries_per_day": queries_per_day,
                "period_days": days
            }

        return await self._execute_with_retry(_get_query_analytics)

    async def update_query_status(self, query_id: str, status: str, **kwargs) -> bool:
        """Update query status and related fields."""
        async def _update_query_status(session: Session) -> bool:
            query = session.get(Query, query_id)
            if not query:
                return False

            query.status = status
            query.updated_at = datetime.now(timezone.utc)
            
            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(query, key):
                    setattr(query, key, value)

            session.flush()
            return True

        return await self._execute_with_retry(_update_query_status)

    async def update_query_response(
        self,
        query_id: str,
        response: Dict[str, Any],
        response_time: Optional[float] = None
    ) -> bool:
        """Update query with response data."""
        async def _update_query_response(session: Session) -> bool:
            query = session.get(Query, query_id)
            if not query:
                return False

            query.response = response
            if response_time is not None:
                query.response_time = response_time
            query.updated_at = datetime.now(timezone.utc)

            session.flush()
            return True

        return await self._execute_with_retry(_update_query_response)

    async def get_queries_with_responses(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Get queries that have responses."""
        async def _get_queries_with_responses(session: Session) -> Tuple[List[Query], int]:
            # Build where conditions
            where_conditions = [Query.response.is_not(None)]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            # Count query
            count_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_get_queries_with_responses)

    async def get_failed_queries(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[Query], int]:
        """Get queries that failed."""
        async def _get_failed_queries(session: Session) -> Tuple[List[Query], int]:
            # Build where conditions
            where_conditions = [Query.status == "failed"]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            # Count query
            count_query = select(func.count()).select_from(Query).where(and_(*where_conditions))
            total_count = session.execute(count_query).scalar()
            
            # Results query
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            result = session.execute(query)
            queries = result.scalars().all()
            
            return queries, total_count

        return await self._execute_with_retry(_get_failed_queries)

    async def get_queries_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Query]:
        """Get queries within a date range."""
        async def _get_queries_by_date_range(session: Session) -> List[Query]:
            # Build where conditions
            where_conditions = [
                Query.created_at >= start_date,
                Query.created_at <= end_date
            ]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            if not include_deleted:
                where_conditions.append(Query.deleted_at.is_(None))
            
            query = (
                select(Query)
                .where(and_(*where_conditions))
                .order_by(Query.created_at.desc())
            )
            
            result = session.execute(query)
            return result.scalars().all()

        return await self._execute_with_retry(_get_queries_by_date_range)

    async def get_query_trends(
        self,
        days: int = 30,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get query trends over time."""
        async def _get_query_trends(session: Session) -> Dict[str, Any]:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Build where conditions
            where_conditions = [Query.created_at >= cutoff_date]
            
            if user_id:
                where_conditions.append(Query.user_id == user_id)
            
            where_conditions.append(Query.deleted_at.is_(None))
            
            # Daily trends
            daily_trends_query = (
                select(
                    func.date(Query.created_at).label('date'),
                    func.count(Query.id).label('total'),
                    func.count(case((Query.status == 'completed', 1))).label('completed'),
                    func.count(case((Query.status == 'failed', 1))).label('failed'),
                    func.avg(Query.response_time).label('avg_response_time')
                )
                .where(and_(*where_conditions))
                .group_by(func.date(Query.created_at))
                .order_by(func.date(Query.created_at))
            )
            
            daily_result = session.execute(daily_trends_query)
            daily_trends = []
            for row in daily_result:
                daily_trends.append({
                    "date": str(row.date),
                    "total": row.total,
                    "completed": row.completed,
                    "failed": row.failed,
                    "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0
                })
            
            # Hourly trends (for last 7 days)
            hourly_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            hourly_where_conditions = [Query.created_at >= hourly_cutoff]
            
            if user_id:
                hourly_where_conditions.append(Query.user_id == user_id)
            
            hourly_where_conditions.append(Query.deleted_at.is_(None))
            
            hourly_trends_query = (
                select(
                    func.extract('hour', Query.created_at).label('hour'),
                    func.count(Query.id).label('count')
                )
                .where(and_(*hourly_where_conditions))
                .group_by(func.extract('hour', Query.created_at))
                .order_by(func.extract('hour', Query.created_at))
            )
            
            hourly_result = session.execute(hourly_trends_query)
            hourly_trends = {int(row.hour): row.count for row in hourly_result}
            
            return {
                "daily_trends": daily_trends,
                "hourly_trends": hourly_trends,
                "period_days": days
            }

        return await self._execute_with_retry(_get_query_trends)

    async def cleanup_old_queries(self, days: int = 90) -> int:
        """Clean up old queries (soft delete)."""
        async def _cleanup_old_queries(session: Session) -> int:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Find old queries
            old_queries_query = (
                select(Query.id)
                .where(
                    and_(
                        Query.created_at < cutoff_date,
                        Query.deleted_at.is_(None)
                    )
                )
            )
            
            old_query_ids = session.execute(old_queries_query).scalars().all()
            
            if not old_query_ids:
                return 0
            
            # Soft delete old queries
            update_query = (
                Query.__table__.update()
                .where(Query.id.in_(old_query_ids))
                .values(
                    deleted_at=datetime.now(timezone.utc),
                    status=RecordStatus.DELETED,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            
            result = session.execute(update_query)
            session.flush()
            
            return len(old_query_ids)

        return await self._execute_with_retry(_cleanup_old_queries)


# Export the repository class
__all__ = ["QueryRepository"]
