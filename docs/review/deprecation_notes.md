# Deprecation Notes - SarvanOM v2

**Generated**: 2025-09-14T14:37:17.140873
**Purpose**: Proposed safe moves to /deprecated/ directory

## Backend Deprecations

### High Priority

**File**: `services\crud\main.py`
**Symbol**: GET /
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: endpoint duplication

**File**: `services\cicd\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\feeds\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\model_router\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: endpoint duplication

**File**: `services\observability\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: endpoint duplication

**File**: `services\retrieval\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /health
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /analytics
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\cicd\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\feeds\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\model_router\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: endpoint duplication

**File**: `services\observability\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: endpoint duplication

**File**: `services\retrieval\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /ready
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\cicd\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\feeds\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\model_router\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: endpoint duplication

**File**: `services\observability\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: endpoint duplication

**File**: `services\retrieval\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /config
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\cicd\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\feeds\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\model_router\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: endpoint duplication

**File**: `services\observability\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: endpoint duplication

**File**: `services\retrieval\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /version
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\security\main.py`
**Symbol**: GET /_debug/trace
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: endpoint duplication

**File**: `services\gateway\main.py`
**Symbol**: GET /health/detailed
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: endpoint duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: POST /query
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: endpoint duplication

**File**: `services\synthesis\main.py`
**Symbol**: POST /synthesize
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: endpoint duplication

**File**: `services\model_registry\main.py`
**Symbol**: GET /models
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: endpoint duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: POST /settings
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: endpoint duplication

**File**: `services\crud\main.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: circular duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: circular duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: circular duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: circular duplication

**File**: `services\fact_check\routes.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\fact_check\routes.py`
**Reason**: circular duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: circular duplication

**File**: `services\gateway\routes.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: circular duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: circular duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: circular duplication

**File**: `services\monitoring\health.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\analytics.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\analytics.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\utilities\validation_utilities.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\utilities\validation_utilities.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics\knowledge_platform_metrics.py`
**Reason**: circular duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_config.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_config.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_invalidation.py`
**Symbol**: circular import shared.core.unified_logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_invalidation.py`
**Reason**: circular duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\core\base_agent.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\models\models.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: circular duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\analytics.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\analytics.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `shared\core\vector_database.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: circular duplication

**File**: `services\gateway\analytics_collector.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\analytics_collector.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\api\config.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import dotenv
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: circular duplication

**File**: `services\analytics\analytics.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\analytics.py`
**Reason**: circular duplication

**File**: `shared\core\health_checker.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: circular duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `shared\core\logging_config.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import shared.core.api.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: circular duplication

**File**: `shared\core\repository.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: circular duplication

**File**: `shared\core\interfaces.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: circular duplication

**File**: `shared\core\error_handler.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: circular duplication

**File**: `shared\core\observer.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: circular duplication

**File**: `shared\core\base_agent.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: circular duplication

**File**: `shared\core\database\repository.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: circular duplication

**File**: `shared\contracts\service_contracts.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\contracts\service_contracts.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: circular duplication

**File**: `services\analytics\feedback_storage.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\feedback_storage.py`
**Reason**: circular duplication

**File**: `shared\core\decorator.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import abc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\services\analytics_dashboard_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\analytics_dashboard_service.py`
**Reason**: circular duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\error_handler.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: circular duplication

**File**: `shared\core\error_handling.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: circular duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: circular duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: circular duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: circular duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\stooq_provider.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\stooq_provider.py`
**Reason**: circular duplication

**File**: `shared\core\logging_config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: circular duplication

**File**: `services\security\security_middleware.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: circular duplication

**File**: `services\analytics\feedback_storage.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\feedback_storage.py`
**Reason**: circular duplication

**File**: `services\auth\routes.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\routes.py`
**Reason**: circular duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\gdelt_provider.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\gdelt_provider.py`
**Reason**: circular duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: circular duplication

**File**: `services\retrieval\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: circular duplication

**File**: `shared\models\models.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: circular duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: circular duplication

**File**: `shared\core\services\meilisearch_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\meilisearch_service.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\guardian_provider.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\guardian_provider.py`
**Reason**: circular duplication

**File**: `shared\core\database\connection.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: circular duplication

**File**: `shared\ci\provider_key_validator.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\ci\provider_key_validator.py`
**Reason**: circular duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: circular duplication

**File**: `shared\core\workflow_manager.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\workflow_manager.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\observability\fallback_metrics.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\observability\fallback_metrics.py`
**Reason**: circular duplication

**File**: `shared\core\input_validation.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: circular duplication

**File**: `shared\core\migrations.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\migrations.py`
**Reason**: circular duplication

**File**: `shared\core\services\multilanguage_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multilanguage_service.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\hn_algolia_provider.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\hn_algolia_provider.py`
**Reason**: circular duplication

**File**: `shared\core\services\cost_aware_llm_router.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\cost_aware_llm_router.py`
**Reason**: circular duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: circular duplication

**File**: `shared\core\database\repository.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: circular duplication

**File**: `shared\core\services\advanced_citations_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\advanced_citations_service.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\sec_edgar_provider.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\sec_edgar_provider.py`
**Reason**: circular duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: circular duplication

**File**: `services\model_router\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: circular duplication

**File**: `shared\core\system_health.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\services\llm_cost_optimizer.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\llm_cost_optimizer.py`
**Reason**: circular duplication

**File**: `shared\repositories\database\user_repository.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\repositories\database\user_repository.py`
**Reason**: circular duplication

**File**: `shared\ci\ci_gates.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\ci\ci_gates.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `shared\core\auth\password_hasher.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\auth\password_hasher.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `shared\core\api\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: circular duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: circular duplication

**File**: `services\feeds\config.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\config.py`
**Reason**: circular duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: circular duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: circular import structlog
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\analytics\feedback_storage.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\feedback_storage.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `shared\core\app_factory.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: circular duplication

**File**: `services\model_registry\feeds_router.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_router.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\observability\fallback_metrics.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\observability\fallback_metrics.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\routing_router.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\routing_router.py`
**Reason**: circular duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: circular duplication

**File**: `services\model_registry\search_router.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\search_router.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics\knowledge_platform_metrics.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import prometheus_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `shared\core\graceful_degradation.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\graceful_degradation.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: circular duplication

**File**: `shared\core\health_checker.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: circular duplication

**File**: `services\retrieval\youtube_retrieval.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\youtube_retrieval.py`
**Reason**: circular duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: circular duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: circular import aiohttp
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\core\health_checker.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: circular duplication

**File**: `shared\core\base_agent.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\auth\routes.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\routes.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\core\app_factory.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: circular duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: circular duplication

**File**: `shared\core\database\connection.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import shared.core.config.central_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import shared.core.llm_client_v3
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import shared.core.llm_client_v3
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import shared.core.llm_client_v3
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: circular import aioredis
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: circular duplication

**File**: `shared\core\base_agent.py`
**Symbol**: circular import aioredis
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import aioredis
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\vector_database.py`
**Symbol**: circular import pinecone
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: circular duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: circular import pinecone
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: circular duplication

**File**: `shared\core\services\analytics_dashboard_service.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\analytics_dashboard_service.py`
**Reason**: circular duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: circular duplication

**File**: `services\gateway\routes.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: circular duplication

**File**: `services\analytics\metrics.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: circular duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: circular duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: circular duplication

**File**: `shared\core\system_health.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: circular duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `services\monitoring\health.py`
**Symbol**: circular import psutil
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: circular duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\core\error_handler.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: circular duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: circular duplication

**File**: `shared\core\logging_config.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager_postgres.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager_postgres.py`
**Reason**: circular duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: circular duplication

**File**: `shared\core\cache_manager_postgres.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache_manager_postgres.py`
**Reason**: circular duplication

**File**: `shared\core\database.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: circular duplication

**File**: `shared\core\app_factory.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: circular duplication

**File**: `shared\core\sla_budget_enforcer.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\sla_budget_enforcer.py`
**Reason**: circular duplication

**File**: `shared\core\database\connection.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `shared\core\database\repository.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: circular duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `shared\core\graceful_degradation.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\graceful_degradation.py`
**Reason**: circular duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: circular import contextlib
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import opentelemetry
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\contracts\query.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\contracts\query.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: circular duplication

**File**: `shared\clients\microservices.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\microservices.py`
**Reason**: circular duplication

**File**: `shared\embeddings\local_embedder.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\embeddings\local_embedder.py`
**Reason**: circular duplication

**File**: `services\retrieval\wiki.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\wiki.py`
**Reason**: circular duplication

**File**: `services\auth\main.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\main.py`
**Reason**: circular duplication

**File**: `services\fact_check\main.py`
**Symbol**: circular import __future__
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\fact_check\main.py`
**Reason**: circular duplication

**File**: `services\auth\main.py`
**Symbol**: circular import shared.core.app_factory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\main.py`
**Reason**: circular duplication

**File**: `services\fact_check\main.py`
**Symbol**: circular import shared.core.app_factory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\fact_check\main.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import shared.core.app_factory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import shared.core.app_factory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `services\auth\main.py`
**Symbol**: circular import services.auth.routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.auth.routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `shared\core\app_factory.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\auth\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\main.py`
**Reason**: circular duplication

**File**: `services\fact_check\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\fact_check\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import uvicorn
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\gateway\routes.py`
**Symbol**: circular import shared.core.api.api_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: circular duplication

**File**: `shared\clients\microservices.py`
**Symbol**: circular import shared.core.api.api_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\microservices.py`
**Reason**: circular duplication

**File**: `services\auth\routes.py`
**Symbol**: circular import shared.core.api.api_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\routes.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import shared.core.api.api_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: circular duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: circular duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager_postgres.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager_postgres.py`
**Reason**: circular duplication

**File**: `services\auth\routes.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auth\routes.py`
**Reason**: circular duplication

**File**: `shared\core\cache_manager_postgres.py`
**Symbol**: circular import shared.core.database
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache_manager_postgres.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import opentelemetry.exporter.jaeger.thrift
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import opentelemetry.sdk.trace
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import opentelemetry.sdk.trace.export
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: circular duplication

**File**: `services\observability\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\model_router\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: circular duplication

**File**: `services\security\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import opentelemetry.instrumentation.fastapi
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `shared\core\migrations.py`
**Symbol**: circular import subprocess
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\migrations.py`
**Reason**: circular duplication

**File**: `services\cicd\main.py`
**Symbol**: circular import subprocess
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: circular duplication

**File**: `shared\core\system_health.py`
**Symbol**: circular import subprocess
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import subprocess
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\contracts\service_contracts.py`
**Symbol**: circular import shared.models.crud_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\contracts\service_contracts.py`
**Reason**: circular duplication

**File**: `shared\clients\service_client.py`
**Symbol**: circular import shared.models.crud_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\service_client.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.models.crud_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import shared.models.crud_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `shared\clients\service_client.py`
**Symbol**: circular import shared.contracts.service_contracts
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\service_client.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.contracts.service_contracts
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import shared.contracts.service_contracts
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\observability.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\observability.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\security\security_middleware.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: circular import starlette.middleware.base
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.windows_compatibility
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\crud\main.py`
**Symbol**: circular import shared.core.windows_compatibility
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: circular duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: circular import routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: circular duplication

**File**: `services\fact_check\main.py`
**Symbol**: circular import routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\fact_check\main.py`
**Reason**: circular duplication

**File**: `services\feeds\attribution_manager.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\attribution_manager.py`
**Reason**: circular duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: circular duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\database\connection.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: circular duplication

