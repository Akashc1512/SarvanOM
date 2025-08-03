import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API Client Configuration
class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env['NEXT_PUBLIC_API_BASE_URL'] || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private handleUnauthorized(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
  }

  // Generic request methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.get('/health');
  }

  // Query endpoints
  async submitQuery(query: string, options?: any): Promise<any> {
    return this.post('/api/query', { query, ...options });
  }

  async getQueryHistory(): Promise<any[]> {
    return this.get('/api/queries');
  }

  // Authentication endpoints
  async login(credentials: { username: string; password: string }): Promise<{ token: string; user: any }> {
    const response = await this.post('/api/auth/login', credentials);
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
    }
    return response;
  }

  async logout(): Promise<void> {
    await this.post('/api/auth/logout');
    localStorage.removeItem('auth_token');
  }

  async getCurrentUser(): Promise<any> {
    return this.get('/api/auth/me');
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<any> {
    return this.get('/api/dashboard/stats');
  }

  async getAnalytics(): Promise<any> {
    return this.get('/api/analytics');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export types
export interface QueryRequest {
  query: string;
  options?: {
    model?: string;
    max_tokens?: number;
    temperature?: number;
    include_citations?: boolean;
    include_fact_check?: boolean;
  };
}

export interface QueryResponse {
  answer: string;
  citations?: Array<{
    source: string;
    title: string;
    url?: string;
    confidence: number;
  }>;
  fact_check?: {
    is_factual: boolean;
    confidence: number;
    explanation: string;
  };
  metadata: {
    model_used: string;
    tokens_used: number;
    processing_time: number;
  };
}

export default apiClient; 