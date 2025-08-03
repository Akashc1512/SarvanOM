// API Types for Universal Knowledge Platform

export interface Citation {
  id: string;
  text: string;
  url?: string;
  title?: string;
  author?: string;
  date?: string;
}

export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  citations: Citation[];
  query_id?: string;
  processing_time?: number;
  query_type?: "cached" | "fresh" | "reprocessed";
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface FeedbackRequest {
  query_id: string;
  feedback_type: "helpful" | "not-helpful";
  details?: string;
}

export interface AnalyticsData {
  total_requests: number;
  total_errors: number;
  average_response_time: number;
  cache_hit_rate: number;
  popular_queries: Record<string, number>;
  timestamp: string;
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_confidence: number;
}

export interface User {
  id: string;
  email: string;
  role: "user" | "expert" | "admin";
  created_at: string;
}

export interface ExpertValidationTask {
  id: string;
  query: string;
  answer: string;
  confidence: number;
  citations: Citation[];
  status: "pending" | "approved" | "rejected" | "corrected";
  submitted_at: string;
  reviewed_at?: string;
  reviewer_id?: string;
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_throughput: number;
  active_connections: number;
  timestamp: string;
  sarvanom_requests_total: number;
  sarvanom_requests_duration_seconds: number;
  sarvanom_requests_duration_seconds_count: number;
  sarvanom_requests_duration_seconds_sum: number;
  sarvanom_requests_duration_seconds_bucket: Record<string, number>;
  sarvanom_errors_total: number;
  sarvanom_cache_hits_total: number;
  sarvanom_cache_misses_total: number;
  sarvanom_average_response_time_seconds: number;
  sarvanom_active_users: number;
  sarvanom_active_sessions: number;
  sarvanom_active_connections: number;
  sarvanom_active_requests: number;
  sarvanom_active_errors: number;
  sarvanom_active_cache_hits: number;
  sarvanom_active_cache_misses: number;
  sarvanom_active_cache_hits_rate: number;
  sarvanom_active_cache_misses_rate: number;
}

export interface IntegrationStatus {
  name: string;
  status: "healthy" | "unhealthy" | "not_configured";
  response_time?: number;
  last_check: string;
  details?: string;
  summary: {
    healthy: number;
    unhealthy: number;
    not_configured: number;
  };
  integrations: Record<string, {
    status: string;
    response_time?: number;
    last_check: string;
    details?: string;
  }>;
}

export interface ErrorResponse {
  error: string;
  status_code: number;
  details?: string;
}

export interface ApiInfo {
  name: string;
  version: string;
  uptime: number;
  environment: string;
  features: string[];
  status: string;
}

export interface QueryUpdateRequest {
  query?: string;
  max_tokens?: number;
  confidence_threshold?: number;
  user_context?: Record<string, any>;
  reprocess?: boolean;
}

export interface QuerySummary {
  query_id: string;
  query: string;
  status: string;
  confidence: number;
  created_at: string;
  processing_time: number;
}

export interface QueryListResponse {
  queries: any[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface QueryDetailResponse {
  query_id: string;
  query: string;
  answer: string;
  confidence: number;
  citations: Citation[];
  processing_time: number;
  created_at: string;
  updated_at: string;
  user_id?: string;
  status: string;
  metadata?: Record<string, any>;
}

export interface QueryListFilters {
  user_filter?: string | undefined;
  status_filter?: string | undefined;
  date_from?: string | undefined;
  date_to?: string | undefined;
  page?: number | undefined;
  page_size?: number | undefined;
}

// Wiki Types
export interface WikiArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  author?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
  read_count?: number;
}

export interface WikiArticleList {
  articles: WikiArticle[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface CreateWikiArticleRequest {
  title: string;
  content: string;
  summary?: string;
  tags?: string[];
}

export interface UpdateWikiArticleRequest {
  title?: string;
  content?: string;
  summary?: string;
  tags?: string[];
}

export interface WikiArticleResponse {
  article: WikiArticle;
  message?: string;
}

export interface WikiErrorResponse {
  error: string;
  status_code: number;
  details?: string;
}
