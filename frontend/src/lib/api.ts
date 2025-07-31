import axios, { AxiosInstance } from "axios";
import { QueryDetailResponse, QuerySummary } from "@/types/api";

// API Configuration
const API_BASE_URL = process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8002";

// Types for API responses
export interface QueryRequest {
  query: string;
  context?: string;
  user_id?: string;
  workspace_id?: string;
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
}

export interface Source {
  title: string;
  url: string;
  snippet: string;
  relevance_score: number;
}

export interface FeedbackRequest {
  query_id: string;
  rating: number;
  feedback_text?: string;
  helpful: boolean;
}

export interface User {
  user_id: string;
  username: string;
  role: string;
  permissions: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  api_key: string;
  user_id: string;
  role: string;
  permissions: string[];
}

// API Client Class
class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
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

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error("API Error:", error.response?.data || error.message);
        return Promise.reject(error);
      },
    );
  }

  // Authentication methods
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post("/auth/login", {
      username,
      password,
    });
    const authData = response.data;
    this.token = authData.access_token;
    localStorage.setItem("auth_token", authData.access_token);
    return authData;
  }

  async register(
    username: string,
    password: string,
    role: string = "user",
  ): Promise<AuthResponse> {
    const response = await this.client.post("/auth/register", {
      username,
      password,
      role,
    });
    const authData = response.data;
    this.token = authData.access_token;
    localStorage.setItem("auth_token", authData.access_token);
    return authData;
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem("auth_token");
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  // Query methods
  async submitQuery(request: QueryRequest): Promise<QueryResponse> {
    const response = await this.client.post("/query", request);
    return response.data;
  }

  async getQueryStatus(queryId: string): Promise<QueryResponse> {
    const response = await this.client.get(`/queries/${queryId}/status`);
    return response.data;
  }

  async getQueryDetails(queryId: string): Promise<QueryResponse> {
    const response = await this.client.get(`/queries/${queryId}`);
    return response.data;
  }

  async getQuery(queryId: string): Promise<QueryDetailResponse> {
    const response = await this.client.get(`/queries/${queryId}`);
    return response.data;
  }

  async updateQuery(queryId: string, data: any): Promise<QueryDetailResponse> {
    const response = await this.client.put(`/queries/${queryId}`, data);
    return response.data;
  }

  async deleteQuery(queryId: string): Promise<void> {
    await this.client.delete(`/queries/${queryId}`);
  }

  async reprocessQuery(queryId: string): Promise<void> {
    await this.client.patch(`/queries/${queryId}/reprocess`);
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
