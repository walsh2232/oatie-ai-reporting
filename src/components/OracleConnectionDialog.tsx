import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  Stepper,
  Step,
  StepLabel,
  Chip,
  CircularProgress,
  Divider,
  useTheme,
  Fade,
  Slide,
} from '@mui/material';
import {
  Close,
  Visibility,
  VisibilityOff,
  Storage,
  Security,
  CheckCircle,
  Info,
  NetworkCheck,
} from '@mui/icons-material';
import { type TransitionProps } from '@mui/material/transitions';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { OracleUtils, oracleProcessor } from '../utils/parallelProcessor';

// Oracle connection validation schema
const connectionSchema = yup.object({
  host: yup
    .string()
    .required('Host is required')
    .matches(
      /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/,
      'Please enter a valid hostname or IP address'
    ),
  port: yup
    .number()
    .required('Port is required')
    .min(1, 'Port must be greater than 0')
    .max(65535, 'Port must be less than 65536'),
  serviceName: yup
    .string()
    .required('Service name is required')
    .min(1, 'Service name cannot be empty'),
  username: yup
    .string()
    .required('Username is required')
    .min(1, 'Username cannot be empty'),
  password: yup
    .string()
    .required('Password is required')
    .min(1, 'Password cannot be empty'),
});

interface OracleConnectionData {
  host: string;
  port: number;
  serviceName: string;
  username: string;
  password: string;
}

interface OracleConnectionDialogProps {
  open: boolean;
  onClose: () => void;
  onConnect?: (connectionData: OracleConnectionData) => Promise<void>;
  title?: string;
}

