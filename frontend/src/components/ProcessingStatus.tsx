import React, { useEffect, useState } from 'react';
import { Clock, CheckCircle, XCircle, FileText, Eye, Shield } from 'lucide-react';
import { apiClient } from '../api';
import { JobStatus, ProcessResult } from '../types';

interface ProcessingStatusProps {
  job: JobStatus | null;
  onComplete: (result: ProcessResult) => void;
  onError: (error: string) => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ 
  job, 
  onComplete, 
  onError 
}) => {
  const [currentStatus, setCurrentStatus] = useState<JobStatus | null>(job);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'failed') {
      return;
    }

    const pollJob = async () => {
      try {
        const updatedJob = await apiClient.getJobStatus(job.id);
        setCurrentStatus(updatedJob);

        // Simulate progress for better UX
        if (updatedJob.status === 'processing') {
          setProgress(prev => Math.min(prev + Math.random() * 20, 85));
        } else if (updatedJob.status === 'completed') {
          setProgress(100);
          
          // Get audit log
          const audit = await apiClient.getAuditLog(job.id);
          
          const result: ProcessResult = {
            job_id: updatedJob.id,
            filename: updatedJob.filename,
            total_pages: audit.summary?.total_pages || 1,
            detections_count: audit.summary?.total_detections || 0,
            audit_entries: audit.audit_entries || [],
            summary: audit.summary || {}
          };
          
          setTimeout(() => onComplete(result), 500);
        } else if (updatedJob.status === 'failed') {
          onError(updatedJob.error || 'Processing failed');
        }
      } catch (error) {
        onError(error instanceof Error ? error.message : 'Polling failed');
      }
    };

    const interval = setInterval(pollJob, 1000);
    return () => clearInterval(interval);
  }, [job, onComplete, onError]);

  if (!currentStatus) {
    return null;
  }

  const getStatusIcon = () => {
    switch (currentStatus.status) {
      case 'queued':
        return <Clock className="h-6 w-6 text-warning-600" />;
      case 'processing':
        return <Eye className="h-6 w-6 text-primary-600 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-success-600" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-error-600" />;
    }
  };

  const getStatusText = () => {
    switch (currentStatus.status) {
      case 'queued':
        return 'Queued for processing...';
      case 'processing':
        return 'Analyzing document for PII...';
      case 'completed':
        return 'Processing completed successfully!';
      case 'failed':
        return 'Processing failed';
    }
  };

  const getStatusColor = () => {
    switch (currentStatus.status) {
      case 'queued':
        return 'border-warning-200 bg-warning-50';
      case 'processing':
        return 'border-primary-200 bg-primary-50';
      case 'completed':
        return 'border-success-200 bg-success-50';
      case 'failed':
        return 'border-error-200 bg-error-50';
    }
  };

  return (
    <div className={`card ${getStatusColor()}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Processing: {currentStatus.filename}
            </h3>
            <p className="text-sm text-gray-600">{getStatusText()}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-primary-600" />
          <span className="text-xs text-gray-600">Secure Processing</span>
        </div>
      </div>

      {/* Progress Bar */}
      {(currentStatus.status === 'processing' || currentStatus.status === 'queued') && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Processing Steps */}
      {currentStatus.status === 'processing' && (
        <div className="mt-6 space-y-3">
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-success-500 rounded-full"></div>
            <span className="text-gray-600">Document parsing</span>
            <CheckCircle className="h-4 w-4 text-success-500" />
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <span className="text-gray-600">PII detection in progress...</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
            <span className="text-gray-400">Document redaction</span>
          </div>
        </div>
      )}

      {/* Error Details */}
      {currentStatus.status === 'failed' && currentStatus.error && (
        <div className="mt-4 p-3 bg-error-100 border border-error-200 rounded-lg">
          <p className="text-sm text-error-700">{currentStatus.error}</p>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;