import { useState } from 'react';
import { 
  ThemeProvider, 
  CssBaseline, 
  Fab, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box,
  Container,
  Tabs,
  Tab
} from '@mui/material';
import { 
  Settings, 
  Dashboard as DashboardIcon, 
  Psychology,
  Logout
} from '@mui/icons-material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import oracleRedwoodTheme from './theme/oracleRedwoodTheme';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import OracleConnectionDialog from './components/OracleConnectionDialog';
import NLPSQLInterface from './components/NLPSQLInterface';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

interface User {
  username: string;
  authenticated: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 0 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [connectionDialogOpen, setConnectionDialogOpen] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);

  const handleLogin = async (credentials: { username: string; password: string }) => {
    // Simulate Oracle authentication
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setUser({
      username: credentials.username,
      authenticated: true,
    });
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentTab(0);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleOpenConnectionDialog = () => {
    setConnectionDialogOpen(true);
  };

  const handleCloseConnectionDialog = () => {
    setConnectionDialogOpen(false);
  };

  const handleConnect = async (connectionData: { host: string; port: number; serviceName: string; username: string; password: string }) => {
    // Simulate Oracle connection establishment
    console.log('Connecting to Oracle:', connectionData);
    await new Promise(resolve => setTimeout(resolve, 2000));
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={oracleRedwoodTheme}>
        <CssBaseline />
        
        {!user?.authenticated ? (
          <LoginForm onLogin={handleLogin} />
        ) : (
          <>
            {/* App Bar */}
            <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'primary.main' }}>
              <Toolbar>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                  Oatie AI Reporting Platform
                </Typography>
                <Typography variant="body2" sx={{ mr: 2, opacity: 0.9 }}>
                  Welcome, {user.username}
                </Typography>
                <Button
                  color="inherit"
                  onClick={handleLogout}
                  startIcon={<Logout />}
                  sx={{ textTransform: 'none' }}
                >
                  Logout
                </Button>
              </Toolbar>
              
              {/* Navigation Tabs */}
              <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
                <Container maxWidth="xl">
                  <Tabs 
                    value={currentTab} 
                    onChange={handleTabChange}
                    aria-label="Navigation tabs"
                    sx={{
                      '& .MuiTab-root': {
                        textTransform: 'none',
                        fontWeight: 500,
                        minHeight: 48,
                      }
                    }}
                  >
                    <Tab 
                      icon={<DashboardIcon />} 
                      label="Dashboard" 
                      iconPosition="start"
                      sx={{ minHeight: 48 }}
                    />
                    <Tab 
                      icon={<Psychology />} 
                      label="NLP to SQL" 
                      iconPosition="start"
                      sx={{ minHeight: 48 }}
                    />
                  </Tabs>
                </Container>
              </Box>
            </AppBar>

            {/* Main Content */}
            <Container maxWidth="xl" sx={{ py: 3, minHeight: 'calc(100vh - 120px)' }}>
              <TabPanel value={currentTab} index={0}>
                <Dashboard userName={user.username} onLogout={handleLogout} />
              </TabPanel>
              <TabPanel value={currentTab} index={1}>
                <NLPSQLInterface />
              </TabPanel>
            </Container>
            
            {/* Floating Action Button for Oracle Connection Settings */}
            <Fab
              color="primary"
              aria-label="Oracle connection settings"
              sx={{
                position: 'fixed',
                bottom: 24,
                right: 24,
                zIndex: 1000,
              }}
              onClick={handleOpenConnectionDialog}
            >
              <Settings />
            </Fab>

            {/* Oracle Connection Dialog */}
            <OracleConnectionDialog
              open={connectionDialogOpen}
              onClose={handleCloseConnectionDialog}
              onConnect={handleConnect}
            />
          </>
        )}
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
