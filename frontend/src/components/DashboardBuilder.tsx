/**
 * Interactive Dashboard Builder Component
 * Drag-and-drop interface for creating custom dashboards with Oracle Redwood design
 */

import React, { useState, useCallback } from 'react'
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
  Divider,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Add,
  DragHandle,
  Edit,
  Delete,
  BarChart,
  PieChart,
  Timeline,
  TableChart,
  Assessment,
  Speed,
  TrendingUp,
  Warning,
  ExpandMore,
  Save,
  Preview,
} from '@mui/icons-material'

interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'table' | 'metric'
  title: string
  config: any
  position: { x: number; y: number; w: number; h: number }
}

interface KPI {
  id: string
  name: string
  formula: string
  dataSource: string
  visualizationType: string
  thresholds: {
    warning: number
    critical: number
  }
}

const DashboardBuilder: React.FC = () => {
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [customKPIs, setCustomKPIs] = useState<KPI[]>([])
  const [showWidgetDialog, setShowWidgetDialog] = useState(false)
  const [showKPIDialog, setShowKPIDialog] = useState(false)
  const [selectedWidget, setSelectedWidget] = useState<Widget | null>(null)
  const [newKPI, setNewKPI] = useState<Partial<KPI>>({
    name: '',
    formula: '',
    dataSource: 'reports',
    visualizationType: 'line',
    thresholds: { warning: 75, critical: 90 }
  })

  const widgetTypes = [
    { id: 'line-chart', name: 'Line Chart', icon: Timeline, description: 'Time series data visualization' },
    { id: 'bar-chart', name: 'Bar Chart', icon: BarChart, description: 'Categorical data comparison' },
    { id: 'pie-chart', name: 'Pie Chart', icon: PieChart, description: 'Proportion visualization' },
    { id: 'kpi-card', name: 'KPI Card', icon: Speed, description: 'Key performance indicator' },
    { id: 'data-table', name: 'Data Table', icon: TableChart, description: 'Tabular data display' },
    { id: 'metric-card', name: 'Metric Card', icon: Assessment, description: 'Single metric display' },
  ]

  const dataSources = [
    { id: 'reports', name: 'Report Executions' },
    { id: 'users', name: 'User Activity' },
    { id: 'performance', name: 'System Performance' },
    { id: 'oracle_bi', name: 'Oracle BI Publisher' },
    { id: 'custom_sql', name: 'Custom SQL Query' },
  ]

  const visualizationTypes = [
    { id: 'line', name: 'Line Chart' },
    { id: 'bar', name: 'Bar Chart' },
    { id: 'area', name: 'Area Chart' },
    { id: 'gauge', name: 'Gauge' },
    { id: 'number', name: 'Number' },
  ]

  const handleAddWidget = (type: string) => {
    const newWidget: Widget = {
      id: `widget_${Date.now()}`,
      type: type.includes('chart') ? 'chart' : type.includes('kpi') ? 'kpi' : type.includes('table') ? 'table' : 'metric',
      title: `New ${type.replace('-', ' ')}`,
      config: {
        chartType: type,
        dataSource: 'reports',
        aggregation: 'count',
        timeRange: '24h'
      },
      position: { x: 0, y: 0, w: 6, h: 4 }
    }

    setWidgets(prev => [...prev, newWidget])
    setShowWidgetDialog(false)
  }

  const handleCreateKPI = () => {
    if (!newKPI.name || !newKPI.formula) return

    const kpi: KPI = {
      id: `kpi_${Date.now()}`,
      name: newKPI.name,
      formula: newKPI.formula || '',
      dataSource: newKPI.dataSource || 'reports',
      visualizationType: newKPI.visualizationType || 'line',
      thresholds: newKPI.thresholds || { warning: 75, critical: 90 }
    }

    setCustomKPIs(prev => [...prev, kpi])
    setNewKPI({
      name: '',
      formula: '',
      dataSource: 'reports',
      visualizationType: 'line',
      thresholds: { warning: 75, critical: 90 }
    })
    setShowKPIDialog(false)
  }

  const handleDeleteWidget = (widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId))
  }

  const handleDeleteKPI = (kpiId: string) => {
    setCustomKPIs(prev => prev.filter(k => k.id !== kpiId))
  }

  const saveDashboard = () => {
    const dashboardConfig = {
      id: `dashboard_${Date.now()}`,
      name: 'Custom Dashboard',
      widgets,
      customKPIs,
      createdAt: new Date().toISOString()
    }

    // In a real implementation, this would save to the backend
    console.log('Saving dashboard:', dashboardConfig)
    alert('Dashboard saved successfully!')
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Interactive Dashboard Builder
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Create custom dashboards with drag-and-drop widgets and KPIs
          </Typography>
        </Box>
        
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={() => setShowWidgetDialog(true)}
          >
            Add Widget
          </Button>
          <Button
            variant="outlined"
            startIcon={<TrendingUp />}
            onClick={() => setShowKPIDialog(true)}
          >
            Create KPI
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={saveDashboard}
          >
            Save Dashboard
          </Button>
        </Box>
      </Box>

      {/* Dashboard Canvas */}
      <Paper sx={{ p: 2, mb: 3, minHeight: 400, backgroundColor: '#f8f9fa' }}>
        <Typography variant="h6" gutterBottom>
          Dashboard Canvas
        </Typography>
        
        {widgets.length === 0 ? (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight={300}
            sx={{ 
              border: '2px dashed #ccc',
              borderRadius: 2,
              backgroundColor: 'white'
            }}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No widgets added yet
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Start by adding widgets to build your custom dashboard
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setShowWidgetDialog(true)}
            >
              Add Your First Widget
            </Button>
          </Box>
        ) : (
          <Grid container spacing={2}>
            {widgets.map((widget) => (
              <Grid item xs={12} md={widget.position.w} key={widget.id}>
                <Card sx={{ position: 'relative' }}>
                  <CardHeader
                    title={widget.title}
                    action={
                      <Box>
                        <IconButton size="small">
                          <DragHandle />
                        </IconButton>
                        <IconButton size="small" onClick={() => setSelectedWidget(widget)}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDeleteWidget(widget.id)}>
                          <Delete />
                        </IconButton>
                      </Box>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      minHeight={150}
                      sx={{ backgroundColor: '#f5f5f5', borderRadius: 1 }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        {widget.type.toUpperCase()} - {widget.config.chartType}
                      </Typography>
                    </Box>
                    <Box mt={2}>
                      <Chip size="small" label={`Source: ${widget.config.dataSource}`} />
                      <Chip size="small" label={`Range: ${widget.config.timeRange}`} sx={{ ml: 1 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Custom KPIs Section */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Custom KPIs ({customKPIs.length})</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {customKPIs.length === 0 ? (
            <Typography color="text.secondary">
              No custom KPIs created yet. Create your first KPI to track business metrics.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {customKPIs.map((kpi) => (
                <Grid item xs={12} md={6} key={kpi.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start">
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {kpi.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Formula: {kpi.formula}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip size="small" label={`Source: ${kpi.dataSource}`} />
                            <Chip size="small" label={kpi.visualizationType} />
                          </Box>
                        </Box>
                        <IconButton onClick={() => handleDeleteKPI(kpi.id)}>
                          <Delete />
                        </IconButton>
                      </Box>
                      
                      <Divider sx={{ my: 2 }} />
                      
                      <Box>
                        <Typography variant="caption" display="block" gutterBottom>
                          Thresholds:
                        </Typography>
                        <Box display="flex" gap={2}>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Warning sx={{ fontSize: 16, color: 'orange' }} />
                            <Typography variant="body2">Warning: {kpi.thresholds.warning}%</Typography>
                          </Box>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Warning sx={{ fontSize: 16, color: 'red' }} />
                            <Typography variant="body2">Critical: {kpi.thresholds.critical}%</Typography>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Add Widget Dialog */}
      <Dialog open={showWidgetDialog} onClose={() => setShowWidgetDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Widget</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Choose a widget type to add to your dashboard
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {widgetTypes.map((type) => (
              <Grid item xs={12} sm={6} md={4} key={type.id}>
                <Card
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { boxShadow: 4 }
                  }}
                  onClick={() => handleAddWidget(type.id)}
                >
                  <CardContent sx={{ textAlign: 'center' }}>
                    <type.icon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6" gutterBottom>
                      {type.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {type.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWidgetDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Create KPI Dialog */}
      <Dialog open={showKPIDialog} onClose={() => setShowKPIDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Custom KPI</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="KPI Name"
              value={newKPI.name}
              onChange={(e) => setNewKPI(prev => ({ ...prev, name: e.target.value }))}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Formula"
              value={newKPI.formula}
              onChange={(e) => setNewKPI(prev => ({ ...prev, formula: e.target.value }))}
              margin="normal"
              placeholder="e.g., COUNT(reports) / COUNT(users)"
              required
              helperText="Define the calculation formula for your KPI"
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Data Source</InputLabel>
              <Select
                value={newKPI.dataSource}
                label="Data Source"
                onChange={(e) => setNewKPI(prev => ({ ...prev, dataSource: e.target.value }))}
              >
                {dataSources.map((source) => (
                  <MenuItem key={source.id} value={source.id}>
                    {source.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Visualization Type</InputLabel>
              <Select
                value={newKPI.visualizationType}
                label="Visualization Type"
                onChange={(e) => setNewKPI(prev => ({ ...prev, visualizationType: e.target.value }))}
              >
                {visualizationTypes.map((type) => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Alert Thresholds
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Warning Threshold (%)"
                    type="number"
                    value={newKPI.thresholds?.warning}
                    onChange={(e) => setNewKPI(prev => ({
                      ...prev,
                      thresholds: { ...prev.thresholds, warning: Number(e.target.value) }
                    }))}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Critical Threshold (%)"
                    type="number"
                    value={newKPI.thresholds?.critical}
                    onChange={(e) => setNewKPI(prev => ({
                      ...prev,
                      thresholds: { ...prev.thresholds, critical: Number(e.target.value) }
                    }))}
                  />
                </Grid>
              </Grid>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowKPIDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateKPI} 
            variant="contained"
            disabled={!newKPI.name || !newKPI.formula}
          >
            Create KPI
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DashboardBuilder