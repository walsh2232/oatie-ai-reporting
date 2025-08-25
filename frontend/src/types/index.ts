// API Types for Oatie AI Reporting

export interface User {
  user_id: string;
  tenant_id: string;
  name: string;
  email: string;
  role: string;
  permissions: string[];
}

export interface SQLRequest {
  natural_language: string;
  schema_context?: Record<string, any>;
  optimization_level?: 'basic' | 'standard' | 'advanced';
}

export interface SQLResponse {
  sql_query: string;
  confidence_score: number;
  optimization_suggestions: string[];
  execution_plan?: Record<string, any>;
  estimated_performance?: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  parameters: TemplateParameter[];
  created_by: string;
  created_at: string;
  version: string;
}

export interface TemplateParameter {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  required: boolean;
  default_value?: any;
  description?: string;
  options?: string[];
}

export interface ReportRequest {
  template_id: string;
  data_source: string;
  parameters: Record<string, any>;
  format: 'PDF' | 'EXCEL' | 'CSV' | 'XML';
}

export interface ReportResponse {
  report_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  download_url?: string;
  created_at: string;
  progress?: number;
  error_message?: string;
}

export interface AnalyticsData {
  query_performance: {
    avg_execution_time: string;
    success_rate: string;
    total_queries: number;
    cache_hit_rate: string;
  };
  user_activity: {
    active_users: number;
    queries_today: number;
    reports_generated: number;
  };
  system_health: {
    cpu_usage: string;
    memory_usage: string;
    database_connections: string;
  };
  popular_queries: Array<{
    query: string;
    usage_count: number;
  }>;
}

export interface PerformanceMetrics {
  response_times: number[];
  throughput: number;
  error_rate: number;
  cache_efficiency: number;
}

export interface SQLValidationResult {
  valid: boolean;
  syntax_errors: string[];
  semantic_warnings: string[];
  optimization_score: number;
  optimization_suggestions: string[];
}

export interface ChartDataPoint {
  name: string;
  value: number;
  timestamp?: string;
}

export interface DashboardCard {
  id: string;
  title: string;
  value: string | number;
  change?: {
    value: number;
    trend: 'up' | 'down' | 'neutral';
  };
  icon?: string;
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
}