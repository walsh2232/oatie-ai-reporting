import React, { useState } from 'react';
import { processAIQuery } from '../services/api';
import { AIQueryResponse } from '../types/ai';

const AIAssistant: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AIQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await processAIQuery({
        query: query.trim(),
        session_id: sessionId,
        context: 'Oracle BI Publisher report generation'
      });
      setResponse(result);
    } catch (err) {
      setError('Failed to process your request. Please try again.');
      console.error('AI query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResponse(null);
    setError(null);
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">🤖 AI Assistant</h1>
          <p style={{ margin: '8px 0 0 0', color: 'var(--oracle-gray)' }}>
            Ask me anything about Oracle BI Publisher reports, SQL queries, or data analysis.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              What would you like help with today?
            </label>
            <textarea
              className="form-input form-textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Create a sales report for the last quarter, Generate SQL for customer data analysis, Help me optimize my report performance..."
              rows={4}
              disabled={loading}
            />
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading || !query.trim()}
            >
              {loading ? 'Processing...' : 'Ask AI'}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              Clear
            </button>
          </div>
        </form>

        {error && <div className="error">{error}</div>}

        {response && (
          <div style={{ marginTop: '32px' }}>
            <div className="card" style={{ backgroundColor: '#f0f7ff', border: '1px solid #bfdbfe' }}>
              <h3 style={{ margin: '0 0 16px 0', color: 'var(--oracle-blue)' }}>
                AI Response
              </h3>
              <p style={{ margin: '0 0 16px 0', lineHeight: '1.6' }}>
                {response.response}
              </p>
              
              {response.confidence && (
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ fontSize: '14px', color: 'var(--oracle-gray)' }}>
                    Confidence: {Math.round(response.confidence * 100)}%
                  </span>
                </div>
              )}
            </div>

            {response.sql_query && (
              <div className="card">
                <h4 style={{ margin: '0 0 12px 0', color: 'var(--oracle-blue)' }}>
                  Generated SQL Query
                </h4>
                <pre style={{ 
                  backgroundColor: '#f9fafb', 
                  padding: '16px', 
                  borderRadius: 'var(--border-radius)',
                  overflow: 'auto',
                  fontSize: '14px',
                  margin: '0'
                }}>
                  {response.sql_query}
                </pre>
                <button 
                  className="btn btn-secondary"
                  style={{ marginTop: '12px' }}
                  onClick={() => navigator.clipboard.writeText(response.sql_query || '')}
                >
                  Copy SQL
                </button>
              </div>
            )}

            {response.suggested_report_name && (
              <div className="card">
                <h4 style={{ margin: '0 0 12px 0', color: 'var(--oracle-blue)' }}>
                  Suggested Report Name
                </h4>
                <p style={{ margin: '0 0 12px 0' }}>{response.suggested_report_name}</p>
                <button className="btn btn-primary">
                  Create Report
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">💡 Sample Questions</h2>
        </div>
        <div style={{ display: 'grid', gap: '12px' }}>
          {[
            "Create a monthly sales report grouped by region",
            "Generate SQL to find top 10 customers by revenue",
            "Help me build a dashboard for inventory tracking",
            "Optimize my existing report performance",
            "Create a financial summary report for executives"
          ].map((example, index) => (
            <button
              key={index}
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', textAlign: 'left' }}
              onClick={() => setQuery(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;