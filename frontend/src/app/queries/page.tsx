"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { api } from "@/services/api";
import type {
  QueryListResponse,
  QueryDetailResponse,
  QuerySummary,
  QueryUpdateRequest,
  QueryListFilters,
} from "@/types/api";

export default function QueriesPage() {
  const [queries, setQueries] = useState<QueryListResponse | null>(null);
  const [selectedQuery, setSelectedQuery] =
    useState<QueryDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editData, setEditData] = useState<QueryUpdateRequest>({});
  const [filters, setFilters] = useState<QueryListFilters>({
    page: 1,
    page_size: 10,
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const loadQueries = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await api.listQueries(filters.page || 1, filters.page_size || 10);
      setQueries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load queries");
    } finally {
      setIsLoading(false);
    }
  }, [filters.page, filters.page_size]);

  // Load queries on component mount and when filters change
  useEffect(() => {
    loadQueries();
  }, [loadQueries, refreshTrigger]);

  const loadQueryDetails = async (queryId: string) => {
    try {
      const data = await api.getQuery(queryId);
      setSelectedQuery(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load query details",
      );
    }
  };

  const handleUpdateQuery = async () => {
    if (!selectedQuery) return;

    try {
      const updatedQuery = await api.updateQuery(
        selectedQuery.query_id,
        editData,
      );
      setSelectedQuery(updatedQuery);
      setShowEditModal(false);
      setEditData({});
      setRefreshTrigger((prev) => prev + 1); // Refresh the list
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update query");
    }
  };

  const handleDeleteQuery = async (queryId: string) => {
    if (!confirm("Are you sure you want to delete this query?")) return;

    try {
      await api.deleteQuery(queryId);
      setRefreshTrigger((prev) => prev + 1); // Refresh the list
      if (selectedQuery?.query_id === queryId) {
        setSelectedQuery(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete query");
    }
  };

  const handleReprocessQuery = async (queryId: string) => {
    try {
      await api.reprocessQuery(queryId);
      // Reload query details to show updated results
      if (selectedQuery?.query_id === queryId) {
        await loadQueryDetails(queryId);
      }
      setRefreshTrigger((prev) => prev + 1); // Refresh the list
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to reprocess query",
      );
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-cosmic-success bg-cosmic-success/10";
      case "processing":
        return "text-cosmic-warning bg-cosmic-warning/10";
      case "failed":
        return "text-cosmic-error bg-cosmic-error/10";
      default:
        return "cosmic-text-tertiary bg-cosmic-bg-secondary";
    }
  };

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container cosmic-section">
        {/* Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-4">
            <Link
              href="/"
              className="cosmic-btn-secondary"
            >
              New Query
            </Link>
            <Link
              href="/queries"
              className="cosmic-btn-primary"
            >
              Manage Queries
            </Link>
            <Link
              href="/dashboard"
              className="cosmic-btn-secondary"
            >
              Dashboard
            </Link>
          </nav>
        </div>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold cosmic-text-primary mb-2">
          Query Management
        </h1>
        <p className="cosmic-text-secondary">
          Manage and review your knowledge queries with full CRUD operations
        </p>
      </div>

      {/* Filters */}
      <div className="cosmic-card p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium cosmic-text-primary mb-1">
              Status Filter
            </label>
            <select
              value={filters.status_filter || ""}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  status_filter: e.target.value as
                    | "completed"
                    | "processing"
                    | "failed"
                    | undefined,
                  page: 1,
                })
              }
              className="cosmic-input"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium cosmic-text-primary mb-1">
              Page Size
            </label>
            <select
              value={filters.page_size}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  page_size: parseInt(e.target.value),
                  page: 1,
                })
              }
              className="cosmic-input"
            >
              <option value={5}>5 per page</option>
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              <option value={50}>50 per page</option>
            </select>
          </div>

          <button
            onClick={() => setRefreshTrigger((prev) => prev + 1)}
            disabled={isLoading}
            className="cosmic-btn-primary disabled:opacity-50"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="cosmic-card border-cosmic-error bg-cosmic-error/5 p-4 mb-6">
          <div className="text-cosmic-error">
            {error}
            <button
              onClick={() => setError(null)}
              className="float-right text-cosmic-error hover:text-cosmic-error/80"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Queries List */}
        <div className="cosmic-card">
          <div className="p-4 border-b border-cosmic-border-primary">
            <h2 className="text-xl font-semibold cosmic-text-primary">Your Queries</h2>
            {queries && (
              <p className="text-sm cosmic-text-tertiary">
                Showing {queries.queries.length} of {queries.total} queries
              </p>
            )}
          </div>

          <div className="divide-y">
            {isLoading ? (
              <div className="p-4 text-center cosmic-text-tertiary">
                Loading queries...
              </div>
            ) : queries?.queries.length === 0 ? (
              <div className="p-4 text-center cosmic-text-tertiary">
                No queries found
              </div>
            ) : (
              queries?.queries.map((query: QuerySummary) => (
                <div
                  key={query.query_id}
                  className={`p-4 cursor-pointer cosmic-hover-lift ${
                    selectedQuery?.query_id === query.query_id
                      ? "bg-cosmic-primary-500/10 border-l-4 border-cosmic-primary-500"
                      : ""
                  }`}
                  onClick={() => loadQueryDetails(query.query_id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium cosmic-text-primary truncate flex-1 mr-2">
                      {query.query.length > 80
                        ? `${query.query.substring(0, 80)}...`
                        : query.query}
                    </h3>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${getStatusColor(query.status)}`}
                    >
                      {query.status}
                    </span>
                  </div>

                  <div className="text-sm cosmic-text-tertiary space-y-1">
                    <div>
                      Confidence: {(query.confidence * 100).toFixed(1)}%
                    </div>
                    <div>Created: {formatDate(query.created_at)}</div>
                    <div>
                      Processing: {(query.processing_time * 1000).toFixed(0)}ms
                    </div>
                  </div>

                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReprocessQuery(query.query_id);
                      }}
                      className="text-xs px-2 py-1 bg-cosmic-warning/10 text-cosmic-warning rounded hover:bg-cosmic-warning/20"
                    >
                      Reprocess
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteQuery(query.query_id);
                      }}
                      className="text-xs px-2 py-1 bg-cosmic-error/10 text-cosmic-error rounded hover:bg-cosmic-error/20"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          {queries && queries.total > 0 && (
            <div className="p-4 border-t flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Page {queries.page} of{" "}
                {Math.ceil(queries.total / queries.page_size)}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() =>
                    setFilters({
                      ...filters,
                      page: Math.max(1, (filters.page || 1) - 1),
                    })
                  }
                  disabled={(filters.page || 1) <= 1}
                  className="px-3 py-1 border rounded disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() =>
                    setFilters({ ...filters, page: (filters.page || 1) + 1 })
                  }
                  disabled={!queries.has_next}
                  className="px-3 py-1 border rounded disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Query Details */}
        <div className="cosmic-card">
          <div className="p-4 border-b border-cosmic-border-primary flex justify-between items-center">
            <h2 className="text-xl font-semibold cosmic-text-primary">Query Details</h2>
            {selectedQuery && (
              <button
                onClick={() => {
                  setEditData({
                    query: selectedQuery.query,
                    max_tokens: 1000,
                    confidence_threshold: 0.8,
                    reprocess: false,
                  });
                  setShowEditModal(true);
                }}
                className="cosmic-btn-primary text-sm px-3 py-1"
              >
                Edit Query
              </button>
            )}
          </div>

          {selectedQuery ? (
            <div className="p-4 space-y-4">
              <div>
                <h3 className="font-medium cosmic-text-primary mb-2">Query</h3>
                <p className="cosmic-text-primary bg-cosmic-bg-secondary p-3 rounded">
                  {selectedQuery.query}
                </p>
              </div>

              <div>
                <h3 className="font-medium cosmic-text-primary mb-2">Answer</h3>
                <div className="cosmic-text-primary bg-cosmic-bg-secondary p-3 rounded">
                  {selectedQuery.answer || (
                    <em className="cosmic-text-tertiary">No answer generated</em>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium cosmic-text-primary">Status</h4>
                  <span
                    className={`inline-block px-2 py-1 text-sm rounded ${getStatusColor(selectedQuery.status)}`}
                  >
                    {selectedQuery.status}
                  </span>
                </div>
                <div>
                  <h4 className="font-medium cosmic-text-primary">Confidence</h4>
                  <p className="cosmic-text-primary">
                    {(selectedQuery.confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium cosmic-text-primary">Created</h4>
                  <p className="cosmic-text-primary">
                    {formatDate(selectedQuery.created_at)}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium cosmic-text-primary">Processing Time</h4>
                  <p className="cosmic-text-primary">
                    {(selectedQuery.processing_time * 1000).toFixed(0)}ms
                  </p>
                </div>
              </div>

              {selectedQuery.updated_at && (
                <div>
                  <h4 className="font-medium cosmic-text-primary">Last Updated</h4>
                  <p className="cosmic-text-primary">
                    {formatDate(selectedQuery.updated_at)}
                  </p>
                </div>
              )}

              {selectedQuery.citations.length > 0 && (
                <div>
                  <h4 className="font-medium cosmic-text-primary mb-2">Citations</h4>
                  <div className="space-y-2">
                    {selectedQuery.citations.map((citation, index) => (
                      <div
                        key={index}
                        className="bg-cosmic-bg-secondary p-2 rounded text-sm"
                      >
                        <p className="cosmic-text-primary">{citation.text}</p>
                        {citation.url && (
                          <a
                            href={citation.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cosmic-primary-500 hover:underline"
                          >
                            {citation.url}
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 text-center cosmic-text-tertiary">
              Select a query to view details
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && selectedQuery && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="cosmic-card max-w-md w-full p-6">
            <h3 className="text-lg font-semibold cosmic-text-primary mb-4">Edit Query</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium cosmic-text-primary mb-1">
                  Query Text
                </label>
                <textarea
                  value={editData.query || selectedQuery.query}
                  onChange={(e) =>
                    setEditData({ ...editData, query: e.target.value })
                  }
                  className="w-full cosmic-input h-24 resize-none"
                  placeholder="Enter your query..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium cosmic-text-primary mb-1">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={editData.max_tokens || 1000}
                  onChange={(e) =>
                    setEditData({
                      ...editData,
                      max_tokens: parseInt(e.target.value),
                    })
                  }
                  className="w-full cosmic-input"
                  min="100"
                  max="4000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium cosmic-text-primary mb-1">
                  Confidence Threshold
                </label>
                <input
                  type="number"
                  value={editData.confidence_threshold || 0.8}
                  onChange={(e) =>
                    setEditData({
                      ...editData,
                      confidence_threshold: parseFloat(e.target.value),
                    })
                  }
                  className="w-full cosmic-input"
                  min="0"
                  max="1"
                  step="0.1"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="reprocess"
                  checked={editData.reprocess || false}
                  onChange={(e) =>
                    setEditData({ ...editData, reprocess: e.target.checked })
                  }
                  className="mr-2"
                />
                <label htmlFor="reprocess" className="text-sm cosmic-text-secondary">
                  Reprocess query after update
                </label>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleUpdateQuery}
                className="flex-1 cosmic-btn-primary"
              >
                Update Query
              </button>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditData({});
                }}
                className="flex-1 cosmic-btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