**File**: `shared\core\evidence_quality_validator.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\evidence_quality_validator.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\input_validation.py`
**Symbol**: circular import urllib.parse
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\feeds\config.py`
**Symbol**: circular import shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\config.py`
**Reason**: circular duplication

**File**: `services\feeds\main.py`
**Symbol**: circular import shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: circular import shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: circular duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\gateway\background_processor.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\background_processor.py`
**Reason**: circular duplication

**File**: `services\gateway\prompt_optimizer.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\prompt_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import pickle
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import gzip
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: circular import gzip
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\cache.py`
**Symbol**: circular import gzip
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: circular duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\gateway\citations.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\citations.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\fallback_vector_db.py`
**Symbol**: circular import numpy
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\fallback_vector_db.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import sklearn.feature_extraction.text
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: circular import sklearn.feature_extraction.text
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import sklearn.metrics.pairwise
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: circular import sklearn.metrics.pairwise
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import services.gateway.cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: circular import services.gateway.streaming_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.streaming_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\routes.py`
**Symbol**: circular import real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: circular duplication

**File**: `services\gateway\agent_orchestrator.py`
**Symbol**: circular import real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\agent_orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\agent_orchestrator.py`
**Symbol**: circular import traceback
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\agent_orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\error_handler.py`
**Symbol**: circular import traceback
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: circular duplication

**File**: `shared\core\error_handling.py`
**Symbol**: circular import traceback
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\analytics_collector.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\analytics_collector.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: circular duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `services\retrieval\wiki.py`
**Symbol**: circular import requests
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\wiki.py`
**Reason**: circular duplication

**File**: `shared\core\system_health.py`
**Symbol**: circular import concurrent.futures
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: circular duplication

**File**: `services\gateway\background_processor.py`
**Symbol**: circular import concurrent.futures
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\background_processor.py`
**Reason**: circular duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: circular import concurrent.futures
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: circular duplication

**File**: `services\gateway\background_processor.py`
**Symbol**: circular import queue
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\background_processor.py`
**Reason**: circular duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: circular import queue
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\background_processor.py`
**Symbol**: circular import signal
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\background_processor.py`
**Reason**: circular duplication

**File**: `shared\core\shutdown_handler.py`
**Symbol**: circular import signal
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\shutdown_handler.py`
**Reason**: circular duplication

**File**: `services\retrieval\routers\free_tier_router.py`
**Symbol**: circular import services.retrieval.free_tier
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\routers\free_tier_router.py`
**Reason**: circular duplication

**File**: `services\gateway\streaming_manager.py`
**Symbol**: circular import services.retrieval.free_tier
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\streaming_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\citations.py`
**Symbol**: circular import services.retrieval.free_tier
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\citations.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.retrieval.free_tier
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: circular import sentence_transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: circular duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: circular import sentence_transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: circular duplication

**File**: `shared\embeddings\local_embedder.py`
**Symbol**: circular import sentence_transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\embeddings\local_embedder.py`
**Reason**: circular duplication

**File**: `services\gateway\citations.py`
**Symbol**: circular import sentence_transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\citations.py`
**Reason**: circular duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: circular import sentence_transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: circular duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: circular import transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: circular duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: circular import transformers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: circular duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: circular import torch
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: circular duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: circular import torch
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import services.gateway.middleware.observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.middleware.observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\resilience\graceful_degradation.py`
**Symbol**: circular import services.gateway.middleware.observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\graceful_degradation.py`
**Reason**: circular duplication

**File**: `services\gateway\streaming_manager.py`
**Symbol**: circular import services.gateway.middleware.observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\streaming_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\metrics_endpoint.py`
**Symbol**: circular import services.gateway.middleware.observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\metrics_endpoint.py`
**Reason**: circular duplication

**File**: `services\gateway\health\comprehensive_monitor.py`
**Symbol**: circular import services.gateway.resilience.circuit_breaker
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\health\comprehensive_monitor.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.resilience.circuit_breaker
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\resilience\graceful_degradation.py`
**Symbol**: circular import services.gateway.resilience.circuit_breaker
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\graceful_degradation.py`
**Reason**: circular duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\services\cost_aware_llm_router.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\cost_aware_llm_router.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `services\gateway\streaming_manager.py`
**Symbol**: circular import services.gateway.real_llm_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\streaming_manager.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import services.gateway.routes
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `services\gateway\metrics_router.py`
**Symbol**: circular import services.gateway.model_router
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\metrics_router.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.model_router
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import services.gateway.huggingface_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\huggingface_client.py`
**Symbol**: circular import services.gateway.huggingface_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\huggingface_client.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.gateway.huggingface_integration
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\search_router.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\search_router.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: circular duplication

**File**: `services\model_registry\refine_router.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\refine_router.py`
**Reason**: circular duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: circular import random
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: circular duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: circular import shared.core.services.arangodb_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: circular duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import shared.core.services.vector_singleton_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import shared.core.services.index_fabric_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.index_fabric_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import shared.core.services.meilisearch_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: circular import shared.core.services.meilisearch_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.meilisearch_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import shared.core.services.retrieval_aggregator
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\retrieval_router.py`
**Symbol**: circular import shared.core.services.retrieval_aggregator
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\retrieval_router.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.retrieval_aggregator
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\citations_router.py`
**Symbol**: circular import shared.core.services.citations_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\citations_router.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.services.citations_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import shared.embeddings.local_embedder
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.embeddings.local_embedder
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\gateway\model_router.py`
**Symbol**: circular import shared.core.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\model_router.py`
**Reason**: circular duplication

**File**: `shared\clients\microservices.py`
**Symbol**: circular import shared.core.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\microservices.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import shared.core.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\feeds\providers\stooq_provider.py`
**Symbol**: circular import io
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\feeds\providers\stooq_provider.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import io
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import services.retrieval.youtube_retrieval
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\main.py`
**Symbol**: circular import services.retrieval.youtube_retrieval
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: circular duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\core\app_factory.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: circular duplication

**File**: `services\gateway\model_router.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\model_router.py`
**Reason**: circular duplication

**File**: `services\search\main.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\search\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: circular duplication

**File**: `services\gateway\metrics_router.py`
**Symbol**: circular import shared.core.logging
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\metrics_router.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import services.gateway.providers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: circular import services.gateway.providers
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import shared.llm.provider_order
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: circular import shared.llm.provider_order
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\registry.py`
**Symbol**: circular import shared.llm.provider_order
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\registry.py`
**Reason**: circular duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: circular import shared.llm.provider_order
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: circular duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: circular import shared.llm.provider_order
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import openai
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\openai_client.py`
**Symbol**: circular import openai
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\openai_client.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: circular import openai
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: circular duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: circular import anthropic
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\anthropic_client.py`
**Symbol**: circular import anthropic
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\anthropic_client.py`
**Reason**: circular duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: circular import anthropic
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import shared.contracts.query
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `services\gateway\routes.py`
**Symbol**: circular import shared.contracts.query
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import shared.contracts.query
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import shared.contracts.query
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `shared\clients\microservices.py`
**Symbol**: circular import shared.contracts.query
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\clients\microservices.py`
**Reason**: circular duplication

**File**: `services\retrieval\config.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: circular duplication

**File**: `services\model_router\config.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: circular duplication

**File**: `services\model_registry\config.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: circular duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: circular import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: circular duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: circular import shared.core.agents.knowledge_graph_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import shared.core.agents.knowledge_graph_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: circular import shared.core.agents.knowledge_graph_service
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\feeds_router.py`
**Symbol**: circular import feeds_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_router.py`
**Reason**: circular duplication

**File**: `services\model_registry\feeds_adapters.py`
**Symbol**: circular import feeds_models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_adapters.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import feeds_adapters
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\model_registry\feeds_router.py`
**Symbol**: circular import feeds_adapters
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_router.py`
**Reason**: circular duplication

**File**: `services\model_registry\router.py`
**Symbol**: circular import models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\router.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: circular import qdrant_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: circular import qdrant_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: circular import qdrant_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: circular duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: circular import qdrant_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import qdrant_client
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: circular import meilisearch
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\services\meilisearch_service.py`
**Symbol**: circular import meilisearch
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\meilisearch_service.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import meilisearch
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: circular import arango
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: circular duplication

**File**: `shared\core\vector_database.py`
**Symbol**: circular import arango
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: circular duplication

**File**: `services\model_registry\main.py`
**Symbol**: circular import arango
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: circular duplication

**File**: `services\monitoring\health.py`
**Symbol**: circular import config.production.monitoring
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: circular duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: circular import config.production.monitoring
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: circular duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: circular import services.retrieval.main
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: circular duplication

**File**: `services\retrieval\tests\test_retrieval_endpoints.py`
**Symbol**: circular import services.retrieval.main
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\retrieval\tests\test_retrieval_endpoints.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: circular import shared.core.cache
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: circular duplication

**File**: `services\synthesis\main.py`
**Symbol**: circular import shared.core.cache
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: circular duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: circular import shared.core.cache
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: circular duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: circular import shared.core.cache
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: circular import starlette.types
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: circular import starlette.types
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: circular import html
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: circular duplication

**File**: `shared\core\input_validation.py`
**Symbol**: circular import html
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: circular import html
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: circular import observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: circular import observability
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: circular duplication

**File**: `shared\core\input_validation.py`
**Symbol**: circular import bleach
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: circular duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: circular import bleach
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: circular duplication

**File**: `services\gateway\routers\tests.py`
**Symbol**: circular import yaml
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/services\gateway\routers\tests.py`
**Reason**: circular duplication

**File**: `shared\core\sla_budget_enforcer.py`
**Symbol**: circular import yaml
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\sla_budget_enforcer.py`
**Reason**: circular duplication

**File**: `shared\core\logging_configuration_manager.py`
**Symbol**: circular import yaml
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\logging_configuration_manager.py`
**Reason**: circular duplication

**File**: `shared\core\database.py`
**Symbol**: circular import tenacity
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: circular duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: circular import tenacity
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: circular duplication

**File**: `shared\core\error_handler.py`
**Symbol**: circular import tenacity
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: circular duplication

**File**: `shared\core\services\analytics_dashboard_service.py`
**Symbol**: circular import statistics
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\analytics_dashboard_service.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import statistics
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: circular import statistics
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: circular duplication

**File**: `shared\core\repository.py`
**Symbol**: circular import interfaces
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: circular duplication

**File**: `shared\core\observer.py`
**Symbol**: circular import interfaces
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: circular duplication

**File**: `shared\core\decorator.py`
**Symbol**: circular import interfaces
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import interfaces
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import shared.core.agents.base_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import shared.core.agents.retrieval_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: circular import shared.core.agents.retrieval_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import shared.core.agents.factcheck_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import shared.core.agents.factcheck_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import shared.core.agents.synthesis_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\factory.py`
**Symbol**: circular import shared.core.agents.synthesis_agent
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: circular duplication

**File**: `shared\core\auth\password_hasher.py`
**Symbol**: circular import secrets
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\auth\password_hasher.py`
**Reason**: circular duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: circular import secrets
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: circular duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: circular import secrets
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: circular duplication

**File**: `shared\core\api\config.py`
**Symbol**: circular import secrets
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: circular duplication

**File**: `shared\core\input_validation.py`
**Symbol**: circular import secrets
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: circular duplication

**File**: `shared\core\api\config.py`
**Symbol**: circular import warnings
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: circular duplication

**File**: `shared\core\logging_config.py`
**Symbol**: circular import warnings
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: circular duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: circular import warnings
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: circular import shared.models.session_memory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: circular duplication

