import axios from 'axios';
import {
  User,
  SQLRequest,
  SQLResponse,
  ReportTemplate,
  ReportRequest,
  ReportResponse,
  AnalyticsData,
  PerformanceMetrics,
  SQLValidationResult
} from '../types';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Service Class
export class ApiService {
  // Health Check
  static async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }

  // Authentication
  static async login(username: string, password: string) {
    const response = await api.post('/auth/login', { username, password });
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token);
    }
    return response.data;
  }

  static async logout() {
    localStorage.removeItem('auth_token');
    await api.post('/auth/logout');
  }

  // User Management
  static async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/profile');
    return response.data;
  }

  // SQL Intelligence
  static async generateSQL(request: SQLRequest): Promise<SQLResponse> {
    const response = await api.post('/sql/generate', request);
    return response.data;
  }

  static async validateSQL(sqlQuery: string): Promise<SQLValidationResult> {
    const response = await api.post('/sql/validate', { sql_query: sqlQuery });
    return response.data;
  }

  // Report Templates
  static async getReportTemplates(category?: string): Promise<ReportTemplate[]> {
    const params = category ? { category } : {};
    const response = await api.get('/templates', { params });
    return response.data.templates;
  }

  static async getReportTemplate(templateId: string): Promise<ReportTemplate> {
    const response = await api.get(`/templates/${templateId}`);
    return response.data;
  }

  // Report Generation
  static async createReport(request: ReportRequest): Promise<ReportResponse> {
    const response = await api.post('/reports/create', request);
    return response.data;
  }

  static async getReportStatus(reportId: string): Promise<ReportResponse> {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  }

  static async downloadReport(reportId: string): Promise<Blob> {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  static async getReportHistory(limit: number = 50): Promise<ReportResponse[]> {
    const response = await api.get('/reports/history', {
      params: { limit }
    });
    return response.data.reports;
  }

  // Analytics Dashboard
  static async getAnalyticsDashboard(): Promise<AnalyticsData> {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  }

  static async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    const response = await api.get('/analytics/performance');
    return response.data;
  }

  static async getQueryHistory(limit: number = 100): Promise<Array<{
    id: string;
    query: string;
    natural_language: string;
    created_at: string;
    execution_time: number;
    success: boolean;
  }>> {
    const response = await api.get('/analytics/queries', {
      params: { limit }
    });
    return response.data.queries;
  }

  // Data Sources
  static async getDataSources(): Promise<Array<{
    id: string;
    name: string;
    type: string;
    status: 'active' | 'inactive' | 'error';
    last_tested: string;
  }>> {
    const response = await api.get('/datasources');
    return response.data.datasources;
  }

  static async testDataSource(dataSourceId: string): Promise<{
    success: boolean;
    message: string;
    response_time?: number;
  }> {
    const response = await api.post(`/datasources/${dataSourceId}/test`);
    return response.data;
  }

  // Schema Information
  static async getSchemaInfo(dataSourceId: string): Promise<{
    tables: Record<string, string[]>;
    relationships: Array<{ from: string; to: string }>;
    indexes: Record<string, string[]>;
  }> {
    const response = await api.get(`/schema/${dataSourceId}`);
    return response.data;
  }

  // System Settings
  static async getSystemSettings(): Promise<Record<string, any>> {
    const response = await api.get('/settings');
    return response.data;
  }

  static async updateSystemSettings(settings: Record<string, any>): Promise<void> {
    await api.put('/settings', settings);
  }
}

// Export default instance
export default ApiService;