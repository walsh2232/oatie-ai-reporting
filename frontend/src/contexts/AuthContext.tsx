import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { AuthContextType, AuthState, LoginCredentials, OracleConnectionForm, User } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthAction {
  type: 'LOGIN_START' | 'LOGIN_SUCCESS' | 'LOGIN_FAILURE' | 'LOGOUT' | 'SET_LOADING' | 'SET_ERROR' | 'UPDATE_USER';
  payload?: any;
}

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        isLoading: false, 
        isAuthenticated: true, 
        user: action.payload,
        error: null 
      };
    case 'LOGIN_FAILURE':
      return { 
        ...state, 
        isLoading: false, 
        isAuthenticated: false, 
        user: null,
        error: action.payload 
      };
    case 'LOGOUT':
      return { 
        ...state, 
        isAuthenticated: false, 
        user: null, 
        isLoading: false,
        error: null 
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'UPDATE_USER':
      return { ...state, user: action.payload };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Check for existing session on app load
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          dispatch({ type: 'SET_LOADING', payload: true });
          // In a real app, validate token with backend
          const userData = localStorage.getItem('userData');
          if (userData) {
            dispatch({ type: 'LOGIN_SUCCESS', payload: JSON.parse(userData) });
          }
        } catch (error) {
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          dispatch({ type: 'LOGIN_FAILURE', payload: 'Session expired' });
        } finally {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      // Mock authentication - in real app, call your auth API
      if (credentials.username === 'admin' && credentials.password === 'admin') {
        const mockUser: User = {
          id: '1',
          username: credentials.username,
          email: 'admin@company.com',
          fullName: 'System Administrator',
          role: 'admin',
          permissions: ['read', 'write', 'admin'],
          oracleConnections: []
        };

        const token = 'mock-jwt-token-' + Date.now();
        
        if (credentials.rememberMe) {
          localStorage.setItem('authToken', token);
          localStorage.setItem('userData', JSON.stringify(mockUser));
        }

        dispatch({ type: 'LOGIN_SUCCESS', payload: mockUser });
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE', payload: error instanceof Error ? error.message : 'Login failed' });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    dispatch({ type: 'LOGOUT' });
  };

  const addOracleConnection = async (connection: OracleConnectionForm): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Test connection first if requested
      if (connection.testConnection) {
        const isValid = await testOracleConnection(connection);
        if (!isValid) {
          throw new Error('Connection test failed');
        }
      }

      const newConnection = {
        id: Date.now().toString(),
        name: connection.name,
        host: connection.host,
        port: connection.port,
        serviceName: connection.serviceName,
        username: connection.username,
        isActive: state.user?.oracleConnections.length === 0,
        lastConnected: new Date(),
        status: 'connected' as const
      };

      const updatedUser = {
        ...state.user!,
        oracleConnections: [...state.user!.oracleConnections, newConnection]
      };

      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      localStorage.setItem('userData', JSON.stringify(updatedUser));

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to add connection' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const removeOracleConnection = async (connectionId: string): Promise<void> => {
    try {
      const updatedConnections = state.user!.oracleConnections.filter(conn => conn.id !== connectionId);
      const updatedUser = {
        ...state.user!,
        oracleConnections: updatedConnections
      };

      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      localStorage.setItem('userData', JSON.stringify(updatedUser));
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to remove connection' });
      throw error;
    }
  };

  const testOracleConnection = async (connection: OracleConnectionForm): Promise<boolean> => {
    try {
      // Mock connection test - in real app, call backend API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate success for demo connections
      if (connection.host && connection.port && connection.serviceName && connection.username) {
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  };

  const setActiveConnection = async (connectionId: string): Promise<void> => {
    try {
      const updatedConnections = state.user!.oracleConnections.map(conn => ({
        ...conn,
        isActive: conn.id === connectionId
      }));

      const updatedUser = {
        ...state.user!,
        oracleConnections: updatedConnections
      };

      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      localStorage.setItem('userData', JSON.stringify(updatedUser));
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to set active connection' });
      throw error;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    addOracleConnection,
    removeOracleConnection,
    testOracleConnection,
    setActiveConnection,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