**File**: `shared\core\memory_manager_postgres.py`
**Symbol**: circular import shared.models.session_memory
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager_postgres.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import weakref
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: circular import weakref
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\observer.py`
**Symbol**: circular import weakref
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: circular duplication

**File**: `shared\core\performance.py`
**Symbol**: circular import gc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: circular duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: circular import gc
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: circular import bcrypt
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: circular duplication

**File**: `shared\core\auth\password_hasher.py`
**Symbol**: circular import bcrypt
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\auth\password_hasher.py`
**Reason**: circular duplication

**File**: `shared\models\session_memory.py`
**Symbol**: circular import shared.models.models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\models\session_memory.py`
**Reason**: circular duplication

**File**: `shared\models\cache_store.py`
**Symbol**: circular import shared.models.models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\models\cache_store.py`
**Reason**: circular duplication

**File**: `shared\core\database\repository.py`
**Symbol**: circular import shared.models.models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: circular duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: circular import qdrant_client.models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: circular import qdrant_client.models
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: circular duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: circular import chromadb
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: circular import chromadb
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: circular duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: circular import chromadb
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: circular import chromadb
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: circular duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: circular import chromadb.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: circular duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: circular import chromadb.config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import task_processor
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import task_processor
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import task_processor
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import task_processor
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import shared.core.utilities.response_utilities
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import shared.core.utilities.response_utilities
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import shared.core.utilities.response_utilities
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import shared.core.utilities.response_utilities
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import agent_decorators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import agent_decorators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import agent_decorators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import agent_decorators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: circular import common_validators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: circular import common_validators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import common_validators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import common_validators
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: circular import shared.core.prompt_templates
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: circular duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: circular import shared.core.prompt_templates
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import cache_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: circular import cache_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: circular import cache_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: circular import cache_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_invalidation.py`
**Symbol**: circular import cache_config
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_invalidation.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: circular import cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cache_invalidation.py`
**Symbol**: circular import cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_invalidation.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: circular import cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: circular duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: circular import cache_manager
**Duplicate Of**: `circular dependency`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: circular duplication

### Medium Priority

**File**: `services\test_all_services.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_all_services.py`
**Reason**: module duplication

**File**: `services\test_cicd.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_cicd.py`
**Reason**: module duplication

**File**: `services\test_feeds.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_feeds.py`
**Reason**: module duplication

**File**: `services\test_guided_prompt.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_guided_prompt.py`
**Reason**: module duplication

**File**: `services\test_model_services.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_model_services.py`
**Reason**: module duplication

**File**: `services\test_observability.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_observability.py`
**Reason**: module duplication

**File**: `services\test_retrieval.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_retrieval.py`
**Reason**: module duplication

**File**: `services\test_security.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\test_security.py`
**Reason**: module duplication

**File**: `services\analytics\feedback_storage.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\feedback_storage.py`
**Reason**: module duplication

**File**: `services\analytics\feedback_storage.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\feedback_storage.py`
**Reason**: module duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: module duplication

**File**: `services\analytics\metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: module duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: module duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: module duplication

**File**: `services\cicd\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: module duplication

**File**: `services\cicd\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: module duplication

**File**: `services\feeds\attribution_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\attribution_manager.py`
**Reason**: module duplication

**File**: `services\feeds\constraint_mapper.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\constraint_mapper.py`
**Reason**: module duplication

**File**: `services\feeds\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: module duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: module duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: module duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: module duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: module duplication

**File**: `services\gateway\advanced_features.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\advanced_features.py`
**Reason**: module duplication

**File**: `services\gateway\agent_orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\agent_orchestrator.py`
**Reason**: module duplication

**File**: `services\gateway\agent_orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\agent_orchestrator.py`
**Reason**: module duplication

**File**: `services\gateway\agent_orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\agent_orchestrator.py`
**Reason**: module duplication

**File**: `services\gateway\analytics_collector.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\analytics_collector.py`
**Reason**: module duplication

**File**: `services\gateway\background_processor.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\background_processor.py`
**Reason**: module duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: module duplication

**File**: `services\gateway\citations.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\citations.py`
**Reason**: module duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: module duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: module duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: module duplication

**File**: `services\gateway\metrics_router.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\metrics_router.py`
**Reason**: module duplication

**File**: `services\gateway\model_router.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\model_router.py`
**Reason**: module duplication

**File**: `services\gateway\prompt_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\prompt_optimizer.py`
**Reason**: module duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: module duplication

**File**: `services\gateway\routes.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: module duplication

**File**: `services\gateway\routes.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: module duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: module duplication

**File**: `services\gateway\security_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\security_middleware.py`
**Reason**: module duplication

**File**: `services\gateway\security_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\security_middleware.py`
**Reason**: module duplication

**File**: `services\gateway\streaming_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\streaming_manager.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: module duplication

**File**: `services\model_registry\feeds_adapters.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_adapters.py`
**Reason**: module duplication

**File**: `services\model_registry\feeds_adapters.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_adapters.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\monitoring\health.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: module duplication

**File**: `services\monitoring\health.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: module duplication

**File**: `services\monitoring\health.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\observability\dashboard_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\dashboard_config.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: module duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `services\retrieval\fusion.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\fusion.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: module duplication

**File**: `services\retrieval\youtube_retrieval.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\youtube_retrieval.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\keyword_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\keyword_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\kg_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\kg_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\markets_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\markets_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\news_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\news_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\preflight_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\preflight_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\vector_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\vector_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\web_lane.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\web_lane.py`
**Reason**: module duplication

**File**: `services\gateway\health\comprehensive_monitor.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\health\comprehensive_monitor.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\observability.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\observability.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\observability.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\observability.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\providers\anthropic_client.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\anthropic_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `services\gateway\providers\huggingface_client.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\huggingface_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\openai_client.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\openai_client.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\circuit_breaker.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\circuit_breaker.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\circuit_breaker.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\circuit_breaker.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\graceful_degradation.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\graceful_degradation.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\graceful_degradation.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\graceful_degradation.py`
**Reason**: module duplication

**File**: `services\feeds\providers\gdelt_provider.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\gdelt_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\guardian_provider.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\guardian_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\hn_algolia_provider.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\hn_algolia_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\markets_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\markets_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\markets_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\markets_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\markets_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\markets_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\sec_edgar_provider.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\sec_edgar_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\stooq_provider.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\stooq_provider.py`
**Reason**: module duplication

**File**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\metrics\knowledge_platform_metrics.py`
**Reason**: module duplication

**File**: `shared\ci\ci_gates.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\ci\ci_gates.py`
**Reason**: module duplication

**File**: `shared\ci\provider_key_validator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\ci\provider_key_validator.py`
**Reason**: module duplication

**File**: `shared\clients\service_client.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\clients\service_client.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\cache_manager_postgres.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache_manager_postgres.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\evidence_quality_validator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\evidence_quality_validator.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\graceful_degradation.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\graceful_degradation.py`
**Reason**: module duplication

**File**: `shared\core\health_checker.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\logging_configuration_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_configuration_manager.py`
**Reason**: module duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: module duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: module duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: module duplication

**File**: `shared\core\memory_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager.py`
**Reason**: module duplication

**File**: `shared\core\memory_manager_postgres.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\memory_manager_postgres.py`
**Reason**: module duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: module duplication

**File**: `shared\core\migrations.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\migrations.py`
**Reason**: module duplication

**File**: `shared\core\migrations.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\migrations.py`
**Reason**: module duplication

**File**: `shared\core\migrations.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\migrations.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\shutdown_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\shutdown_handler.py`
**Reason**: module duplication

**File**: `shared\core\shutdown_handler.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\shutdown_handler.py`
**Reason**: module duplication

**File**: `shared\core\sla_budget_enforcer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\sla_budget_enforcer.py`
**Reason**: module duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: module duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: module duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: module duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: module duplication

**File**: `shared\core\system_health.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\workflow_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\workflow_manager.py`
**Reason**: module duplication

**File**: `shared\core\workflow_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\workflow_manager.py`
**Reason**: module duplication

**File**: `shared\core\workflow_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\workflow_manager.py`
**Reason**: module duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\models\frontend_state.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\models\frontend_state.py`
**Reason**: module duplication

**File**: `shared\observability\fallback_metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\observability\fallback_metrics.py`
**Reason**: module duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: module duplication

**File**: `shared\vectorstores\fallback_vector_db.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\fallback_vector_db.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\repositories\database\user_repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\repositories\database\user_repository.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: module duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\task_processor.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\task_processor.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\auth\password_hasher.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\auth\password_hasher.py`
**Reason**: module duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: module duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: module duplication

**File**: `shared\core\cache\cached_agents.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_agents.py`
**Reason**: module duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_invalidation.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_invalidation.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `shared\core\database\connection.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: module duplication

**File**: `shared\core\database\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: module duplication

**File**: `shared\core\database\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: module duplication

**File**: `shared\core\database\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: module duplication

**File**: `shared\core\database\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: module duplication

**File**: `shared\core\database\repository.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\database\repository.py`
**Reason**: module duplication

**File**: `shared\core\logging\structured_logger.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\logging\structured_logger.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: module duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: module duplication

**File**: `shared\core\services\advanced_citations_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\advanced_citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\analytics_dashboard_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\analytics_dashboard_service.py`
**Reason**: module duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: module duplication

**File**: `shared\core\services\audit_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\audit_service.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\cost_aware_llm_router.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\cost_aware_llm_router.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: module duplication

**File**: `shared\core\services\llm_cost_optimizer.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\llm_cost_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\meilisearch_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\meilisearch_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multilanguage_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multilanguage_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function __init__
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `services\analytics\metrics.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: module duplication

**File**: `services\gateway\metrics_router.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\metrics_router.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\observability.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\observability.py`
**Reason**: module duplication

**File**: `shared\core\interfaces.py`
**Symbol**: class MetricsCollector
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: module duplication

**File**: `services\gateway\model_router.py`
**Symbol**: function categorize_query
**Duplicate Of**: `services\analytics\analytics.py`
**Proposed Move**: `deprecated/backend/services\gateway\model_router.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: class FeedbackRequest
**Duplicate Of**: `services\analytics\feedback_storage.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: class IntegrationStatus
**Duplicate Of**: `services\analytics\integration_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function get_metrics_collector
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\observability.py`
**Symbol**: function get_metrics_collector
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\observability.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function get_metrics_collector
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function record_cache_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function record_cache_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Symbol**: function record_business_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\analytics\metrics\knowledge_platform_metrics.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function record_request
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function record_request
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function record_request
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function record_request
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function record_request
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function record_cache_hit
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function record_cache_hit
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function record_cache_hit
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function record_cache_miss
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function record_cache_miss
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function record_cache_miss
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function record_error
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function record_error
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function record_error
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function record_error
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `services\analytics\monitoring.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\analytics\monitoring.py`
**Reason**: module duplication

**File**: `services\retrieval\youtube_retrieval.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/services\retrieval\youtube_retrieval.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\workflow_manager.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\workflow_manager.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function get_metrics
**Duplicate Of**: `services\analytics\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: class MetricType
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: class MetricType
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: class MetricsExporter
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: module duplication

**File**: `services\gateway\routes.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: module duplication

**File**: `services\gateway\routes.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `shared\core\app_factory.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\database.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\agents\agent_decorators.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\agent_decorators.py`
**Reason**: module duplication

**File**: `shared\core\logging\structured_logger.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\logging\structured_logger.py`
**Reason**: module duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function decorator
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `services\feeds\config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\feeds\config.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\retrieval\config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\input_validation.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\input_validation.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_config.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_config.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_config.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\utilities\validation_utilities.py`
**Symbol**: function __post_init__
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\validation_utilities.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function record_success
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\circuit_breaker.py`
**Symbol**: function record_success
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\circuit_breaker.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function record_success
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function record_success
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function record_failure
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `services\gateway\resilience\circuit_breaker.py`
**Symbol**: function record_failure
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\gateway\resilience\circuit_breaker.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: function record_failure
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function record_failure
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\agents\agent_decorators.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\agent_decorators.py`
**Reason**: module duplication

**File**: `shared\core\logging\structured_logger.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\logging\structured_logger.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function sync_wrapper
**Duplicate Of**: `services\analytics\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: class ModelStatus
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: class ModelCandidate
**Duplicate Of**: `services\auto_upgrade\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: module duplication

**File**: `shared\core\logging_configuration_manager.py`
**Symbol**: class Environment
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_configuration_manager.py`
**Reason**: module duplication

**File**: `shared\core\api\config.py`
**Symbol**: class Environment
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: class Environment
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: class Environment
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `services\gateway\routers\tests.py`
**Symbol**: class PerformanceMetrics
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\routers\tests.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: class PerformanceMetrics
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: class PerformanceMetrics
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: class PerformanceMetrics
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: class PerformanceMetrics
**Duplicate Of**: `services\cicd\main.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `services\gateway\security_middleware.py`
**Symbol**: class SecurityMiddleware
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: class SecurityMiddleware
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: class SecurityMiddleware
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function _add_security_headers
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function _add_security_headers
**Duplicate Of**: `services\crud\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\main.py`
**Symbol**: class FactCheckRequest
**Duplicate Of**: `services\fact_check\routes.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: module duplication

**File**: `services\gateway\routes.py`
**Symbol**: class FactCheckRequest
**Duplicate Of**: `services\fact_check\routes.py`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function get_config
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_config
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_config
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\retrieval\config.py`
**Symbol**: function get_config
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_provider_api_key
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_provider_api_key
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_provider_api_key
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_provider_api_key
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function _load_provider_configurations
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function _load_provider_configurations
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function _load_provider_configurations
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function _load_provider_configurations
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function _log_configuration_status
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function _log_configuration_status
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function _log_configuration_status
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\retrieval\config.py`
**Symbol**: function _log_configuration_status
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function get_service_health
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_service_health
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_service_health
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\retrieval\config.py`
**Symbol**: function get_service_health
**Duplicate Of**: `services\feeds\config.py`
**Proposed Move**: `deprecated/backend/services\retrieval\config.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: class ProviderStatus
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: class ProviderStatus
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: class ProviderStatus
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: class ProviderStatus
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\feeds\providers\markets_providers.py`
**Symbol**: class NormalizedFeedItem
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\markets_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: class NormalizedFeedItem
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\markets_providers.py`
**Symbol**: class FeedResult
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\markets_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: class FeedResult
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: function _record_metrics
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: function _record_metrics
**Duplicate Of**: `services\feeds\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: class CacheStrategy
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: class CacheStrategy
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: class PerformanceOptimizer
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\models\cache_store.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\models\cache_store.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function is_expired
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function optimize_query
**Duplicate Of**: `services\gateway\advanced_features.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class AgentType
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: class AgentType
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: class QueryContext
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class QueryContext
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: class QueryContext
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class AgentResult
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: class AgentResult
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function _normalize_query
**Duplicate Of**: `services\gateway\agent_orchestrator.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: function get_performance_metrics
**Duplicate Of**: `services\gateway\analytics_collector.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function get_performance_metrics
**Duplicate Of**: `services\gateway\analytics_collector.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class TaskPriority
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: class TaskPriority
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `services\gateway\huggingface_integration.py`
**Symbol**: class TaskType
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/services\gateway\huggingface_integration.py`
**Reason**: module duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: module duplication

**File**: `services\gateway\prompt_optimizer.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/services\gateway\prompt_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\logging_configuration_manager.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_configuration_manager.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\models\cache_store.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\models\cache_store.py`
**Reason**: module duplication

**File**: `shared\models\frontend_state.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\models\frontend_state.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\session_memory.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\models\session_memory.py`
**Reason**: module duplication

**File**: `shared\core\agents\base_agent.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: module duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: module duplication

**File**: `shared\core\agents\knowledge_graph_service.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\knowledge_graph_service.py`
**Reason**: module duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\api\config.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function to_dict
**Duplicate Of**: `services\gateway\background_processor.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_config.py`
**Symbol**: class CacheLevel
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_config.py`
**Reason**: module duplication

**File**: `services\gateway\main.py`
**Symbol**: class CacheEntry
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: class CacheEntry
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: class CacheEntry
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: class CacheEntry
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: class CacheEntry
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `services\gateway\prompt_optimizer.py`
**Symbol**: function _generate_cache_key
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/services\gateway\prompt_optimizer.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function _generate_cache_key
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function _generate_cache_key
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function _generate_cache_key
**Duplicate Of**: `services\gateway\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\evidence_quality_validator.py`
**Symbol**: class Citation
**Duplicate Of**: `services\gateway\citations.py`
**Proposed Move**: `deprecated/backend/shared\core\evidence_quality_validator.py`
**Reason**: module duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: class Citation
**Duplicate Of**: `services\gateway\citations.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: class Citation
**Duplicate Of**: `services\gateway\citations.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\data_models.py`
**Symbol**: class FactCheckResult
**Duplicate Of**: `services\gateway\citations.py`
**Proposed Move**: `deprecated/backend/shared\core\data_models.py`
**Reason**: module duplication

**File**: `shared\core\services\advanced_citations_service.py`
**Symbol**: function generate_bibliography
**Duplicate Of**: `services\gateway\citations.py`
**Proposed Move**: `deprecated/backend/shared\core\services\advanced_citations_service.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: class ModelConfig
**Duplicate Of**: `services\gateway\huggingface_integration.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `services\model_registry\search_router.py`
**Symbol**: class SearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\search_router.py`
**Reason**: module duplication

**File**: `services\retrieval\routers\free_tier_router.py`
**Symbol**: class SearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\routers\free_tier_router.py`
**Reason**: module duplication

**File**: `services\gateway\routers\retrieval_router.py`
**Symbol**: class SearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\routers\retrieval_router.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class SearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\contracts\query.py`
**Symbol**: class SynthesisRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\contracts\query.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class AuthRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\contracts\query.py`
**Symbol**: class VectorSearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\contracts\query.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class VectorSearchRequest
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: class UserProfile
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: class ModelConfiguration
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: class Dataset
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: class SystemSetting
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `services\retrieval\routers\free_tier_router.py`
**Symbol**: class HealthResponse
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\routers\free_tier_router.py`
**Reason**: module duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: class HealthResponse
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: class HealthResponse
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `shared\core\api\api_responses.py`
**Symbol**: class HealthResponse
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_responses.py`
**Reason**: module duplication

**File**: `services\retrieval\routers\free_tier_router.py`
**Symbol**: function validate_query
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\routers\free_tier_router.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: function validate_query
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_username
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function validate_username
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function validate_url
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_key
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_service
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security.py`
**Symbol**: function validate_email
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_email
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function validate_email
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_model_name
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_dataset_id
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `shared\models\crud_models.py`
**Symbol**: function validate_setting_key
**Duplicate Of**: `services\gateway\main.py`
**Proposed Move**: `deprecated/backend/shared\models\crud_models.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: class QueryComplexity
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: class QueryComplexity
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: class QueryComplexity
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: class QueryComplexity
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class QueryComplexity
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: class QueryCategory
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class QueryCategory
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: class ModelSelection
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: class ModelRouter
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: function _load_configuration
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: module duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: function select_model
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: module duplication

**File**: `services\gateway\scoring_router.py`
**Symbol**: function _get_emergency_fallback
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\gateway\scoring_router.py`
**Reason**: module duplication

**File**: `services\guided_prompt\config.py`
**Symbol**: function get_available_models
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\guided_prompt\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_available_models
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\model_registry\config.py`
**Symbol**: function get_available_models
**Duplicate Of**: `services\gateway\model_router.py`
**Proposed Move**: `deprecated/backend/services\model_registry\config.py`
**Reason**: module duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: class LLMRequest
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: module duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: class LLMResponse
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: module duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: class LLMResponse
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: class ProviderConfig
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: class ProviderConfig
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function _is_provider_available
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function _is_provider_available
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: function _is_provider_available
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function _create_error_response
**Duplicate Of**: `services\gateway\real_llm_integration.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: function _sanitize_response
**Duplicate Of**: `services\gateway\providers\ollama_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: module duplication

**File**: `shared\contracts\service_contracts.py`
**Symbol**: class ServiceResponse
**Duplicate Of**: `services\gateway\routes.py`
**Proposed Move**: `deprecated/backend/shared\contracts\service_contracts.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: class BaseModel
**Duplicate Of**: `services\gateway\routes.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function get
**Duplicate Of**: `services\gateway\routes.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: class RoutingRequest
**Duplicate Of**: `services\gateway\scoring_router.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: function _check_provider_availability
**Duplicate Of**: `services\gateway\scoring_router.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function _calculate_model_score
**Duplicate Of**: `services\gateway\scoring_router.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function _calculate_model_score
**Duplicate Of**: `services\gateway\scoring_router.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function _get_client_ip
**Duplicate Of**: `services\gateway\security_middleware.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function _get_client_ip
**Duplicate Of**: `services\gateway\security_middleware.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function _check_rate_limit
**Duplicate Of**: `services\gateway\security_middleware.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function get_provider_summary
**Duplicate Of**: `services\guided_prompt\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function get_provider_summary
**Duplicate Of**: `services\guided_prompt\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_refinement_model_selection
**Duplicate Of**: `services\guided_prompt\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\model_router\config.py`
**Symbol**: function get_refinement_model_selection
**Duplicate Of**: `services\guided_prompt\config.py`
**Proposed Move**: `deprecated/backend/services\model_router\config.py`
**Reason**: module duplication

**File**: `services\model_registry\refine_router.py`
**Symbol**: class ConstraintChip
**Duplicate Of**: `services\guided_prompt\main.py`
**Proposed Move**: `deprecated/backend/services\model_registry\refine_router.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: class ConstraintChip
**Duplicate Of**: `services\guided_prompt\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\model_router\main.py`
**Symbol**: class QueryRequest
**Duplicate Of**: `services\guided_prompt\main.py`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: module duplication

**File**: `shared\contracts\query.py`
**Symbol**: class QueryRequest
**Duplicate Of**: `services\guided_prompt\main.py`
**Proposed Move**: `deprecated/backend/shared\contracts\query.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: class QueryRequest
**Duplicate Of**: `services\guided_prompt\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function get_active_providers
**Duplicate Of**: `services\model_registry\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function get_active_providers
**Duplicate Of**: `services\model_registry\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: function get_models_by_provider
**Duplicate Of**: `services\model_registry\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: function get_stable_models
**Duplicate Of**: `services\model_registry\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\model_registry\main.py`
**Symbol**: function get_refiner_models
**Duplicate Of**: `services\model_registry\config.py`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: module duplication

