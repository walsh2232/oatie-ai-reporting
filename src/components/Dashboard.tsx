import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Notifications,
  AccountCircle,
  Assessment,
  TrendingUp,
  Storage,
  Speed,
  Warning,
  CheckCircle,
  Error,
  Info,
} from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { oracleProcessor, OracleUtils } from '../utils/parallelProcessor';

// Mock Oracle BI data
const generateMockData = () => ({
  reportMetrics: [
    { name: 'Jan', reports: 24, queries: 156, users: 89 },
    { name: 'Feb', reports: 32, queries: 203, users: 112 },
    { name: 'Mar', reports: 45, queries: 287, users: 134 },
    { name: 'Apr', reports: 38, queries: 251, users: 118 },
    { name: 'May', reports: 52, queries: 324, users: 145 },
    { name: 'Jun', reports: 67, queries: 398, users: 167 },
  ],
  performanceData: [
    { name: 'Query Time', value: 85, status: 'good' },
    { name: 'Report Gen', value: 92, status: 'excellent' },
    { name: 'User Satisfaction', value: 78, status: 'good' },
    { name: 'System Load', value: 45, status: 'excellent' },
  ],
  statusDistribution: [
    { name: 'Active Reports', value: 234, color: '#22c55e' },
    { name: 'Pending', value: 45, color: '#f59e0b' },
    { name: 'Failed', value: 12, color: '#ef4444' },
    { name: 'Archived', value: 89, color: '#6b7280' },
  ],
});

