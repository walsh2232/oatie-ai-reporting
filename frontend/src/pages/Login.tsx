import React, { useState } from 'react';
import { Database, Bot, Lock, User } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: 'demo@oracle.com',
    password: 'demo123'
  });
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const success = await login(credentials.username, credentials.password);
      if (success) {
        toast.success('Welcome to Oatie AI Reporting!');
      } else {
        toast.error('Invalid credentials. Please try again.');
      }
    } catch (error) {
      toast.error('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-orange-600 to-orange-800 flex-col justify-center items-center text-white">
        <div className="max-w-md text-center">
          <div className="flex items-center justify-center mb-8">
            <Database className="w-16 h-16 mr-4" />
            <div>
              <h1 className="text-4xl font-bold">Oatie</h1>
              <p className="text-orange-200">AI Reporting Assistant</p>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold mb-4">
            Transform Your Fusion Reporting with AI
          </h2>
          
          <p className="text-lg text-orange-100 mb-8">
            Oracle BI Publisher AI Assistant with Oracle Redwood Design System
          </p>

          <div className="space-y-4 text-left">
            <div className="flex items-center">
              <Bot className="w-6 h-6 mr-3 text-orange-200" />
              <span>Natural language to SQL conversion</span>
            </div>
            <div className="flex items-center">
              <Database className="w-6 h-6 mr-3 text-orange-200" />
              <span>Complete Oracle BI Publisher integration</span>
            </div>
            <div className="flex items-center">
              <Lock className="w-6 h-6 mr-3 text-orange-200" />
              <span>Enterprise-grade security & multi-tenancy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50">
        <div className="max-w-md w-full">
          {/* Mobile branding */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <Database className="w-12 h-12 text-orange-600 mr-2" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Oatie</h1>
                <p className="text-gray-600">AI Reporting Assistant</p>
              </div>
            </div>
          </div>

          <div className="redwood-card">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Welcome back</h2>
              <p className="text-gray-600 mt-2">
                Sign in to your Oracle BI Publisher AI Assistant
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Username or Email
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="username"
                    type="text"
                    value={credentials.username}
                    onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                    className="redwood-input pl-10"
                    placeholder="Enter your username"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="password"
                    type="password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    className="redwood-input pl-10"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember"
                    type="checkbox"
                    className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember" className="ml-2 block text-sm text-gray-700">
                    Remember me
                  </label>
                </div>
                <a href="#" className="text-sm text-orange-600 hover:text-orange-500">
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full redwood-button redwood-button--primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="redwood-spinner mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  'Sign in'
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800 font-medium mb-2">Demo Credentials:</p>
                <p className="text-sm text-blue-700">
                  Username: <code className="bg-blue-100 px-1 rounded">demo@oracle.com</code><br />
                  Password: <code className="bg-blue-100 px-1 rounded">demo123</code>
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-8 text-sm text-gray-600">
            <p>© 2024 Oracle Corporation. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;