// Slide transition for dialog
const SlideTransition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const OracleConnectionDialog: React.FC<OracleConnectionDialogProps> = ({
  open,
  onClose,
  onConnect,
  title = 'Connect to Oracle Database',
}) => {
  const theme = useTheme();
  const [showPassword, setShowPassword] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [connectionSuccess, setConnectionSuccess] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  const steps = ['Connection Details', 'Test Connection', 'Complete Setup'];

  const {
    control,
    formState: { errors, isValid },
    getValues,
    reset,
  } = useForm<OracleConnectionData>({
    resolver: yupResolver(connectionSchema),
    mode: 'onChange',
    defaultValues: {
      host: 'localhost',
      port: 1521,
      serviceName: 'ORCLPDB1',
      username: '',
      password: '',
    },
  });

  const handleClose = () => {
    reset();
    setActiveStep(0);
    setConnectionError(null);
    setConnectionSuccess(false);
    setTestResult(null);
    onClose();
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleNext = () => {
    if (activeStep === 0) {
      // Move to test connection step
      setActiveStep(1);
    } else if (activeStep === 1) {
      // Test connection and move to final step
      testConnection();
    } else {
      // Complete setup
      handleFinalConnect();
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    setConnectionError(null);
    setTestResult(null);
  };

  const testConnection = async () => {
    setIsConnecting(true);
    setConnectionError(null);

    try {
      const connectionData = getValues();
      
      // Simulate Oracle connection test using parallel processor
      const testTaskId = await OracleUtils.validateOracleData({
        type: 'connection_test',
        connection: connectionData,
      });

      // Wait for test result
      const checkResult = () => {
        const result = oracleProcessor.getTaskResult(testTaskId);
        if (result) {
          if (result.success) {
            setTestResult({
              success: true,
              latency: Math.random() * 100 + 50, // Mock latency
              version: '19c Enterprise Edition',
              schemas: ['HR', 'OE', 'PM', 'IX', 'SH'],
            });
            setActiveStep(2);
          } else {
            setConnectionError(result.error || 'Connection test failed');
          }
          setIsConnecting(false);
        } else {
          setTimeout(checkResult, 100);
        }
      };

      setTimeout(checkResult, 1000); // Start checking after 1 second
    } catch (err: any) {
      const errorMessage = err?.message || 'Connection test failed';
      setConnectionError(errorMessage);
      setIsConnecting(false);
    }
  };

  const handleFinalConnect = async () => {
    setIsConnecting(true);
    setConnectionError(null);

    try {
      const connectionData = getValues();
      
      if (onConnect) {
        await onConnect(connectionData);
      }
      
      setConnectionSuccess(true);
      
      // Close dialog after short delay
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err: any) {
      const errorMessage = err?.message || 'Failed to establish connection';
      setConnectionError(errorMessage);
    } finally {
      setIsConnecting(false);
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="body2" color="textSecondary" sx={{ marginBottom: 3 }}>
              Enter your Oracle database connection details below.
            </Typography>

            <Controller
              name="host"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Host"
                  placeholder="localhost or IP address"
                  error={!!errors.host}
                  helperText={errors.host?.message}
                  sx={{ marginBottom: 2 }}
                />
              )}
            />

            <Controller
              name="port"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Port"
                  type="number"
                  placeholder="1521"
                  error={!!errors.port}
                  helperText={errors.port?.message}
                  sx={{ marginBottom: 2 }}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || '')}
                />
              )}
            />

            <Controller
              name="serviceName"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Service Name"
                  placeholder="ORCLPDB1"
                  error={!!errors.serviceName}
                  helperText={errors.serviceName?.message}
                  sx={{ marginBottom: 2 }}
                />
              )}
            />

            <Controller
              name="username"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Username"
                  placeholder="Database username"
                  error={!!errors.username}
                  helperText={errors.username?.message}
                  sx={{ marginBottom: 2 }}
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
                  placeholder="Database password"
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={handleTogglePasswordVisibility} edge="end">
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              )}
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ textAlign: 'center', padding: 3 }}>
            {isConnecting ? (
              <Box>
                <CircularProgress size={60} sx={{ marginBottom: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Testing Oracle Connection...
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Please wait while we verify your connection details.
                </Typography>
              </Box>
            ) : testResult ? (
              <Fade in={true}>
                <Box>
                  <CheckCircle 
                    sx={{ 
                      fontSize: 60, 
                      color: theme.palette.success.main, 
                      marginBottom: 2 
                    }} 
                  />
                  <Typography variant="h6" gutterBottom color="success.main">
                    Connection Successful!
                  </Typography>
                  <Box sx={{ marginTop: 2 }}>
                    <Chip 
                      icon={<NetworkCheck />} 
                      label={`Latency: ${testResult.latency.toFixed(0)}ms`} 
                      sx={{ margin: 0.5 }}
                    />
                    <Chip 
                      icon={<Storage />} 
                      label={testResult.version} 
                      sx={{ margin: 0.5 }}
                    />
                    <Chip 
                      icon={<Security />} 
                      label={`${testResult.schemas.length} schemas available`} 
                      sx={{ margin: 0.5 }}
                    />
                  </Box>
                </Box>
              </Fade>
            ) : (
              <Box>
                <Info sx={{ fontSize: 60, color: theme.palette.primary.main, marginBottom: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Ready to Test Connection
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Click "Test Connection" to verify your Oracle database settings.
                </Typography>
              </Box>
            )}

            {connectionError && (
              <Alert severity="error" sx={{ marginTop: 2 }}>
                {connectionError}
              </Alert>
            )}
          </Box>
        );

      case 2:
        return (
          <Box sx={{ textAlign: 'center', padding: 3 }}>
            {connectionSuccess ? (
              <Fade in={true}>
                <Box>
                  <CheckCircle 
                    sx={{ 
                      fontSize: 60, 
                      color: theme.palette.success.main, 
                      marginBottom: 2 
                    }} 
                  />
                  <Typography variant="h6" gutterBottom color="success.main">
                    Connection Established!
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Your Oracle database connection is now active.
                  </Typography>
                </Box>
              </Fade>
            ) : (
              <Box>
                <Storage sx={{ fontSize: 60, color: theme.palette.primary.main, marginBottom: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Complete Setup
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ marginBottom: 2 }}>
                  Your connection test was successful. Click "Connect" to establish the connection.
                </Typography>
                
                {testResult && (
                  <Box sx={{ marginTop: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Connection Summary:
                    </Typography>
                    <Typography variant="body2">
                      Host: {getValues().host}:{getValues().port}
                    </Typography>
                    <Typography variant="body2">
                      Service: {getValues().serviceName}
                    </Typography>
                    <Typography variant="body2">
                      User: {getValues().username}
                    </Typography>
                  </Box>
                )}
              </Box>
            )}

            {connectionError && (
              <Alert severity="error" sx={{ marginTop: 2 }}>
                {connectionError}
              </Alert>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      TransitionComponent={SlideTransition}
      keepMounted={false}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Storage sx={{ marginRight: 1, color: theme.palette.primary.main }} />
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          </Box>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <Divider />

      <DialogContent>
        <Box sx={{ marginTop: 2 }}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ marginTop: 3 }}>
            {getStepContent(activeStep)}
          </Box>
        </Box>
      </DialogContent>

      <Divider />

      <DialogActions sx={{ padding: 2 }}>
        <Button
          onClick={handleClose}
          disabled={isConnecting}
        >
          Cancel
        </Button>
        
        {activeStep > 0 && (
          <Button
            onClick={handleBack}
            disabled={isConnecting}
          >
            Back
          </Button>
        )}
        
        <Button
          onClick={handleNext}
          variant="contained"
          disabled={
            (activeStep === 0 && !isValid) ||
            isConnecting ||
            connectionSuccess
          }
        >
          {isConnecting ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={16} color="inherit" />
              {activeStep === 1 ? 'Testing...' : 'Connecting...'}
            </Box>
          ) : activeStep === 0 ? (
            'Next'
          ) : activeStep === 1 ? (
            'Test Connection'
          ) : (
            'Connect'
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default OracleConnectionDialog;