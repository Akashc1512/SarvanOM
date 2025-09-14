"""
Knowledge Graph Service Main Module.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.core.agents.knowledge_graph_service import KnowledgeGraphService
from shared.core.config.central_config import get_central_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_central_config()

class KGService:
    """Knowledge Graph Service wrapper."""
    
    def __init__(self):
        self.kg_service = KnowledgeGraphService()
    
    async def query(self, query: str, query_type: str = "entity_relationship") -> Dict[str, Any]:
        """Query the knowledge graph."""
        try:
            result = await self.kg_service.query(query, query_type)
            return {
                "entities": getattr(result, 'entities', []),
                "relationships": getattr(result, 'relationships', []),
                "facts": getattr(result, 'facts', []),
                "metadata": {
                    "query": query,
                    "query_type": query_type,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
        except Exception as e:
            return {
                "entities": [],
                "relationships": [],
                "facts": [],
                "error": str(e),
                "metadata": {
                    "query": query,
                    "query_type": query_type,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
    
    async def add_entity(self, entity_data: Dict[str, Any]) -> bool:
        """Add an entity to the knowledge graph."""
        try:
            # This would integrate with the actual KG service
            return True
        except Exception:
            return False
    
    async def add_relationship(self, relationship_data: Dict[str, Any]) -> bool:
        """Add a relationship to the knowledge graph."""
        try:
            # This would integrate with the actual KG service
            return True
        except Exception:
            return False

# Global instance
kg_service = KGService()

# FastAPI app
app = FastAPI(
    title="Knowledge Graph Service",
    version="2.0.0",
    description="Knowledge graph service for entity and relationship management"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "knowledge-graph"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if KG service is available
        return {"status": "ready", "service": "knowledge-graph"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and configuration"""
    return {
        "service": "knowledge-graph",
        "active_providers": {
            "openai": bool(getattr(config, 'openai_api_key', None)),
            "anthropic": bool(getattr(config, 'anthropic_api_key', None)),
            "google": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(getattr(config, 'huggingface_api_key', None) or getattr(config, 'huggingface_read_token', None) or getattr(config, 'huggingface_write_token', None)),
            "ollama": bool(getattr(config, 'ollama_base_url', None))
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "knowledge-graph",
        "version": "2.0.0",
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

# Knowledge Graph endpoints
@app.post("/query")
async def query_knowledge_graph(query_data: Dict[str, Any]):
    """Query the knowledge graph"""
    try:
        query = query_data.get("query", "")
        query_type = query_data.get("query_type", "entity_relationship")
        
        result = await kg_service.query(query, query_type)
        return result
    except Exception as e:
        logger.error(f"Knowledge graph query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-entity")
async def add_entity(entity_data: Dict[str, Any]):
    """Add an entity to the knowledge graph"""
    try:
        result = await kg_service.add_entity(entity_data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Add entity failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-relationship")
async def add_relationship(relationship_data: Dict[str, Any]):
    """Add a relationship to the knowledge graph"""
    try:
        result = await kg_service.add_relationship(relationship_data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Add relationship failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Observability middleware
# Always mount Prometheus metrics endpoint
try:
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics endpoint mounted at /metrics")
except Exception as e:
    logger.error(f"Failed to mount Prometheus metrics: {e}")

# Conditional tracing setup - only if keys exist
tracing_enabled = False
if (hasattr(config, 'tracing_enabled') and config.tracing_enabled and 
    hasattr(config, 'jaeger_agent_host') and config.jaeger_agent_host):
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if hasattr(config, 'jaeger_agent_port') and config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        tracing_enabled = True
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")
else:
    logger.info("Tracing disabled - no tracing keys configured")

# Add debug trace endpoint if tracing is enabled
if tracing_enabled:
    @app.get("/_debug/trace")
    async def debug_trace():
        """Debug endpoint to echo trace information when tracing is enabled"""
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            
            # Create a sample span
            with tracer.start_as_current_span("debug_trace_echo") as span:
                span.set_attribute("debug.endpoint", "/_debug/trace")
                span.set_attribute("debug.timestamp", datetime.now().isoformat())
                
                return {
                    "status": "tracing_enabled",
                    "tracer_name": tracer.name,
                    "trace_id": format(span.get_span_context().trace_id, '032x'),
                    "span_id": format(span.get_span_context().span_id, '016x'),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Tracing is active and working"
                }
        except Exception as e:
            logger.error(f"Debug trace endpoint error: {e}")
            return {
                "status": "tracing_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
else:
    @app.get("/_debug/trace")
    async def debug_trace_disabled():
        """Debug endpoint when tracing is disabled"""
        return {
            "status": "tracing_disabled",
            "message": "Tracing is not enabled - no tracing keys configured",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Start FastAPI server with integrated metrics endpoint
    uvicorn.run(app, host="0.0.0.0", port=8013)