**File**: `services\model_registry\feeds_adapters.py`
**Symbol**: function _initialize_providers
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_adapters.py`
**Reason**: module duplication

**File**: `services\model_registry\feeds_adapters.py`
**Symbol**: function _initialize_providers
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\model_registry\feeds_adapters.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function _initialize_providers
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: function get_model
**Duplicate Of**: `services\model_registry\main.py`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: module duplication

**File**: `services\model_registry\routing_router.py`
**Symbol**: class RefineRequest
**Duplicate Of**: `services\model_registry\refine_router.py`
**Proposed Move**: `deprecated/backend/services\model_registry\routing_router.py`
**Reason**: module duplication

**File**: `services\model_registry\routing_router.py`
**Symbol**: class RefineResponse
**Duplicate Of**: `services\model_registry\refine_router.py`
**Proposed Move**: `deprecated/backend/services\model_registry\routing_router.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: class LaneResult
**Duplicate Of**: `services\model_registry\search_router.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: class LaneResult
**Duplicate Of**: `services\model_registry\search_router.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `services\model_registry\search_router.py`
**Symbol**: class SearchResponse
**Duplicate Of**: `services\gateway\routers\retrieval_router.py`
**Proposed Move**: `deprecated/backend/services\model_registry\search_router.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: class SearchResponse
**Duplicate Of**: `services\gateway\routers\retrieval_router.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class SearchResponse
**Duplicate Of**: `services\gateway\routers\retrieval_router.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: class QueryClassifier
**Duplicate Of**: `services\model_router\main.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\core\query_classifier.py`
**Symbol**: function classify_query
**Duplicate Of**: `services\model_router\main.py`
**Proposed Move**: `deprecated/backend/shared\core\query_classifier.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function classify_query
**Duplicate Of**: `services\model_router\main.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\health_checker.py`
**Symbol**: class HealthChecker
**Duplicate Of**: `services\monitoring\health.py`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: module duplication

**File**: `services\monitoring\health.py`
**Symbol**: function get_health_summary
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: module duplication

**File**: `services\monitoring\health.py`
**Symbol**: function get_health_summary
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: function get_health_summary
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `shared\core\system_health.py`
**Symbol**: function get_health_summary
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: class PerformanceMonitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: class PerformanceMonitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: class PerformanceMonitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function get_performance_monitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function get_performance_monitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function get_performance_monitor
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function record_database_query
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function increment_counter
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function set_gauge
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function record_histogram
**Duplicate Of**: `services\monitoring\metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `services\monitoring\metrics.py`
**Symbol**: function get_metrics_summary
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/services\monitoring\metrics.py`
**Reason**: module duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: function get_metrics_summary
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function generate_system_health_dashboard
**Duplicate Of**: `services\observability\dashboard_config.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function generate_performance_dashboard
**Duplicate Of**: `services\observability\dashboard_config.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: function generate_guided_prompt_dashboard
**Duplicate Of**: `services\observability\dashboard_config.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class QueryMode
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class QueryMode
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class LaneName
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\main.py`
**Symbol**: class TraceContext
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: module duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: class TraceContext
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class SLAMetrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class LaneMetrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: class GuidedPromptMetrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function record_sla_metrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function record_lane_metrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function record_guided_prompt_metrics
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\metrics_utils.py`
**Symbol**: function record_provider_health
**Duplicate Of**: `services\observability\main.py`
**Proposed Move**: `deprecated/backend/services\observability\metrics_utils.py`
**Reason**: module duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: function __enter__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: module duplication

**File**: `shared\core\app_factory.py`
**Symbol**: function __enter__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __enter__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `services\observability\tracing_middleware.py`
**Symbol**: function __exit__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/services\observability\tracing_middleware.py`
**Reason**: module duplication

**File**: `shared\core\app_factory.py`
**Symbol**: function __exit__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function __exit__
**Duplicate Of**: `services\observability\metrics_utils.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\config\provider_config.py`
**Symbol**: function get_lane_config
**Duplicate Of**: `services\retrieval\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\provider_config.py`
**Reason**: module duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: class ProviderHealth
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: module duplication

**File**: `shared\core\agents\retrieval_agent.py`
**Symbol**: class SearchResult
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class SearchResult
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `services\retrieval\youtube_retrieval.py`
**Symbol**: function _calculate_relevance_score
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/services\retrieval\youtube_retrieval.py`
**Reason**: module duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: function _check_provider_health
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: module duplication

**File**: `services\retrieval\fusion.py`
**Symbol**: function _deduplicate_results
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/services\retrieval\fusion.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function _deduplicate_results
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\agent_pattern.py`
**Symbol**: function _deduplicate_results
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\agent_pattern.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function _deduplicate_results
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: function _title_similarity
**Duplicate Of**: `services\retrieval\free_tier.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: class FusedResult
**Duplicate Of**: `services\retrieval\fusion.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: class LaneStatus
**Duplicate Of**: `services\retrieval\main.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: class LaneStatus
**Duplicate Of**: `services\retrieval\main.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: class LaneStatus
**Duplicate Of**: `services\retrieval\main.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `services\retrieval\main.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\kg_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\kg_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\markets_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\markets_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\news_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\news_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\preflight_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\preflight_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\vector_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\vector_lane.py`
**Reason**: module duplication

**File**: `services\retrieval\lanes\web_lane.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/services\retrieval\lanes\web_lane.py`
**Reason**: module duplication

**File**: `shared\core\data_models.py`
**Symbol**: class RetrievalResult
**Duplicate Of**: `services\retrieval\lanes\keyword_lane.py`
**Proposed Move**: `deprecated/backend/shared\core\data_models.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: class OrchestrationConfig
**Duplicate Of**: `services\retrieval\orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function get_provider_order
**Duplicate Of**: `services\retrieval\orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function get_provider_order
**Duplicate Of**: `services\retrieval\orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: function _calculate_performance_metrics
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: function get_warmup_status
**Duplicate Of**: `services\retrieval\warmup.py`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: module duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: function get_warmup_status
**Duplicate Of**: `services\retrieval\warmup.py`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: class RateLimiter
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: class RateLimiter
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: class RateLimiter
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: module duplication

**File**: `shared\core\services\retrieval_aggregator.py`
**Symbol**: class RateLimiter
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/shared\core\services\retrieval_aggregator.py`
**Reason**: module duplication

**File**: `services\security\security_middleware.py`
**Symbol**: function _redact_pii
**Duplicate Of**: `services\security\main.py`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: module duplication

**File**: `services\security\main.py`
**Symbol**: function _generate_recommendations
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: module duplication

**File**: `shared\core\agents\common_processors.py`
**Symbol**: function calculate_confidence
**Duplicate Of**: `services\synthesis\main.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\common_processors.py`
**Reason**: module duplication

**File**: `shared\core\system_health.py`
**Symbol**: class HealthStatus
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: module duplication

**File**: `shared\core\api\api_models.py`
**Symbol**: class HealthStatus
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_models.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class HealthStatus
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `services\gateway\routers\health_router.py`
**Symbol**: class ServiceHealth
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/services\gateway\routers\health_router.py`
**Reason**: module duplication

**File**: `shared\contracts\service_contracts.py`
**Symbol**: class ServiceHealth
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\contracts\service_contracts.py`
**Reason**: module duplication

**File**: `shared\core\system_health.py`
**Symbol**: class SystemHealth
**Duplicate Of**: `services\gateway\health\comprehensive_monitor.py`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function log_error
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\services\audit_service.py`
**Symbol**: function log_error
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\services\audit_service.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function monitor_performance
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function monitor_performance
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function monitor_performance
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\logging\structured_logger.py`
**Symbol**: function get_request_id
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\logging\structured_logger.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function log_security_event
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\services\audit_service.py`
**Symbol**: function log_security_event
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\services\audit_service.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function record_api_cost
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function record_api_cost
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: function calculate_percentiles
**Duplicate Of**: `services\gateway\middleware\observability.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function _get_client_key
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function is_rate_limited
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function _is_trusted_host
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: function _validate_request_size
**Duplicate Of**: `services\gateway\middleware\security.py`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: module duplication

**File**: `services\gateway\providers\huggingface_client.py`
**Symbol**: function setup_client
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\huggingface_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: function setup_client
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\openai_client.py`
**Symbol**: function setup_client
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\openai_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\huggingface_client.py`
**Symbol**: function is_available
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\huggingface_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: function is_available
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: module duplication

**File**: `services\gateway\providers\openai_client.py`
**Symbol**: function is_available
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\openai_client.py`
**Reason**: module duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: function is_available
**Duplicate Of**: `services\gateway\providers\anthropic_client.py`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: class LLMProvider
**Duplicate Of**: `services\gateway\providers\base.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function get_available_providers
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: function get_available_providers
**Duplicate Of**: `services\gateway\providers\gpu_providers.py`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: module duplication

**File**: `services\gateway\providers\ollama_client.py`
**Symbol**: function _select_model
**Duplicate Of**: `services\gateway\providers\huggingface_client.py`
**Proposed Move**: `deprecated/backend/services\gateway\providers\ollama_client.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function register
**Duplicate Of**: `services\gateway\providers\registry.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: class CircuitState
**Duplicate Of**: `services\gateway\resilience\circuit_breaker.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: class CircuitBreaker
**Duplicate Of**: `services\gateway\resilience\circuit_breaker.py`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: class CircuitBreaker
**Duplicate Of**: `services\gateway\resilience\circuit_breaker.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\retry_logic.py`
**Symbol**: class CircuitBreaker
**Duplicate Of**: `services\gateway\resilience\circuit_breaker.py`
**Proposed Move**: `deprecated/backend/shared\core\retry_logic.py`
**Reason**: module duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: function get_status
**Duplicate Of**: `services\gateway\resilience\circuit_breaker.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: module duplication

**File**: `services\feeds\providers\guardian_provider.py`
**Symbol**: function _normalize_article
**Duplicate Of**: `services\feeds\providers\gdelt_provider.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\guardian_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\hn_algolia_provider.py`
**Symbol**: function _normalize_article
**Duplicate Of**: `services\feeds\providers\gdelt_provider.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\hn_algolia_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\news_providers.py`
**Symbol**: function _normalize_article
**Duplicate Of**: `services\feeds\providers\gdelt_provider.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\news_providers.py`
**Reason**: module duplication

**File**: `services\feeds\providers\sec_edgar_provider.py`
**Symbol**: function _extract_tickers
**Duplicate Of**: `services\feeds\providers\markets_providers.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\sec_edgar_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\stooq_provider.py`
**Symbol**: function _extract_tickers
**Duplicate Of**: `services\feeds\providers\markets_providers.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\stooq_provider.py`
**Reason**: module duplication

**File**: `services\feeds\providers\stooq_provider.py`
**Symbol**: function _normalize_market_data
**Duplicate Of**: `services\feeds\providers\sec_edgar_provider.py`
**Proposed Move**: `deprecated/backend/services\feeds\providers\stooq_provider.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function reset_metrics
**Duplicate Of**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function __new__
**Duplicate Of**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\services\arangodb_service.py`
**Symbol**: function __new__
**Duplicate Of**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\arangodb_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function __new__
**Duplicate Of**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function __new__
**Duplicate Of**: `services\analytics\metrics\knowledge_platform_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\agents\common_validators.py`
**Symbol**: class ValidationResult
**Duplicate Of**: `shared\ci\provider_key_validator.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\common_validators.py`
**Reason**: module duplication

**File**: `shared\core\utilities\validation_utilities.py`
**Symbol**: class ValidationResult
**Duplicate Of**: `shared\ci\provider_key_validator.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\validation_utilities.py`
**Reason**: module duplication

**File**: `shared\core\system_health.py`
**Symbol**: function _determine_overall_status
**Duplicate Of**: `shared\ci\provider_key_validator.py`
**Proposed Move**: `deprecated/backend/shared\core\system_health.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class VectorSearchResponse
**Duplicate Of**: `shared\contracts\query.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: class PromptTemplate
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: class AgentFactory
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function format
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function format
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function validate_variables
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function _load_default_templates
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function get_template
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function add_template
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\prompt_templates.py`
**Symbol**: function list_templates
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\prompt_templates.py`
**Reason**: module duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: function _calculate_synthesis_confidence
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\synthesis_agent.py`
**Symbol**: function _fallback_synthesis
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\synthesis_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: function _extract_claims_from_text
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: function _is_factual_statement
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: function _filter_verified_facts
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: module duplication

**File**: `shared\core\agents\factcheck_agent.py`
**Symbol**: function _calculate_verification_confidence
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\agents\factcheck_agent.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function create_agent
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function list_supported_types
**Duplicate Of**: `shared\core\agent_pattern.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\app_factory.py`
**Symbol**: function labels
**Duplicate Of**: `shared\core\api\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: module duplication

**File**: `shared\core\app_factory.py`
**Symbol**: function inc
**Duplicate Of**: `shared\core\api\monitoring.py`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class MessageType
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: class MessageType
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class AgentMessage
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: class BaseAgent
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function message_queue
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function _create_control_response
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function _create_result_message
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function _create_error_message
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function _create_heartbeat_response
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function get_health_status
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\base_agent.py`
**Symbol**: function record_metric
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\base_agent.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function record_metric
**Duplicate Of**: `shared\core\agents\base_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\cache.py`
**Symbol**: function get_settings
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\cache.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: class CacheStats
**Duplicate Of**: `shared\core\cache.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_config.py`
**Symbol**: class CacheBackend
**Duplicate Of**: `shared\core\cache.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_config.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_manager.py`
**Symbol**: function hit_rate
**Duplicate Of**: `shared\core\cache.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_manager.py`
**Reason**: module duplication

**File**: `shared\core\cache\cache_metrics.py`
**Symbol**: function hit_rate
**Duplicate Of**: `shared\core\cache.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cache_metrics.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_router_service.py`
**Symbol**: function success_rate
**Duplicate Of**: `shared\core\connection_pool.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_router_service.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function p95_response_time
**Duplicate Of**: `shared\core\connection_pool.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: function can_execute
**Duplicate Of**: `shared\core\connection_pool.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\interfaces.py`
**Symbol**: function can_execute
**Duplicate Of**: `shared\core\connection_pool.py`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: module duplication

**File**: `shared\core\database\connection.py`
**Symbol**: function get_pool_stats
**Duplicate Of**: `shared\core\connection_pool.py`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: module duplication

**File**: `shared\core\interfaces.py`
**Symbol**: class Repository
**Duplicate Of**: `shared\core\database.py`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function get_repository
**Duplicate Of**: `shared\core\database.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\core\data_models.py`
**Symbol**: class VerifiedFactModel
**Duplicate Of**: `shared\core\agents\factcheck_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\data_models.py`
**Reason**: module duplication

**File**: `shared\core\data_models.py`
**Symbol**: class SynthesisResult
**Duplicate Of**: `shared\core\agents\synthesis_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\data_models.py`
**Reason**: module duplication

**File**: `shared\core\middleware\rate_limiter.py`
**Symbol**: class RateLimitExceeded
**Duplicate Of**: `shared\core\decorator.py`
**Proposed Move**: `deprecated/backend/shared\core\middleware\rate_limiter.py`
**Reason**: module duplication

**File**: `shared\core\decorator.py`
**Symbol**: function get_cache_stats
**Duplicate Of**: `shared\core\cache\cached_agents.py`
**Proposed Move**: `deprecated/backend/shared\core\decorator.py`
**Reason**: module duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: function get_cache_stats
**Duplicate Of**: `shared\core\cache\cached_agents.py`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: module duplication

**File**: `shared\core\cache\cached_retrieval_agent.py`
**Symbol**: function get_cache_stats
**Duplicate Of**: `shared\core\cache\cached_agents.py`
**Proposed Move**: `deprecated/backend/shared\core\cache\cached_retrieval_agent.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function build
**Duplicate Of**: `shared\core\decorator.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\interfaces.py`
**Symbol**: function build
**Duplicate Of**: `shared\core\decorator.py`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class ErrorSeverity
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class ErrorCategory
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handler.py`
**Symbol**: class ErrorResponse
**Duplicate Of**: `shared\core\api\api_responses.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class ErrorResponse
**Duplicate Of**: `shared\core\api\api_responses.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class ErrorHandler
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: function _check_alerts
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function _check_alerts
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function _check_alerts
**Duplicate Of**: `shared\core\error_handler.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class AuthenticationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class AuthenticationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class ValidationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class ValidationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\error_handling.py`
**Symbol**: class DatabaseError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\error_handling.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class DatabaseError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function detect_disagreements
**Duplicate Of**: `shared\core\evidence_quality_validator.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function validate_config
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function validate_config
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function validate_config
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\factory.py`
**Symbol**: function get_instance
**Duplicate Of**: `shared\core\cache\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\factory.py`
**Reason**: module duplication

**File**: `shared\core\interfaces.py`
**Symbol**: function reset
**Duplicate Of**: `shared\core\factory.py`
**Proposed Move**: `deprecated/backend/shared\core\interfaces.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function can_handle
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function can_handle
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function can_handle
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function can_handle
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function can_handle
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function attach
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\observer.py`
**Symbol**: function detach
**Duplicate Of**: `shared\core\interfaces.py`
**Proposed Move**: `deprecated/backend/shared\core\observer.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function get_logger
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function get_logger
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function get_logger
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\logging_config.py`
**Symbol**: function _mask_sensitive_data
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_config.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function start_timer
**Duplicate Of**: `shared\core\logging_config.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `shared\core\utilities\timing_utilities.py`
**Symbol**: function start_timer
**Duplicate Of**: `shared\core\logging_config.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\timing_utilities.py`
**Reason**: module duplication

**File**: `shared\core\logging_configuration_manager.py`
**Symbol**: class LogLevel
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\logging_configuration_manager.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: class LogLevel
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function start_monitoring
**Duplicate Of**: `shared\core\logging_configuration_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\performance.py`
**Symbol**: function stop_monitoring
**Duplicate Of**: `shared\core\logging_configuration_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\performance.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: class LaneBudget
**Duplicate Of**: `shared\core\metrics_tracer.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function get_performance_summary
**Duplicate Of**: `shared\core\performance.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function get_performance_summary
**Duplicate Of**: `shared\core\performance.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: function get_performance_summary
**Duplicate Of**: `shared\core\performance.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\services\llm_cost_optimizer.py`
**Symbol**: function get_optimization_recommendations
**Duplicate Of**: `shared\core\performance.py`
**Proposed Move**: `deprecated/backend/shared\core\services\llm_cost_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\performance_optimizer.py`
**Symbol**: function optimize_memory
**Duplicate Of**: `shared\core\performance.py`
**Proposed Move**: `deprecated/backend/shared\core\performance_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: class PerformanceAlert
**Duplicate Of**: `shared\core\performance_optimizer.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\embeddings\model_cache.py`
**Symbol**: function clear_cache
**Duplicate Of**: `shared\core\performance_optimizer.py`
**Proposed Move**: `deprecated/backend/shared\embeddings\model_cache.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: class BaseRepository
**Duplicate Of**: `shared\core\database\repository.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: class Query
**Duplicate Of**: `shared\core\repository.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\core\repository.py`
**Symbol**: function _apply_filters
**Duplicate Of**: `shared\core\database\repository.py`
**Proposed Move**: `deprecated/backend/shared\core\repository.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: class UserSession
**Duplicate Of**: `shared\core\secure_auth.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function hash_password
**Duplicate Of**: `shared\core\auth\password_hasher.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: function verify_password
**Duplicate Of**: `shared\core\auth\password_hasher.py`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: module duplication

**File**: `shared\core\sla_budget_enforcer.py`
**Symbol**: function _load_config
**Duplicate Of**: `shared\core\services\index_fabric_service.py`
**Proposed Move**: `deprecated/backend/shared\core\sla_budget_enforcer.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function log_execution_time
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function debug
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function info
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function warning
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function error
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\unified_logging.py`
**Symbol**: function critical
**Duplicate Of**: `shared\core\logging\structured_logger.py`
**Proposed Move**: `deprecated/backend/shared\core\unified_logging.py`
**Reason**: module duplication

**File**: `shared\core\vector_database.py`
**Symbol**: class KnowledgeGraphResult
**Duplicate Of**: `shared\core\agents\knowledge_graph_service.py`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: module duplication

**File**: `shared\embeddings\local_embedder.py`
**Symbol**: function _get_cache_key
**Duplicate Of**: `shared\core\services\vector_singleton_service.py`
**Proposed Move**: `deprecated/backend/shared\embeddings\local_embedder.py`
**Reason**: module duplication

**File**: `shared\vectorstores\fallback_vector_db.py`
**Symbol**: function _estimate_memory_usage
**Duplicate Of**: `shared\embeddings\model_cache.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\fallback_vector_db.py`
**Reason**: module duplication

**File**: `shared\models\frontend_state.py`
**Symbol**: function __repr__
**Duplicate Of**: `shared\models\cache_store.py`
**Proposed Move**: `deprecated/backend/shared\models\frontend_state.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function __repr__
**Duplicate Of**: `shared\models\cache_store.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\models\session_memory.py`
**Symbol**: function __repr__
**Duplicate Of**: `shared\models\cache_store.py`
**Proposed Move**: `deprecated/backend/shared\models\session_memory.py`
**Reason**: module duplication

**File**: `shared\models\models.py`
**Symbol**: function add_result
**Duplicate Of**: `shared\core\services\retrieval_aggregator.py`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: class VectorDocument
**Duplicate Of**: `shared\vectorstores\fallback_vector_db.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: function _cosine_similarity
**Duplicate Of**: `shared\vectorstores\fallback_vector_db.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: module duplication

**File**: `shared\vectorstores\fallback_vector_db.py`
**Symbol**: function get_stats
**Duplicate Of**: `shared\core\cache\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\vectorstores\fallback_vector_db.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function get_stats
**Duplicate Of**: `shared\core\cache\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\enhanced_vector_optimizer.py`
**Symbol**: function get_stats
**Duplicate Of**: `shared\core\cache\cache_manager.py`
**Proposed Move**: `deprecated/backend/shared\core\services\enhanced_vector_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: class Claim
**Duplicate Of**: `shared\core\agents\factcheck_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\api\config.py`
**Symbol**: function model_dump
**Duplicate Of**: `shared\core\agents\synthesis_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function model_dump
**Duplicate Of**: `shared\core\agents\synthesis_agent.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\api\api_responses.py`
**Symbol**: class QueryResponse
**Duplicate Of**: `shared\core\api\api_models.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_responses.py`
**Reason**: module duplication

**File**: `shared\core\api\api_responses.py`
**Symbol**: class MetricsResponse
**Duplicate Of**: `shared\core\api\api_models.py`
**Proposed Move**: `deprecated/backend/shared\core\api\api_responses.py`
**Reason**: module duplication

**File**: `shared\core\api\unified_models.py`
**Symbol**: class AuthResponse
**Duplicate Of**: `shared\core\api\api_models.py`
**Proposed Move**: `deprecated/backend/shared\core\api\unified_models.py`
**Reason**: module duplication

**File**: `shared\core\utilities\response_utilities.py`
**Symbol**: function create_error_response
**Duplicate Of**: `shared\core\api\api_responses.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\response_utilities.py`
**Reason**: module duplication

