import React from 'react';
import { useQuery } from 'react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Database,
  Clock,
  CheckCircle,
  AlertCircle,
  Activity
} from 'lucide-react';
import ApiService from '../services/api';
import { DashboardCard } from '../types';
import { clsx } from 'clsx';

const Dashboard: React.FC = () => {
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    'analytics-dashboard',
    ApiService.getAnalyticsDashboard,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: performanceData, isLoading: performanceLoading } = useQuery(
    'performance-metrics',
    ApiService.getPerformanceMetrics,
    { refetchInterval: 15000 } // Refresh every 15 seconds
  );

  // Mock data for charts (in real app, this would come from API)
  const queryVolumeData = [
    { name: 'Mon', queries: 120, reports: 45 },
    { name: 'Tue', queries: 165, reports: 62 },
    { name: 'Wed', queries: 142, reports: 38 },
    { name: 'Thu', queries: 198, reports: 71 },
    { name: 'Fri', queries: 234, reports: 89 },
    { name: 'Sat', queries: 87, reports: 23 },
    { name: 'Sun', queries: 156, reports: 34 },
  ];

  const responseTimeData = [
    { time: '00:00', response_time: 1.2 },
    { time: '04:00', response_time: 0.8 },
    { time: '08:00', response_time: 2.1 },
    { time: '12:00', response_time: 2.8 },
    { time: '16:00', response_time: 1.9 },
    { time: '20:00', response_time: 1.5 },
  ];

  const queryTypeData = [
    { name: 'SELECT', value: 68, color: '#ED6C02' },
    { name: 'Reports', value: 22, color: '#FFB000' },
    { name: 'Analytics', value: 7, color: '#A76914' },
    { name: 'Other', value: 3, color: '#522916' },
  ];

  const dashboardCards: DashboardCard[] = [
    {
      id: 'total-queries',
      title: 'Total Queries Today',
      value: analyticsData?.user_activity.queries_today || 0,
      change: { value: 12, trend: 'up' },
      icon: 'database',
      color: 'blue'
    },
    {
      id: 'active-users',
      title: 'Active Users',
      value: analyticsData?.user_activity.active_users || 0,
      change: { value: 8, trend: 'up' },
      icon: 'users',
      color: 'green'
    },
    {
      id: 'avg-response',
      title: 'Avg Response Time',
      value: analyticsData?.query_performance.avg_execution_time || '0s',
      change: { value: -5, trend: 'down' },
      icon: 'clock',
      color: 'orange'
    },
    {
      id: 'success-rate',
      title: 'Success Rate',
      value: analyticsData?.query_performance.success_rate || '0%',
      change: { value: 2, trend: 'up' },
      icon: 'check',
      color: 'green'
    },
  ];

  const getCardIcon = (iconName: string) => {
    const icons = {
      database: Database,
      users: Users,
      clock: Clock,
      check: CheckCircle,
    };
    return icons[iconName as keyof typeof icons] || Activity;
  };

  const getCardColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      orange: 'bg-orange-500',
      red: 'bg-red-500',
      purple: 'bg-purple-500',
    };
    return colors[color as keyof typeof colors] || 'bg-gray-500';
  };

  if (analyticsLoading || performanceLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="redwood-spinner w-8 h-8"></div>
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Real-time insights into your Oracle BI Publisher AI Assistant performance
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {dashboardCards.map((card) => {
          const Icon = getCardIcon(card.icon || 'activity');
          return (
            <div key={card.id} className="redwood-card hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{card.value}</p>
                  {card.change && (
                    <div className="flex items-center mt-1">
                      {card.change.trend === 'up' ? (
                        <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
                      )}
                      <span
                        className={clsx(
                          'text-sm font-medium',
                          card.change.trend === 'up' ? 'text-green-600' : 'text-red-600'
                        )}
                      >
                        {Math.abs(card.change.value)}%
                      </span>
                      <span className="text-sm text-gray-500 ml-1">vs yesterday</span>
                    </div>
                  )}
                </div>
                <div className={clsx('p-3 rounded-lg', getCardColorClasses(card.color || 'gray'))}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Query Volume Chart */}
        <div className="redwood-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Query Volume & Reports
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={queryVolumeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip />
              <Bar dataKey="queries" fill="#ED6C02" name="Queries" />
              <Bar dataKey="reports" fill="#FFB000" name="Reports" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Response Time Chart */}
        <div className="redwood-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Response Time (24h)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="response_time"
                stroke="#ED6C02"
                fill="#ED6C02"
                fillOpacity={0.2}
                name="Response Time (s)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Query Types Distribution */}
        <div className="redwood-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Query Types Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={queryTypeData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {queryTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* System Health */}
        <div className="redwood-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">CPU Usage</span>
                <span className="text-sm text-gray-600">
                  {analyticsData?.system_health.cpu_usage || '0%'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full"
                  style={{ width: analyticsData?.system_health.cpu_usage || '0%' }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Memory Usage</span>
                <span className="text-sm text-gray-600">
                  {analyticsData?.system_health.memory_usage || '0%'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: analyticsData?.system_health.memory_usage || '0%' }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Cache Hit Rate</span>
                <span className="text-sm text-gray-600">
                  {analyticsData?.query_performance.cache_hit_rate || '0%'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: analyticsData?.query_performance.cache_hit_rate || '0%' }}
                ></div>
              </div>
            </div>

            <div className="pt-2 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Database Connections</span>
                <span className="text-sm text-gray-600">
                  {analyticsData?.system_health.database_connections || '0/0'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Popular Queries */}
      <div className="redwood-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Queries</h3>
        <div className="space-y-3">
          {analyticsData?.popular_queries.map((query, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">{query.query}</span>
              <span className="text-sm font-medium text-gray-900">{query.usage_count} uses</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;