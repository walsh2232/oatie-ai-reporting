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
import { oracleOCIColors, oracleOCILayout, oracleTypography } from '../themes/oracleRedwoodTheme';

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
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!credentials.username || !credentials.password) {
      setLocalError('Please enter both username and password');
      return;
    }

    try {
      await login(credentials);
      onSuccess?.();
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Login failed');
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
          backgroundColor: oracleOCIColors.console.background,
          padding: oracleOCILayout.spacing / 8, // Convert to Material-UI spacing units
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: oracleOCILayout.spacing / 8 * 4, // Use Oracle spacing system
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: oracleOCILayout.borderRadius * 2,
            width: '100%',
            maxWidth: oracleOCILayout.containerWidth * 2, // Use Oracle container width
            backgroundColor: oracleOCIColors.console.panelBackground,
            border: `1px solid ${oracleOCIColors.neutral.gray30}`,
          }}
        >
          <Avatar 
            sx={{ 
              m: 1, 
              bgcolor: `rgb(${oracleOCIColors.brand.primary})`,
              width: oracleOCILayout.iconSize + 16, 
              height: oracleOCILayout.iconSize + 16,
            }}
          >
            <LockOutlined fontSize="large" />
          </Avatar>
          
          <Typography 
            component="h1" 
            variant="h4" 
            sx={{ 
              mb: 1, 
              fontWeight: oracleTypography.weights.bold, 
              color: `rgb(${oracleOCIColors.brand.primary})`,
              fontFamily: oracleTypography.fontFamily,
            }}
          >
            Oatie
          </Typography>
          
          <Typography 
            component="h2" 
            variant="h6" 
            sx={{ 
              mb: 3, 
              color: oracleOCIColors.neutral.gray70, 
              textAlign: 'center',
              fontFamily: oracleTypography.fontFamily,
            }}
          >
            Oracle BI Publisher AI Assistant
          </Typography>

          {(error || localError) && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error || localError}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={credentials.username}
              onChange={handleInputChange('username')}
              disabled={isLoading}
              sx={{ mb: 2 }}
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
              disabled={isLoading}
              sx={{ 
                mb: 2,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: oracleOCIColors.console.background,
                  '& fieldset': {
                    borderColor: oracleOCIColors.neutral.gray40,
                  },
                  '&:hover fieldset': {
                    borderColor: `rgb(${oracleOCIColors.brand.primary})`,
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: `rgb(${oracleOCIColors.brand.primary})`,
                  },
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      sx={{ color: `rgb(${oracleOCIColors.brand.primary})` }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={credentials.rememberMe}
                  onChange={handleInputChange('rememberMe')}
                  disabled={isLoading}
                  sx={{ 
                    color: `rgb(${oracleOCIColors.brand.primary})`,
                    '&.Mui-checked': {
                      color: `rgb(${oracleOCIColors.brand.primary})`,
                    },
                  }}
                />
              }
              label="Remember me"
              sx={{ 
                mb: 2,
                color: oracleOCIColors.neutral.gray70,
                fontFamily: oracleTypography.fontFamily,
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 2, 
                mb: 2, 
                py: 1.5,
                fontSize: oracleTypography.sizes.base,
                fontWeight: oracleTypography.weights.medium,
                fontFamily: oracleTypography.fontFamily,
                backgroundColor: `rgb(${oracleOCIColors.brand.primary})`,
                minHeight: oracleOCILayout.iconSize,
                borderRadius: oracleOCILayout.borderRadius,
                textTransform: 'none',
                '&:hover': {
                  backgroundColor: `rgb(${oracleOCIColors.brand.dark})`,
                },
                '&:disabled': {
                  backgroundColor: oracleOCIColors.neutral.gray50,
                },
              }}
              }}
              disabled={isLoading}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Demo Credentials: admin / admin
              </Typography>
            </Box>
          </Box>
        </Paper>

        <Typography variant="body2" color="rgba(255,255,255,0.8)" sx={{ mt: 3, textAlign: 'center' }}>
          Transform your Oracle BI Publisher reporting with AI-powered SQL generation
        </Typography>
      </Box>
    </Container>
  );
};
