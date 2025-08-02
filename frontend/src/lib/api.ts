import axios, { AxiosInstance, AxiosError, AxiosResponse } from "axios";
import { QueryDetailResponse, QuerySummary } from "@/types/api";

// API Configuration
const API_BASE_URL = process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8000";

// Enhanced error types
export interface APIError {
  message: string;
  code: string;
  details?: any;
  timestamp: string;
}

export interface APIResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  timestamp: string;
}

// Request/Response types
export interface QueryRequest {
  query: string;
  context?: string;
  user_id?: string;
  workspace_id?: string;
  priority?: "low" | "medium" | "high";
  max_tokens?: number;
  temperature?: number;
}

export interface QueryResponse {
  query_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  answer?: string;
  sources?: Source[];
  confidence?: number;
  created_at: string;
  updated_at: string;
  llm_provider?: string;
  llm_model?: string;
  processing_time?: number;
  error?: string;
  progress?: number;
}

export interface Source {
  title: string;
  url: string;
  snippet: string;
  relevance_score: number;
  source_type: "web" | "document" | "database" | "api";
  credibility_score?: number;
}

export interface FeedbackRequest {
  query_id: string;
  rating: number;
  feedback_text?: string;
  helpful: boolean;
  category?: string;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  api_key: string;
  user_id: string;
  role: string;
  permissions: string[];
  expires_in: number;
  refresh_token?: string;
}

// Circuit Breaker Implementation
class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";
  private readonly failureThreshold = 5;
  private readonly resetTimeout = 60000; // 1 minute

  canExecute(): boolean {
    if (this.state === "CLOSED") return true;
    
    if (this.state === "OPEN") {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = "HALF_OPEN";
        return true;
      }
      return false;
    }
    
    return true; // HALF_OPEN
  }

  recordSuccess(): void {
    this.failures = 0;
    this.state = "CLOSED";
  }

  recordFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    
    if (this.failures >= this.failureThreshold) {
      this.state = "OPEN";
    }
  }
}

// Retry Logic Implementation
class RetryManager {
  private readonly maxRetries = 3;
  private readonly baseDelay = 1000;

  async executeWithRetry<T>(
    operation: () => Promise<T>,
    retries = this.maxRetries
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (retries > 0 && this.isRetryableError(error)) {
        const delay = this.baseDelay * (this.maxRetries - retries + 1);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.executeWithRetry(operation, retries - 1);
      }
      throw error;
    }
  }

  private isRetryableError(error: any): boolean {
    if (error instanceof AxiosError) {
      const status = error.response?.status;
      return status === 429 || status === 500 || status === 502 || status === 503 || status === 504;
    }
    return false;
  }
}

