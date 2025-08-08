"""
Agent Services Package

This package contains service layer implementations for all agent functionality.
Services separate business logic from route handlers and provide a clean interface
for agent operations.
"""

from .base_service import BaseAgentService
from .browser_service import BrowserService
from .pdf_service import PDFService
from .knowledge_service import KnowledgeService
from .code_service import CodeService
from .database_service import DatabaseService
from .crawler_service import CrawlerService
from .service_factory import ServiceFactory
from .health_service import HealthService
from .sso_service import SSOService, sso_service
from .multi_tenant_service import MultiTenantService, multi_tenant_service
from .advanced_analytics_service import AdvancedAnalyticsService, advanced_analytics_service

# Create service instances
health_service = HealthService()

__all__ = [
    "BaseAgentService",
    "BrowserService", 
    "PDFService",
    "KnowledgeService",
    "CodeService",
    "DatabaseService",
    "CrawlerService",
    "ServiceFactory",
    "health_service",
    "sso_service",
    "multi_tenant_service",
    "advanced_analytics_service"
] 