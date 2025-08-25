import axios from 'axios';
import { Report, CreateReportRequest } from '../types/report';
import { AIQueryRequest, AIQueryResponse } from '../types/ai';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding correlation IDs
api.interceptors.request.use((config) => {
  config.headers['X-Correlation-ID'] = `frontend_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Reports API
export const getReports = async (): Promise<Report[]> => {
  const response = await api.get('/reports/');
  return response.data;
};

export const getReport = async (id: number): Promise<Report> => {
  const response = await api.get(`/reports/${id}`);
  return response.data;
};

export const createReport = async (report: CreateReportRequest): Promise<Report> => {
  const response = await api.post('/reports/', report);
  return response.data;
};

// AI API
export const processAIQuery = async (request: AIQueryRequest): Promise<AIQueryResponse> => {
  const response = await api.post('/ai/query', request);
  return response.data;
};

export const getAIInteractions = async (sessionId: string) => {
  const response = await api.get(`/ai/interactions/${sessionId}`);
  return response.data;
};

// Health API
export const getHealth = async () => {
  const response = await api.get('/health/detailed');
  return response.data;
};

export const getHealthLive = async () => {
  const response = await api.get('/health/live');
  return response.data;
};

export default api;