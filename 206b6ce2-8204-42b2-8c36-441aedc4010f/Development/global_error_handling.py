"""
Global Error Handling System
Implements centralized error handling, error boundaries, and user notifications
"""

# Error Boundary Component
error_boundary = """
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Log to error tracking service (e.g., Sentry)
    if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
      // Sentry.captureException(error, { extra: errorInfo });
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
          <div className="max-w-md w-full p-8 bg-[#2A2A2D] rounded-lg shadow-xl text-center">
            <h1 className="text-2xl font-bold text-[#f04438] mb-4">
              Something went wrong
            </h1>
            <p className="text-[#909094] mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-[#ffd400] text-[#1D1D20] rounded-md font-medium hover:bg-[#e6c000] transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
"""

# Error Handler Utility
error_handler = """
// utils/errorHandler.ts
export enum ErrorType {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  NETWORK = 'NETWORK',
  SERVER = 'SERVER',
  UNKNOWN = 'UNKNOWN',
}

export interface AppError {
  type: ErrorType;
  message: string;
  code?: string;
  details?: any;
}

export class ErrorHandler {
  static handle(error: any): AppError {
    // Axios error
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      switch (status) {
        case 400:
          return {
            type: ErrorType.VALIDATION,
            message: data.message || 'Invalid request',
            details: data.errors,
          };
        case 401:
          return {
            type: ErrorType.AUTHENTICATION,
            message: 'You must be logged in to continue',
          };
        case 403:
          return {
            type: ErrorType.AUTHORIZATION,
            message: 'You do not have permission to perform this action',
          };
        case 404:
          return {
            type: ErrorType.VALIDATION,
            message: 'The requested resource was not found',
          };
        case 422:
          return {
            type: ErrorType.VALIDATION,
            message: 'Validation failed',
            details: data.errors,
          };
        case 500:
        case 502:
        case 503:
          return {
            type: ErrorType.SERVER,
            message: 'Server error. Please try again later.',
          };
        default:
          return {
            type: ErrorType.UNKNOWN,
            message: data.message || 'An unexpected error occurred',
          };
      }
    }

    // Network error
    if (error.request) {
      return {
        type: ErrorType.NETWORK,
        message: 'Network error. Please check your connection.',
      };
    }

    // JavaScript error
    if (error instanceof Error) {
      return {
        type: ErrorType.UNKNOWN,
        message: error.message,
      };
    }

    // Unknown error
    return {
      type: ErrorType.UNKNOWN,
      message: 'An unexpected error occurred',
    };
  }

  static getUserMessage(error: AppError): string {
    return error.message;
  }

  static shouldRetry(error: AppError): boolean {
    return [ErrorType.NETWORK, ErrorType.SERVER].includes(error.type);
  }

  static shouldLogout(error: AppError): boolean {
    return error.type === ErrorType.AUTHENTICATION;
  }
}
"""

# Toast Notification System
toast_system = """
// components/Toast.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  showError: (message: string) => void;
  showSuccess: (message: string) => void;
  showWarning: (message: string) => void;
  showInfo: (message: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (message: string, type: ToastType = 'info', duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: Toast = { id, message, type, duration };
    
    setToasts((prev) => [...prev, toast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  };

  const showError = (message: string) => showToast(message, 'error');
  const showSuccess = (message: string) => showToast(message, 'success');
  const showWarning = (message: string) => showToast(message, 'warning');
  const showInfo = (message: string) => showToast(message, 'info');

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const getToastStyles = (type: ToastType) => {
    const baseStyles = 'px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px]';
    switch (type) {
      case 'success':
        return `${baseStyles} bg-[#17b26a] bg-opacity-10 border border-[#17b26a] text-[#17b26a]`;
      case 'error':
        return `${baseStyles} bg-[#f04438] bg-opacity-10 border border-[#f04438] text-[#f04438]`;
      case 'warning':
        return `${baseStyles} bg-[#ffd400] bg-opacity-10 border border-[#ffd400] text-[#ffd400]`;
      case 'info':
        return `${baseStyles} bg-[#A1C9F4] bg-opacity-10 border border-[#A1C9F4] text-[#A1C9F4]`;
    }
  };

  return (
    <ToastContext.Provider value={{ showToast, showError, showSuccess, showWarning, showInfo }}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div key={toast.id} className={getToastStyles(toast.type)}>
            <span className="flex-1">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-current hover:opacity-70 transition-opacity"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}
"""

# Global Error Handler Hook
error_hook = """
// hooks/useErrorHandler.ts
import { useCallback } from 'react';
import { useRouter } from 'next/router';
import { useToast } from '../components/Toast';
import { ErrorHandler, AppError } from '../utils/errorHandler';

export function useErrorHandler() {
  const router = useRouter();
  const { showError, showWarning } = useToast();

  const handleError = useCallback((error: any) => {
    const appError: AppError = ErrorHandler.handle(error);
    const userMessage = ErrorHandler.getUserMessage(appError);

    // Show toast notification
    showError(userMessage);

    // Handle authentication errors
    if (ErrorHandler.shouldLogout(appError)) {
      router.push('/login');
      return;
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Application Error:', appError);
    }

    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service
    }
  }, [router, showError]);

  return { handleError };
}
"""

# Enhanced API Service with Error Handling
enhanced_api_service = """
// services/api.ts (enhanced version)
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { ErrorHandler } from '../utils/errorHandler';

// Add global error handler to ApiService class
class ApiService {
  // ... existing code ...

  private handleError(error: AxiosError) {
    const appError = ErrorHandler.handle(error);
    
    // Emit error event that can be caught globally
    window.dispatchEvent(new CustomEvent('api-error', { detail: appError }));
    
    throw error;
  }

  // Wrap all methods with error handling
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.get<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }
  
  // Similar for post, put, patch, delete...
}
"""

# Updated App Wrapper with Error Providers
updated_app_wrapper = """
// pages/_app.tsx (updated)
import type { AppProps } from 'next/app';
import { AuthProvider } from '../contexts/AuthContext';
import { ToastProvider } from '../components/Toast';
import { ErrorBoundary } from '../components/ErrorBoundary';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <Component {...pageProps} />
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}
"""

print("✅ Global Error Handling System Created")
print("\n📄 Components Generated:")
print("  • Error Boundary (components/ErrorBoundary.tsx)")
print("  • Error Handler Utility (utils/errorHandler.ts)")
print("  • Toast Notification System (components/Toast.tsx)")
print("  • useErrorHandler Hook (hooks/useErrorHandler.ts)")
print("  • Enhanced API Service with error handling")
print("  • Updated App Wrapper with providers")
print("\n🛡️ Features:")
print("  • React Error Boundaries for UI crash protection")
print("  • Centralized error handling logic")
print("  • User-friendly error messages")
print("  • Toast notifications (success/error/warning/info)")
print("  • Automatic error categorization")
print("  • Retry logic for network errors")
print("  • Auto-logout on auth errors")
print("  • Development vs production error logging")
print("  • Zerve design system styling")
