import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Add,
  Storage,
  CheckCircle,
  Error,
  Settings,
  Code,
  Analytics,
  Speed
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { OracleConnectionDialog } from './OracleConnectionDialog';
import { QueryInterface } from './QueryInterface';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [connectionDialogOpen, setConnectionDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'query' | 'connections' | 'analytics'>('query');

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
  };

  const getConnectionStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'success';
      case 'disconnected': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getConnectionStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle />;
      case 'error': return <Error />;
      default: return <Storage />;
    }
  };

  const activeConnection = user?.oracleConnections?.find(conn => conn.isActive);

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f5f7fa' }}>
      {/* Top Navigation */}
      <AppBar 
        position="static" 
        sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}
      >
        <Toolbar>
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Oatie Dashboard
          </Typography>
          
          {activeConnection && (
            <Chip
              icon={getConnectionStatusIcon(activeConnection.status)}
              label={`${activeConnection.name} (${activeConnection.status})`}
              color={getConnectionStatusColor(activeConnection.status) as any}
              variant="outlined"
              sx={{ mr: 2, backgroundColor: 'rgba(255,255,255,0.1)', color: 'white' }}
            />
          )}

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body1" sx={{ mr: 1 }}>
              {user?.fullName}
            </Typography>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>
                <Settings sx={{ mr: 1 }} /> Profile
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} /> Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Tab Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', backgroundColor: 'white' }}>
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', gap: 1, py: 1 }}>
            <Button
              variant={activeTab === 'query' ? 'contained' : 'text'}
              startIcon={<Code />}
              onClick={() => setActiveTab('query')}
              sx={{ borderRadius: 2 }}
            >
              SQL Query
            </Button>
            <Button
              variant={activeTab === 'connections' ? 'contained' : 'text'}
              startIcon={<Storage />}
              onClick={() => setActiveTab('connections')}
              sx={{ borderRadius: 2 }}
            >
              Connections
            </Button>
            <Button
              variant={activeTab === 'analytics' ? 'contained' : 'text'}
              startIcon={<Analytics />}
              onClick={() => setActiveTab('analytics')}
              sx={{ borderRadius: 2 }}
            >
              Analytics
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {activeTab === 'query' && (
          <QueryInterface />
        )}

        {activeTab === 'connections' && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#333' }}>
                Oracle Connections
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setConnectionDialogOpen(true)}
                sx={{ 
                  borderRadius: 2,
                  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                }}
              >
                Add Connection
              </Button>
            </Box>

            <Grid container spacing={3}>
              {user?.oracleConnections?.map((connection) => (
                <Grid item xs={12} md={6} lg={4} key={connection.id}>
                  <Card 
                    sx={{ 
                      height: '100%',
                      borderRadius: 3,
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      border: connection.isActive ? '2px solid #667eea' : '1px solid #e0e0e0',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 30px rgba(0,0,0,0.15)'
                      }
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        {getConnectionStatusIcon(connection.status)}
                        <Typography variant="h6" sx={{ ml: 1, fontWeight: 'bold' }}>
                          {connection.name}
                        </Typography>
                        {connection.isActive && (
                          <Chip
                            label="Active"
                            size="small"
                            color="primary"
                            sx={{ ml: 'auto' }}
                          />
                        )}
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Host:</strong> {connection.host}:{connection.port}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Service:</strong> {connection.serviceName}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Username:</strong> {connection.username}
                      </Typography>
                      {connection.lastConnected && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Last Connected:</strong> {connection.lastConnected.toLocaleString()}
                        </Typography>
                      )}
                    </CardContent>
                    <CardActions>
                      <Button size="small" color="primary">
                        Test Connection
                      </Button>
                      <Button size="small" color="secondary">
                        Edit
                      </Button>
                      <Button size="small" color="error">
                        Remove
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}

              {(!user?.oracleConnections || user.oracleConnections.length === 0) && (
                <Grid item xs={12}>
                  <Card sx={{ textAlign: 'center', py: 6, borderRadius: 3 }}>
                    <CardContent>
                      <Storage sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
                      <Typography variant="h5" sx={{ mb: 2, color: '#666' }}>
                        No Oracle Connections
                      </Typography>
                      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                        Add your first Oracle database connection to start generating SQL queries
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={() => setConnectionDialogOpen(true)}
                        size="large"
                        sx={{ borderRadius: 2 }}
                      >
                        Add Connection
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Box>
        )}

        {activeTab === 'analytics' && (
          <Box>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold', color: '#333' }}>
              Query Analytics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, textAlign: 'center', p: 3 }}>
                  <Speed sx={{ fontSize: 48, color: '#667eea', mb: 2 }} />
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#333' }}>
                    127
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Queries Generated
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, textAlign: 'center', p: 3 }}>
                  <CheckCircle sx={{ fontSize: 48, color: '#4caf50', mb: 2 }} />
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#333' }}>
                    98.2%
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Success Rate
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, textAlign: 'center', p: 3 }}>
                  <Analytics sx={{ fontSize: 48, color: '#ff9800', mb: 2 }} />
                  <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#333' }}>
                    2.3s
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Avg Response Time
                  </Typography>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Container>

      {/* Floating Action Button */}
      {activeTab === 'connections' && (
        <Fab
          color="primary"
          aria-label="add connection"
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
          }}
          onClick={() => setConnectionDialogOpen(true)}
        >
          <Add />
        </Fab>
      )}

      {/* Oracle Connection Dialog */}
      <OracleConnectionDialog
        open={connectionDialogOpen}
        onClose={() => setConnectionDialogOpen(false)}
      />
    </Box>
  );
};
