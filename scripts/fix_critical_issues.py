#!/usr/bin/env python3
"""
Critical Issues Fix Script for SarvanOM

This script automatically fixes the critical issues identified in the analysis:
1. Consolidate service entry points
2. Fix import path inconsistencies
3. Remove hardcoded values
4. Update stub implementations

Usage:
    python scripts/fix_critical_issues.py --fix-all
    python scripts/fix_critical_issues.py --fix-imports
    python scripts/fix_critical_issues.py --fix-config
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_import_paths():
    """Fix inconsistent import paths throughout the codebase."""
    print("🔧 Fixing import paths...")
    
    # Define import mappings
    import_mappings = {
        r'from shared\.core\.config\.central_config import get_central_config': 
            'from shared.core.config import get_central_config',
        r'from shared\.core\.logging\.structured_logger import get_logger': 
            'from shared.core.logging import get_logger',
        r'from shared\.core\.metrics\.metrics_service import get_metrics_service': 
            'from shared.core.metrics import get_metrics_service',
        r'from shared\.core\.cache\.cache_manager import get_cache_manager': 
            'from shared.core.cache import get_cache_manager',
        r'from shared\.core\.llm_client\.llm_client import get_llm_client': 
            'from shared.core.llm_client import get_llm_client',
    }
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_files = 0
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply import mappings
            for old_pattern, new_pattern in import_mappings.items():
                content = re.sub(old_pattern, new_pattern, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed imports in {file_path}")
                fixed_files += 1
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"🎉 Fixed imports in {fixed_files} files")

def create_shared_core_init():
    """Create proper __init__.py files for shared modules."""
    print("📁 Creating shared module structure...")
    
    # Create shared/core/__init__.py
    shared_core_init = '''"""
Shared Core Modules - SarvanOM

This module provides core functionality shared across all services.
"""

# Core configuration
from .config import get_central_config
from .logging import get_logger
from .metrics import get_metrics_service
from .cache import get_cache_manager
from .llm_client import get_llm_client

__all__ = [
    'get_central_config',
    'get_logger', 
    'get_metrics_service',
    'get_cache_manager',
    'get_llm_client',
]
'''
    
    # Create shared/__init__.py
    shared_init = '''"""
Shared Modules - SarvanOM

