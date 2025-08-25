/**
 * Login Page with Oracle Redwood Design System and SSO Support
 * WCAG 2.1 AA compliant with proper form accessibility
 */

import React, { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/UI/LoadingSpinner'

const Login: React.FC = () => {
  const { state, login, initiateSSOLogin } = useAuth()
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Redirect if already authenticated
  if (state.isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await login(credentials.username, credentials.password)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCredentials((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-indigo-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">O</span>
          </div>
          <h1 className="text-heading-xl text-gray-900 mb-2">Oatie AI Reporting</h1>
          <p className="text-body-md text-gray-600">
            Enterprise Oracle BI Publisher AI Assistant
          </p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="form-label">
                Username or Email
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="form-input"
                placeholder="Enter your username"
                value={credentials.username}
                onChange={handleInputChange}
                disabled={isLoading}
                aria-describedby="username-help"
              />
              <p id="username-help" className="sr-only">
                Enter your username or email address to sign in
              </p>
            </div>

            <div>
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  className="form-input pr-10"
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  aria-describedby="password-help"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              <p id="password-help" className="sr-only">
                Enter your password to sign in
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading || !credentials.username || !credentials.password}
              className="w-full btn btn-primary"
              aria-describedby="login-status"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="sm" className="mr-2" />
                  Signing in...
                </div>
              ) : (
                'Sign In'
              )}
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <button
              type="button"
              onClick={initiateSSOLogin}
              disabled={isLoading}
              className="w-full btn btn-secondary"
            >
              Enterprise SSO
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-body-sm text-gray-600">
              Demo credentials: Any username/password combination
            </p>
          </div>
        </div>

        <div className="text-center text-body-sm text-gray-500">
          <p>Protected by enterprise-grade security</p>
          <p>© 2024 Oatie AI Reporting Platform</p>
        </div>
      </div>
    </div>
  )
}

export default Login