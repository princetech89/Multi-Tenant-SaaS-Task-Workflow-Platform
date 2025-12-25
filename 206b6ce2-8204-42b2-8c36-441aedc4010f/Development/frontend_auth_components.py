"""
Frontend Authentication Components
Creates React/Next.js authentication pages and components with OAuth integration
"""

# Login Page Component
login_page = """
// pages/login.tsx
import { useState } from 'react';
import { useRouter } from 'next/router';
import { AuthService } from '../services/auth';
import { FcGoogle } from 'react-icons/fc';
import { FaGithub } from 'react-icons/fa';

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await AuthService.login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthLogin = (provider: 'google' | 'github') => {
    const authUrl = AuthService.getOAuthUrl(provider);
    window.location.href = authUrl;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
      <div className="max-w-md w-full space-y-8 p-8 bg-[#2A2A2D] rounded-lg shadow-xl">
        <div>
          <h2 className="text-center text-3xl font-bold text-[#fbfbff]">
            Sign in to your account
          </h2>
        </div>
        
        {error && (
          <div className="bg-[#f04438] bg-opacity-10 border border-[#f04438] text-[#f04438] px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleEmailLogin}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="text-[#fbfbff] text-sm font-medium">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="text-[#fbfbff] text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-[#1D1D20] bg-[#ffd400] hover:bg-[#e6c000] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#3A3A3D]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#2A2A2D] text-[#909094]">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <button
              onClick={() => handleOAuthLogin('google')}
              className="w-full inline-flex justify-center items-center py-2 px-4 border border-[#3A3A3D] rounded-md shadow-sm bg-[#1D1D20] text-sm font-medium text-[#fbfbff] hover:bg-[#2A2A2D] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400]"
            >
              <FcGoogle className="h-5 w-5 mr-2" />
              Google
            </button>
            <button
              onClick={() => handleOAuthLogin('github')}
              className="w-full inline-flex justify-center items-center py-2 px-4 border border-[#3A3A3D] rounded-md shadow-sm bg-[#1D1D20] text-sm font-medium text-[#fbfbff] hover:bg-[#2A2A2D] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400]"
            >
              <FaGithub className="h-5 w-5 mr-2" />
              GitHub
            </button>
          </div>
        </div>

        <div className="text-center">
          <a href="/signup" className="text-[#ffd400] hover:text-[#e6c000] text-sm">
            Don't have an account? Sign up
          </a>
        </div>
      </div>
    </div>
  );
}
"""

# Signup Page Component
signup_page = """
// pages/signup.tsx
import { useState } from 'react';
import { useRouter } from 'next/router';
import { AuthService } from '../services/auth';
import { FcGoogle } from 'react-icons/fc';
import { FaGithub } from 'react-icons/fa';

export default function Signup() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await AuthService.signup({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName
      });
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthSignup = (provider: 'google' | 'github') => {
    const authUrl = AuthService.getOAuthUrl(provider);
    window.location.href = authUrl;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
      <div className="max-w-md w-full space-y-8 p-8 bg-[#2A2A2D] rounded-lg shadow-xl">
        <div>
          <h2 className="text-center text-3xl font-bold text-[#fbfbff]">
            Create your account
          </h2>
        </div>
        
        {error && (
          <div className="bg-[#f04438] bg-opacity-10 border border-[#f04438] text-[#f04438] px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSignup}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="text-[#fbfbff] text-sm font-medium">
                  First Name
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  required
                  value={formData.firstName}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="lastName" className="text-[#fbfbff] text-sm font-medium">
                  Last Name
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  required
                  value={formData.lastName}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label htmlFor="email" className="text-[#fbfbff] text-sm font-medium">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="text-[#fbfbff] text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="text-[#fbfbff] text-sm font-medium">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 bg-[#1D1D20] border border-[#3A3A3D] rounded-md text-[#fbfbff] focus:outline-none focus:ring-2 focus:ring-[#ffd400] focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-[#1D1D20] bg-[#ffd400] hover:bg-[#e6c000] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#3A3A3D]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#2A2A2D] text-[#909094]">Or sign up with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <button
              onClick={() => handleOAuthSignup('google')}
              className="w-full inline-flex justify-center items-center py-2 px-4 border border-[#3A3A3D] rounded-md shadow-sm bg-[#1D1D20] text-sm font-medium text-[#fbfbff] hover:bg-[#2A2A2D] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400]"
            >
              <FcGoogle className="h-5 w-5 mr-2" />
              Google
            </button>
            <button
              onClick={() => handleOAuthSignup('github')}
              className="w-full inline-flex justify-center items-center py-2 px-4 border border-[#3A3A3D] rounded-md shadow-sm bg-[#1D1D20] text-sm font-medium text-[#fbfbff] hover:bg-[#2A2A2D] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ffd400]"
            >
              <FaGithub className="h-5 w-5 mr-2" />
              GitHub
            </button>
          </div>
        </div>

        <div className="text-center">
          <a href="/login" className="text-[#ffd400] hover:text-[#e6c000] text-sm">
            Already have an account? Sign in
          </a>
        </div>
      </div>
    </div>
  );
}
"""

# OAuth Callback Page
oauth_callback = """
// pages/auth/callback.tsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { AuthService } from '../../services/auth';

export default function OAuthCallback() {
  const router = useRouter();
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const { code, state, error: oauthError } = router.query;

      if (oauthError) {
        setError(oauthError as string);
        setTimeout(() => router.push('/login'), 3000);
        return;
      }

      if (code && state) {
        try {
          await AuthService.handleOAuthCallback(code as string, state as string);
          router.push('/dashboard');
        } catch (err: any) {
          setError(err.message || 'Authentication failed');
          setTimeout(() => router.push('/login'), 3000);
        }
      }
    };

    if (router.isReady) {
      handleCallback();
    }
  }, [router.isReady, router.query]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1D1D20]">
      <div className="text-center">
        {error ? (
          <div>
            <div className="text-[#f04438] text-xl font-semibold mb-4">
              Authentication Failed
            </div>
            <p className="text-[#909094]">{error}</p>
            <p className="text-[#909094] mt-2">Redirecting to login...</p>
          </div>
        ) : (
          <div>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ffd400] mx-auto mb-4"></div>
            <p className="text-[#fbfbff] text-lg">Completing authentication...</p>
          </div>
        )}
      </div>
    </div>
  );
}
"""

print("✅ Frontend Authentication Pages Created")
print("\n📄 Components Generated:")
print("  • Login Page (pages/login.tsx)")
print("  • Signup Page (pages/signup.tsx)")
print("  • OAuth Callback Page (pages/auth/callback.tsx)")
print("\n🎨 Features:")
print("  • Zerve design system (#1D1D20 bg, #fbfbff text, #ffd400 accent)")
print("  • Email/password authentication")
print("  • Google & GitHub OAuth buttons")
print("  • Form validation and error handling")
print("  • Loading states")
print("  • Responsive design")
print("  • Professional UI with Tailwind CSS")
