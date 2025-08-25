import { useState } from 'react';
import { ThemeProvider, CssBaseline, Fab } from '@mui/material';
import { Settings } from '@mui/icons-material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import oracleRedwoodTheme from './theme/oracleRedwoodTheme';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import OracleConnectionDialog from './components/OracleConnectionDialog';

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

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [connectionDialogOpen, setConnectionDialogOpen] = useState(false);

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
            <Dashboard userName={user.username} onLogout={handleLogout} />
            
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