// Enhanced API Client Class
class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;
  private circuitBreaker: CircuitBreaker;
  private retryManager: RetryManager;
  private requestQueue: Array<() => Promise<any>> = [];
  private isProcessingQueue = false;

  constructor() {
    this.circuitBreaker = new CircuitBreaker();
    this.retryManager = new RetryManager();
    
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );

    // Add response interceptor for enhanced error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        this.circuitBreaker.recordSuccess();
        return response;
      },
      (error: AxiosError) => {
        this.circuitBreaker.recordFailure();
        
        // Enhanced error logging
        const errorInfo = {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: error.config?.url,
          method: error.config?.method,
          timestamp: new Date().toISOString(),
        };
        
        console.error("API Error:", errorInfo);
        
        // Transform error for better handling
        const apiError: APIError = {
          message: (error.response?.data as any)?.detail || error.message,
          code: error.response?.status?.toString() || "UNKNOWN",
          details: error.response?.data,
          timestamp: new Date().toISOString(),
        };
        
        return Promise.reject(apiError);
      },
    );
  }

  // Enhanced API methods with circuit breaker and retry logic
  private async executeRequest<T>(
    operation: () => Promise<AxiosResponse<T>>
  ): Promise<T> {
    if (!this.circuitBreaker.canExecute()) {
      throw new Error("Service temporarily unavailable. Please try again later.");
    }

    return this.retryManager.executeWithRetry(async () => {
      const response = await operation();
      return response.data;
    });
  }

  // Authentication methods
  async login(username: string, password: string): Promise<AuthResponse> {
    const authData = await this.executeRequest(() =>
      this.client.post("/auth/login", {
        username,
        password,
      })
    );
    this.token = authData.access_token;
    localStorage.setItem("auth_token", authData.access_token);
    return authData;
  }

  async register(
    username: string,
    password: string,
    role: string = "user",
  ): Promise<AuthResponse> {
    const authData = await this.executeRequest(() =>
      this.client.post("/auth/register", {
        username,
        password,
        role,
      })
    );
    this.token = authData.access_token;
    localStorage.setItem("auth_token", authData.access_token);
    return authData;
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem("auth_token");
    sessionStorage.removeItem("auth_token");
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  // Query methods
  async submitQuery(request: QueryRequest): Promise<QueryResponse> {
    return this.executeRequest(() =>
      this.client.post("/query/comprehensive", request)
    );
  }

  async getQueryStatus(queryId: string): Promise<QueryResponse> {
    return this.executeRequest(() =>
      this.client.get(`/queries/${queryId}/status`)
    );
  }

  async getQueryDetails(queryId: string): Promise<QueryResponse> {
    return this.executeRequest(() =>
      this.client.get(`/queries/${queryId}`)
    );
  }

  async getQuery(queryId: string): Promise<QueryDetailResponse> {
    return this.executeRequest(() =>
      this.client.get(`/queries/${queryId}`)
    );
  }

  async updateQuery(queryId: string, data: any): Promise<QueryDetailResponse> {
    return this.executeRequest(() =>
      this.client.put(`/queries/${queryId}`, data)
    );
  }

  async deleteQuery(queryId: string): Promise<void> {
    return this.executeRequest(() =>
      this.client.delete(`/queries/${queryId}`)
    );
  }

  async reprocessQuery(queryId: string): Promise<void> {
    return this.executeRequest(() =>
      this.client.patch(`/queries/${queryId}/reprocess`)
    );
  }

  async listQueries(
    page: number = 1,
    pageSize: number = 20,
  ): Promise<{
    queries: QuerySummary[];
    total: number;
    page: number;
    page_size: number;
    has_next: boolean;
    has_prev: boolean;
  }> {
    const response = await this.client.get("/queries", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  // Feedback methods
  async submitFeedback(feedback: FeedbackRequest): Promise<void> {
    await this.client.post("/feedback", feedback);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }

  // Analytics
  async getAnalytics(): Promise<any> {
    const response = await this.client.get("/analytics");
    return response.data;
  }

  // Metrics
  async getMetrics(): Promise<any> {
    const response = await this.client.get("/metrics");
    return response.data;
  }

  async getIntegrationStatus(): Promise<any> {
    const response = await this.client.get("/integrations");
    return response.data;
  }

  async getApiInfo(): Promise<any> {
    const response = await this.client.get("/");
    return response.data;
  }

  // Expert reviews
  async getPendingReviews(): Promise<any[]> {
    const response = await this.client.get("/expert-reviews/pending");
    return response.data;
  }

  async submitExpertReview(reviewId: string, review: any): Promise<any> {
    const response = await this.client.post(
      `/expert-reviews/${reviewId}`,
      review,
    );
    return response.data;
  }

  // Task generation methods
  async generateTasks(
    answer?: string,
    query?: string,
  ): Promise<{
    tasks: Array<{
      task: string;
      priority: string;
      status: string;
    }>;
    total_tasks: number;
    generated_at: string;
    request_id: string;
  }> {
    const response = await this.client.post("/tasks", {
      answer,
      query,
    });
    return response.data;
  }

  // Session state methods
  async getSessionState(sessionId: string): Promise<any> {
    const response = await this.client.get(`/api/state/${sessionId}`);
    return response.data;
  }

  async updateSessionState(sessionId: string, state: any): Promise<any> {
    const response = await this.client.put(`/api/state/${sessionId}`, state);
    return response.data;
  }

  // Knowledge graph methods
  async queryKnowledgeGraph(params: {
    query: string;
    query_type?: string;
    max_entities?: number;
    max_relationships?: number;
  }): Promise<any> {
    const response = await this.client.post("/knowledge-graph/query", params);
    return response.data;
  }

  // WebSocket methods (for future implementation)
  async getWebSocketUrl(): Promise<string> {
    const response = await this.client.get("/ws/url");
    return response.data.url;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }
}

// Create and export API instance
export const api = new APIClient();