**File**: `shared\core\utilities\response_utilities.py`
**Symbol**: function create_error_response
**Duplicate Of**: `shared\core\api\api_responses.py`
**Proposed Move**: `deprecated/backend/shared\core\utilities\response_utilities.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: class SecureSettings
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function from_string
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function from_string
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function dict
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function _mask_secrets
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function parse_cors_origins
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function fix_redis_url_scheme
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function validate_vector_provider
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function validate_log_level
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function validate_environment
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function parse_features
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\config\central_config.py`
**Symbol**: function get_feature
**Duplicate Of**: `shared\core\api\config.py`
**Proposed Move**: `deprecated/backend/shared\core\config\central_config.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class UKPException
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class UKPHTTPException
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class AuthorizationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class InvalidAPIKeyError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class RateLimitExceededError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class AgentError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class AgentTimeoutError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class AgentProcessingError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class QueryProcessingError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class ResourceNotFoundError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class CacheError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class ExternalServiceError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class SecurityViolationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class ConfigurationError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: class ExpertReviewError
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function handle_agent_error
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function handle_external_service_error
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\api\exceptions_backup.py`
**Symbol**: function sanitize_error_message
**Duplicate Of**: `shared\core\api\exceptions.py`
**Proposed Move**: `deprecated/backend/shared\core\api\exceptions_backup.py`
**Reason**: module duplication

**File**: `shared\core\services\performance_monitor.py`
**Symbol**: class MetricPoint
**Duplicate Of**: `shared\core\cache\cache_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\services\performance_monitor.py`
**Reason**: module duplication

**File**: `shared\core\metrics\metrics_service.py`
**Symbol**: function record_cache_operation
**Duplicate Of**: `shared\core\cache\cache_metrics.py`
**Proposed Move**: `deprecated/backend/shared\core\metrics\metrics_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: class LaneConfig
**Duplicate Of**: `shared\core\config\provider_config.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\llm_cost_optimizer.py`
**Symbol**: function is_provider_available
**Duplicate Of**: `shared\core\config\provider_config.py`
**Proposed Move**: `deprecated/backend/shared\core\services\llm_cost_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: class Bibliography
**Duplicate Of**: `shared\core\services\advanced_citations_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\citations_service.py`
**Symbol**: function export_citations
**Duplicate Of**: `shared\core\services\advanced_citations_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\citations_service.py`
**Reason**: module duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: function from_environment
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\meilisearch_service.py`
**Symbol**: function from_environment
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\meilisearch_service.py`
**Reason**: module duplication

**File**: `shared\core\services\multi_lane_orchestrator.py`
**Symbol**: function from_environment
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\multi_lane_orchestrator.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function from_environment
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\meilisearch_service.py`
**Symbol**: function get_redacted_config
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\meilisearch_service.py`
**Reason**: module duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: function get_redacted_config
**Duplicate Of**: `shared\core\services\arangodb_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: module duplication

**File**: `shared\core\services\llm_cost_optimizer.py`
**Symbol**: function _check_budget_limits
**Duplicate Of**: `shared\core\services\enhanced_router_service.py`
**Proposed Move**: `deprecated/backend/shared\core\services\llm_cost_optimizer.py`
**Reason**: module duplication

**File**: `shared\core\services\startup_warmup_service.py`
**Symbol**: function duration_ms
**Duplicate Of**: `shared\core\services\multi_lane_orchestrator.py`
**Proposed Move**: `deprecated/backend/shared\core\services\startup_warmup_service.py`
**Reason**: module duplication

### Low Priority

**File**: `services\retrieval\free_tier.py`
**Symbol**: import asyncio
**Duplicate Of**: `services\retrieval\free_tier.py:16`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import asyncio
**Duplicate Of**: `services\retrieval\free_tier.py:16`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import json
**Duplicate Of**: `services\gateway\main.py:39`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import json
**Duplicate Of**: `services\retrieval\free_tier.py:18`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `shared\core\api\config.py`
**Symbol**: import json
**Duplicate Of**: `shared\core\api\config.py:30`
**Proposed Move**: `deprecated/backend/shared\core\api\config.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\main.py:37`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import time
**Duplicate Of**: `services\gateway\routes.py:12`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import time
**Duplicate Of**: `services\retrieval\free_tier.py:22`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import time
**Duplicate Of**: `services\retrieval\orchestrator.py:20`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `shared\core\services\multilanguage_service.py`
**Symbol**: import time
**Duplicate Of**: `shared\core\services\multilanguage_service.py:23`
**Proposed Move**: `deprecated/backend/shared\core\services\multilanguage_service.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import typing
**Duplicate Of**: `services\gateway\main.py:35`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import typing
**Duplicate Of**: `services\retrieval\free_tier.py:25`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import logging
**Duplicate Of**: `services\retrieval\free_tier.py:19`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import re
**Duplicate Of**: `services\gateway\main.py:38`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: import re
**Duplicate Of**: `services\gateway\real_llm_integration.py:29`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import re
**Duplicate Of**: `services\retrieval\free_tier.py:21`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\security\security_middleware.py`
**Symbol**: import re
**Duplicate Of**: `services\security\security_middleware.py:186`
**Proposed Move**: `deprecated/backend/services\security\security_middleware.py`
**Reason**: import duplication

**File**: `services\synthesis\main.py`
**Symbol**: import re
**Duplicate Of**: `services\synthesis\main.py:3`
**Proposed Move**: `deprecated/backend/services\synthesis\main.py`
**Reason**: import duplication

**File**: `shared\core\error_handler.py`
**Symbol**: import re
**Duplicate Of**: `shared\core\error_handler.py:330`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: import duplication

**File**: `shared\core\error_handler.py`
**Symbol**: import re
**Duplicate Of**: `shared\core\error_handler.py:330`
**Proposed Move**: `deprecated/backend/shared\core\error_handler.py`
**Reason**: import duplication

**File**: `shared\models\models.py`
**Symbol**: import re
**Duplicate Of**: `shared\models\models.py:513`
**Proposed Move**: `deprecated/backend/shared\models\models.py`
**Reason**: import duplication

**File**: `shared\core\agents\citation_agent.py`
**Symbol**: import re
**Duplicate Of**: `shared\core\agents\citation_agent.py:9`
**Proposed Move**: `deprecated/backend/shared\core\agents\citation_agent.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import hashlib
**Duplicate Of**: `services\retrieval\free_tier.py:17`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `shared\embeddings\local_embedder.py`
**Symbol**: import hashlib
**Duplicate Of**: `shared\embeddings\local_embedder.py:4`
**Proposed Move**: `deprecated/backend/shared\embeddings\local_embedder.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import datetime
**Duplicate Of**: `services\retrieval\free_tier.py:24`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\analytics\metrics.py`
**Symbol**: import os
**Duplicate Of**: `services\analytics\metrics.py:6`
**Proposed Move**: `deprecated/backend/services\analytics\metrics.py`
**Reason**: import duplication

**File**: `services\gateway\cache_manager.py`
**Symbol**: import os
**Duplicate Of**: `services\gateway\cache_manager.py:20`
**Proposed Move**: `deprecated/backend/services\gateway\cache_manager.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import os
**Duplicate Of**: `services\retrieval\free_tier.py:20`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import os
**Duplicate Of**: `services\retrieval\orchestrator.py:123`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import os
**Duplicate Of**: `services\retrieval\orchestrator.py:123`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import os
**Duplicate Of**: `services\retrieval\orchestrator.py:123`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import fastapi.responses
**Duplicate Of**: `services\gateway\main.py:33`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import fastapi.responses
**Duplicate Of**: `services\gateway\main.py:33`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import fastapi.responses
**Duplicate Of**: `services\gateway\main.py:33`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: import dotenv
**Duplicate Of**: `services\analytics\integration_monitor.py:28`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import dataclasses
**Duplicate Of**: `services\retrieval\free_tier.py:27`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import enum
**Duplicate Of**: `services\retrieval\free_tier.py:28`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import pydantic
**Duplicate Of**: `services\gateway\main.py:34`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `shared\core\database.py`
**Symbol**: import sqlalchemy.ext.asyncio
**Duplicate Of**: `shared\core\database.py:17`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: import duplication

**File**: `shared\core\database.py`
**Symbol**: import sqlalchemy
**Duplicate Of**: `shared\core\database.py:21`
**Proposed Move**: `deprecated/backend/shared\core\database.py`
**Reason**: import duplication

**File**: `services\auto_upgrade\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\auto_upgrade\main.py:22`
**Proposed Move**: `deprecated/backend/services\auto_upgrade\main.py`
**Reason**: import duplication

**File**: `services\cicd\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\cicd\main.py:26`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: import duplication

**File**: `services\feeds\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\feeds\main.py:26`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: import duplication

**File**: `services\guided_prompt\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\guided_prompt\main.py:27`
**Proposed Move**: `deprecated/backend/services\guided_prompt\main.py`
**Reason**: import duplication

**File**: `services\model_registry\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\model_registry\main.py:23`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: import duplication

**File**: `services\model_router\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\model_router\main.py:22`
**Proposed Move**: `deprecated/backend/services\model_router\main.py`
**Reason**: import duplication

**File**: `services\observability\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\observability\main.py:27`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: import duplication

**File**: `services\observability\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\observability\main.py:27`
**Proposed Move**: `deprecated/backend/services\observability\main.py`
**Reason**: import duplication

**File**: `services\retrieval\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\retrieval\main.py:27`
**Proposed Move**: `deprecated/backend/services\retrieval\main.py`
**Reason**: import duplication

**File**: `services\security\main.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `services\security\main.py:27`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: import duplication

**File**: `shared\core\app_factory.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `shared\core\app_factory.py:37`
**Proposed Move**: `deprecated/backend/shared\core\app_factory.py`
**Reason**: import duplication

**File**: `shared\core\api\monitoring.py`
**Symbol**: import prometheus_client
**Duplicate Of**: `shared\core\api\monitoring.py:36`
**Proposed Move**: `deprecated/backend/shared\core\api\monitoring.py`
**Reason**: import duplication

**File**: `services\analytics\health_checks.py`
**Symbol**: import aiohttp
**Duplicate Of**: `services\analytics\health_checks.py:17`
**Proposed Move**: `deprecated/backend/services\analytics\health_checks.py`
**Reason**: import duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: import aiohttp
**Duplicate Of**: `services\analytics\integration_monitor.py:203`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: import duplication

**File**: `services\analytics\integration_monitor.py`
**Symbol**: import aiohttp
**Duplicate Of**: `services\analytics\integration_monitor.py:203`
**Proposed Move**: `deprecated/backend/services\analytics\integration_monitor.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import aiohttp
**Duplicate Of**: `services\retrieval\free_tier.py:30`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `shared\core\connection_pool.py`
**Symbol**: import aiohttp
**Duplicate Of**: `shared\core\connection_pool.py:24`
**Proposed Move**: `deprecated/backend/shared\core\connection_pool.py`
**Reason**: import duplication

**File**: `shared\core\health_checker.py`
**Symbol**: import shared.core.config.central_config
**Duplicate Of**: `shared\core\health_checker.py:147`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: import duplication

**File**: `shared\core\health_checker.py`
**Symbol**: import shared.core.config.central_config
**Duplicate Of**: `shared\core\health_checker.py:147`
**Proposed Move**: `deprecated/backend/shared\core\health_checker.py`
**Reason**: import duplication

**File**: `shared\core\vector_database.py`
**Symbol**: import pinecone
**Duplicate Of**: `shared\core\vector_database.py:23`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: import duplication

**File**: `shared\core\vector_database.py`
**Symbol**: import pinecone
**Duplicate Of**: `shared\core\vector_database.py:23`
**Proposed Move**: `deprecated/backend/shared\core\vector_database.py`
**Reason**: import duplication

