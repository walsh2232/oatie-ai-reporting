export interface Report {
  id: number;
  name: string;
  description?: string;
  oracle_report_path?: string;
  ai_generated_query?: string;
  parameters?: Record<string, any>;
  created_by?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateReportRequest {
  name: string;
  description?: string;
  oracle_report_path?: string;
  ai_generated_query?: string;
  parameters?: Record<string, any>;
  created_by?: string;
}