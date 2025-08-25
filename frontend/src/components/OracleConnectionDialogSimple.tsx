import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Stack
} from '@mui/material';
import { Close, Science } from '@mui/icons-material';
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
  const { addOracleConnection } = useAuth();
  const [connectionForm, setConnectionForm] = useState<OracleConnectionForm>({
    host: '',
    port: 1521,
    serviceName: '',
    username: '',
    password: '',
    name: ''
  });
  const [formError, setFormError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    setFormError('');
    try {
      await addOracleConnection(connectionForm);
      onClose();
      // Reset form
      setConnectionForm({
        host: '',
        port: 1521,
        serviceName: '',
        username: '',
        password: '',
        name: ''
      });
    } catch (error: any) {
      setFormError(error instanceof Error ? error.message : 'Failed to save connection');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Science sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Add Oracle Connection</Typography>
        </Box>
        <Button onClick={handleClose} sx={{ minWidth: 'auto', p: 1 }}>
          <Close />
        </Button>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          {formError && (
            <Alert severity="error" onClose={() => setFormError('')}>
              {formError}
            </Alert>
          )}

          <TextField
            label="Connection Name"
            value={connectionForm.name}
            onChange={(e) => setConnectionForm(prev => ({ ...prev, name: e.target.value }))}
            required
            fullWidth
          />

          <Stack direction="row" spacing={2}>
            <TextField
              label="Host"
              value={connectionForm.host}
              onChange={(e) => setConnectionForm(prev => ({ ...prev, host: e.target.value }))}
              required
              fullWidth
            />
            <TextField
              label="Port"
              value={connectionForm.port.toString()}
              onChange={(e) => setConnectionForm(prev => ({ ...prev, port: parseInt(e.target.value) || 1521 }))}
              required
              sx={{ minWidth: '120px' }}
            />
          </Stack>

          <TextField
            label="Service Name"
            value={connectionForm.serviceName}
            onChange={(e) => setConnectionForm(prev => ({ ...prev, serviceName: e.target.value }))}
            required
            fullWidth
          />

          <TextField
            label="Username"
            value={connectionForm.username}
            onChange={(e) => setConnectionForm(prev => ({ ...prev, username: e.target.value }))}
            required
            fullWidth
          />

          <TextField
            label="Password"
            type="password"
            value={connectionForm.password}
            onChange={(e) => setConnectionForm(prev => ({ ...prev, password: e.target.value }))}
            required
            fullWidth
          />
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={loading || !connectionForm.name || !connectionForm.host || !connectionForm.serviceName || !connectionForm.username || !connectionForm.password}
          startIcon={loading ? <CircularProgress size={16} /> : <Science />}
        >
          {loading ? 'Connecting...' : 'Save Connection'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