**File**: `services\monitoring\health.py`
**Symbol**: import psutil
**Duplicate Of**: `services\monitoring\health.py:236`
**Proposed Move**: `deprecated/backend/services\monitoring\health.py`
**Reason**: import duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: import psutil
**Duplicate Of**: `shared\core\metrics_tracer.py:208`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: import duplication

**File**: `shared\core\metrics_tracer.py`
**Symbol**: import psutil
**Duplicate Of**: `shared\core\metrics_tracer.py:208`
**Proposed Move**: `deprecated/backend/shared\core\metrics_tracer.py`
**Reason**: import duplication

**File**: `services\gateway\gateway_app.py`
**Symbol**: import contextlib
**Duplicate Of**: `services\gateway\gateway_app.py:23`
**Proposed Move**: `deprecated/backend/services\gateway\gateway_app.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import contextlib
**Duplicate Of**: `services\gateway\main.py:248`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\cicd\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\cicd\main.py:813`
**Proposed Move**: `deprecated/backend/services\cicd\main.py`
**Reason**: import duplication

**File**: `services\crud\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\crud\main.py:614`
**Proposed Move**: `deprecated/backend/services\crud\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\gateway\main.py:3358`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\knowledge_graph\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\knowledge_graph\main.py:185`
**Proposed Move**: `deprecated/backend/services\knowledge_graph\main.py`
**Reason**: import duplication

**File**: `services\model_registry\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\model_registry\main.py:990`
**Proposed Move**: `deprecated/backend/services\model_registry\main.py`
**Reason**: import duplication

**File**: `services\security\main.py`
**Symbol**: import opentelemetry
**Duplicate Of**: `services\security\main.py:753`
**Proposed Move**: `deprecated/backend/services\security\main.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import uuid
**Duplicate Of**: `services\retrieval\free_tier.py:23`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\feeds\main.py`
**Symbol**: import shared.core.config.provider_config
**Duplicate Of**: `services\feeds\main.py:30`
**Proposed Move**: `deprecated/backend/services\feeds\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.gateway.streaming_manager
**Duplicate Of**: `services\gateway\main.py:218`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\retrieval\orchestrator.py`
**Symbol**: import requests
**Duplicate Of**: `services\retrieval\orchestrator.py:566`
**Proposed Move**: `deprecated/backend/services\retrieval\orchestrator.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.retrieval.free_tier
**Duplicate Of**: `services\gateway\main.py:124`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\streaming_manager.py`
**Symbol**: import services.retrieval.free_tier
**Duplicate Of**: `services\gateway\streaming_manager.py:467`
**Proposed Move**: `deprecated/backend/services\gateway\streaming_manager.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.gateway.middleware.observability
**Duplicate Of**: `services\gateway\main.py:73`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.gateway.middleware.security_hardening
**Duplicate Of**: `services\gateway\main.py:92`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.analytics.metrics.knowledge_platform_metrics
**Duplicate Of**: `services\gateway\main.py:113`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.analytics.metrics.knowledge_platform_metrics
**Duplicate Of**: `services\gateway\main.py:113`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.analytics.metrics.knowledge_platform_metrics
**Duplicate Of**: `services\gateway\main.py:113`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import services.analytics.metrics.knowledge_platform_metrics
**Duplicate Of**: `services\gateway\main.py:113`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: import services.gateway.huggingface_integration
**Duplicate Of**: `services\gateway\real_llm_integration.py:580`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.audit_service
**Duplicate Of**: `services\gateway\main.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.audit_service
**Duplicate Of**: `services\gateway\main.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.audit_service
**Duplicate Of**: `services\gateway\main.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: import shared.core.services.arangodb_service
**Duplicate Of**: `shared\core\services\index_fabric_service.py:154`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.vector_singleton_service
**Duplicate Of**: `services\gateway\main.py:313`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: import shared.core.services.vector_singleton_service
**Duplicate Of**: `shared\core\services\index_fabric_service.py:131`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: import duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: import shared.core.services.vector_singleton_service
**Duplicate Of**: `shared\core\services\index_fabric_service.py:131`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: import duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: import shared.core.services.vector_singleton_service
**Duplicate Of**: `shared\core\services\index_fabric_service.py:131`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.multi_lane_orchestrator
**Duplicate Of**: `services\gateway\main.py:1385`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.datastores_optimizer
**Duplicate Of**: `services\gateway\main.py:1483`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.core.services.datastores_optimizer
**Duplicate Of**: `services\gateway\main.py:1483`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `shared\core\services\index_fabric_service.py`
**Symbol**: import shared.core.services.meilisearch_service
**Duplicate Of**: `shared\core\services\index_fabric_service.py:121`
**Proposed Move**: `deprecated/backend/shared\core\services\index_fabric_service.py`
**Reason**: import duplication

**File**: `services\retrieval\warmup.py`
**Symbol**: import shared.embeddings.local_embedder
**Duplicate Of**: `services\retrieval\warmup.py:74`
**Proposed Move**: `deprecated/backend/services\retrieval\warmup.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.vectorstores.vector_store_service
**Duplicate Of**: `services\gateway\main.py:2538`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\main.py`
**Symbol**: import shared.vectorstores.vector_store_service
**Duplicate Of**: `services\gateway\main.py:2538`
**Proposed Move**: `deprecated/backend/services\gateway\main.py`
**Reason**: import duplication

**File**: `services\gateway\real_llm_integration.py`
**Symbol**: import services.gateway.providers
**Duplicate Of**: `services\gateway\real_llm_integration.py:70`
**Proposed Move**: `deprecated/backend/services\gateway\real_llm_integration.py`
**Reason**: import duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: import openai
**Duplicate Of**: `services\gateway\providers\gpu_providers.py:467`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: import duplication

**File**: `services\gateway\providers\gpu_providers.py`
**Symbol**: import openai
**Duplicate Of**: `services\gateway\providers\gpu_providers.py:467`
**Proposed Move**: `deprecated/backend/services\gateway\providers\gpu_providers.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import analytics_collector
**Duplicate Of**: `services\gateway\routes.py:90`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import analytics_collector
**Duplicate Of**: `services\gateway\routes.py:90`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import analytics_collector
**Duplicate Of**: `services\gateway\routes.py:90`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `services\gateway\routes.py`
**Symbol**: import shared.clients.microservices
**Duplicate Of**: `services\gateway\routes.py:343`
**Proposed Move**: `deprecated/backend/services\gateway\routes.py`
**Reason**: import duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `shared\llm\provider_order.py:926`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: import duplication

**File**: `shared\llm\provider_order.py`
**Symbol**: import sarvanom.shared.core.config.provider_config
**Duplicate Of**: `shared\llm\provider_order.py:926`
**Proposed Move**: `deprecated/backend/shared\llm\provider_order.py`
**Reason**: import duplication

**File**: `shared\vectorstores\connection_manager.py`
**Symbol**: import qdrant_client
**Duplicate Of**: `shared\vectorstores\connection_manager.py:17`
**Proposed Move**: `deprecated/backend/shared\vectorstores\connection_manager.py`
**Reason**: import duplication

**File**: `shared\vectorstores\vector_store_service.py`
**Symbol**: import qdrant_client
**Duplicate Of**: `shared\vectorstores\vector_store_service.py:352`
**Proposed Move**: `deprecated/backend/shared\vectorstores\vector_store_service.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import bs4
**Duplicate Of**: `services\retrieval\free_tier.py:32`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\retrieval\free_tier.py`
**Symbol**: import feedparser
**Duplicate Of**: `services\retrieval\free_tier.py:49`
**Proposed Move**: `deprecated/backend/services\retrieval\free_tier.py`
**Reason**: import duplication

**File**: `services\gateway\middleware\security_hardening.py`
**Symbol**: import starlette.responses
**Duplicate Of**: `services\gateway\middleware\security_hardening.py:45`
**Proposed Move**: `deprecated/backend/services\gateway\middleware\security_hardening.py`
**Reason**: import duplication

**File**: `shared\core\database\connection.py`
**Symbol**: import sqlalchemy.pool
**Duplicate Of**: `shared\core\database\connection.py:29`
**Proposed Move**: `deprecated/backend/shared\core\database\connection.py`
**Reason**: import duplication

**File**: `shared\core\secure_auth.py`
**Symbol**: import backend.repositories.database.user_repository
**Duplicate Of**: `shared\core\secure_auth.py:546`
**Proposed Move**: `deprecated/backend/shared\core\secure_auth.py`
**Reason**: import duplication

**File**: `shared\core\socket_io_manager.py`
**Symbol**: import socketio
**Duplicate Of**: `shared\core\socket_io_manager.py:53`
**Proposed Move**: `deprecated/backend/shared\core\socket_io_manager.py`
**Reason**: import duplication

**File**: `shared\core\services\vector_singleton_service.py`
**Symbol**: import qdrant_client.models
**Duplicate Of**: `shared\core\services\vector_singleton_service.py:43`
**Proposed Move**: `deprecated/backend/shared\core\services\vector_singleton_service.py`
**Reason**: import duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: import qdrant_client.http
**Duplicate Of**: `shared\core\services\datastores_optimizer.py:349`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: import duplication

**File**: `shared\core\services\datastores_optimizer.py`
**Symbol**: import qdrant_client.http
**Duplicate Of**: `shared\core\services\datastores_optimizer.py:349`
**Proposed Move**: `deprecated/backend/shared\core\services\datastores_optimizer.py`
**Reason**: import duplication

## Frontend Deprecations

### Medium Priority

**File**: `frontend\src\app\(main)\page.tsx`
**Symbol**: page /
**Duplicate Of**: `frontend\src\app\page.tsx`
**Proposed Move**: `deprecated/frontend/frontend\src\app\(main)\page.tsx`
**Reason**: page duplication

### Low Priority

**File**: `frontend\src\components\theme\ThemeProvider.tsx`
**Symbol**: unused component ThemeProvider
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\theme\ThemeProvider.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\layout\Header.tsx`
**Symbol**: unused component Header
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\layout\Header.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\security\SecurityFooter.tsx`
**Symbol**: unused component SecurityFooter
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\security\SecurityFooter.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\analytics\DataNovaDashboard.tsx`
**Symbol**: unused component DataNovaDashboard
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\analytics\DataNovaDashboard.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\theme\ThemeToggle.tsx`
**Symbol**: unused component ThemeToggle
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\theme\ThemeToggle.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\search\CitationTooltip.tsx`
**Symbol**: unused component CitationTooltip
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\search\CitationTooltip.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\streaming\TokenStream.tsx`
**Symbol**: unused component TokenStream
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\streaming\TokenStream.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\ui\FallbackBadge.tsx`
**Symbol**: unused component FallbackBadge
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\ui\FallbackBadge.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\blog\EruditeBlog.tsx`
**Symbol**: unused component EruditeBlog
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\blog\EruditeBlog.tsx`
**Reason**: component duplication

**File**: `frontend\src\components\layout\StandardLayout.tsx`
**Symbol**: unused component StandardLayout
**Duplicate Of**: `unused`
**Proposed Move**: `deprecated/frontend/frontend\src\components\layout\StandardLayout.tsx`
**Reason**: component duplication

## Summary

- **Backend Duplicates**: 1841
- **Frontend Duplicates**: 11
- **Total Duplicates**: 1852

## Next Steps

1. Review proposed moves for safety
2. Create /deprecated/ directory structure
3. Move files to deprecated locations
4. Update import statements
5. Test application functionality
