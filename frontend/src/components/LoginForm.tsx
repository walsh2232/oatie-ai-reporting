import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Container,
  Paper,
  Avatar,
  Link,
  Divider
} from '@mui/material';
import { LockOutlined, Visibility, VisibilityOff, Business } from '@mui/icons-material';
import { IconButton, InputAdornment } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { LoginCredentials } from '../types/auth';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const { login, isLoading, error } = useAuth();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!credentials.username) {
      errors.username = 'Username is required';
    } else if (!/\S+@\S+\.\S+/.test(credentials.username)) {
      errors.username = 'Please enter a valid email address';
    }
    
    if (!credentials.password) {
      errors.password = 'Password is required';
    } else if (credentials.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await login(credentials);
      onSuccess?.();
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleInputChange = (field: keyof LoginCredentials) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCredentials(prev => ({
      ...prev,
      [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value
    }));
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'background.default',
          padding: 2,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: 2,
            width: '100%',
            maxWidth: 400,
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Avatar 
            sx={{ 
              m: 1, 
              bgcolor: 'primary.main',
              width: 56, 
              height: 56,
            }}
          >
            <LockOutlined fontSize="large" />
          </Avatar>

          <Typography 
            component="h1" 
            variant="h4" 
            sx={{ 
              mb: 1,
              fontWeight: 600,
              color: 'primary.main',
              textAlign: 'center',
            }}
          >
            Welcome to Oatie
          </Typography>

          <Typography 
            variant="body2" 
            sx={{ 
              mb: 3,
              color: 'text.secondary',
              textAlign: 'center',
              maxWidth: 320,
            }}
          >
            Transform your Oracle BI Publisher reporting with AI-powered SQL generation
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Email Address"
              name="username"
              autoComplete="email"
              autoFocus
              value={credentials.username}
              onChange={handleInputChange('username')}
              error={!!validationErrors.username}
              helperText={validationErrors.username}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'background.paper',
                  '&:hover': {
                    borderColor: 'primary.light',
                  },
                  '&.Mui-focused': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={credentials.password}
              onChange={handleInputChange('password')}
              error={!!validationErrors.password}
              helperText={validationErrors.password}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      sx={{ color: 'primary.main' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'background.paper',
                  '&:hover': {
                    borderColor: 'primary.light',
                  },
                  '&.Mui-focused': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />

            <FormControlLabel
              control={
                <Checkbox 
                  checked={credentials.rememberMe}
                  onChange={handleInputChange('rememberMe')}
                  color="primary"
                />
              }
              label="Remember me"
              sx={{ mt: 1, mb: 2 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isLoading}
              sx={{
                mt: 3,
                mb: 2,
                height: 48,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
              }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>

            <Divider sx={{ my: 2 }}>
              <Typography variant="body2" color="text.secondary">
                OR
              </Typography>
            </Divider>

            <Box sx={{ textAlign: 'center' }}>
              <Link href="#" variant="body2" color="primary">
                Forgot your password?
              </Link>
            </Box>

            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Don't have an account?{' '}
                <Link href="#" color="primary">
                  Contact your administrator
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Powered by AI • Oracle BI Publisher Integration
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};
