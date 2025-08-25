import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  CircularProgress,
  Divider,
  Link,
  useTheme,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Lock,
  Person,
  Security,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Oracle authentication validation schema
const loginSchema = yup.object({
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain uppercase, lowercase, number, and special character'
    ),
});

interface LoginFormData {
  username: string;
  password: string;
}

interface LoginFormProps {
  onLogin?: (credentials: LoginFormData) => Promise<void>;
  loading?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, loading = false }) => {
  const theme = useTheme();
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
    mode: 'onChange',
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    setLoginError(null);

    try {
      if (onLogin) {
        await onLogin(data);
      } else {
        // Mock Oracle authentication
        await new Promise((resolve, reject) => {
          setTimeout(() => {
            if (data.username === 'oracle_user' && data.password === 'Oracle123!') {
              resolve(true);
            } else {
              reject(new Error('Invalid Oracle credentials'));
            }
          }, 1500);
        });
      }
      
      // Success - form will be handled by parent component
      reset();
    } catch (error) {
      setLoginError(
        error instanceof Error 
          ? error.message 
          : 'Authentication failed. Please check your Oracle credentials.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `linear-gradient(135deg, ${theme.palette.primary.light}15 0%, ${theme.palette.secondary.light}15 100%)`,
        padding: theme.spacing(2),
      }}
    >
      <Card
        sx={{
          width: '100%',
          maxWidth: 420,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          border: `1px solid ${theme.palette.grey[200]}`,
        }}
      >
        <CardContent sx={{ padding: theme.spacing(4) }}>
          {/* Oracle Branding Header */}
          <Box sx={{ textAlign: 'center', marginBottom: theme.spacing(4) }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: theme.spacing(2),
              }}
            >
              <Security
                sx={{
                  fontSize: 48,
                  color: theme.palette.primary.main,
                  marginRight: theme.spacing(1),
                }}
              />
              <Typography
                variant="h4"
                component="h1"
                sx={{
                  fontWeight: 700,
                  color: theme.palette.primary.main,
                  fontFamily: theme.typography.fontFamily,
                }}
              >
                Oracle
              </Typography>
            </Box>
            <Typography
              variant="h6"
              sx={{
                color: theme.palette.text.secondary,
                fontWeight: 500,
                marginBottom: theme.spacing(1),
              }}
            >
              Oatie AI Reporting
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: theme.palette.text.secondary,
              }}
            >
              Sign in to your Oracle BI Publisher account
            </Typography>
          </Box>

          {/* Error Alert */}
          {loginError && (
            <Alert
              severity="error"
              sx={{
                marginBottom: theme.spacing(3),
                borderRadius: 2,
              }}
              onClose={() => setLoginError(null)}
            >
              {loginError}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            <Controller
              name="username"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Username"
                  placeholder="Enter your Oracle username"
                  error={!!errors.username}
                  helperText={errors.username?.message}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    marginBottom: theme.spacing(3),
                  }}
                  disabled={isSubmitting || loading}
                />
              )}
            />

            <Controller
              name="password"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your Oracle password"
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleTogglePasswordVisibility}
                          edge="end"
                          aria-label="toggle password visibility"
                          disabled={isSubmitting || loading}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    marginBottom: theme.spacing(4),
                  }}
                  disabled={isSubmitting || loading}
                />
              )}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={!isValid || isSubmitting || loading}
              sx={{
                height: 56,
                marginBottom: theme.spacing(3),
                fontSize: '1rem',
                fontWeight: 600,
              }}
            >
              {isSubmitting || loading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} color="inherit" />
                  Signing In...
                </Box>
              ) : (
                'Sign In to Oracle'
              )}
            </Button>

            <Divider sx={{ marginY: theme.spacing(3) }}>
              <Typography variant="body2" color="text.secondary">
                Oracle BI Publisher
              </Typography>
            </Divider>

            {/* Additional Oracle Links */}
            <Box sx={{ textAlign: 'center' }}>
              <Link
                href="#"
                variant="body2"
                sx={{
                  color: theme.palette.primary.main,
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Forgot your password?
              </Link>
              <Typography
                variant="body2"
                sx={{
                  color: theme.palette.text.secondary,
                  marginTop: theme.spacing(2),
                }}
              >
                Need help accessing your Oracle account?{' '}
                <Link
                  href="#"
                  sx={{
                    color: theme.palette.primary.main,
                    textDecoration: 'none',
                    fontWeight: 500,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Contact Support
                </Link>
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginForm;