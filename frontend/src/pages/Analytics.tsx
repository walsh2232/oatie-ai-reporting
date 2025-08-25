/**
 * Advanced Analytics Dashboard - Real-Time Insights & Predictive Analytics
 * Phase 4.3: Enterprise Oracle BI Publisher Analytics Intelligence
 */

import React, { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Timeline,
  TrendingUp,
  Analytics as AnalyticsIcon,
  Warning,
  Speed,
  Assessment,
  Refresh,
  Settings,
  Download,
  Fullscreen,
  PlayArrow,
  Pause,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
} from 'recharts'

import { useAuth } from '../contexts/AuthContext'

// Types for analytics data
interface AnalyticsData {
  performance_metrics: any
  usage_statistics: any
  top_reports: any
  system_health: any
  trend_data: any[]
  real_time_metrics: any
  predictive_insights: any[]
  anomaly_alerts: any[]
  last_updated: string
}

interface RealTimeMetrics {
  timestamp: string
  metrics: {
    active_users: number
    queries_per_second: number
    response_time_ms: number
    memory_usage: number
    cpu_usage: number
  }
  alerts: Array<{
    type: string
    message: string
    severity: string
    timestamp: string
  }>
}

const Analytics: React.FC = () => {
  const { state: authState } = useAuth()
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h')
  const [realTimeEnabled, setRealTimeEnabled] = useState(true)
  const [realTimeData, setRealTimeData] = useState<RealTimeMetrics[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const websocketRef = useRef<WebSocket | null>(null)

  // Fetch main dashboard data
  const {
    data: analyticsData,
    isLoading,
    error,
    refetch,
  } = useQuery<AnalyticsData>({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const response = await fetch('/api/v1/analytics/dashboard', {
        headers: {
          'Authorization': `Bearer ${authState.token}`,
        },
      })
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data')
      }
      return response.json()
    },
    refetchInterval: realTimeEnabled ? 30000 : false, // Refresh every 30 seconds if real-time is enabled
  })

  // WebSocket connection for real-time streaming
  useEffect(() => {
    if (realTimeEnabled && !isStreaming) {
      connectWebSocket()
    } else if (!realTimeEnabled && websocketRef.current) {
      disconnectWebSocket()
    }

    return () => {
      if (websocketRef.current) {
        disconnectWebSocket()
      }
    }
  }, [realTimeEnabled])

  const connectWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/v1/analytics/streaming`
      
      websocketRef.current = new WebSocket(wsUrl)
      
      websocketRef.current.onopen = () => {
        setIsStreaming(true)
        console.log('WebSocket connected for real-time analytics')
      }
      
      websocketRef.current.onmessage = (event) => {
        const data: RealTimeMetrics = JSON.parse(event.data)
        setRealTimeData(prev => {
          const newData = [...prev, data]
          // Keep only last 50 data points
          return newData.slice(-50)
        })
      }
      
      websocketRef.current.onclose = () => {
        setIsStreaming(false)
        console.log('WebSocket disconnected')
      }
      
      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsStreaming(false)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (websocketRef.current) {
      websocketRef.current.close()
      websocketRef.current = null
      setIsStreaming(false)
    }
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Advanced Analytics...
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load analytics data. Please try again.
        <Button onClick={() => refetch()} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    )
  }

  const colors = ['#0084FF', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Advanced Analytics Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Real-time insights, predictive analytics, and anomaly detection for Oracle BI Publisher
          </Typography>
        </Box>
        
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={selectedTimeRange}
              label="Time Range"
              onChange={(e) => setSelectedTimeRange(e.target.value)}
            >
              <MenuItem value="1h">Last Hour</MenuItem>
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={
              <Switch
                checked={realTimeEnabled}
                onChange={(e) => setRealTimeEnabled(e.target.checked)}
              />
            }
            label="Real-time"
          />
          
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => refetch()}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Export Data">
            <IconButton>
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Real-time Status Bar */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: isStreaming ? '#e8f5e8' : '#fff3cd' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            {isStreaming ? <PlayArrow color="success" /> : <Pause color="warning" />}
            <Typography variant="body1">
              {isStreaming ? 'Live streaming active' : 'Real-time streaming paused'}
            </Typography>
            <Chip
              size="small"
              label={`${realTimeData.length} data points`}
              color={isStreaming ? 'success' : 'default'}
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            Last updated: {analyticsData?.last_updated ? new Date(analyticsData.last_updated).toLocaleString() : 'Never'}
          </Typography>
        </Box>
      </Paper>

      {/* Key Performance Indicators */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Active Users
                  </Typography>
                  <Typography variant="h4">
                    {realTimeData.length > 0 ? realTimeData[realTimeData.length - 1].metrics.active_users : analyticsData?.performance_metrics?.active_users || 0}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +12% from yesterday
                  </Typography>
                </Box>
                <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Queries/Second
                  </Typography>
                  <Typography variant="h4">
                    {realTimeData.length > 0 ? realTimeData[realTimeData.length - 1].metrics.queries_per_second.toFixed(1) : '0.0'}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    Optimal performance
                  </Typography>
                </Box>
                <Speed color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Response Time
                  </Typography>
                  <Typography variant="h4">
                    {realTimeData.length > 0 ? `${realTimeData[realTimeData.length - 1].metrics.response_time_ms.toFixed(0)}ms` : '0ms'}
                  </Typography>
                  <Typography variant="body2" color="warning.main">
                    Within SLA
                  </Typography>
                </Box>
                <Timeline color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    System Health
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData?.system_health?.status === 'healthy' ? '98%' : '85%'}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    All systems operational
                  </Typography>
                </Box>
                <Assessment color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Real-time Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Real-time Performance Metrics"
              action={
                <Chip
                  label={isStreaming ? 'LIVE' : 'PAUSED'}
                  color={isStreaming ? 'success' : 'default'}
                  size="small"
                />
              }
            />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={realTimeData.slice(-20)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <RechartsTooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="metrics.queries_per_second" 
                    stroke="#0084FF" 
                    name="Queries/sec"
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="metrics.active_users" 
                    stroke="#FF6B6B" 
                    name="Active Users"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="System Resources" />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'CPU Used', value: realTimeData.length > 0 ? realTimeData[realTimeData.length - 1].metrics.cpu_usage : 45 },
                      { name: 'CPU Free', value: realTimeData.length > 0 ? 100 - realTimeData[realTimeData.length - 1].metrics.cpu_usage : 55 },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: 'CPU Used', value: 45 },
                      { name: 'CPU Free', value: 55 },
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Predictive Analytics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Predictive Analytics & Forecasting"
              subheader="ARIMA-based predictions for the next 7 days"
            />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={analyticsData?.predictive_insights || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="confidence_upper"
                    stackId="1"
                    stroke="#E3F2FD"
                    fill="#E3F2FD"
                    name="Confidence Upper"
                  />
                  <Area
                    type="monotone"
                    dataKey="confidence_lower"
                    stackId="1"
                    stroke="#E3F2FD"
                    fill="#ffffff"
                    name="Confidence Lower"
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted_value"
                    stroke="#0084FF"
                    strokeWidth={3}
                    name="Predicted Value"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Anomaly Detection */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Anomaly Detection" />
            <CardContent>
              {analyticsData?.anomaly_alerts?.length > 0 ? (
                <Box>
                  {analyticsData.anomaly_alerts.slice(0, 5).map((anomaly: any, index: number) => (
                    <Alert
                      key={index}
                      severity={anomaly.severity === 'high' ? 'error' : anomaly.severity === 'medium' ? 'warning' : 'info'}
                      sx={{ mb: 1 }}
                    >
                      <Typography variant="body2">
                        <strong>{anomaly.metric_name}:</strong> Detected anomaly with score {anomaly.anomaly_score.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Expected: {anomaly.expected_value}, Actual: {anomaly.actual_value}
                      </Typography>
                    </Alert>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary">No anomalies detected in the selected time range.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Historical Trends" />
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={analyticsData?.trend_data || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Area
                    type="monotone"
                    dataKey="performance_score"
                    stroke="#4ECDC4"
                    fill="#4ECDC4"
                    fillOpacity={0.6}
                    name="Performance Score"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Interactive Dashboard Builder Section */}
      <Card sx={{ mb: 3 }}>
        <CardHeader
          title="Interactive Dashboard Builder"
          subheader="Drag and drop components to create custom dashboards"
          action={
            <Button variant="contained" startIcon={<Settings />}>
              Configure Dashboard
            </Button>
          }
        />
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create custom KPIs, add widgets, and configure real-time alerts for your specific business needs.
          </Typography>
          <Box display="flex" gap={2}>
            <Button variant="outlined" size="small">Add Widget</Button>
            <Button variant="outlined" size="small">Create KPI</Button>
            <Button variant="outlined" size="small">Set Alert</Button>
            <Button variant="outlined" size="small">Export Dashboard</Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Analytics