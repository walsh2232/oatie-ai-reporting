import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  CircularProgress,
  Stack
} from '@mui/material';
import {
  Send,
  Clear,
  History,
  ContentCopy,
  Download,
  ExpandMore,
  CheckCircle,
  Error as ErrorIcon,
  Code,
  Psychology
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface QueryResult {
  sql: string;
  valid: boolean;
  generation_method: string;
  timestamp: Date;
  error?: string;
}

interface QueryHistory {
  id: string;
  query: string;
  result: QueryResult;
  timestamp: Date;
}

export const QueryInterface: React.FC = () => {
  const { user } = useAuth();
  const [naturalQuery, setNaturalQuery] = useState('');
  const [sqlResult, setSqlResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryHistory, setQueryHistory] = useState<QueryHistory[]>([]);
  const [showHistory, setShowHistory] = useState(true);

  const activeConnection = user?.oracleConnections?.find(conn => conn.isActive);

  useEffect(() => {
    // Load query history from localStorage
    const savedHistory = localStorage.getItem('queryHistory');
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        setQueryHistory(parsed.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp),
          result: {
            ...item.result,
            timestamp: new Date(item.result.timestamp)
          }
        })));
      } catch (e) {
        console.error('Failed to load query history:', e);
      }
    }
  }, []);

  const saveToHistory = (query: string, result: QueryResult) => {
    const historyItem: QueryHistory = {
      id: Date.now().toString(),
      query,
      result,
      timestamp: new Date()
    };

    const newHistory = [historyItem, ...queryHistory].slice(0, 50); // Keep last 50 queries
    setQueryHistory(newHistory);
    localStorage.setItem('queryHistory', JSON.stringify(newHistory));
  };

  const handleGenerateSQL = async () => {
    if (!naturalQuery.trim()) {
      setError('Please enter a natural language query');
      return;
    }

    if (!activeConnection) {
      setError('Please add and activate an Oracle connection first');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSqlResult(null);

    try {
      const response = await fetch('http://localhost:8000/sql/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: naturalQuery }),
      });

      if (!response.ok) {
        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
      }

      const data = await response.json();
      const result: QueryResult = {
        sql: data.sql,
        valid: data.valid,
        generation_method: data.generation_method || 'Unknown',
        timestamp: new Date()
      };

      setSqlResult(result);
      saveToHistory(naturalQuery, result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate SQL';
      setError(errorMessage);
      setSqlResult({
        sql: '',
        valid: false,
        generation_method: 'Error',
        timestamp: new Date(),
        error: errorMessage
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidateSQL = async (sql: string) => {
    if (!sql.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/sql/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sql }),
      });

      const data = await response.json();
      setSqlResult(prev => prev ? { ...prev, valid: data.valid } : null);
    } catch (err) {
      console.error('Validation failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopySQL = () => {
    if (sqlResult?.sql) {
      navigator.clipboard.writeText(sqlResult.sql);
    }
  };

  const handleClear = () => {
    setNaturalQuery('');
    setSqlResult(null);
    setError(null);
  };

  const handleHistoryClick = (historyItem: QueryHistory) => {
    setNaturalQuery(historyItem.query);
    setSqlResult(historyItem.result);
    setError(null);
  };

  const getSampleQueries = () => [
    "Show me all active employees",
    "Get employee count by department", 
    "Find employees hired in the last 30 days",
    "List all managers with their direct reports",
    "Show salary distribution by job title"
  ];

  return (
    <Box>
      <Stack direction={{ xs: 'column', lg: 'row' }} spacing={3} alignItems="flex-start">
        {/* Main Query Interface */}
        <Box sx={{ flex: '1 1 60%', minWidth: '300px' }}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Psychology sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  Natural Language to SQL
                </Typography>
              </Box>

              {!activeConnection && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  No active Oracle connection. Please add a connection in the Connections tab.
                </Alert>
              )}

              <TextField
                fullWidth
                multiline
                rows={4}
                placeholder="Describe what data you want to retrieve... e.g., 'Show me all active employees with their departments'"
                value={naturalQuery}
                onChange={(e) => setNaturalQuery(e.target.value)}
                disabled={!activeConnection || isLoading}
                sx={{ mb: 3 }}
              />

              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <Button
                  variant="contained"
                  startIcon={isLoading ? <CircularProgress size={16} /> : <Send />}
                  onClick={handleGenerateSQL}
                  disabled={!activeConnection || !naturalQuery.trim() || isLoading}
                  sx={{ 
                    borderRadius: 2,
                    background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                  }}
                >
                  Generate SQL
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={handleClear}
                  disabled={isLoading}
                  sx={{ borderRadius: 2 }}
                >
                  Clear
                </Button>
              </Box>

              {/* Sample Queries */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Try these sample queries:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {getSampleQueries().map((query, index) => (
                    <Chip
                      key={index}
                      label={query}
                      variant="outlined"
                      size="small"
                      onClick={() => setNaturalQuery(query)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {/* SQL Result */}
              {sqlResult && (
                <Paper sx={{ p: 3, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Code sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        Generated SQL
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        icon={sqlResult.valid ? <CheckCircle /> : <ErrorIcon />}
                        label={sqlResult.valid ? 'Valid' : 'Invalid'}
                        color={sqlResult.valid ? 'success' : 'error'}
                        size="small"
                      />
                      <Chip
                        label={sqlResult.generation_method}
                        variant="outlined"
                        size="small"
                      />
                      <Tooltip title="Copy SQL">
                        <IconButton size="small" onClick={handleCopySQL}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>

                  <Paper 
                    sx={{ 
                      p: 2, 
                      backgroundColor: '#2d3748', 
                      color: '#e2e8f0',
                      fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                      fontSize: '0.9rem',
                      borderRadius: 1,
                      overflow: 'auto'
                    }}
                  >
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {sqlResult.sql || 'No SQL generated'}
                    </pre>
                  </Paper>

                  {sqlResult.error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {sqlResult.error}
                    </Alert>
                  )}
                </Paper>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Query History Sidebar */}
        <Box sx={{ flex: '1 1 40%', minWidth: '300px' }}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <History sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Query History
                </Typography>
              </Box>

              {queryHistory.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No queries yet. Start by generating your first SQL query!
                </Typography>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {queryHistory.map((item) => (
                    <ListItem
                      key={item.id}
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 1,
                        mb: 1,
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => handleHistoryClick(item)}
                    >
                      <ListItemText
                        primary={
                          <Typography variant="body2" noWrap>
                            {item.query}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                            <Chip
                              size="small"
                              label={item.result.generation_method}
                              variant="outlined"
                              sx={{ fontSize: '0.7rem', height: 20, mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {item.timestamp.toLocaleTimeString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>
      </Stack>
    </Box>
  );
};
