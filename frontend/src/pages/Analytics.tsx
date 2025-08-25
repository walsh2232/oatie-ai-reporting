import React from 'react';
import Dashboard from './Dashboard';

// Analytics page reuses Dashboard components for now
// In a real implementation, this would have more detailed analytics
const Analytics: React.FC = () => {
  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-1">
          Detailed performance analytics and system insights
        </p>
      </div>

      {/* Reuse Dashboard components */}
      <Dashboard />
    </div>
  );
};

export default Analytics;