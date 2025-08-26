/**
 * Simplified Main Application Component for Development
 * Oracle BI Publisher Integration Platform Frontend
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'

// Simplified components for development
import Layout from './components/Layout/Layout-simple'
import Dashboard from './pages/Dashboard-simple'

// React Query configuration
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            retry: 2,
            refetchOnWindowFocus: false,
        },
    },
})

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <div className="app" style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
                    <Routes>
                        <Route path="/" element={<Layout />}>
                            <Route index element={<Dashboard />} />
                        </Route>
                    </Routes>

                    {/* Global toast notifications */}
                    <Toaster
                        position="top-right"
                        toastOptions={{
                            duration: 4000,
                            style: {
                                background: '#ffffff',
                                color: '#1f2937',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                                fontSize: '14px',
                            },
                        }}
                    />
                </div>
            </Router>
        </QueryClientProvider>
    )
}

export default App
