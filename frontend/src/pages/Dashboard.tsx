import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Welcome to Oatie AI Reporting</h1>
        </div>
        <p>Transform your Oracle BI Publisher experience with AI-powered report generation and analysis.</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '32px' }}>
          <div className="card">
            <h3 style={{ marginTop: 0, color: 'var(--oracle-blue)' }}>📊 Reports</h3>
            <p>Manage and generate Oracle BI Publisher reports with AI assistance.</p>
            <button className="btn btn-primary">View Reports</button>
          </div>
          
          <div className="card">
            <h3 style={{ marginTop: 0, color: 'var(--oracle-blue)' }}>🤖 AI Assistant</h3>
            <p>Get intelligent help with report creation, data analysis, and SQL generation.</p>
            <button className="btn btn-primary">Open AI Assistant</button>
          </div>
          
          <div className="card">
            <h3 style={{ marginTop: 0, color: 'var(--oracle-blue)' }}>⚡ Quick Actions</h3>
            <p>Perform common tasks quickly and efficiently.</p>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button className="btn btn-secondary">New Report</button>
              <button className="btn btn-secondary">Import Data</button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">System Health</h2>
        </div>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#10b981' }}></div>
            <span>Database: Healthy</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#10b981' }}></div>
            <span>API: Operational</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#10b981' }}></div>
            <span>AI Service: Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;