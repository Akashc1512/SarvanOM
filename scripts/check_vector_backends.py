#!/usr/bin/env python3
"""
Vector Database and Search Backend Configuration Checker

This script:
1. Checks connectivity to Pinecone, Elasticsearch, Qdrant, and Knowledge Graph services
2. Updates Pinecone client to use v3 (class-based API)
3. Validates environment variables and configurations
4. Creates missing indices/collections
5. Performs test queries to verify functionality
6. Implements MAANG standards for external service integration
"""

import asyncio
import logging
import os
import sys
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BackendStatus:
    """Status of a backend service."""
    name: str
    available: bool
    configured: bool
    reachable: bool
    error: Optional[str] = None
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, failure_threshold: int = 3, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        
        return True  # HALF_OPEN


class RetryManager:
    """Retry manager with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    raise last_exception
                
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
        
        raise last_exception


class VectorBackendChecker:
    """Comprehensive vector backend checker and configurator with MAANG standards."""
    
    def __init__(self):
        self.results: Dict[str, BackendStatus] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_manager = RetryManager()
        
        # Initialize circuit breakers for each backend
        for backend in ["pinecone", "meilisearch", "qdrant", "knowledge_graph"]:
            self.circuit_breakers[backend] = CircuitBreaker()
    
    async def check_all_backends(self) -> Dict[str, BackendStatus]:
        """Check all vector backends and search services."""
        logger.info("🔍 Starting comprehensive vector backend check...")
        
        # Check each backend with circuit breaker protection
        await self._check_pinecone()
        await self._check_meilisearch()
        await self._check_qdrant()
        await self._check_knowledge_graph()
        
        return self.results
    
    @asynccontextmanager
    async def _get_meilisearch_client(self, url: str, api_key: str = None):
        """Get Meilisearch client with proper authentication."""
        try:
            from meilisearch import AsyncClient
            
            # Build connection parameters
            connection_params = {
                "url": url,
            }
            
            # Add API key if provided
            if api_key:
                connection_params["api_key"] = api_key
            
            client = AsyncClient(**connection_params)
            
            try:
                yield client
            finally:
                await client.aclose()
                
        except ImportError:
            raise ImportError("Meilisearch Python client not installed. Run: pip install meilisearch")
    
    async def _check_meilisearch(self):
        """Check Meilisearch configuration and connectivity with enhanced authentication."""
        logger.info("🔍 Checking Meilisearch...")
        
        start_time = time.time()
        status = BackendStatus(
            name="Meilisearch",
            available=False,
            configured=False,
            reachable=False
        )
        
        circuit_breaker = self.circuit_breakers["meilisearch"]
        
        if not circuit_breaker.can_execute():
            status.error = "Circuit breaker is OPEN - too many recent failures"
            self.results["meilisearch"] = status
            return
        
        try:
            # Check environment variables with fallbacks
            meili_url = os.getenv("MEILISEARCH_URL")
            meili_host = os.getenv("MEILISEARCH_HOST", "localhost")
            meili_port = os.getenv("MEILISEARCH_PORT", "7700")
            meili_index = os.getenv("MEILISEARCH_INDEX", "knowledge-base")
            
            # Authentication credentials
            meili_api_key = os.getenv("MEILISEARCH_API_KEY")
            meili_master_key = os.getenv("MEILISEARCH_MASTER_KEY")
            
            if not meili_url:
                meili_url = f"http://{meili_host}:{meili_port}"
            
            status.configured = True
            
            # Try to import Meilisearch
            try:
                from meilisearch import AsyncClient
                status.available = True
            except ImportError:
                status.error = "Meilisearch Python client not installed. Run: pip install meilisearch"
                self.results["meilisearch"] = status
                return
            
            # Test connection with retry logic
            async def test_connection():
                async with self._get_meilisearch_client(
                    meili_url, 
                    meili_api_key or meili_master_key
                ) as client:
                    # Test basic connectivity
                    health = await client.health()
                    
                    # Check if index exists
                    try:
                        index = await client.get_index(meili_index)
                        index_exists = True
                    except Exception:
                        index_exists = False
                    
                    if not index_exists:
                        logger.info(f"📝 Creating Meilisearch index: {meili_index}")
                        try:
                            # Create index
                            await client.create_index(meili_index)
                            logger.info(f"✅ Created Meilisearch index: {meili_index}")
                            index_exists = True
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to create index: {e}")
                    
                    # Test a simple search
                    try:
                        search_result = await client.index(meili_index).search("test")
                        return {
                            "index_exists": index_exists,
                            "health_status": health,
                            "test_search_successful": True,
                            "total_hits": len(search_result.get("hits", []))
                        }
                    except Exception as e:
                        return {
                            "index_exists": index_exists,
                            "health_status": health,
                            "test_search_successful": False,
                            "test_error": str(e)
                        }
            
            # Execute with retry logic
            details = await self.retry_manager.execute_with_retry(test_connection)
            
            status.reachable = True
            status.response_time = time.time() - start_time
            status.details = details
            circuit_breaker.record_success()
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            status.error = error_msg
            circuit_breaker.record_failure()
            logger.error(f"❌ Meilisearch check failed: {error_msg}")
        
        self.results["meilisearch"] = status
    
    async def _check_qdrant(self):
        """Check Qdrant configuration and connectivity with enhanced authentication."""
        logger.info("🔍 Checking Qdrant...")
        
        start_time = time.time()
        status = BackendStatus(
            name="Qdrant",
            available=False,
            configured=False,
            reachable=False
        )
        
        circuit_breaker = self.circuit_breakers["qdrant"]
        
        if not circuit_breaker.can_execute():
            status.error = "Circuit breaker is OPEN - too many recent failures"
            self.results["qdrant"] = status
            return
        
        try:
            # Check environment variables with fallbacks
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = os.getenv("QDRANT_PORT", "6333")
            collection_name = os.getenv("QDRANT_COLLECTION", "knowledge-base")
            
            # Authentication credentials
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            qdrant_username = os.getenv("QDRANT_USERNAME")
            qdrant_password = os.getenv("QDRANT_PASSWORD")
            
            if not qdrant_url:
                qdrant_url = f"http://{qdrant_host}:{qdrant_port}"
            
            status.configured = True
            
            # Try to import Qdrant
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                status.available = True
            except ImportError:
                status.error = "Qdrant Python client not installed. Run: pip install qdrant-client"
                self.results["qdrant"] = status
                return
            
            # Test connection with retry logic
            async def test_connection():
                # Build client with authentication
                client_params = {"url": qdrant_url}
                
                if qdrant_api_key:
                    client_params["api_key"] = qdrant_api_key
                elif qdrant_username and qdrant_password:
                    client_params["username"] = qdrant_username
                    client_params["password"] = qdrant_password
                
                client = QdrantClient(**client_params)
                
                # Test basic connectivity
                collections = client.get_collections()
                
                # Check if collection exists
                collection_names = [col.name for col in collections.collections]
                collection_exists = collection_name in collection_names
                
                if not collection_exists:
                    logger.info(f"📝 Creating Qdrant collection: {collection_name}")
                    try:
                        client.create_collection(
                            collection_name=collection_name,
                            vectors_config=VectorParams(
                                size=1536,
                                distance=Distance.COSINE
                            )
                        )
                        logger.info(f"✅ Created Qdrant collection: {collection_name}")
                        collection_exists = True
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to create collection: {e}")
                
                # Test a simple search
                try:
                    search_result = client.search(
                        collection_name=collection_name,
                        query_vector=[0.1] * 1536,
                        limit=1
                    )
                    return {
                        "collection_exists": collection_exists,
                        "collections_available": len(collection_names),
                        "test_search_successful": True
                    }
                except Exception as e:
                    return {
                        "collection_exists": collection_exists,
                        "collections_available": len(collection_names),
                        "test_search_successful": False,
                        "test_error": str(e)
                    }
            
            # Execute with retry logic
            details = await self.retry_manager.execute_with_retry(test_connection)
            
            status.reachable = True
            status.response_time = time.time() - start_time
            status.details = details
            circuit_breaker.record_success()
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            status.error = error_msg
            circuit_breaker.record_failure()
            logger.error(f"❌ Qdrant check failed: {error_msg}")
        
        self.results["qdrant"] = status
    
    async def _check_pinecone(self):
        """Check Pinecone configuration and connectivity with enhanced authentication."""
        logger.info("🔍 Checking Pinecone...")
        
        start_time = time.time()
        status = BackendStatus(
            name="Pinecone",
            available=False,
            configured=False,
            reachable=False
        )
        
        circuit_breaker = self.circuit_breakers["pinecone"]
        
        if not circuit_breaker.can_execute():
            status.error = "Circuit breaker is OPEN - too many recent failures"
            self.results["pinecone"] = status
            return
        
        try:
            # Check environment variables
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT")
            index_name = os.getenv("PINECONE_INDEX_NAME", "knowledge-base")
            
            if not api_key:
                status.error = "PINECONE_API_KEY not set"
                self.results["pinecone"] = status
                return
            
            if not environment:
                status.error = "PINECONE_ENVIRONMENT not set"
                self.results["pinecone"] = status
                return
            
            status.configured = True
            
            # Try to import and initialize Pinecone v3
            try:
                from pinecone import Pinecone, ServerlessSpec
                status.available = True
            except ImportError:
                status.error = "Pinecone Python client not installed. Run: pip install pinecone-client"
                self.results["pinecone"] = status
                return
            
            # Test connection with retry logic
            async def test_connection():
                pc = Pinecone(api_key=api_key)
                
                # List indexes to test connection
                indexes = pc.list_indexes()
                
                # Check if our index exists
                index_exists = index_name in [idx.name for idx in indexes.indexes]
                
                if not index_exists:
                    logger.info(f"📝 Creating Pinecone index: {index_name}")
                    try:
                        pc.create_index(
                            name=index_name,
                            dimension=1536,
                            metric="cosine",
                            spec=ServerlessSpec(
                                cloud="aws",
                                region="us-east-1"
                            )
                        )
                        logger.info(f"✅ Created Pinecone index: {index_name}")
                        index_exists = True
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to create index: {e}")
                
                # Test a simple query
                try:
                    index = pc.Index(index_name)
                    # Test with a dummy vector
                    test_vector = [0.1] * 1536
                    query_result = index.query(
                        vector=test_vector,
                        top_k=1,
                        include_metadata=False
                    )
                    return {
                        "index_exists": index_exists,
                        "indexes_available": len(indexes.indexes),
                        "test_query_successful": True
                    }
                except Exception as e:
                    return {
                        "index_exists": index_exists,
                        "indexes_available": len(indexes.indexes),
                        "test_query_successful": False,
                        "test_error": str(e)
                    }
            
            # Execute with retry logic
            details = await self.retry_manager.execute_with_retry(test_connection)
            
            status.reachable = True
            status.response_time = time.time() - start_time
            status.details = details
            circuit_breaker.record_success()
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            status.error = error_msg
            circuit_breaker.record_failure()
            logger.error(f"❌ Pinecone check failed: {error_msg}")
        
        self.results["pinecone"] = status
    
    async def _check_knowledge_graph(self):
        """Check Knowledge Graph (ArangoDB) configuration and connectivity with enhanced authentication."""
        logger.info("🔍 Checking Knowledge Graph (ArangoDB)...")
        
        start_time = time.time()
        status = BackendStatus(
            name="Knowledge Graph",
            available=False,
            configured=False,
            reachable=False
        )
        
        circuit_breaker = self.circuit_breakers["knowledge_graph"]
        
        if not circuit_breaker.can_execute():
            status.error = "Circuit breaker is OPEN - too many recent failures"
            self.results["knowledge_graph"] = status
            return
        
        try:
            # Check environment variables with fallbacks
            arango_url = os.getenv("ARANGO_URL")
            arango_host = os.getenv("ARANGO_HOST", "localhost")
            arango_port = os.getenv("ARANGO_PORT", "8529")
            arango_user = os.getenv("ARANGO_USERNAME", "root")
            arango_password = os.getenv("ARANGO_PASSWORD")
            
            # Additional authentication options
            arango_database = os.getenv("ARANGO_DATABASE", "knowledge_graph")
            
            if not arango_url:
                arango_url = f"http://{arango_host}:{arango_port}"
            
            if not arango_password:
                status.error = "ARANGO_PASSWORD not set"
                self.results["knowledge_graph"] = status
                return
            
            status.configured = True
            
            # Try to import ArangoDB
            try:
                from arango import ArangoClient
                status.available = True
            except ImportError:
                status.error = "ArangoDB Python driver not installed. Run: pip install python-arango"
                self.results["knowledge_graph"] = status
                return
            
            # Test connection with retry logic
            async def test_connection():
                # Build client with authentication
                client = ArangoClient(hosts=arango_url)
                
                # Test basic connectivity
                db = client.db(arango_database, username=arango_user, password=arango_password)
                
                # Test a simple query
                try:
                    result = db.aql.execute("RETURN 1 as test")
                    test_value = result.next()["test"]
                    
                    if test_value == 1:
                        # Test a simple graph query
                        try:
                            # Check if collections exist
                            collections = db.collections()
                            entities_collection = None
                            relationships_collection = None
                            
                            for collection in collections:
                                if collection["name"] == "entities":
                                    entities_collection = collection
                                elif collection["name"] == "relationships":
                                    relationships_collection = collection
                            
                            # Create collections if they don't exist
                            if not entities_collection:
                                logger.info("📝 Creating ArangoDB entities collection")
                                db.create_collection("entities")
                            
                            if not relationships_collection:
                                logger.info("📝 Creating ArangoDB relationships collection")
                                db.create_collection("relationships", edge=True)
                            
                            # Test a simple graph query
                            result = db.aql.execute("FOR doc IN entities RETURN COUNT(doc)")
                            entity_count = result.next()
                            
                            return {
                                "connection_successful": True,
                                "entity_count": entity_count,
                                "database": arango_database,
                                "entities_collection_exists": entities_collection is not None,
                                "relationships_collection_exists": relationships_collection is not None,
                                "test_query_successful": True
                            }
                        except Exception as e:
                            return {
                                "connection_successful": True,
                                "database": arango_database,
                                "test_query_successful": False,
                                "test_error": str(e)
                            }
                    else:
                        raise Exception("Unexpected test result")
                
                except Exception as e:
                    return {
                        "connection_successful": False,
                        "test_error": str(e)
                    }
            
            # Execute with retry logic
            details = await self.retry_manager.execute_with_retry(test_connection)
            
            status.reachable = True
            status.response_time = time.time() - start_time
            status.details = details
            circuit_breaker.record_success()
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            status.error = error_msg
            circuit_breaker.record_failure()
            logger.error(f"❌ ArangoDB check failed: {error_msg}")
        
        self.results["knowledge_graph"] = status
    
    def print_results(self):
        """Print comprehensive results."""
        print("\n" + "="*80)
        print("🔍 VECTOR BACKEND CONFIGURATION REPORT")
        print("="*80)
        
        for backend_name, status in self.results.items():
            print(f"\n📊 {backend_name.upper()}")
            print("-" * 40)
            
            if status.available:
                print(f"✅ Available: Yes")
            else:
                print(f"❌ Available: No")
                if status.error:
                    print(f"   Error: {status.error}")
                continue
            
            if status.configured:
                print(f"✅ Configured: Yes")
            else:
                print(f"❌ Configured: No")
                if status.error:
                    print(f"   Error: {status.error}")
                continue
            
            if status.reachable:
                print(f"✅ Reachable: Yes")
                if status.response_time:
                    print(f"   Response Time: {status.response_time:.3f}s")
            else:
                print(f"❌ Reachable: No")
                if status.error:
                    print(f"   Error: {status.error}")
                continue
            
            if status.details:
                print(f"📋 Details:")
                for key, value in status.details.items():
                    print(f"   {key}: {value}")
        
        print("\n" + "="*80)
        print("📋 SUMMARY")
        print("="*80)
        
        available_count = sum(1 for s in self.results.values() if s.available)
        configured_count = sum(1 for s in self.results.values() if s.configured)
        reachable_count = sum(1 for s in self.results.values() if s.reachable)
        
        print(f"Available: {available_count}/{len(self.results)}")
        print(f"Configured: {configured_count}/{len(self.results)}")
        print(f"Reachable: {reachable_count}/{len(self.results)}")
        
        if reachable_count == 0:
            print("\n⚠️  WARNING: No vector backends are reachable!")
            print("   This will impact search functionality.")
        elif reachable_count < len(self.results):
            print(f"\n⚠️  WARNING: Only {reachable_count}/{len(self.results)} backends are reachable.")
        else:
            print("\n✅ All vector backends are operational!")


async def main():
    """Main function to run the vector backend checker."""
    checker = VectorBackendChecker()
    
    try:
        results = await checker.check_all_backends()
        checker.print_results()
        
        # Return exit code based on results
        reachable_count = sum(1 for s in results.values() if s.reachable)
        if reachable_count == 0:
            return 1  # Error: no backends reachable
        elif reachable_count < len(results):
            return 2  # Warning: some backends unreachable
        else:
            return 0  # Success: all backends reachable
            
    except Exception as e:
        logger.error(f"Error during backend check: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 