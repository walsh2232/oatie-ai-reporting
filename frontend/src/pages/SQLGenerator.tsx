import React, { useState } from 'react';
import { useMutation, useQuery } from 'react-query';
import { Send, Sparkles, Database, CheckCircle, AlertCircle, Copy, Download } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ApiService from '../services/api';
import { SQLRequest, SQLResponse } from '../types';
import toast from 'react-hot-toast';
import { clsx } from 'clsx';

const SQLGenerator: React.FC = () => {
  const [naturalLanguage, setNaturalLanguage] = useState('');
  const [sqlResult, setSqlResult] = useState<SQLResponse | null>(null);
  const [optimizationLevel, setOptimizationLevel] = useState<'basic' | 'standard' | 'advanced'>('standard');

  const generateSQLMutation = useMutation(
    (request: SQLRequest) => ApiService.generateSQL(request),
    {
      onSuccess: (data) => {
        setSqlResult(data);
        toast.success(`SQL generated with ${(data.confidence_score * 100).toFixed(1)}% confidence`);
      },
      onError: () => {
        toast.error('Failed to generate SQL. Please try again.');
      },
    }
  );

  const validateSQLMutation = useMutation(
    (sql: string) => ApiService.validateSQL(sql),
    {
      onSuccess: (data) => {
        if (data.valid) {
          toast.success('SQL is valid!');
        } else {
          toast.error('SQL validation failed');
        }
      },
    }
  );

  const handleGenerateSQL = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalLanguage.trim()) {
      toast.error('Please enter a natural language query');
      return;
    }

    const request: SQLRequest = {
      natural_language: naturalLanguage,
      optimization_level: optimizationLevel,
    };

    generateSQLMutation.mutate(request);
  };

  const handleCopySQL = () => {
    if (sqlResult?.sql_query) {
      navigator.clipboard.writeText(sqlResult.sql_query);
      toast.success('SQL copied to clipboard');
    }
  };

  const handleValidateSQL = () => {
    if (sqlResult?.sql_query) {
      validateSQLMutation.mutate(sqlResult.sql_query);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const exampleQueries = [
    "Show me the top 5 sales representatives by total revenue this quarter",
    "Get all employees hired in the last 6 months with their department and salary",
    "Find products with low inventory levels below 10 units",
    "Calculate the average order value by region for the past year",
    "List customers who haven't placed an order in the last 90 days"
  ];

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">SQL Generator</h1>
        <p className="text-gray-600 mt-1">
          Transform natural language into optimized SQL queries with AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="space-y-6">
          {/* Natural Language Input */}
          <div className="redwood-card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              <Sparkles className="w-5 h-5 inline mr-2 text-orange-500" />
              Natural Language Query
            </h2>
            
            <form onSubmit={handleGenerateSQL} className="space-y-4">
              <div>
                <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                  Describe what you want to query
                </label>
                <textarea
                  id="query"
                  value={naturalLanguage}
                  onChange={(e) => setNaturalLanguage(e.target.value)}
                  placeholder="e.g., Show me the top 10 customers by revenue this month"
                  rows={4}
                  className="redwood-textarea"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Optimization Level
                </label>
                <select
                  value={optimizationLevel}
                  onChange={(e) => setOptimizationLevel(e.target.value as any)}
                  className="redwood-input"
                >
                  <option value="basic">Basic - Simple queries</option>
                  <option value="standard">Standard - Balanced performance</option>
                  <option value="advanced">Advanced - Maximum optimization</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={generateSQLMutation.isLoading || !naturalLanguage.trim()}
                className="w-full redwood-button redwood-button--primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generateSQLMutation.isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="redwood-spinner mr-2"></div>
                    Generating SQL...
                  </div>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Generate SQL
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Example Queries */}
          <div className="redwood-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Queries</h3>
            <div className="space-y-2">
              {exampleQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => setNaturalLanguage(query)}
                  className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {sqlResult && (
            <>
              {/* Generated SQL */}
              <div className="redwood-card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    <Database className="w-5 h-5 inline mr-2 text-blue-500" />
                    Generated SQL
                  </h2>
                  <div className="flex items-center space-x-2">
                    <span
                      className={clsx(
                        'px-2 py-1 text-xs font-medium rounded-full',
                        getConfidenceColor(sqlResult.confidence_score)
                      )}
                    >
                      {(sqlResult.confidence_score * 100).toFixed(1)}% confidence
                    </span>
                    <button
                      onClick={handleCopySQL}
                      className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100"
                      title="Copy SQL"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="sql-editor">
                  <SyntaxHighlighter
                    language="sql"
                    style={oneLight}
                    customStyle={{
                      margin: 0,
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '14px',
                      lineHeight: '1.5'
                    }}
                  >
                    {sqlResult.sql_query}
                  </SyntaxHighlighter>
                </div>

                <div className="flex space-x-2 mt-4">
                  <button
                    onClick={handleValidateSQL}
                    disabled={validateSQLMutation.isLoading}
                    className="redwood-button redwood-button--secondary"
                  >
                    {validateSQLMutation.isLoading ? (
                      <div className="redwood-spinner w-4 h-4 mr-2"></div>
                    ) : (
                      <CheckCircle className="w-4 h-4 mr-2" />
                    )}
                    Validate SQL
                  </button>
                  <button className="redwood-button redwood-button--secondary">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </button>
                </div>
              </div>

              {/* Performance & Optimization */}
              <div className="redwood-card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Performance Analysis
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">Estimated Performance</span>
                      <span className="text-sm text-gray-600">{sqlResult.estimated_performance}</span>
                    </div>
                  </div>

                  {sqlResult.optimization_suggestions.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Optimization Suggestions</h4>
                      <div className="space-y-2">
                        {sqlResult.optimization_suggestions.map((suggestion, index) => (
                          <div key={index} className="flex items-start space-x-2 p-2 bg-yellow-50 rounded-lg">
                            <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-yellow-800">{suggestion}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {sqlResult.execution_plan && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Execution Plan</h4>
                      <div className="bg-gray-50 rounded-lg p-3">
                        <pre className="text-xs text-gray-600">
                          {JSON.stringify(sqlResult.execution_plan, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {!sqlResult && (
            <div className="redwood-card">
              <div className="text-center py-12">
                <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready to Generate SQL
                </h3>
                <p className="text-gray-600">
                  Enter a natural language query to get started with AI-powered SQL generation.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SQLGenerator;