This module contains shared functionality across all services.
"""

# Core modules
from . import core

__all__ = ['core']
'''
    
    # Write files
    shared_core_path = Path('shared/core/__init__.py')
    shared_core_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(shared_core_path, 'w', encoding='utf-8') as f:
        f.write(shared_core_init)
    
    shared_path = Path('shared/__init__.py')
    with open(shared_path, 'w', encoding='utf-8') as f:
        f.write(shared_init)
    
    print("✅ Created shared module structure")

def remove_conflicting_entry_points():
    """Remove conflicting service entry points."""
    print("🗑️ Removing conflicting entry points...")
    
    # List of files to remove or rename
    conflicting_files = [
        'backend/main.py',  # Remove this conflicting entry point
    ]
    
    for file_path in conflicting_files:
        if os.path.exists(file_path):
            # Backup before removing
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)
            os.remove(file_path)
            print(f"✅ Removed {file_path} (backed up to {backup_path})")
        else:
            print(f"⏭️ {file_path} doesn't exist, skipping")

def fix_hardcoded_values():
    """Remove hardcoded values from configuration files."""
    print("🔐 Fixing hardcoded values...")
    
    # Files to check for hardcoded values
    config_files = [
        'docker-compose.yml',
        'services/deployment/docker/docker-compose.yml',
        'docker-compose.meilisearch.yml',
    ]
    
    # Patterns to replace
    hardcoded_patterns = {
        r'MEILI_MASTER_KEY=sarvanom-master-key-2024': 'MEILI_MASTER_KEY=${MEILI_MASTER_KEY}',
        r'MEILI_MASTER_KEY=your-master-key-here': 'MEILI_MASTER_KEY=${MEILI_MASTER_KEY}',
        r'JWT_SECRET_KEY=your-secret-key': 'JWT_SECRET_KEY=${JWT_SECRET_KEY}',
        r'DATABASE_PASSWORD=password': 'DATABASE_PASSWORD=${DATABASE_PASSWORD}',
    }
    
    for file_path in config_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply replacements
                for old_pattern, new_pattern in hardcoded_patterns.items():
                    content = re.sub(old_pattern, new_pattern, content)
                
                # Write back if changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed hardcoded values in {file_path}")
                else:
                    print(f"⏭️ No hardcoded values found in {file_path}")
                    
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")

def create_env_example():
    """Create .env.example with all required environment variables."""
    print("📝 Creating .env.example...")
    
    env_example_content = '''# SarvanOM Environment Variables
# Copy this file to .env and fill in your values

# Application
ENVIRONMENT=development
APP_VERSION=1.0.0
SERVICE_NAME=sarvanom-api

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sarvanom
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sarvanom
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-database-password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=sarvanom_vectors

# Search Engine
MEILISEARCH_URL=http://localhost:7700
MEILI_MASTER_KEY=your-meilisearch-master-key
MEILISEARCH_INDEX=sarvanom_documents

# Knowledge Graph
ARANGO_URL=http://localhost:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=your-arangodb-password
ARANGO_DATABASE=knowledge_graph

# AI Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PASSWORD=admin

# Service URLs
AUTH_SERVICE_URL=http://localhost:8004
RETRIEVAL_SERVICE_URL=http://localhost:8001
SYNTHESIS_SERVICE_URL=http://localhost:8002
FACTCHECK_SERVICE_URL=http://localhost:8003

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Cache
CACHE_TTL_DEFAULT=300
CACHE_TTL_USER=600
CACHE_TTL_QUERY=3600
'''
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example_content)
    
    print("✅ Created .env.example")

def update_synthesis_service():
    """Update synthesis service with real LLM integration."""
    print("🤖 Updating synthesis service...")
    
    synthesis_main = '''from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.llm_client import get_llm_client
from shared.core.cache import get_cache_manager
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import SynthesisRequest, SynthesisResponse

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-synthesis",
    version=config.app_version,
    description="Synthesis microservice with real LLM integration",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {"service": "synthesis", "status": "healthy", "timestamp": datetime.now().isoformat()}

_t0 = time.time()
REQUEST_COUNTER = Counter("synthesis_requests_total", "Total synthesis requests")
REQUEST_LATENCY = Histogram("synthesis_request_latency_seconds", "Synthesis request latency")

@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root() -> dict:
    return {"service": "synthesis", "version": config.app_version, "status": "ok"}

def format_sources_for_llm(sources: list) -> str:
    """Format sources for LLM consumption."""
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        formatted_sources.append(f"Source {i}: {source.get('content', '')}")
    return "\\n\\n".join(formatted_sources)

def extract_citations(content: str) -> list:
    """Extract citations from LLM response."""
    import re
    citations = []
    # Look for citation pattern 【source†Lx-Ly】
    citation_pattern = r'【([^†]+)†L(\d+)-L(\d+)】'
    matches = re.findall(citation_pattern, content)
    for match in matches:
        citations.append({
            "source": match[0],
            "start_line": int(match[1]),
            "end_line": int(match[2])
        })
    return citations

def calculate_confidence(content: str, sources: list) -> float:
    """Calculate confidence score for synthesis."""
    # Simple confidence calculation based on content length and source count
    if not sources:
        return 0.0
    
    content_length = len(content)
    source_count = len(sources)
    
    # Basic confidence calculation
    base_confidence = min(0.9, source_count * 0.1)
    length_confidence = min(0.1, content_length / 1000 * 0.1)
    
    return min(1.0, base_confidence + length_confidence)

@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(payload: SynthesisRequest) -> SynthesisResponse:
    REQUEST_COUNTER.inc()
    
    with REQUEST_LATENCY.time():
        try:
            # Get LLM client and cache
            llm_client = get_llm_client()
            cache = get_cache_manager()
            
            # Create cache key
            cache_key = f"synthesis:{hash(payload.query)}:{hash(str(payload.sources))}"
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for synthesis", query=payload.query[:100])
                return SynthesisResponse(**cached_result)
            
            # Format sources for LLM
            sources_text = format_sources_for_llm(payload.sources)
            
            # Create synthesis prompt
            prompt = f"""
            Query: {payload.query}
            
            Sources:
            {sources_text}
            
            Instructions:
            1. Generate a comprehensive answer using ONLY the provided sources
            2. Include citations in format 【source†Lx-Ly】
            3. If information is missing from sources, say so
            4. Structure the answer clearly with headings if needed
            5. Maximum {payload.max_tokens} tokens
            6. Be accurate and factual
            """
            
            # Call LLM
            response = await llm_client.generate(
                prompt=prompt,
                max_tokens=payload.max_tokens,
                temperature=0.3
            )
            
            # Extract citations
            citations = extract_citations(response.content)
            
            # Calculate confidence
            confidence = calculate_confidence(response.content, payload.sources)
            
            # Create result
            result = SynthesisResponse(
                answer=response.content,
                method="llm_synthesis",
                tokens=response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else len(response.content),
                citations=citations,
                confidence=confidence
            )
            
            # Cache result for 1 hour
            await cache.set(cache_key, result.dict(), ttl=3600)
            
            logger.info("Synthesis completed", 
                       query=payload.query[:100], 
                       tokens=result.tokens,
                       confidence=confidence)
            
            return result
            
        except Exception as e:
            logger.error("Synthesis failed", error=str(e), query=payload.query[:100])
            # Fallback to stub implementation
            answer = f"SYNTHESIZED: {payload.query[:100]} (using {len(payload.sources)} sources) - Error: {str(e)}"
            return SynthesisResponse(
                answer=answer,
                method="stub_synthesis_fallback",
                tokens=min(payload.max_tokens, len(answer)),
                citations=[],
                confidence=0.0
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.synthesis.main:app", host="0.0.0.0", port=8002, reload=True)
'''
    
    synthesis_path = Path('services/synthesis/main.py')
    synthesis_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(synthesis_path, 'w', encoding='utf-8') as f:
        f.write(synthesis_main)
    
    print("✅ Updated synthesis service with real LLM integration")

def update_retrieval_service():
    """Update retrieval service with real vector search."""
    print("🔍 Updating retrieval service...")
    
    retrieval_main = '''from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.cache import get_cache_manager
from shared.embeddings.local_embedder import embed_texts
from shared.vectorstores.vector_store_service import (
    ChromaVectorStore,
    QdrantVectorStore,
    InMemoryVectorStore,
    VectorDocument,
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalIndexRequest,
    RetrievalIndexResponse,
)

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-retrieval",
    version=config.app_version,
    description="Retrieval microservice with real vector search",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {
        "service": "retrieval",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

_service_start = time.time()
REQUEST_COUNTER = Counter("retrieval_requests_total", "Total retrieval requests")
REQUEST_LATENCY = Histogram("retrieval_request_latency_seconds", "Retrieval request latency")

def _init_vector_store():
    cfg = get_central_config()
    provider = getattr(cfg, "vector_db_provider", "chroma").lower()
    if provider == "qdrant":
        return QdrantVectorStore(
            url=str(cfg.qdrant_url),
            api_key=(cfg.qdrant_api_key.get_secret_value() if cfg.qdrant_api_key else None),
            collection=str(cfg.qdrant_collection),
            vector_size=int(getattr(cfg, "embedding_dimension", 384)),
        )
    elif provider == "inmemory" or provider == "memory":
        return InMemoryVectorStore()
    # default to chroma (local/in-process)
    return ChromaVectorStore(collection_name="knowledge")

VECTOR_STORE = _init_vector_store()

@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root() -> dict:
    return {
        "service": "retrieval",
        "version": config.app_version,
        "status": "ok",
    }

@app.post("/search", response_model=RetrievalSearchResponse)
async def search(payload: RetrievalSearchRequest) -> RetrievalSearchResponse:
    REQUEST_COUNTER.inc()
    
    with REQUEST_LATENCY.time():
        try:
            # Get cache
            cache = get_cache_manager()
            
            # Create cache key
            cache_key = f"search:{hash(payload.query)}:{payload.max_results}"
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for search", query=payload.query[:100])
                return RetrievalSearchResponse(**cached_result)
            
            # Generate embeddings for query
            query_embedding = await embed_texts([payload.query])
            
            # Perform vector search
            search_results = await VECTOR_STORE.search(
                query_embedding=query_embedding[0],
                top_k=payload.max_results
            )
            
            # Format results
            sources = []
            relevance_scores = []
            
            for result in search_results:
                if isinstance(result, tuple):
                    doc, score = result
                    sources.append({
                        "id": doc.id,
                        "content": doc.text,
                        "metadata": doc.metadata,
                        "score": score
                    })
                    relevance_scores.append(score)
                else:
                    # Handle dict format
                    sources.append(result)
                    relevance_scores.append(result.get("score", 0.0))
            
            # Create response
            response = RetrievalSearchResponse(
                sources=sources,
                method="vector_search",
                total_results=len(sources),
                relevance_scores=relevance_scores,
                limit=payload.max_results
            )
            
            # Cache result for 1 hour
            await cache.set(cache_key, response.dict(), ttl=3600)
            
            logger.info("Search completed", 
                       query=payload.query[:100], 
                       results_count=len(sources))
            
            return response
            
        except Exception as e:
            logger.error("Search failed", error=str(e), query=payload.query[:100])
            # Fallback to empty results
            return RetrievalSearchResponse(
                sources=[],
                method="stub_search_fallback",
                total_results=0,
                relevance_scores=[],
                limit=payload.max_results
            )

@app.post("/index", response_model=RetrievalIndexResponse)
async def index(payload: RetrievalIndexRequest) -> RetrievalIndexResponse:
    try:
        # Validate input
        payload.validate_lengths()
        
        # Generate embeddings
        embeddings = await embed_texts(payload.texts)
        
        # Create vector documents
        documents = []
        for i, (doc_id, text, embedding) in enumerate(zip(payload.ids, payload.texts, embeddings)):
            metadata = payload.metadatas[i] if i < len(payload.metadatas) else {}
            documents.append(VectorDocument(
                id=doc_id,
                text=text,
                embedding=embedding,
                metadata=metadata
            ))
        
        # Index documents
        upserted_count = await VECTOR_STORE.upsert(documents)
        
        logger.info("Indexing completed", 
                   documents_count=len(documents),
                   upserted_count=upserted_count)
        
        return RetrievalIndexResponse(upserted=upserted_count)
        
    except Exception as e:
        logger.error("Indexing failed", error=str(e))
        return RetrievalIndexResponse(upserted=0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.retrieval.main:app", host="0.0.0.0", port=8001, reload=True)
'''
    
    retrieval_path = Path('services/retrieval/main.py')
    retrieval_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(retrieval_path, 'w', encoding='utf-8') as f:
        f.write(retrieval_main)
    
    print("✅ Updated retrieval service with real vector search")

def main():
    """Main function to run all fixes."""
    parser = argparse.ArgumentParser(description='Fix critical issues in SarvanOM')
    parser.add_argument('--fix-all', action='store_true', help='Apply all fixes')
    parser.add_argument('--fix-imports', action='store_true', help='Fix import paths')
    parser.add_argument('--fix-config', action='store_true', help='Fix configuration')
    parser.add_argument('--fix-services', action='store_true', help='Fix service implementations')
    
    args = parser.parse_args()
    
    if args.fix_all or args.fix_imports:
        create_shared_core_init()
        fix_import_paths()
    
    if args.fix_all or args.fix_config:
        remove_conflicting_entry_points()
        fix_hardcoded_values()
        create_env_example()
    
    if args.fix_all or args.fix_services:
        update_synthesis_service()
        update_retrieval_service()
    
    if not any([args.fix_all, args.fix_imports, args.fix_config, args.fix_services]):
        print("🔧 Running all fixes...")
        create_shared_core_init()
        fix_import_paths()
        remove_conflicting_entry_points()
        fix_hardcoded_values()
        create_env_example()
        update_synthesis_service()
        update_retrieval_service()
    
    print("\n🎉 Critical issues fixed!")
    print("\nNext steps:")
    print("1. Review the changes made")
    print("2. Test the services")
    print("3. Update your .env file with proper values")
    print("4. Run the services to verify they work")

if __name__ == "__main__":
    main()
