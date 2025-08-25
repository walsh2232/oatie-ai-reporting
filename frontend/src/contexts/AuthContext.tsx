/**
 * Authentication Context Provider
 * Manages user authentication state and enterprise SSO integration
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

interface User {
  id: string
  username: string
  email: string
  roles: string[]
  full_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: true,
  isAuthenticated: false,
}

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true }
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        isAuthenticated: true,
      }
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      }
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      }
    
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    default:
      return state
  }
}

interface AuthContextType {
  state: AuthState
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  initiateSSOLogin: () => Promise<void>
  hasRole: (role: string) => boolean
  hasPermission: (permission: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)
  const navigate = useNavigate()

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      
      if (token) {
        try {
          const response = await fetch('/api/v1/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          })
          
          if (response.ok) {
            const userData = await response.json()
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: {
                user: userData,
                token,
              },
            })
          } else {
            localStorage.removeItem('access_token')
            dispatch({ type: 'LOGOUT' })
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('access_token')
          dispatch({ type: 'LOGOUT' })
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false })
      }
    }

    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    dispatch({ type: 'LOGIN_START' })

    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch('/api/v1/auth/token', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const { access_token } = await response.json()
        localStorage.setItem('access_token', access_token)

        // Get user information
        const userResponse = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${access_token}`,
          },
        })

        if (userResponse.ok) {
          const userData = await userResponse.json()
          
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: {
              user: userData,
              token: access_token,
            },
          })

          toast.success('Successfully logged in!')
          navigate('/')
        } else {
          throw new Error('Failed to get user information')
        }
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error instanceof Error ? error.message : 'Login failed',
      })
      toast.error(error instanceof Error ? error.message : 'Login failed')
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      dispatch({ type: 'LOGOUT' })
      toast.success('Successfully logged out')
      navigate('/login')
    }
  }

  const initiateSSOLogin = async () => {
    try {
      const response = await fetch('/api/v1/auth/sso/initiate', {
        method: 'POST',
      })

      if (response.ok) {
        const { redirect_url } = await response.json()
        window.location.href = redirect_url
      } else {
        throw new Error('SSO not available')
      }
    } catch (error) {
      console.error('SSO initiation error:', error)
      toast.error('SSO login not available')
    }
  }

  const hasRole = (role: string): boolean => {
    return state.user?.roles.includes(role) || false
  }

  const hasPermission = (permission: string): boolean => {
    // Simple permission check based on roles
    const rolePermissions: Record<string, string[]> = {
      admin: ['*'],
      analyst: ['reports:read', 'reports:create', 'queries:execute', 'data:read'],
      viewer: ['reports:read', 'data:read'],
    }

    if (!state.user) return false

    for (const role of state.user.roles) {
      const permissions = rolePermissions[role] || []
      if (permissions.includes('*') || permissions.includes(permission)) {
        return true
      }
    }

    return false
  }

  const contextValue: AuthContextType = {
    state,
    login,
    logout,
    initiateSSOLogin,
    hasRole,
    hasPermission,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}