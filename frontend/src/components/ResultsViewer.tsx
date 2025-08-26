import React, { useState } from 'react';
import { Download, FileText, Eye, Shield, BarChart3, Calendar } from 'lucide-react';
import { apiClient } from '../api';
import { ProcessResult } from '../types';

interface ResultsViewerProps {
  results: ProcessResult;
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ results }) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [activeTab, setActiveTab] = useState<'summary' | 'details' | 'audit'>('summary');

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const blob = await apiClient.downloadResult(results.job_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `redacted_${results.filename}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const getPIITypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'PERSON': 'bg-blue-100 text-blue-800',
      'PHONE': 'bg-green-100 text-green-800',
      'EMAIL': 'bg-purple-100 text-purple-800',
      'AADHAAR': 'bg-red-100 text-red-800',
      'PAN': 'bg-yellow-100 text-yellow-800',
      'FACE': 'bg-pink-100 text-pink-800',
      'SIGNATURE': 'bg-indigo-100 text-indigo-800',
      'DATE': 'bg-gray-100 text-gray-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card bg-success-50 border-success-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-success-100 rounded-full">
              <Shield className="h-6 w-6 text-success-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Processing Complete</h2>
              <p className="text-sm text-gray-600">
                Found and redacted {results.detections_count} PII items in {results.filename}
              </p>
            </div>
          </div>
          
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="btn-success"
          >
            <Download className="h-4 w-4 mr-2" />
            {isDownloading ? 'Downloading...' : 'Download Redacted File'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'summary', label: 'Summary', icon: BarChart3 },
              { id: 'details', label: 'PII Details', icon: Eye },
              { id: 'audit', label: 'Audit Log', icon: FileText },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'summary' && (
            <div className="space-y-6">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-primary-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-primary-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-primary-600">Total Pages</p>
                      <p className="text-2xl font-bold text-primary-900">{results.total_pages}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-warning-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <Eye className="h-8 w-8 text-warning-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-warning-600">PII Items Found</p>
                      <p className="text-2xl font-bold text-warning-900">{results.detections_count}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-success-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <Shield className="h-8 w-8 text-success-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-success-600">Items Redacted</p>
                      <p className="text-2xl font-bold text-success-900">{results.detections_count}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-8 w-8 text-gray-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-600">PII Types</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {results.summary.pii_types_found?.length || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* PII Types Distribution */}
              {results.summary.pii_counts && Object.keys(results.summary.pii_counts).length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">PII Distribution</h3>
                  <div className="space-y-3">
                    {Object.entries(results.summary.pii_counts).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPIITypeColor(type)}`}>
                            {type}
                          </span>
                          <span className="text-sm text-gray-600">{type.replace('_', ' ')}</span>
                        </div>
                        <span className="text-sm font-medium text-gray-900">{count} items</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Detected PII Items</h3>
              
              {results.audit_entries.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No PII items detected in this document.
                </div>
              ) : (
                <div className="space-y-3">
                  {results.audit_entries.map((entry, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPIITypeColor(entry.pii_type)}`}>
                            {entry.pii_type}
                          </span>
                          <span className="text-sm text-gray-600">Page {entry.page + 1}</span>
                          <span className="text-sm text-gray-600">
                            Confidence: {Math.round(entry.confidence * 100)}%
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Method: <span className="font-medium">{entry.method}</span>
                        </div>
                      </div>
                      
                      <div className="mt-2 text-xs text-gray-500">
                        Location: ({entry.bbox.x}, {entry.bbox.y}) - 
                        Size: {entry.bbox.width} × {entry.bbox.height}px
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Audit Trail</h3>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-900">Document:</span>
                    <span className="ml-2 text-gray-600">{results.filename}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-900">Total Items Processed:</span>
                    <span className="ml-2 text-gray-600">{results.detections_count}</span>
                  </div>
                </div>
              </div>

              {results.audit_entries.length > 0 && (
                <div className="space-y-2">
                  {results.audit_entries.map((entry, index) => (
                    <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-500">#{index + 1}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPIITypeColor(entry.pii_type)}`}>
                          {entry.pii_type}
                        </span>
                        <span className="text-sm text-gray-600">
                          {entry.method} on page {entry.page + 1}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(entry.timestamp)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsViewer;