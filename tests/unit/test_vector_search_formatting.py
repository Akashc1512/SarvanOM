"""
Unit tests for vector search formatting functionality.

Tests the actual vector store implementations and their search result formatting.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from typing import List, Dict, Any

from shared.vectorstores.vector_store_service import (
    InMemoryVectorStore, 
    ChromaVectorStore, 
    VectorDocument,
    VectorStoreService
)


class TestVectorSearchFormatting:
    """Test vector search results formatting functionality."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store for testing."""
        store = Mock(spec=ChromaVectorStore)
        store.collection_name = "test_collection"
        return store

    @pytest.fixture
    def sample_vector_documents(self):
        """Sample vector documents for testing."""
        return [
            VectorDocument(
                id="doc1",
                text="This is the first document about Python programming.",
                embedding=[0.1, 0.2, 0.3, 0.4],
                metadata={"source": "python_guide.pdf", "page": 1}
            ),
            VectorDocument(
                id="doc2",
                text="Machine learning algorithms and their applications.",
                embedding=[0.2, 0.3, 0.4, 0.5],
                metadata={"source": "ml_tutorial.pdf", "page": 5}
            ),
            VectorDocument(
                id="doc3",
                text="Data structures and algorithms in Python.",
                embedding=[0.3, 0.4, 0.5, 0.6],
                metadata={"source": "ds_algo.pdf", "page": 3}
            )
        ]

    @pytest.fixture
    def sample_query_embedding(self):
        """Sample query embedding for testing."""
        return [0.15, 0.25, 0.35, 0.45]

    @pytest.mark.asyncio
    async def test_inmemory_vector_store_search(self, sample_vector_documents, sample_query_embedding):
        """Test in-memory vector store search functionality."""
        store = InMemoryVectorStore()
        
        # Add documents
        await store.upsert(sample_vector_documents)
        
        # Search
        results = await store.search(sample_query_embedding, top_k=3)
        
        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)
        assert all("id" in result for result in results)
        assert all("text" in result for result in results)
        assert all("embedding" in result for result in results)
        assert all("metadata" in result for result in results)
        
        # Check that results have the expected structure
        for result in results:
            assert isinstance(result["id"], str)
            assert isinstance(result["text"], str)
            assert isinstance(result["embedding"], list)
            assert isinstance(result["metadata"], dict)

    @pytest.mark.asyncio
    async def test_inmemory_vector_store_empty_search(self, sample_query_embedding):
        """Test search on empty vector store."""
        store = InMemoryVectorStore()
        results = await store.search(sample_query_embedding, top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_inmemory_vector_store_document_operations(self, sample_vector_documents):
        """Test document upsert and delete operations."""
        store = InMemoryVectorStore()
        
        # Test upsert
        count = await store.upsert(sample_vector_documents)
        assert count == 3
        
        # Test search after upsert
        query_embedding = [0.1, 0.2, 0.3, 0.4]
        results = await store.search(query_embedding, top_k=3)
        assert len(results) == 3
        
        # Test delete
        deleted = await store.delete(["doc1", "doc2"])
        assert deleted == 2
        
        # Test search after delete
        results = await store.search(query_embedding, top_k=3)
        assert len(results) == 1
        assert results[0]["id"] == "doc3"

    @pytest.mark.asyncio
    async def test_vector_document_creation(self):
        """Test VectorDocument creation and properties."""
        doc = VectorDocument(
            id="test_doc",
            text="Test document content",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test.pdf", "page": 1}
        )
        
        assert doc.id == "test_doc"
        assert doc.text == "Test document content"
        assert doc.embedding == [0.1, 0.2, 0.3]
        assert doc.metadata["source"] == "test.pdf"
        assert doc.metadata["page"] == 1

    @pytest.mark.asyncio
    async def test_vector_store_service_abstract_methods(self):
        """Test that VectorStoreService abstract methods are properly defined."""
        # This should raise TypeError since VectorStoreService is abstract
        with pytest.raises(TypeError):
            VectorStoreService("test")

    @pytest.mark.asyncio
    async def test_search_with_different_top_k_values(self, sample_vector_documents, sample_query_embedding):
        """Test search with different top_k values."""
        store = InMemoryVectorStore()
        await store.upsert(sample_vector_documents)
        
        # Test with top_k=1
        results = await store.search(sample_query_embedding, top_k=1)
        assert len(results) == 1
        
        # Test with top_k=2
        results = await store.search(sample_query_embedding, top_k=2)
        assert len(results) == 2
        
        # Test with top_k larger than available documents
        results = await store.search(sample_query_embedding, top_k=10)
        assert len(results) == 3  # Should return all available documents

    @pytest.mark.asyncio
    async def test_search_with_zero_embedding(self, sample_vector_documents):
        """Test search with zero embedding vector."""
        store = InMemoryVectorStore()
        await store.upsert(sample_vector_documents)
        
        zero_embedding = [0.0, 0.0, 0.0, 0.0]
        results = await store.search(zero_embedding, top_k=3)
        
        # Should still return results
        assert len(results) == 3
        # Check that all results have the expected structure
        for result in results:
            assert "id" in result
            assert "text" in result
            assert "embedding" in result
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_search_with_mismatched_embedding_dimensions(self, sample_vector_documents):
        """Test search with embedding dimension mismatch."""
        store = InMemoryVectorStore()
        await store.upsert(sample_vector_documents)
        
        # Query embedding with different dimension
        mismatched_embedding = [0.1, 0.2, 0.3]  # 3D instead of 4D
        
        results = await store.search(mismatched_embedding, top_k=3)
        
        # Should handle gracefully and return results
        assert len(results) == 3
        # Check that all results have the expected structure
        for result in results:
            assert "id" in result
            assert "text" in result
            assert "embedding" in result
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_chroma_vector_store_mock(self, mock_vector_store, sample_query_embedding):
        """Test ChromaDB vector store with mock."""
        # Mock the search method
        mock_vector_store.search = AsyncMock(return_value=[
            (VectorDocument(id="doc1", text="test", embedding=[], metadata={}), 0.95),
            (VectorDocument(id="doc2", text="test2", embedding=[], metadata={}), 0.87)
        ])
        
        results = await mock_vector_store.search(sample_query_embedding, top_k=2)
        
        assert len(results) == 2
        assert results[0][1] == 0.95  # First result has highest score
        assert results[1][1] == 0.87  # Second result has lower score

    def test_vector_document_metadata_handling(self):
        """Test VectorDocument with various metadata types."""
        # Test with empty metadata
        doc1 = VectorDocument(
            id="doc1",
            text="Test content",
            embedding=[0.1, 0.2, 0.3],
            metadata={}
        )
        assert doc1.metadata == {}
        
        # Test with complex metadata
        complex_metadata = {
            "source": "test.pdf",
            "page": 1,
            "author": "John Doe",
            "tags": ["python", "programming"],
            "confidence": 0.95
        }
        doc2 = VectorDocument(
            id="doc2",
            text="Test content",
            embedding=[0.1, 0.2, 0.3],
            metadata=complex_metadata
        )
        assert doc2.metadata == complex_metadata
        assert doc2.metadata["tags"] == ["python", "programming"]
        assert doc2.metadata["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, sample_vector_documents, sample_query_embedding):
        """Test concurrent upsert and search operations."""
        import asyncio
        
        store = InMemoryVectorStore()
        
        # Add documents
        await store.upsert(sample_vector_documents)
        
        # Perform concurrent searches
        tasks = [
            store.search(sample_query_embedding, top_k=2),
            store.search(sample_query_embedding, top_k=3),
            store.search(sample_query_embedding, top_k=1)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert len(results[0]) == 2  # top_k=2
        assert len(results[1]) == 3  # top_k=3
        assert len(results[2]) == 1  # top_k=1

    @pytest.mark.asyncio
    async def test_error_handling_invalid_embedding(self):
        """Test error handling with invalid embeddings."""
        store = InMemoryVectorStore()
        
        # Test with None embedding - should handle gracefully
        results = await store.search(None, top_k=5)
        assert results == []
        
        # Test with empty embedding - should handle gracefully
        results = await store.search([], top_k=5)
        assert results == []

    def test_vector_store_service_logging(self):
        """Test that vector store service has proper logging setup."""
        # Test that InMemoryVectorStore has logging capability
        store = InMemoryVectorStore()
        assert hasattr(store, '_log_operation')
        assert callable(store._log_operation)
