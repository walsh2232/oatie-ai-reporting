export interface AIQueryRequest {
  query: string;
  context?: string;
  session_id?: string;
  user_id?: string;
}

export interface AIQueryResponse {
  response: string;
  sql_query?: string;
  suggested_report_name?: string;
  confidence?: number;
}