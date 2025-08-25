import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  Plus,
  Search,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle
} from 'lucide-react';
import ApiService from '../services/api';
import { ReportTemplate, ReportRequest, ReportResponse } from '../types';
import toast from 'react-hot-toast';
import { clsx } from 'clsx';

const Reports: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: templates, isLoading: templatesLoading } = useQuery(
    ['templates', selectedCategory],
    () => ApiService.getReportTemplates(selectedCategory === 'all' ? undefined : selectedCategory)
  );

  const { data: reportHistory, isLoading: historyLoading } = useQuery(
    'report-history',
    () => ApiService.getReportHistory(20)
  );

  const createReportMutation = useMutation(
    (request: ReportRequest) => ApiService.createReport(request),
    {
      onSuccess: (data) => {
        toast.success(`Report "${data.report_id}" created successfully`);
        setShowCreateModal(false);
      },
      onError: () => {
        toast.error('Failed to create report');
      },
    }
  );

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'Sales', name: 'Sales' },
    { id: 'Finance', name: 'Finance' },
    { id: 'Operations', name: 'Operations' },
    { id: 'HR', name: 'Human Resources' },
  ];

  const filteredTemplates = templates?.filter(template =>
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (templatesLoading || historyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="redwood-spinner w-8 h-8"></div>
        <span className="ml-2 text-gray-600">Loading reports...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-1">
            Generate and manage Oracle BI Publisher reports
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="redwood-button redwood-button--primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Report
        </button>
      </div>

      {/* Filters */}
      <div className="redwood-card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="redwood-input pl-10"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div className="sm:w-48">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="redwood-input"
            >
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Templates */}
        <div className="lg:col-span-2">
          <div className="redwood-card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Report Templates</h2>
            
            {filteredTemplates.length > 0 ? (
              <div className="space-y-4">
                {filteredTemplates.map((template) => (
                  <div key={template.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                      <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded-full">
                        {template.category}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-3">{template.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        Created by {template.created_by} • {new Date(template.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex space-x-2">
                        <button className="redwood-button redwood-button--secondary text-xs">
                          <Eye className="w-3 h-3 mr-1" />
                          Preview
                        </button>
                        <button
                          onClick={() => {
                            // TODO: Open create report modal with this template
                            toast.info('Create report modal would open here');
                          }}
                          className="redwood-button redwood-button--primary text-xs"
                        >
                          <FileText className="w-3 h-3 mr-1" />
                          Generate
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No templates found</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Reports */}
        <div>
          <div className="redwood-card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Reports</h2>
            
            {reportHistory && reportHistory.length > 0 ? (
              <div className="space-y-3">
                {reportHistory.slice(0, 10).map((report) => (
                  <div key={report.report_id} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        {report.report_id}
                      </span>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(report.status)}
                        <span className={clsx(
                          'px-2 py-1 text-xs font-medium rounded-full',
                          getStatusColor(report.status)
                        )}>
                          {report.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-500 mb-2">
                      {new Date(report.created_at).toLocaleString()}
                    </div>
                    
                    {report.status === 'completed' && report.download_url && (
                      <button className="w-full redwood-button redwood-button--secondary text-xs">
                        <Download className="w-3 h-3 mr-1" />
                        Download
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-sm">No reports generated yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;