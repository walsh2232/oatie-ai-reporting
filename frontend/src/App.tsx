/**
 * Main Application Component with Oracle Redwood Design System
 * Implements enterprise-grade UI with accessibility compliance (WCAG 2.1 AA)
 */

import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ApolloProvider } from '@apollo/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import { apolloClient } from './lib/apollo'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Queries from './pages/Queries'
import Analytics from './pages/Analytics'
import Users from './pages/Users'
import Settings from './pages/Settings'
import Login from './pages/Login'
import ProtectedRoute from './components/Auth/ProtectedRoute'

// React Query configuration for optimal performance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ApolloProvider client={apolloClient}>
        <ThemeProvider>
          <AuthProvider>
            <Router>
              <div className="app" role="application" aria-label="Oatie AI Reporting Platform">
                <Routes>
                  <Route path="/login" element={<Login />} />
                  <Route path="/" element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }>
                    <Route index element={<Dashboard />} />
                    <Route path="reports" element={<Reports />} />
                    <Route path="queries" element={<Queries />} />
                    <Route path="analytics" element={<Analytics />} />
                    <Route path="users" element={<Users />} />
                    <Route path="settings" element={<Settings />} />
                  </Route>
                </Routes>
                
                {/* Global toast notifications */}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: 'var(--oj-palette-neutral-0)',
                      color: 'var(--oj-palette-neutral-190)',
                      border: '1px solid var(--oj-palette-neutral-40)',
                      borderRadius: 'var(--oj-border-radius-md)',
                      fontSize: 'var(--oj-typography-body-md-font-size)',
                    },
                    success: {
                      iconTheme: {
                        primary: 'var(--oj-palette-green-70)',
                        secondary: 'var(--oj-palette-neutral-0)',
                      },
                    },
                    error: {
                      iconTheme: {
                        primary: 'var(--oj-palette-red-70)',
                        secondary: 'var(--oj-palette-neutral-0)',
                      },
                    },
                  }}
                />
              </div>
            </Router>
          </AuthProvider>
        </ThemeProvider>
      </ApolloProvider>
    </QueryClientProvider>
  )
}

export default App