interface DashboardProps {
  userName?: string;
  onLogout?: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ userName = 'Oracle User', onLogout }) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [dashboardData, setDashboardData] = useState(generateMockData());
  const [loading, setLoading] = useState(true);
  const [processingStatus, setProcessingStatus] = useState<any>(null);

  useEffect(() => {
    // Simulate loading Oracle BI data with parallel processing
    const loadDashboardData = async () => {
      setLoading(true);

      try {
        // Execute multiple Oracle queries in parallel
        const queries = [
          { queryId: 'reports_metrics', table: 'BI_REPORTS', mockData: dashboardData.reportMetrics },
          { queryId: 'performance_data', table: 'BI_PERFORMANCE', mockData: dashboardData.performanceData },
          { queryId: 'status_distribution', table: 'BI_STATUS', mockData: dashboardData.statusDistribution },
        ];

        const results = await OracleUtils.executeParallelQueries(queries);
        
        // Update dashboard with real data
        if (results.every(result => result.success)) {
          setDashboardData({
            reportMetrics: results[0].data?.data || dashboardData.reportMetrics,
            performanceData: results[1].data?.data || dashboardData.performanceData,
            statusDistribution: results[2].data?.data || dashboardData.statusDistribution,
          });
        }

        // Get processing status
        setProcessingStatus(oracleProcessor.getStatus());
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();

    // Update processing status every 5 seconds
    const statusInterval = setInterval(() => {
      setProcessingStatus(oracleProcessor.getStatus());
    }, 5000);

    return () => clearInterval(statusInterval);
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    if (onLogout) onLogout();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <CheckCircle sx={{ color: theme.palette.success.main }} />;
      case 'good':
        return <Info sx={{ color: theme.palette.primary.main }} />;
      case 'warning':
        return <Warning sx={{ color: theme.palette.warning.main }} />;
      case 'error':
        return <Error sx={{ color: theme.palette.error.main }} />;
      default:
        return <Info sx={{ color: theme.palette.grey[500] }} />;
    }
  };

  const getStatusColor = (value: number) => {
    if (value >= 90) return theme.palette.success.main;
    if (value >= 70) return theme.palette.primary.main;
    if (value >= 50) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: theme.palette.background.default }}>
      {/* Oracle App Bar */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <DashboardIcon sx={{ marginRight: theme.spacing(2) }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Oatie AI Reporting - Oracle BI Dashboard
          </Typography>
          
          {/* Processing Status Indicator */}
          {processingStatus && (
            <Chip
              icon={<Speed />}
              label={`${processingStatus.activeJobs} Active | ${processingStatus.queueSize} Queued`}
              variant="outlined"
              size="small"
              sx={{
                marginRight: theme.spacing(2),
                backgroundColor: alpha(theme.palette.background.paper, 0.1),
                color: theme.palette.text.primary,
                borderColor: alpha(theme.palette.text.primary, 0.3),
              }}
            />
          )}
          
          <IconButton color="inherit">
            <Badge badgeContent={4} color="error">
              <Notifications />
            </Badge>
          </IconButton>
          
          <IconButton
            onClick={handleMenuOpen}
            sx={{ marginLeft: theme.spacing(1) }}
          >
            <Avatar sx={{ width: 32, height: 32, backgroundColor: theme.palette.secondary.main }}>
              {userName.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <MenuItem onClick={handleMenuClose}>
              <AccountCircle sx={{ marginRight: theme.spacing(1) }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Loading State */}
      {loading && (
        <LinearProgress 
          sx={{ 
            height: 3,
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            '& .MuiLinearProgress-bar': {
              backgroundColor: theme.palette.primary.main,
            },
          }} 
        />
      )}

      {/* Dashboard Content */}
      <Box sx={{ padding: theme.spacing(3) }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, marginBottom: 3 }}>
          {/* Key Metrics Cards */}
          <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Total Reports
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                      234
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.palette.success.main }}>
                      +12.5% from last month
                    </Typography>
                  </Box>
                  <Assessment sx={{ fontSize: 48, color: theme.palette.primary.main, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Active Users
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                      167
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.palette.success.main }}>
                      +8.2% from last month
                    </Typography>
                  </Box>
                  <AccountCircle sx={{ fontSize: 48, color: theme.palette.secondary.main, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Query Performance
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                      85%
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.palette.warning.main }}>
                      -2.1% from last month
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 48, color: theme.palette.success.main, opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Data Storage
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                      2.4TB
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.palette.primary.main }}>
                      +15.3% from last month
                    </Typography>
                  </Box>
                  <Storage sx={{ fontSize: 48, color: theme.palette.grey[600], opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, marginBottom: 3 }}>
          {/* Report Metrics Chart */}
          <Box sx={{ flex: '2 1 600px', minWidth: '400px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div" gutterBottom sx={{ fontWeight: 600 }}>
                  Report Generation Trends
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={dashboardData.reportMetrics}>
                      <defs>
                        <linearGradient id="colorReports" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={theme.palette.secondary.main} stopOpacity={0.3}/>
                          <stop offset="95%" stopColor={theme.palette.secondary.main} stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.grey[300]} />
                      <XAxis dataKey="name" stroke={theme.palette.text.secondary} />
                      <YAxis stroke={theme.palette.text.secondary} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: theme.palette.background.paper, 
                          border: `1px solid ${theme.palette.grey[300]}`,
                          borderRadius: 8,
                        }} 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="reports" 
                        stroke={theme.palette.primary.main} 
                        fillOpacity={1} 
                        fill="url(#colorReports)" 
                        strokeWidth={2}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="queries" 
                        stroke={theme.palette.secondary.main} 
                        fillOpacity={1} 
                        fill="url(#colorQueries)" 
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Status Distribution */}
          <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div" gutterBottom sx={{ fontWeight: 600 }}>
                  Report Status Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={dashboardData.statusDistribution}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                      >
                        {dashboardData.statusDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Performance Metrics */}
        <Card>
          <CardContent>
            <Typography variant="h6" component="div" gutterBottom sx={{ fontWeight: 600 }}>
              System Performance Metrics
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
              {dashboardData.performanceData.map((metric, index) => (
                <Box key={index} sx={{ flex: '1 1 250px', minWidth: '200px' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {getStatusIcon(metric.status)}
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        {metric.name}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={metric.value}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: alpha(getStatusColor(metric.value), 0.2),
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getStatusColor(metric.value),
                            borderRadius: 4,
                          },
                        }}
                      />
                      <Typography variant="h6" sx={{ marginTop: 1, fontWeight: 600 }}>
                        {metric.value}%
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard;