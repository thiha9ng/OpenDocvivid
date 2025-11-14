import { ApiResponse } from './types/api';
import { toast } from 'sonner';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Custom error class for API errors
export class ApiClientError extends Error {
  public status: number;
  public code?: string;
  public details?: any;

  constructor(message: string, status: number, code?: string, details?: any) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// Request configuration interface
interface RequestConfig extends RequestInit {
  timeout?: number;
}

// API Client class
export class ApiClient {
  private baseURL: string;
  private defaultHeaders: HeadersInit;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || API_BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Set authorization token
  setAuthToken(token: string) {
    this.defaultHeaders = {
      ...this.defaultHeaders,
      Authorization: `Bearer ${token}`,
    };
  }

  // Remove authorization token
  removeAuthToken() {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { Authorization, ...headers } = this.defaultHeaders as any;
    this.defaultHeaders = headers;
  }

  // Create authenticated request with session token
  private async createAuthenticatedRequest(
    url: string,
    config: RequestConfig = {}
  ): Promise<Response> {
    // Try to get session token from NextAuth
    if (typeof window !== 'undefined') {
      try {
        const { getSession } = await import('next-auth/react');
        const session = await getSession();
        
        if (session?.user && (session.user as any).accessToken) {
          const token = (session.user as any).accessToken;
          // Temporarily set token for this request
          const originalHeaders = this.defaultHeaders;
          this.setAuthToken(token);
          
          try {
            const response = await this.createRequest(url, config);
            // Restore original headers
            this.defaultHeaders = originalHeaders;
            return response;
          } catch (error) {
            // Restore original headers on error
            this.defaultHeaders = originalHeaders;
            throw error;
          }
        }
      } catch (error) {
        console.warn('Failed to get session token:', error);
      }
    }
    
    // Fallback to regular request without auth
    return this.createRequest(url, config);
  }

  // Create request with timeout
  private async createRequest(
    url: string,
    config: RequestConfig = {}
  ): Promise<Response> {
    const { timeout = 30000, ...fetchConfig } = config;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        headers: {
          ...this.defaultHeaders,
          ...fetchConfig.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiClientError('Request timeout', 408);
      }
      throw error;
    }
  }

  // Handle response and errors
  private async handleResponse<T>(response: Response): Promise<T> {
    let data: any;
    
    try {
      const text = await response.text();
      data = text ? JSON.parse(text) : {};
    } catch {
      throw new ApiClientError(
        'Invalid JSON response',
        response.status,
        'INVALID_JSON'
      );
    }

    if (!response.ok) {
      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        const errorMessage = data.message || 'Please login first';
        toast.warning(errorMessage, {
          duration: 2000,
        });
        
        // Redirect to home page after showing the toast
        if (typeof window !== 'undefined') {
          setTimeout(() => {
            window.location.href = '/';
          }, 2500);
        }
      }
      
      const errorMessage = data.message || `HTTP ${response.status}: ${response.statusText}`;
      throw new ApiClientError(
        errorMessage,
        response.status,
        data.code,
        data.details
      );
    }

    // Check if the response has the expected API format
    if (data.status === 'error') {
      throw new ApiClientError(
        data.message || 'API Error',
        response.status,
        data.code,
        data.details
      );
    }

    return data;
  }

  // GET request
  async get<T = any>(
    endpoint: string,
    params?: Record<string, any>,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    // Properly construct URL by joining base URL and endpoint
    const fullUrl = this.baseURL.endsWith('/') 
      ? this.baseURL + endpoint.replace(/^\//, '') 
      : this.baseURL + (endpoint.startsWith('/') ? endpoint : '/' + endpoint);
    const url = new URL(fullUrl);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await this.createAuthenticatedRequest(url.toString(), {
      method: 'GET',
      ...config,
    });

    return this.handleResponse<ApiResponse<T>>(response);
  }

  // POST request with JSON body
  async post<T = any>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    const fullUrl = this.baseURL.endsWith('/') 
      ? this.baseURL + endpoint.replace(/^\//, '') 
      : this.baseURL + (endpoint.startsWith('/') ? endpoint : '/' + endpoint);

    const response = await this.createAuthenticatedRequest(fullUrl, {
      method: 'POST',
      body: JSON.stringify(data),
      ...config,
    });

    return this.handleResponse<ApiResponse<T>>(response);
  }

  // POST request with FormData (for file uploads)
  async postFormData<T = any>(
    endpoint: string,
    formData: FormData,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    const fullUrl = this.baseURL.endsWith('/') 
      ? this.baseURL + endpoint.replace(/^\//, '') 
      : this.baseURL + (endpoint.startsWith('/') ? endpoint : '/' + endpoint);

    // For FormData, we need to completely avoid setting Content-Type
    // Let the browser set it automatically with the correct boundary
    // We need a special handling that bypasses the default headers in createAuthenticatedRequest
    
    // Build headers without Content-Type
    const headers: HeadersInit = {};
    
    // Add Authorization if available
    const authHeader = (this.defaultHeaders as any)['Authorization'];
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    // Add any additional headers from config, but remove Content-Type
    if (config?.headers) {
      const configHeaders = { ...config.headers };
      delete (configHeaders as any)['Content-Type'];
      Object.assign(headers, configHeaders);
    }

    // We need to bypass the createAuthenticatedRequest's default header merging
    // So we'll call createRequest directly but handle auth manually
    const controller = new AbortController();
    const timeout = config?.timeout || 30000;
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      // Get session token if available and add Authorization header
      if (typeof window !== 'undefined') {
        try {
          const { getSession } = await import('next-auth/react');
          const session = await getSession();
          
          if (session?.user && (session.user as any).accessToken) {
            const token = (session.user as any).accessToken;
            (headers as any)['Authorization'] = `Bearer ${token}`;
          }
        } catch (error) {
          console.warn('Failed to get session token:', error);
        }
      }

      const response = await fetch(fullUrl, {
        method: 'POST',
        body: formData,
        headers: headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return this.handleResponse<ApiResponse<T>>(response);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiClientError('Request timeout', 408);
      }
      throw error;
    }
  }

}

// Default API client instance
export const apiClient = new ApiClient();
