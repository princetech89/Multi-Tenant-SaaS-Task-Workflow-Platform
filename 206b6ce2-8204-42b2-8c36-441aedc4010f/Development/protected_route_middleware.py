"""
Protected Route Middleware & Higher-Order Components
Implements route protection and authentication checks for frontend
"""

# Protected Route HOC
protected_route_hoc = """
// components/ProtectedRoute.tsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { AuthService } from '../services/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredPermission?: string;
  fallbackUrl?: string;
}

export function ProtectedRoute({
  children,
  requiredRole,
  requiredPermission,
  fallbackUrl = '/login'
}: ProtectedRouteProps) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthorization();
  }, []);

  const checkAuthorization = async () => {
    try {
      const isAuthenticated = await AuthService.isAuthenticated();
      
      if (!isAuthenticated) {
        router.push(`${fallbackUrl}?redirect=${router.pathname}`);
        return;
      }

      // Check role if required
      if (requiredRole) {
        const hasRole = await AuthService.hasRole(requiredRole);
        if (!hasRole) {
          router.push('/unauthorized');
          return;
        }
      }

      // Check permission if required
      if (requiredPermission) {
        const hasPermission = await AuthService.hasPermission(requiredPermission);
        if (!hasPermission) {
          router.push('/unauthorized');
          return;
        }
      }

      setIsAuthorized(true);
    } catch (error) {
      console.error('Authorization check failed:', error);
      router.push(fallbackUrl);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ffd400] mx-auto mb-4"></div>
          <p className="text-[#fbfbff]">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return null;
  }

  return <>{children}</>;
}

// Convenience wrapper for pages
export function withAuth(
  Component: React.ComponentType,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function AuthenticatedComponent(props: any) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}
"""

# Auth Context Provider
auth_context = """
// contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { AuthService } from '../services/auth';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const authenticated = await AuthService.isAuthenticated();
      if (authenticated) {
        const userData = await AuthService.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await AuthService.login(email, password);
    setUser(response.user);
    setIsAuthenticated(true);
  };

  const signup = async (data: any) => {
    const response = await AuthService.signup(data);
    setUser(response.user);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    await AuthService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshAuth = async () => {
    try {
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh auth:', error);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        signup,
        logout,
        refreshAuth
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
"""

# Next.js Middleware for route protection
nextjs_middleware = """
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const publicRoutes = ['/login', '/signup', '/auth/callback', '/'];
const adminRoutes = ['/admin'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('access_token')?.value;

  // Allow public routes
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Redirect to login if no token
  if (!token) {
    const url = new URL('/login', request.url);
    url.searchParams.set('redirect', pathname);
    return NextResponse.redirect(url);
  }

  // Check admin routes (would verify JWT in production)
  if (adminRoutes.some(route => pathname.startsWith(route))) {
    // In production, decode JWT and check role
    // For now, just allow if token exists
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
"""

# App wrapper with providers
app_wrapper = """
// pages/_app.tsx
import type { AppProps } from 'next/app';
import { AuthProvider } from '../contexts/AuthContext';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}
"""

# Unauthorized page
unauthorized_page = """
// pages/unauthorized.tsx
import Link from 'next/link';

export default function Unauthorized() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-[#f04438] mb-4">403</h1>
        <h2 className="text-2xl font-semibold text-[#fbfbff] mb-4">
          Access Denied
        </h2>
        <p className="text-[#909094] mb-8">
          You don't have permission to access this page.
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-6 py-3 bg-[#ffd400] text-[#1D1D20] rounded-md font-medium hover:bg-[#e6c000] transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
"""

print("✅ Protected Route Middleware Created")
print("\n📄 Components Generated:")
print("  • ProtectedRoute HOC (components/ProtectedRoute.tsx)")
print("  • AuthContext Provider (contexts/AuthContext.tsx)")
print("  • Next.js Middleware (middleware.ts)")
print("  • App Wrapper (_app.tsx)")
print("  • Unauthorized Page (pages/unauthorized.tsx)")
print("\n🔒 Features:")
print("  • Route-level authentication checks")
print("  • Role-based access control")
print("  • Permission-based access control")
print("  • Automatic redirect to login")
print("  • Loading states during auth check")
print("  • Global auth context")
print("  • Server-side middleware protection")
