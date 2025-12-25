"""
Token-Aware API Service Layer with Auto-Refresh
Implements API client with automatic token refresh and request interceptors
"""

# API Service with Token Management
api_service = """
// services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Include cookies
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add access token to headers
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // If error is 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                return this.client(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshAccessToken();
            this.processQueue(null, newToken);
            
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private processQueue(error: any, token: string | null = null) {
    this.failedQueue.forEach((promise) => {
      if (error) {
        promise.reject(error);
      } else {
        promise.resolve(token);
      }
    });
    this.failedQueue = [];
  }

  private async refreshAccessToken(): Promise<string> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        {},
        { withCredentials: true }
      );
      
      const newAccessToken = response.data.access_token;
      this.setAccessToken(newAccessToken);
      return newAccessToken;
    } catch (error) {
      throw new Error('Token refresh failed');
    }
  }

  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private setAccessToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private clearTokens() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      document.cookie = 'refresh_token=; Max-Age=0; path=/;';
    }
  }

  // Public API methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // Helper method to set tokens after login
  setTokens(accessToken: string) {
    this.setAccessToken(accessToken);
  }

  // Helper method to clear tokens on logout
  logout() {
    this.clearTokens();
  }
}

// Export singleton instance
export const apiService = new ApiService();
"""

# Auth Service using API Service
auth_service = """
// services/auth.ts
import { apiService } from './api';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  };
}

interface SignupData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export class AuthService {
  static async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>('/auth/login', {
      email,
      password,
    });
    
    // Store access token
    apiService.setTokens(response.access_token);
    
    return response;
  }

  static async signup(data: SignupData): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>('/auth/signup', data);
    
    // Store access token
    apiService.setTokens(response.access_token);
    
    return response;
  }

  static async logout(): Promise<void> {
    try {
      await apiService.post('/auth/logout');
    } finally {
      apiService.logout();
    }
  }

  static async getCurrentUser() {
    return apiService.get('/auth/me');
  }

  static async isAuthenticated(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch {
      return false;
    }
  }

  static async hasRole(role: string): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return user.role === role;
    } catch {
      return false;
    }
  }

  static async hasPermission(permission: string): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return user.permissions?.includes(permission) ?? false;
    } catch {
      return false;
    }
  }

  static getOAuthUrl(provider: 'google' | 'github'): string {
    const redirectUri = `${window.location.origin}/auth/callback`;
    const state = Math.random().toString(36).substring(7);
    
    // Store state for verification
    sessionStorage.setItem('oauth_state', state);
    
    return `${process.env.NEXT_PUBLIC_API_URL}/auth/oauth/${provider}?redirect_uri=${redirectUri}&state=${state}`;
  }

  static async handleOAuthCallback(code: string, state: string): Promise<LoginResponse> {
    const storedState = sessionStorage.getItem('oauth_state');
    
    if (state !== storedState) {
      throw new Error('Invalid state parameter');
    }
    
    sessionStorage.removeItem('oauth_state');
    
    const response = await apiService.post<LoginResponse>('/auth/oauth/callback', {
      code,
      state,
    });
    
    apiService.setTokens(response.access_token);
    
    return response;
  }
}
"""

# Example API hooks for data fetching
api_hooks = """
// hooks/useApi.ts
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useApi<T = any>(url: string, options?: {
  skip?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!options?.skip);
  const [error, setError] = useState<Error | null>(null);
  const [refetchCounter, setRefetchCounter] = useState(0);

  useEffect(() => {
    if (options?.skip) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiService.get<T>(url);
        setData(result);
        options?.onSuccess?.(result);
      } catch (err) {
        const error = err as Error;
        setError(error);
        options?.onError?.(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, options?.skip, refetchCounter]);

  const refetch = () => {
    setRefetchCounter(prev => prev + 1);
  };

  return { data, loading, error, refetch };
}

export function useMutation<TData = any, TVariables = any>(
  url: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST'
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (variables?: TVariables): Promise<TData | null> => {
    try {
      setLoading(true);
      setError(null);
      
      let result: TData;
      switch (method) {
        case 'POST':
          result = await apiService.post<TData>(url, variables);
          break;
        case 'PUT':
          result = await apiService.put<TData>(url, variables);
          break;
        case 'PATCH':
          result = await apiService.patch<TData>(url, variables);
          break;
        case 'DELETE':
          result = await apiService.delete<TData>(url);
          break;
      }
      
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { mutate, loading, error };
}
"""

print("✅ Token-Aware API Service Layer Created")
print("\n📄 Components Generated:")
print("  • API Service with Auto-Refresh (services/api.ts)")
print("  • Auth Service (services/auth.ts)")
print("  • API Hooks (hooks/useApi.ts)")
print("\n🔧 Features:")
print("  • Automatic access token injection")
print("  • Auto-refresh on 401 responses")
print("  • Request queue during token refresh")
print("  • Axios interceptors for seamless token management")
print("  • TypeScript types for type safety")
print("  • Custom hooks for data fetching and mutations")
print("  • Singleton pattern for shared instance")
print("  • Cookie + localStorage token storage")
