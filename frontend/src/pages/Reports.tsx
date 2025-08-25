import React, { useState, useEffect } from 'react';
import { getReports, createReport } from '../services/api';
import { Report } from '../types/report';

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newReport, setNewReport] = useState({
    name: '',
    description: '',
    oracle_report_path: ''
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await getReports();
      setReports(data);
    } catch (err) {
      setError('Failed to load reports');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const report = await createReport(newReport);
      setReports([...reports, report]);
      setNewReport({ name: '', description: '', oracle_report_path: '' });
      setShowCreateForm(false);
    } catch (err) {
      setError('Failed to create report');
      console.error('Error creating report:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading reports...</div>;
  }

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Oracle BI Publisher Reports</h1>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancel' : '+ New Report'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {showCreateForm && (
          <form onSubmit={handleCreateReport} style={{ marginBottom: '32px' }}>
            <div className="form-group">
              <label className="form-label">Report Name</label>
              <input
                type="text"
                className="form-input"
                value={newReport.name}
                onChange={(e) => setNewReport({ ...newReport, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-input form-textarea"
                value={newReport.description}
                onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Oracle Report Path</label>
              <input
                type="text"
                className="form-input"
                value={newReport.oracle_report_path}
                onChange={(e) => setNewReport({ ...newReport, oracle_report_path: e.target.value })}
                placeholder="/path/to/oracle/report"
              />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button type="submit" className="btn btn-primary">Create Report</button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        <div style={{ display: 'grid', gap: '16px' }}>
          {reports.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--oracle-gray)' }}>
              No reports found. Create your first report to get started.
            </div>
          ) : (
            reports.map((report) => (
              <div key={report.id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <h3 style={{ margin: '0 0 8px 0', color: 'var(--oracle-blue)' }}>
                      {report.name}
                    </h3>
                    {report.description && (
                      <p style={{ margin: '0 0 12px 0', color: '#6b7280' }}>
                        {report.description}
                      </p>
                    )}
                    {report.oracle_report_path && (
                      <p style={{ margin: '0', fontSize: '14px', color: '#9ca3af' }}>
                        Path: {report.oracle_report_path}
                      </p>
                    )}
                    <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#9ca3af' }}>
                      Created: {new Date(report.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary">Edit</button>
                    <button className="btn btn-primary">Run</button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;