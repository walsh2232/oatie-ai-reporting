import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  Box,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
  Typography,
  IconButton,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { Close, TestTube, CheckCircle, Error } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { OracleConnectionForm } from '../types/auth';

interface OracleConnectionDialogProps {
  open: boolean;
  onClose: () => void;
}

export const OracleConnectionDialog: React.FC<OracleConnectionDialogProps> = ({
  open,
  onClose
}) => {
  const { addOracleConnection, testOracleConnection, isLoading } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [connectionForm, setConnectionForm] = useState<OracleConnectionForm>({
    name: '',
    host: '',
    port: 1521,
    serviceName: '',
    username: '',
    password: '',
    testConnection: true
  });
  const [testResult, setTestResult] = useState<{
    status: 'idle' | 'testing' | 'success' | 'error';
    message?: string;
  }>({ status: 'idle' });
  const [formError, setFormError] = useState<string | null>(null);

  const steps = ['Connection Details', 'Test Connection', 'Save'];

  const handleInputChange = (field: keyof OracleConnectionForm) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.type === 'number' ? parseInt(e.target.value) || 0 :
                  e.target.type === 'checkbox' ? e.target.checked :
                  e.target.value;
    
    setConnectionForm(prev => ({
      ...prev,
      [field]: value
    }));
    setFormError(null);
  };

  const validateForm = () => {
    if (!connectionForm.name.trim()) {
      setFormError('Connection name is required');
      return false;
    }
    if (!connectionForm.host.trim()) {
      setFormError('Host is required');
      return false;
    }
    if (!connectionForm.port || connectionForm.port <= 0) {
      setFormError('Valid port number is required');
      return false;
    }
    if (!connectionForm.serviceName.trim()) {
      setFormError('Service name is required');
      return false;
    }
    if (!connectionForm.username.trim()) {
      setFormError('Username is required');
      return false;
    }
    if (!connectionForm.password.trim()) {
      setFormError('Password is required');
      return false;
    }
    return true;
  };

  const handleNext = async () => {
    if (activeStep === 0) {
      if (!validateForm()) return;
      setActiveStep(1);
    } else if (activeStep === 1) {
      if (connectionForm.testConnection) {
        await handleTestConnection();
        if (testResult.status === 'success') {
          setActiveStep(2);
        }
      } else {
        setActiveStep(2);
      }
    } else if (activeStep === 2) {
      await handleSave();
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleTestConnection = async () => {
    setTestResult({ status: 'testing' });
    try {
      const isValid = await testOracleConnection(connectionForm);
      if (isValid) {
        setTestResult({ 
          status: 'success', 
          message: 'Connection test successful!' 
        });
      } else {
        setTestResult({ 
          status: 'error', 
          message: 'Connection test failed. Please check your credentials.' 
        });
      }
    } catch (error) {
      setTestResult({ 
        status: 'error', 
        message: 'Connection test failed. Please check your credentials.' 
      });
    }
  };

  const handleSave = async () => {
    try {
      await addOracleConnection(connectionForm);
      handleClose();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Failed to save connection');
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setConnectionForm({
      name: '',
      host: '',
      port: 1521,
      serviceName: '',
      username: '',
      password: '',
      testConnection: true
    });
    setTestResult({ status: 'idle' });
    setFormError(null);
    onClose();
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Connection Name"
                value={connectionForm.name}
                onChange={handleInputChange('name')}
                placeholder="e.g., Production Oracle DB"
                required
              />
            </Grid>
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="Host"
                value={connectionForm.host}
                onChange={handleInputChange('host')}
                placeholder="e.g., oracle.company.com"
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Port"
                value={connectionForm.port}
                onChange={handleInputChange('port')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Service Name"
                value={connectionForm.serviceName}
                onChange={handleInputChange('serviceName')}
                placeholder="e.g., ORCL"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Username"
                value={connectionForm.username}
                onChange={handleInputChange('username')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="password"
                label="Password"
                value={connectionForm.password}
                onChange={handleInputChange('password')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={connectionForm.testConnection}
                    onChange={handleInputChange('testConnection')}
                    color="primary"
                  />
                }
                label="Test connection before saving"
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            {testResult.status === 'idle' && (
              <Box>
                <TestTube sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Ready to Test Connection
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Click "Test Connection" to verify your Oracle database credentials
                </Typography>
              </Box>
            )}
            
            {testResult.status === 'testing' && (
              <Box>
                <CircularProgress size={64} sx={{ mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Testing Connection...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Connecting to {connectionForm.host}:{connectionForm.port}
                </Typography>
              </Box>
            )}

            {testResult.status === 'success' && (
              <Box>
                <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 2, color: 'success.main' }}>
                  Connection Successful!
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {testResult.message}
                </Typography>
              </Box>
            )}

            {testResult.status === 'error' && (
              <Box>
                <Error sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 2, color: 'error.main' }}>
                  Connection Failed
                </Typography>
                <Typography variant="body2" color="error.main">
                  {testResult.message}
                </Typography>
                <Button
                  variant="outlined"
                  onClick={handleTestConnection}
                  sx={{ mt: 2 }}
                  disabled={testResult.status === 'testing'}
                >
                  Retry Test
                </Button>
              </Box>
            )}
          </Box>
        );

      case 2:
        return (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Connection Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Name:</Typography>
                <Typography variant="body1">{connectionForm.name}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Host:</Typography>
                <Typography variant="body1">{connectionForm.host}:{connectionForm.port}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Service:</Typography>
                <Typography variant="body1">{connectionForm.serviceName}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Username:</Typography>
                <Typography variant="body1">{connectionForm.username}</Typography>
              </Grid>
            </Grid>
            
            {testResult.status === 'success' && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Connection test passed successfully
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
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3 }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h5" component="div">
          Add Oracle Connection
        </Typography>
        <IconButton onClick={handleClose} size="small">
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pb: 1 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {formError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {formError}
          </Alert>
        )}

        {getStepContent(activeStep)}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={handleClose}>
          Cancel
        </Button>
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        {activeStep === 1 && testResult.status !== 'success' && connectionForm.testConnection && (
          <Button
            onClick={handleTestConnection}
            variant="outlined"
            disabled={testResult.status === 'testing'}
            startIcon={testResult.status === 'testing' ? <CircularProgress size={16} /> : <TestTube />}
          >
            Test Connection
          </Button>
        )}
        <Button
          onClick={handleNext}
          variant="contained"
          disabled={isLoading || (activeStep === 1 && connectionForm.testConnection && testResult.status !== 'success')}
          startIcon={isLoading ? <CircularProgress size={16} /> : null}
        >
          {activeStep === steps.length - 1 ? 'Save Connection' : 'Next'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
