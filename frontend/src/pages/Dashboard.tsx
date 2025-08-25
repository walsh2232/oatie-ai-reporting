/**
 * Dashboard Page - Enterprise Overview with Oracle Redwood Design
 * Displays key metrics, performance indicators, and quick actions
 */

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  ChartBarIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CogIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

import { useAuth } from '../contexts/AuthContext'
import Card from '../components/UI/Card'
import LoadingSpinner from '../components/UI/LoadingSpinner'
import ErrorMessage from '../components/UI/ErrorMessage'

interface PerformanceMetrics {
  average_response_time: number
  total_requests: number
  cache_hit_rate: number
  active_users: number
  error_rate: number
}

interface UsageStats {
  report_generations: number
  query_executions: number
  data_exports: number
  unique_users: number
}

const Dashboard: React.FC = () => {
  const { state: authState, hasPermission } = useAuth()

  // Fetch performance metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery<PerformanceMetrics>({
    queryKey: ['performance-metrics'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/analytics/performance', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!response.ok) throw new Error('Failed to fetch metrics')
      return response.json()
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch usage statistics
  const {
    data: usage,
    isLoading: usageLoading,
    error: usageError,
  } = useQuery<UsageStats>({
    queryKey: ['usage-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/analytics/usage?period=24h', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!response.ok) throw new Error('Failed to fetch usage stats')
      return response.json()
    },
  })

  if (metricsLoading || usageLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (metricsError || usageError) {
    return (
      <ErrorMessage
        title="Failed to load dashboard data"
        message="Please try refreshing the page or contact support if the problem persists."
      />
    )
  }

  const quickActions = [
    {
      title: 'Generate Report',
      description: 'Create a new report using AI-enhanced templates',
      icon: DocumentTextIcon,
      href: '/reports',
      color: 'blue',
      permission: 'reports:create',
    },
    {
      title: 'Execute Query',
      description: 'Run SQL queries with intelligent caching',
      icon: ChartBarIcon,
      href: '/queries',
      color: 'green',
      permission: 'queries:execute',
    },
    {
      title: 'View Analytics',
      description: 'Monitor system performance and usage',
      icon: ArrowTrendingUpIcon,
      href: '/analytics',
      color: 'purple',
      permission: 'data:read',
    },
    {
      title: 'Manage Users',
      description: 'Administer user accounts and permissions',
      icon: UserGroupIcon,
      href: '/users',
      color: 'orange',
      permission: 'users:manage',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-heading-xl mb-2">
          Welcome back, {authState.user?.full_name || authState.user?.username}!
        </h1>
        <p className="text-body-lg opacity-90">
          Oracle BI Publisher AI Assistant - Enterprise Dashboard
        </p>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-4">
            <ClockIcon className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-heading-sm mb-1">Response Time</h3>
          <p className="text-heading-lg text-blue-600">
            {metrics?.average_response_time.toFixed(2)}s
          </p>
          <p className="text-body-sm text-gray-600">Average response time</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-4">
            <ArrowTrendingUpIcon className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-heading-sm mb-1">Cache Hit Rate</h3>
          <p className="text-heading-lg text-green-600">
            {metrics?.cache_hit_rate.toFixed(1)}%
          </p>
          <p className="text-body-sm text-gray-600">Cache performance</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-4">
            <UserGroupIcon className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-heading-sm mb-1">Active Users</h3>
          <p className="text-heading-lg text-purple-600">{metrics?.active_users}</p>
          <p className="text-body-sm text-gray-600">Currently online</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-4">
            <ChartBarIcon className="w-6 h-6 text-orange-600" />
          </div>
          <h3 className="text-heading-sm mb-1">Total Requests</h3>
          <p className="text-heading-lg text-orange-600">
            {metrics?.total_requests.toLocaleString()}
          </p>
          <p className="text-body-sm text-gray-600">Since last reset</p>
        </Card>
      </div>

      {/* Usage Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-heading-md mb-4">Today's Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Report Generations</span>
              <span className="text-heading-sm font-semibold">
                {usage?.report_generations.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Query Executions</span>
              <span className="text-heading-sm font-semibold">
                {usage?.query_executions.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Data Exports</span>
              <span className="text-heading-sm font-semibold">
                {usage?.data_exports.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Unique Users</span>
              <span className="text-heading-sm font-semibold">
                {usage?.unique_users.toLocaleString()}
              </span>
            </div>
          </div>
        </Card>

        <Card>
          <h2 className="text-heading-md mb-4">System Health</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Database</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Healthy
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Cache System</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Operational
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">Oracle BI Publisher</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-body-md text-gray-600">API Gateway</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Available
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <h2 className="text-heading-md mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            if (!hasPermission(action.permission)) return null

            return (
              <Link
                key={action.title}
                to={action.href}
                className="group p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center mb-3">
                  <action.icon className="w-8 h-8 text-gray-600 group-hover:text-indigo-600 transition-colors" />
                </div>
                <h3 className="text-heading-sm mb-2 group-hover:text-indigo-600 transition-colors">
                  {action.title}
                </h3>
                <p className="text-body-sm text-gray-600">{action.description}</p>
              </Link>
            )
          })}
        </div>
      </Card>
    </div>
  )
}

export default Dashboard