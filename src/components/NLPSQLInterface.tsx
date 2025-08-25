/**
 * Advanced NLP to SQL Query Interface
 * Enterprise-grade natural language to SQL conversion with Oracle optimization
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  Paper,
  useTheme,
} from '@mui/material';
import {
  ExpandMore,
  PlayArrow,
  Tune,
  CheckCircle,
  Info,
  ContentCopy,
  QueryStats,
  Psychology,
  Speed,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Validation schema
const querySchema = yup.object({
  naturalQuery: yup
    .string()
    .required('Please enter a natural language query')
    .min(3, 'Query must be at least 3 characters long'),
  dialect: yup.string().required(),
  useCache: yup.boolean().default(true),
});

interface NLQueryFormData {
  naturalQuery: string;
  dialect: string;
  useCache: boolean;
}

interface SQLGenerationResult {
  query_id: string;
  natural_query: string;
  generated_sql: string;
  confidence: number;
  complexity: string;
  estimated_cost: number;
  optimization_hints: string[];
  tables_used: string[];
  explanation: string;
  cached: boolean;
  execution_time_ms: number;
}

const NLPSQLInterface: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SQLGenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('query');

  const { control, handleSubmit, formState: { errors }, reset } = useForm<NLQueryFormData>({
    resolver: yupResolver(querySchema),
    defaultValues: {
      naturalQuery: '',
      dialect: 'oracle',
      useCache: true,
    },
  });

  const handlePanelChange = (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const onSubmit = useCallback(async (data: NLQueryFormData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Simulate API call - in production, this would call the actual backend
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay

      // Mock response for demonstration
      const mockResult: SQLGenerationResult = {
        query_id: 'ql_' + Math.random().toString(36).substr(2, 9),
        natural_query: data.naturalQuery,
        generated_sql: generateMockSQL(data.naturalQuery),
        confidence: Math.random() * 0.3 + 0.7, // 0.7 - 1.0
        complexity: getComplexity(data.naturalQuery),
        estimated_cost: Math.floor(Math.random() * 500) + 50,
        optimization_hints: generateOptimizationHints(data.naturalQuery),
        tables_used: extractTableReferences(data.naturalQuery),
        explanation: generateExplanation(data.naturalQuery),
        cached: data.useCache && Math.random() > 0.6,
        execution_time_ms: Math.random() * 1000 + 200,
      };

      setResult(mockResult);
      setExpandedPanel('result');
    } catch (err) {
      setError((err as Error)?.message || 'Failed to generate SQL');
    } finally {
      setLoading(false);
    }
  }, []);

  const copyToClipboard = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
  }, []);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'success';
    if (confidence >= 0.7) return 'primary';
    if (confidence >= 0.5) return 'warning';
    return 'error';
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity.toLowerCase()) {
      case 'simple': return 'success';
      case 'moderate': return 'primary';
      case 'complex': return 'warning';
      case 'advanced': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto', padding: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        color: theme.palette.primary.main,
        fontWeight: 600
      }}>
        <Psychology />
        Advanced NLP to SQL Generator
      </Typography>
      
      <Typography variant="subtitle1" gutterBottom sx={{ color: theme.palette.text.secondary, mb: 3 }}>
        Transform natural language queries into optimized Oracle SQL with AI-powered intelligence
      </Typography>

      {/* Query Input Form */}
      <Accordion 
        expanded={expandedPanel === 'query'} 
        onChange={handlePanelChange('query')}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <QueryStats />
            Natural Language Query
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ width: '100%' }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Controller
                name="naturalQuery"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    multiline
                    rows={4}
                    label="Describe your query in natural language"
                    placeholder="e.g., Show me the total sales by region for the last quarter"
                    error={!!errors.naturalQuery}
                    helperText={errors.naturalQuery?.message || 'Describe what data you want to retrieve'}
                    variant="outlined"
                  />
                )}
              />
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Controller
                  name="dialect"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      select
                      label="SQL Dialect"
                      SelectProps={{ native: true }}
                    >
                      <option value="oracle">Oracle</option>
                      <option value="postgres">PostgreSQL</option>
                      <option value="mysql">MySQL</option>
                    </TextField>
                  )}
                />
              
                <Controller
                  name="useCache"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      select
                      label="Use Cache"
                      SelectProps={{ native: true }}
                    >
                      <option value="true">Yes</option>
                      <option value="false">No</option>
                    </TextField>
                  )}
                />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <LinearProgress /> : <PlayArrow />}
                  sx={{ minWidth: 120 }}
                >
                  {loading ? 'Generating...' : 'Generate SQL'}
                </Button>
                
                <Button
                  variant="outlined"
                  onClick={() => reset()}
                  disabled={loading}
                >
                  Clear
                </Button>
              </Box>
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Loading Indicator */}
      {loading && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LinearProgress sx={{ flexGrow: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Analyzing query and generating optimized SQL...
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {result && (
        <Accordion 
          expanded={expandedPanel === 'result'} 
          onChange={handlePanelChange('result')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle color="success" />
              Generated SQL Result
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Metadata */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip
                  label={`Confidence: ${(result.confidence * 100).toFixed(1)}%`}
                  color={getConfidenceColor(result.confidence) as any}
                  variant="filled"
                />
                <Chip
                  label={`Complexity: ${result.complexity}`}
                  color={getComplexityColor(result.complexity) as any}
                  variant="outlined"
                />
                <Chip
                  label={`Cost: ${result.estimated_cost}`}
                  icon={<Speed />}
                  variant="outlined"
                />
                <Chip
                  label={`${result.execution_time_ms.toFixed(0)}ms`}
                  variant="outlined"
                />
                {result.cached && (
                  <Chip
                    label="Cached"
                    color="info"
                    variant="filled"
                  />
                )}
              </Box>

              {/* Generated SQL */}
              <Paper sx={{ p: 2, bgcolor: theme.palette.grey[50] }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Generated SQL
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton 
                      size="small" 
                      onClick={() => copyToClipboard(result.generated_sql)}
                    >
                      <ContentCopy />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Typography 
                  component="pre" 
                  sx={{ 
                    fontFamily: 'monospace', 
                    fontSize: '0.875rem',
                    whiteSpace: 'pre-wrap',
                    margin: 0
                  }}
                >
                  {result.generated_sql}
                </Typography>
              </Paper>

              {/* Explanation */}
              <Alert severity="info" icon={<Info />}>
                <Typography variant="body2">
                  <strong>Explanation:</strong> {result.explanation}
                </Typography>
              </Alert>

              {/* Tables Used and Optimization Hints in Flex Layout */}
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                {/* Tables Used */}
                {result.tables_used.length > 0 && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
                      Tables Referenced
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {result.tables_used.map((table) => (
                        <Chip
                          key={table}
                          label={table}
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Optimization Hints */}
                {result.optimization_hints.length > 0 && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Tune />
                      Optimization Hints
                    </Typography>
                    <List dense>
                      {result.optimization_hints.map((hint, index) => (
                        <ListItem key={index} sx={{ py: 0.25 }}>
                          <ListItemText 
                            primary={hint}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Help Section */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">
            Examples & Help
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            Example Queries:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Show me the total sales by region for the last quarter" />
            </ListItem>
            <ListItem>
              <ListItemText primary="List the top 10 customers by purchase amount" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Find all products in the electronics category with price greater than 500" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Show sales trends over the past 12 months grouped by month" />
            </ListItem>
          </List>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
            Supported Features:
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="Aggregations" 
                secondary="COUNT, SUM, AVG, MAX, MIN operations"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Temporal Queries" 
                secondary="Last N days/weeks/months/years"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Filtering" 
                secondary="WHERE conditions with comparisons"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Ranking" 
                secondary="TOP/BOTTOM N results"
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Joins" 
                secondary="Multi-table relationships"
              />
            </ListItem>
          </List>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

// Helper functions for mock data generation
function generateMockSQL(query: string): string {
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('total') && lowerQuery.includes('sales')) {
    if (lowerQuery.includes('region')) {
      return `SELECT /*+ USE_HASH */ 
    r.region_name,
    SUM(s.amount) as total_sales
FROM sales s
JOIN customers c ON s.customer_id = c.id
JOIN regions r ON c.region_id = r.id
WHERE s.sale_date >= SYSDATE - INTERVAL '3' MONTH
GROUP BY r.region_name
ORDER BY total_sales DESC`;
    }
    return `SELECT SUM(amount) as total_sales
FROM sales
WHERE sale_date >= SYSDATE - INTERVAL '1' YEAR`;
  }
  
  if (lowerQuery.includes('top') && lowerQuery.includes('customer')) {
    return `SELECT /*+ PARALLEL(4) */
    c.name,
    SUM(s.amount) as total_purchases
FROM customers c
JOIN sales s ON c.id = s.customer_id
GROUP BY c.name
ORDER BY total_purchases DESC
FETCH FIRST 10 ROWS ONLY`;
  }
  
  if (lowerQuery.includes('product') && lowerQuery.includes('price')) {
    return `SELECT name, category, price
FROM products
WHERE category = 'electronics'
  AND price > 500
ORDER BY price DESC`;
  }
  
  return `SELECT *
FROM sales
WHERE created_at >= SYSDATE - INTERVAL '1' MONTH
ORDER BY created_at DESC`;
}

function getComplexity(query: string): string {
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('join') || lowerQuery.includes('group by') || lowerQuery.includes('aggregate')) {
    return 'complex';
  }
  if (lowerQuery.includes('where') || lowerQuery.includes('order') || lowerQuery.includes('top')) {
    return 'moderate';
  }
  return 'simple';
}

function generateOptimizationHints(query: string): string[] {
  const hints = [];
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('total') || lowerQuery.includes('sum')) {
    hints.push('Consider using Oracle parallel processing for large aggregations');
  }
  if (lowerQuery.includes('join')) {
    hints.push('Oracle: USE_HASH hint applied for optimal join performance');
  }
  if (lowerQuery.includes('top') || lowerQuery.includes('order')) {
    hints.push('Ensure ORDER BY columns are indexed for better performance');
  }
  if (lowerQuery.includes('last') || lowerQuery.includes('recent')) {
    hints.push('Date range filter automatically optimized with Oracle date functions');
  }
  
  return hints;
}

function extractTableReferences(query: string): string[] {
  const tables = [];
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('sales')) tables.push('sales');
  if (lowerQuery.includes('customer')) tables.push('customers');
  if (lowerQuery.includes('product')) tables.push('products');
  if (lowerQuery.includes('region')) tables.push('regions');
  if (lowerQuery.includes('order')) tables.push('orders');
  
  return tables.length > 0 ? tables : ['sales'];
}

function generateExplanation(query: string): string {
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('total') && lowerQuery.includes('region')) {
    return 'Generated aggregation query with JOIN operations to combine sales data with regional information. Uses Oracle-specific hints for optimal performance.';
  }
  if (lowerQuery.includes('top')) {
    return 'Generated ranking query using Oracle FETCH FIRST syntax for optimal performance. Includes appropriate sorting and grouping.';
  }
  if (lowerQuery.includes('product') && lowerQuery.includes('price')) {
    return 'Generated filtered query with price comparison. Uses efficient WHERE clause indexing strategy.';
  }
  
  return 'Generated optimized SELECT query based on natural language pattern matching with Oracle-specific optimizations applied.';
}

export default NLPSQLInterface;